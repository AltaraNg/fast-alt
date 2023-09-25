run-dev:
	echo "Starting Application In Development Mode"
	uvicorn main:app --reload --port=7001
test:
	pytest -v
execute-bank-statement:
	python bank_statement_reader.py

generate-statement:
	@echo "Generating bank statement class for "  $(bank_name)
	@python generate_statement.py $(bank_name)