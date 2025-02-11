import unittest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import GET.get_fun as get
import POST.post_fun as post
import UPDATE.update_fun as update
import azure.functions as func


def test_get_products():
    req = func.HttpRequest(method="GET", url="/api/GET", body=None)
    response = get.main(req)

    assert response.status_code == 200
    data = json.loads(response.get_body())
    assert "data" in data 

def test_post_product():
    req_body = json.dumps({"Name": "Laptop", "Price": 2500, "Stock": 10})
    req = func.HttpRequest(method="POST", url="/api/POST", body=req_body.encode("utf-8"))

    response = post.main(req)

    assert response.status_code == 200
    assert b"Item created successfully" in response.get_body()

def test_update_product():
    req_body = json.dumps({"ProductID": 1, "Price": 2700})
    req = func.HttpRequest(method="PUT", url="/api/UPDATE", body=req_body.encode("utf-8"))

    response = update.main(req)

    assert response.status_code == 200
    assert b"Item updated successfully" in response.get_body()