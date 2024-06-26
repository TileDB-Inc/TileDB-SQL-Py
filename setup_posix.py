import os
import sys

# This dequote() business is required for some older versions
# of mysql_config


def dequote(s):
    if not s:
        raise Exception(
            "Wrong MySQL configuration: maybe https://bugs.mysql.com/bug.php?id=86971 ?"
        )
    if s[0] in "\"'" and s[0] == s[-1]:
        s = s[1:-1]
    return s


_mysql_config_path = "mysql_config"


def mysql_config(what):
    from os import popen

    f = popen("{} --{}".format(_mysql_config_path, what))
    data = f.read().strip().split()
    ret = f.close()
    if ret:
        if ret / 256:
            data = []
        if ret / 256 > 1:
            raise OSError("{} not found".format(_mysql_config_path))
    return data


def get_config():
    from setup_common import get_metadata_and_options, enabled

    global _mysql_config_path

    metadata, options = get_metadata_and_options()

    if "mysql_config" in options:
        _mysql_config_path = options["mysql_config"]
    else:
        try:
            mysql_config("version")
        except OSError:
            # try mariadb_config
            _mysql_config_path = "mariadb_config"
            try:
                mysql_config("version")
            except OSError:
                _mysql_config_path = "mysql_config"

    extra_objects = []
    static = enabled(options, "static")

    # allow a command-line option to override the base config file to permit
    # a static build to be created via requirements.txt
    #
    if "--static" in sys.argv:
        static = True
        sys.argv.remove("--static")

    if enabled(options, "embedded"):
        libs = mysql_config("libmysqld-libs")
    else:
        libs = mysql_config("libs")

    library_dirs = [dequote(i[2:]) for i in libs if i.startswith("-L")]
    libraries = [dequote(i[2:]) for i in libs if i.startswith("-l")]
    extra_link_args = [x for x in libs if not x.startswith(("-l", "-L"))]

    removable_compile_args = ("-I", "-L", "-l")
    extra_compile_args = [
        i.replace("%", "%%")
        for i in mysql_config("cflags")
        if i[:2] not in removable_compile_args
    ]

    # Copy the arch flags for linking as well
    for i in range(len(extra_compile_args)):
        if extra_compile_args[i] == "-arch":
            extra_link_args += ["-arch", extra_compile_args[i + 1]]

    include_dirs = [
        dequote(i[2:]) for i in mysql_config("include") if i.startswith("-I")
    ]

    if static:
        # properly handle mysql client libraries that are not called libmysqlclient
        client = None
        CLIENT_LIST = [
            "mysqlclient",
            "mysqlclient_r",
            "mysqld",
            "mariadb",
            "mariadbd",
            "mariadbclient",
            "perconaserverclient",
            "perconaserverclient_r",
        ]
        for c in CLIENT_LIST:
            if c in libraries:
                client = c
                break

        if client == "mariadb":
            client = "mariadbclient"
        if client is None:
            raise ValueError("Couldn't identify mysql client library")

        extra_objects.append(os.path.join(library_dirs[0], "lib%s.a" % client))
        if client in libraries:
            libraries.remove(client)
    else:
        # mysql_config may have "-lmysqlclient -lz -lssl -lcrypto", but zlib and
        # ssl is not used by _mysql.  They are needed only for static build.
        for L in ("crypto", "ssl", "z"):
            if L in libraries:
                libraries.remove(L)

    name = "tiledb-sql"
    metadata["name"] = name

    ext_options = dict(
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=include_dirs,
        extra_objects=extra_objects,
    )

    # newer versions of gcc require libstdc++ if doing a static build
    if static:
        ext_options["language"] = "c++"

    return metadata, ext_options


if __name__ == "__main__":
    sys.stderr.write(
        """You shouldn't be running this directly; it is used by setup.py."""
    )
