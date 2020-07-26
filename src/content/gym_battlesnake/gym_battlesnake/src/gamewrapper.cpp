#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <memory>
#include <random>
#include <utility>
#include <vector>

#include "gameinstance.h"
#include "threadpool.h"

#define NUM_LAYERS 17 // 7 layers indicating the number of alive opponents
#define LAYER_WIDTH 23
#define LAYER_HEIGHT 23
#define OBS_SIZE NUM_LAYERS *LAYER_WIDTH *LAYER_HEIGHT

struct info {
  unsigned health_;
  unsigned length_;
  unsigned turn_;
  unsigned alive_count_;
  unsigned death_reason_;
  bool alive_;
  bool ate_;
  bool over_;
};

class GameWrapper {

  /* Randomly* orient the board by flipping in x and y */
  unsigned orientation(unsigned game_id, unsigned turn, unsigned player_id, bool fixed) {
    if (fixed) {
      return 0u;
    }

    return std::hash<unsigned>{}(game_id) ^ player_id ^
           std::hash<unsigned>{}(turn);
  }

  char getaction(unsigned model_i, unsigned env_i, unsigned ori, unsigned player_id, State gamestate) {
    const char moves[4] = {'u', 'd', 'l', 'r'};
    auto index = acts_[model_i * n_envs_ + env_i];
    char action = moves[index];
    auto &players = std::get<1>(gamestate);
    Tile head, neck;
    const auto it = players.find(player_id);
    if (it != players.end()) {
      head = it->second.body_.front();
      neck = *std::next(it->second.body_.begin(), 1);
    } else {
      std::abort();
    }
    auto flip_y = false;
    auto transpose = false;
    auto transpose_rotate = false;
    int diff_x = head.first - neck.first;
    int diff_y = head.second - neck.second;

    // We'll rotate the inputs such that all snakes face up
    if (use_symmetry_) {
      // Disable orientation rotations
      // YOU CAN ONLY DO THIS IF THE GAME BOARD IS SQUARE
      if (diff_x == 0) {
        // Check if head is above neck
        if (diff_y == 1) {
          flip_y = true;
        }
      } else {
        // We're going to need a transpose here
        if (diff_x == 1) {
          // head is on the right
          transpose_rotate = true;
        }
        if (diff_x == -1) {
          transpose = true;
        }
      }
    }

    if (use_symmetry_) {
      if (transpose) {
        switch (action) {
          case 'l':
            return 'u';
          case 'r':
            return 'd'; // this is the bad move
          case 'u':
            return 'l';
          case 'd':
            return 'r';
        }
      }
      if (transpose_rotate) {
        switch (action) {
          case 'l':
            return 'u';
          case 'r':
            return 'd'; // this is the bad move
          case 'u':
            return 'r';
          case 'd':
            return 'l';
        }
      }
      if (flip_y) {
        switch (action) {
          case 'l':
            return 'l';
          case 'r':
            return 'r';
          case 'u':
            return 'd'; // this is the bad move
          case 'd':
            return 'u';
        }
      }
    }

    if (!use_symmetry_) {
      if ((ori & 1) && (action == 'l' || action == 'r'))
        action = action == 'l' ? 'r' : 'l';
      if ((ori & 2) && (action == 'u' || action == 'd'))
        action = action == 'd' ? 'u' : 'd';
    }
    return action;
  }

  void writeobs(unsigned model_i, unsigned env_i, unsigned player_id,
                State gamestate, unsigned ori) {
    /*
        layer0: snake health on heads {0,...,100}
        layer1: snake bodies {0,1}
        layer2: segment numbers {0,...,255}
        layer3: snake length >= player {0,1}
        layer4: food {0,1}
        layer5: gameboard {0,1}
        layer6: head_mask {0,1}
        layer7: double_tail_mask {0,1}
        layer8: snake bodies >= us {0,1}
        layer9: snake bodies < us {0,1}
        layer10-16: Alive count
    */
    auto &players = std::get<1>(gamestate);
    Tile head, neck;
    const auto it = players.find(player_id);
    if (it != players.end()) {
      head = it->second.body_.front();
      neck = *std::next(it->second.body_.begin(), 1);
    } else {
      std::abort();
    }

    auto flip_y = false;
    auto transpose = false;
    auto transpose_rotate = false;
    int diff_x = head.first - neck.first;
    int diff_y = head.second - neck.second;

    // We'll rotate the inputs such that all snakes face up
    if (use_symmetry_) {
      // Disable orientation rotations
      ori = 0;
      // YOU CAN ONLY DO THIS IF THE GAME BOARD IS SQUARE
      if (diff_x == 0) {
        // Check if head is above neck
        if (diff_y == 1) {
          flip_y = true;
        }
      } else {
        // We're going to need a transpose here
        if (diff_x == 1) {
          // head is on the right
          transpose_rotate = true;
        }
        if (diff_x == -1) {
          transpose = true;
        }
      }
    }

    auto get_x = [this, head, flip_y, transpose, transpose_rotate, ori](const Tile &xy) {
      int x = (int(xy.first) - int(head.first)) * ((ori & 1) ? -1 : 1); 
      int y = (int(xy.second) - int(head.second))* ((ori & 2) ? -1 : 1); 
      x += (LAYER_WIDTH / 2);
      y += (LAYER_HEIGHT / 2);

      if (transpose) {
        return y;
      }
      if (transpose_rotate) {
        return y;
      }
      // Default case, return x
      return x;
    };

    auto get_y = [this, head, transpose, transpose_rotate, flip_y, ori](const Tile &xy) {
      int x = (int(xy.first) - int(head.first)) * ((ori & 1) ? -1 : 1);
      int y = (int(xy.second) - int(head.second)) * ((ori & 2) ? -1 : 1);
      x += (LAYER_WIDTH / 2);
      y += (LAYER_HEIGHT / 2);

      if (transpose) {
        return x;
      }
      if (transpose_rotate) {
        return LAYER_WIDTH - x - 1;
      }
      if (flip_y) {
        return LAYER_HEIGHT - y - 1;
      }

      // Default case, return y
      return y;
    };

    auto assign = [this, model_i, env_i, head, ori, get_x, get_y](const Tile &xy, unsigned l,
                                                    uint8_t val) {
      int x = get_x(xy);
      int y = get_y(xy);
      
      if (x >= 0 && x < LAYER_WIDTH && y >= 0 && y < LAYER_HEIGHT)
        obss_[ model_i*(n_envs_*OBS_SIZE) + env_i*OBS_SIZE + l*(LAYER_HEIGHT*LAYER_WIDTH) + x*LAYER_HEIGHT + y] += val;
    };

    unsigned playersize = it->second.body_.size();
    // Assign head_mask
    assign(it->second.body_.front(), 6, 1);

    auto alive_count = 0;
    for (const auto &p : players) {
      if (!p.second.alive_)
        continue;
      alive_count++;
      // Assign health on head
      assign(p.second.body_.front(), 0, p.second.health_);
      unsigned i = 0;
      Tile tail_1, tail_2;
      for (auto cit = p.second.body_.crbegin(); cit != p.second.body_.crend();
           ++cit) {
        if (i == 0) {
          tail_1 = *cit;
        }
        if (i == 1) {
          tail_2 = *cit;

          // Check if the tails are the same
          if (tail_1.first == tail_2.first && tail_1.second == tail_2.second) {
            // Double tail
            assign(*cit, 7, 1);
          }
        }
        assign(*cit, 1, 1);
        assign(*cit, 2, std::min(++i, static_cast<unsigned>(255)));
        if (p.second.id_ != player_id) {
          if (p.second.body_.size() >= playersize) {
            assign(*cit, 8, 1 + p.second.body_.size() - playersize); // Store the difference
          }
          if (p.second.body_.size() < playersize) {
            assign(*cit, 9, -p.second.body_.size() + playersize); // Store the difference
          }
        }
      }
      if (p.second.id_ != player_id)
        assign(p.second.body_.front(), 3,
               p.second.body_.size() >= playersize ? 1 : 0);
    }

    // Subtract 1 from alive_count to get the layer index
    alive_count -= 2;

    auto &food = std::get<2>(gamestate);
    for (const auto &xy : food)
      assign(xy, 4, 1);

    for (int x = 0; x < static_cast<int>(std::get<3>(gamestate)); ++x) {
      for (int y = 0; y < static_cast<int>(std::get<4>(gamestate)); ++y) {
        assign({x, y}, 5, 1);
        // Signal how many players are alive
        assign({x, y}, 10 + alive_count, 1);
      }
    }
  }

public:
  GameWrapper(unsigned n_threads, unsigned n_envs, unsigned n_models, bool fixed_orientation, bool use_symmetry)
      : n_threads_(n_threads), n_envs_(n_envs), n_models_(n_models),
        threadpool_(n_threads) {
    // 1. Create envs
    envs_.resize(n_envs, nullptr);
    // 2. Allocate obs and act arrays
    obss_.resize(n_models * n_envs * OBS_SIZE);
    acts_.resize(n_models * n_envs);
    info_.resize(n_envs);
    fixed_orientation_ = fixed_orientation;
    use_symmetry_ = use_symmetry;
    // 3. Reset envs
    reset();
  }

  ~GameWrapper() = default;

  void reset() {
    // Clear obs arrays
    memset(&obss_[0], 0, obss_.size() * sizeof obss_[0]);
    // Reset all envs
    for (unsigned ii{0}; ii < n_envs_; ++ii) {
      threadpool_.schedule([this, ii]() {
        auto &gi = envs_[ii];
        gi.reset();
        // Create new game instance
        // unsigned bwidth = (std::rand() % (1+19-7)) + 7;
        // unsigned bheight = (std::rand() % (1+19-7)) + 7;
        unsigned bwidth = 11;
        unsigned bheight = 11;
        float food_spawn_chance = 0.15;
        gi = std::make_shared<GameInstance>(bwidth, bheight, n_models_,
                                            food_spawn_chance);
        // Write states into observation arrays
        auto ids = gi->getplayerids();
        auto state = gi->getstate();
        for (unsigned m{0}; m < n_models_; ++m) {
          writeobs(m, ii, ids[m], state,
                   orientation(gi->gameid(), gi->turn(), ids[m], fixed_orientation_));
        }
        info_[ii].health_ = 100;
        info_[ii].length_ = PLAYER_STARTING_LENGTH;
        info_[ii].turn_ = 0;
        info_[ii].alive_ = true;
        info_[ii].ate_ = false;
        info_[ii].over_ = false;
        info_[ii].alive_count_ = n_models_;
        info_[ii].death_reason_ = DEATH_NONE;
      });
    }
    threadpool_.wait();
  }

  void step() {
    // Clear obs arrays
    memset(&obss_[0], 0, obss_.size() * sizeof obss_[0]);
    // Step all envs
    for (unsigned ii{0}; ii < n_envs_; ++ii) {
      threadpool_.schedule([this, ii]() {

        auto &gi = envs_[ii];
        // Read actions into gameinstance
        auto ids = gi->getplayerids();
        for (unsigned m{0}; m < n_models_; ++m) {
          gi->setplayermove(
              ids[m],
              getaction(m, ii, orientation(gi->gameid(), gi->turn(), ids[m], fixed_orientation_), ids[m], gi->getstate()));
        }

        // Get player length before step
        auto player_id = ids[0];
        auto it = std::get<1>(gi->getstate()).find(player_id);

        // Step game
        gi->step();

        // Figure out if done
        it = std::get<1>(gi->getstate()).find(player_id);
        bool done = !(it->second.alive_) || gi->over();

        // Count how many players are alive
        unsigned count = 0;
        for (auto i = 0; i < ids.size(); i++) {
          auto id = ids[i];
          auto it = std::get<1>(gi->getstate()).find(id);

          // Count number of alive snakes
          if (it->second.alive_) {
            count++;
          }
        }

        // Write info
        info_[ii].health_ = it->second.health_;
        info_[ii].length_ = it->second.body_.size();
        info_[ii].turn_ = gi->turn();
        info_[ii].alive_ = it->second.alive_;
        info_[ii].ate_ = it->second.health_ == 100 && gi->turn() > 0;
        info_[ii].over_ = done;
        info_[ii].alive_count_ = count;
        info_[ii].death_reason_ = it->second.death_reason_;

        // Reset game if over
        if (done) {
          gi.reset();
          // Create new game instance
          // unsigned bwidth = (std::rand() % (1+19-7)) + 7;
          // unsigned bheight = (std::rand() % (1+19-7)) + 7;
          unsigned bwidth = 11;
          unsigned bheight = 11;
          float food_spawn_chance = 0.15;
          gi = std::make_shared<GameInstance>(bwidth, bheight, n_models_,
                                              food_spawn_chance);
          ids = gi->getplayerids();
        }
        // Write states into observation arrays
        for (unsigned m{0}; m < n_models_; ++m) {
          writeobs(m, ii, ids[m], gi->getstate(),
                   orientation(gi->gameid(), gi->turn(), ids[m], fixed_orientation_));
        }
      });
    }
    threadpool_.wait();
  }

  unsigned n_threads_, n_envs_, n_models_;
  ThreadPool threadpool_;
  bool fixed_orientation_, use_symmetry_;
  std::vector<std::shared_ptr<GameInstance>> envs_;
  std::vector<uint8_t> obss_;
  std::vector<uint8_t> acts_;
  std::vector<info> info_;
};

extern "C" {
GameWrapper *env_new(unsigned n_threads, unsigned n_envs, unsigned n_models, bool fixed_orientation, bool use_symmetry) {
  return new GameWrapper(n_threads, n_envs, n_models, fixed_orientation, use_symmetry);
}
void env_delete(GameWrapper *p) { delete p; }
void env_reset(GameWrapper *p) { p->reset(); }
void env_step(GameWrapper *p) { p->step(); }
uint8_t *env_getobspointer(GameWrapper *p, unsigned model_i) {
  return &p->obss_[model_i * (p->n_envs_ * OBS_SIZE)];
}
uint8_t *env_getactpointer(GameWrapper *p, unsigned model_i) {
  return &p->acts_[model_i * p->n_envs_];
}
info *env_getinfopointer(GameWrapper *p) { return &p->info_[0]; }
}