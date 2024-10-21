import os
import pandas as pd
import json
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import matplotlib.pyplot as plt
import io
import contextlib
from dotenv import load_dotenv
from google.oauth2 import service_account
import plotly.graph_objects as go
import streamlit as st
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory


# env
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
GCP_API_KEY = os.environ["GCP_API_KEY"]
vertexai.init(project=PROJECT_ID, location=LOCATION)
GCP_MODEL_ID = "gemini-1.5-flash-002"


def submit_query():
    st.session_state.user_input = st.session_state.widget
    st.session_state.widget = ''


def reset_memory():
    """resets assistant memory"""
    st.session_state.ai_assistant = 0
    st.session_state.chat_memory = ChatMessageHistory()


def set_credentials(credential_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    return service_account.Credentials.from_service_account_file(credential_path)


def parse_df_competitividad(df: pd.DataFrame):
    df['productPrices'] = df['productPrices'].apply(json.loads)
    df['image'] = df['image'].apply(json.loads)
    json_df_prices = pd.json_normalize(df['productPrices'])
    json_df_image = pd.json_normalize(df['image'])
    df = df.drop(columns=['productPrices', 'image', 'prices'])
    df_parsed = pd.concat([df, json_df_prices, json_df_image], axis=1)
    df_parsed = df_parsed.convert_dtypes()
    df_parsed['stock'] = pd.to_numeric(df_parsed["stock"], errors='coerce')
    df_parsed['price_index'] = pd.to_numeric(df_parsed["price_index"], errors='coerce')
    df_parsed['final_price'] = pd.to_numeric(df_parsed["final_price"], errors='coerce')
    df_parsed['normal_price'] = pd.to_numeric(df_parsed["normal_price"], errors='coerce')
    df_parsed['last_final_price'] = pd.to_numeric(df_parsed["last_final_price"], errors='coerce')
    df_parsed.columns = (df_parsed.columns.str.replace(' ', '_').str.lower().
                  str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

    return df_parsed

def parse_null_list(value):
    if pd.isnull(value):
        parse = '[]'
        return parse
    else:
        return value


def execute_code(snippet, df: pd.DataFrame):
    # Strip the code snippet
    code = snippet.strip().strip('```python').strip('```').strip()
    local_vars = {'df': df, 'plt': plt}
    # Redirect standard output to capture `print()` statements
    output_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(output_capture):
            exec(code, globals(), local_vars)
        output = output_capture.getvalue()
        return local_vars, output
    except Exception as e:
        return {}, f"Error: {e}"


def generate_llm_chain(df: pd.DataFrame, model_name=GCP_MODEL_ID):
    """generates a python snippet based on a user query using the GCP_MODEL_ID LLM model.
    The query should be for solving something related to the df DataFrame"""
    llm = GoogleGenerativeAI(model=model_name, google_api_key=GCP_API_KEY,
                             generation_config={"max_output_tokens": 8192,  # max
                                                "temperature": 1,  # deterministic output
                                                "top_p": 0.95,
                                                },
                             safety_settings={
                                 HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                 HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                 HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                 HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                             })

    if len(df) > 50:
        df_sample = df.sample(n=50, random_state=42)
    else:
        df_sample = df

    df_parsed = df_sample.to_string(index=False)  # random sample. Little hack for reducing Input tokens needed
                                                  # Faster and cheaper.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", [
                "Eres un asistente de IA experto en análisis de datos y programación en el lenguaje python",
                f"Debes responder preguntas relacionadas a la siguiente tabla de datos: {df_parsed}.",
                "El usuario te proporcionará una consulta en lenguaje natural y debes responderla entregando un código en python.",
                "Usa el nombre 'df' para la tabla que contenga la data. No vuelvas a generar la data en el código.",
                f"Si vas a filtrar columnas de la tabla, siempre usa las siguientes columnas: {df.columns}."
                "Si necesitas graficar, siempre usa la librería: 'plotly.express' sin imprimir la imagen (no uses .show())",
                "Si necesitas graficar, siempre incluye un título para el gráfico",
                "Piensa paso a paso, verificando que los formatos y tipos de datos sean los correctos y siempre importa las librerías necesarias en el código.",
                "No imprimas comentarios en el código (no uses #).",
                "En el caso en que tengas que entregar una tabla con la respuesta final a la consulta del usuario, llama a esta tabla: df_temp en el código generado.",
                "No uses la función print para imprimir la tabla al final del código",
                "Si no respondiste generando código en python, siempre respondes en español"],
             ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ])

    chain = prompt | llm
    return chain


def add_memory_chain(chain, chat_history):
    """adds memory for adding more context for the queries """
    #demo_ephemeral_chat_history_for_chain = ChatMessageHistory()

    chain_with_message_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    return chain_with_message_history


def fix_query(query: str):
    """fix results if user does not explicitly ask for a table. This fix should be monitored"""
    check_words = ['gráfico', 'grafico', 'tabla', 'dataframe', 'plot', 'boxplot', 'histograma',
                   'df', 'graficame', 'grafícame', 'plotea', 'ploteame', 'plotéame']

    words_cap = list(map(lambda x: str(x).capitalize(), check_words))
    words_upper = list(map(lambda x: str(x).upper(), check_words))
    check_words.extend(words_cap)
    check_words.extend(words_upper)
    # check_words = words from list + words in capital letter + words with first string in Upper
    if any(word in query for word in check_words):
        return query
    else:
        fixed_query = query + ' en una tabla'
        return fixed_query