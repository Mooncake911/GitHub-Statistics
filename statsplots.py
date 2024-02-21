import os
import base64
import streamlit as st
import plotly.express as px
import pandas as pd


def draw_plots(user, language, data, to_csv=True):
    df = pd.DataFrame(data, columns=['Repo', 'Path', 'File', 'Lines of Code'])
    st.dataframe(df)

    bins = pd.cut(df['Lines of Code'], bins=3)
    df['Category'] = [f'{int(interval.left)}-{int(interval.right)}' for interval in bins]
    fig0 = px.parallel_categories(df, color='Lines of Code', dimensions=['Category', 'Repo'],
                                  color_continuous_scale=px.colors.sequential.Inferno,
                                  title='Lines of Code per Category (Categories)')
    st.plotly_chart(fig0, use_container_width=True)

    fig1 = px.histogram(df, x='Repo', y='Lines of Code', barmode='group', text_auto=True,
                        title='Lines of Code per Repository')
    fig1.update_traces(textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x='Repo', y='Lines of Code', title='Lines of Code per Repository (Scatter Plot)',
                      hover_data={'Repo': False, 'File': True})
    st.plotly_chart(fig2, use_container_width=True)

    cols = st.columns(2)
    with cols[0]:
        fig3 = px.histogram(df, x='Lines of Code', marginal='rug', title='Lines of Code Distribution (Histogram)')
        st.plotly_chart(fig3, use_container_width=True)

    with cols[1]:
        fig4 = px.pie(df, names='Repo', values='Lines of Code', title='Lines of Code per Repository (Pie Chart)')
        fig4.update_traces(textposition='inside')
        st.plotly_chart(fig4, use_container_width=True)

    if to_csv:
        filename = f'progress/{user}_{language}.csv'
        if not os.path.exists(filename):
            df.to_csv(filename, index=False)
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)
