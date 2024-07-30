import streamlit as st
from utils import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import plotly.graph_objects as go
matplotlib.use('Agg')

try:
    df = st.session_state.df

    if 'df_filtered' in st.session_state:
        if len(df) > 0:
            st.dataframe(st.session_state.df[:5000])
            aux = 1

        else:
            st.dataframe(st.session_state.df[:5000])
            st.write('Revise sus filtros: No hay datos para los filtros seleccionados')

    else:
        st.dataframe(st.session_state.df[:5000])
        aux = 0

    tab1, tab2, tab3, tab4 = st.tabs(["Analista de datos AI", "Tabla dinámica", "Insights", "dummy"])
    with tab1:
        if 'user_input' not in st.session_state:
            st.session_state.user_input = ''

        st.text_input('Qué desea saber de la tabla?', key='widget', on_change=submit_query)
        st.write(f'Última consulta: {st.session_state.user_input}')

        # Display the stored user input
        if st.session_state.user_input != '':

            col1, col2 = st.columns(2, gap='large')
            with col1:
                with st.spinner('Pensando...'):
                    try:
                        if 'df_filtered' in st.session_state:
                            response = analyze_table_gemini(query=st.session_state.user_input, df=st.session_state.df,
                                                            plot_type='plotly')

                            local_vars, output = execute_code(response, df=st.session_state.df)
                        else:
                            response = analyze_table_gemini(query=st.session_state.user_input, df=df,
                                                            plot_type='plotly')
                            local_vars, output = execute_code(response, df=df)

                        st.write('Python Snippet:')
                        st.text(response)

                    except Exception as e:
                        st.text('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

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
                                st.text('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

                    else:
                        try:
                            st.dataframe(local_vars['df_temp'])

                        except Exception as e:
                            st.text(output)

                except Exception as e:
                    st.text('Error al ejecutar la query. Intente de nuevo modificando su consulta.')

            st.session_state.user_input = ''

    with tab2:
        st.write('#todo')

    with tab3:
        st.write('#todo')

    with tab4:
        st.write('#todo')

except Exception as e:
    st.warning('Cargue una tabla en Home, antes de usar el asistente')