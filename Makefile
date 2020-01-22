dev:
    pipenv install --dev

dists: requirements sdist bdist wheels clean

requirements:
    # For a library, use:
    pipenv_to_requirements
    # For an application, use:
    # pipenv run pipenv_to_requirements -f

sdist: requirements
    python setup.py sdist

bdist: requirements
    python setup.py bdist

wheels: requirements
    python setup.py bdist_wheel

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.DS_Store' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
