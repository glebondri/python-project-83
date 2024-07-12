install:
	poetry install
dev:
	poetry run flask --debug --app page_analyzer.app:app run
lint:
	poetry run flake8
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app
waitress-serve:
	poetry run waitress-serve --listen='0.0.0.0:$(PORT)' page_analyzer.app:app