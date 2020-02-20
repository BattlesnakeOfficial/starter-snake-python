# starter-snake-python

A simple [Battlesnake AI](http://play.battlesnake.com) written in Python.

Visit [https://github.com/BattlesnakeOfficial/community/blob/master/starter-snakes.md](https://github.com/BattlesnakeOfficial/community/blob/master/starter-snakes.md) for API documentation and instructions for running your AI.

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) to serve requests and the [gunicorn web server](http://gunicorn.org/) for running bottle on Heroku. Dependencies are listed in [requirements.txt](requirements.txt).

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Prerequisites

- a working [Python 3.7](https://www.python.org/downloads/) development environment ([MacOS guide](http://hackercodex.com/guide/python-development-environment-on-mac-osx/), [Windows guide](https://docs.battlesnake.com/tutorials/python))
- [pip](https://pip.pypa.io/en/latest/installing.html) to install Python dependencies
- experience [deploying Python apps to Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)

## Running the Snake Locally

1. [Fork this repo](https://github.com/BattlesnakeOfficial/starter-snake-python/fork).

2. Clone repo to your development environment:

    ```shell
    git clone git@github.com:<your github username>/starter-snake-python.git
    ```

3. Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):

    ```shell
    pip install -r requirements.txt
    ```

4. Run local server:

    ```shell
    python run.py
    ```

5. Test your snake by sending a curl to the running snake

    ```shell
    curl -XPOST -H 'Content-Type: application/json' -d '{ "hello": "world"}' http://localhost:8080/start
    ```

## Deploying to Heroku

1. Create a new Heroku app:

    ```shell
    heroku create [APP_NAME]
    ```

2. Deploy code to Heroku servers:

    ```shell
    git push heroku master
    ```

3. Open Heroku app in browser:

    ```shell
    heroku open
    ```

or visit [http://APP_NAME.herokuapp.com](http://APP_NAME.herokuapp.com).

4. View server logs with the `heroku logs` command:

    ```shell
    heroku logs --tail
    ```

## Questions?

Email [hello@battlesnake.com](mailto:hello@battlesnake.com), or tweet [@battlesnakeio](http://twitter.com/battlesnakeio).
