#######################################################
#### MazeGame uses a grid of rows X cols to demonstrate
#### pathfinding using A*.
####
#### AI, Spring 2024
#######################################################
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

    #### Compare two cells based on their evaluation functions
    def __lt__(self, other):
        return self.f < other.f


######################################################
# A maze is a grid of size rows X cols
######################################################
class MazeGame:
    def __init__(self, root, maze):
        self.root = root
        self.maze = maze

        self.rows = len(maze)
        self.cols = len(maze[0])

        #### Start state: (0,0) or top left
        self.agent_pos = (0, 0)

        #### Goal state:  (rows-1, cols-1) or bottom right
        self.goal_pos = (self.rows - 1, self.cols - 1)

        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        #### Start state's initial values for f(n) = g(n) + h(n)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos)

        #### The maze cell size in pixels
        self.cell_size = 75
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        self.draw_maze()

        #### Display the optimum path in the maze
        self.find_path()

    ############################################################
    #### This is for the GUI part. No need to modify this unless
    #### GUI changes are needed.
    ############################################################
    def draw_maze(self):
        for x in range(self.rows):
            for y in range(self.cols):
                ## do the dx dy from find path here to get any missing NWSE connections
                color = 'maroon' if self.maze[x][y] == 1 else 'white'
                self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                             (x + 1) * self.cell_size, fill=color)
                if not self.cells[x][y].is_wall:
                    text = f'g={self.cells[x][y].g}\nh={self.cells[x][y].h}'
                    self.canvas.create_text((y + 0.5) * self.cell_size, (x + 0.5) * self.cell_size, font=("Purisa", 12),
                                            text=text)

        #### Load the animated GIF
        #### Use this site to resize/crop/recolor gif images: https://ezgif.com/
        gif_path = "images/ghost.gif"
        gif = Image.open(gif_path)

        #### Maze/screen locations of the ghost
        x, y = 1, 5
        xx, yy = x * self.cell_size, y * self.cell_size

        #### Create a function to animate the GIF
        def animate(frame_num=0):
            gif.seek(frame_num)
            frame = ImageTk.PhotoImage(gif)
            self.canvas.create_image(xx, yy, anchor=tk.NW, image=frame, tag="image")
            frame_num = (frame_num + 1) % gif.n_frames
            self.canvas.after(100, animate, frame_num)

            #### Keep a reference to the frame to prevent it from being garbage collected
            animate.frame = frame

        #### Start the animation
        animate()

    ############################################################
    #### Manhattan distance
    ############################################################
    def heuristic(self, pos):
        return (abs(pos[0] - self.goal_pos[0]) + abs(pos[1] - self.goal_pos[1]))

    ############################################################
    #### A* Algorithm
    ############################################################
    def find_path(self):
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
                        self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos)

                        ### Update the evaluation function for the cell n: f(n) = g(n) + h(n)
                        self.cells[new_pos[0]][new_pos[1]].f = new_g + self.cells[new_pos[0]][new_pos[1]].h
                        self.cells[new_pos[0]][new_pos[1]].parent = current_cell

                        #### Add the new cell to the priority queue
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))

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

            # Redraw cell with updated g() and h() values
            self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size, (y + 1) * self.cell_size,
                                         (x + 1) * self.cell_size, fill='skyblue')
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


floor_plan = [
	0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 1, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 1, 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 1, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 1, 'm', 0, 'm', 'm', 'g', 'm', 'm', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 1, 1, 1, 1, 1, 1, 1, 1,
	1, 0, 0, 0, 0, 0, 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 0, 0, 'e', 'e', 'e', 'a', 'a', 1,
	1, 0, 0, 0, 'i', 'i', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1,
	1, 0, 0, 0, 0, 'i', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1,
	1, 0, 0, 0, 0, 'i', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1,
	1, 0, 0, 0, 0, 0, 0, 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'e', 'i', 'i', 'i', 0, 'e', 'e', 'e', 'a', 'a', 1,
	1, 0, 0, 0, 'o', 'o', 'o', 'o', 'g', 'g', 'g', 'g', 'b', 'g', 'g', 'g', 'g', 'g', 'g', 'e', 'i', 'i', 'i', 0, 'c', 'a', 'a', 'a', 'a', 1,
	1, 0, 0, 0, 'o', 'o', 'o', 'o', 'g', 'g', 'g', 'g', 'b', 'g', 'g', 'g', 'g', 'g', 'g', 'e', 'o', 'e', 'e', 0, 'c', 'a', 'a', 'a', 'a', 1,
	1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 'e', 'o', 'e', 'e', 0, 'c', 'c', 'c', 'c', 'c', 1,
	1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 'g', 'e', 'o', 'o', 'o', 0, 'c', 'c', 'c', 'c', 'c', 1,
	1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 'g', 'g', 'i', 'o', 'o', 'o', 0, 'c', 'c', 'c', 'c', 'c', 1,
	1, 0, 0, 0, 'o', 'o', 'o', 'o', 'b', 'b', 'b', 'b', 'b', 'g', 'g', 'g', 'g', 0, 0, 'i', 'o', 'o', 'o', 0, 'c', 'c', 'c', 'c', 'c', 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'c', 'c', 'c', 'c', 1,
	1, 1, 1, 0, 0, 'i', 'o', 'o', 'a', 'a', 'a', 'a', 'h', 'h', 'h', 'h', 'h', 0, 's', 's', 's', 'o', 'o', 0, 'o', 'o', 'o', 'o', 1, 1,
	0, 0, 1, 0, 0, 'o', 'o', 'o', 'a', 'a', 'a', 'a', 'h', 'h', 'h', 'h', 'h', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0,
	0, 0, 1, 0, 0, 'o', 'o', 'o', 'o', 'o', 'p', 'h', 'h', 'h', 'h', 'h', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0,
	0, 0, 1, 0, 0, 'o', 'o', 'o', 'o', 'o', 'p', 'h', 'h', 'h', 'h', 'h', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0,
	0, 0, 1, 0, 0, 'o', 'o', 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 1, 0,
	0, 0, 1, 0, 0, 'o', 'o', 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 0, 's', 's', 's', 'o', 'o', 'o', 'p', 'p', 'o', 'o', 1, 0,
	0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 's', 's', 's', 's', 's', 's', 's', 's', 's', 1, 0,
	0, 0, 1, 0, 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 's', 'd', 'd', 's', 's', 's', 's', 1, 0,
	0, 0, 1, 0, 'o', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 'd', 'd', 'd', 's', 's', 's', 's', 1, 0,
	0, 0, 1, 0, 0, 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 'd', 'd', 'd', 's', 's', 's', 's', 1, 0,
	0, 0, 1, 'i', 'i', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 's', 'd', 'd', 'd', 'd', 's', 's', 's', 's', 1, 0,
	0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
]


############################################################
#### The mainloop activates the GUI.
############################################################
root = tk.Tk()
root.title("A* Maze")

game = MazeGame(root, floor_plan)
root.bind("<KeyPress>", game.move_agent)

root.mainloop()



