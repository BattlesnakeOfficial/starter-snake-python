#ifndef GAME_INSTANCE_H
#define GAME_INSTANCE_H

#include <vector>
#include <list>
#include <tuple>
#include <utility>
#include <unordered_set>
#include <unordered_map>

#define PLAYER_STARTING_LENGTH 3
#define FOOD_ID 1

#define DEATH_NONE 0u
#define DEATH_EATEN 1u
#define DEATH_STARVE 2u
#define DEATH_BODY 2u // This is the worst -- wall collision

using Tile = std::pair<unsigned, unsigned>;
using Position = std::pair<int, int>;
using Node = std::pair<Position, int>;
namespace std {
	template<>
	struct hash<Tile> {
		size_t operator()(const Tile& a) const {
			return hash<unsigned>()(a.first) ^ hash<unsigned>()(a.second);
		}
	};
}

struct Player {
	Player(unsigned id) : id_(id), alive_(true), health_(100), move_('u'), turn_(0) {}
	unsigned id_;
	bool alive_;
	unsigned health_;
	char move_;
	unsigned turn_;
	unsigned death_reason_;
	std::list<Tile> body_;
	bool operator==(const Player& a) const { return id_ == a.id_; }
};

/* board, players, food, width, height */
using State = std::tuple<const std::vector<unsigned>&, const std::unordered_map<unsigned, Player>&, const std::unordered_set<Tile>&, unsigned, unsigned>;
/* width, height, num players, num food */
using Parameters = std::tuple<unsigned, unsigned, unsigned, float>;

class GameInstance {
public:
	GameInstance(unsigned board_width, unsigned board_length, unsigned num_players, float food_spawn_chance);

	GameInstance(const GameInstance&) = delete;
	GameInstance(GameInstance&&) = delete;
	GameInstance& operator=(const GameInstance&) = delete;
	GameInstance& operator=(GameInstance&&) = delete;

	~GameInstance() = default;

	void step();

	State getstate() const {
		return std::tie(board_, players_, food_, board_width_, board_length_);
	}

	Parameters getparameters() const {
		return std::make_tuple(board_width_, board_length_, num_players_, food_spawn_chance_);
	}

	bool setplayermove(unsigned id, char m) {
		auto it = players_.find(id);
		if(it == players_.end()) {
			return false;
		} else {
			it->second.move_ = m;
			return true;
		}
	}

	bool over() const { return over_; }

	unsigned turn() const { return turn_; }

	unsigned gameid() const { return game_id_; }

	unsigned tileid(unsigned i, unsigned j) { return board_.at(i*board_length_ + j); }

	unsigned tileid(const Tile& t) { return board_.at(t.first*board_length_ + t.second); }

	std::vector<unsigned> getplayerids() const {
		std::vector<unsigned> playerids;
		playerids.reserve(players_.size());
		for(const auto& p : players_) playerids.push_back(p.first);
		return playerids;
	}

	unsigned getplayerid(unsigned num = 0) const {
		unsigned i {0};
		for(const auto& p : players_) {
			if(i == num) return p.first;
			++i;
		}
		return 0;
	}

private:
	// Helper functions
	unsigned& at(unsigned i, unsigned j) { return board_.at(i*board_length_ + j); }
	unsigned& at(const Tile& t) { return board_.at(t.first*board_length_ + t.second); }

	// Game parameters
	unsigned board_width_;
	unsigned board_length_;
	unsigned num_players_;
	float food_spawn_chance_;

	// State parameters
	bool over_;
	unsigned turn_;
	unsigned game_id_;

	// Game data
	std::vector<unsigned> board_;
	std::unordered_map<unsigned, Player> players_;
	std::unordered_set<Tile> food_;
};

#endif