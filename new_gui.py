"""<title>Containers and more Connections</title>
A container is added, and centered a button within that
container.
"""
import pygame
import spiceIslands
from pygame.locals import *

# the following line is not needed if pgu is installed
import sys; sys.path.insert(0, "pgu")
from pgu import gui # TODO: figure out how to install pgu

# global variable settings
SHIPNAME = "SANTA MARIA"
NUMTURNS = 30
MOVESPTURN = 5

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
    def __init__(this, width, height):
        gui.Widget.__init__(this, width=width, height=height)
        this.imageBuffer = pygame.Surface((width, height))

    def paint(this, surf):
        # Paint whatever has been captured in the buffer
        surf.blit(this.imageBuffer, (0, 0))

    # Call this function to take a snapshot of whatever has been rendered
    # onto the display over this widget.
    def save_background(this):
        disp = pygame.display.get_surface()
        this.imageBuffer.blit(disp, this.get_abs_rect())
        
class MainGui(gui.Desktop):
    gameAreaWidth = 500
    gameArea = None
    menuArea = None

    def __init__(this, disp):
        gui.Desktop.__init__(this)

        # Setup the 'game' area where the action takes place
        this.gameArea = DrawingArea(this.gameAreaWidth,
                                    disp.get_height())
        # Setup the gui area
        this.menuArea = gui.Container(
            width=disp.get_width()-this.gameAreaWidth)
        
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
        tbl.td(this.gameArea)
        
        this.init(tbl, disp)


if __name__ == '__main__':
    disp = pygame.display.set_mode((800,600))
    gui = MainGui(disp)
    gui.run()
    
    
