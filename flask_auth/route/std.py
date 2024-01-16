from flask import Blueprint,request
from ..controller.helper import *
std = Blueprint("std",__name__)


@std.route('/create_employee', methods=['POST'])
def route_create_employee():
    return "helloooo"

