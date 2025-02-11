import os
import pyodbc

def get_db_connection():
    connection_string = os.getenv("DB_CONNECTION_STRING")

    return pyodbc.connect(connection_string)