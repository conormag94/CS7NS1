from flask import Blueprint, jsonify, request
from pygit2 import Repository, clone_repository, GitError

from project import db
from project.models import Chunk

REPO_DIR = './repo'
REPO_PATH = REPO_DIR + '/.git'
REPO_URL = 'https://github.com/google/tangent.git'

q = [0, 2, 4, 5]
cnt = 0

manager_blueprint = Blueprint('manager', __name__)

def check_repo():
    print("Checking if the git repo exists...")
    try:
        print("Repo found")
        repo = Repository(REPO_PATH)
    except GitError as e:
        print("Repo not found - cloning...")
        repo = clone_repository(REPO_URL, REPO_DIR)
    print("Finished!")

@manager_blueprint.before_app_first_request
def init():
    check_repo()

@manager_blueprint.route('/', methods=['GET'])
def hello_world():
    chunks = Chunk.query.all()
    for chunk in chunks:
    	print(chunk.message)
    
    global cnt
    result = q[cnt % 4]
    cnt += 1
    return str(result)