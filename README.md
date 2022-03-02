# Getting started with [Battlesnake](http://play.battlesnake.com?utm_source=github&utm_medium=readme&utm_campaign=python_starter&utm_content=homepage) and Python

![Battlesnake Logo](https://media.battlesnake.com/social/StarterSnakeGitHubRepos_Python.png)

This is a basic implementation of the [Battlesnake API](https://docs.battlesnake.com/references/api) in Python. It's a great starting point for anyone wanting to program their first Battlesnake using Python, and comes ready to deploy with [Replit](https://repl.it) and [Heroku](https://heroku.com), or you can use any other cloud provider you'd like.

## Technologies Used

* [Python3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/)


## Quickstart

The [Quick Start Coding Guide](https://docs.battlesnake.com/guides/getting-started) provides the full set of instructions to customize, register, and create your first games with your Battlesnake! While the guide uses [Replit](https://repl.it) as an example host, the instructions can be modified to work with any hosting provider. You can also find advice on other hosting providers on our [Hosting Suggestions](https://docs.battlesnake.com/references/hosting-suggestions) page.

### Prerequisites

* A free [Battlesnake Account](https://play.battlesnake.com/?utm_source=github&utm_medium=readme&utm_campaign=python_starter&utm_content=homepage)

---

## Customizing Your Battlesnake

Locate the `get_info` function inside [logic.py](logic.py#L11). You should see a line that looks like this:

```python
return {
    "apiversion": "1",
    "author": "",
    "color": "#888888",
    "head": "default",
    "tail": "default",
}
```

This function is called by the game engine periodically to make sure your Battlesnake is healthy, responding correctly, and to determine how your Battlesnake will appear on the game board. See [Battlesnake Personalization](https://docs.battlesnake.com/references/personalization) for how to customize your Battlesnake's appearance using these values.

Whenever you update these values, go to the page for your Battlesnake and select 'Refresh Metadata' from the option menu. This will update your Battlesnake to use your latest configuration and those changes should be reflected in the UI as well as any new games created.

## Changing Behavior

On every turn of each game your Battlesnake receives information about the game board and must decide its next move.

Locate the `choose_move` function inside [logic.py](logic.py#L27). Possible moves are "up", "down", "left", or "right" and initially your Battlesnake will choose a move randomly. Your goal as a developer is to read information sent to you about the game (available in the `data` variable) and decide where your Battlesnake should move next. All your Battlesnake logic lives in [logic.py](logic.py), and this is the code you will want to edit.

See the [Battlesnake Game Rules](https://docs.battlesnake.com/references/rules) for more information on playing the game, moving around the board, and improving your algorithm.

## (Optional) Running Your Battlesnake Locally

Eventually you might want to run your Battlesnake server locally for faster testing and debugging. You can do this by installing [Python 3.8](https://www.python.org/downloads/) and running:

```shell
python src/main.py
```

**Note:** You cannot create games on [play.battlesnake.com](https://play.battlesnake.com) using a locally running Battlesnake unless you install and use a port forwarding tool like [ngrok](https://ngrok.com/). See [Hosting Suggestions.](https://docs.battlesnake.com/references/hosting-suggestions#local)

## Running Tests

This Starter Project comes with a very simple test suite for you to expand! Located in [src/tests.py](src/tests.py) you can run them using the following command:
```python src/tests.py -v```

---

## Playing Battlesnake

### Completing Challenges

If you're looking for the Single Player Mode of Battlesnake, or something to practice with between events, check out [Challenges.](https://docs.battlesnake.com/guides/quick-start-challenges-guide)

### Joining a Battlesnake Arena

Once you've made your Battlesnake behave and survive on its own, you can enter it into the [Global Battlesnake Arena](https://play.battlesnake.com/arena/global) to see how it performs against other Battlesnakes worldwide.

Arenas will regularly create new games and rank Battlesnakes based on their results. They're a good way to get regular feedback on how well your Battlesnake is performing, and a fun way to track your progress as you develop your algorithm.

### Joining a Battlesnake League

Want to get out there to compete and win prizes? Check out the [Quick Start League Guide](https://docs.battlesnake.com/guides/quick-start-league-guide) for information on the how and when of our competitive seasons.

---

## Resources

All documentation is available at [docs.battlesnake.com](https://docs.battlesnake.com), including detailed Guides, API References, and Tips.

You can also join the Battlesnake Developer Community on [Discord](https://play.battlesnake.com/discord?utm_source=github&utm_medium=readme&utm_campaign=python_starter&utm_content=discord). We have a growing community of Battlesnake developers of all skill levels wanting to help everyone succeed and have fun with Battlesnake :)

Check out live Battlesnake events on [Twitch](https://www.twitch.tv/battlesnakeofficial) and see what is happening when on the [Calendar.](https://play.battlesnake.com/calendar?utm_source=github&utm_medium=readme&utm_campaign=python_starter&utm_content=calendar)

Want to contribute to Battlesnake? We have a number of open-source codebases and would love for you to get involved! Check out our page on [Contributing.](https://docs.battlesnake.com/guides/contributing)


## Feedback

**Do you have an issue or suggestions for this repository?** Head over to our [Feedback Repository](https://play.battlesnake.com/feedback?utm_source=github&utm_medium=readme&utm_campaign=python_starter&utm_content=feedback) today and let us know!
