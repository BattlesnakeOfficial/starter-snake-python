from gym_battlesnake.gymbattlesnake import BattlesnakeEnv
from gym_battlesnake.custompolicy import CustomPolicy
from stable_baselines import PPO2

num_agents = 4
# placeholder_env necessary for model to recognize,
# the observation and action space, and the vectorized environment
placeholder_env = BattlesnakeEnv(n_threads=4, n_envs=16)
models = [PPO2(CustomPolicy, placeholder_env, verbose=1, learning_rate=1e-3) for _ in range(num_agents)]
# Close environment to free allocated resources
placeholder_env.close()

for _ in range(10):
    for model in models:
        env = BattlesnakeEnv(n_threads=4, n_envs=16, opponents=[ m for m in models if m is not model])
        model.set_env(env)
        model.learn(total_timesteps=100000)
        env.close()

model = models[0]
env = BattlesnakeEnv(n_threads=1, n_envs=1, opponents=[ m for m in models if m is not model])
obs = env.reset()
for _ in range(10000):
    action,_ = model.predict(obs)
    obs,_,_,_ = env.step(action)
    env.render()