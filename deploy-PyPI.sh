#!/bin/bash
rm -rf dist/; python3.8 -m build -o dist/

# to testpypi
pipenv run twine upload --repository testpypi dist/*
# https://test.pypi.org/project/pronunciation-dictionary/

# to pypi
pipenv run twine upload --repository pypi dist/*
