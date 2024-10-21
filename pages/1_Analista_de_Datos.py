import streamlit as st
from utils import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import plotly.graph_objects as go
matplotlib.use('Agg')

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon=":robot_face:",
    layout="wide",
)

try:
    df = st.session_state.df

    if 'df_filtered' in st.session_state:
        if len(df) > 0:
            st.dataframe(st.session_state.df[:5000], height=200)
            aux = 1

        else:
            #st.dataframe(st.session_state.df[:5000])
            st.write('Revise sus filtros: No hay datos para los filtros seleccionados')

    else:
        st.dataframe(st.session_state.df[:5000], height=200)
        aux = 0

    tab1, tab2, tab3, tab4 = st.tabs(["Analista de datos AI", "Tabla dinámica", "Insights", "dummy"])
    with tab1:
        if 'user_input' not in st.session_state:
            st.session_state.user_input = ''

        col1, col2 = st.columns([0.8, 0.12], gap='large')
        with col1:
            st.text_input('', key='widget', on_change=submit_query,
                          placeholder='Qué desea saber de la tabla?')

            if st.session_state.user_input != '':
                st.write(f'Última consulta: {st.session_state.user_input}')

        with col2:
            st.write('')
            st.button('Reset', on_click=reset_memory)

        # Display the stored user input
        if st.session_state.user_input != '':

            st.session_state.user_input = fix_query(st.session_state.user_input)
            col1, col2 = st.columns(2, gap='large')
            with col1:
                with st.spinner('Pensando...'):
                    try:
                        if 'ai_assistant' not in st.session_state:
                            st.session_state.ai_assistant = 0

                        if st.session_state.ai_assistant == 0:
                            st.session_state.chain = generate_llm_chain(df=df)
                            st.session_state.chat_memory = ChatMessageHistory()
                            st.session_state.ai_memory = add_memory_chain(st.session_state.chain,
                                                                          st.session_state.chat_memory)
                            st.session_state.ai_assistant = 1

                        if st.session_state.ai_assistant:
                            response = st.session_state.ai_memory.invoke(
                                {"input": st.session_state.user_input},
                                {"configurable": {"session_id": "unused"}},
                            )
                        local_vars, output = execute_code(response, df=df)

                        st.write('Python Snippet:')
                        st.text(response)

                    except Exception as e:
                        st.warning('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

            with col2:
                try:
                    st.write('Respuesta generada por IA:')
                    if 'plotly.express' in response:
                        try:
                            st.write("Generated Plot:")
                            fig = local_vars['fig']
                            st.plotly_chart(fig)
                        except Exception as e:
                            try:
                                st.dataframe(local_vars['df_temp'])

                            except Exception as e:
                                st.warning('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

                    else:
                        try:
                            st.dataframe(local_vars['df_temp'])

                        except Exception as e:
                            #st.text(output)
                            st.warning('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

                except Exception as e:
                    st.warning('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

            st.session_state.user_input = ''

    with tab2:
        st.write('#todo')

    with tab3:
        st.write('#todo')

    with tab4:
        st.write('#todo')

except Exception as e:
    st.warning('Cargue una tabla en Home, antes de usar el asistente')