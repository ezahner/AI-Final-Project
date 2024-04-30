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
import time


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
        self.success_flag = False
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
                    self.cells[x][y].priority = -1

        self.destinations = PriorityQueue()
        self.goals_left = []
        self.goals_complete = []
        self.success_goals = []
        self.same_ward_flag = False
        self.path_stack = []

        #### Start state: (0,0) or top left
        # self.agent_pos = (3, 5)

        # #### Goal state:  (rows-1, cols-1) or bottom right
        # ## other test data examples that worked 20, 15    14, 6      17, 25

        #### The maze cell size in pixels
        self.cell_size = 25
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        self.draw_maze()

        #### Begin the path finding process
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

        print(self.goals_left)


        #### Create a loop to allow for multiple goal states and paths to be found
        while not self.destinations.empty():
            # check list of goals left to see if any are in the same ward first
            for x in self.goals_left:
                if self.cells[x[0]][x[1]].ward == self.cells[self.agent_pos[0]][self.agent_pos[1]].ward:
                    self.goal_pos = x
                    self.same_ward_flag = True
                    break

            # goal position not updated, need to move to priority queue for next goal position
            #if self.goal_pos == self.agent_pos:
            if not self.same_ward_flag:
                self.priority, self.goal_pos = self.destinations.get()
                for x in self.goals_complete:
                    if x == self.goal_pos:
                        # already completed goal
                        _, self.goal_pos = self.destinations.get()

            print(self.cells[self.goal_pos[0]][self.goal_pos[1]].priority, self.cells[self.goal_pos[0]][self.goal_pos[1]].ward, self.goal_pos)
            #### Display the optimum path in the maze
            self.find_path()

            # adds the goal to goals complete list and removes from goals left
            #if self.goal_pos in self.goals_left:
            self.goals_left.remove(self.goal_pos)
            self.goals_complete.append(self.goal_pos)
            self.same_ward_flag = False

            ## sets the new current position to the goal position since the path has been found
            self.agent_pos = self.goal_pos
        #self.find_path()

        #### Highlight goal state
        # TODO: make it so it only highlights the successful goals
        for current_cell in self.success_goals:
            x, y = current_cell[0], current_cell[1]
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill="royal blue")


        #### Print out if the robot successfully delivered the needed medications
        if (self.success_flag):
            print("Success finding an optimal path!")
        else:
            print("Failure: unable to find a path to goal states")

        #print(self.cells[25][25].priority)
        #print(self.cells[14][6].priority)
        #print(self.cells[7][25].priority)

        # Read from input file

    def parse_input_file(self, file_path):
        with open(file_path, 'r') as file:
            # Read from file, turn everything to lower case
            lines = [line.strip().lower() for line in file.readlines()]

            # Check if the file is 3 lines long
            if len(lines) < 3:
                raise ValueError("Error: Input file length must be 3 lines")

            # Check if the first line contains the delivery algorithm
            if not (lines[0].startswith("delivery algorithm: astar") or  lines[0].startswith("delivery algorithm: dijkstra")):
                raise ValueError("Error: First line should specify the delivery algorithm")

            # Check if the second line contains the start location
            if not lines[1].startswith("start location:"):
                raise ValueError("Error: Second line should specify the start location")

            # Check if the third line contains delivery locations
            if not lines[2].startswith("delivery locations:"):
                raise ValueError("Error: Third line should specify the delivery locations")

            # Get algorithm
            self.alg = lines[0].split(":")[1].strip()

            # Get start position using regular expression
            start_match = re.match(r'start location:\s*\((\d+),\s*(\d+)\)', lines[1])
            if not start_match:
                raise ValueError("Start location format is incorrect")
            self.start_pos = tuple(map(int, start_match.groups()))

            # Get delivery locations using regular expression
            delivery_match = re.findall(r'\((\d+),\s*(\d+)\)', lines[2])
            if not delivery_match:
                raise ValueError("Delivery locations format is incorrect")
            self.goal_pos = [(int(x), int(y)) for x, y in delivery_match]

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
                # if not self.cells[x][y].is_wall:
                #     text = f'g={self.cells[x][y].g}\nh={self.cells[x][y].h}'
                #     self.canvas.create_text((y + 0.5) * self.cell_size, (x + 0.5) * self.cell_size, font=("Purisa", 12),
                #                             text=text)


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
            print(self.agent_pos, "agent pos")

            #### Continue exploring until the queue is exhausted
            while not open_set.empty():
                current_cost, current_pos = open_set.get()
                current_cell = self.cells[current_pos[0]][current_pos[1]]

                #### Stop if goal is reached
                if current_pos == self.goal_pos and self.goal_pos != self.start_pos:
                    self.reconstruct_path()
                    self.success_flag = True
                    #print(self.goal_pos, "from path find success")
                    self.success_goals.append(self.goal_pos)
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
                            self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos, self.alg)

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
    def draw_path_with_delay(self):
        if self.path_stack:
            current_cell = self.path_stack.pop()
            x, y = current_cell.x, current_cell.y
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill='green')
            self.root.update()  # Update the GUI to show the drawn path
            time.sleep(0.1)  # Add a delay between steps

            # Redraw cell with updated g() and h() values
            color = 'darkblue'
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill=color)
            self.draw_path_with_delay()  # Recursively draw the next step

    def reconstruct_path(self):
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        while current_cell.parent:
            self.path_stack.append(current_cell)
            current_cell = current_cell.parent

        self.draw_path_with_delay()  # Start drawing the path with a delay
    #def draw_path(self):


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
	[0, 0, 1, 0, 0, 'o', 'o', 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0],
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



