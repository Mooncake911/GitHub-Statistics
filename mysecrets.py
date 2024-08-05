import os
import subprocess
import shutil

from git import Repo


def clone_repo(repo_url, repo_path):
    """
    Clone repo from GitHub to local dir.
    """
    try:
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        Repo.clone_from(repo_url, repo_path)
        print(f"Git repository {repo_url} was cloned to {repo_path}.")

    except Exception as e:
        print(f"Error occurred during cloning Git repository: {e}")


def delete_repo(repo_path):
    """
    Delete local repo by repo_path.
    """

    def change_permissions(path):
        """
        Change permissions to all files by path.
        """
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.chmod(file_path, 0o777)  # Assign full access
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.chmod(dir_path, 0o777)  # Assign full access

    try:
        change_permissions(repo_path)
        shutil.rmtree(repo_path)
        print(f"Git repository was deleted by path: {repo_path}.")

    except FileNotFoundError:
        print(f"Git repository wasn't be found by path: {repo_path}.")

    except Exception as e:
        print(f"Error occurred during deleting Git repository: {e}")


def gitleaks_check_secrets(repo_path):
    """
    Check secrets with gitleaks.
    """
    secrets_path = f'secrets/gitleaks_report_{repo_path.split('/')[-1]}.json'

    try:
        scan_command = ["gitleaks_8.18.4_windows_x64/gitleaks.exe", "detect", "--source", repo_path,
                        "--report-format", "json", "--report-path", secrets_path]
        subprocess.run(scan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except Exception as e:
        print(f"Somthing went wrong in checking secrets: {e}")

    return secrets_path


def check_secrets(user, repository):
    repo_url = f'https://github.com/{user}/{repository}'
    repo_path = f'repository/{repository}'
    clone_repo(repo_url, repo_path)
    secrets_path = gitleaks_check_secrets(repo_path)
    delete_repo(repo_path)
    return secrets_path
