import logging
import azure.functions as func
import pyodbc
import os
from logger import IpLogger, log_function_call
from exceptions_class import *

logger = IpLogger()

@log_function_call
def update_data(req: func.HttpRequest, update, cursor, **kwargs) -> func.HttpResponse:
    update_id = update.pop("ProductID")
    parameters = update

    if len(parameters) == 0:
        return func.HttpResponse("Error no enought data", status_code=400)
    

    sql = "UPDATE products SET " + "".join([f"{key} = ? " for key in parameters.keys()]) + "where ProductID = ?"
    print(sql)
    parameters = [key for key in parameters.values()]
    parameters.append(update_id)
    cursor.execute(sql,parameters)

    return func.HttpResponse(f"Item updated successfully.", status_code=200)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return update_data(req)
