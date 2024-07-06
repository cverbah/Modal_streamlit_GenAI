import streamlit as st
import pandas as pd
import os
import numpy as np
from utils import parse_null_list
from ast import literal_eval


st.set_page_config(
    page_title="App LLMs Testing",
    page_icon=":robot_face:",
    layout="wide",
)
st.title(':wrench: Dashboard & LLMs Tests :wrench:')

uploaded_file = st.file_uploader("Seleccione un archivo CSV o Excel para analizar", type=["xlsx", "xls", "csv"])

try:
    if uploaded_file:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, } #"FileSize": uploaded_file.size
        st.write(file_details)

        with open("temp.csv", "wb") as f:
            f.write(uploaded_file.getvalue())

        temp_location = os.path.abspath("temp.csv")

        #Dataframe formatting
        if 'df' not in st.session_state:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(temp_location, index_col=0)
                #df = format_compete_table(df)   # deactivated for now

                # por ahora este preprocessing para una tabla de prueba que estoy usando (ofertas_test.csv)
                # parse data
                df['marcas_en_promo'] = df['marcas_en_promo'].apply(lambda row: parse_null_list(row))
                df['marcas_en_promo'] = df['marcas_en_promo'].apply(literal_eval)
                df['publico_objetivo'] = df['publico_objetivo'].apply(lambda row: parse_null_list(row))
                df['publico_objetivo'] = df['publico_objetivo'].apply(literal_eval)
                df['categorias_en_promo'] = df['categorias_en_promo'].apply(lambda row: parse_null_list(row))
                df['categorias_en_promo'] = df['categorias_en_promo'].apply(literal_eval)
                df['productos_en_oferta'] = df['productos_en_oferta'].apply(lambda row: parse_null_list(row))
                df['datetime_checked'] = pd.to_datetime(df['datetime_checked'])
                df['date_checked'] = df['datetime_checked'].dt.date
                df['descuentos_promo'] = df['descuentos_promo'].str.rstrip('%')
                df['descuentos_promo'] = pd.to_numeric(df['descuentos_promo'], errors='coerce')
                # Divide by 100 to convert to decimal form
                df['descuentos_promo'] = df['descuentos_promo'] / 100
                # Save the data to session state
                st.session_state.df = df

            if uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                # por ahora este preprocessing para una tabla de prueba que estoy usando (Purina Specialty - Catálogo de sustitutos.xlsx)
                # columnas con precios
                precios_tienda = df.iloc[:, 4:]
                for col in precios_tienda.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                #df = df.fillna(0)
                df = df[~df.SKU.isnull()]
                df.columns = df.columns.str.lower()
                # Save the data to session state
                st.session_state.df = df

        st.subheader("DataFrame Head:")
        st.dataframe(df.head(10))

        st.subheader("DataFrame Stats:")
        st.dataframe(df.describe())
except Exception as e:
    st.error(f"Error: {e}. Check your uploaded dataset")
