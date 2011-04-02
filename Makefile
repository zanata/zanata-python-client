# Makefile for python client
VERSION_GEN = $(shell ./VERSION-GEN)

all: setup.py VERSION-GEN
	$(VERSION_GEN)
	python setup.py sdist
