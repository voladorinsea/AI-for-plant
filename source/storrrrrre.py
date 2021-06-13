__author__ = 'marble_xu'
from source.constants import GRID_X_SIZE
import time
from threading import Timer,activeCount
import os
import json
from abc import abstractmethod
import pygame as pg
import numpy as np
from random import shuffle
from . import constants as c
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
        self.delay = 0.5

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
        self.v_zombie = 1.0/70.0    # 像素/ms
        self.v_bullet = 4*60/1000.0 # 像素/ms
        self.T_attack = 2000.0      # 植物攻击间隔ms  
        self.Z_attack = 1000.0      # 僵尸攻击间隔ms       
        self.Wallnut_HP = 30        # 坚果血量

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
    
    def Grid2PixelsX(self, map_x):
        if map_x < 0:
            return 0
        return map_x * c.GRID_X_SIZE + c.GRID_X_SIZE//2 + c.MAP_OFFSET_X
    
    def PixelsX2Grid(self,pixelsX):
        # print("pixelsX",pixelsX)
        if pixelsX > c.SCREEN_WIDTH:
            return 8
        else:
            return int(pixelsX/c.GRID_X_SIZE) - 1
                
    def getMapGridPosY(self, map_y):
        return map_y * c.GRID_Y_SIZE + c.GRID_Y_SIZE//5 * 3 + c.MAP_OFFSET_Y

    def LinearControl(self):
        if self.state_name != c.LEVEL:
            return
        if self.state.state != c.PLAY:
            return
        # 冷却没好
        if self.state.menubar.my_checkCardClick(c.PEASHOOTER) == False and \
            self.state.menubar.my_checkCardClick(c.SUNFLOWER) == False and \
            self.state.menubar.my_checkCardClick(c.WALLNUT) == False and \
            self.state.menubar.my_checkCardClick(c.SQUASH) == False:
            return
        if self.sun_value < 50:
            return

        '''
        读取每行最右侧植物信息
        Pp[0,i] = 第i行最右侧的植物位置(像素)
        Pp[1,i] = 第i行最右侧的植物血量
        Pp[2,i] = 第i行可种植植物(除坚果外)的最佳位置偏置(Grid坐标)
        Pp[3,i] = 第i行最右侧的植物位置(Grid)
        
        读取每行关键植物信息:豌豆射手、倭瓜、坚果
        Sp[0,i] = 第i行的豌豆射手数目
        Sp[1,i] = 第i行的坚果位置(Grid坐标)
        Sp[2,i] = 第i行的坚果血量
        Sp[3,i] = 第i行的倭瓜位置(Grid坐标)

        '''

        num_of_sunflower = 0 
        plant_pivot = np.zeros((4,5))
        plant_pivot[0,:] -= 1
        plant_pivot[2,:] -= 1
        plant_pivot[3,:] -= 1

        special_plant = np.zeros((4,5))
        special_plant[1,:] -= 1
        special_plant[3,:] -= 1
        for y in range(5):
            posX = -1
            for x in range(9):
                if self.plant_state_all.plant_pos[y,x] == 1:
                    num_of_sunflower += 1
                    posX = x
                if self.plant_state_all.plant_pos[y,x] == 2:
                    special_plant[0,y] += 1
                    posX = x
                if self.plant_state_all.plant_pos[y,x] == 3:
                    special_plant[1,y] = x
                    special_plant[2,y] = self.plant_state_all.plant_health[y,x]
                if self.plant_state_all.plant_pos[y,x] == 4:
                    special_plant[3,y] = x
                 
            plant_pivot[0,y] = self.Grid2PixelsX(posX)
            plant_pivot[1,y] = self.plant_state_all.plant_health[y,posX]
            plant_pivot[2,y] = 1
            plant_pivot[3,y] = posX
            while ( plant_pivot[3,y] + plant_pivot[2,y] == special_plant[1,y] or 
                    plant_pivot[3,y] + plant_pivot[2,y] == special_plant[3,y] ):
                plant_pivot[2,y] += 1
        
        '''
        简化僵尸模型1.0
        将第i行的多只僵尸合并为一只僵尸
        Zp[0,i] = 第i行僵尸血量加权位置
        Zp[1,i] = 第i行僵尸血量总和

        僵尸地图
        Zm[5,9] 五行十列的栅格地图,存储每格僵尸的个数
        '''
        zombie_pivot = np.zeros((2,5))
        zombie_map = np.zeros((5,10))
        
        if self.has_zombie == 1:
            for i in range(len(self.zombie_state_all)):
                tempY = self.zombie_state_all[i].y
                tempX = self.zombie_state_all[i].x
                tempH = self.zombie_state_all[i].health
                if tempX < c.ZOMBIE_START_X:
                    zombie_pivot[0,tempY] += tempX*tempH
                zombie_pivot[1,tempY] += tempH
                grid_X = self.PixelsX2Grid(tempX)
                zombie_map[tempY,grid_X] += 1   
                

        for i in range(5):
            if zombie_pivot[1,i] != 0:
                zombie_pivot[0,i]/=zombie_pivot[1,i]
            else:
                zombie_pivot[0,i] = c.ZOMBIE_START_X

        # print(zombie_map)      
        xi = [-1,0,1,2,3,4] #决策变量：在哪一行种植向日葵
        yi = [-1,0,1,2,3,4] #决策变量：在哪一行种植豌豆射手
        zi = [-1,0,1,2,3,4] #决策变量：在哪一行种坚果
        wi = [-1,0,1,2,3,4] #决策变量：在哪一行种倭瓜
        
        if num_of_sunflower >= 12 or self.state.menubar.my_checkCardClick(c.SUNFLOWER) == False:
            xi = [-1]
        if self.state.menubar.my_checkCardClick(c.PEASHOOTER) == False or self.sun_value < 100:
            yi = [-1]
        if self.state.menubar.my_checkCardClick(c.WALLNUT) == False or self.sun_value < 50:
            zi = [-1]
        if self.state.menubar.my_checkCardClick(c.SQUASH) == False or self.sun_value < 50:
            wi = [-1]

        out1 = -1 # 求解结果 在哪一行种向日葵 
        out2 = -1 # 求解结果：在哪一行种豌豆射手
        out3 = -1 # 求解结果：在哪一行种坚果
        out4 = -1 # 求解结果：在哪一行种倭瓜

        squash_position = -1
        wallnut_position = -1
        squash_position = -1

        # 倭瓜先行
        if wi != -1:
            fatal_row = 0
            min_dist = 800

            for row in range(5):
                Dist = zombie_pivot[0,row] - plant_pivot[0,row]
                if Dist < min_dist:
                    fatal_row = row
                    min_dist = Dist

            if min_dist < 300:
                out4 =  fatal_row
                squash_position = min(self.PixelsX2Grid(zombie_pivot[0,out4]),8)
                if squash_position == plant_pivot[3,out4]:
                    squash_position = min(squash_position + 1, 8)
                    plant_pivot[2,out4] += 1 #偏置+1
                self.sun_value -= 50
                zombie_pivot[1,i] -= 10

        # 线性评估法
        best_val = -1000
        for x in xi: # x是向日葵的决策变量
            for y in yi: # y是豌豆的决策变量
                for z in zi: # z是坚果的决策变量
                    if x == y and x!= -1: # 在同一个位置种两个植物
                        continue
                    if int(x!=-1)*50 + int(y!=-1)*100 + int(z!=-1)*50 >self.sun_value: 
                        continue
                    
                    # 攻击价值
                    attack_value = 0
                    for row in range(5):
                        Dist = zombie_pivot[0,row] - plant_pivot[0,row]
                        if x == row or y == row:
                            Dist -= c.GRID_X_SIZE * plant_pivot[2,row]
                        During = Dist/self.v_zombie
                        
                        if special_plant[2,row] != 0: # 此行已有坚果
                            num_of_zombie = zombie_map[row,int(special_plant[1,row])]
                            num_of_zombie += zombie_map[row,int(special_plant[1,row])+1]
                            During += special_plant[2,row]*self.Z_attack/(num_of_zombie+0.01)
                        
                        if z == row: #此行新增坚果
                            temp  = np.nonzero(zombie_map[row,:])[0]
                            if len(temp) != 0:
                                wallnut_position = min(8,temp[0])
                            else:
                                wallnut_position = 8
                            num_of_zombie = zombie_map[row,int(wallnut_position)]
                            num_of_zombie += zombie_map[row,int(wallnut_position)+1]
                            During += self.Wallnut_HP*self.Z_attack/(num_of_zombie+0.01)

                        AD = During * (special_plant[0,row] + int(y == row))/self.T_attack

                        if special_plant[3,row] != -1: # 有正在出击的倭瓜,僵尸血量--
                            zombie_pivot[1,row] -= 10
                        attack_value += min(AD - zombie_pivot[1,row],0)

                    # 阳光价值
                    sun_value = 0
                    if x != -1:
                        sun_value = (zombie_pivot[0,x] - plant_pivot[0,x] - c.GRID_X_SIZE)/c.SCREEN_WIDTH

                    # 未来价值
                    future_value = 0
                    if y != -1:
                        future_value = (zombie_pivot[0,y] - plant_pivot[0,y] - c.GRID_X_SIZE)/c.SCREEN_WIDTH
                    
                    temp_val = sun_value + future_value + 2*attack_value 
                    
                    # print(temp_val)
                    if best_val < temp_val:
                        best_val = temp_val
                        out1 = x
                        out2 = y
                        out3 = z
        
        print(out1,out2,out3,out4)
        print("------------------------")
        if out1 != -1:
            self.state.my_addPlant(int(plant_pivot[3,out1]+plant_pivot[2,out1]),out1,c.SUNFLOWER)
        if out2 != -1:
            self.state.my_addPlant(int(plant_pivot[3,out2]+plant_pivot[2,out2]),out2,c.PEASHOOTER)
        if out3 != -1:
            self.state.my_addPlant(int(wallnut_position),out3,c.WALLNUT)
        if out4 != -1:
            self.state.my_addPlant(int(squash_position),out4,c.SQUASH)
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

    def run(self):
        self.LinearControl()
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
    file_path = os.path.join(path1,'source', 'data', 'entity', 'zombie.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.ZOMBIE_IMAGE_RECT]

def loadPlantImageRect():
    file_path = os.path.join(path1,'source', 'data', 'entity', 'plant.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.PLANT_IMAGE_RECT]

pg.init()
pg.display.set_caption(c.ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(c.SCREEN_SIZE)

GFX = load_all_gfx(os.path.join(path1,"resources","graphics"))
ZOMBIE_RECT = loadZombieImageRect()
PLANT_RECT = loadPlantImageRect()