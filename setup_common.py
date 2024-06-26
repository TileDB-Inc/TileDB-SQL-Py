from configparser import ConfigParser as SafeConfigParser


def get_metadata_and_options():
    config = SafeConfigParser()
    config.read(["metadata.cfg", "site.cfg"])

    metadata = dict(config.items("metadata"))
    options = dict(config.items("options"))

    metadata["py_modules"] = list(filter(None, metadata["py_modules"].split("\n")))
    metadata["classifiers"] = list(filter(None, metadata["classifiers"].split("\n")))

    metadata["use_setuptools_scm"] = True
    metadata["use_scm_version"] = {
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag",
        "write_to": "tiledb/sql/version.py",
    }
    metadata["setup_requires"] = ["setuptools_scm>=1.5.4", "setuptools_scm_git_archive"]
    return metadata, options


def enabled(options, option):
    value = options[option]
    s = value.lower()
    if s in ("yes", "true", "1", "y"):
        return True
    elif s in ("no", "false", "0", "n"):
        return False
    else:
        raise ValueError("Unknown value {} for option {}".format(value, option))
