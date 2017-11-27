import os
import random
import time

import requests
from pygit2 import Repository, clone_repository, GitError

from radon.complexity import cc_visit

REPO_DIR = './repo'
REPO_PATH = REPO_DIR + '/.git'
REPO_URL = 'https://github.com/rubik/radon.git'
# REPO_URL = 'https://github.com/KupynOrest/DeblurGAN.git'
WORK_URL = os.getenv('WORK_URL')

def get_repo_obj():
    """
    Return a repo object. 
    If the git repo hasn't been cloned, clone it and return a repo object
    """
    try:
        repo = Repository(REPO_PATH)
    except GitError as e:
        repo = clone_repository(REPO_URL, REPO_DIR)
    return repo


def find_py_files(repo, current_dir):
    """
    Recursively walk the repo at a certain commit and return all Python files
    to be analyzed
    """
    py_files = []
    for entry in current_dir:
        # If the object is a directory, recurse down
        if entry.type == 'tree':
            py_files += find_py_files(repo, repo[entry.id])
        elif entry.name.endswith('.py'):
            py_files.append(entry)
    return py_files


def calculate_average_cc(filetext):
    complexities = []
    complexity_objs = cc_visit(filetext)

    for obj in complexity_objs:
        complexities.append(obj.complexity)

    total = sum(complexities)

    try:
        return total / len(complexities)
    except ZeroDivisionError:
        return 0.0

def ask_for_work():
    work = requests.get(WORK_URL)
    if work.status_code == requests.codes.ok:
        return work.json()["commit"]
    else:
        return None

def send_results(average_cc, commit_hash):
    results = {
        "commit": commit_hash,
        "complexity": average_cc
    }
    r = requests.post(WORK_URL, json=results)

def main():
    repo = get_repo_obj()

    commit_hash = ask_for_work()

    while commit_hash is not None:
        cc_list = []
        commit = repo.get(commit_hash)

        files_to_analyze = find_py_files(repo, commit.tree)
        for file in files_to_analyze:
            try:
                filetext = repo[file.id].data
                cc = calculate_average_cc(filetext)
                cc_list.append(cc)
            except SyntaxError:
                guess_cc = random.randint(0, len(cc_list)-1)
                cc_list.append(cc_list[guess_cc])
        
        overall_avg = sum(cc_list) / len(cc_list)
        print(f'{commit_hash}: {overall_avg} ({len(files_to_analyze)} file(s))')

        send_results(overall_avg, commit_hash)
        
        sleepy_time = random.randint(0, 1)
        time.sleep(sleepy_time)
        
        commit_hash = ask_for_work()

if __name__ == '__main__':
    main()

