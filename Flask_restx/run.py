from flask import Flask
from flask_restx import Resource
from res import ns
from ext import api,db
from flask_migrate import Migrate

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db1.sqlite3"

api.init_app(app)
db.init_app(app)
api.add_namespace(ns)

migrate = Migrate(app,db)

if __name__ =="__main__":

    #using waitress
    # from waitress import serve
    # serve(app,port=8081)


    #from gevent.pywsgi import WSGIServer
    #http_server=WSGIServer(("127.0.0.1",8080),app)
    #http_server.serve_forever()
    app.run(debug=True)    
