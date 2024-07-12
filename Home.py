import streamlit as st
import pandas as pd
import os
from ast import literal_eval
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="App LLMs Testing",
    page_icon=":robot_face:",
    layout="wide",
)
st.title(':wrench: LLMs Assistant Tests :wrench:')

SESSION_TIMEOUT_MINUTES = 15

# Initialize session state variables
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
    st.session_state.df = None


def check_session_timeout():
    now = datetime.now()
    session_start = st.session_state.session_start
    if now - session_start > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        st.warning("Session has expired. Please reload the page.")
        return False
    return True


def reset_session():
    st.session_state.session_start = datetime.now()
    st.session_state.df = None

@st.cache_data
def load_dataframe(file_path: str, file):
    try:
        if file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file, index_col=0)
            except:
                df = pd.read_csv(file, index_col=0, delimiter=';')

        elif file_path.endswith(('.xls', '.xlsx')):

            df = pd.read_excel(file, engine='openpyxl')
            # especial pa prueba con json col:
            if 'Información extendida' in df.columns:
                df['Información extendida'] = df['Información extendida'].apply(json.loads)
                json_df = pd.json_normalize(df['Información extendida'])
                df = df.drop(columns=['Información extendida'])
                df = pd.concat([df, json_df], axis=1)


        df = df.convert_dtypes()
        df.columns = (df.columns.str.replace(' ', '_').str.lower().
                      str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

        return df

    except Exception as e:
        output = {
            "error": str(e),
        }
        return output


# Check session timeout
if check_session_timeout():

    uploaded_file = st.file_uploader("Seleccione un archivo CSV o Excel para analizar", type=["xlsx", "xls", "csv"])

    try:
        if uploaded_file:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, } #"FileSize": uploaded_file.size
            st.write(file_details)

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

else:
    # Button to reset the session
    if st.button("Reset Session"):
        reset_session()
        st.experimental_rerun()