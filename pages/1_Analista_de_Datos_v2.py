import streamlit as st
from utils import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Agg')


st.set_page_config(
    page_title="Data Analyst Testing",
    page_icon=":robot_face:",
    layout="wide",
)

#add_logo("https://www.python.org/static/community_logos/python-powered-w-100x40.png", height=0 )
st.title(':robot_face: Analista de datos')
# Display DataFrame
st.subheader("DataFrame cargado:")
try:
    df = st.session_state.df
    st.dataframe(df)
except Exception as e:
    st.error(f'Error: {e}')

user_input = st.text_input("Que desea saber de la tabla?")
if user_input:
    col1, col2= st.columns(2, gap='large')
    with col1:
        with st.spinner('Pensando...'):
            try:
                response = analyze_table_gemini(query=user_input, df=df)
                local_vars, output = execute_code(response, df=df)
                #st.write(local_vars)
                st.write('Snippet en Python:')
                st.text(response)
            except Exception as e:
                st.text('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

    with col2:
        try:
            st.write('Respuesta generada por IA:')
            if 'plt.' in response:
                try:
                    st.write("Generated Plot:")
                    fig = local_vars['plt'].gcf()
                    #fig.set_size_inches(5, 5)
                    st.pyplot(fig)
                except Exception as e:
                    try:
                        st.dataframe(local_vars['df_temp'])
                    except Exception as e:
                        st.text('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

            else:
                try:
                    st.dataframe(local_vars['df_temp'])
                except Exception as e:
                    st.text(output)

        except Exception as e:
            st.text('Error al ejecutar la query. Intente de nuevo modificando su consulta.')