from flask import Blueprint, jsonify, request
from pygit2 import Repository, clone_repository, GitError

from project import db
from project.models import Chunk

REPO_DIR = './repo'
REPO_PATH = REPO_DIR + '/.git'
REPO_URL = 'https://github.com/google/tangent.git'

commits_list = []
next_task = 0

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

def get_commits():
    global commits_list

    repo = Repository(REPO_PATH)
    for commit in repo.walk(repo.head.target):
        commits_list.append(commit.id)

@manager_blueprint.before_app_first_request
def init():
    check_repo()
    get_commits()

@manager_blueprint.route('/', methods=['GET'])
def hello_world():
    chunks = Chunk.query.all()
    for chunk in chunks:
    	print(chunk.message)
    
    global commits_list
    global next_task

    result = commits_list[next_task % len(commits_list)]
    next_task += 1
    return str(result)

@manager_blueprint.route('/work', methods=['GET'])
def get_work():
    global commits_list
    global next_task

    try:
        commit_hash = str(commits_list[next_task])
        next_task += 1
        return jsonify({'commit': commit_hash}), 200
    except IndexError:
        return jsonify({"commit": None}), 404
