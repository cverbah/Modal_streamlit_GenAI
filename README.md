# GenAI Data Analyst Project
Built using:
- Modal Cloud, Streamlit, LLM model: Gemini Pro 1.5
<br><br>


You need:
- To set up a modal account [Modal: Serverless platform for AI teams](https://modal.com/)
- To have a GCP account with the Vertex AI API enabled
- A service account key saved as key.json in the project folder <br><br>
For running the app: <br>
1. `pip install -r requirements.txt`
2. `modal serve serve_streamlit.py`    For serving the app OR
3. `modal deploy serve_streamlit.py` For deploying the app in the modal cloud