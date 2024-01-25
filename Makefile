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

start_date = 17/01/2024
end_date = 24/01/2024
folder_prefix = 2024-01-17_2024-01-24 # first-drop

ingest-new-data:
	python3 -m mlops_nba.data_pipeline.ingest.boxscores --start_date $(start_date) --end_date $(end_date)
	python3 -m mlops_nba.data_pipeline.ingest.players --folder-prefix $(folder_prefix)


pre-raw-to-raw:
	python3 -m mlops_nba.data_pipeline.pre_raw_to_raw --folder-prefix $(folder_prefix)

raw-to-curated:
	python3 -m mlops_nba.data_pipeline.raw_to_curated --folder-prefix $(folder_prefix)

curated-to-preprocessed:
	python3 -m mlops_nba.data_pipeline.curated_to_preprocessed

run: curated-to-preprocessed