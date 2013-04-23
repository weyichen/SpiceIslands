# Spice Islands
# A game by Daniel (Yichen[g]) Wei and Anand Sundaram

import random, pygame, sys, os
from pygame.locals import *
import map
from perlin_noise import *
from island_generator import *
import numpy as np

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

def isReachable(left, top, ship_pos, canvas):
    slice = canvas[left:left+39,top:top+39, :-1]
    destination = np.array([left, top])
    current_location = np.array(ship_pos)
    dist = np.linalg.norm(destination - current_location)
    return dist < 100 and not (slice > 25).any()

def drawHighlightBox(boxx, boxy, ship_pos, canvas):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    if isReachable(left, top, ship_pos, canvas):
        pygame.draw.rect(DISPLAYSURF, GREEN, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
    else:
        pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)
    return

def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * BOXSIZE + MARGIN
    top = boxy * BOXSIZE + MARGIN
    return (left, top) 

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Spice Islands')

    firstSelection = None # stores the (x, y) of the first box clicked.

    DISPLAYSURF.fill(BGCOLOR)
 
    noise_w = 40
    noise_h = 40
    noise_f = 1
    noise_o = 5
    
    p = PerlinNoiseGenerator()
    
    raw_ship_img = pygame.image.load(os.path.join('Images', 'sailboat.png'))
    ship_img = pygame.transform.smoothscale(raw_ship_img, (40, 40))
    
    shipPlaced = False
    ship_pos = None
    
    for x in range(4):
        for y in range(3):
            world = map.Map('Island',
            IslandGenerator().generate_island(noise_w, noise_h, noise_f, noise_o))
            if random.randint(1,3) > 1 and (x + y) % 2 == 0:
                world.map = IslandGenerator().generate_island(noise_w, noise_h, noise_f, noise_o)
                world.draw_minimap()
                DISPLAYSURF.blit(world.minimap, (x * 160, y * 160))
            else:
                noise = np.array(p.generate_noise(4*noise_w,4*noise_h,noise_f, noise_o))
                rg = np.zeros(noise.shape, dtype=np.int8)
                rg.fill(25)
                bg = np.transpose(np.array([rg, rg, noise]))
                s = pygame.surfarray.make_surface(bg)
                DISPLAYSURF.blit(s, (x * 160, y* 160))
                if not shipPlaced:
                    ship_pos = (x * 160 + 20, y * 160 + 20)
                    shipPlaced = True
    
    canvas = pygame.surfarray.array3d(DISPLAYSURF)
    
    while True: # main game loop
        mouseClicked = False
        pygame.surfarray.blit_array(DISPLAYSURF,canvas)
        DISPLAYSURF.blit(ship_img, ship_pos)
        
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            drawHighlightBox(boxx, boxy, ship_pos, canvas)
            # The mouse is currently over a box.
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if isReachable(left, top, ship_pos, canvas) and mouseClicked:
                    ship_pos = (left, top) # move the ship
        
        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        pygame.display.flip()
        FPSCLOCK.tick(FPS)
             
if __name__ == '__main__':
 main()