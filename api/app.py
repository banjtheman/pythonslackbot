"""
  app.py
    Purpose:
        API layer for pythonslackbot
"""

# Python Library Imports
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import os
import json
import random
import time
import pandas as pd, numpy as np
import csv


import sys
from io import StringIO
import contextlib

application = Flask(__name__)
CORS(application)


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


@application.route("/health")
def health():
    return jsonify({"healthy": "true"})



@application.route("/run_code")
def run_code():

    jsonResp = {}


    code = request.args.get("code")
    print("Got this as code " + str(code))
    jsonResp["input"] = code

    with stdoutIO() as s:
        try:
            exec(code,globals())
            jsonResp["status"] = "success"
            jsonResp["output"] = s.getvalue()
            try:
                jsonResp["eval"] = eval(code)
            except:
                jsonResp["eval"] = ""
        except Exception as e:
            print(e)
            print("Something wrong with the code")
            jsonResp["status"] = "error"
            jsonResp["error"] = str(e)


    return jsonify(jsonResp)



if __name__ == "__main__":
    application.run(host="0.0.0.0", port="9005") 