# IndustriindexDE
Data backend for IndustriIndex
An index describing Swedish counties and municipalities according to different industrial manufacturing dimensions.

# Participation
Use Git Flow model - branch names
`main` — production-ready code; release branches are created from here
`develop` — integration/staging branch
`feature/<ticket-id-or-short-description>` — feature branches off develop
`release/<version>` — preparation for production release (branched from develop, merged into main and back into develop)
`hotfix/<ticket-id-or-short-description>` — urgent fixes off main (merged into main and back into develop)

# Installation
Install local environment using virtual environment. 
`python -m venv /path/to/new/virtual/environment`
Generally you want your .venv folder in the repo parent folder
`python -m venv .venv`

Activate your environment from the same .venv folder as above
`.venv/Scripts/activate`

Install all dependencies still standing in parent directory. Installs dependencies from pyproject.toml
`pip install -e .`
