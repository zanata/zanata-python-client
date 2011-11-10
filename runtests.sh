#!/bin/sh
if which coverage > /dev/null; then
    coverage run test/test_all.py
    coverage report
else
    /usr/bin/env python tests/tests.py
fi
