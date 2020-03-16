# A simple [Battlesnake](http://play.battlesnake.com) written in Python.

This is a basic implementation of the [Battlesnake API](https://docs.battlesnake.com/snake-api) that moves randomly around the board. It's a great starting point for anyone wanting to program their first Battlesnake using Python. It comes ready to deploy to [Heroku](https://heroku.com), and you can use other cloud providers if you'd like.

### Technologies

This Battlesnake uses [Python 3.7](https://www.python.org/), [CherryPy](https://cherrypy.org/), and [Heroku](https://heroku.com).

### Prerequisites

* [GitHub Account](https://github.com/) and [Git Command Line](https://www.atlassian.com/git/tutorials/install-git)
* [Heroku Account](https://signup.heroku.com/) and [Heroku Command Line](https://devcenter.heroku.com/categories/command-line)
* [Battlesnake Account](https://play.battlesnake.com)



## Deploying Your First Battlesnake

1. [Fork this repo](https://github.com/BattlesnakeOfficial/starter-snake-python/fork) into your own GitHub Account.

2. [Clone your forked repo](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) to your local environment.
    ```shell
    git clone git@github.com:[YOUR-GITHUB-USERNAME]/starter-snake-python.git
    ```

3. [Create a new Heroku app](https://devcenter.heroku.com/articles/creating-apps).
    ```shell
    heroku create [YOUR-APP-NAME]
    ```

4. [Deploy your code to Heroku](https://devcenter.heroku.com/articles/git#deploying-code).
    ```shell
    git push heroku master
    ```

5. Open your new Heroku app in your browser.
    ```shell
    heroku open
    ```
    You should see the following text:
    ```
    Your Battlesnake is alive!
    ```

Optionally, you can view your server logs using the [Heroku logs command](https://devcenter.heroku.com/articles/logging#log-retrieval).
```shell
heroku logs --tail
```
(the `--tail` option will show a live feed of your logs in real-time)

**At this point your Battlesnake is live and ready to enter games!**



## Registering Your Battlesnake and Creating Your First Game

1. Log in to [play.battlesnake.com](https://play.battlesnake.com/login/).

2. [Create a new Battlesnake](https://play.battlesnake.com/account/snakes/create/).

    Give your Battlesnake a name, and complete the form using the URL for your Heroku app.

3. Once your Battlesnake has been created, you can [create a new game](https://play.battlesnake.com/account/games/create/) and add your Battlesnake to it.

    Type your Battlesnake's name into the search field and click 'Add' to add it to the game. Then click 'Create Game' to start the game running.

4. You should now see a brand new Battlesnake game with your Battlesnake in it! Yay! Press `Play` to start the game and watch how your Battlesnake does.

Repeat step 3 & 4 every time you want to start a new game and see how your snake behaves. It's common for Battlesnake developers to repeat these steps often as they make their Battlesnake smarter.

By default, your Battlesnake will move randomly around the board. See server.py for details on how it achieves that.

Optionally, open your [Heroku logs](https://devcenter.heroku.com/articles/logging#log-retrieval) while the game is running to see your Battlesnake receiving API calls and responding with its moves.
    ```shell
    heroku logs --tail
    ```

**At this point you should have a registered Battlesnake and be able to create games!**



## Customizing Your Battlesnake

Now you're ready to start making your Battlesnake yours.

### Changing Appearance

When the game engine tells your Battlesnake that a new game is starting, you can optionally reply with information about how you want your Battlesnake to look.

Locate the `start` function inside server.py. You should see a line that looks like this:
```python
return {"color": "#888888", "headType": "regular", "tailType": "regular"}
```

See [Customizing Your Battlesnake](https://docs.battlesnake.com/snake-customization) for how to customize your Battlesnake's appearance using these values.

### Changing Behavior

On every turn of each game your Battlesnake receives information about the game board and has to respond with its next move.

Locate the `move` function inside server.py. You should see code that looks like this:
```python
data = cherrypy.request.json
# Choose a random direction to move in
possible_moves = ["up", "down", "left", "right"]
move = random.choice(possible_moves)
return {"move": move}
```

Your Battlesnake can move one of four directions: "up", "down", "left", or "right". By default your Battlesnake chooses a direction randomly. Your goal is to read board information from `data` and make an intelligent decision on where your Battlesnake should move next.

See the [Battlesnake Rules](https://docs.battlesnake.com/rules) for more information on playing the game and moving around the board and developing your Battlesnake.

### Updating Your Battlesnake

After making changes, commit them using git and deploy your changes to Heroku.
```shell
git add .
git commit -m "update my battlesnake's appearance"
git push heroku master
```

Once heroku has updated you can [create a new game](https://play.battlesnake.com/account/games/create/) with your Battlesnake to view your latest changes in action.

**At this point you should feel comfortable making changes to your code and deploying those changes to Heroku!**



## Developing Your Battlesnake Further

Now you have everything you need to start making your Battlesnake smarter. Here are a few more helpful tips...

* Keeping your logs open in a second window (using `heroku logs --tail`) is helpful for watching activity and debugging any problems with your Battlesnake.

* You can use the Python [print()](https://docs.python.org/3.7/library/functions.html#print) function to output information to your server logs. This is very useful for viewing what information is available in each command, and debugging any logic in your code during Battlesnake games.

* Review the [Battlesnake API Docs](https://docs.battlesnake.com/snake-api) to learn what information is provided with each command. You can also output the data to your logs:
    ```python
    def move(self):
        data = cherrypy.request.json
        print(data)
        return {"move": "up"}
    ```

* When viewing a Battlesnake game, you can pause playback and move forward/backward one frame at a time. If you review your logs at the same time, you can see what decision your Battlesnake made on each turn.



## Joining a Battlesnake Arena

Once you've made your Battlesnake behave and survive on its own, you can enter it into the [Global Battlesnake Arena](https://play.battlesnake.com/arena/global) to see how it performs against other Battlesnakes.

Arenas will regularly create new games and rank Battlesnakes based on their results. They're a good way to get regular feedback on how well your Battlesnake is performing, and a fun way to track your progress as you develop your algorithm.



## (Optional) Running Your Battlesnake Locally

Eventually you might want to run your Battlesnake server locally for faster debugging and code testing. You can do this by installing [Python 3.7](https://www.python.org/downloads/) and running `server.py` from the command line:
    ```shell
    python server.py
    ```

**Note:** You cannot create games on [play.battlesnake.com](https://play.battlesnake.com) using a locally running Battlesnake unless you install a tunnelling tool like [ngrok](https://ngrok.com/).


---

### Questions?

All documentation is available at [docs.battlesnake.com](https://docs.battlesnake.com), including detailed Guides, API References, and Tips.

You can also join the [Battlesnake Developer Community on Slack](https://play.battlesnake.com/slack). We have a growing community of Battlesnake Developers of all skill levels wanting to help everyone succeed and have fun with Battlesnake :)
