from datetime import datetime,timezone
from flask import jsonify
import phonenumbers
from ext import db
from email_validator import validate_email, EmailNotValidError
import re
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt
bcrypt=Bcrypt()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    create_time = db.Column(db.String, default=lambda: datetime.now(timezone.utc).isoformat())
    last_login_time = db.Column(db.String, default=None)
    jwt_token = db.Column(db.String(200), default=None)
    ref_jwt_token = db.Column(db.String(200), default=None)
    img_path = db.Column(db.String(200), default=None)
    
    
    @validates("email")
    def validate_email(self, k, email):
        isValid = isValidMail(email)
        print(isValid)
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
    def validate_password(self, key, passsword):
        bcrypt=Bcrypt()
        isValidPass = isPassValid(passsword)
        if not isValidPass:
            return bcrypt.generate_password_hash(passsword).decode('utf-8')
        else:
            raise ValueError(isValidPass)

def isValidMail(mail):
    try:
        # Check if there are uppercase letters in the email address
        if any(char.isupper() for char in mail):
            raise EmailNotValidError("Gmail addresses should not contain uppercase letters.")

        # Validate the email address (this may include additional checks)
        emailinfo = validate_email(mail, check_deliverability=False)

    except EmailNotValidError as e:
        return str(e)

    # return "Email is valid."

def isValidPhone(phone):
    try:
        if phone[0] == '+' and len(phone) == 13:
            p = phonenumbers.parse(phone)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        elif len(phone) == 10:
            # Assuming it's a 10-digit number (without country code)
            p = phonenumbers.parse("+91" + phone)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        else:
            raise ValueError()
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        return 'Invalid phone number'
def isPassValid(passwd):
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
    SpecialSym = ['$', '@', '#', '%','!']
    return (
    f'Password should have at least one of the symbols: {SpecialSym}'
    if all(char not in SpecialSym for char in passwd)
    else None
)







