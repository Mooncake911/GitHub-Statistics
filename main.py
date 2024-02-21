from github import Github
import csv

SKIP_FILES = ['__init__.py']

lang_ext = {
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

languages = 'Python'


def process_repo_contents(contents, repo, csv_writer):
    for content in contents:
        if content.type == "dir":
            process_repo_contents(repo.get_contents(content.path), repo, csv_writer)
        elif (content.type == "file"
              and content.name.endswith(lang_ext[languages])
              and content.name not in SKIP_FILES):
            file_content = repo.get_contents(content.path).decoded_content
            code_lines = len(file_content.splitlines())
            csv_writer.writerow([repo.name, content.path, content.name, code_lines])
            # print(f"Repository:{repo.name}, Path:{content.path}, File Name:{content.name}, Code Length:{code_lines}")


def get_repo_file_info(repo, csv_writer):
    try:
        # Get the contents of the root folder of the repository
        contents = repo.get_contents("")
        # Processing the content recursively
        process_repo_contents(contents, repo, csv_writer)

    except Exception as e:
        print(f"Error processing the repository {repo.name}: {e}")


def main():
    access_token = 'Your GitHub API access token'
    g = Github(access_token)
    user = g.get_user()

    # Going through all the user's repositories
    with open("github.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Repo", "Path", "File", "Lines of Code"])

        for repo in user.get_repos():
            get_repo_file_info(repo, csv_writer)


if __name__ == "__main__":
    main()
