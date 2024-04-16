#######################################################
#### MazeGame uses a grid of rows X cols to demonstrate
#### pathfinding using A*.
####
#### AI, Spring 2024
#######################################################
import re
import sys
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
from queue import PriorityQueue


######################################################

#### A cell stores f(), g() and h() values
#### A cell is either open or part of a wall
######################################################

class Cell:
    #### Initially, arre maze cells have g() = inf and h() = 0
    def __init__(self, x, y, is_wall=False):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None
        self.ward = None
        self.priority = None

    #### Compare two cells based on their evaluation functions
    def __lt__(self, other):
        return self.f < other.f


######################################################
# A maze is a grid of size rows X cols
######################################################
class MazeGame:
    def __init__(self, root, maze, wards, input_file):
        self.root = root
        self.maze = maze
        self.wards = wards
        self.alg, self.start_pos, self.goal_pos_list = self.parse_input_file(input_file)

        self.rows = len(maze)
        self.cols = len(maze[0])
        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        #### Assign ward to each cell
        for x in range(self.rows):
            for y in range(self.cols):
                self.cells[x][y].ward = self.wards[x][y]

        #### Assign priority to each cell
        for x in range(self.rows):
            for y in range(self.cols):
                currentWard = self.cells[x][y].ward
                if currentWard == 'c' or currentWard == 'e' or currentWard == 'o' or currentWard == 'b':
                    self.cells[x][y].priority = 5
                elif currentWard == 'm' or currentWard == 's':
                    self.cells[x][y].priority = 4
                elif currentWard == 'h' or currentWard == 'p':
                    self.cells[x][y].priority = 3
                elif currentWard == 'd' or currentWard == 'g':
                    self.cells[x][y].priority = 2
                elif currentWard == 'a' or currentWard == 'i':
                    self.cells[x][y].priority = 1
                else:
                    self.cells[x][y].priority = 0

        #### TODO: add mock data to test
        self.destinations = PriorityQueue()
        self.goals_left = []
        self.goals_complete = []

        #### Start state: (0,0) or top left
        # self.agent_pos = (3, 5)

        # #### Goal state:  (rows-1, cols-1) or bottom right
        # ## other test data examples that worked 20, 15    14, 6      17, 25
        # self.goal_pos = (3, 5)
        # self.goal_pos1 = (20, 15)
        # self.goal_pos2 = (14, 6)
        # self.goal_pos3 = (16, 5)
        # self.goal_pos4 = (17, 8)
        #
        # #self.goal_test = (self.cells[self.goal_pos[0]][self.goal_pos[1]].priority, self.goal_pos)
        # self.destinations.put((-self.cells[self.goal_pos1[0]][self.goal_pos1[1]].priority, self.goal_pos1))
        # self.destinations.put((-self.cells[self.goal_pos2[0]][self.goal_pos2[1]].priority, self.goal_pos2))
        # self.destinations.put((-self.cells[self.goal_pos3[0]][self.goal_pos3[1]].priority, self.goal_pos3))
        # self.destinations.put((-self.cells[self.goal_pos4[0]][self.goal_pos4[1]].priority, self.goal_pos4))
        #
        #
        # self.goals_left.append(self.goal_pos1)
        # self.goals_left.append(self.goal_pos2)
        # self.goals_left.append(self.goal_pos3)
        # self.goals_left.append(self.goal_pos4)
        #
        # #### Start state's initial values for f(n) = g(n) + h(n)
        # self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        # self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos, self.alg)
        # self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos, self.alg)

        #### The maze cell size in pixels
        self.cell_size = 25
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        self.draw_maze()

        ### Testing
        self.agent_pos = self.start_pos

        for goal_pos in self.goal_pos_list:
            self.goal_pos = goal_pos

            # Update goal test and destinations for each goal position
            self.goal_test = (self.cells[self.goal_pos[0]][self.goal_pos[1]].priority, self.goal_pos)
            self.destinations.put((-self.cells[self.goal_pos[0]][self.goal_pos[1]].priority, self.goal_pos))
            self.goals_left.append(goal_pos)

            # Reset agent position and calculate heuristic
            self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
            self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos, self.alg)
            self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos, self.alg)

        #### Create a loop to allow for multiple goal states and paths to be found
        #### TODO: test wards are picked before priority
        while not self.destinations.empty():
            # check list of goals left to see if any are in the same ward first
            for x in self.goals_left:
                if self.cells[x[0]][x[1]].ward == self.cells[self.agent_pos[0]][self.agent_pos[1]].ward:
                    #self.priority = self.cells[x[0]][x[1]].priority
                    self.goal_pos = x
                    break

            # goal position not updated, need to move to priority queue for next goal position
            if self.goal_pos == self.agent_pos:
                self.priority, self.goal_pos = self.destinations.get()
                for x in self.goals_complete:
                    if x == self.goal_pos:
                        # already completed goal
                        _, self.goal_pos = self.destinations.get()

            #self.priority, self.goal_pos = self.destinations.get()
            print(self.cells[self.goal_pos[0]][self.goal_pos[1]].priority, self.cells[self.goal_pos[0]][self.goal_pos[1]].ward, self.goal_pos)

            #### Display the optimum path in the maze
            self.find_path()

            # adds the goal to goals complete list and removes from goals left
            self.goals_left.remove(self.goal_pos)
            self.goals_complete.append(self.goal_pos)

            ## sets the new current position to the goal position since the path has been found
            self.agent_pos = self.goal_pos
        self.find_path()

        #print(self.cells[25][25].priority)
        #print(self.cells[14][6].priority)
        #print(self.cells[7][25].priority)

    # Read from input file
    def parse_input_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # Save algorithm
            self.alg = lines[0].split(":")[1].strip()
            self.start_pos_str = lines[1].split(":")[1].strip()
            self.start_pos = tuple(map(int, self.start_pos_str.strip('()').split(',')))
            self.delivery_locations_str = lines[2].split(":")[1].strip()
            self.goal_pos = re.findall(r'\((\d+),\s*(\d+)\)', self.delivery_locations_str)
            self.goal_pos = [(int(x), int(y)) for x, y in self.goal_pos]
            return self.alg, self.start_pos, self.goal_pos

    ############################################################
    #### This is for the GUI part. No need to modify this unless
    #### GUI changes are needed.
    ############################################################
    def draw_maze(self):
        for x in range(self.rows):
            for y in range(self.cols):
                cell_color = 'white'  # Default color for cells


                # Assign colors based on ward
                ward = self.cells[x][y].ward
                if ward == 'm':
                    cell_color = 'lightblue'
                elif ward == 'g':
                    cell_color = 'firebrick'
                elif ward == 'e':
                    cell_color = 'yellow'
                elif ward == 'a':
                    cell_color = 'grey'
                elif ward == 'i':
                    cell_color = 'powderblue'
                elif ward == 'o':
                    cell_color = 'forestgreen'
                elif ward == 'b':
                    cell_color = 'mediumpurple'
                elif ward == 'p':
                    cell_color = 'yellowgreen'
                elif ward == 's':
                    cell_color = 'lightcoral'
                elif ward == 'd':
                    cell_color = 'olivedrab'
                elif ward == 'c':
                    cell_color = 'sandybrown'
                elif ward == 'h':
                    cell_color = 'chocolate'

                if self.cells[x][y].is_wall:
                    cell_color = 'black'  # Wall color
                self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                             (x + 1) * self.cell_size, fill=cell_color)
                if not self.cells[x][y].is_wall:
                    text = f'g={self.cells[x][y].g}\nh={self.cells[x][y].h}'
                    self.canvas.create_text((y + 0.5) * self.cell_size, (x + 0.5) * self.cell_size, font=("Purisa", 12),
                                            text=text)


    ############################################################
    #### Manhattan distance
    ############################################################
    def heuristic(self, pos, alg):
        if (alg == "astar"):
            # A Star uses heuristics and actual path cost
            current_cell = self.goal_pos
            return (abs(pos[0] - current_cell[0]) + abs(pos[1] - current_cell[1]))
        else:
            # Dijkstra uses just actual path cost so heuristics should be 0
            return 0



    ############################################################
    #### A* Algorithm
    ############################################################
    def find_path(self):
        ##self.priority, self.goal_pos = self.destinations.get()
            open_set = PriorityQueue()

            #### Add the start state to the queue
            open_set.put((0, self.agent_pos))

            #### Continue exploring until the queue is exhausted
            while not open_set.empty():
                current_cost, current_pos = open_set.get()
                current_cell = self.cells[current_pos[0]][current_pos[1]]

                #### Stop if goal is reached
                if current_pos == self.goal_pos:
                    self.reconstruct_path()
                    break

                #### Agent goes E, W, N, and S, whenever possible
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    new_pos = (current_pos[0] + dx, current_pos[1] + dy)

                    if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and not self.cells[new_pos[0]][
                        new_pos[1]].is_wall:

                        #### The cost of moving to a new position is 1 unit
                        new_g = current_cell.g + 1

                        if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                            ### Update the path cost g()
                            self.cells[new_pos[0]][new_pos[1]].g = new_g

                            ### Update the heurstic h()
                            # TODO: filled with astar alg for now, will need to update once file input complete
                            self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos, "astar")

                            ### Update the evaluation function for the cell n: f(n) = g(n) + h(n)
                            self.cells[new_pos[0]][new_pos[1]].f = new_g + self.cells[new_pos[0]][new_pos[1]].h
                            self.cells[new_pos[0]][new_pos[1]].parent = current_cell

                            #### Add the new cell to the priority queue
                            open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))
            #self.agent_pos = self.goal_pos

    ############################################################
    #### This is for the GUI part. No need to modify this unless
    #### screen changes are needed.
    ############################################################
    def reconstruct_path(self):
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        while current_cell.parent:
            x, y = current_cell.x, current_cell.y
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill='green')
            current_cell = current_cell.parent
            print(current_cell.x, current_cell.y)

            # Redraw cell with updated g() and h() values
            color = 'darkblue'
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill=color)
            text = f'g={self.cells[x][y].g}\nh={self.cells[x][y].h}'
            self.canvas.create_text((y + 0.5) * self.cell_size, (x + 0.5) * self.cell_size, font=("Purisa", 12),
                                    text=text)

    ############################################################
    #### This is for the GUI part. No need to modify this unless
    #### screen changes are needed.
    ############################################################
    def move_agent(self, event):

        #### Move right, if possible
        if event.keysym == 'Right' and self.agent_pos[1] + 1 < self.cols and not self.cells[self.agent_pos[0]][
            self.agent_pos[1] + 1].is_wall:
            self.agent_pos = (self.agent_pos[0], self.agent_pos[1] + 1)

        #### Move Left, if possible
        elif event.keysym == 'Left' and self.agent_pos[1] - 1 >= 0 and not self.cells[self.agent_pos[0]][
            self.agent_pos[1] - 1].is_wall:
            self.agent_pos = (self.agent_pos[0], self.agent_pos[1] - 1)

        #### Move Down, if possible
        elif event.keysym == 'Down' and self.agent_pos[0] + 1 < self.rows and not self.cells[self.agent_pos[0] + 1][
            self.agent_pos[1]].is_wall:
            self.agent_pos = (self.agent_pos[0] + 1, self.agent_pos[1])

        #### Move Up, if possible
        elif event.keysym == 'Up' and self.agent_pos[0] - 1 >= 0 and not self.cells[self.agent_pos[0] - 1][
            self.agent_pos[1]].is_wall:
            self.agent_pos = (self.agent_pos[0] - 1, self.agent_pos[1])

        #### Erase agent from the previous cell at time t
        self.canvas.delete("agent")

        ### Redraw the agent in color navy in the new cell position at time t+1
        self.canvas.create_rectangle(self.agent_pos[1] * self.cell_size, self.agent_pos[0] * self.cell_size,
                                     (self.agent_pos[1] + 1) * self.cell_size, (self.agent_pos[0] + 1) * self.cell_size,
                                     fill='navy', tags="agent")


############################################################
#### Modify the wall cells to experiment with different maze
#### configurations.
############################################################
## used for walls
maze = [
	[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
	[1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
	[1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1],
	[1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
	[1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
	[1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
	[1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1],
	[1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
	[1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
	[1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
	[1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1],
	[0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
	[0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
	[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
]

## used for assigning wards
floor_plan = [
	[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 1, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 1, 0, 0, 0, 0, 0, 0, 0],
	[1, 1, 1, 'm', 0, 'm', 'm', 'g', 'm', 'm', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 1, 1, 1, 1, 1, 1, 1, 1],
	[1, 0, 0, 0, 0, 0, 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 0, 0, 'e', 'e', 'e', 'a', 'a', 1],
	[1, 0, 0, 0, 'i', 'i', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1],
	[1, 0, 0, 0, 0, 'i', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1],
	[1, 0, 0, 0, 0, 'i', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1],
	[1, 0, 0, 0, 0, 0, 0, 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'e', 'i', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1],
	[1, 0, 0, 0, 'o', 'o', 'o', 'o', 'g', 'g', 'g', 'g', 'b', 'g', 'g', 'g', 'g', 'g', 'g', 'e', 'i', 'i', 'i', 0, 'c', 'a', 'a', 'a', 'a', 1],
	[1, 0, 0, 0, 'o', 'o', 'o', 'o', 'g', 'g', 'g', 'g', 'b', 'g', 'g', 'g', 'g', 'g', 'g', 'e', 'o', 'e', 'e', 0, 'c', 'a', 'a', 'a', 'a', 1],
	[1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 'e', 'o', 'e', 'e', 0, 'c', 'c', 'c', 'c', 'c', 1],
	[1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 'g', 'e', 'o', 'o', 'o', 0, 'c', 'c', 'c', 'c', 'c', 1],
	[1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'o', 'o', 'o', 0, 'c', 'c', 'c', 'c', 'c', 1],
	[1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 0, 0, 'i', 'o', 'o', 'o', 0, 'c', 'c', 'c', 'c', 'c', 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'c', 'c', 'c', 'c', 1],
	[1, 1, 1, 0, 0, 'i', 'o', 'o', 'a', 'a', 'a', 'a', 'h', 'h', 'h', 'h', 'h', 0, 's', 's', 's', 'o', 'o', 0, 'o', 'o', 'o', 'o', 1, 1],
	[0, 0, 1, 0, 0, 'o', 'o', 'o', 'a', 'a', 'a', 'a', 'h', 'h', 'h', 'h', 'h', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0],
	[0, 0, 1, 0, 0, 'o', 'o', 'o', 'o', 'o', 'p', 'h', 'h', 'h', 'h', 'h', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0],
	[0, 0, 1, 0, 0, 'o', 'o', 'o', 'o', 'o', 'p', 'h', 'h', 'h', 'h', 'h', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0],
	[0, 0, 1, 0, 0, 'o', 'o', 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0],
	[0, 0, 1, 0, 0, 'o', 'o', 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'p', 'p', 'o', 'o', 1, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 's', 's', 's', 's', 's', 's', 's', 's', 's', 1, 0],
	[0, 0, 1, 0, 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 's', 'd', 'd', 's', 's', 's', 's', 1, 0],
	[0, 0, 1, 0, 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 'd', 'd', 'd', 's', 's', 's', 's', 1, 0],
	[0, 0, 1, 0, 0, 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 'd', 'd', 'd', 's', 's', 's', 's', 1, 0],
	[0, 0, 1, 'i', 'i', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 'd', 'd', 'd', 's', 's', 's', 's', 1, 0],
	[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
]


############################################################
#### The mainloop activates the GUI.
############################################################
root = tk.Tk()
root.title("A* Maze")

input_file = sys.argv[1]
game = MazeGame(root, maze, floor_plan, input_file)
root.bind("<KeyPress>", game.move_agent)

root.mainloop()



