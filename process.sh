#!/usr/bin/bash
set +e
source env/bin/activate
./collect.py
/usr/local/bin/quarto render index.qmd
deactivate
