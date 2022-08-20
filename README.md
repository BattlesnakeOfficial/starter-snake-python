# Battlesnake Python Starter Project

![Battlesnake Logo](https://media.battlesnake.com/social/StarterProjectBanner-Python.png)

This project is a simple template that implements the [Battlesnake API](https://docs.battlesnake.com/api) in Python. It's a great starting point for anyone wanting to program their first Battlesnake, and can easily be deployed to a cloud provider of your choosing or run locally using a tool like [ngrok](https://ngrok.com/).

**To get started, click [Use This Template](https://github.com/BattlesnakeOfficial/starter-snake-python/generate) to clone it to your own GitHub account.**

## Technologies Used

* [Python 3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/)

## Run Your Battlesnake

Install dependencies using pip

```sh
pip install -r requirements.txt
```

Start your Battlesnake

```sh
python main.py
```

You should see the following output once it is running

```sh
Running your Battlesnake at http://0.0.0.0:8000
 * Serving Flask app 'My Battlesnake'
 * Debug mode: off
```

Open [localhost:8000](http://localhost:8000) in your browser and you should see

```json
{"apiversion":"1","author":"","color":"#888888","head":"default","tail":"default"}
```

## Play a Game Locally

Install the [Battlesnake CLI](https://github.com/BattlesnakeOfficial/rules/tree/main/cli)
* You can [download compiled binaries here](https://github.com/BattlesnakeOfficial/rules/releases)
* or [install as a go package](https://github.com/BattlesnakeOfficial/rules/tree/main/cli#installation) (requires Go 1.18 or higher)

Command to run a local game

```sh
battlesnake play -W 11 -H 11 --name 'Python Starter Project' --url http://localhost:8000 -g solo --browser
```

## Next Steps

Continue with the [Battlesnake Quickstart Guide](https://docs.battlesnake.com/quickstart) to customize and improve your Battlesnake's behavior.

**Note:** To play games on [play.battlesnake.com](https://play.battlesnake.com) you'll need to deploy your Battlesnake to a live web server OR use a port forwarding tool like [ngrok](https://ngrok.com/) to access your server locally.
