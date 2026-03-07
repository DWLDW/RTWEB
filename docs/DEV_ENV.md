# DEVELOPMENT ENVIRONMENT

This project may be developed on multiple machines.

Important rules:

Encoding:
- UTF-8 without BOM.

Editing:
- Prefer Python patch scripts.
- Avoid PowerShell multiline replacements.

Validation:
Run after each change:

python -m py_compile app.py

Git workflow:

git add .
git commit -m "message"
git pull --rebase
git push

If local changes block pull:

git stash
git pull --rebase
git stash pop
