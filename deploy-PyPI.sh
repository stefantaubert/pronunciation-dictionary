#!/bin/bash
python3.8 -m build

# to testpypi
pipenv run twine upload --repository testpypi dist/*

# to pypi
pipenv run twine upload --repository pypi dist/*