import os
import time
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


def remove_old_files(age_limit_hours=1):
    """
    Delete files from folder_path, if they were created more than age_limit_hours.

    :param age_limit_hours: Age limit of files to remove.
    """
    current_time = time.time()
    age_limit_seconds = age_limit_hours * 3600

    folder_paths = [PROGRESS_FOLDER, REPOSITORY_FOLDER, SECRETS_FOLDER]
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder was created: {folder_paths}")

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if os.path.isfile(file_path):
                file_creation_time = os.path.getctime(file_path)

                if (current_time - file_creation_time) > age_limit_seconds:
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
