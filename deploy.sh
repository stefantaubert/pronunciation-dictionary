#!/bin/bash

prog_name="pronunciation-dictionary-cli"
cli_path=src/pronunciation_dictionary/cli.py

mkdir -p ./dist-freeze

pipenv run cxfreeze \
  -O \
  --compress \
  --target-dir=dist-freeze \
  --zip-include "/usr/lib/python3.8/typing.py" \
  --target-name=cli \
  $cli_path

cd dist-freeze
zip $prog_name-linux.zip ./ -r
cd ..
echo "zipped."