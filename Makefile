# Makefile for python client

default: all

sdist: all lint test
	python setup.py sdist

install:
	python setup.py install

uninstall:
	@/bin/echo "NB: if you don't have pip-python, try this: rm -rf /usr/bin/flies /usr/bin/zanata /usr/lib/python2.*/site-packages/zanata*"
	pip-python uninstall zanata-python-client

clean:
	python setup.py clean
	rm -f zanataclient/VERSION-FILE

run:
	python zanata help

lint:
	pylint -E zanata zanataclient # NB: requires recent version of pylint

lint-report:
	pylint --reports=n zanata zanataclient

test: 
	(cd test; python test_all.py)

all: zanataclient/VERSION-FILE

zanataclient/VERSION-FILE:
	./VERSION-GEN

help:
	@echo "Avail targets:"
	@echo "   all sdist install uninstall clean run lint lint-report test"
	@echo ""
	@echo "For help on zanata itself, use 'make run'"


.PHONY: all sdist install uninstall clean run lint lint-report test
