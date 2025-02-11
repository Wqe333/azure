import logging
import azure.functions as func
import pyodbc
import os
from logger import IpLogger, log_function_call
from exceptions_class import *

logger = IpLogger()

def get_db_connection():
    connection_string = os.getenv("DB_CONNECTION_STRING")
    return pyodbc.connect(connection_string)

@log_function_call
def post_data(req: func.HttpRequest, data, cursor, **kwargs) -> func.HttpResponse:
    """add new product to products table"""

    name = data.get("Name")
    price = data.get("Price")
    stock = data.get("Stock")
    if not name or not price or not stock:
        return func.HttpResponse("Error not fully data", status_code=400)

    sql = "INSERT INTO products(Name, Price, Stock) VALUES (?, ?, ?)"
    values = (name, price, stock)
    cursor.execute(sql,values)

    return func.HttpResponse(f"Item created successfully.", status_code=200)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return post_data(req)
