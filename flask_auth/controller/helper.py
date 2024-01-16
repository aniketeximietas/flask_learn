from datetime import datetime, timedelta
from flask import jsonify, session,request
from ..extensions import db
from ..models.employee import Employee
from flask_bcrypt import Bcrypt
# import jwt
from werkzeug.utils import secure_filename
import os
import phonenumbers
from wtforms.validators import DataRequired, ValidationError
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from email_validator import validate_email, EmailNotValidError

bcrypt=Bcrypt()
def create_employee(request_data):
    try:
        bcrypt = Bcrypt()
        email = request_data.get('email',"")
        phone = request_data.get('phone',"")

        if not email or not phone:
            return f'missing attribute'
        user = Employee.query.filter_by(email=email).first()
        if user:
            return "user already registered"
        usr = Employee.query.filter_by(phone=phone).first()
        if usr:
            return "Phone number exist"
        
        new_employee = Employee(
            email=request_data['email'],
            first_name=request_data['first_name'],
            last_name=request_data['last_name'],
            phone=request_data['phone'],
            password=request_data['password'],
            # image="filepath"
        )
        db.session.add(new_employee)
        db.session.commit()
        return jsonify(message='Employee created successfully', email=new_employee.email,
                    first_name=new_employee.first_name,
                    last_name=new_employee.last_name,
                    phone=new_employee.phone), 200
    except Exception as e:
        print(e)
        return jsonify(message=str(e))


def update_employee(employee_id, request_data):

    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify(message='Employee not found'), 404
    
    email = request_data.get('email',employee.email)
    if email!=employee.email:
        user = Employee.query.filter_by(email=email).first()
        if user:
            return "user already registered"
    ph = request_data.get('phone',employee.phone)
    if ph != employee.phone:
        usr = Employee.query.filter_by(phone=ph).first()
        if usr:
            return "Phone number exist"

    employee.email = request_data.get('email', employee.email)
    employee.first_name = request_data.get('first_name', employee.first_name)
    employee.last_name = request_data.get('last_name', employee.last_name)
    employee.phone = request_data.get('phone', employee.phone)
    passw=request_data.get('password',None)
    # print("password new in helper ",passw)
    if passw:
        employee.password = passw

    db.session.commit()
    # result = Employee.query.filter_by(id=employee_id).update({'phone': new_phone})
    # db.session.commit()
    return jsonify(message='Employee updated successfully', email=employee.email,
                   first_name=employee.first_name,
                   last_name=employee.last_name,
                   phone=employee.phone), 200


def login(request_data):
    bcrypt = Bcrypt()
    email = request_data.get('email')
    password = request_data.get('password')
    employee = Employee.query.filter_by(email=email).first()
    if not employee:
        return jsonify(message='Invalid email'), 401
    is_valid = bcrypt.check_password_hash(employee.password, password)
    if not is_valid:
        return jsonify(message='Invalid password'), 401
    else:
        employee.last_login_time = datetime.utcnow().isoformat()
        session['logged_in'] = True
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        # token = jwt.encode({
        #     'user':email,
        #     'expiration':str(datetime.utcnow()+timedelta(seconds=120))
        # },
        # "14cd27c2b8f34b45a0ea4fb0571547e4")
        employee.jwt_access_token = access_token
        employee.jwt_refresh_token = refresh_token
        # return jsonify({'token':token.decode('utf-8')})
        # employee.jwt_token = generate_jwt_token()
        db.session.commit()
        return jsonify(email=employee.email,
                       first_name=employee.first_name,
                       last_name=employee.last_name,
                       phone=employee.phone, message='Login successful', access_token=access_token, refresh_token=refresh_token,login_time=employee.last_login_time), 200
    # else:
    #     return jsonify(message='Invalid credentials'), 401


def logout(brearer_token):
    employee = Employee.query.filter_by(jwt_access_token=brearer_token).first()
    if employee:
        employee.jwt_access_token = None
        employee.jwt_refresh_token = None
        session['logged_in'] = False
        db.session.commit()
        return jsonify(message='Logout successful'), 200
    else:
        return jsonify(message='Employee not found'), 404


def issueAccessToken(refresh_token):
    
    emp = Employee.query.filter_by(jwt_refresh_token=refresh_token).first()
    if emp:
        access_token = create_access_token(identity=emp.email)
        refresh_token = create_refresh_token(identity=emp.email)
        emp.jwt_access_token = access_token
        emp.jwt_refresh_token = refresh_token
        db.session.commit()
        return jsonify(accessToken=emp.jwt_access_token,refresh_token=emp.jwt_refresh_token)
    else:
        return "Wrong Refresh Token"
    



def isThere(access_token):
    # tk = access_token['access_token']
    emp = Employee.query.filter_by(jwt_access_token=access_token).first()
    # print(emp)
    if emp:
        return True,emp.first_name
    else:
        return False


def isPassValid(passwd):
    SpecialSym = ['$', '@', '#', '%']
    if len(passwd) < 6:
        return 'passsword length should be at least 6'

    if len(passwd) > 20:
        return 'password length should be not be greater than 20'

    if not any(char.isdigit() for char in passwd):
        return 'Password should have at least one numeral'

    if not any(char.isupper() for char in passwd):
        return 'Password should have at least one uppercase letter'

    if not any(char.islower() for char in passwd):
        return 'Password should have at least one lowercase letter'

    if not any(char in SpecialSym for char in passwd):
        return 'Password should have at least one of the symbols $@#'
    else:
        return None


def isValidMail(mail):
    try:
        emailinfo = validate_email(
            mail, check_deliverability=False)
    except EmailNotValidError as e:
        return str(e)


def isValidPhone(phone):
    try:
        p = phonenumbers.parse(phone)
        if not phonenumbers.is_valid_number(p):
            raise ValueError()
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        return 'Invalid phone number'
