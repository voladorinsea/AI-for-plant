import tensorflow as tf
import numpy as np
import time
from threading import Timer,activeCount
# training a value network
# based on TD(0) algorithm
# receive {observation,action,reward,last_observation}
# return Q(s,a)
class value_network():
    def __init__(self):
        self.zero=0

# switch on the game
# play the game
# receive action
# return {observation,action,reward,last_observation}
class env():
    def __init__(self):
        1
    def begin(self):
        1
    def control(self, action):
        1
    def step(self):
        return observation,action,reward,last_observation
# find action executable
# evaluate the best action based value_network
# receive state
# return action
class agent():
    def __init__(self,delay):
        self.delay=delay
    def AIsetting(self):
        1
    def AI(self):
        print("Hello!!!")
    def run(self):
        self.AI()
        self.timer = Timer(self.delay, self.run,())
        self.timer.start()

def RLplanning(env,value_network,agent):
    1