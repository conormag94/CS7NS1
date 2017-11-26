import requests
from pygit2 import Repository, clone_repository, GitError

from radon.complexity import cc_visit

REPO_PATH = './repo'
REPO_URL = 'https://github.com/google/tangent.git'


def get_repo_obj():
    try:
        repo = Repository(REPO_PATH + '/.git')
    except GitError as e:
        repo = clone_repository(REPO_URL, REPO_PATH)
    return repo

def main():
    repo = get_repo_obj()
    print(repo)
    
if __name__ == '__main__':
    main()

