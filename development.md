# Getting Started for Development
These steps show how to get started with development on the Trelliscope library itself.

## Clone the Source
```
git clone https://github.com/trelliscope/trelliscope-py
```

## Setup the Virtual Environment
Create a new virtual environment for development:
```
python -m venv tr-dev-env
```

Activate the virtual environment:

Linux/macOS:
```
source ./tr-dev-env/bin/activate
```
Windows:
```
./tr-dev-env/Scripts/activate
```

## Install the project in an editable state
In the root directory of the project, run:
```
pip install -e .
```

## Install other libraries
While not tecnically required by Trelliscope, it is likely that you will want
to install Plotly Express in the virtual environment and the corresponding `kaleido`
to write Plotly images.
```
pip install plotly-express
pip install kaleido
```

## Verify Trelliscope package is accessible
Run a simple trelliscope example:
```
python trelliscope/examples/fruit.py
```
This creates a directory for the output called `./test-build-output/`

## Run the Unit tests
### Installing PyTest
If you do not already have PyTest installed, you can install it with:
```
pip install -U pytest
```
Verify installation:
```
pytest --version
```

### Running PyTest
You can run all tests in the project:
```
pytest trelliscope/tests
```

Note that PyTest can also be invoked via Python on the command line:
```
python -m pytest trelliscope/tests
```

Also note that, if desired, you can redirect the output to a file, or tee it so that it goes to a file and to the console:
```
pytest trelliscope/tests >test-output.log
pytest trelliscope/tests | tee test-output.log
```

## Format code with Ruff

This codebase uses Ruff to define and check codestyle.

### Install linting dependencies

```
pip install -e .[lint]
```

### Run checks and formatter with Ruff
```
ruff check --fix .  # Lint all files in the current directory, and fix any fixable errors.
ruff format .       # Format all files in the current directory.
```

## Deactivate Virtual Environment
When finished, if desired, you can deactivate the virtual environment:
```
deactivate
```

## Using Trelliscope in a Jupyter Notebook
1. Follow the steps above to create a virtual environment and download and install the Trelliscope library.
2. Install Jupyter notebook package (if not already installed)

```
pip install notebook
```

3. Start a Jupyter notebook server

```
jupyter notebook
```

4. Create a new notebook, or browse to the example notebook (`trelliscope/examples/introduction.ipynb`)
