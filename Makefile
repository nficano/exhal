dev:
	pipenv install --dev

dists: requirements sdist bdist wheels upload clean

requirements:
	pipenv_to_requirements

sdist: requirements
	python setup.py sdist

bdist: requirements
	python setup.py bdist

wheels: requirements
	python setup.py bdist_wheel

clean: clean-build clean-pyc

upload:
	python setup.py sdist bdist bdist_wheel upload

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
