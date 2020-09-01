import pygame
import math
from queue import PriorityQueue

# Using a box screen, so width and height are the same
WIDTH = 1000

screen = pygame.display.set_mode((WIDTH, WIDTH))
title = pygame.display.set_caption("Personal Project")

# RGB values for different colors
# Taken from https://www.rapidtables.com/web/color/RGB_Color.html
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (127, 0, 255)
GRAY = (128, 128, 128)



# Nodes in our grid
# Keeps track of where it is, what row/col pos, width, each neighbor node, and color of each node
class Node:
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col
        self.width = width
        self.totalRows = totalRows

        # Determines the position of node
        self.x = row * width
        self.y = col * width

        # Set default as color as white
        self.color = WHITE


        self.neighbors = []

    #
    def getPos(self):
        return self.row, self.col

    # checks if we already looked/considered the node
    def checked(self):
        return self.color == YELLOW

    def notChecked(self):
        return self.color == GREEN


    def walls(self):
        return self.color == BLACK

    def start(self):
        return self.color == BLUE

    def end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    # Changes the Node to its respected color
    def changeChecked(self):
        self.color = YELLOW

    def changeNotChecked(self):
        self.color = GREEN

    def changeWalls(self):
        self.color = BLACK

    def changeStart(self):
        self.color = BLUE

    def changeEnd(self):
        self.color = PURPLE

    def makePath(self):
        self.color = RED

    # Draws node in its given position
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbors(self, grid):
        self.neighbors = []

        # Checks the position of the neighbors and makes sure that it is not a wall. Then append it to neighbors
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].walls(): #DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].walls(): #UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].walls(): #RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].walls():  #LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    # Compares 2 nodes


# Outlines the shortest path
def quickestPath(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.makePath()
        draw()

# the A* algorithm expands the node with the lowest value of g(n) + h(n)
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {box: float("inf") for row in grid for box in row}
    g_score[start] = 0
    h_score = {box: float("inf") for row in grid for box in row}
    h_score[start] = heuristic(start.getPos(), end.getPos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            quickestPath(came_from, end, draw)
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                h_score[neighbor] = temp_g_score + heuristic(neighbor.getPos(), end.getPos())

                if neighbor not in open_set_hash:
                    count +=1
                    open_set.put((h_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.changeChecked()
        draw()
        if current != start:
            current.changeNotChecked()
    return False

# Estimates whether or not we are close to the goal,
# It ignores all walls using the Manhattan distance
def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Draws the grid lines
def drawGrid(screen, rows, width):
    size = width // rows

    for i in range(rows):
        pygame.draw.line(screen, GRAY, (0, i*size), (width, i*size))
        for j in range(rows):
            pygame.draw.line(screen, GRAY, (j * size, 0), (j * size, width))

# Creates the grid and nodes for each box
# Creates a bunch of lists inside lists that store nodes
def makeGrid(rows, width):
    grid = []

    # size of each box in grid
    size = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, size, rows)
            grid[i].append(node)

    return grid

# Fills each box with a color
def draw(screen, grid, rows, width):
    screen.fill(WHITE)
    for row in grid:
        for box in row:
            box.draw(screen)
    drawGrid(screen, rows, width)
    pygame.display.update()

# Takes the position of the node the mouse clicked
def clicked(pos, rows, width):
    size = width // rows
    y, x = pos

    row = y // size
    col = x // size

    return row, col

def main(screen, width):
    # Determines dimensions of the grid
    # Will break if row is "NOT" a factor of the width/height
    ROWS = 50

    grid = makeGrid(ROWS, width)

    # Does not choose a start and end point automatically
    start = None
    end = None

    run = True
    started = False

    while run:
        draw(screen, grid, ROWS, width)

        # Closes the game via X
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Will not let User click on grid while it is running
            if started:
                continue

            # When User clicks left mouse button
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()

                row, col = clicked(pos, ROWS, width)
                box = grid[row][col]

                # Lets you pick your starting point
                if not start and box != end:
                    start = box
                    start.changeStart()

                # Lets you choose end point
                elif not end and box != start:
                    end = box
                    end.changeEnd()

                # Lets you draw walls after you pick the start and end point
                elif box != end and box != start:
                    box.changeWalls()

            # Clears the block with right click
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = clicked(pos, ROWS, width)
                box = grid[row][col]

                box.reset()
                if box == start:
                    start = None
                if box == end:
                    end = None

            # Starts the algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for box in row:
                            box.updateNeighbors(grid)

                    algorithm(lambda: draw(screen, grid, ROWS, width), grid, start, end)

                # Resets the grid on Escape
                if event.key == pygame.K_ESCAPE:
                    start = None
                    end = None
                    grid = makeGrid(ROWS, width)





    pygame.quit()


main(screen, WIDTH)