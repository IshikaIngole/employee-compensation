import os
import pyodbc


def get_connection():
    connection_string = os.getenv("SqlConnectionString")

    if not connection_string:
        raise RuntimeError(
            "SqlConnectionString application setting is not configured."
        )

    return pyodbc.connect(connection_string)
