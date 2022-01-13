SHELL := /bin/bash

.DEFAULT_GOAL := help

VENV := venv

virtualenv: ## Create virtualenv
	@if [ -d $(VENV) ]; then rm -rf $(VENV); fi
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

update-requirements-txt: VENV := /tmp/venv
update-requirements-txt: ## Update requirements.txt
	@if [ -d $(VENV) ]; then rm -rf $(VENV); fi
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install wheel
	$(VENV)/bin/pip install -r unpinned_requirements.txt
	echo "# DO NOT EDIT! Automatically created by make update-requirements-txt" > requirements.txt
	$(VENV)/bin/pip freeze | grep -v pkg_resources >> requirements.txt

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-25s %s\n" "task" "help" ; \
	printf "%-25s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-25s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done	
