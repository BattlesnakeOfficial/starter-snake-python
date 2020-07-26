# Original Repo: [here](https://github.com/ArthurFirmino/gym-battlesnake)

Changes vs original:

* Updated input layer (now has 12 input feature layers, instead of original 6)
* Proper food spawning rules (to make arena)
* Game execution logic bugfixes
* Uses pytorch
* Removed SFML rendering dependency

# Gym-Battlesnake

Gym-Battlesnake is a multi-agent reinforcement learning environment inspired by the annual Battlesnake event held in Victoria, BC each year, and conforming to the OpenAI Gym interface.

## Features

  - Multi-threaded game implementation written in fast C++
  - Single agent training with multiple other agents as opponents

## Installation
### Prerequisites
Gym-Battlesnake has only been tested on **Ubuntu 18.04**. Install the dependencies using the command:

```
sudo apt-get update && sudo apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev
```

## Contributing
 1. **Fork**
 2.  **Clone and Setup**
 3. **Develop**
 4.  **Pull Request**
