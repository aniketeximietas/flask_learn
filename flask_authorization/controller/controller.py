from datetime import datetime, timezone
from flask import jsonify, request, request_finished
from werkzeug.utils import secure_filename
from ext import db
import os
import re
from modals.models import Employee
from flask_jwt_extended import get_jwt_identity, jwt_required, unset_jwt_cookies, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from controller.jwt_tokn import access_token
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


# regX patterns
password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[a-zA-Z\d!@#$%^&*]{4,}$'
email_pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
phone_pattern = r"^(?:\+?(\d{10})|\+?(\d{13}))$"


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
upload_folder = 'flask_auth\media'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_employee():
    try:
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        password = request.form.get('password')

        new_employee = Employee(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            create_time=datetime.now(timezone.utc).isoformat()
        )
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>",new_employee.password)
        # Check if 'img_path' is present in the request files
        if 'img_path' in request.files:
            img_file = request.files['img_path']

            # Check if the file has an allowed extension
            if img_file and allowed_file(img_file.filename):
                # Securely generate a filename to avoid potential security issues
                filename = secure_filename(img_file.filename)

                # Ensure the target directory exists
                os.makedirs(upload_folder, exist_ok=True)

                # Save the file to the specified folder with a secure filename
                image_path = os.path.join(
                    os.path.abspath(upload_folder), filename)
                img_file.save(image_path)

                # Set the img_path attribute of the new_employee
                new_employee.img_path = image_path

        existing_employee = Employee.query.filter(
            Employee.email == new_employee.email).first()
        if existing_employee:
            return jsonify(message='Email already exists'), 400

        existing_employee = Employee.query.filter(
            Employee.phone == new_employee.phone).first()
        if existing_employee:
            return jsonify(message='Phone number already exists'), 400

        db.session.add(new_employee)
        db.session.commit()

        return jsonify(message='Employee created successfully'), 201

    except Exception as e:
        return jsonify(message=str(e)), 400


def update_employee(employee_id, request_data):
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify(message='Employee not found'), 404

        new_password = request_data.get('password')
        # emp = Employee(
        #     password=new_password
        # )
        print("___________________________________", new_password)

        new_email = request_data.get('email', employee.email)
        new_phone = request_data.get('phone', employee.phone)

        # Validate new phone number if it has changed
        if new_phone != employee.phone:
            existing_employee = Employee.query.filter(
                Employee.phone == new_phone).first()
            if existing_employee:
                return jsonify(message='Phone number already exists'), 400

        # Update employee data
        if new_password:
            employee.password = new_password  # Fix the typo here
            print("__________________________",employee.password)
        employee.email = new_email or employee.email
        employee.first_name = request_data.get('first_name', employee.first_name)
        employee.last_name = request_data.get('last_name', employee.last_name)
        employee.phone = new_phone or employee.phone
        employee.img_path = request_data.get('img_path', employee.img_path)

        db.session.commit()
        return jsonify(message='Employee data updated successfully'), 200
    except Exception as e:
        return jsonify(message=str(e)), 400



def update_employe(employee_id):
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify(message='Employee not found'), 404

        new_password = request.form.get('password')
        print("___________________________________",new_password)
        new_email = request.form.get('email', employee.email)
        new_phone = request.form.get('phone', employee.phone)

        # Validate new phone number if it has changed
        if new_phone != employee.phone:
            existing_employee = Employee.query.filter(
                Employee.phone == new_phone).first()
            if existing_employee:
                return jsonify(message='Phone number already exists'), 400

        # Update employee data
        if new_password:
            employee.password = new_password  # Fix the typo here
            print("__________________________",employee.password)
        employee.email = new_email or employee.email
        employee.first_name = request.form.get(
            'first_name', employee.first_name)
        employee.last_name = request.form.get('last_name', employee.last_name)
        employee.phone = new_phone or employee.phone

        # Check if 'img_path' is present in the request files
        if 'img_path' in request.files:
            img_file = request.files['img_path']

            # Check if the file has an allowed extension
            if img_file and allowed_file(img_file.filename):
                # Securely generate a filename to avoid potential security issues
                filename = secure_filename(img_file.filename)

                # Ensure the target directory exists
                os.makedirs(upload_folder, exist_ok=True)

                # Save the file to the specified folder with a secure filename
                image_path = os.path.join(
                    os.path.abspath(upload_folder), filename)
                img_file.save(image_path)

                # Set the img_path attribute of the new_employee
                employee.img_path = image_path

        db.session.commit()
        return jsonify(message='Employee data updated successfully'), 200
    except Exception as e:
        return jsonify(message=str(e)), 400


def login(request_data):
    bcrypt = Bcrypt()
    request_email = request_data.get('email')
    request_password = request_data.get('password')
    employee = Employee.query.filter_by(email=request_email).first()

    if not re.match(password_pattern, request_password):
        return jsonify(message='Please enter a valid alphanumeric password'), 400

    if employee:
        stored_hash = employee.password
        try:
            is_valid_password = bcrypt.check_password_hash(stored_hash, request_password)
        except ValueError as e:
            return jsonify(message=f'Error checking password: {str(e)}'), 500

        if is_valid_password:
            tokens = access_token(request_email)
            print(tokens[0])

            employee.last_login_time = datetime.now(timezone.utc).isoformat()
            employee.jwt_token = tokens[0]
            employee.ref_jwt_token = tokens[1]
            db.session.commit()

            return jsonify(message='Login successful'), 200
        else:
            return jsonify(message='Incorrect password'), 401
    else:
        return jsonify(message='Employee not found or Invalid Email/Password'), 404


def logout(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify(message='Employee not found'), 404
    if employee.jwt_token is None:
        return jsonify(message='User not signed in yet'), 200
    employee.jwt_token = None
    db.session.commit()
    return jsonify(message='Logout successful'), 200


def logout2():
    try:
        # Verify the presence of a JWT token in the request
        verify_jwt_in_request()

        # Get the bearer token from the Authorization header
        bearer_token = request.headers.get('Authorization')

        # Check if the token is provided
        if not bearer_token or not bearer_token.startswith('Bearer '):
            return jsonify(message='Bearer token is missing or invalid'), 401

        jwt_token = bearer_token.split(' ')[1]

        # Get the identity of the current user from the JWT token
        current_user = get_jwt_identity()

        # Log out the user by setting JWT token to None
        # Note: This assumes you have a valid way to decode the JWT and obtain the user identity
        # If not, you may need to adjust this part based on your actual implementation
        # For example, if the JWT itself contains the user ID, you can use it directly
        # If you are using an alternative approach for decoding the JWT, adjust accordingly
        employee = Employee.query.filter_by(id=current_user).first()

        if not employee:
            return jsonify(message='Employee not found'), 404

        if employee.jwt_token is None:
            return jsonify(message='User not signed in yet'), 200

        employee.jwt_token = None
        db.session.commit()

        return jsonify(message='Logout successful'), 200

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify(message='Internal server error'), 500


def checking_user(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify(message='Employee not found'), 404
    elif employee.jwt_token is None:
        return jsonify(message='Please login'), 200
    else:
        firstName = employee.first_name
        lastName = employee.last_name
        email = employee.email
        phone = employee.phone
        createdAt = employee.create_time
        loginTime = employee.last_login_time

        return jsonify(message='Welcome to Eximietas',
                       first_name=firstName,
                       last_name=lastName,
                       email=email,
                       phone=phone,
                       created_at=createdAt,
                       login_time=loginTime), 200


def refresh(email):
    refresh_email = email
    employee = Employee.query.filter_by(email=refresh_email).first()
    if employee is None:
        return jsonify(message='Employee not found'), 404
    tokens = access_token(refresh_email)
    employee.jwt_token = tokens[0]
    employee.ref_jwt_token = tokens[1]
    db.session.commit()
    return jsonify(message='Refresh successful'), 200


def checked_user():
    try:
        # Verify the presence of a JWT token in the request
        verify_jwt_in_request()

        # Get the bearer token from the Authorization header
        bearer_token = request.headers.get('Authorization')

        # Check if the token is provided
        if not bearer_token or not bearer_token.startswith('Bearer '):
            return jsonify(message='Bearer token is missing or invalid'), 401

        # jwt_token = bearer_token.split(' ')[1]
        # print(jwt_token)
        # Get the identity of the current user from the JWT token
        current_user = get_jwt_identity()
        print(current_user)

        # Log out the user by setting JWT token to None
        # Note: This assumes you have a valid way to decode the JWT and obtain the user identity
        # If not, you may need to adjust this part based on your actual implementation
        # For example, if the JWT itself contains the user ID, you can use it directly
        # If you are using an alternative approach for decoding the JWT, adjust accordingly
        employee = Employee.query.filter_by(id=current_user).first()
        if not employee:
            return jsonify(message='Employee not found'), 404

        if employee.jwt_token is None:
            return jsonify(message='User not signed in yet'), 200

        firstName = employee.first_name
        lastName = employee.last_name
        email = employee.email
        phone = employee.phone
        createdAt = employee.create_time
        loginTime = employee.last_login_time

        return jsonify(message='Welcome to Eximietas',
                       first_name=firstName,
                       last_name=lastName,
                       email=email,
                       phone=phone,
                       created_at=createdAt,
                       login_time=loginTime), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify(message='Internal server error'), 500


def display_img(employee_id):
    emp = Employee.query.filter_by(id=employee_id).first()
    if not emp:
        return jsonify(message="Employee is not signed up"), 404
    else:
        return emp.img_path


def display_image():
    try:
        # Verify the presence of a JWT token in the request
        verify_jwt_in_request()

        # Get the bearer token from the Authorization header
        bearer_token = request.headers.get('Authorization')

        # Check if the token is provided
        if not bearer_token or not bearer_token.startswith('Bearer '):
            return jsonify(message='Bearer token is missing or invalid'), 401

        jwt_token = bearer_token.split(' ')[1]

        # Get the identity of the current user from the JWT token
        current_user = get_jwt_identity()

        # Log out the user by setting JWT token to None
        # Note: This assumes you have a valid way to decode the JWT and obtain the user identity
        # If not, you may need to adjust this part based on your actual implementation
        # For example, if the JWT itself contains the user ID, you can use it directly
        # If you are using an alternative approach for decoding the JWT, adjust accordingly
        employee = Employee.query.filter_by(id=current_user).first()

        if employee.jwt_token is None:
            return jsonify(message='User not signed in yet'), 200

        if not employee:
            return jsonify(message='Employee not found'), 404
        else:
            return employee.img_path
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify(message='Internal server error'), 500
