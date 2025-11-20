# IndustriIndexDE
Data backend for IndustriIndex
An index describing Swedish counties and municipalities according to different industrial manufacturing dimensions.

# Participation
Use Git Flow model - branch names<br>
`main` — production-ready code; release branches are created from here<br>
`develop` — integration/staging branch<br>
`feature/<ticket-id-or-short-description>` — feature branches off develop<br>
`release/<version>` — preparation for production release (branched from develop, merged into main and back into develop)<br>
`hotfix/<ticket-id-or-short-description>` — urgent fixes off main (merged into main and back into develop)

# Installation
Install local environment using virtual environment. <br>
`python -m venv /path/to/new/virtual/environment`<br>
Generally you want your .venv folder in the repo parent folder<br>
`python -m venv .venv`

Activate your environment from the same .venv folder as above<br>
`.venv/Scripts/activate`

From the parent directory, install all dependencies (defined in pyproject.toml):<br>
`pip install -e .`<br>
*or* <br>
`pip install -e ".[dev]"` to install with dev dependencies (formatter, linter)

Run the application with:<br>
`industriindex-de`<br>

If installed in .[dev]-mode:
Run linter [flake8](https://pypi.org/project/flake8/)<br>
`flake8 source/` <br>
Run code formatter [black](https://pypi.org/project/black/)<br>
`black source/` <br>
*or* <br>
`black --check source/`<br>
to see what black is going to reformat.
