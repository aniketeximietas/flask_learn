from controller.controller import *
import os
from flask import Blueprint,render_template, send_from_directory
from flask import request


ns = Blueprint("ns", __name__)

upload_folder = 'flask_auth\media'


@ns.route('/')
def home():
    return "<h1>Started the program </h1><br><h1>We welcome you</h1>"


@ns.route('/dashboard')
def Dashbord():
    return "<h1>Welcome to the dashboard</h1>"


@ns.route('/create_employee', methods=['POST'])
def route_create_employee():
    # request_data = request.get_json()
    return create_employee()


@ns.route('/update_employee/<int:employee_id>', methods=['PATCH'])
def route_update_employee(employee_id):
    request_data = request.get_json()
    return update_employee(employee_id, request_data)

@ns.route('/update_employe/<int:employee_id>', methods=['PATCH'])
def route_update_employe(employee_id):
    return update_employe(employee_id)

@ns.route('/login', methods=['POST'])
def user_login():
    request_data = request.get_json()
    return login(request_data)


@ns.route('/logout/<int:employee_id>', methods=['POST'])
def route_logout(employee_id):
    return logout(employee_id)


@ns.route('/logout', methods=['POST'])
def route_bearer_logout():
    return logout2()


@ns.route('/refresh/<int:employee_id>', methods=['POST'])
def reload_access_token(employee_id):
    employee = Employee.query.filter_by(id=employee_id).first()
    if not employee:
        return jsonify(message='Invalid Id'), 404
    if employee.ref_jwt_token is None:
        return jsonify(message='User not loged in yet'), 400
    eml = employee.email
    return refresh(eml)


@ns.route('/refresh/<string:refresh>', methods=['POST'])
def reload_acces_token(refresh):
    employee = Employee.query.filter_by(ref_jwt_token=refresh).first()
    eml = employee.email
    return refresh(eml)


@ns.route('/dashboard/<int:employee_id>', methods=['POST'])
def display_user(employee_id):
    return checking_user(employee_id)


@ns.route('/dashboard', methods=['POST'])
def check_user():
    return checked_user()

@ns.route('/display/<int:employee_id>', methods=['GET','POST'])
def display(employee_id):
    img = Employee.query.filter(Employee.id == employee_id).first()

    if img:
        path = img.img_path
        print(path)

        directory, filename = os.path.split(path)
        print(directory)
        print(filename)
        return send_from_directory(directory, filename, mimetype='image/jpeg')
    else:
        return jsonify(message='Can\'t fetch the image'), 404
    
# @ns.route('/display/<string:name>', methods=['GET'])
# def displayN(name):
#     image_path = f'flask_auth/media/{name}'
#     return render_template('display.html', image_path=image_path)
