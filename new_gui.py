"""<title>Containers and more Connections</title>
A container is added, and centered a button within that
container.
"""
import pygame
import random, pygame, sys, os
from pygame.locals import *
import map
from perlin_noise import *
from island_generator import *
import numpy as np

# the following line is not needed if pgu is installed
sys.path.insert(0, "pgu")
from pgu import gui # TODO: figure out how to install pgu

# global variable settings
SHIPNAME = "SANTA MARIA"
NUMTURNS = 30
MOVESPTURN = 5

FPS = 30 # frames per second, the general speed of the program
WINDOWWIDTH = 640 # size of window's width in pixels
WINDOWHEIGHT = 480 # size of windows' height in pixels
MARGIN = 20
BOXSIZE = 40 # size of box height & width in pixels
BOARDWIDTH = (WINDOWWIDTH - 2 * MARGIN) / BOXSIZE # number of columns of icons
BOARDHEIGHT = (WINDOWHEIGHT - 2 * MARGIN) / BOXSIZE # number of rows of icons

# COLORS
# NAME     (   R,   G,   B)
OCEAN    = (  25, 135, 255)
GREEN    = (   0, 255,  85)
RED      = ( 255,   0,   0)
YELLOW   = ( 255, 255,  0)

# initial setup tbl
class InitDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Initial Game Options")
        width = 200
        height = 100
        
        # create a form. all widgets with names are added to the form, along with their data
        self.value = gui.Form()
        
        winit = gui.Table()
        
        winit.tr()
        winit.td(gui.Label("Name of Ship"))
        self.name_Input = gui.Input(name="name", value="Santa Maria",size=20)
        winit.td(self.name_Input)
        
        winit.tr()
        winit.td(gui.Label("Number of Turns"))
        turn_slider = gui.HSlider(value=50,min=15,max=75,size=32,width=175,height=16)
        winit.td(turn_slider)
        turn_slider.connect(gui.CLICK, self.adj_scroll, (0, turn_slider))
        self.turn_Input = gui.Input(name="turns", value=turn_slider.value, size=2, width=25)
        winit.td(self.turn_Input)
        
        winit.tr()
        winit.td(gui.Label("Moves per Turn"))
        move_slider = gui.HSlider(value=5,min=3,max=10,size=32,width=175,height=16)
        winit.td(move_slider)
        move_slider.connect(gui.CLICK, self.adj_scroll, (1, move_slider))
        self.move_Input = gui.Input(name="moves", value=move_slider.value, size=2, width=25)
        winit.td(self.move_Input)
        
        winit.tr()
        okay_button = gui.Button("Okay")
        okay_button.connect(gui.CLICK,self.confirm)
        winit.td(okay_button) # TODO: continue button to setup game
        winit.td(Quit())
        
        gui.Dialog.__init__(self, title, winit)
        
    # updates displayed values of scroll bars
    def adj_scroll(self, value):
        (num, slider) = value
        if num == 0:
            self.turn_Input.value = slider.value
        if num == 1:
            self.move_Input.value = slider.value
    
    # sets values
    def confirm(self):
        global SHIPNAME, NUMTURNS, MOVESPTURN
        SHIPNAME = self.name_Input.value
        NUMTURNS = self.turn_Input.value
        MOVESPTURN = self.move_Input.value
        self.send(gui.CHANGE)

# code for organizing tbl is like a HTML table
# using the tr and td methods
# td method adds elements to container by placing it in a subcontainer, so that it will not fill the whole cell


# drawing area where the action happens
class DrawingArea(gui.Widget):
    def __init__(self, width, height):
        gui.Widget.__init__(self, width=width, height=height)
        self.image_buffer = pygame.Surface((width, height))

    def paint(self, surf):
        # Paint whatever has been captured in the buffer
        surf.blit(self.image_buffer, (0, 0))
        
    # Call self function to take a snapshot of whatever has been rendered
    # onto the display over self widget.
    def save_background(self):
        disp = pygame.display.get_surface()
        self.image_buffer.blit(disp, self.get_abs_rect())
        
class MainGui(gui.Desktop):
    game_area_w = 480
    game_area_h = 640
    game_area = None
    menu_area = None

    def __init__(self, disp):
        gui.Desktop.__init__(self)
        
        self.connect(gui.QUIT, self.quit, None)

        # Setup the 'game' area where the action takes place
        self.game_area = DrawingArea(self.game_area_w,
                                    self.game_area_h)
                                    
        # Setup the gui area
        self.menu_area = gui.Container(
            width=disp.get_width()-self.game_area_w)
        
        tbl = gui.Table(height=disp.get_height())
        
        # row 1: name of ship
        tbl.tr()
        name_label = gui.Label(SHIPNAME)
        tbl.td(name_label)
        
        # row 2: sidebar and map tbl
        tbl.tr()
        # column 1 : sidebar
        sidebar = gui.Table(width=100, height=600)
        
        # sidebar row 1: spices and resources table
        sidebar.tr()
        sidebar.td(gui.Label("Spices & Resources"))

        # row 3: turns left, moves left, and directional controls
        sidebar.tr()
        sidebar.td(gui.Label("Turns Left"))
        sidebar.td(gui.Label("Moves Left"))

        # row 4: score table
        sidebar.tr()
        sidebar.td(gui.Label("Scores"))
        
        tbl.td(sidebar)

        # column 2 : map tbl
        tbl.td(self.game_area)
        
        self.init(tbl, disp)

        noise_w = 40
        noise_h = 40
        noise_f = 1
        noise_o = 5
        
        p = PerlinNoiseGenerator()
        
        raw_ship_img = pygame.image.load(os.path.join('Images', 'sailboat.png'))
        self.ship_img = pygame.transform.smoothscale(raw_ship_img, (40, 40))
        
        ship_placed = False
        self.ship_pos = None
        
        for x in range(4):
            for y in range(3):
                world = map.Map('Island',
                IslandGenerator().generate_island(noise_w, noise_h, noise_f, noise_o))
                if random.randint(1,3) > 1 and (x + y) % 2 == 0:
                    world.map = IslandGenerator().generate_island(noise_w, noise_h, noise_f, noise_o)
                    world.draw_minimap()
                    self.drape(world.minimap, (x * 160, y * 160))
                else:
                    noise = np.array(p.generate_noise(4*noise_w,4*noise_h,noise_f, noise_o))
                    rg = np.zeros(noise.shape, dtype=np.int8)
                    rg.fill(25)
                    bg = np.transpose(np.array([rg, rg, noise]))
                    s = pygame.surfarray.make_surface(bg)
                    self.drape(s, (x * 160, y* 160))
                    if not ship_placed:
                        self.ship_pos = (x * 160 + 20, y * 160 + 20)
                        ship_placed = True
                        
        self.canvas = pygame.surfarray.array3d(self.game_area.image_buffer)

    def run(self):
        self.init()
        FPSCLOCK = pygame.time.Clock()
        mouse_x = 0 # used to store x coordinate of mouse event
        mouse_y = 0 # used to store y coordinate of mouse event
                
        while True: # main game loop
            mouse_clicked = False
            self.plaster(self.canvas)
            self.drape(self.ship_img, self.ship_pos)
            
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    mouse_clicked = True
            
            boxx, boxy = self.get_box_at_pixel(mouse_x, mouse_y)
            if boxx != None and boxy != None:
                self.highlight_border(boxx, boxy, self.ship_pos, self.canvas)
                # The mouse is currently over a box.
                left, top = self.box_corner(boxx, boxy)
                if self.is_reachable(left, top, self.ship_pos, self.canvas) and mouse_clicked:
                        self.ship_pos = (left, top) # move the ship
                        self.game_area.repaint()
            
            # Redraw the screen and wait a clock tick.
            self.repaint()
            self.loop()
            FPSCLOCK.tick(FPS)
    
    def is_reachable(self, left, top, ship_pos, canvas):
        slice = canvas[left:left+39,top:top+39, :-1]
        destination = np.array([left, top])
        current_location = np.array(ship_pos)
        dist = np.linalg.norm(destination - current_location)
        return dist < 100 and not self.is_island(slice)
    
    def is_island(self, slice):
        return np.sum(slice != 25) > 2 * np.size(slice) / 3
    
    def near_island(self, x, y, ship_pos, canvas):
        island = False
        for box_x in range(max(0, x-1), min(BOARDWIDTH, x + 2)):
            for box_y in range(max(0, y-1), min(BOARDHEIGHT, y + 2)):
                (left, top) = self.box_corner(box_x, box_y)
                slice = canvas[left:left+39,top:top+39, :-1]
                if self.is_island(slice):
                    island = True
        
        return island
    
    def highlight_border(self, box_x, box_y, ship_pos, canvas):
        left, top = self.box_corner(box_x, box_y)
        if self.is_reachable(left, top, ship_pos, canvas):
            if self.near_island(box_x, box_y, ship_pos, canvas):
                color = GREEN
            else:
                color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(self.game_area.image_buffer, color, 
                (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
        return

    def box_corner(self, box_x, box_y):
        # Convert board coordinates to pixel coordinates
        left = box_x * BOXSIZE + MARGIN
        top = box_y * BOXSIZE + MARGIN
        return (left, top) 

    def get_box_at_pixel(self, x, y):
        for box_x in range(BOARDWIDTH):
            for box_y in range(BOARDHEIGHT):
                left, top = self.box_corner(box_x, box_y)
                box_rect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
                if box_rect.collidepoint(x - 275, y - 10):
                    return (box_x, box_y)
        return (None, None)
    
    def get_render_area(self):
        return self.game_area.get_abs_rect()
        
    def get_canvas(self):
        return pygame.surfarray.array3d(self.game_area.image_buffer)
        
    def drape(self, surf, pos):
        self.game_area.image_buffer.blit(surf, pos)
        
    def plaster(self, canvas):
        pygame.surfarray.blit_array(self.game_area.image_buffer, canvas)

def main():
    pygame.init()
    disp = pygame.display.set_mode((800,600))
    pygame.display.set_caption('Spice Islands')
    gui = MainGui(disp)
    gui.run()

if __name__ == '__main__':
    main()  
    
