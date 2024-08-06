import os
import json
import base64
import datetime
import requests

import streamlit as st
import pandas as pd


from configs import LANG_EXT, create_folders

from mylines import get_progress
from mysecrets import check_secrets
from statsplots import draw_plots


def get_repos(user):
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


def generate_download_link(filename, ext):
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:application/{ext};base64,{b64}" download="{filename}">Download {ext}</a>'
    st.markdown(href, unsafe_allow_html=True)


def renew_main_window():
    if st.session_state.progress:
        df = pd.read_csv(st.session_state.progress)
        st.empty().title(f'{st.session_state.user}')
        st.empty().info(f'Found {len(st.session_state.repos)} repositories.')
        st.empty().info(f'Total Lines of {st.session_state.language}: {df["Lines of Code"].sum()}')
        draw_plots(df)

    if st.session_state.secrets:
        with open(st.session_state.secrets, 'r') as file:
            data = json.load(file)
        st.empty().info(f'Secrets was found in {st.session_state.repository}:')
        st.json(data)


def init_states(user):
    if not user:
        st.session_state.repos = []
    elif user != st.session_state.user:
        st.session_state.repos = get_repos(user)
    st.session_state.language = None
    st.session_state.progress = None
    st.session_state.repository = None
    st.session_state.secrets = None


def main():
    st.session_state.setdefault('folders_created', create_folders())

    st.set_page_config(layout='wide')
    logo_url = 'https://raw.githubusercontent.com/NoDataFound/CMC/main/githublogo.png'
    st.sidebar.markdown(
        f"<div style='text-align: center'><img src='{logo_url}' width='40%'></div>",
        unsafe_allow_html=True,
    )

    user = st.sidebar.text_input('Enter GitHub Username').replace(' ', '')
    st.session_state.setdefault('user', None)
    init_states(user)

    if user:
        st.sidebar.code(f'Found {len(st.session_state.repos)} repositories for {user}.')

    with st.sidebar.form(key='SidebarForm1'):
        st.title('Lines of Code Counter')
        language = st.selectbox('Select Language', list(LANG_EXT.keys()))
        count_button = st.form_submit_button(label='Count')

        if count_button:
            if not user or not language:
                st.sidebar.error(f'GitHub Username or Language is empty. Please try again!')
            elif user == st.session_state.user and language == st.session_state.language:
                st.sidebar.warning(f"Neither GitHub Username nor Language has changed.")
            else:
                st.session_state.progress = get_progress(user, language, st.session_state.repos)
                st.session_state.language = language

        if st.session_state.progress:
            generate_download_link(st.session_state.progress, ext="csv")
        elif st.session_state.language:
            st.sidebar.code(
                f"{st.session_state.language} code is absent in your {len(st.session_state.repos)} repositories.")

    with st.sidebar.form(key='SidebarForm2'):
        st.title('Check your Repo for Secrets')
        repository = st.selectbox('Select Repo', st.session_state.repos)
        check_button = st.form_submit_button(label='Check')

        if check_button:
            if not user or not repository:
                st.sidebar.error(f'GitHub Username or Repository is empty. Please try again!')
            elif user == st.session_state.user and repository == st.session_state.repository:
                st.sidebar.warning(f"Neither GitHub Username nor Repository has changed.")
            else:
                st.session_state.secrets = check_secrets(user, repository)
                st.session_state.repository = repository

        if st.session_state.secrets:
            generate_download_link(st.session_state.secrets, ext="json")
        elif st.session_state.repository:
            st.sidebar.code(
                f"Secrets are absent in {st.session_state.repository} repository.")

    st.session_state.user = user
    renew_main_window()


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
        # clean_progress_folder() # TODO: it doesn't work

    main()
