game = {
  "game": {
    "id": "totally-unique-game-id",
    "ruleset": {
      "name": "standard",
      "version": "v1.1.15",
      "settings": {
        "foodSpawnChance": 15,
        "minimumFood": 1,
        "hazardDamagePerTurn": 14
      }
    },
    "map": "standard",
    "source": "league",
    "timeout": 500
  },
  "turn": 14,
  "board": {
    "height": 11,
    "width": 11,
    "food": [
      {"x": 2, "y": 0},
      {"x": 1, "y": 9},
      {"x": 4, "y": 6}
    ],
    "hazards": [
      {"x": 3, "y": 2}
    ],
    "snakes": [
      {
        "id": "snake-508e96ac-94ad-11ea-bb37",
        "name": "My Snake",
        "health": 54,
        "body": [
          {"x": 5, "y": 4},
          {"x": 5, "y": 5},
          {"x": 5, "y": 6},
          {"x": 5, "y": 7},
          {"x": 5, "y": 8},
          {"x": 5, "y": 9},
          {"x": 5, "y": 10},
          # {"x": 5, "y": 7},
          # {"x": 5, "y": 8},
          # {"x": 4, "y": 9}
        ],
        "latency": "111",
        "head": {"x": 0, "y": 0},
        "length": 3,
        "shout": "why are we shouting??",
        "customizations":{
          "color":"#FF0000",
          "head":"pixel",
          "tail":"pixel"
        }
      },
      # {
      #   "id": "snake-b67f4906-94ae-11ea-bb37",
      #   "name": "Another Snake",
      #   "health": 16,
      #   "body": [
      #     {"x": 5, "y": 4},
      #     {"x": 5, "y": 3},
      #     {"x": 6, "y": 3},
      #     {"x": 6, "y": 2}
      #   ],
      #   "latency": "222",
      #   "head": {"x": 5, "y": 4},
      #   "length": 4,
      #   "shout": "I'm not really sure...",
      #   "customizations":{
      #     "color":"#26CF04",
      #     "head":"silly",
      #     "tail":"curled"
      #   }
      # }
    ]
  },
  "you": {
    "id": "snake-508e96ac-94ad-11ea-bb37",
    "name": "My Snake",
    "health": 54,
    "body": [
      {"x": 1, "y": 0},
      {"x": 1, "y": 1},
      {"x": 1, "y": 2},
      {"x": 1, "y": 3},
      {"x": 1, "y": 4},
      {"x": 2, "y": 4},
      {"x": 3, "y": 4},
      {"x": 4, "y": 4},
      {"x": 4, "y": 3},
      {"x": 4, "y": 2},
      {"x": 4, "y": 1},
      {"x": 5, "y": 1},
      {"x": 5, "y": 0},
      {"x": 6, "y": 0},
    ],
    "latency": "111",
    "head": {"x": 1, "y": 0},
    "length": 3,
    "shout": "why are we shouting??",
    "customizations": {
      "color":"#FF0000",
      "head":"pixel",
      "tail":"pixel"
    }
  }
}


from helper_battlesnake import *

my_head = {"x": 1, "y": 0}
safe_moves = obvious_moves(game, my_head)
for safe in safe_moves:
    f = flood_fill(game, look_ahead(my_head, safe))
    print(safe, f)
print("=" * 50)

food = game['board']['food']
food_dist = []
food_moves = []
# Big idea: loop through all food and find the shortest path using A* search
for food_loc in food:
    best_path, best_dist = a_star_search(game, my_head.copy(), food_loc)
    print(f"Food: {food_loc}")
    print(f"Shortest dist: {best_dist}")
    if best_path is not None:
        food_dist.append(best_dist)
        lesgo = snake_compass(my_head, best_path[-2])
        food_moves.append(lesgo)

    f = flood_fill(game, look_ahead(my_head, lesgo))
    print(f"Direction {lesgo} at {f}")
    print(best_dist * 11 * 11 / f ** 2.25)