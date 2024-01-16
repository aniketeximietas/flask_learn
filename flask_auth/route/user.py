from flask import Blueprint, request, session
from ..controller.helper import *
from ..extensions import db
from ..models.employee import Employee
from flask import send_from_directory
from werkzeug.utils import secure_filename

user = Blueprint("user", __name__)


@user.route('/create_employee', methods=['POST'])
def route_create_employee():
    request_data = request.get_json()
    return create_employee(request_data)


@user.route('/update_employee/<int:employee_id>', methods=['PATCH'])
def route_update_employee(employee_id):
    request_data = request.get_json()
    return update_employee(employee_id, request_data)


@user.route('/login', methods=['POST'])
def route_login():
    request_data = request.get_json()
    return login(request_data)


@user.route('/logout', methods=['GET'])
def route_logout():
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        bearer_token = authorization_header[len('Bearer '):]
        return logout(bearer_token)
    return "No valid Bearer token found",401


@user.route('/dashboard', methods=['GET'])
def isPresent():
    # access_token = request.get_json()
    authorization_header = request.headers.get('Authorization')

    if authorization_header and authorization_header.startswith('Bearer '):
        bearer_token = authorization_header[len('Bearer '):]
        isT,name=isThere(bearer_token)
        if isT:
            return f"HELLO {name} WELCOME TO EXIMIETAS"
        else:
            return "UNAUTHORIZED"

    return "No valid Bearer token found", 401
    # if not session.get('logged_in'):
    #     return "not logged in"
    # else:
    #     return "logged in"


@user.route('/request_access_token', methods=['GET'])
def access():
    # refresh_token = request.get_json()
    authorization_header = request.headers.get('Authorization')

    if authorization_header and authorization_header.startswith('Bearer '):
        bearer_token = authorization_header[len('Bearer '):]
        return issueAccessToken(bearer_token)

    return "No valid Bearer token found", 401

@user.route('/upload/<int:id>',methods=["POST"])
def upload(id):
    authorization_header = request.headers.get('Authorization')

    if authorization_header and authorization_header.startswith('Bearer '):
        bearer_token = authorization_header[len('Bearer '):]
        # return issueAccessToken(bearer_token)
    file=request.files["pic"]
    if not file:
        return "no file uploaded",400
    else:

        emp = Employee.query.get(id)
        if emp.jwt_access_token == bearer_token:
            filename = secure_filename(file.filename)
            if emp.image and os.path.exists(emp.image):
                os.remove(emp.image)
            path=os.path.join(os.path.abspath('img'), filename)
            print("gf   ",path)
            emp.image=path
            db.session.commit()
            file.save(path)
            return "file uploaded"
        else:
            return "not loggedin pass your access token"
    

@user.route('/profileimg/<int:id>',methods=["GET"])
def uploaded_file(id):
    user=Employee.query.get(id)
    if user:
        path=user.image
        directory,filename=os.path.split(path)
        
        return send_from_directory(directory, filename,mimetype="image/jpeg")    
    else:
        return "user not found"
