from github import Github
# import magic
import csv


def process_repo_contents(contents, repo, csv_writer):
    for content in contents:
        if content.type == "dir":
            process_repo_contents(repo.get_contents(content.path), repo, csv_writer)
        elif content.type == "file" and content.name.endswith('.py'):
            file_content = repo.get_contents(content.path).decoded_content
            code_lines = len(file_content.splitlines())
            if content.name != "__init__.py":
                csv_writer.writerow([repo.name, content.path, content.name, code_lines])
            # print(f"Repository:{repo.name}, Path:{content.path}, File Name:{content.name}, Code Length:{code_lines}")


def get_repo_file_info(repo, csv_writer):
    try:
        # Получаем содержимое корневой папки репозитория
        contents = repo.get_contents("")
        # Обрабатываем содержимое рекурсивно
        process_repo_contents(contents, repo, csv_writer)

    except Exception as e:
        print(f"Ошибка при обработке репозитория {repo.name}: {e}")


def main():
    access_token = "Your Token"
    g = Github(access_token)
    user = g.get_user()

    # Перебираем все репозитории пользователя
    with open("github.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Repository", "Path", "File Name", "Code Length"])

        for repo in user.get_repos():
            get_repo_file_info(repo, csv_writer)


if __name__ == "__main__":
    main()
