import os
import pandas as pd
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import matplotlib.pyplot as plt
import io
import contextlib
from dotenv import load_dotenv
# env
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
vertexai.init(project=PROJECT_ID, location=LOCATION)


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


def analyze_table_gemini(query: str, df: pd.DataFrame):
    generation_config = {
        "max_output_tokens": 8192,  # max
        "temperature": 1,
        "top_p": 0.95,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    if len(df) > 50:
        df_sample = df.sample(n=50, random_state=42)
    else:
        df_sample = df

    df_parsed = df_sample.to_string(index=False) # random sample. Little hack
    model = GenerativeModel(
        model_name="gemini-1.5-pro-001",
        system_instruction=[
            "Eres un asistente de IA experto en análisis de datos y programación en el lenguaje python.",
            f"Debes responder preguntas relacionadas a la siguiente tabla de datos: {df_parsed}.",
            "El usuario te proporcionará una consulta en lenguaje natural y debes responderla entregando un código en python.",
            "Usa el nombre 'df' para la tabla que contenga la data. No vuelvas a generar la data en el código.",
            f"Si vas a filtrar columnas de la tabla, siempre usa las siguientes columnas: {df.columns}."
            "Piensa paso a paso, verificando que los formatos y tipos de datos sean los correctos y siempre importa las librerias necesarias en el codigo.",
            "No imprimas comentarios en el código. (no uses #) y utiliza el comando print para imprimir la tabla con los datos de la consulta.",
            "En el caso que tengas que imprimir una tabla con la respuesta final, llama a esta tabla: df_temp en el código generado."
            "En el caso de que tengas que graficar, ocupa un fig_size fijo de (5,5) y siempre usa tight_layout.",
            "Si no respondiste generando código en python, siempre respondes en español",
            ])

    prompt = f"""
             User input: {query}
             Answer:
            """

    contents = [prompt]

    responses = model.generate_content(contents,
                                       generation_config=generation_config,
                                       safety_settings=safety_settings,
                                       stream=False)  # Si True -> la parte de text tiene que ser iterada

    # for response in responses:
    #    print(response.text, end="")
    return responses.text
