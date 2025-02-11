import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def set_env_variables():
    os.environ["DB_CONNECTION_STRING"] = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:ecommerce-server121.database.windows.net,1433;Database=EcommerceDB;Uid=adminuser;Pwd={Qwerty123@};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
