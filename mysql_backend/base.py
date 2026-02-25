"""MySQL connector database backend for Django.

Requires mysql-connector-python: https://github.com/mysql/mysql-connector-python
"""
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql import base as mysql_base

try:
    from mysql.connector import MySQLConnection, Error
except ImportError as e:
    raise ImportError(
        "mysql-connector-python is not installed. "
        "Run: pip install mysql-connector-python"
    ) from e


class DatabaseWrapper(mysql_base.DatabaseWrapper):
    """Database wrapper that uses mysql-connector-python instead of MySQLdb."""

    vendor = "mysql"

    Database = MySQLConnection
