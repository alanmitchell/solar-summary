#!/usr/bin/bash
set +e
source env/bin/activate
./collect.py
quarto render index.qmd
deactivate
