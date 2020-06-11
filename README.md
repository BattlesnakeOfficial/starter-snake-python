# A simple [Battlesnake](http://play.battlesnake.com) written in Python.

This is a basic implementation of the [Battlesnake API](https://docs.battlesnake.com/references/api). It's a great starting point for anyone wanting to program their first Battlesnake using Python. It comes ready to use with [Repl.it](https://repl.it), or even deploy to [Heroku](https://heroku.com). You can also use other cloud providers if you'd like.

### Technologies Used

* [Python3](https://www.python.org/)
* [CherryPy](https://cherrypy.org/)

# Programming your first Battlesnake using [Repl.it](https://repl.it)



## Prerequisites

* [Battlesnake Account](https://play.battlesnake.com)
* [Repl.it Account](https://repl.it)
* [GitHub Account](https://github.com) (Optional)

## Running your code on [Repl.it](https://repl.it)

1. Login to your [Repl.it](https://repl.it) account.

2. Create a new Repl and select `Import From GitHub`.

3. Paste the URL for this GitHub repo into the text field.

    ```
    https://github.com/BattlesnakeOfficial/starter-snake-python
    ```

4. Click Import from GitHub to finish creating your new Repl. You should see your new Repl being created - this might take a few moments to complete.

4. Once your Repl is ready to run, click `run ▶️` at the top of the screen. You should see CherryPy and any other dependencies being installed. Once installation is complete, your server will start:

    ```
    Starting Battlesnake Server...
    ENGINE Serving on http://0.0.0.0:8080
    ```

5. Above the terminal window you'll see the live output from your Battlesnake server, including its URL. That URL will be the URL used to create your Battlesnake in the next step.

    You should see output similar to this:

    ```
    {"apiversion": "1", "author": "", "color": "#888888", "head": "default", "tail": "default"}
    ```

**At this point your Battlesnake is live and ready to enter games!**



## Registering your Battlesnake and creating your first game

1. Sign in to [play.battlesnake.com](https://play.battlesnake.com/login/).

2. Go [here to create a new Battlesnake](https://play.battlesnake.com/account/snakes/create/). Give it a meaningful name and complete the form using the URL for your Repl from above.

3. Once your Battlesnake has been saved you can [create a new game](https://play.battlesnake.com/account/games/create/) and add your Battlesnake to it. Type your Battlesnake's name into the search field and click "Add" to add it to the game. Then click "Create Game" to start the game.

4. You should see a brand new Battlesnake game with your Battlesnake in it! Yay! Press "Play" to start the game and watch how your Battlesnake behaves. By default your Battlesnake should move randomly around the board.

5. Optionally, watch your Repl logs while the game is running to see your Battlesnake receiving API calls and responding with its moves.

Repeat steps 3 and 4 every time you want to see how your Battlesnake behaves. It's common for Battlesnake developers to repeat these steps often as they make their Battlesnake smarter.

You can also use the "Create Rematch" button to quickly start a new game using the same Battlesnakes and configuration.

**At this point you should have a registered Battlesnake and be able to create games!**



## Customizing Your Battlesnake

Now you're ready to start customizing your Battlesnake and improving its algorithm.

### Changing Appearance

Locate the `index` function inside [server.py](server.py#L15). You should see a line that looks like this:
```python
return {
    "apiversion": "1",
    "author": "",
    "color": "#888888",
    "head": "default",
    "tail": "default",
}
```

This function is called by the game engine to make sure your Battlesnake is healthy and responding correctly. Your response determines what your Battlesnake will look like on the game board. See [Battlesnake Personalization](https://docs.battlesnake.com/references/personalization) for how to customize your Battlesnake's appearance using these values.

Whenever you update these values, go to the page for your Battlesnake and select 'Refresh Metadata' from the option menu. This will update your Battlesnake to use your latest configuration.

### Changing Behavior

On every turn of each game your Battlesnake receives information about the game board and must decide its next move.

Locate the `move` function inside [server.py](server.py#L37). Possible moves are "up", "down", "left", or "right". To start your Battlesnake will choose a move randomly. Your goal as a developer is to read information sent to you about the board (available in the `data` variable) and make an intelligent decision about where your Battlesnake should move next.

See the [Battlesnake Game Rules](https://docs.battlesnake.com/references/rules) for more information on playing the game, moving around the board, and improving your algorithm.

### Updating Your Battlesnake

After making changes to your Battlesnake, you can stop and restart your Repl to have the change take effect (or in many cases your Repl will restart automatically).

Once the Repl has restarted, you can [create a new game](https://play.battlesnake.com/account/games/create/) with your Battlesnake to watch your latest changes in action.

**At this point you should feel comfortable making changes to your code and starting new Battlesnake games to test those changes!**



## Developing Your Battlesnake Further

Now you have everything you need to start making your Battlesnake super smart!

### Early Development Goals

- [ ] Avoid colliding with yourself
- [ ] Avoid colliding with walls
- [ ] Try to move towards food
- [ ] Avoid colliding with other snakes

Once you have completed those steps, you'll be ready to compete live against other Battlesnakes, and start implementing more complex strategies to surive.


### Helpful Tips

* Keeping your Repl open in a second window while games are running is helpful for watching server activity and debugging any problems with your Battlesnake.

* You can use the Python [print function](https://docs.python.org/3.7/library/functions.html#print) to output information to your server logs. This is very useful for debugging logic in your code during Battlesnake games.

* Review the [Battlesnake API Docs](https://docs.battlesnake.com/references/api) to learn what information is provided with each command.

* When viewing a Battlesnake game you can pause playback and step forward/backward one frame at a time. If you review your logs at the same time, you can see what decision your Battlesnake made on each turn.



## Joining a Battlesnake Arena

Once you've made your Battlesnake behave and survive on its own, you can enter it into the [Global Battlesnake Arena](https://play.battlesnake.com/arena/global) to see how it performs against other Battlesnakes worldwide.

Arenas will regularly create new games and rank Battlesnakes based on their results. They're a good way to get regular feedback on how well your Battlesnake is performing, and a fun way to track your progress as you develop your algorithm.



## (Optional) Using a Cloud Provider

As your Battlesnake gets more complex, it might make sense to move it to a dedicated hosting provider such as Heroku or AWS. We suggest choosing a platform you're familiar with, or one you'd be interested in learning more about.

If you have questions or ideas, our developer community on [Slack](https://play.battlesnake.com/slack) and [Discord](https://play.battlesnake.com/discord) will be able to help out.



## (Optional) Running Your Battlesnake Locally

Eventually you might want to run your Battlesnake server locally for faster testing and debugging. You can do this by installing [Python 3.7](https://www.python.org/downloads/) and running:

```shell
python server.py
```

**Note:** You cannot create games on [play.battlesnake.com](https://play.battlesnake.com) using a locally running Battlesnake unless you install and use a port forwarding tool like [ngrok](https://ngrok.com/).


---


### Questions?

All documentation is available at [docs.battlesnake.com](https://docs.battlesnake.com), including detailed Guides, API References, and Tips.

You can also join the [Battlesnake Developer Community on Slack](https://play.battlesnake.com/slack). We have a growing community of Battlesnake developers of all skill levels wanting to help everyone succeed and have fun with Battlesnake :)
