import pygame
import random, pygame, sys, os
from pygame.locals import *
import map
from perlin_noise import *
from island_generator import *
import numpy as np
import Queue
import time

# the following line is not needed if pgu is installed
sys.path.insert(0, "pgu")
from pgu import gui # TODO: figure out how to install pgu

# initial setup settings
ship_name = "SANTA MARIA"
num_turns = 30
moves_per_turn = 3
spices_to_win = 5

""" Graphical Parameters for Game Map """

# Display Scaling Factors
SCREEN_WIDTH = 850 # size of window's width in pixels
SCREEN_HEIGHT = 480 # size of window's height in pixels
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
MAP_WIDTH = 600 # size of map's width in pixels
MAP_HEIGHT = 480 # size of map's height in pixels
MAP_SIZE = (MAP_WIDTH, MAP_HEIGHT)
MAP_TILE_WIDTH = 20 # size of map tile's width in pixels
MAP_TILE_HEIGHT = 20 # size of map tile's height in pixels
MAP_TILE_SIZE = (MAP_TILE_WIDTH, MAP_TILE_HEIGHT)
ISLAND_WIDTH = 6 * MAP_TILE_WIDTH # size of island bounding box height & width in pixels
ISLAND_HEIGHT = 6 * MAP_TILE_HEIGHT # size of island bounding box height & width in pixels
ISLAND_SIZE = (ISLAND_WIDTH, ISLAND_HEIGHT)

# Other scale constants
MARGIN = 20
MAP_COLUMNS = (MAP_WIDTH - 2 * MARGIN) / MAP_TILE_WIDTH # number of columns of icons
MAP_ROWS = (MAP_HEIGHT - 2 * MARGIN) / MAP_TILE_HEIGHT # number of rows of icons

# Non-scaling constants
FPS = 30 # frames per second, the general speed of the program
BG_COLOR_LEVEL = 25
NUM_ISLANDS = 7

# Very basic quality control on constant parameters
assert MAP_WIDTH <= SCREEN_WIDTH
assert MAP_HEIGHT <= SCREEN_HEIGHT
assert MAP_TILE_WIDTH <= ISLAND_WIDTH
assert MAP_TILE_HEIGHT <= ISLAND_HEIGHT
assert MAP_COLUMNS >= 10
assert MAP_ROWS >= 10

# COLORS
# NAME     (   R,   G,   B)
OCEAN    = (  25, 135, 255)
GREEN    = (   0, 255,  85)
RED      = ( 255,   0,   0)
YELLOW   = ( 255, 255,   0)
WHITE    = ( 255, 255, 255)

# GUI Elements that need to be updated
spice_table = gui.List(width=125, height=100)
spice_win_table = gui.List(width=125, height=100)
resources_table = gui.List(width=125, height=100)
islands_table = gui.List(width=125, height=100)
turns_label = gui.Label(str(num_turns))
moves_label = gui.Label(str(moves_per_turn))
ship_label = gui.Label(ship_name)

# Variables that keep track of the state of the game
dialog_on = True
dialog_q = Queue.LifoQueue()
moves_left = moves_per_turn
spices_collected = []
resources_collected = []

# proper nouns
SPICE_LIST = ["clove","cardamom","nutmeg","mace","anise",
        "cinnamon","pepper","cumin","camphor","fennel"]
random.shuffle(SPICE_LIST)
winning_spices = SPICE_LIST[:spices_to_win]
        
RESOURCE_LIST = ["sago","rice","tempeh","orangutan","guilders","cloth","wood"]

ISLAND_NAMES = ["Sumatra","Java","Sulawesi","Quezon","New Guinea",
        "Bali", "Singapore", "Borneo", "Hawaii", "Madagascar", "Mauritius",
        "Trinidad", "Tobago", "Tasmania", "Tahiti"]
random.shuffle(ISLAND_NAMES)
        
def set_event(image, message):
    """ helper method to set event image and message """
    global event_img, event_msg, dialog_q
    event_img = "./Images/" + image + ".png"
    event_msg = message
    
    event_dialog = EventDialog()
    dialog_q.put(event_dialog)

# events that can occur on the high seas!        
# we use a dictionary to map the randomly generated number to events
     
def natives_attack():
    global num_turns, spices_collected
    num_spices = len(spices_collected)
    
    if (num_spices):
        spice_no = random.randint(0,len(spices_collected)-1)
        spice = spices_collected[spice_no]
        set_event("Events/attack", "The natives are hostile! You lose a turn and your " + spice + ".")
        
        spices_collected.pop(spice_no)
        set_table(spice_table, spices_collected)
    else:
        set_event("Events/attack", "The natives are hostile! You lose a turn.")
    
    num_turns -= 1

     
def natives_help():
    global num_turns, spices_collected
    spice_no = random.randint(0,len(SPICE_LIST) - 1)
    spice = SPICE_LIST[spice_no]
    set_event("Events/help", "The natives are friendly! You gain a turn and some " + spice + ".")
    
    spices_collected.append(spice)
    set_table(spice_table, spices_collected)
    num_turns += 1

def find_resource():
    global resources_collected    
    resource_no = random.randint(0,len(RESOURCE_LIST) - 1)
    resource = RESOURCE_LIST[resource_no]
    set_event("Resources/" + resource, "Fortune smiles upon you! You have found " + resource + ".")
    
    resources_collected.append(resource)
    set_table(resources_table, resources_collected)
    
def malaria():
    global moves_per_turn
    set_event("Events/malaria", "A crew member has succumbed to malaria. You lose one move per turn!")
    
    moves_per_turn -= 1
    
def voc_bad():
    global resources_collected
    num_resources = len(resources_collected)
    
    if (num_resources):
        resource_no = random.randint(0,len(resources_collected) - 1)
        resource = RESOURCE_LIST[resource_no]
        set_event("Events/voc", "Fellow VOC employees are in need. You give them your " + resource + ".")
        
        resources_collected.pop(resource_no)
        set_table(resources_table, resources_collected)

def voc_good():
    global moves_per_turn
    set_event("Events/voc", "The VOC is pleased with your efforts. A new crew member has been recruited " + \
            "into your service. You gain one move per turn!")
    
    moves_per_turn += 1

def typhoon():
    global num_turns, spices_collected
    num_spices = len(spices_collected)
    
    if (num_spices):
        spice_no = random.randint(0,len(spices_collected)-1)
        spice = spices_collected[spice_no]
        set_event("Events/typhoon", "You are caught in a typhoon! Your " + spice + " is washed off board and lost in the sea. " + \
            "You also lose one turn to inclement weather.")
        
        spices_collected.pop(spice_no)
        set_table(spice_table, spices_collected)
    else:
        set_event("Events/typhoon", "You are caught in a typhoon! You lose one turn to inclement weather.")
    
    num_turns -= 1
    
def cyclone():
    global num_turns
    
    set_event("Events/cyclone", "A cyclone is brewing, and you are forced to wait for clearer skies. " \
            "You lose one turn to inclement weather.")
    num_turns -= 1

def scurvy():
    global moves_per_turn
    set_event("Events/scurvy", "You should have stocked up on limes! A crew member has succumbed to scurvy. " + \
            "You lose one move per turn!")
    
    moves_per_turn -= 1

def pirates():
    global resources_collected
    num_resources = len(resources_collected)
    
    if (num_resources):
        resource_no = random.randint(0,len(resources_collected) - 1)
        resource = RESOURCE_LIST[resource_no]
        set_event("Events/pirates", "AAAARGHH! Pirates have stolen your " + resource + ".")
        
        resources_collected.pop(resource_no)
        set_table(resources_table, resources_collected)

def flotsam():
    global resources_collected
    resource_no = random.randint(0,len(RESOURCE_LIST) - 1)
    resource = RESOURCE_LIST[resource_no]
    set_event("Resources/" + resource, "You narrowly missed a storm in this area. As you pass the remains of a " + \
            "shipwreck, you find some valuable " + resource + ".")
    
    resources_collected.append(resource)
    set_table(resources_table, resources_collected)

def lost_at_sea():
    global num_turns
    set_event("Events/lost_at_sea", "What have you been doing with your sextant?! Due to poor navigation, " + \
            "you have become lost at sea. You lose 2 turns!")
            
    num_turns -= 1

def treasure():
    global resources_collected
    set_event("Events/treasure", "You have discovered sunken treasure!")
    
    resources_collected.append("treasure")

def fish():
    global moves_per_turn
    set_event("Events/fish", "Fishing has yielded better than normal hauls lately. Your crew is well fed, so you gain " + \
            "1 move per turn.")
            
    moves_per_turn += 1

def check_game_over():
    """ helper method to check if win or lose conditions have been met """
    global num_turns, dialog_q
    
    if set(winning_spices).issubset(set(spices_collected)):
        num_turns = 0
        over_msg = "You have collected all the required spices! Your riches will be told in legends for generations to come!"
        set_event("Events/won", over_msg)
        over_dialog = GameOverDialog()
        dialog_q.put(over_dialog)
        
    if num_turns == 0 or moves_per_turn == 0:
        if moves_per_turn == 0:
            num_turns = 0
            over_msg = "You were lucky to be the last survivor of your crew. Now you are dead."
        else:
            over_msg = "You have run out of time. The VOC will not be pleased to hear of your failure."      
        set_event("Events/lost", over_msg)
        over_dialog = GameOverDialog()
        dialog_q.put(over_dialog)

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
    9: lost_at_sea,
    10: lost_at_sea,
    11: treasure,
    12: treasure,
    13: fish
}    

# Helper functions for updating labels and lists
def update_table(element, string):
    """ Adds the specified string to the given GUI table """
    element.add(string)
    element.resize()
    element.repaint()
   
def set_table(element, strings):
    """ Sets the contents of the given GUI table to the specified list of strings """
    element.clear()
    for string in strings:
        element.add(string)
    element.repaint()
    
# Helper function for updating labels and lists
def update_label(element, string):
    """ Sets the contents of the given label to the specified string """
    element.set_text(str(string))
    element.resize()
    element.repaint()

# initial setup tbl
class InitDialog(gui.Dialog):
    """ Dialog that displays when game loads to allow user to choose parameters."""
    def __init__(self,**params):
        global dialog_on
        dialog_on = True
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
        turn_slider = gui.HSlider(value=num_turns,min=2,max=75,size=32,width=175,height=16)
        winit.td(turn_slider)
        turn_slider.connect(gui.CLICK, self.adj_scroll, (0, turn_slider))
        self.turn_label = gui.Label(str(num_turns))
        winit.td(self.turn_label)
        
        winit.tr()
        winit.td(gui.Label("Moves per Turn"))
        move_slider = gui.HSlider(value=moves_per_turn,min=3,max=10,size=32,width=175,height=16)
        winit.td(move_slider)
        move_slider.connect(gui.CLICK, self.adj_scroll, (1, move_slider))
        self.move_label = gui.Label(str(moves_per_turn))
        winit.td(self.move_label)
        
        
        winit.tr()
        winit.td(gui.Label("Spices Needed to Win"))
        spice_slider = gui.HSlider(value=NUM_ISLANDS-2,min=3,max=NUM_ISLANDS+3,size=32,width=175,height=16)
        winit.td(spice_slider)
        spice_slider.connect(gui.CLICK, self.adj_scroll, (2, spice_slider))
        self.spice_label = gui.Label(str(NUM_ISLANDS-2))
        winit.td(self.spice_label)
        
        winit.tr()
        okay_button = gui.Button("Okay")
        okay_button.connect(gui.CLICK,self.confirm)
        winit.td(okay_button)
        
        gui.Dialog.__init__(self, title, winit)
        
    def adj_scroll(self, value):
        """ updates displayed values of scroll bars """
        (num, slider) = value
        if num == 0:
            update_label(self.turn_label, str(slider.value))
        elif num == 1:
            update_label(self.move_label, str(slider.value))
        elif num == 2:
            update_label(self.spice_label, str(slider.value))
    
    def confirm(self):
        """ sets values and exits """
        global ship_name, num_turns, moves_per_turn, dialog_on
        ship_name = str(self.name_input.value)
        num_turns = int(self.turn_label.value)
        moves_per_turn = int(self.move_label.value)
        update_label(ship_label, ship_name)
        update_label(turns_label, num_turns)
        update_label(moves_label, moves_per_turn)
        self.close()
        pygame.display.update()
        # Don't free display immediately; avoid erroneous map clicks
        time.sleep(0.1)
        dialog_on = False

class EventDialog(gui.Dialog):
    """ Dialogs that display when random events occur."""
    def __init__(self,**params):
        global dialog_on
        dialog_on = True
        title = gui.Label("Game Event")
        #width = 200
        #height = 100
        
        doc = gui.Document(width=400)
        space = title.style.font.size(" ")
        
        doc.block(align=1)
        doc.add(gui.Image(event_img),align=-1)
        for word in event_msg.split(" "):
            doc.add(gui.Label(word))
            doc.space(space)
            
        okay_button = gui.Button("Okay")
        okay_button.connect(gui.CLICK,self.confirm)
        doc.add(okay_button)
            
        gui.Dialog.__init__(self,title,doc)
    
    def confirm(self):
        """ sets values and exits """
        global dialog_on
        update_label(turns_label, num_turns)
        update_label(moves_label, moves_per_turn)
        self.close()
        pygame.display.update()
        # Don't free display immediately; avoid erroneous map clicks
        time.sleep(0.1)
        dialog_on = False

class GameOverDialog(gui.Dialog):
    """ Dialogs that display when the game ends, one way or another. """
    def __init__(self, **params):
        global dialog_on
        dialog_on = True
        title = gui.Label("Game Over")
        
        doc = gui.Document(width=400)
        space = title.style.font.size(" ")
        
        doc.block(align=1)
        doc.add(gui.Image(event_img),align=-1)
        for word in event_msg.split(" "):
            doc.add(gui.Label(word))
            doc.space(space)
            
        okay_button = gui.Button("Okay")
        okay_button.connect(gui.CLICK,self.confirm)
        doc.add(okay_button)
        
        #doc.block(align=0)
        
        gui.Dialog.__init__(self,title,doc)
    
    def confirm(self):
        """ sets values and exits """
        global dialog_on
        self.close()
        pygame.display.update()
        # Don't free display immediately; avoid erroneous map clicks
        time.sleep(0.1)
        dialog_on = False
        
class Island:
    """ An object that represents a single island on the map. """
    def __init__(self, name, loc):
        self.name = name
        self.area = pygame.Rect(loc, ISLAND_SIZE)
        self.visited = False
        
    def discovered(self):
        """ Has this island been newly discovered on this trip? """
        return not self.visited
        
    def get_name(self):
        return self.name
        
    def get_area(self):
        return self.area
        
    def contains(self, loc):
        """ Does this island's landmass encompass the coordinates in question? """
        tile_rect = pygame.Rect(loc, MAP_TILE_SIZE)
        return self.area.colliderect(tile_rect)
        
    def visit(self):
        """ Record a visit to this island by the player. """
        self.visited = True
        update_table(islands_table, self.name)
    

# drawing area where the action happens
class DrawingArea(gui.Widget):
    """ A GUI wrapper for the game map display """
    def __init__(self, width, height):
        gui.Widget.__init__(self, width=width, height=height)
        self.image_buffer = pygame.Surface((width, height))

    def paint(self, surf):
        """ Paint whatever has been captured in the buffer """
        surf.blit(self.image_buffer, (0, 0))
        
class MainGui(gui.Desktop):
    """ The main GUI wrapper for our game """

    def make_island_minimaps(self):
        """ Use the island generator to create island minimaps for the game map """
        noise_w = ISLAND_WIDTH / 2
        noise_h = ISLAND_HEIGHT / 2
        noise_f = 3
        noise_o = 3
        minimaps = []
        for _ in range(NUM_ISLANDS):
            world = map.Map('Island', 
                    IslandGenerator().generate_island(noise_w, noise_h, noise_f, noise_o))
            world.draw_minimap()
            minimaps.append(world.minimap)
        # Make sure the number of island minimaps is correct
        assert len(minimaps) == NUM_ISLANDS
        return minimaps
        
    def make_ocean_surface(self):
        """ Create a smooth-looking ocean surface image using varying intensities of blue """
        p = PerlinNoiseGenerator()
        blue_values = np.array(p.generate_noise(ISLAND_WIDTH, ISLAND_HEIGHT, 1.5, 3))
        red_green_values = np.zeros(blue_values.shape, dtype=np.int8)
        red_green_values.fill(25)
        rgb = np.transpose(np.array([red_green_values, red_green_values, blue_values]))
        water = pygame.surfarray.make_surface(rgb)
        return water
        
    def spread_islands(self, num_cols, num_rows):
        """ Pick the desired number of island locations
            such that no two are adjacent
        """
        options = [(x,y) for x in range(num_cols) for y in range(num_rows)]
        clustered = True
        while clustered:
            random.shuffle(options)
            island_positions = options[:NUM_ISLANDS]
            
            free = 0
            for pos in island_positions:
                x, y = pos
                if (x - 1, y) not in island_positions and \
                    (x + 1, y) not in island_positions and \
                    (x, y - 1) not in island_positions and \
                    (x, y + 1) not in island_positions:
                    free += 1
            if free == len(island_positions):
                clustered = False
        # Ensure we have placed the right number of islands
        assert len(island_positions) == NUM_ISLANDS
        return island_positions
        
    def make_game_map(self):
        """ Generate a random game map and initialize the display """
        ship_placed = False
        self.ship_pos = None
        self.islands = []
        
        island_number = 0
        num_cols = MAP_WIDTH / ISLAND_WIDTH
        num_rows = MAP_HEIGHT / ISLAND_HEIGHT
        
        # Ensure the map is big enough
        assert num_cols >= 2
        assert num_rows >= 2
        
        # Pick the desired number of island locations such that no two are adjacent
        island_positions = self.spread_islands(num_cols, num_rows)
        
        # Generate random islands and a water surface to display
        island_minimaps = self.make_island_minimaps()
        water = self.make_ocean_surface()
        
        # Randomize order of map building to randomize initial ship position
        cols = range(num_cols)
        rows = range(num_rows)
        random.shuffle(cols)
        random.shuffle(rows)
        
        for x in cols:
            for y in rows:
                location = (x * ISLAND_WIDTH, y * ISLAND_HEIGHT)
                if (x, y) in island_positions:
                    # Draw island on map
                    minimap = island_minimaps[island_number]
                    self.draw_surface(minimap, location)
                    # Create and store an island object
                    island_name = ISLAND_NAMES[island_number]
                    self.islands.append(Island(island_name, location))
                    island_number += 1
                else:
                    # Draw ocean where there are no islands
                    self.draw_surface(water, location)
                    if not ship_placed:
                        left, top = location
                        self.ship_pos = (left + MARGIN, top + MARGIN)
                        ship_placed = True
                        
        # Capture initial map layout for future redrawing
        self.canvas = pygame.surfarray.array3d(self.game_area.image_buffer)
        
    def load_splashscreen(self, display):
        """ Display a splashscreen while the main game is loading """
        raw_splash_img = pygame.image.load(os.path.join('Images', 'splash.png'))
        splash_img = pygame.transform.smoothscale(raw_splash_img, SCREEN_SIZE)
        # Check for correct resizing
        assert splash_img.get_size() == SCREEN_SIZE
        display.blit(splash_img, (0, 0))
        pygame.display.update()
        
    def make_menu_sidebar(self):
        """ Make a sidebar containing GUI elements reporting game status """
        menu = gui.Table(width=100, height=300, vpadding = 0, hpadding = 2, valign = -1)
        
        # row 1: name of ship
        menu.tr()
        menu.td(ship_label)
        
        # sidebar row 1: tables of spices on hand and spices needed to win
        menu.tr()
        menu.td(gui.Label("Spices you have"))
        menu.td(gui.Label("Spices to win"))
        menu.tr()
        menu.td(spice_table, align=-1, valign=-1)
        set_table(spice_win_table, winning_spices)
        menu.td(spice_win_table, align=-1, valign=-1)

        # row 3: turns left, moves left, and directional controls
        menu.tr()
        menu.td(gui.Label("Turns Left"))
        menu.td(turns_label)
        menu.tr()
        menu.td(gui.Label("Moves Left"))
        menu.td(moves_label)

        # row 4: resource and islands visited tables
        menu.tr()
        menu.td(gui.Label("Resources"))
        menu.td(gui.Label("Islands Visited"))
        menu.tr()
        menu.td(resources_table, align=-1, valign=-1)
        menu.td(islands_table, align=-1, valign=-1)
        return menu
    
    def __init__(self, disp):
        gui.Desktop.__init__(self)
        self.connect(gui.QUIT, self.quit, None)
        
        # Display splashscreen while loading
        self.load_splashscreen(disp)

        # Setup the 'game' area where the action takes place and a sidebar for the menu
        self.game_area = DrawingArea(MAP_WIDTH, MAP_HEIGHT)
        menu = self.make_menu_sidebar()
        
        # set up the overall layout
        tbl = gui.Table(height=disp.get_height())
        tbl.tr()
        tbl.td(menu)
        tbl.td(self.game_area)
        self.init(tbl, disp)
        
        # Load ship image
        raw_ship_img = pygame.image.load(os.path.join('Images', 'sailboat.png'))
        self.ship_img = pygame.transform.smoothscale(raw_ship_img, MAP_TILE_SIZE)
        # Check for correct resizing
        assert self.ship_img.get_size() == MAP_TILE_SIZE
        
        # game setup dialog
        init_dialog = InitDialog()
        self.connect(gui.INIT, init_dialog.open, None)
        
        # Create the main game map
        self.make_game_map()

    def run(self):
        global moves_left, dialog_q
        screen_rect = self.get_map_area()
        
        self.init()
        FPSCLOCK = pygame.time.Clock()
        mouse_x = 0 # used to store x coordinate of mouse event
        mouse_y = 0 # used to store y coordinate of mouse event
        
        # Prevent mouse input to map while dialog boxes are open
        delay_input = True
        
        while True:
            mouse_clicked = False
            map_tile_x, map_tile_y = None, None
            self.draw_pixel_array(self.canvas)
            self.draw_surface(self.ship_img, self.ship_pos)
            while not dialog_q.empty():
                dialog = dialog_q.get()
                dialog.open()
            pygame.display.update()
            
            for event in pygame.event.get(): # event handling loop
                self.event(event)
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    if dialog_on:
                        delay_input = True
                    else:
                        delay_input = False
                elif event.type == MOUSEBUTTONUP:
                    # only get map position if we clicked inside map
                    screen_rect = self.get_map_area()
                    mouse_x, mouse_y = event.pos
                    if mouse_x > screen_rect.x and not dialog_on and not delay_input:
                        mouse_clicked = True
            
            map_tile_x, map_tile_y = self.get_map_tile_at_pixel(mouse_x, mouse_y)
            if map_tile_x != None and map_tile_y != None and not dialog_on and not delay_input and num_turns > 0:
                # The mouse is currently over a box.
                self.highlight_border(map_tile_x, map_tile_y, self.ship_pos, self.canvas)
                left, top = self.map_tile_corner(map_tile_x, map_tile_y)
                if self.is_reachable(left, top, self.ship_pos, self.canvas) and mouse_clicked:
                    # The player has successfully executed a move
                    self.move_ship(left, top)
                    # Report spices collected and update visited islands list
                    nearby = self.nearby_islands(map_tile_x, map_tile_y, self.canvas)
                    if nearby:
                        for island in nearby:
                            self.visit_island(island)
                    else :
                        sea_event_gen = random.randint(0,42)
                        num_resources = len(resources_collected)
    
                        if sea_event_gen < 14 :
                            sea_events[sea_event_gen]()
    
                    check_game_over() # check if the game is over
    
            # Redraw the screen and wait a clock tick.
            self.repaint()
            self.loop()
            FPSCLOCK.tick(FPS)
            
    def move_ship(self, left, top):
        """ Move the ship to the specified destination, redraw the display,
            and adjust the moves and turns remaining accordingly.
        """
        global moves_left, num_turns
        # decrement number of moves by the distance traveled
        moves_left-= self.block_distance(left, top, self.ship_pos)
        # decrement number of turns
        if moves_left == 0:
            moves_left = moves_per_turn
            num_turns-=1
            update_label(turns_label, str(num_turns))
        update_label(moves_label, str(moves_left))
        
        self.ship_pos = (left, top) # move the ship
        self.game_area.repaint()
    
    def visit_island(self, island):
        """ The player has successfully made landfall. Allow them to either
            experience random events, harvest spices from the island, or trade
            resources for spices.
        """
        
        land_event_gen = random.randint(0,22)
        num_resources = len(resources_collected)
        
        if land_event_gen < 11 :
            land_events[land_event_gen]()
            
        if island.discovered():
            island.visit()
            
            spice_no = random.randint(0,9)
            the_spice = SPICE_LIST[spice_no]
            set_event("Spices/"+the_spice, "You collected " + \
                    the_spice+" from " + island.get_name() + ".")
            spices_collected.append(the_spice)
            set_table(spice_table, spices_collected)
                    
        if (num_resources):
            if "treasure" in resources_collected:
                resources_collected.remove("treasure")
                
                spice_no = random.randint(0,9)
                spice_1 = SPICE_LIST[spice_no]
                
                spice_no = random.randint(0,9)
                spice_2 = SPICE_LIST[spice_no]
            
                set_event("Events/treasure", "You are able to purchase " + \
                    spice_1 + " " + spice_2 + " from " + island.get_name() + \
                    " with your treasure.")
                
                spices_collected.append(spice_1)
                spices_collected.append(spice_2)
                set_table(spice_table, spices_collected)
                
            else:
                resource_no = random.randint(0, len(resources_collected) - 1)
                resource = resources_collected[resource_no]
                
                spice_no = random.randint(0,9)
                the_spice = SPICE_LIST[spice_no]
            
                set_event("Spices/" + the_spice, "You are able to trade " + \
                    "your " + resource + " for " + the_spice + "!")
                    
                resources_collected.pop(resource_no)
                set_table(resources_table, resources_collected)
                spices_collected.append(the_spice)
                set_table(spice_table, spices_collected)
    
    def block_distance(self, left, top, ship_pos):
        """ Determine how many blocks away from the ship's current
            position the user's intended destination lies.
        """
        destination = np.array([left, top])
        current_location = np.array(ship_pos)
        return int(np.linalg.norm(destination - current_location) / np.linalg.norm(np.array(MAP_TILE_SIZE)))
    
    def is_reachable(self, left, top, ship_pos, canvas):
        """ Determine whether or not the user's intended destination
            is a navigable marine tile that is also within reach considering
            the range of the ship in the current turn.
        """
        slice = canvas[left:left+39,top:top+39, :-1]
        dist = self.block_distance(left, top, ship_pos)
        return (left, top) != ship_pos and dist <= moves_left and not self.is_island(slice)
    
    def is_island(self, slice):
        """ Determine from a pixel array slice whether or not a part
            of the map belongs to an island minimap.
        """
        return np.sum(slice != BG_COLOR_LEVEL) > 3 * np.size(slice) / 8
    
    def nearby_islands(self, x, y, canvas):
        """ List all islands neighboring the square in question """
        islands_here = []
        for map_tile_x in range(max(0, x-1), min(MAP_COLUMNS, x + 2)):
            for map_tile_y in range(max(0, y-1), min(MAP_ROWS, y + 2)):
                if (map_tile_x == x or map_tile_y == y) :
                    (left, top) = self.map_tile_corner(map_tile_x, map_tile_y)
                    slice = canvas[left:left+39,top:top+39, :-1]
                    if self.is_island(slice):
                        for island in self.islands:
                            if island.contains((left, top)):
                                islands_here.append(island)
        return islands_here
    
    def highlight_border(self, map_tile_x, map_tile_y, ship_pos, canvas):
        """ Draw a border around the square that the user's cursor is hovering over
            with a color corresponding to its status as a navigable marine target,
            reachable island port, or an unaccessible destination.
        """
        color = None
        left, top = self.map_tile_corner(map_tile_x, map_tile_y)
        if (left, top) == ship_pos:
            color = WHITE
        elif self.is_reachable(left, top, ship_pos, canvas):
            if self.nearby_islands(map_tile_x, map_tile_y, canvas):
                color = GREEN
            else:
                color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(self.game_area.image_buffer, color, 
                (left - 5, top - 5, MAP_TILE_WIDTH + 10, MAP_TILE_HEIGHT + 10), 4)
        return

    def map_tile_corner(self, map_tile_x, map_tile_y):
        """ Report the pixel coordinates of the top-left corner of the
            specified tile of the game map.
        """
        # Convert board coordinates to pixel coordinates
        left = map_tile_x * MAP_TILE_WIDTH + MARGIN
        top = map_tile_y * MAP_TILE_HEIGHT + MARGIN
        return (left, top) 

    def get_map_tile_at_pixel(self, x, y):
        """ Report the indices of the map tile, if any, overlapping
            with the specified pixel position
        """
        screen_rect = self.get_map_area()
        for map_tile_x in range(MAP_COLUMNS):
            for map_tile_y in range(MAP_ROWS):
                loc = self.map_tile_corner(map_tile_x, map_tile_y)
                tile_rect = pygame.Rect(loc, MAP_TILE_SIZE)
                if tile_rect.collidepoint(x - screen_rect.x, y - screen_rect.y):
                    return (map_tile_x, map_tile_y)
        return (None, None)
    
    def get_map_area(self):
        """ Report the bounding box of the game map within the display """
        return self.game_area.get_abs_rect()
        
    def draw_surface(self, surf, pos):
        """ Layer the desired image surface onto the display at the specified pixel position. """
        self.game_area.image_buffer.blit(surf, pos)
        
    def draw_pixel_array(self, canvas):
        """ Layer the desired pixel array onto the display at the specified pixel position. """
        pygame.surfarray.blit_array(self.game_area.image_buffer, canvas)

def main():
    pygame.init()
    disp = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Spice Islands')
    gui = MainGui(disp)
    gui.run()

if __name__ == '__main__':
    main()  
    
