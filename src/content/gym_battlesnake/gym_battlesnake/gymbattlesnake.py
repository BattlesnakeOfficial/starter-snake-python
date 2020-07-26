import numpy as np
import ctypes
import pathlib
import random
from time import sleep
from gym import spaces
import torch
from stable_baselines.common.vec_env import VecEnv

def wrap_function(lib, funcname, restype, argtypes):
    """Simplify wrapping ctypes functions"""
    func = lib.__getattr__(funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func

class info(ctypes.Structure):
    _fields_ = [('health', ctypes.c_uint), ('length', ctypes.c_uint), ('turn', ctypes.c_uint), ('alive_count', ctypes.c_uint), ('death_reason', ctypes.c_uint),
        ('alive', ctypes.c_bool), ('ate', ctypes.c_bool), ('over', ctypes.c_bool)]

gamelib = None
try:
    gamelib = ctypes.cdll.LoadLibrary(str(pathlib.Path(__file__).with_name('libgymbattlesnake.so')))
except:
    gamelib = ctypes.cdll.LoadLibrary(str(pathlib.Path(__file__).with_name('libgymbattlesnake.dylib')))
env_new = wrap_function(gamelib, 'env_new', ctypes.c_void_p, [ctypes.c_uint,ctypes.c_uint,ctypes.c_uint,ctypes.c_bool, ctypes.c_bool])
env_delete = wrap_function(gamelib, 'env_delete', None, [ctypes.c_void_p])
env_reset = wrap_function(gamelib, 'env_reset', None, [ctypes.c_void_p])
env_step = wrap_function(gamelib, 'env_step', None, [ctypes.c_void_p])
env_obsptr = wrap_function(gamelib, 'env_getobspointer', ctypes.POINTER(ctypes.c_ubyte), [ctypes.c_void_p,ctypes.c_uint])
env_actptr = wrap_function(gamelib, 'env_getactpointer', ctypes.POINTER(ctypes.c_ubyte), [ctypes.c_void_p,ctypes.c_uint])
env_infoptr = wrap_function(gamelib, 'env_getinfopointer', ctypes.POINTER(info), [ctypes.c_void_p])

NUM_LAYERS = 17
LAYER_WIDTH = 23
LAYER_HEIGHT = 23

class ParallelBattlesnakeEnv(VecEnv):
    """Multi-Threaded Multi-Agent Snake Environment"""
    """ Parallel version assumes self play with same policy, so it can batch observation calculations better """
    def __init__(self, n_threads=4, n_envs=16, n_opponents=7, opponent=None, device=torch.device('cpu'), fixed_orientation=False, use_symmetry=False, dtype=torch.float32):
        # Define action and observation space
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0,high=255, shape=(NUM_LAYERS, LAYER_WIDTH, LAYER_HEIGHT), dtype=np.uint8)
        self.n_opponents = n_opponents
        self.opponent = opponent
        self.n_threads = n_threads
        self.n_envs = n_envs
        self.device = device
        self.fixed_orientation = fixed_orientation
        self.use_symmetry = use_symmetry
        if use_symmetry and not fixed_orientation:
            raise ValueError("symmetry must be used with fixed orientation")
        self.ptr = env_new(self.n_threads, self.n_envs, self.n_opponents+1, self.fixed_orientation, self.use_symmetry)
        self.dtype = dtype
        super(ParallelBattlesnakeEnv, self).__init__(self.n_envs, self.observation_space, self.action_space)
        self.reset()

    def close(self):
        env_delete(self.ptr)

    def step_async(self, actions):
        # Write player actions into buffer
        np.copyto(self.getact(0), np.asarray(actions,dtype=np.uint8))
        # Get observations for each opponent and predict actions
        all_obs = []
        for i in range(self.n_opponents):
            all_obs.append(self.getobs(i+1))
        obs = np.vstack(all_obs)
        obs = torch.tensor(obs, dtype=self.dtype).to(self.device)
        with torch.no_grad():
            acts,_ = self.opponent.predict(obs, deterministic=True)
        acts = acts.view(self.n_opponents, self.n_envs).cpu().detach().numpy().astype(np.uint8)
        for i in range(self.n_opponents):
            np.copyto(self.getact(i+1), acts[i].flatten())
            
        # Step game
        env_step(self.ptr)

    def step_wait(self):

        info = [{} for _ in range(self.n_envs)]
        dones = np.asarray([ False for _ in range(self.n_envs) ])
        rews = np.zeros((self.n_envs))

        infoptr = env_infoptr(self.ptr)
        for i in range(self.n_envs):
            if infoptr[i].over:
                dones[i] = True
                info[i]['episode'] = {}
                if infoptr[i].alive:
                    rews[i] += 1.0
                    info[i]['episode']['r'] = rews[i]
                else:
                    rews[i] -= 1.0
                    info[i]['episode']['r'] = rews[i]
                info[i]['episode']['l'] = infoptr[i].turn

        return self.getobs(0), rews, dones, info

    def reset(self):
        env_reset(self.ptr)
        return self.getobs(0)


    def getobs(self, agent_i):
        obsptr = env_obsptr(self.ptr, agent_i)
        return np.ctypeslib.as_array(obsptr, shape=(self.n_envs, NUM_LAYERS, LAYER_WIDTH, LAYER_HEIGHT))

    def getact(self, agent_i):
        actptr = env_actptr(self.ptr, agent_i)
        return np.ctypeslib.as_array(actptr, shape=(self.n_envs,))

    def get_attr(self, attr_name, indices=None):
        pass

    def set_attr(self, attr_name, value, indices=None):
        pass

    def env_method(self,
                   method_name,
                   *method_args,
                   indices=None,
                   **method_kwargs):
        pass

    def seed(self, seed=None):
        pass

class BattlesnakeEnv(VecEnv):
    """Multi-Threaded Multi-Agent Snake Environment"""
    def __init__(self, n_threads=4, n_envs=16, opponents=[], device=torch.device('cpu'), fixed_orientation=False, use_symmetry=False):
        # Define action and observation space
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0,high=255, shape=(NUM_LAYERS, LAYER_WIDTH, LAYER_HEIGHT), dtype=np.uint8)
        self.n_opponents = len(opponents)
        self.opponents = opponents
        self.n_threads = n_threads
        self.n_envs = n_envs
        self.device = device
        self.fixed_orientation = fixed_orientation
        self.use_symmetry = use_symmetry
        if use_symmetry and not fixed_orientation:
            raise ValueError("symmetry must be used with fixed orientation")
        self.ptr = env_new(self.n_threads, self.n_envs, self.n_opponents+1, self.fixed_orientation, self.use_symmetry)
        super(BattlesnakeEnv, self).__init__(self.n_envs, self.observation_space, self.action_space)
        self.reset()

    def close(self):
        env_delete(self.ptr)

    def step_async(self, actions):
        # Write player actions into buffer
        np.copyto(self.getact(0), np.asarray(actions,dtype=np.uint8))
        # Get observations for each opponent and predict actions
        with torch.no_grad():
            for i in range(1,self.n_opponents+1):
                obss = torch.tensor(self.getobs(i), dtype=torch.float32).to(self.device)
                acts,_ = self.opponents[i-1].predict(obss, deterministic=True)
                np.copyto(self.getact(i), acts.detach().cpu().numpy().flatten().astype(np.uint8))
        # Step game
        env_step(self.ptr)

    def step_wait(self):

        info = [{} for _ in range(self.n_envs)]
        dones = np.asarray([ False for _ in range(self.n_envs) ])
        rews = np.zeros((self.n_envs))

        infoptr = env_infoptr(self.ptr)
        for i in range(self.n_envs):
            if infoptr[i].over:
                dones[i] = True
                info[i]['episode'] = {}
                if infoptr[i].alive:
                    rews[i] += 1.0
                    info[i]['episode']['r'] = rews[i]
                else:
                    rews[i] -= 1.0
                    info[i]['episode']['r'] = rews[i]
                info[i]['episode']['l'] = infoptr[i].turn

        return self.getobs(0), rews, dones, info

    def reset(self):
        env_reset(self.ptr)
        return self.getobs(0)


    def getobs(self, agent_i):
        obsptr = env_obsptr(self.ptr, agent_i)
        return np.ctypeslib.as_array(obsptr, shape=(self.n_envs, NUM_LAYERS, LAYER_WIDTH, LAYER_HEIGHT))

    def getact(self, agent_i):
        actptr = env_actptr(self.ptr, agent_i)
        return np.ctypeslib.as_array(actptr, shape=(self.n_envs,))

    def get_attr(self, attr_name, indices=None):
        pass

    def set_attr(self, attr_name, value, indices=None):
        pass

    def env_method(self,
                   method_name,
                   *method_args,
                   indices=None,
                   **method_kwargs):
        pass

    def seed(self, seed=None):
        pass