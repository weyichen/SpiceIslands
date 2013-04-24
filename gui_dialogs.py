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

# GUI debugging mode: do not generate map
gui_debug = True

# global variable settings
SHIPNAME = "SANTA MARIA"
NUMTURNS = 30
MOVESPTURN = 3

# Graphical Parameters for Game Map
FPS = 30 # frames per second, the general speed of the program
MAP_WIDTH = 640 # size of window's width in pixels
MAP_HEIGHT = 480 # size of windows' height in pixels
MARGIN = 20
BOX_SIZE = 20 # size of box height & width in pixels
BG_COLOR_LEVEL = 25
ISLAND_SIZE = 6 * BOX_SIZE # size of island bounding box height & width in pixels
MAP_COLUMNS = (MAP_WIDTH - 2 * MARGIN) / BOX_SIZE # number of columns of icons
MAP_ROWS = (MAP_HEIGHT - 2 * MARGIN) / BOX_SIZE # number of rows of icons
# COLORS
# NAME     (   R,   G,   B)
OCEAN    = (  25, 135, 255)
GREEN    = (   0, 255,  85)
RED      = ( 255,   0,   0)
YELLOW   = ( 255, 255,   0)

# GUI Elements that need to be updated
spice_table = gui.List(width=150, height=100)
score_table = gui.List(width=150, height=100)
turns_label = gui.Label(str(NUMTURNS))
moves_label = gui.Label(str(MOVESPTURN))
ship_label = gui.Label(SHIPNAME)

# Variables that keep track of the state of the game
dialog_on = False
moves_left = MOVESPTURN
spices_collected = {}
winning_spices = ["clove"]
event_img = "./Images/Spices/fennel.png"
event_msg = "You found fennel! You found fennel! You found fennel! You found fennel! You found fennel!"

# proper nouns
SPICELIST = ["clove","cardamom","nutmeg","mace","anise",
        "cinnamon","pepper","cumin","camphor","fennel"]
        
RESOURCELIST = ["sago","rice","tempeh","orangutan","guilders"]

ISLANDNAMES = ["Sumatra","Java","Sulawesi","Quezon","New Guinea",
        "Bali", "Singapore", "Borneo", "Hawaii", "Madagascar", "Mauritius",
        "Trinidad", "Tobago", "Atlantis", "Tasmania", "Tahiti"]

# events that can occur on the high seas!        
# we use a dictionary to map the randomly generated number to events
     
def natives_attack():
    event_img = ""
    event_msg = ""
    
def natives_help():
    event_img = ""
    event_msg = ""

def find_resource():
    event_img = "" 
    event_msg = ""
    
def malaria():
    event_img = "" 
    event_msg = "" 
    
def voc_bad():
    event_img = "" 
    event_msg = "" 

def voc_good():
    event_img = "" 
    event_msg = "" 

def typhoon():
    event_img = "" 
    event_msg = "" 

def cyclone():
    event_img = "" 
    event_msg = "" 

def scurvy():
    event_img = "" 
    event_msg = "" 

def pirates():
    event_img = "" 
    event_msg = "" 

def flotsam():
    event_img = "" 
    event_msg = "" 

def lost():
    event_img = "" 
    event_msg = "" 

def treasure():
    event_img = "" 
    event_msg = "" 

def fish():
    event_img = "" 
    event_msg = "" 

land_events = {
    0: natives_attack,
    1: natives_attack,
    2: natives_attack,
    3: natives_help,
    4: natives_help,
    5: find_resource,
    6: find_resource,
    7: find_resource,
    8: malaria,
    9: voc_bad,
    10: voc_good
}
sea_events = {
    0: typhoon,
    1: cyclone,
    2: cyclone,
    3: scurvy,
    4: pirates,
    5: pirates,
    6: voc_good,
    7: voc_good,
    8: flotsam,
    9: lost,
    10: lost,
    11: treasure,
    12: treasure,
    13: fish
}    
    

# Helper functions for updating labels and lists
def update_table(element, string):
    element.add(string)
    element.resize()
    element.repaint()
   
def set_table(element, strings):
    element.clear()
    for string in strings:
        element.add(string)
    element.repaint()
    
# Helper function for updating labels and lists
def update_label(element, string):
    element.set_text(string)
    element.resize()
    element.repaint()

# initial setup tbl
class InitDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Setup Game Options")
        width = 200
        height = 100
        
        winit = gui.Table()
        
        winit.tr()
        winit.td(gui.Label("Name of Ship"))
        self.name_input = gui.Input(value="Santa Maria",size=20)
        winit.td(self.name_input)
        
        winit.tr()
        winit.td(gui.Label("Number of Turns"))
        turn_slider = gui.HSlider(value=NUMTURNS,min=15,max=75,size=32,width=175,height=16)
        winit.td(turn_slider)
        turn_slider.connect(gui.CLICK, self.adj_scroll, (0, turn_slider))
        self.turn_label = gui.Label(str(NUMTURNS))
        winit.td(self.turn_label)
        
        winit.tr()
        winit.td(gui.Label("Moves per Turn"))
        move_slider = gui.HSlider(value=MOVESPTURN,min=3,max=10,size=32,width=175,height=16)
        winit.td(move_slider)
        move_slider.connect(gui.CLICK, self.adj_scroll, (1, move_slider))
        self.move_label = gui.Label(str(MOVESPTURN))
        winit.td(self.move_label)
        
        winit.tr()
        okay_button = gui.Button("Okay")
        okay_button.connect(gui.CLICK,self.confirm)
        winit.td(okay_button) # TODO: continue button to setup game
        #winit.td(Quit())
        
        gui.Dialog.__init__(self, title, winit)
        
    # updates displayed values of scroll bars
    def adj_scroll(self, value):
        (num, slider) = value
        if num == 0:
            update_label(self.turn_label, str(slider.value))
        if num == 1:
            update_label(self.move_label, str(slider.value))
    
    # sets values
    def confirm(self):
        global SHIPNAME, NUMTURNS, MOVESPTURN
        SHIPNAME = self.name_input.value
        NUMTURNS = self.turn_label.value
        MOVESPTURN = self.move_label.value
        update_label(ship_label, SHIPNAME)
        update_label(turns_label, NUMTURNS)
        update_label(moves_label, MOVESPTURN)
        self.close()

class EventDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Game Event")
        width = 200
        height = 100
        
        doc = gui.Document(width=400)
        space = title.style.font.size(" ")
        
        doc.block(align=1)
        doc.add(gui.Image(event_img),align=-1)
        for word in event_msg.split(" "):
            doc.add(gui.Label(word))
            doc.space(space)
            
        gui.Dialog.__init__(self,title,doc)
    
    def confirm(self):
        update_label(turns_label, NUMTURNS)
        update_label(moves_label, MOVESPTURN)
        self.close()
        
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
        
class MainGui(gui.Desktop):
    game_area_w = 480
    game_area_h = 640
    game_area = None

    def __init__(self, disp):
        gui.Desktop.__init__(self)
        
        self.connect(gui.QUIT, self.quit, None)
        
        # Display splashscreen while loading
        raw_splash_img = pygame.image.load(os.path.join('Images', 'splash.png'))
        splash_img = pygame.transform.smoothscale(raw_splash_img, (800, 480))
        disp.blit(splash_img, (0, 0))
        pygame.display.update()

        # Setup the 'game' area where the action takes place
        self.game_area = DrawingArea(self.game_area_w,
                                    self.game_area_h)
                                    
        init_dialog = InitDialog()
        self.connect(gui.INIT, init_dialog.open, None)
        
        event_dialog = EventDialog()
        self.connect(gui.INIT, event_dialog.open, None)
                                    
        menu = gui.Table(width=100, height=300, vpadding = 0, hpadding = 2, valign = -1)
        
        # row 1: name of ship
        menu.tr()
        name_label = gui.Label(SHIPNAME)
        menu.td(name_label)
        
        # sidebar row 1: spices and resources table
        menu.tr()
        menu.td(gui.Label("Spices & Resources"))
        menu.tr()
        menu.td(spice_table, align=-1, valign=-1)

        # row 3: turns left, moves left, and directional controls
        menu.tr()
        menu.td(gui.Label("Turns Left"))
        menu.td(turns_label)
        menu.tr()
        menu.td(gui.Label("Moves Left"))
        menu.td(moves_label)
        
        help_button = gui.Button("Help")
        help_button.connect(gui.CLICK, update_table(spice_table, "Clicked"), None)
        menu.td(help_button)

        # row 4: score table
        menu.tr()
        menu.td(gui.Label("Islands Visited"))
        menu.tr()
        menu.td(score_table, align=-1, valign=-1)
        
        spacer = gui.Table(width=800, height=100, vpadding = 0, hpadding = 2, valign = -1)
        
        # set up the overall layout
        tbl = gui.Table(height=disp.get_height())
        tbl.tr()
        tbl.td(menu)
        tbl.td(self.game_area)
        
        self.init(tbl, disp)

        noise_w = ISLAND_SIZE / 2
        noise_h = ISLAND_SIZE / 2
        noise_f = 3
        noise_o = 3
        
        p = PerlinNoiseGenerator()
        
        raw_ship_img = pygame.image.load(os.path.join('Images', 'sailboat.png'))
        self.ship_img = pygame.transform.smoothscale(raw_ship_img, (BOX_SIZE, BOX_SIZE))
        
        ship_placed = False
        self.ship_pos = None
        
        noise = np.array(p.generate_noise(ISLAND_SIZE, ISLAND_SIZE, 1.5, 3))
        rg = np.zeros(noise.shape, dtype=np.int8)
        rg.fill(25)
        bg = np.transpose(np.array([rg, rg, noise]))
        water = pygame.surfarray.make_surface(bg)
        
        self.islands = {}
        num_islands = 0
        
        for x in range(MAP_WIDTH / ISLAND_SIZE):
            for y in range(MAP_HEIGHT / ISLAND_SIZE):
                (left, top) = (x * ISLAND_SIZE, y * ISLAND_SIZE)
                if random.randint(1,3) > 1 and (x + y) % 2 == 0 and num_islands < len(ISLANDNAMES):
                    world = map.Map('Island', 
                        IslandGenerator().generate_island(noise_w, noise_h, noise_f, noise_o))
                    world.draw_minimap()
                    self.draw_surface(world.minimap, (left, top))
                    island_rect = pygame.Rect(left, top, ISLAND_SIZE, ISLAND_SIZE)
                    self.islands[ISLANDNAMES[num_islands]] = (False, island_rect)
                    num_islands += 1
                else:
                    self.draw_surface(water, (left, top))
                    if not ship_placed:
                        self.ship_pos = (left + MARGIN, top + MARGIN)
                        ship_placed = True
        
        self.canvas = pygame.surfarray.array3d(self.game_area.image_buffer)

    def run(self):
        global NUMTURNS, moves_left
        screen_rect = self.get_map_area()
        
        self.init()
        FPSCLOCK = pygame.time.Clock()
        mouse_x = 0 # used to store x coordinate of mouse event
        mouse_y = 0 # used to store y coordinate of mouse event
                
        # only run main game loop when there is no dialog
        while True and not dialog_on:
            mouse_clicked = False
            map_tile_x, map_tile_y = None, None
            self.draw_pixel_array(self.canvas)
            self.draw_surface(self.ship_img, self.ship_pos)
            
            for event in pygame.event.get(): # event handling loop
                self.event(event)
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                elif event.type == MOUSEBUTTONUP:
                    # only get map position if we clicked inside map
                    screen_rect = self.get_map_area()
                    mouse_x, mouse_y = event.pos
                    if mouse_x > screen_rect.x:
                        mouse_clicked = True
            
            map_tile_x, map_tile_y = self.get_map_tile_at_pixel(mouse_x, mouse_y)
            if map_tile_x != None and map_tile_y != None and NUMTURNS > 0:
                self.highlight_border(map_tile_x, map_tile_y, self.ship_pos, self.canvas)
                # The mouse is currently over a box.
                left, top = self.map_tile_corner(map_tile_x, map_tile_y)
                if self.is_reachable(left, top, self.ship_pos, self.canvas) and mouse_clicked:
                        # decrement number of moves by the distance traveled
                        moves_left-= self.block_distance(left, top, self.ship_pos)
                        # decrement number of turns
                        if moves_left == 0:
                            moves_left = MOVESPTURN
                            NUMTURNS-=1
                            update_label(turns_label, str(NUMTURNS))
                        update_label(moves_label, str(moves_left))
                
                        self.ship_pos = (left, top) # move the ship
                        self.game_area.repaint()
                        
                        # Report spices collected and update visited islands list
                        nearby = self.nearby_islands(map_tile_x, map_tile_y, self.canvas)
                        if nearby:
                            for island in nearby:
                                info = self.islands[island]
                                visited = info[0]
                                island_rect = info[1]
                                if not visited:
                                    update_table(score_table, island)
                                    
                                    spice_no = random.randint(0,9)
                                    the_spice = SPICELIST[spice_no]
                                    if the_spice in spices_collected:
                                        spices_collected[the_spice] = spices_collected[the_spice] + 1
                                    else:
                                        spices_collected[the_spice] = 1
                                    spice_list = [str(key) + " : " + str(val) \
                                            for key, val in spices_collected.items()]
                                    set_table(spice_table, spice_list)
                                    
                                    # Mark as visited
                                    self.islands[island] = (True, island_rect)
                                    
                                    if set(winning_spices).issubset(set(spices_collected)):
                                        update_table(score_table, "You Won!")
            
            # Redraw the screen and wait a clock tick.
            self.repaint()
            self.loop()
            FPSCLOCK.tick(FPS)
    
    def block_distance(self, left, top, ship_pos):
        destination = np.array([left, top])
        current_location = np.array(ship_pos)
        return int(np.linalg.norm(destination - current_location) / BOX_SIZE)
    
    def is_reachable(self, left, top, ship_pos, canvas):
        slice = canvas[left:left+39,top:top+39, :-1]
        dist = self.block_distance(left, top, ship_pos)
        return dist <= moves_left and not self.is_island(slice)
    
    def is_island(self, slice):
        return np.sum(slice != BG_COLOR_LEVEL) > 3 * np.size(slice) / 8
    
    def nearby_islands(self, x, y, canvas):
        islands_here = []
        for map_tile_x in range(max(0, x-1), min(MAP_COLUMNS, x + 2)):
            for map_tile_y in range(max(0, y-1), min(MAP_ROWS, y + 2)):
                if (map_tile_x == x or map_tile_y == y) :
                    (left, top) = self.map_tile_corner(map_tile_x, map_tile_y)
                    slice = canvas[left:left+39,top:top+39, :-1]
                    if self.is_island(slice):
                        box_rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
                        for island in self.islands:
                            island_rect = self.islands[island][1]
                            if island_rect.colliderect(box_rect):
                                islands_here.append(island)
        return islands_here
    
    def highlight_border(self, map_tile_x, map_tile_y, ship_pos, canvas):
        left, top = self.map_tile_corner(map_tile_x, map_tile_y)
        if self.is_reachable(left, top, ship_pos, canvas):
            if self.nearby_islands(map_tile_x, map_tile_y, canvas):
                color = GREEN
            else:
                color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(self.game_area.image_buffer, color, 
                (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)
        return

    def map_tile_corner(self, map_tile_x, map_tile_y):
        # Convert board coordinates to pixel coordinates
        left = map_tile_x * BOX_SIZE + MARGIN
        top = map_tile_y * BOX_SIZE + MARGIN
        return (left, top) 

    def get_map_tile_at_pixel(self, x, y):
        screen_rect = self.get_map_area()
        for map_tile_x in range(MAP_COLUMNS):
            for map_tile_y in range(MAP_ROWS):
                left, top = self.map_tile_corner(map_tile_x, map_tile_y)
                box_rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
                if box_rect.collidepoint(x - screen_rect.x, y - screen_rect.y):
                    return (map_tile_x, map_tile_y)
        return (None, None)
    
    def get_map_area(self):
        return self.game_area.get_abs_rect()
        
    def draw_surface(self, surf, pos):
        self.game_area.image_buffer.blit(surf, pos)
        
    def draw_pixel_array(self, canvas):
        pygame.surfarray.blit_array(self.game_area.image_buffer, canvas)

def main():
    pygame.init()
    disp = pygame.display.set_mode((800,480))
    pygame.display.set_caption('Spice Islands')
    gui = MainGui(disp)
    gui.run()

if __name__ == '__main__':
    main()  
    
