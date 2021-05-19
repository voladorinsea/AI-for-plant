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
        self.w=np.mat(np.zeros([13,19]))
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
        ActionGraph=np.ones(19)
        v1 = np.asarray(self.state_valuesearch(state))
        for i in range(19):
            if actionList[i]==0:
                ActionGraph[i]=-1000
                continue
            ActionGraph[i]=v1[0][i]*actionList[i]
            
        maxindex = ActionGraph.argmax()
        print(ActionGraph)
        gen1=random.random()
        if gen1>=self.epsilon:
            return maxindex
        else:
            choose=[]
            for i in range(19):
                if actionList[i]==1:
                    choose.append(i)
            n=len(choose)
            gen2=random.randint(0,n-1)
            return choose[gen2]

    def gradient(self,state,reward,last_state,action):
        next_valueList=self.state_valuesearch(state)
        # using TD(0)
        #next_valueList[action]
        maxvalue = next_valueList.max()
        sample_value=reward+self.gama*maxvalue
        evaluate_value=self.state_valuesearch(last_state)
        maxvalue2 = evaluate_value[0,action]
        
        #last_state=np.mat(last_state).reshape(1,4)
        action=np.matrix(self.action_to_onehot(action))
        last_state=np.matrix(last_state).T
        t=last_state*action
        delta_w=self.learning_rate*(sample_value-maxvalue2)*t
        #print(delta_w)
        self.w=self.w+delta_w
        #print(self.w.T)
    

    def state_valuesearch(self,state):
        # based on best policy principle
        state=np.array(state)
        v1=np.matmul(state,self.w)
        # print(value0)
        return v1[0]
    def action_to_onehot(self,action):
        actionlist = np.zeros(19)
        actionlist[action] = 1
        return actionlist

# switch on the game
# play the game
# receive action
# return {observation,action,reward,last_observation}

class env():
    def __init__(self,cycle,value_network,delay=1):
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
        self.way=-1
        self.last_zombie=[0,0,850]
        self.zombie=[0,0,850]
        gm.set_value("exit",self.exit)


    def episode_generate(self):
        self.time=0
        self.observation=self.env.reset()#np.append(self.env.reset(),[1],axis=0) 
        self.env.render()

    def openGame(self):
        self.episode_generate()
        self.state=self.observation

    def updateState(self):
        self.Plant = gm.get_value("plant_state_all")
        self.Zombie = gm.get_value("zombie_state_all")
        self.hasZombie = gm.get_value("has_zombie")
        self.PEASHOOTERcd = gm.get_value("PEASHOOTER_COOL")
        self.SUNFLOWERcd = gm.get_value("SUNFLOWER_COOL")
        self.SunValue = gm.get_value("sun_value")


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
        if gm.get_value("State") == None:
            self.timer = Timer(self.delay, self.run,())
            self.timer.start()
            return 
        
        
        self.updateState()
        self.row =self.SelectRow()
        self.count = 1 + self.count
        
        NowState = self.StateZip()
        print(NowState)
        self.GameState = gm.get_value("State")
        if self.GameState == c.LOSE:
            reward = -1
            print("The reward is:",reward)
        elif self.GameState == c.GAMING:
            reward = 0
        elif self.GameState == c.WIN:
            reward = 1
        #elif self.zombie[2]>self.last_zombie[2] and self.way==self.row:
        #    reward = 1

        
        if reward == 1:
            print("The reward is:",reward)
       
        if self.time !=1 and self.way==self.row:
            self.value_network.gradient(NowState, reward, self.last_state,self.action)
        else:
            self.time = 2

        self.last_zombie=self.zombie    
        self.way=self.row
        while(gm.get_value("State") != c.GAMING):
            self.way=self.row
            self.row =self.SelectRow()
            self.updateState()
            NowState = self.StateZip()

        action=self.value_network.policysearch(NowState,self.SelectAction())
        print(action)
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
        #print(self.Plant)

        return self.Plant.plant_pos[row,:]

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
            if ZombieHealth==0:
                ZombiePos=850
            else:
                ZombiePos = ZombiePos/ZombieHealth
            return [ZombieHealth/100,ZombiePos/850,ZombieFrontal/850]
        else:
            ZombiePos = 850
            return [ZombieHealth/100,ZombiePos/850,ZombieFrontal/850]

    def SelectRow(self):
        maxium=0
        row=-1
        for i in range(5):
            defendnum=0
            for j in self.PlantHandle(i):
                if j==2:
                    defendnum=defendnum+1
            #print(defendnum)
            t=self.ZombieHandle(i)[0]*(1+1/(self.ZombieHandle(i)[1]))/(defendnum+0.25)*(1+1/(self.ZombieHandle(i)[2]))
            if t>maxium:
                maxium=t
                row=i
        if row==-1:
            row=random.randint(0,4)
        return row 
    def StateZip(self):
        self.zombie=self.ZombieHandle(self.row)
        IntactState =  list(self.PlantHandle(self.row))
        IntactState.extend(self.zombie)
        IntactState.append(gm.get_value("sun_value")/250)
        return IntactState

    def SelectAction(self):
        Action = np.ones(19)
        #Action = Action + 1
        self.updateState()
        if self.PEASHOOTERcd == False:
            Action[0:9] = 0
        if self.SUNFLOWERcd == False:
            Action[9:18] = 0
        if self.SunValue < 50:
            Action[0:18] = 0
        elif 50 <= self.SunValue and self.SunValue < 100:
            Action[0:9] = 0

        for i in range(9):
            if self.Plant.plant_pos[self.row,i] != 0 :
                Action[i] = 0
                Action[i+9] = 0
        
        return np.array(Action)