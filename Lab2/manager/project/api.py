import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Blueprint, jsonify, request
from pygit2 import Repository, clone_repository, GitError

from project import db
from project.models import Chunk

REPO_DIR = './repo'
REPO_PATH = REPO_DIR + '/.git'
REPO_URL = 'https://github.com/rubik/radon.git'
# REPO_URL = 'https://github.com/KupynOrest/DeblurGAN.git'

commit_list = []
work_list = []
commit_complexities = []
next_task = 0
graphed = False

manager_blueprint = Blueprint('manager', __name__)

def finish():
    global commit_complexities
    global commit_list
    global graphed

    if not graphed:
        graphed = True
        x_axis = list(range(len(commit_list)))
        y_axis = commit_complexities
        plt.plot(x_axis, y_axis.reverse())
        plt.xlabel('Commit Number')
        plt.ylabel('Mean Cyclomatic Complexity')
        plt.savefig('graph.png')    

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
    global commit_list
    global work_list
    global commit_complexities

    repo = Repository(REPO_PATH)
    for commit in repo.walk(repo.head.target):
        commit_list.append(str(commit.id))
        work_list.append(str(commit.id))
        commit_complexities.append(0.0)

@manager_blueprint.before_app_first_request
def init():
    check_repo()
    get_commits()

@manager_blueprint.route('/', methods=['GET'])
def hello_world():
    return "Use /work endpoint"

@manager_blueprint.route('/work', methods=['GET'])
def get_work():
    global commit_complexities
    global commit_list
    global work_list
    global next_task

    try:
        commit_hash = str(work_list[next_task % len(work_list)])
        next_task += 1
        return jsonify({'commit': commit_hash}), 200
    except IndexError:
        return jsonify({"commit": None}), 404
    except ZeroDivisionError:
        for i in range(len(commit_list)):
            print(f'{i}: {commit_complexities[i]} <{commit_list[i]}>')
        print("Graphing")
        finish()
        return jsonify({"commit": None}), 404

@manager_blueprint.route('/work', methods=['POST'])
def work_result():
    result = request.get_json()

    commit = result.get("commit")
    complexity = result.get("complexity")

    # print(f'{commit}: {complexity}')
    
    global commit_complexities
    global work_list
    global commit_list

    if len(work_list) != 0:
        idx = commit_list.index(commit)
        commit_complexities[idx] = complexity
        try:
            work_list.remove(commit)
        except ValueError:
            print("\tCommit already completed")
    print(f'{len(work_list)} commits remaining')

    response = {"message": "sound m8"}
    return jsonify(response), 200
