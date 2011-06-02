# Makefile for python client

default: test

sdist:
	python setup.py sdist

install:
	python setup.py install

uninstall:
	rm -fr /usr/lib/python2.*/site-packages/zanata*

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
