# Makefile for python client

NOSE_FLAGS=--with-coverage --cover-package=zanataclient --cover-tests -sv

default: all

sdist: all lint test
	python setup.py sdist

install: all
	python setup.py install

uninstall:
	@/bin/echo "NB: if you don't have pip, try this: rm -rf /usr/bin/flies /usr/bin/zanata /usr/lib/python2.*/site-packages/zanata*"
	pip uninstall zanata-python-client

clean:
	python setup.py clean
	rm -f zanataclient/VERSION-FILE

run:
	python zanata help

lint:
	pylint -E zanata zanataclient # NB: requires recent version of pylint

lint-report:
	pylint --reports=n zanata zanataclient

flake8:
	flake8 --ignore=E501,F403,F841,F401 zanataclient test

test:
	(cd test; nosetests ${NOSE_FLAGS} test_all.py)

all: zanataclient/VERSION-FILE

zanataclient/VERSION-FILE:
	./VERSION-GEN

help:
	@echo "Avail targets:"
	@echo "   all sdist install uninstall clean run lint lint-report test"
	@echo ""
	@echo "For help on zanata itself, use 'make run'"


.PHONY: all sdist install uninstall clean run lint lint-report flake8 test
