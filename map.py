import pygame



class Map:


    def __init__(self, type, map):

        self.type = type
        self.map = map
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.tile_size = 4

        self.waterline = 0
        
        self.minimap = pygame.Surface((self.width * self.tile_size,
                                       self.height * self.tile_size))
        self.draw_minimap()


    def get_waterline(self):

        values = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                values.append(self.map[y][x])
        values.sort()

        return values[int((len(values)-1)*.60)]
        

    def draw_minimap(self):

        self.waterline = self.get_waterline()

        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.map[y][x] > 255.0:
                    self.map[y][x] = 255.0
                tile = int(self.map[y][x])

                if tile <= self.waterline:
                    color = (25, 25, tile+75)
                elif tile > self.waterline and tile <= self.waterline + 10:
                    color = (tile+80, tile+80, 100)
                elif tile > self.waterline + 10 and tile <= self.waterline + 40:
                    color = (0, 255-tile, 0)
                elif tile > self.waterline + 40 and tile <= 190:
                    color = (0, 255-tile, 0)
                elif tile > 190:
                    color = (255-tile, 255-tile, 255-tile)

                #color = (tile, tile, tile)
                
                image = pygame.Surface((self.tile_size, self.tile_size))
                image.fill(color)
                self.minimap.blit(image, (x * self.tile_size,
                                          y * self.tile_size))
