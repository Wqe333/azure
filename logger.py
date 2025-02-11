import logging
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
from functools import wraps
import pyodbc
import azure.functions as func

DEFAULT_LOG_LEVEL = "info"
DEFAULT_LOG_LEVEL_INT = 20

class IpLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IpLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_level=None):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True

        self.log_level = log_level
        self.logger = self.create_logger()

    def create_logger(self):
        logger = logging.getLogger("ip_logger")

        # Clear existing handlers to avoid duplicates
        if logger.hasHandlers():
            logger.handlers.clear()

        log_cfg = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }

        log_level = os.getenv("LOG_LEVEL") if not self.log_level else self.log_level
        logger.setLevel(log_cfg.get(log_level, DEFAULT_LOG_LEVEL_INT))

        # Add Application Insights handler for Azure Functions
        insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        if insights_connection_string:
            logger.addHandler(AzureLogHandler(connection_string=insights_connection_string))

        # Add console handler for Azure Functions live logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.propagate = False

        return logger

    def error(self, msg, error_code=None):
        if error_code:
            self.logger.error(f"Error Code: {error_code}, Message: {msg}")
        else:
            self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def get_log_level(self):
        return logging.getLevelName(self.logger.getEffectiveLevel())
    
class Custom_exceptions(Exception):
    def __init__(self, message, error_code):
        super().__init__(self.message)
        self.error_code = error_code

    def __str__(self):
        return f''




def get_db_connection():
    connection_string = os.getenv("DB_CONNECTION_STRING")
    return pyodbc.connect(connection_string)

def log_function_call(func_towrap):
    
    logger = IpLogger().logger  

    @wraps(func_towrap)
    def wrapper(req: func.HttpRequest, *args, **kwargs):
        function_name = func_towrap.__name__
        http_method = req.method  

        logger.info(f"Executing function: {function_name} [HTTP {http_method}]")

        if http_method not in ["GET", "POST", "PUT", "DELETE"]:
            logger.warning(f"Invalid HTTP method used: {http_method}. Allowed methods: GET, POST, PUT, DELETE.")
            return func.HttpResponse("Method not allowed.", status_code=405)

        conn = get_db_connection() 
        cursor = conn.cursor()
        try:
            kwargs['data'] = req.get_json() if http_method in ["POST"] else None
            kwargs['update'] = req.get_json() if (http_method == 'PUT' and "ProductID" in req.get_json()) else None
            kwargs['delete'] = req.get_json() if (http_method == 'DELETE' and len(req.get_json()) == 1 and "ProductID" in req.get_json()) else None
            kwargs["cursor"] = cursor 

            result = func_towrap(req, *args, **kwargs)

            conn.commit() 
            logger.info(f"Function {function_name} executed successfully [HTTP {http_method}]")

            return result 

        except pyodbc.Error as e:
            logger.exception(f"Database error in {function_name} [HTTP {http_method}]: {str(e)}")
            return func.HttpResponse("Database error. Please try again later.", status_code=500)

        except Exception as e:
            logger.exception(f"Unexpected error in {function_name} [HTTP {http_method}]: {str(e)}")
            return func.HttpResponse("An unexpected error occurred.", status_code=500)

        finally:
            cursor.close()
            conn.close()
            logger.info(f"Database connection closed for function: {function_name} [HTTP {http_method}]")

    return wrapper