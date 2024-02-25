# README

## Installation

All actions to take place in root of project.

Get the right python:

```
pyenv install < .python-version
```

Create the virtualenv

```
mkvirtualenv daniel.feldroy.com
pip install -r requirements.txt
```

# Running

```
uvicorn main:app --reload
```

# Deploying on fly.io

1. Create an account on fly.io
2. Login with `fly auth login`
3. Deploy with `fly deploy`
4. Get a coffee, the screen will do docker stuff for a wgile
5. Enter `fly open`
