# IndustriIndexDE
Data backend for IndustriIndex
An index describing Swedish counties and municipalities according to different industrial manufacturing dimensions.

# Participation
Use Git Flow model - branch names:

|name                                          |—|purpose                                                                                           |
|----------------------------------------------|-|--------------------------------------------------------------------------------------------------|
|`main`                                        |—|production-ready code; release branches are created from here                                     |
|`develop`                                     |—|integration/staging branch                                                                        |
|`feature/<`*ticket‑id‑or‑short‑description*`>`|—|feature branches off develop                                                                      |
|`release/<`*version*`>`                       |—|preparation for production release (branched from develop, merged into main and back into develop)|
|`hotfix/<`*ticket‑id‑or‑short‑description*`>` |—|urgent fixes off main (merged into main and back into develop)                                    |

# Installation

## Windows

Install local environment using virtual environment. The general form is:
```
python -m venv \path\to\new\virtual\environment
```
Here we'll use `.venv` folder in the repo parent folder
```
python -m venv .venv
```
Activate your environment from the same .venv folder as above
```
.venv\Scripts\activate
```
From the parent directory, install all dependencies (defined in pyproject.toml):
```
pip install -e .
```
*or*
```
pip install -e ".[dev]"
```
to install with dev dependencies (formatter, linter)

Run the application with:
```
.venv\Scripts\industriindex-de.exe
```
If installed in .[dev]-mode:

Run linter [flake8](https://pypi.org/project/flake8/)
```
flake8 src/
```
Run code formatter [black](https://pypi.org/project/black/)
```
black src/
```
*or*
```
black --check src/
```
to see what black is going to reformat.

## Linux

Install local environment using virtual environment. The general form is:
```
python -m venv /path/to/new/virtual/environment
```
Here we'll use `.venv` folder in the repo parent folder
```
python -m venv .venv
```
Activate your environment from the same .venv folder as above
<pre>
. .venv/bin/activate
</pre>
From the parent directory, install all dependencies (defined in pyproject.toml):
```
pip install -e .
```
*or*
```
pip install -e ".[dev]"
```
to install with dev dependencies (formatter, linter)

Run the application with:
```
.venv/bin/industriindex-de
```

## Docker

Build the image from the repository root:
```powershell
docker build -t industriindex-de .
```

Run the container and forward port 8000 to the host:
```powershell
docker run --rm -p 8000:8000 industriindex-de
```

The app listens on `0.0.0.0:8000`; verify healthcheck at `http://localhost:8000/healthcheck`.

## Devcontainer — debug / development mode

When using the VS Code devcontainer, run the app in debug/reload mode with Uvicorn so code changes are reloaded automatically.

Install dev dependencies in the container or dev environment:
```bash
pip install -e '.[dev]'
```

Start the app with automatic reload (works in the devcontainer terminal):
```bash
# runs the app and enables reload on code changes
uvicorn industriindex_de.__main__:app --reload --host 0.0.0.0 --port 8000
```

You can then connect to the app on the forwarded port (usually `localhost:8000` on the host).
If installed in .[dev]-mode:
Run linter [flake8](https://pypi.org/project/flake8/)
```
flake8 src/
```
Run code formatter [black](https://pypi.org/project/black/)
```
black src/
```
*or*
```
black --check src/
```
to see what black is going to reformat.

