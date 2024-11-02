all: test black lint
	@echo "All done"
test:
	pytest -o log_cli=true -vv  -W ignore::DeprecationWarning

black:
	black --line-length 91 .

lint:
	flake8 .
