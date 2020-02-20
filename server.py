#!/usr/bin/python3
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import dialogflow
from google.api_core.exceptions import InvalidArgument
import dialogflow_v2 as dialogflow
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./irbot-rjibay-e94b1844aae0.json";        

db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)


class Employee(Resource):
    def get(self):
        DIALOGFLOW_PROJECT_ID = 'irbot-rjibay'
        DIALOGFLOW_LANGUAGE_CODE = 'en-US'
        SESSION_ID = 'kowthalganesh.kowthalraj@gmail.com'
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
        text = 'Hi IRBot!'
        text_input = dialogflow.types.TextInput(
            text=text, language_code=DIALOGFLOW_LANGUAGE_CODE)

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(
            session=session, query_input=query_input)

        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))
        return { 'dialog': response.query_result.fulfillment_text }

    def post(self):
        conn = db_connect.connect()
        print(request.json)
        LastName = request.json['LastName']
        FirstName = request.json['FirstName']
        Title = request.json['Title']
        ReportsTo = request.json['ReportsTo']
        BirthDate = request.json['BirthDate']
        HireDate = request.json['HireDate']
        Address = request.json['Address']
        City = request.json['City']
        State = request.json['State']
        Country = request.json['Country']
        PostalCode = request.json['PostalCode']
        Phone = request.json['Phone']
        Fax = request.json['Fax']
        Email = request.json['Email']
        query = conn.execute("insert into employees values(null,'{0}','{1}','{2}','{3}', \
                             '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}', \
                             '{13}')".format(LastName,FirstName,Title,
                             ReportsTo, BirthDate, HireDate, Address,
                             City, State, Country, PostalCode, Phone, Fax,
                             Email))
        return {'status':'success'}


class Employees(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from employees") # This line performs query and returns json result
        req = request.get_json(force=True)        
        # fetch action from json
        action = req.get('queryResult').get('action')
        print(query)
        resp = { 'dialog': [i[0] for i in query.cursor.fetchall()] }
        return make_response(jsonify(resp))
    
    def post(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from employees") # This line performs query and returns json result
        req = request.get_json(force=True)        
        # fetch action from json
        action = req.get('queryResult').get('action')
        fulfillment_text = ''
        result = query.cursor.fetchall() 
        for i in result:
            fulfillment_text = fulfillment_text +','+ i[1] +'-'+i[3]
        resp = {'fulfillmentText': fulfillment_text}
        print(resp)
        return jsonify(resp)
    
api.add_resource(Employees, '/employees') # Route_1

if __name__ == '__main__':
     app.run(port=3000)
