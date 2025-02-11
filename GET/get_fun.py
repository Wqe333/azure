import logging
import azure.functions as func
import pyodbc
import os
from logger import IpLogger, log_function_call
from exceptions_class import *
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from decimal import Decimal

def decimal_to_float(value):
    return float(value) if isinstance(value, Decimal) else value
@log_function_call
def get_data(req: func.HttpRequest,cursor, **kwargs) -> func.HttpResponse:
    cursor.execute('SELECT * FROM PRODUCTS')
    rows = cursor.fetchall()

    data = [dict(zip([column[0] for column in cursor.description], map(decimal_to_float, row))) for row in rows]
    return func.HttpResponse(
        json.dumps({"data": data}),
        mimetype="application/json",
        status_code = 200
    )

def main(req: func.HttpRequest) -> func.HttpResponse:
    return get_data(req)

