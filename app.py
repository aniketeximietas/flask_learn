from flask import Flask, request, jsonify
from ext import init_db, db
from flask_migrate import Migrate
from modals.models import *
from flask_jwt_extended import JWTManager
from controller import *
from route.routes import ns
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

bcrypt = Bcrypt(app)
# Initialize SQLAlchemy
init_db(app)

# Create the database and tables
with app.app_context():
    db.create_all()

app.register_blueprint(ns)
if __name__ == '__main__':
    app.run(debug=True)
