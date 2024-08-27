### Hexlet tests and linter status:
[![Actions Status](https://github.com/glebondri/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/glebondri/python-project-83/actions)

[![Maintainability](https://api.codeclimate.com/v1/badges/492e58e7971271712d25/maintainability)](https://codeclimate.com/github/glebondri/python-project-83/maintainability)


# Page Analyzer
**A web tool to test out the URL's accessibility**

## Requirements:
 - Python (^3.10)
 - Poetry
 - PostgreSQL (16)

## Installation:
    $ git clone https://github.com/glebondri/python-project-83
    $ cd python-project-83
    $ make install

*Note:*
> `'SECRET_KEY'` & `'DATABASE_URL'` variables must be specified in `.env` file
> 
> or, defined via `environment variables`

## Running a Server:
> Fulfill the migration by running `make build` before starting a server

Use `'make dev'` to run a local server (dev purpose, w/ interactive traceback),

or `'make start'` to run a production-ready server  (`'make waitress-serve'` for Windows)


### Available [here](https://python-project-83-r29s.onrender.com/)