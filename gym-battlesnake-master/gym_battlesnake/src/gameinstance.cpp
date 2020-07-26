#include <algorithm>
#include <array>
#include <chrono>
#include <cstring>
#include <random>

#include "gameinstance.h"

std::random_device rd;
std::mt19937 gen(rd());
std::uniform_real_distribution<> dis(0.0, 1.0);
unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
auto g = std::default_random_engine(seed);

unsigned next_game_id = 1000000;

GameInstance::GameInstance(unsigned board_width, unsigned board_length,
                           unsigned num_players, float food_spawn_chance)
    : board_width_(board_width), board_length_(board_length),
      num_players_(num_players), food_spawn_chance_(food_spawn_chance) {

  // Set parameters
  game_id_ = next_game_id++;
  over_ = false;
  turn_ = 0;

  // Create board
  board_.resize(board_width_ * board_length_, 0);
  players_.reserve(2 * num_players_);
  std::uniform_int_distribution<> X(0, board_width_ - 1);
  std::uniform_int_distribution<> Y(0, board_length_ - 1);

  // Get a list of spawn points
  std::array<Tile, 8> available_spawn;
  available_spawn[0] = {1u, 1u};
  available_spawn[1] = {5u, 1u};
  available_spawn[2] = {9u, 1u};
  available_spawn[3] = {1u, 5u};
  available_spawn[4] = {9u, 5u};
  available_spawn[5] = {1u, 9u};
  available_spawn[6] = {5u, 9u};
  available_spawn[7] = {9u, 9u};

  // Shuffle the items
  std::shuffle(available_spawn.begin(), available_spawn.end(), g);

  // Place players (equally around)
  std::uniform_int_distribution<> ID(1000000, 9999999);
  for (unsigned i{0}; i < num_players_; ++i) {
    unsigned id;
    do {
      id = static_cast<unsigned>(ID(gen));
    } while (players_.find(id) != players_.end());
    auto pit = players_.emplace(std::make_pair(id, id));
    auto next = available_spawn[i];
    auto x = static_cast<unsigned>(next.first);
    auto y = static_cast<unsigned>(next.second);
    at(x, y) = id;
    for (int j{0}; j < PLAYER_STARTING_LENGTH; ++j) {
      pit.first->second.body_.push_back(next);
    }
  }

  // Place food
  for (unsigned i{0}; i < num_players; ++i) {
    unsigned x, y;
    do {
      x = static_cast<unsigned>(X(gen));
      y = static_cast<unsigned>(Y(gen));
    } while (at(x, y) != 0);
    at(x, y) = FOOD_ID;
    food_.insert({x, y});
  }
}

void GameInstance::step() {

  ++turn_;
  std::unordered_set<unsigned> players_to_kill;

  std::vector<Tile> food_to_delete;

  // Move players, check for out of bounds, self collisions, and food
  for (auto &p : players_) {
    // Skip dead players
    if (!p.second.alive_)
      continue;
    // Subtract health
    --p.second.health_;
    // Next head location
    Tile curr_head = p.second.body_.front();
    char move = p.second.move_;
    Tile next_head = curr_head;
    switch (move) {
    case 'u': {
      --next_head.second;
      break;
    }
    case 'd': {
      ++next_head.second;
      break;
    }
    case 'l': {
      --next_head.first;
      break;
    }
    case 'r': {
      ++next_head.first;
      break;
    }
    }
    // Check out of bounds, then check food
    if (next_head.first < 0 || next_head.first >= board_width_ ||
        next_head.second < 0 || next_head.second >= board_length_) {
      players_to_kill.insert(p.second.id_);
      p.second.body_.pop_back();
    } else if (at(next_head) == FOOD_ID) {
      p.second.health_ = 100;
      p.second.body_.push_front(next_head);
      food_to_delete.push_back(next_head);
    } else {
      p.second.body_.pop_back();
      p.second.body_.push_front(next_head);
    }
    // Starvation
    if (p.second.health_ == 0) {
      players_to_kill.insert(p.second.id_);
      p.second.death_reason_ = DEATH_STARVE;
    }
  }

  for (auto &p : food_to_delete) {
    food_.erase(p);
  }

  // Reset board, add player bodies, map heads
  memset(&board_[0], 0, board_.size() * sizeof board_[0]);
  std::unordered_multimap<Tile, unsigned> heads;
  for (const auto &p : players_) {
    if (!p.second.alive_)
      continue;

    auto it = p.second.body_.begin();
    heads.insert({*it, p.second.id_});
    ++it;
    for (; it != p.second.body_.end(); ++it) {
      at(*it) = p.second.id_;
    }
  }

  // Check head on head collisions
  for (auto &p : players_) {
    if (!p.second.alive_)
      continue;

    for (const auto &other : players_) {
      if (!other.second.alive_)
        continue;
      if (p.second.id_ == other.second.id_)
        continue;

      auto head_1 = p.second.body_.front();
      auto head_2 = other.second.body_.front();
      if (head_1.first == head_2.first && head_1.second == head_2.second) {
        if (other.second.body_.size() >= p.second.body_.size()) {
          players_to_kill.insert(p.second.id_);
          p.second.death_reason_ = DEATH_EATEN;
        }
      }
    }
  }

  // Check for collisions with bodies
  for (auto &p : players_) {
    if (!p.second.alive_)
      continue;

    auto head = p.second.body_.front();
    if (at(head) >= 1000000) {
      players_to_kill.insert(p.second.id_);
      p.second.death_reason_ = DEATH_BODY;
    }
  }

  // Kill players
  for (auto &id : players_to_kill) {
    players_.find(id)->second.alive_ = false;
  }

  // Add new food
  std::uniform_int_distribution<> X(0, board_width_ - 1);
  std::uniform_int_distribution<> Y(0, board_length_ - 1);
  unsigned loopiter = 0;

  // GET A CHANCE TO SPAWN FOOD
  float chance = dis(gen);

  // If there are no food, set chance to 0 --> Force a food spawn
  if (food_.size() == 0) {
    chance = 0;
  }

  // If we are meant to spawn a food, then do it!
  if (chance < food_spawn_chance_) {
    unsigned x, y;
    do {
      x = static_cast<unsigned>(X(gen));
      y = static_cast<unsigned>(Y(gen));
      if (++loopiter >= 1000u)
        break;
    } while (at(x, y) != 0);
    at(x, y) = FOOD_ID;
    food_.insert({x, y});
  }

  // Reset board, set players, and food
  memset(&board_[0], 0, board_.size() * sizeof board_[0]);
  int players_alive{0};
  for (const auto &p : players_) {
    if (!p.second.alive_)
      continue;
    ++players_alive;
    for (const auto &b : p.second.body_)
      at(b) = p.second.id_;
  }

  over_ = (players_alive <= 1 && num_players_ > 1) ||
          (players_alive == 0 && num_players_ == 1);
  for (const auto &f : food_)
    at(f) = FOOD_ID;
}