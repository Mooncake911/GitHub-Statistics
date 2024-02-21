import os
import datetime
import requests
import streamlit as st
import subprocess
import json

from statsplots import draw_plots


SKIP_FILES = ['__init__.py']

DATA = []
TOTAL_LINES = 0


def run_gitleaks(user, repo):
    repo_url = f'https://github.com/{user}/{repo}.git'
    output_file = f"{user}_secrets.txt"

    cmd = f'chmod +x /app/cmc/gitleaks && /app/cmc/gitleaks --repo-url={repo_url} --report={output_file}'
    subprocess.run(cmd, shell=True)


# st.sidebar.checkbox('Look for secrets?', key='run_secrets_key')
# st.sidebar.checkbox('Show secrets', key='show_secrets_key')
# if st.session_state.run_secrets:
#     for x in repos:
#         run_gitleaks(user, x)
# if st.session_state.show_secrets:
#     secrets_file = f"{user}_secrets.txt"
#     with open(secrets_file, 'r') as f:
#         secrets = f.read()
#         st.code(secrets)
#         st.markdown(f'<a href="{secrets_file}" download>Download {user} secrets</a>', unsafe_allow_html=True)


def count_lines_in_files(lang_ext, user, repo, path=''):
    global TOTAL_LINES, DATA
    repo_url = f'https://api.github.com/repos/{user}/{repo}/contents/{path}'

    try:
        response = requests.get(repo_url, headers={'Authorization': f'token {st.secrets.GITHUB_TOKEN}'})
        response.raise_for_status()
        for content in response.json():
            if (content['type'] == 'file'
                    and content['name'].endswith(lang_ext)
                    and content['name'] not in SKIP_FILES):
                file_url = content['download_url']
                file_content = requests.get(file_url).text
                code_lines = len(file_content.split('\n'))
                TOTAL_LINES += code_lines
                DATA.append([repo, content['path'], content['name'], code_lines])
            elif content['type'] == 'dir':
                subdir_path = f"{path}/{content['name']}" if path else content['name']
                count_lines_in_files(lang_ext, user, repo, subdir_path)

    except requests.exceptions.RequestException as e:
        st.sidebar.error(e)


def get_all_user_repos(user):
    url = f'https://api.github.com/users/{user}/repos'
    params = {'type': 'all', 'sort': 'full_name', 'direction': 'asc'}

    try:
        repos = requests.get(url, params=json.dumps(params), headers={'Authorization': f'token {st.secrets.GITHUB_TOKEN}'})
        repos.raise_for_status()
        st.sidebar.success(f'Fetching repositories for {user}')
        return [r['name'] for r in repos.json()]

    except requests.exceptions.RequestException as e:
        st.sidebar.error(e)
        return []


def main():
    st.set_page_config(layout='wide')
    logo_url = 'https://raw.githubusercontent.com/NoDataFound/CMC/main/githublogo.png'
    st.sidebar.markdown(
        f"<div style='text-align: center'><img src='{logo_url}' width='40%'></div>",
        unsafe_allow_html=True,
    )

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

    with st.sidebar.form(key='SidebarForm'):
        st.title('Lines of Code Counter')
        user = st.text_input('Enter GitHub Username').replace(' ', '')
        language = st.selectbox('Select Language', list(lang_ext.keys()))
        button = st.form_submit_button(label='Run')
        to_csv = st.checkbox('Save to .csv', value=True)

    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'language' not in st.session_state:
        st.session_state.language = None
    if 'repos' not in st.session_state:
        st.session_state.repos = None
    if 'result' not in st.session_state:
        st.session_state.result = None

    if button:
        if not user or not language:
            st.sidebar.error(f'GitHub Username or Language is empty. Please try again!')
            return

        elif st.session_state.user != user or st.session_state.language != language:

            if st.session_state.user != user:
                st.session_state.repos = get_all_user_repos(user)
            repos = st.session_state.repos

            st.sidebar.code(f'Found {len(repos)} repositories for {user}.')

            progress_bar = st.progress(0)
            processing_message = st.empty()
            metrics_message = st.empty()
            repo_metrics_message = st.empty()

            for i, repo in enumerate(repos):
                count_lines_in_files(lang_ext[language], user, repo)
                # Display progress
                progress_bar.progress((i + 1) / len(repos))
                processing_message.code(f'Processing: {repo}')
                metrics_message.info(f'𝖳𝗈𝗍𝖺𝗅 𝖫𝗂𝗇𝖾𝗌 𝗈𝖿 {language}: {TOTAL_LINES}')
                repo_metrics_message.success(f'𝖳𝗈𝗍𝖺𝗅 𝖱𝖾𝗉𝗈𝗌𝗂𝗍𝗈𝗋𝗂𝖾𝗌: {i + 1}')

            st.session_state.user = user
            st.session_state.language = language
            st.session_state.result = DATA

        elif st.session_state.user == user and st.session_state.language == language:
            st.sidebar.error(f"Neither GitHub Username nor Language has changed.")

        if st.session_state.result:
            draw_plots(st.session_state.user, st.session_state.language, st.session_state.result, to_csv)
        else:
            st.sidebar.code(f"{st.session_state.language} code is absent in your {len(st.session_state.repos)} repositories.")


def clean_progress_folder():
    directory = os.path.dirname('progress')
    current_time = datetime.datetime.now()

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isfile(filepath):
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath))
            time_difference = current_time - creation_time

            if time_difference.total_seconds() > 3600:
                os.remove(filepath)


if __name__ == "__main__":
    if 'time' not in st.session_state:
        st.session_state.time = datetime.datetime.now()

    elif (datetime.datetime.now() - st.session_state.time).total_seconds() > 3600:
        st.session_state.time = datetime.datetime.now()
        clean_progress_folder()

    main()
