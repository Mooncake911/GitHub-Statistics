import os
import platform


OS_TYPE = platform.system()

SKIP_FILES = ['__init__.py']

LANG_EXT = {
    'Python': '.py',
    'Java': '.java',
    'JavaScript': '.js',
    'C': '.c',
    'C++': '.cpp',
    'C#': '.cs',
    'TypeScript': '.ts',
    'PHP': '.php',
    'Swift': '.swift',
    'Go': '.go'
}

PROGRESS_FOLDER = "progress"
REPOSITORY_FOLDER = "repository"
SECRETS_FOLDER = "secrets"


def create_folders():
    folder_paths = [PROGRESS_FOLDER, REPOSITORY_FOLDER, SECRETS_FOLDER]
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    return True
