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
        self.w=np.mat(np.zeros([30,21]))
        self.gama=gama
        self.epsilon=epsilon
        self.PEASHOOTERcd = gm.get_value("PEASHOOTER_COOL")
        self.SUNFLOWERcd = gm.get_value("SUNFLOWER_COOL")
        self.SunValue = gm.get_value("sun_value")
        self.count = 0
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
        ActionGraph=np.ones(21)
        v1 = np.asarray(self.state_valuesearch(state)[0])
        for i in range(21):
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
            for i in range(21):
                if actionList[i]==1:
                    choose.append(i)
            n=len(choose)
            gen2=random.randint(0,n-1)
            return choose[gen2]
            


    def gradient(self,state,reward,last_state,action):
        next_valueList=self.state_valuesearch(state)
        # using TD(0)
        #next_valueList[action]
        maxvalue = next_valueList[0].max()
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
        print(self.w.T)
        self.count += 1

        self.epsilon -= 0.01
        if self.epsilon<=0.05:
            self.epsilon = 0.05
        self.learning_rate -= 0.001
        if self.learning_rate<=0.005:
            self.learning_rate = 0.005
    def state_valuesearch(self,state):
        # based on best policy principle
        state=np.array(state)
        v1=np.matmul(state,self.w)
        # print(value0)
        return v1[0]
    def action_to_onehot(self,action):
        actionlist = np.zeros(21)
        actionlist[action] = 1
        return actionlist

# switch on the game
# play the game
# receive action
# return {observation,action,reward,last_observation}

class env():
    def __init__(self,cycle,value_network,delay=0.4):
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
        self.GameState = gm.get_value("State")
    def run(self):
        #action = self.agent.execute()
        if gm.get_value("State") == None:
            self.timer = Timer(self.delay, self.run,())
            self.timer.start()
            return 
        
        self.updateState()
        if self.SunValue <50:
            1
        else:

            if self.time !=1:
                self.lastrow_newState = self.StateZip(self.lastrow)
                self.NowZomH = self.ZombieHealth(self.lastrow)
                reward =self.Getreward(self.tmp,self.lastrow_state,self.lastrow_newState,self.lastrow_action,self.LastZomH,self.NowZomH)
                self.value_network.gradient(self.lastrow_newState, reward, self.lastrow_state,self.lastrow_action)
                
                

                if self.GameState == c.GAMING:
                    self.row =self.SelectRow()
                    self.NewState=self.StateZip(self.row)
                    self.NowZomH = self.ZombieHealth(self.row)
                    self.action=self.value_network.policysearch(self.NewState,self.SelectAction())
                    self.action,self.tmp = self.actionlim(self.action)

                    self.actionexe(self.action,self.row)


                    
                    self.LastZomH = self.NowZomH
                    self.lastrow = self.row
                    self.lastrow_state = self.NewState
                    self.lastrow_action = self.action

                else:
                    self.time = 1
                    while self.GameState != c.GAMING:
                        self.GameState = gm.get_value("State")
                        1
            else:
                self.row =self.SelectRow()
                self.NewState=self.StateZip(self.row)
                self.action=self.value_network.policysearch(self.NewState,self.SelectAction())
                self.action,self.tmp = self.actionlim(self.action)
                self.actionexe(self.action,self.row)
                #僵尸血量
                self.NowZomH = self.ZombieHealth(self.row)



                self.lastrow = self.row
                self.lastrow_action = self.action
                self.lastrow_state = self.NewState
                self.LastZomH = self.NowZomH
                self.time = 2

        self.timer = Timer(self.delay, self.run,())
        self.timer.start()
       

    def actionexe(self,action,row):
        if action <9 and action >=0:
            #1是向日葵
            x = action
            y = row
            species = 1
        elif action >=9 and action <=17:
            #2是豌豆
            x = action-9
            y = row
            species = 2
        else:
            x = -1
            y = -1
            species = 0
        GetState = gm.get_value("ALLSTATE")
        if species == 1:
            GetState.my_addPlant(x,y,c.SUNFLOWER)
        elif species == 2:
            GetState.my_addPlant(x,y,c.PEASHOOTER)

    def Getreward(self,tmp,laststate,nowstate,action,LastZomH,NowZomH):

        reward = 0
        lastnum = self.PlantNum(laststate)
        nownum = self.PlantNum(nowstate)
        lastFront = self.ZombieFront(laststate)
        nowFront = self.ZombieFront(nowstate)
        NewPlantPos = self.ActionPos(action)*9/8.0
        if tmp == 1:
            reward += 0.01
        if self.GameState == c.LOSE:
            reward -= 1
        elif self.GameState == c.WIN:
            reward += 1
        else:
            if lastnum>nownum:
                reward -= 0.02
            if lastFront < nowFront:
                reward += 0.01
            if NewPlantPos + 9/8.0 >= lastFront:
                reward -= 0.01
            if LastZomH > NowZomH:
                reward += 0.01
        return reward

    def actionlim(self,action):
        #self.SunValue
        #false 正在冷却
        #self.PEASHOOTERcd
        #self.SUNFLOWERcd
        reward = 0
        if self.SunValue <100 and self.SunValue >= 50:
            if action <=8 and self.SUNFLOWERcd == False:
                action = 19
                reward = 1
            elif action<=17 and action>=9: 
                action =18
                reward = 1
        elif self.SunValue >=100:
            if action <=8 and self.SUNFLOWERcd == False:
                action = 19
                reward = 1
            elif action<=17 and action>=9 and self.PEASHOOTERcd == False: 
                action =20
                reward = 1
        return action,reward
            
    def cancel(self):
        self.timer.cancel()
    
    def PlantHandle1(self,row):
        #gm.set_value("plant_state_all",self.plant_state_all)
        #print(self.Plant)

        return self.Plant.plant_pos[row,:]
    
    def PlantHandle(self,row):
        #0-8 向日葵   9-17是豌豆
        newlist = [0] * 18
        for i in range(len(self.Plant.plant_pos[row,:])):
            if  self.Plant.plant_pos[row,i] == 1:
                newlist[i] = 1
            elif  self.Plant.plant_pos[row,i] == 2:
                newlist[i+9] = 1
        return newlist

    def PlantNum(self,state):
        count = 0
        for i in range(18):
            if state[i]==1:
                count += 1
        
        return count

    def ActionPos(self,action):
        if action <9 and action >=0:
            #1是向日葵
            x = action
        
        elif action >=9 and action <=17:
            #2是豌豆
            x = action-9
            
        else:
            x = -1
        return x
            
    def ZombieHealth(self,row):
        ZombieHealth = 0
        ZombieFrontal = 850
        if self.hasZombie:
            for each in self.Zombie:
                if each.y == row:
                    #ZombieHealth = ZombieHealth + each.health
                    #ZombiePos = each.health*each.x+ZombiePos
                    if ZombieFrontal > each.x:
                        ZombieFrontal = each.x
                        ZombieHealth = each.health
        return ZombieHealth
    
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
    
    def PixelToBox(self,Pixel):
        Box = Pixel // 85
        return Box
    
    def ZombieHandleArray(self,row):
        ZombieList = [0] * 10
        numList = [0] * 10
        if self.hasZombie:
            for each in self.Zombie:
                if each.y == row:
                    Boxx = self.PixelToBox(each.x)
                    #TotalHealth = ZombieList[Boxx]*numList[Boxx]+each.health 
                    numList[Boxx] += 1
                    #ZombieList[Boxx] = #TotalHealth/numList[Boxx]
            return list(np.array(numList)/10)
        else:
            return list(np.array(numList)/10)

    def SelectRow(self):
        minimum = 1
        maxium=-1
        row1= -1
        row2 = -1
        for i in range(5):
            defendnum=0
            for j in self.PlantHandle1(i):
                if j==2:
                    defendnum=defendnum+1
            #print(defendnum)
            #t=self.ZombieHandle(i)[0]*(1+1/(self.ZombieHandle(i)[1]))/(defendnum+0.25)*(1+1/(self.ZombieHandle(i)[2]))
            t = self.ZombieHandle(i)[1] + defendnum*0.2
            if t>maxium:
                maxium=t
                row1=i
            if t<=minimum:
                minimum=t
                row2=i
        if minimum < 0.8:
            return row2
        else:
            return row1
        
        #if row==-1:
            #row=random.randint(0,4)

        #return row 
    
    
    def StateZip(self,row):
        self.zombie=self.ZombieHandleArray(row)
        IntactState =self.PlantHandle(row)
        IntactState.extend(self.zombie)
        IntactState.append(self.PEASHOOTERcd)
        IntactState.append(self.SUNFLOWERcd)
        #IntactState.append(gm.get_value("sun_value")/250)
        return IntactState

    def ZombieFront(self,state):
        for i in range(10):
            if state[18+i] !=0:
                return i
        return i
    def SelectAction(self):
        Action = np.ones(21)
        #Action = Action + 1
        self.updateState()
        
        for i in range(9):
            if self.Plant.plant_pos[self.row,i] != 0 :
                Action[i] = 0
                Action[i+9] = 0
        
        return np.array(Action)
    
    
    '''
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
    '''