from ext import db 

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
    students = db.relationship("Student", back_populates="course")


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    course_id = db.Column(db.ForeignKey("course.id"))

    course = db.relationship("Course", back_populates="students")


class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    area = db.Column(db.Integer)

class Country(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    volume = db.Column(db.Integer)

class Hat(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    length = db.Column(db.Integer)

class odisha(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    volume = db.Column(db.Integer)    


class yyyy(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    volume = db.Column(db.Integer)  