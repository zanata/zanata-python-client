# Makefile for python client

default: test

sdist:
	python setup.py sdist

install:
	python setup.py install

uninstall:
	@/bin/echo "NB: if you don't have pip-python, try this: rm -rf /usr/bin/flies /usr/bin/zanata /usr/lib/python2.*/site-packages/zanata*"
	pip-python uninstall zanata-python-client

clean:
	python setup.py clean

run:
	python zanata help

lint:
	pylint -E zanata zanataclient # NB: requires recent version of pylint

lint-report:
	pylint --reports=n zanata zanataclient

test: 
	(cd test; python test_all.py)

all: run lint test sdist

.PHONY: test uninstall
