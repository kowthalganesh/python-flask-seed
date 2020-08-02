#!/usr/bin/python3
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from pandas_profiling import ProfileReport
from pandas_profiling.utils.cache import cache_file
from pathlib import Path
from flask_cors import CORS, cross_origin

import sqlite3
import dialogflow
import json
import dialogflow_v2 as dialogflow
import pandas as pd

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={"/liver": {"origins": "http://localhost:4200"}})

@app.route('/liver')
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def GET_RECORDS():
    conn1 = sqlite3.connect("chinook.db")
    conn1.row_factory = sqlite3.Row  
    cur = conn1.cursor()
    cur.execute("select * from liver") 
    data = []
    rows = cur.fetchall()
    for row in rows:
        data.append(dict(row))
    df = pd.DataFrame.from_dict(data)
    return json.dumps(data)

@app.route('/reports', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def GET_REPORTS():
    conn1 = sqlite3.connect("chinook.db")
    conn1.row_factory = sqlite3.Row  
    cur = conn1.cursor()
    cur.execute("select * from liver") 
    data = []
    rows = cur.fetchall()
    for row in rows:
        data.append(dict(row))
    df = pd.DataFrame.from_dict(data)    
    profile = ProfileReport(df, title="Indian Liver Patient Dataset (ILPD) report.html", explorative=True)
    profile.to_file(Path("Indian Liver Patient Dataset (ILPD) report.html"))

@app.route('/liversearch', methods=['POST'])
def POST_RECORDS():
    conn1 = sqlite3.connect("chinook.db")
    conn1.row_factory = sqlite3.Row  
    cur = conn1.cursor()
    cur.execute("select * from liver") 
    data = []
    rows = cur.fetchall()
    for row in rows:
        data.append(dict(row))
    df = pd.DataFrame.from_dict(data)
    probhability = 0
    df.append({"probhability": probhability}, ignore_index=True)
    item = request.data.decode('utf8')
    results = json.loads(item)
    result = df
    if results["ALT"] >= 25:
        probhability += 16
        result = df.loc[df["SgptAlamineAminotransferase"] <= results["ALT"]]
    if results["AST"] >= 40:
        probhability += 16
        result = result.loc[result["SgotAspartateAminotransferase"] <= results["AST"]]
    if results["ALP"] > 120:
        probhability += 16
        result = result.loc[result["AlkphosAlkalinePhosphotase"] <= results["ALP"]]
    if (results["albumin"] < 3.5 AND results["albumin"] > 5.0):
        probhability += 16
        result = result.loc[result["Albumin"] <= results["albumin"]]
    if (results["bilirubin"] < 0.1 AND results["bilirubin"] > 1.2):
        probhability += 16
        result = result.loc[result["DirectBilirubin"] <= results["bilirubin"]]
    if results["AFP"] > 10:
        probhability += 16
        result = result.loc[result["TotalProtiens"] <= results["AFP"]]
    print(probhability)
    result["probhability"] = probhability
    response = result.to_json(orient='records')
    print(response)
    return response
	
if __name__ == '__main__':
     app.run(port=3000)
