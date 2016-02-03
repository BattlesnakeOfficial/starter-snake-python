# battlesnake-python

A simple [BattleSnake AI](http://battlesnake.io) written in Python.

You will need:
* a working Python 2.7 development environment ([getting started guide](http://hackercodex.com/guide/python-development-environment-on-mac-osx/)).
* experience [deploying Python apps to Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
* 
* [pip](https://pip.pypa.io/en/latest/installing.html) to install Python dependencies.

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) to serve requests and the [gunicorn web server](http://gunicorn.org/) for running bottle on Heroku. Dependencies are listed in [requirements.txt](requirements.txt).


##### DOES THIS WORK STILL??
[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Running the Snake Locally

1) [Fork this repo](#fork-destination-box).

2) Clone repo to your development environment:
```
git clone git@github.com:username/battlesnake-python.git
```

3) Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):
```
pip install -r requirements.txt
```

4) Run local server:
```
python app/main.py
```

5) Test client in your browser: [http://localhost:8080](http://localhost:8080).

## Deploying to Heroku

1) Create a new Heroku app:
```
heroku create [APP_NAME]
```

2) Deploy code to Heroku servers:
```
git push heroku master
```

3) Open Heroku app in browser:
```
heroku open
```
or visit [http://APP_NAME.herokuapp.com](http://APP_NAME.herokuapp.com).

4) View server logs with the `heroku logs` command:
```
heroku logs --tail
```

## Questions?

[Email](mailto:battlesnake@sendwithus.com), [Twitter](http://twitter.com/send_with_us)
