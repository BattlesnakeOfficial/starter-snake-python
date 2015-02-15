## battlesnake-python

A simple [BattleSnake AI](http://battlesnake.io) written in Python. Available live at [battlesnake-python.herokuapp.com](http://battlesnake-python.herokuapp.com).

To get started you'll need a working Python 2.7.6+ development environment and should be familiar with [deploying Python apps to Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction).

If you don't have a Python environment setup, we suggest [starting here](http://hackercodex.com/guide/python-development-environment-on-mac-osx/). You'll need [pip](https://pip.pypa.io/en/latest/installing.html) and [virtualenv](https://virtualenv.pypa.io/en/latest/) for dependency management. We also suggest using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/).

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) for route management and response building, and the [gunicorn web server](http://gunicorn.org/) for running bottle on Heroku.

Dependencies are listed in [requirements.txt](requirements.txt).

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### Running the AI locally

Fork and clone this repo:
```
> git clone git@github.com:sendwithus/battlesnake-python.git
> cd battlesnake-python
```

Create new virtualenv (using virtualenvwrapper) and install dependencies:
```
> mkvirtualenv battlesnake-python
> workon battlesnake-python
> pip install -r requirements.txt
```

Run the server locally:
```
> ./run
Bottle v0.12.8 server starting up (using WSGIRefServer())...
Listening on http://localhost:8080/
Hit Ctrl-C to quit.
```

Test client in your browser: [http://localhost:8080](http://localhost:8080)

### Deploying to Heroku

Create a new Heroku app:
```
heroku create [APP_NAME]
```

Push code to Heroku servers:
```
git push heroku master
```

Open Heroku app in browser.
```
heroku open
```

Or go directly to: [http://APP_NAME.herokuapp.com](http://APP_NAME.herokuapp.com)

You can also view liveserver logs with the heroku logs command:
```
heroku logs --tail
```

### Questions?

[Email](mailto:battlesnake@sendwithus.com), [Twitter](http://twitter.com/send_with_us)
