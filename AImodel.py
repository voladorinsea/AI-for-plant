from source.constants import SUNFLOWER
import numpy as np
import time
from threading import Timer,activeCount
import source.GlobalManager as gm
from . import constants as c
import random
# training a value network
# based on TD(0) algorithm
# receive {observation,action,reward,last_observation}
# return Q(s,a)
class value_network():
    def __init__(self,learning_rate,gama,epsilon):
        self.learning_rate=learning_rate
        self.w=np.zeros([13,19])
        self.gama=gama
        self.epsilon=epsilon
        self.PEASHOOTERcd = gm.get_value("PEASHOOTER_COOL")
        self.SUNFLOWERcd = gm.get_value("SUNFLOWER_COOL")
        self.SunValue = gm.get_value("sun_value")
        '''
        self.Pidout=PID.PIDcontrol(0.3,1000,5,0,0)
        self.Pidin=PID.PIDcontrol(0.5,1000,0,50,0)
        '''
    def policysearch(self,state,actionList):
        # PID for a test
        '''
        out1=self.Pidout.control(state[1])
        self.Pidin.modify(out1)
        out2=self.Pidin.control(state[3])
        action = 1 if out2<=50 else 0
        '''
        # based on epsilon-greedy policy
        v1 = self.state_valuesearch(state)
        ActionGraph = v1*actionList
        maxindex = ActionGraph.argmax()

        gen1=random.random()
        if gen1>=self.epsilon:
            return maxindex
        else:
            gen2=random.randint(0,18)
            return gen2

    def gradient(self,state,reward,last_state,action):
        next_valueList=self.state_valuesearch(state)
        # using TD(0)
        #next_valueList[action]
        maxvalue = next_valueList.max()
        sample_value=reward+self.gama*maxvalue
        evaluate_value=self.state_valuesearch(last_state)
        maxvalue2 = evaluate_value[action]
        
        #last_state=np.mat(last_state).reshape(1,4)
        action=np.mat(self.action_to_onehot(action)).reshape(1,19)

        t=np.mat(last_state).reshape(1,13).T*action
        delta_w=self.learning_rate*(sample_value-maxvalue2)*t
        #print(delta_w)
        self.w=self.w+delta_w
        #print(self.w.T)
    

    def state_valuesearch(self,state):
        # based on best policy principle
        state=np.array(state)
        v1=np.matmul(state,self.w)
        # print(value0)
        return v1
    def action_to_onehot(self,action):
        actionlist = np.zeros(19)
        actionlist[action] = 1
        return actionlist

# switch on the game
# play the game
# receive action
# return {observation,action,reward,last_observation}

class env():
    def __init__(self,cycle,value_network,delay=2):
        self.time=1
        #self.end=end
        #elf.env=gym.make('CartPole-v0')
        self.cycle = cycle
        self.value_network = value_network
        self.delay = delay
        self.Plant = gm.get_value("plant_state_all")
        self.Zombie = gm.get_value("zombie_state_all")
        self.hasZombie = gm.get_value("has_zombie")
        self.PEASHOOTERcd = gm.get_value("PEASHOOTER_COOL")
        self.SUNFLOWERcd = gm.get_value("SUNFLOWER_COOL")
        self.SunValue = gm.get_value("sun_value")
        self.count = 0
        self.exit = 1
        gm.set_value("exit",self.exit)

    def episode_generate(self):
        self.time=0
        self.observation=self.env.reset()#np.append(self.env.reset(),[1],axis=0) 
        self.env.render()

    def openGame(self):
        self.episode_generate()
        self.state=self.observation

        
    


    def training(self):
        cycle=0
        while(cycle!=self.cycle):
            self.check=0
            self.openGame()
            self.run()
            # accelerate the train process
            self.value_network.epsilon-=0.002
            if self.value_network.epsilon<=0.1:
                self.value_network.epsilo=0.05
            #for i in range(self.aimstep):
            

            if self.check==1:
                self.score.extend([i+1])
                print("Episode finished after {} timesteps".format(i + 1))
                self.timer.cancel()
                    #break
            cycle=cycle+1
        print("training finished!!!")

    def run(self):
        #action = self.agent.execute()
        self.count = 1 + self.count
        self.row =self.SelectRow()
        NowState = self.StateZip()
        self.GameState = gm.get_value("State")
        if self.GameState == c.LOSE:
            reward = -1
        elif self.GameState == c.GAMING:
            reward = 0
        elif self.GameState == c.WIN:
            reward = 1

        if self.time !=1:
            self.value_network.gradient(NowState, reward, self.last_state,self.action)
        else:
            self.time = 2
        action=self.value_network.policysearch(NowState,self.SelectAction())

        if action <9 and action >=0:
            #2是豌豆
            x = action
            y = self.row
            species = 2
        elif action >=9 and action <=17:
            #1是向日葵
            x = action-9
            y = self.row
            species = 1
        else:
            x = -1
            y = -1
            species = 0
        GetState = gm.get_value("ALLSTATE")
        if species == 1:
            GetState.my_addPlant(x,y,c.SUNFLOWER)
        elif species == 2:
            GetState.my_addPlant(x,y,c.PEASHOOTER)
        #self.state, reward, self.check, self.last_state=self.episode_action(action)
        self.last_state = NowState
        self.action = action
        self.timer = Timer(self.delay, self.run,())
        self.timer.start()


        if self.count == self.cycle:
            self.exit = 0

    def cancel(self):
        self.timer.cancel()

    def PlantHandle(self,row):
        #gm.set_value("plant_state_all",self.plant_state_all)
        return self.Plant[row,:]

    def ZombieHandle(self,row):
        ZombieHealth = 0
        ZombiePos = 0
        ZombieFrontal = 850
        if self.hasZombie:
            for each in self.Zombie:
                if each.y == row:
                    ZombieHealth = ZombieHealth + each.health
                    ZombiePos = each.health*each.x+ZombiePos
                    if ZombieFrontal > each.x:
                        ZombieFrontal = each.x
            ZombiePos = ZombiePos/ZombieHealth
            return [ZombieHealth,ZombiePos,ZombieFrontal]
        else:
            ZombiePos = 850
            return [ZombieHealth,ZombiePos,ZombieFrontal]

    def SelectRow(self):
        row = 1
        return row 
    def StateZip(self):

        IntactState =  self.PlantHandle(self.row)
        IntactState.extend(self.ZombieHandle(self.row))
        IntactState.append(gm.get_value("sun_value"))
        return IntactState

    def SelectAction(self):
        Action = np.ones(19)
        #Action = Action + 1
        if self.PEASHOOTERcd == False:
            Action[0:9] = 0
        if self.SUNFLOWERcd == False:
            Action[9:19] = 0
        if self.SunValue < 50:
            Action[0:19] = 0
        elif 50 < self.SunValue and self.SunValue < 100:
            Action[0:9] = 0

        for i in range(9):
            if self.Plant[self.row,i] != 0 :
                Action[i] = 0
                Action[i+9] = 0
        
        return np.array(Action)