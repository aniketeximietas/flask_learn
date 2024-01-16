import re
from datetime import datetime
from sqlalchemy.orm import validates
from email_validator import validate_email, EmailNotValidError
from ..extensions import db
import phonenumbers
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
# from ..controller.helper import bcrypt


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    create_time = db.Column(db.String, default=str(datetime.utcnow().isoformat()))
    last_login_time = db.Column(db.String, default=None)
    jwt_access_token = db.Column(db.String, default=None)
    jwt_refresh_token = db.Column(db.String, default=None)
    image = db.Column(db.String,default=None)

    @validates("email")
    def validate_status(self, k, email):
        isValid = isValidMail(email)
        # print(isValid)
        if isValid:
            raise ValueError(isValid)
        else:
            return email

    @validates("phone")
    def validate_phone(self, k, phone):
        isPhone = isValidPhone(phone)
        if isPhone:
            raise ValueError(isPhone)
        else:
            return phone

    @validates("password")
    def validate_password(self, k, passsword):
        # bcrypt=Bcrypt()
        isValidPass = isPassValid(passsword)
        print("pass in emp ",isValidPass)
        if not isValidPass:
            return bcrypt.generate_password_hash(passsword).decode('utf-8')
        else:
            raise ValueError(isValidPass)


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


class Erd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    create_time = db.Column(db.String, default=str(datetime.utcnow().isoformat()))
    last_login_time = db.Column(db.String, default=None)
    jwt_access_token = db.Column(db.String, default=None)
    jwt_refresh_token = db.Column(db.String, default=None)
    image = db.Column(db.String,default=None)
