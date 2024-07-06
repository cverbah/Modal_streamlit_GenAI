# ---
# deploy: true
# cmd: ["modal", "serve", "10_integrations/streamlit/serve_streamlit.py"]
import shlex
import subprocess
from pathlib import Path
from modal import Image, Mount, App, web_server

# ## Define container dependencies
#
# The `Home.py` script imports three third-party packages, so we include these in the example's
# image definition.

image = (Image.micromamba()
         .pip_install("streamlit~=1.35.0", "numpy==1.23.5", "pandas==1.5.3", "openpyxl==3.1.2",
                      "matplotlib==3.7.1", "seaborn==0.12.2", "PyQt5==5.15.10", "google-cloud-aiplatform==1.48.0",
                      )
         )

app = App(name="streamlit-genai-demo-v1", image=image)

# ## Mounting the `Home.py` script
#
# We can just mount the `Home.py` script inside the container at a pre-defined path using a Modal
# [`Mount`](https://modal.com/docs/guide/local-data#mounting-directories).
streamlit_script_local_path_folder = Path(__file__).parent
streamlit_script_remote_path_folder = Path("/root/")

streamlit_script_local_path = Path(__file__).parent / "Home.py"
streamlit_script_remote_path = streamlit_script_remote_path_folder / "Home.py"

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "Home.py not found! Place the script with your streamlit app in the same directory."
    )

streamlit_script_mount = Mount.from_local_file(
    streamlit_script_local_path,
    remote_path=streamlit_script_remote_path,
)

streamlit_folder_mount = Mount.from_local_dir(
    streamlit_script_local_path_folder,
    remote_path=streamlit_script_remote_path_folder,
)

# ## Spawning the Streamlit server
#
# Inside the container, we will run the Streamlit server in a background subprocess using
# `subprocess.Popen`. We also expose port 8000 using the `@web_server` decorator.


@app.function(
    allow_concurrent_inputs=100,
    mounts=[streamlit_script_mount,
            streamlit_folder_mount,
            Mount.from_local_file("key.json",
                                  remote_path="/root/key.json")
            ],
)
@web_server(8000)
def run():
    target = shlex.quote(str(streamlit_script_remote_path))
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)


# ## Iterate and Deploy
#
# While you're iterating on your screamlit app, you can run it "ephemerally" with `modal serve`. This will
# run a local process that watches your files and updates the app if anything changes.
#
# ```shell
# modal serve serve_streamlit.py
# ```
#
# Once you're happy with your changes, you can deploy your application with
#
# ```shell
# modal deploy serve_streamlit.py
# ```
#
# If successful, this will print a URL for your app, that you can navigate to from
# your browser 🎉 .
