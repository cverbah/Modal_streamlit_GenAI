import shlex
import subprocess
from pathlib import Path
from modal import Image, Mount, App, web_server

image = (Image.micromamba()
         .pip_install("streamlit~=1.35.0", "numpy==1.23.5", "pandas==1.5.3", "openpyxl==3.1.2",
                      "matplotlib==3.7.1", "seaborn==0.12.2","python-dotenv==1.0.0", "PyQt5==5.15.10",
                      "google-cloud-aiplatform==1.48.0",
                      )
         )

app = App(name="streamlit-genai-demo-v1", image=image)

# folders and files mount
streamlit_script_local_path_folder = Path(__file__).parent
streamlit_script_remote_path_folder = Path("/root/")

streamlit_script_local_path = Path(__file__).parent / "Home.py"                   # main file to run streamlit
streamlit_script_remote_path = streamlit_script_remote_path_folder / "Home.py"

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "Home.py not found! Place the script with your streamlit app in the same directory."
    )

streamlit_script_mount = Mount.from_local_file(local_path=streamlit_script_local_path,
                                               remote_path=streamlit_script_remote_path,
)

streamlit_folder_mount = Mount.from_local_dir(local_path=streamlit_script_local_path_folder,
                                              remote_path=streamlit_script_remote_path_folder,
)


# Inside the container, we will run the Streamlit server in a background subprocess using
# `subprocess.Popen`. We also expose port 8000 using the `@web_server` decorator.
@app.function(
    allow_concurrent_inputs=100,
    mounts=[streamlit_script_mount,
            streamlit_folder_mount,
            ],
)
@web_server(8000)
def run():
    target = shlex.quote(str(streamlit_script_remote_path))
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)
