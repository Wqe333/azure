import logging
import azure.functions as func
import pyodbc
import os
from logger import IpLogger, log_function_call
from exceptions_class import *

logger = IpLogger()

@log_function_call
def delete_data(req: func.HttpRequest, delete, cursor, **kwargs) -> func.HttpResponse:

    sql = "DELETE FROM products where ProductID = ?"
    values = delete.get("ProductID")
    
    cursor.execute(sql,values)
    return func.HttpResponse(f"Item deleted successfully.", status_code=200)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return delete_data(req)
