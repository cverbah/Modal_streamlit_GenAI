import streamlit as st
import pandas as pd
import os
from ast import literal_eval


st.set_page_config(
    page_title="App LLMs Testing",
    page_icon=":robot_face:",
    layout="wide",
)
st.title(':wrench: Dashboard & LLMs Tests :wrench:')


@st.cache_data
def load_dataframe(file_name, file):
    if file_name.endswith('.csv'):
        df = pd.read_csv(file, index_col=0)

    elif file_name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file, engine='openpyxl')

    else:
        st.error(f"Error: {e}. Check your uploaded dataset")

    df = df.convert_dtypes()
    df.columns = (df.columns.str.replace(' ', '_').str.lower().
                  str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

    return df

uploaded_file = st.file_uploader("Seleccione un archivo CSV o Excel para analizar", type=["xlsx", "xls", "csv"])

try:
    if uploaded_file:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, } #"FileSize": uploaded_file.size
        st.write(file_details)

        with open("temp.csv", "wb") as f:
            f.write(uploaded_file.getvalue())

        temp_location = os.path.abspath("temp.csv")

        # Load file
        if 'df' not in st.session_state:
            df = load_dataframe(uploaded_file.name, uploaded_file)
            st.session_state.df = df
        else:
            df = load_dataframe(uploaded_file.name, uploaded_file)
            st.session_state.df = df

        st.subheader("DataFrame Head:")
        st.dataframe(st.session_state.df.head(10))

        st.subheader("DataFrame Stats:")
        st.dataframe(st.session_state.df.describe())
except Exception as e:
    st.error(f"Error: {e}. Check your uploaded dataset")
