import requests
import streamlit as st
import pandas as pd

from configs import SKIP_FILES, LANG_EXT


def count_lines_in_repo(data, user, ext, repo, repo_lines=0, path=''):
    repo_url = f'https://api.github.com/repos/{user}/{repo}/contents/{path}'

    try:
        response = requests.get(repo_url, headers={'Authorization': f'token {st.secrets.GITHUB_TOKEN}'})
        response.raise_for_status()
        for content in response.json():
            if content['type'] == 'file':
                if content['name'].endswith(ext) and content['name'] not in SKIP_FILES:
                    file_url = content['download_url']
                    file_content = requests.get(file_url).text
                    code_lines = len(file_content.split('\n'))
                    repo_lines += code_lines
                    data.append([repo, content['path'], content['name'], code_lines])
            elif content['type'] == 'dir':
                subdir_path = f"{path}/{content['name']}" if path else content['name']
                repo_lines = count_lines_in_repo(data, user, ext, repo, repo_lines, subdir_path)

    except requests.exceptions.RequestException as e:
        st.sidebar.error(e)

    return repo_lines


def get_progress(user, language, repos):
    data = []
    total_lines = 0

    progress_bar = st.progress(0)
    processing_message = st.empty()
    metrics_message = st.empty()
    repo_metrics_message = st.empty()

    for i, repo in enumerate(repos, start=1):
        repo_lines = count_lines_in_repo(data, user, LANG_EXT[language], repo)
        total_lines += repo_lines
        # Display progress in real time
        progress_bar.progress(i / len(repos))
        processing_message.code(f'Processing: {repo}')
        metrics_message.info(f'𝖳𝗈𝗍𝖺𝗅 𝖫𝗂𝗇𝖾𝗌 𝗈𝖿 {language}: {total_lines}')
        repo_metrics_message.success(f'𝖳𝗈𝗍𝖺𝗅 𝖱𝖾𝗉𝗈𝗌𝗂𝗍𝗈𝗋𝗂𝖾𝗌: {i}')

    df = pd.DataFrame(data, columns=['Repo', 'Path', 'File', 'Lines of Code'])
    filename = f'progress/{user}_{language}.csv'
    df.to_csv(filename, index=False)

    return filename
