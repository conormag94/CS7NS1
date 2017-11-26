import requests
from pygit2 import Repository, clone_repository, GitError

from radon.complexity import cc_visit

REPO_DIR = './repo'
REPO_PATH = REPO_DIR + '/.git'
REPO_URL = 'https://github.com/google/tangent.git'


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

def main():
    repo = get_repo_obj()

    commit_hash = '418ae74aa28d35cb395d98bb3377609f11428af4'
    commit = repo.get(commit_hash)

    files_to_analyze = find_py_files(repo, commit.tree)
    for file in files_to_analyze:
        filetext = repo[file.id].data.decode()
        cc = calculate_average_cc(filetext)
        print(f'{file.name}\t{cc}')
    print(f'Complexity calculated for {len(files_to_analyze)} file(s)')

if __name__ == '__main__':
    main()

