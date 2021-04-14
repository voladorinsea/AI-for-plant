__author__ = 'marble_xu'

import os
import sys
#path=os.getcwd()
sys.path.append("..\source\AImodel.py")
import sched
import time
import json
from abc import abstractmethod
import pygame as pg
from . import constants as c
from . import AImodel
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
                print('pos:', self.mouse_pos, ' mouse:', self.mouse_click)
    
    def ai_test(self):
        if self.state_name == c.LEVEL:
            if self.state.state == c.PLAY:
                if (self.sun_value >=100) & self.state.menubar.my_checkCardClick(c.PEASHOOTER):
                    print(self.state.menubar.my_checkCardClick(c.PEASHOOTER))
                    self.state.my_addPlant(2,self.y,c.PEASHOOTER)
                    self.y = self.y +1
                    print("y is%d"%self.y)

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
    # function helps AI join the game in a setting delay
    def main(self):
        AlphaPlant=AImodel.agent(5)
        AlphaPlant.run()
        while not self.done:
            self.event_loop()
            self.update() 
            pg.display.update()
            self.clock.tick(self.fps)
            self.my_update()
            if c.AUTO:
                self.ai_test()
        print('game over')
        AlphaPlant.timer.cancel()

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
    file_path = os.path.join('source', 'data', 'entity', 'zombie.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.ZOMBIE_IMAGE_RECT]

def loadPlantImageRect():
    file_path = os.path.join('source', 'data', 'entity', 'plant.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.PLANT_IMAGE_RECT]

pg.init()
pg.display.set_caption(c.ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(c.SCREEN_SIZE)

GFX = load_all_gfx(os.path.join("resources","graphics"))
ZOMBIE_RECT = loadZombieImageRect()
PLANT_RECT = loadPlantImageRect()
