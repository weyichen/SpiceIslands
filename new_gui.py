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
NAVYBLUE = (  60,  60, 100)
OCEAN    = (  25, 135, 255)
GREEN    = (   0, 255,  85)
RED      = ( 255,   0,   0)

BGCOLOR = OCEAN
BOXCOLOR = GREEN
HIGHLIGHTCOLOR = RED

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
        self.imageBuffer = pygame.Surface((width, height))

    def paint(self, surf):
        # Paint whatever has been captured in the buffer
        surf.blit(self.imageBuffer, (0, 0))
        
    # Call self function to take a snapshot of whatever has been rendered
    # onto the display over self widget.
    def save_background(self):
        disp = pygame.display.get_surface()
        self.imageBuffer.blit(disp, self.get_abs_rect())
        
class MainGui(gui.Desktop):
    gameAreaWidth = 480
    gameAreaHeight = 640
    gameArea = None
    menuArea = None

    def __init__(self, disp):
        gui.Desktop.__init__(self)
        
        self.connect(gui.QUIT, self.quit, None)

        # Setup the 'game' area where the action takes place
        self.gameArea = DrawingArea(self.gameAreaWidth,
                                    self.gameAreaHeight)
                                    
        # Setup the gui area
        self.menuArea = gui.Container(
            width=disp.get_width()-self.gameAreaWidth)
        
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
        tbl.td(self.gameArea)
        
        self.init(tbl, disp)

        noise_w = 40
        noise_h = 40
        noise_f = 1
        noise_o = 5
        
        p = PerlinNoiseGenerator()
        
        raw_ship_img = pygame.image.load(os.path.join('Images', 'sailboat.png'))
        self.ship_img = pygame.transform.smoothscale(raw_ship_img, (40, 40))
        
        shipPlaced = False
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
                    if not shipPlaced:
                        self.ship_pos = (x * 160 + 120, y * 160 + 20)
                        shipPlaced = True
                        
        self.canvas = pygame.surfarray.array3d(self.gameArea.imageBuffer)

    def run(self):
        self.init()
        FPSCLOCK = pygame.time.Clock()
        mousex = 0 # used to store x coordinate of mouse event
        mousey = 0 # used to store y coordinate of mouse event
                
        while True: # main game loop
            mouseClicked = False
            self.plaster(self.canvas)
            self.drape(self.ship_img, self.ship_pos)
            
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True
            
            boxx, boxy = self.getBoxAtPixel(mousex, mousey)
            if boxx != None and boxy != None:
                self.drawHighlightBox(boxx, boxy, self.ship_pos, self.canvas)
                # The mouse is currently over a box.
                left, top = self.leftTopCoordsOfBox(boxx, boxy)
                if self.isReachable(left, top, self.ship_pos, self.canvas) and mouseClicked:
                        self.ship_pos = (left + 20, top + 20) # move the ship
                        self.gameArea.repaint()
            
            # Redraw the screen and wait a clock tick.
            self.repaint()
            self.loop()
            FPSCLOCK.tick(FPS)
    
    def isReachable(self, left, top, ship_pos, canvas):
        slice = canvas[left:left+39,top:top+39, :-1]
        destination = np.array([left, top])
        current_location = np.array(ship_pos)
        dist = np.linalg.norm(destination - current_location)
        return dist < 100 and not (slice > 25).any()
    
    def drawHighlightBox(self, boxx, boxy, ship_pos, canvas):
        left, top = self.leftTopCoordsOfBox(boxx, boxy)
        if self.isReachable(left, top, ship_pos, canvas):
            pygame.draw.rect(self.gameArea.imageBuffer, GREEN, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
        else:
            pygame.draw.rect(self.gameArea.imageBuffer, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
        return

    def leftTopCoordsOfBox(self, boxx, boxy):
        # Convert board coordinates to pixel coordinates
        left = boxx * BOXSIZE + MARGIN
        top = boxy * BOXSIZE + MARGIN
        return (left, top) 

    def getBoxAtPixel(self, x, y):
        for boxx in range(BOARDWIDTH):
            for boxy in range(BOARDHEIGHT):
                left, top = self.leftTopCoordsOfBox(boxx, boxy)
                boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
                if boxRect.collidepoint(x - 275, y - 10):
                    return (boxx, boxy)
        return (None, None)
    
    def get_render_area(self):
        return self.gameArea.get_abs_rect()
        
    def get_canvas(self):
        return pygame.surfarray.array3d(self.gameArea.imageBuffer)
        
    def drape(self, surf, pos):
        self.gameArea.imageBuffer.blit(surf, pos)
        
    def plaster(self, canvas):
        pygame.surfarray.blit_array(self.gameArea.imageBuffer, canvas)

def main():
    pygame.init()
    disp = pygame.display.set_mode((800,600))
    pygame.display.set_caption('Spice Islands')
    gui = MainGui(disp)
    gui.run()

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    
    #canvas = gui.get_canvas()
    
    while True: # main game loop
        mouseClicked = False
        gui.plaster(canvas)
        gui.drape(ship_img, ship_pos)
        
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        mousex -= gameArea.rect.x
        mousy -= gameArea.rect.y
        boxx, boxy = gui.getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            gui.drawHighlightBox(boxx, boxy, ship_pos, canvas)
            # The mouse is currently over a box.
            left, top = gui.leftTopCoordsOfBox(boxx, boxy)
            if gui.isReachable(left, top, ship_pos, canvas) and mouseClicked:
                    ship_pos = (left, top) # move the ship
        
        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()  
    
