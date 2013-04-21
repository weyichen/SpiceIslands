import perlin_noise
import random



class IslandGenerator:


    def __init__(self):

        self.map = []
        self.map_width = 0
        self.map_height = 0


    def double_size(self):

        """This function just doubles the size of the map. Making 4 'tiles'
           out of 1, that way when we actually make a walkable world for a
           game, it will be spaced out."""

        new_map = []
        for y in range(0, self.map_height):
            row = []
            for x in range(0, self.map_width):
                row.append(self.map[y][x])
                row.append(self.map[y][x])
            new_map.append(row)
            new_map.append(row)

        self.map = list(new_map)
        self.map_height *= 2
        self.map_width *= 2


    def smoothen(self):

        """A simple blurring function for the map. Gets rid of unwanted
           sharpness such as a single sand tile in the middle of a bunch
           of grass, etc."""

        for y in range(0, self.map_height):
            for x in range(0, self.map_width):
                average = 0.0
                times = 0.0

                if x - 1 >= 0:
                    average += self.map[y][x-1]
                    times += 1
                if x + 1 < self.map_width-1:
                    average += self.map[y][x+1]
                    times += 1
                if y - 1 >= 0:
                    average += self.map[y-1][x]
                    times += 1
                if y + 1 < self.map_height-1:
                    average += self.map[y+1][x]
                    times += 1

                if x - 1 >= 0 and y - 1 >= 0:
                    average += self.map[y-1][x-1]
                    times += 1
                if x + 1 < self.map_width and y - 1 >= 0:
                    average += self.map[y-1][x+1]
                    times += 1
                if x - 1 >= 0 and y + 1 < self.map_height:
                    average += self.map[y+1][x-1]
                    times += 1
                if x + 1 < self.map_width and y + 1 < self.map_height:
                    average += self.map[y+1][x+1]
                    times += 1

                average += self.map[y][x]
                times += 1

                average /= times

                self.map[y][x] = average


    def generate_island(self, width, height, frequency, octaves):


        """Generates the actual island."""


        #Uses perlin noise to generate a random noise map. Everything after
        #this line just masks the random noise to look more like an island.
        self.map = perlin_noise.PerlinNoiseGenerator().generate_noise(width,
                                                                      height,
                                                                      frequency,
                                                                      octaves)
        self.map_width = width
        self.map_height = height

        particle_map = []
        for y in range(0, self.map_height):
            row = []
            for x in range(0, self.map_width):
                row.append(0)
            particle_map.append(row)

        for i in range(0, int((width*height)*(.85))):
            x = random.randint(15, self.map_width-16)
            y = random.randint(15, self.map_height-16)

            for j in range(0, int((width*height)*(0.05))):
                particle_map[y][x] += 7
                if particle_map[y][x] >= 255:
                    particle_map[y][x] == 255
                current_value = particle_map[y][x]
                choices = []
                if x-1 > 0:
                    if particle_map[y][x-1] <= current_value:
                        choices.append("left")
                if x+1 < self.map_width-1:
                    if particle_map[y][x+1] <= current_value:
                        choices.append("right")
                if y-1 > 0:
                    if particle_map[y-1][x] <= current_value:
                        choices.append("up")
                if y+1 < self.map_height-1:
                    if particle_map[y+1][x] <= current_value:
                        choices.append("down")

                if not choices:
                    break;
                
                new = random.choice(choices)
                if new == "left":
                    x -= 1
                elif new == "right":
                    x += 1
                elif new == "up":
                    y -= 1
                elif new == "down":
                    y += 1

        #return particle_map

        for y in range(0, self.map_height):
            for x in range(0, self.map_width):
                self.map[y][x] *= ((particle_map[y][x]) / 255.0)

        self.smoothen()

        return self.map
