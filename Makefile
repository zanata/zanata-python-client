# Makefile for python client

default: test

sdist:
	python setup.py sdist

install:
	python setup.py install

run:
	python zanata help

lint:
	pylint -E zanata zanataclient # NB: requires recent version of pylint

lint-report:
	pylint --reports=n zanata zanataclient

test: 
	(cd test; ls test_*.py | xargs --verbose -n1 python)

all: run lint test sdist

.PHONY: test
