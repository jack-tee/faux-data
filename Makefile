.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))

init:
	@virtualenv venv
	@pip install -r requirements.txt -r local_requirements.txt
	@echo "activate the virtualenv with 'source venv/bin/activate'"

test:
	pytest

docs:
	@python docs/main.py
