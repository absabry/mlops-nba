dir=mlops_nba
VENV=venv
PYTHON_VERSION=3
PRECOMMIT=$(VENV)/bin/pre-commit
PYTHON=$(VENV)/bin/python$(PYTHON_VERSION)
SAFETY=$(VENV)/bin/safety

## environnement
clean-venv:
	rm -rf $(VENV)

add-venv:
	python$(PYTHON_VERSION) -m venv $(VENV)
	echo "Have a look on if you're on Apple M2 chips https://stackoverflow.com/a/76264243"

install-dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

install:
	$(PYTHON) -m pip install -r requirements.txt --no-cache-dir


## linters
lint:
	$(PYTHON) -m pylint $(dir) --rcfile ./setup.cfg

black:
	$(PYTHON) -m black $(dir) --check

flake:
	$(PYTHON) -m flake8 $(dir) --config ./setup.cfg

isort:
	$(PYTHON) -m isort $(dir) --check-only --settings-file ./setup.cfg

format:
	$(PYTHON) -m black $(dir)
	$(PYTHON) -m isort $(dir) --settings-file ./setup.cfg


check: black isort flake

format-tests:
	$(PYTHON) -m black tests
	$(PYTHON) -m isort tests --settings-file ./setup.cfg

## unit tests and coverage
test:
	$(PYTHON) -m pytest tests -vv --capture=tee-sys

coverage:
	$(PYTHON) -m pytest tests --cov-config=.coveragerc --cov=$(dir)

coverage-html:
	$(PYTHON) -m pytest tests --cov-config=.coveragerc --cov=$(dir) --cov-report html


clean-logs:
	rm -rf .pytest_cache
	rm -rf htmlcov
	find . -path '*/.output*' -delete
	find . -path '*/__pycache__*' -delete
	find . -path '*/.ipynb_checkpoints*' -delete

safety:
	$(SAFETY) check

setup: clean-venv add-venv install-dev install

ingest-new-data:
	python3 -m mlops_nba.data_pipeline.ingest.players --start_date 17/01/2024 --end_date 24/01/2024
	python3 -m mlops_nba.data_pipeline.ingest.boxscores --start_date 17/01/2024 --end_date 24/01/2024

pre-raw-to-raw:
	python3 -m mlops_nba.data_pipeline.preraw_to_raw

raw-to-curated:
	python3 -m mlops_nba.data_pipeline.raw_to_curated


run: ingest-new-data