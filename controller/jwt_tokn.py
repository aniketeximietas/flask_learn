import jwt
import datetime
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
import random
from modals.models import Employee

# Move the initialization of JWTManager inside the access_token function


def access_token(eml):
      # Initialize JWTManager with your Flask application

    employee = Employee.query.filter_by(email=eml).first()
    if not employee:
        # Handle the case when the employee is not found
        return None, None

    fname = employee.first_name
    lname = employee.last_name
    uid = employee.id

    # Convert uid to a string before concatenating
    username = str(uid) 
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return access_token, refresh_token
