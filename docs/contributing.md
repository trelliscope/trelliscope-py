# Contributing

## Getting Started for Development
These steps show how to get started with development on the Trelliscope library itself.

### Clone the Source
```
git clone https://github.com/trelliscope/trelliscope-py
```

### Setup the Virtual Environment
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

### Install the project in an editable state
In the root directory of the project, run:
```
pip install -e .
```

### Verify Trelliscope package is accessible
Run a simple trelliscope example:
```
python trelliscope/examples/fruit.py
```
This creates a directory for the output called `./test-build-output/`

### Install development libraries
The standard dependencies are sufficient to use Trelliscope. If you plan to do development with Trelliscope you will also want to install the optional dependencies for "dev" and "test".

Windows
```
pip install -e .[dev]
```

Please note that on MacOS the `[]` characters will be pulled out by the shell, so you should enclose them in `''` characters as follows:

Linux/macOS
```
pip install -e .'[dev]'
```

## Deactivate Virtual Environment
When finished, if desired, you can deactivate the virtual environment:
```
deactivate
```

## Run the Unit tests
Verify pytest installation:
```
pytest --version
```

### Running PyTest
You can run all tests in the project using the options specified in teh pyproject.toml file:

```
pytest
```

Alternatively, you can run the tests directly:

```
pytest trelliscope/tests/
```

Note that PyTest can also be invoked via Python on the command line:
```
python -m pytest trelliscope/tests/
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
pip install -e .'[lint]'
```

### Run checks and formatter with Ruff
```
ruff check --fix .  # Lint all files in the current directory, and fix any fixable errors.
ruff format .       # Format all files in the current directory.
```

## Set up `pre-commit`

Using pre-commit, you as a developer can ensure that certain checks are done before committing changes. By making
sure you only commit code when it passes these checks, we reduce the number of Github Actions that are run and
we can ensure that pushed code passes quality checks.

### Install pre-commit

Install it using the extra `dev` dependencies with this package,

```
pip install -e .[dev]
```

Or separately,

```
pip install pre-commit
```

### Enable pre-commit

To enable pre-commit, you install it. It will look at the `.pre-commit-config.yaml` file, and also use settings
from the `pyproject.toml` to set up.

```
pre-commit install
```

### Running pre-commit

Pre-commit will automatically apply to files you are trying to commit. Your commit will be denied if checks
are not succesful.

To manually apply pre-commit to all files, run this,

```
pre-commit run --all-files
```

## Build docs

Make sure to install the documentation requirements:

```shell
pip install -e .[docs]
```

Then build the HTML docs using sphinx as follows,

```shell
cd ./docs
make html
```

This requires `make` and `pandoc` to be installed on your system. TODO: instructions...

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
