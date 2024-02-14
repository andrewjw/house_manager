#!/bin/bash

set -e

mypy -m house_manager

mypy bin/server.py

${PYCODESTYLE:-pycodestyle} bin/server.py house_manager/
