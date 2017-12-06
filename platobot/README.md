# Plato-Bot

This is a backend application (long running process) which will help orchestrate conversations

UPDATE:

* Stray files in Project root:
  * tox.ini -  This is how `tox` identifies, that the current directory is a tox project.
  * requirements.txt - Define all the python dependencies here, tox reads this to get list of third party packages and versions to install in the venv.
  * activate - This script can be sourced to activate the venv in the current shell session. So instead of referring `.tox/py36/bin/python`, we can just run python scripts with `python`.
  * .gitignore - Standard file in a git project to exclude files not intended to be put in version control.
  * setup.sh - Intended to be the sole script we could run to setup this project (run tox, create angular build, etc)

## Setup Guide:
  * You should have these installed:
      * mysql (see below if you want to use docker)
      * python 3.6.x - Use official python installer (https://www.python.org/downloads/release/python-364/)
      * pip  `sudo easy_install pip`
      * tox  `pip install tox`

  * **Project setup**
      * `./setup.sh` to setup the python virtual environment - put all setup steps here
      * Make sure your virtual environment is activated while you are developing on the `platobot` project.
      * `python -m platobot.bin.bootstrap_db`

  * **Pycharm**
      * Setup project interpreter in Pycharm->Preferences->Project Interpreter
      * Interpreter is located in .tox directory which is hidden, on Mac this could be a problem since
        Finder won't show hidden folders and pycharm won't let you add path manually. Don't panic, when pycharm
        opens Finder dialogue to enable selection of interpreter, just do CMD + SHIFT + G to enter path
        or CMD + SHIFT + . to show hidden files :)

  * **Dependencies:**
    * Python dependencies are specified in requirements.txt - mainly used by platobot

## Run Guide:

  * To bootstrap database, run `python platobot/bin/bootstrap_db.py`. Enter 'I agree' to confirm.

  * To run flask server, run `./run_server.sh`. To stop server and kill daemon processes, run `./stop_server.sh`.

  * To run gunicorn server(serve multiple http requests at same time), run `./server.sh start`. To stop it and kill daemon processes, run `./server.sh stop`.

## Test
  * `./run_test.sh`
  * run one test: `nose2 platobot.test.test_webhook.TestWebhook`

## mysql docker setup
```
docker pull mysql/mysql-server
docker run --name mysqlserver -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_ROOT_HOST=172.17.0.1 -d mysql/mysql-server
```

After the set up, `docker start mysqlserver` will start the mysql server, don't need to execute docker run again.
