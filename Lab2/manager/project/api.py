from flask import Blueprint, jsonify, request

from project import db
from project.models import Chunk

manager_blueprint = Blueprint('manager', __name__)

@manager_blueprint.route('/', methods=['GET'])
def hello_world():
    chunks = Chunk.query.all()
    for chunk in chunks:
    	print(chunk.message)
    return "Ay okay"