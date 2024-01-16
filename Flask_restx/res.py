from flask import request
from flask_restx import Namespace,Resource
from api_models import *
from ext import db
from models import Course,Student
ns = Namespace("think")
nss=Namespace("main")


@ns.route("/hey")
class hey(Resource):
    def get(self):
        language = request.args.get('language') 
        return f'Helloo {language}'
    def post(self):
        return {"this one":"is post"}

@nss.route("/hey")
class yyy(Resource):
    def get(self):
        language = request.args.get('language') 
        return f'Helloo {language}'
    def post(self):
        return {"this one":"is post"}

@ns.route("/course")    
class course(Resource):
    @ns.marshal_list_with(course_model)
    def get(self):
        return Course.query.all()
    @ns.expect(course_input_model)
    @ns.marshal_with(course_model)
    def post(self):
        cou =  Course(name=ns.payload["name"])
        db.session.add(cou)
        db.session.commit()
        return cou,201
    

@ns.route("/students")    
class student(Resource):
    @ns.marshal_list_with(student_model)
    def get(self):
        return Student.query.all()
    
    @ns.expect(student_input_model)
    @ns.marshal_with(student_model)
    def post(self):
        st = Student(name=ns.payload["name"],course_id=ns.payload["course_id"])
        db.session.add(st)
        db.session.commit()
        return st,201
    

@ns.route("/course/<int:id>")
class courseInd(Resource):
    @ns.marshal_with(course_model)
    @ns.marshal_with(error_model)
    def get(self,id):
        co = Course.query.get(id)
        if co == None:
            print("error")
            return {"error":"course not found"}
        return co
    


