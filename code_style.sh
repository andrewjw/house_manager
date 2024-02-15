#!/bin/bash

set -e

mypy -p house_manager

mypy bin/server.py

${PYCODESTYLE:-pycodestyle} bin/server.py house_manager/
