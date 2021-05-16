__author__ = 'marble_xu'

import time
from threading import Timer,activeCount
import os
import json
from abc import abstractmethod
import pygame as pg
import numpy as np
from random import shuffle
from . import constants as c
from . import AImodel
path1=os.path.abspath('.')
class State():
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}
    
    @abstractmethod
    def startup(self, current_time, persist):
        '''abstract method'''

    def cleanup(self):
        self.done = False
        return self.persist
    
    @abstractmethod
    def update(self, surface, keys, current_time):
        '''abstract method'''

class Control():
    def __init__(self):
        self.delay=0.5

        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed()
        self.mouse_pos = None
        self.mouse_click = [False, False]  # value:[left mouse click, right mouse click]
        self.current_time = 0.0
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.game_info = {c.CURRENT_TIME:0.0,
                          c.LEVEL_NUM:c.START_LEVEL_NUM}
        #add some varialble
        self.frequency = 30
        self.count_time = 0  
        self.v_zombie = 1.0/70.0    # 像素/ms
        self.v_bullet = 4*60/1000.0 # 像素/ms
        self.T_attack = 2000.0        # 攻击间隔ms          
        self.y=0
        self.sun_value=0
        self.has_zombie = 0
        self.zombie_state_all = []
        self.has_bullet = 0
        self.bullet_state_all = []

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, self.game_info)

    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.current_time, self.mouse_pos, self.mouse_click)
        self.mouse_pos = None
        self.mouse_click[0] = False
        self.mouse_click[1] = False

    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pos = pg.mouse.get_pos()
                self.mouse_click[0], _, self.mouse_click[1] = pg.mouse.get_pressed()
                #print('pos:', self.mouse_pos, ' mouse:', self.mouse_click)
    
    def ai_test(self):
        if self.state_name == c.LEVEL:
            if self.state.state == c.PLAY:
                if (self.sun_value >=100) & self.state.menubar.my_checkCardClick(c.PEASHOOTER):
                    print(self.state.menubar.my_checkCardClick(c.PEASHOOTER))
                    self.state.my_addPlant(2,self.y,c.PEASHOOTER)
                    self.y = self.y +1
                    print("y is%d"%self.y)
    
    def Grid2PixelsX(self, map_x):
        if map_x < 0:
            return 0
        return map_x * c.GRID_X_SIZE + c.GRID_X_SIZE//2 + c.MAP_OFFSET_X
                
    def getMapGridPosY(self, map_y):
        return map_y * c.GRID_Y_SIZE + c.GRID_Y_SIZE//5 * 3 + c.MAP_OFFSET_Y

    def LinearControl(self):
        if self.state_name != c.LEVEL:
            return
        if self.state.state != c.PLAY:
            return
        if self.count_time < self.frequency:
            return
        # 冷却没好
        if self.state.menubar.my_checkCardClick(c.PEASHOOTER) == False and \
            self.state.menubar.my_checkCardClick(c.SUNFLOWER) == False:
            return
        if self.sun_value <50:
            return
        # 30*1/30 = 0.5s 每隔0.5s进行一次决策
        self.count_time = 0
        '''
        读取每行最右侧植物信息 以及 豌豆射手数量
        Pp[0,i] = 第i行最右侧的植物位置(像素)
        Pp[1,i] = 第i行最右侧的植物血量
        Pp[2,i] = 第i行的豌豆射手数目
        Pp[3,i] = 第i行最右侧的植物位置(Grid)
        '''
        plant_pivot = np.zeros((4,5))
        plant_pivot[0,:] -= 1
        plant_pivot[3,:] -= 1
        for y in range(5):
            posX = -1
            for x in range(9):
                if self.plant_state_all.plant_pos[y,x]!=0:
                    posX = x
                if self.plant_state_all.plant_pos[y,x]==2:
                    plant_pivot[2,y] += 1
            plant_pivot[0,y] = self.Grid2PixelsX(posX)
            plant_pivot[3,y] = posX
            plant_pivot[1,y] = self.plant_state_all.plant_health[y,posX]

        '''
        简化僵尸模型1.0
        将第i行的多只僵尸合并为一只僵尸
        Zp[0,i] = 第i行僵尸血量加权位置
        Zp[1,i] = 第i行僵尸血量总和
        '''
        zombie_pivot = np.zeros((2,5))
        if self.has_zombie == 1:
            for i in range(len(self.zombie_state_all)):
                tempY = self.zombie_state_all[i].y
                tempX = self.zombie_state_all[i].x
                tempH = self.zombie_state_all[i].health
                if tempX < c.ZOMBIE_START_X:
                    zombie_pivot[0,tempY] += tempX*tempH   
                zombie_pivot[1,tempY] += tempH
        for i in range(5):
            if zombie_pivot[1,i] != 0:
                zombie_pivot[0,i]/=zombie_pivot[1,i]
            else:
                zombie_pivot[0,i] = c.ZOMBIE_START_X

        print(zombie_pivot)      
        xi = [-1,0,1,2,3,4] #决策变量：在哪一行种植
        out1 = -1 #求解结果 在哪一行种向日葵 
        out2 = -1 #求解结果：在哪一行种豌豆射手

        if self.state.menubar.my_checkCardClick(c.PEASHOOTER) == False \
            or self.sun_value < 100: #只能种向日葵
            best_val = 0
            for each in xi:
                temp_val = 0
                # 约束条件折算为损失函数
                if each != -1:
                    Dist = zombie_pivot[0,each] - plant_pivot[0,each] - c.GRID_X_SIZE
                    temp_val = Dist
                if best_val < temp_val:
                    best_val = temp_val
                    out1 = each
                #elif best_val == temp_val:

        elif self.state.menubar.my_checkCardClick(c.SUNFLOWER) == False: #只能种豌豆射手
            best_val = -1000
            for each in xi:
                sum_loss = 0
                for row in range(5):
                    # 检测约束条件
                    Dist = zombie_pivot[0,row] - plant_pivot[0,row]
                    if each == row:
                        Dist -= c.GRID_X_SIZE
                    During = Dist/self.v_zombie
                    AD = During * (plant_pivot[2,row] + int(each == row))/self.T_attack
                    sum_loss += min(AD - zombie_pivot[1,row],0)
                temp_val = sum_loss 
                if best_val < temp_val:
                    best_val = temp_val
                    out2 = each
        
        else: #都可以种
            best_val = -1000
            for x in xi:
                for y in xi:
                    if x == y and x!= -1:
                        continue
                    if int(x!=-1)*50 + int(y!=-1)*100 >self.sun_value:
                        continue
                    sum_loss = 0
                    for row in range(5):
                        Dist = zombie_pivot[0,row] - plant_pivot[0,row]
                        if x == row or y == row:
                            Dist -= c.GRID_X_SIZE
                        During = Dist/self.v_zombie
                        AD = During * (plant_pivot[2,row] + int(y == row))/self.T_attack
                        sum_loss += min(AD - zombie_pivot[1,row],0)
                        
                    temp_val = int(x != -1) + 10*sum_loss 
                    if best_val < temp_val:
                        best_val = temp_val
                        out1 = x
                        out2 = y
        
        print(out1,out2)
        print("------------------------")
        if out1 != -1:
            self.state.my_addPlant(int(plant_pivot[3,out1])+1,out1,c.SUNFLOWER)
        if out2 != -1:
            self.state.my_addPlant(int(plant_pivot[3,out2])+1,out2,c.PEASHOOTER)
        return

    def my_update(self):
        if self.state_name == c.LEVEL:
            if self.state.state == c.PLAY:
                self.sun_value = self.state.sun_value

                # 植物信息(class)
                # 地图上的植物分布：game.plant_state_all.plant_pos
                #               1、数据类型 np.array(5,9)
                #               2、植物种类：0表示没植物，1表示向日葵，2表示豌豆射手
                # 地图上的植物血量：game.plant_state_all.plant_health
                #               1、数据类型 np.array(5,9) 
                self.plant_state_all = self.state.plant_state_all

                # 是否有僵尸（0无，1有）
                self.has_zombie = self.state.has_zombie

                # 僵尸信息(list)，其中的每一个元素为一个class
                # eg:
                #     僵尸种类：self.zombie_state_all[0].name
                #     僵尸坐标x(像素表示）：self.zombie_state_all[0].x
                #     僵尸坐标y(0,1,2,3,4,5表示）：self.zombie_state_all[0].y
                #     僵尸血量：self.zombie_state_all[0].health
                #     僵尸状态：self.zombie_state_all[0].state（walk：正常行走；attack：被攻击）
                # 无僵尸则为[]
                self.zombie_state_all = self.state.zombie_state_all

                # 是否有子弹（0无，1有）
                self.has_bullet = self.state.has_bullet

                # 子弹信息(list)，其中的每一个元素为一个class
                # eg:
                #     子弹种类：self.bullet_state_all[0].name
                #     子弹坐标x(像素表示）：self.bullet_state_all[0].x
                #     子弹坐标y(像素表示）：self.bullet_state_all[0].y
                #     子弹状态：self.bullet_state_all[0].state（fly：正常飞行；explode：击中目标）
                # 无子弹则为[]
                self.bullet_state_all = self.state.bullet_state_all
    
    def AI(self):
        self.LinearControl()
    def run(self):
        self.AI()
        self.timer = Timer(self.delay, self.run,())
        self.timer.start()

    def main(self):
        self.run()
        while not self.done:
            self.event_loop()
            self.update() 
            pg.display.update()
            self.clock.tick(self.fps)
            self.my_update()
            self.count_time += 1
            #if c.AUTO:
            #self.LinearControl()
        print('game over')

def get_image(sheet, x, y, width, height, colorkey=c.BLACK, scale=1):
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(colorkey)
        image = pg.transform.scale(image,
                                   (int(rect.width*scale),
                                    int(rect.height*scale)))
        return image

def load_image_frames(directory, image_name, colorkey, accept):
    frame_list = []
    tmp = {}
    # image_name is "Peashooter", pic name is 'Peashooter_1', get the index 1
    index_start = len(image_name) + 1 
    frame_num = 0
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            index = int(name[index_start:])
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            tmp[index]= img
            frame_num += 1

    for i in range(frame_num):
        frame_list.append(tmp[i])
    return frame_list

def load_all_gfx(directory, colorkey=c.WHITE, accept=('.png', '.jpg', '.bmp', '.gif')):
    graphics = {}
    for name1 in os.listdir(directory):
        # subfolders under the folder resources\graphics
        dir1 = os.path.join(directory, name1)
        if os.path.isdir(dir1):
            for name2 in os.listdir(dir1):
                dir2 = os.path.join(dir1, name2)
                if os.path.isdir(dir2):
                # e.g. subfolders under the folder resources\graphics\Zombies
                    for name3 in os.listdir(dir2):
                        dir3 = os.path.join(dir2, name3)
                        # e.g. subfolders or pics under the folder resources\graphics\Zombies\ConeheadZombie
                        if os.path.isdir(dir3):
                            # e.g. it's the folder resources\graphics\Zombies\ConeheadZombie\ConeheadZombieAttack
                            image_name, _ = os.path.splitext(name3)
                            graphics[image_name] = load_image_frames(dir3, image_name, colorkey, accept)
                        else:
                            # e.g. pics under the folder resources\graphics\Plants\Peashooter
                            image_name, _ = os.path.splitext(name2)
                            graphics[image_name] = load_image_frames(dir2, image_name, colorkey, accept)
                            break
                else:
                # e.g. pics under the folder resources\graphics\Screen
                    name, ext = os.path.splitext(name2)
                    if ext.lower() in accept:
                        img = pg.image.load(dir2)
                        if img.get_alpha():
                            img = img.convert_alpha()
                        else:
                            img = img.convert()
                            img.set_colorkey(colorkey)
                        graphics[name] = img
    return graphics

def loadZombieImageRect():
    file_path = os.path.join(path1,"AI-for-plant",'source', 'data', 'entity', 'zombie.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.ZOMBIE_IMAGE_RECT]

def loadPlantImageRect():
    file_path = os.path.join(path1,"AI-for-plant",'source', 'data', 'entity', 'plant.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.PLANT_IMAGE_RECT]

pg.init()
pg.display.set_caption(c.ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(c.SCREEN_SIZE)

GFX = load_all_gfx(os.path.join(path1,"AI-for-plant","resources","graphics"))
ZOMBIE_RECT = loadZombieImageRect()
PLANT_RECT = loadPlantImageRect()
