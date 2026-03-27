#!/bin/bash

set -e

mypy -p house_manager

mypy bin/server.py

${BLACK:-black} --check bin/server.py house_manager/
