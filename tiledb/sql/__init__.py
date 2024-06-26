"""
TileDB SQL - A DB API v2.0 compatible interface to MySQL.

This package is a wrapper around _mysql, which mostly implements the
MySQL C API.

connect() -- connects to server

See the C API specification and the MySQL documentation for more info
on other items.

For information on how TileDB SQL handles type conversion, see the
tiledb.sql.converters module.
"""

from tiledb.sql.version import version

threadsafety = 1
apilevel = "2.0"
paramstyle = "format"

from ._mysql import (
    NotSupportedError,
    OperationalError,
    get_client_info,
    ProgrammingError,
    Error,
    InterfaceError,
    debug,
    IntegrityError,
    string_literal,
    MySQLError,
    DataError,
    escape,
    escape_string,
    DatabaseError,
    InternalError,
    Warning,
    server_init,
    server_end,
)
from tiledb.sql.constants import FIELD_TYPE
from tiledb.sql.times import (
    Date,
    Time,
    Timestamp,
    DateFromTicks,
    TimeFromTicks,
    TimestampFromTicks,
)

# Shutdown the server only on module exit
import atexit

atexit.register(server_end)

import os

module_path = os.path.dirname(os.path.realpath(__file__))

import tempfile

dirpath = tempfile.mkdtemp()

os.mkdir(os.path.join(dirpath, "test"))

# Init the embedded server on module load
server_init(
    args=[
        "--lc_messages_dir={}".format(module_path),
        "--language={}/".format(module_path),
        "--datadir={}".format(dirpath),
    ]
)

try:
    frozenset
except NameError:
    from sets import ImmutableSet as frozenset

threadsafety = 1
apilevel = "2.0"
paramstyle = "format"


class DBAPISet(frozenset):
    """A special type of set for which A == x is true if A is a
    DBAPISet and x is a member of that set."""

    def __eq__(self, other):
        if isinstance(other, DBAPISet):
            return not self.difference(other)
        return other in self


STRING = DBAPISet([FIELD_TYPE.ENUM, FIELD_TYPE.STRING, FIELD_TYPE.VAR_STRING])
BINARY = DBAPISet(
    [
        FIELD_TYPE.BLOB,
        FIELD_TYPE.LONG_BLOB,
        FIELD_TYPE.MEDIUM_BLOB,
        FIELD_TYPE.TINY_BLOB,
    ]
)
NUMBER = DBAPISet(
    [
        FIELD_TYPE.DECIMAL,
        FIELD_TYPE.DOUBLE,
        FIELD_TYPE.FLOAT,
        FIELD_TYPE.INT24,
        FIELD_TYPE.LONG,
        FIELD_TYPE.LONGLONG,
        FIELD_TYPE.TINY,
        FIELD_TYPE.YEAR,
        FIELD_TYPE.NEWDECIMAL,
    ]
)
DATE = DBAPISet([FIELD_TYPE.DATE])
TIME = DBAPISet([FIELD_TYPE.TIME])
TIMESTAMP = DBAPISet([FIELD_TYPE.TIMESTAMP, FIELD_TYPE.DATETIME])
DATETIME = TIMESTAMP
ROWID = DBAPISet()


def test_DBAPISet_set_equality():
    assert STRING == STRING


def test_DBAPISet_set_inequality():
    assert STRING != NUMBER


def test_DBAPISet_set_equality_membership():
    assert FIELD_TYPE.VAR_STRING == STRING


def test_DBAPISet_set_inequality_membership():
    assert FIELD_TYPE.DATE != STRING


def Binary(x):
    return bytes(x)


def Connect(*args, **kwargs):
    """Factory function for connections.Connection."""
    from tiledb.sql.connections import Connection

    return Connection(*args, **kwargs)


connect = Connection = Connect

__all__ = [
    "BINARY",
    "Binary",
    "Connect",
    "Connection",
    "DATE",
    "Date",
    "Time",
    "Timestamp",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "DataError",
    "DatabaseError",
    "Error",
    "FIELD_TYPE",
    "IntegrityError",
    "InterfaceError",
    "InternalError",
    "MySQLError",
    "NUMBER",
    "NotSupportedError",
    "DBAPISet",
    "OperationalError",
    "ProgrammingError",
    "ROWID",
    "STRING",
    "TIME",
    "TIMESTAMP",
    "Warning",
    "apilevel",
    "connect",
    "connections",
    "constants",
    "converters",
    "cursors",
    "debug",
    "escape",
    "escape_string",
    "get_client_info",
    "paramstyle",
    "string_literal",
    "threadsafety",
    "version",
]
