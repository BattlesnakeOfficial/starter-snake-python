# A simple [Battlesnake](http://play.battlesnake.com) written in Python.

This is a basic implementation of the [Battlesnake API](https://docs.battlesnake.com/snake-api). It's a great starting point for anyone wanting to program their first Battlesnake using Python. It comes ready to deploy to [Heroku](https://heroku.com), but you can use other cloud providers if you'd like.

### Technologies

This Battlesnake uses [Python 3.7](https://www.python.org/) and [CherryPy](https://cherrypy.org/), deployed to [Heroku](https://heroku.com).

### Prerequisites

* [GitHub Account](https://github.com/) and [Git Command Line](https://www.atlassian.com/git/tutorials/install-git)
* [Heroku Account](https://signup.heroku.com/) and [Command Line](https://devcenter.heroku.com/categories/command-line)
* [Battlesnake Account](https://play.battlesnake.com)

## Deploying Your First Battlesnake

1. [Fork this repo](https://github.com/BattlesnakeOfficial/starter-snake-python/fork) into your own GitHub Account

2. [Clone your forked repo](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) to your local dev environment
    ```shell
    git clone git@github.com:[YOUR-GITHUB-USERNAME]/starter-snake-python.git
    ```

3. [Create a new Heroku app](https://devcenter.heroku.com/articles/creating-apps)
    ```shell
    heroku create [YOUR-APP-NAME]
    ```

4. [Deploy your code to Heroku](https://devcenter.heroku.com/articles/git#deploying-code)
    ```shell
    git push heroku master
    ```

5. Open your new Heroku app in your browser
    ```shell
    heroku open
    ```
    If everything worked successfully, your browser should open up to http://[YOUR-APP-NAME].herokuapp.com and show the following message:
    ```
    Your Battlesnake is alive!
    ```

6. If you want, you can view your server logs using the [Heroku logs command](https://devcenter.heroku.com/articles/logging#log-retrieval)
    ```shell
    heroku logs --tail
    ```
    (the `--tail` option will show a live feed of your logs in real-time)

**At this point your Battlesnake is live and ready to enter games!**

## Register Your Battlesnake and Create Your First Game

1. [Login to your Battlesnake account](https://play.battlesnake.com/login/) if you haven't already

2. [Create a new Battlesnake](https://play.battlesnake.com/account/snakes/create/).

    **Name**<br>
    Whatever you want to call your Battlesnake!

    **URL**<br>
    The URL for your Heroku app, http://[YOUR-APP-NAME].herokuapp.com.

    **Description**<br>
    Describe your Battlesnake for other Battlesnake Developers who might be interested.

    **Tags**<br>
    List any technologies you used to build your Battlesnake - probably `Heroku` and `Python`.

    **Allow anyone to add your snake to a game?**<br>
    Select this if you want to allow other Battlesnake Developers to enter this Battlesnake into their own games.

3. Once your Battlesnake has been created, click [Create Game](https://play.battlesnake.com/account/games/create/) to start a new game with your new Battlesnake. Type your Battlesnake's name into the search field and click 'Add' to add it to the game. Then click 'Create Game' to start the game.

4. You should now see a brand new Battlesnake game with your Battlesnake in it! Yay! Press `Play` to start the game and watch how your Battlesnake does.

5. Repeat step 3 every time you want to start a new game and see how your snake behaves!

6. If you open your [Heroku logs](https://devcenter.heroku.com/articles/logging#log-retrieval) while the game is running, you'll see your snake recieving API calls from the game engine and responding with its moves.
    ```shell
    heroku logs --tail
    ```

**At this point you should have a registered Battlesnake and be able to create games!**

## Customizing Your Battlesnake

Now you're ready to start making your Battlesnake your own. By default, your Battlesnake won't be unique looking, nor very smart. Let's change that!

### Customize your Battlesnake's appearance

When the game engine tells your Battlesnake that a new game is starting, you can optionally reply with what color you want to Battlesnake to be, and what you want your head and tail to look like.

Locate the `start` function inside server.py. You should see a line that looks like this:
```python
return {"color": "#888888", "headType": "regular", "tailType": "regular"}
```

See the [Battlesnake Documentation - Customizing Your Battlesnake](https://docs.battlesnake.com/snake-customization) for how to customize your Battlesnake's appearance using these values.

### Change Your Battlesnake's Behaviour

On every turn of the game, your Battlesnake receives information about the game board and has to respond with its next move.

Locate the `move` function inside server.py. You should see a line that looks like this:
```python
return {"move": "up"}
```

Your Battlesnake can move one of four directions: "up", "down", "left", or "right". For now, choose a new direction to move in.

See the [Battlesnake Documentation - Battlesnake Rules](https://docs.battlesnake.com/rules) for more information on playing the game and moving around the board.

### Updating Your Battlesnake

Once you've made your changes, commit them using git and deploy your changes to Heroku.
```shell
git add .
git commit -m "update my battlesnake's appearance"
git push heroku master
```

Once heroku has been updated, you can [start a new game](https://play.battlesnake.com/account/games/create/) with your Battlesnake to view your new changes!

**At this point you should feel comfortable making changes to your code and deploying those changes to Heroku!**

## Developing Your Battlesnake

Now you have everything you need to start making your Battlesnake smarter. Here are a few helpful tips as you get going...

* Keeping your `heroku logs --tail` command always running in a second window is always helpful for watching activity and debugging any problems with your Battlesnake.

* You can use the Python `print()` function to output information to your `heroku logs` stream. This is very useful for viewing what information is available in each command, and debugging any logic in your code during Battlesnake games.

* Review the [Battlesnake API Docs](https://docs.battlesnake.com/snake-api) to learn what information is provided with each comamnd. You can also output the data to your logs:
    ```python
    def move(self):
        data = cherrypy.request.json
        print(data)
        return {"move": "up"}
    ```

* When viewing a Battlesnake game, you can pause playback and move forward/backward one frame at a time. If you review your logs at the same time, you can see what decision your Battlesnake made on each turn.

Once you've made your Battlesnake behave and survive on its own, you can enter it into the [Global Battlesnake Arena](https://play.battlesnake.com/arena/global) to see how it performs against other Developers.

---

### Questions?

You can join the [Battlesnake Developer Community on Slack](https://play.battlesnake.com/slack). We have a growing community of Battlesnake Developers of all skill levels wanting to help everyone succeed and have fun with Battlesnake :)
