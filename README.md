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
. .venv/bin/industriindex-de
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

