all: test black lint
	@echo "All done"
test:
	pytest -o log_cli=true --log-cli-level=DEBUG -vv  -W ignore::DeprecationWarning

black:
	black --line-length 91 .

lint:
	flake8 .
