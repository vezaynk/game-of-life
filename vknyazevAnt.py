import turtle
import random
import math
from tkinter import Tk, messagebox
# from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askinteger


class Cell:
    def __init__(self, index, state, dish):
        self.index = index
        self.state = state
        self._dish = dish

    def toggle(self):
        self.state = (1-self.state[0], self.state[1])


    def get_next_cell(self):
        # Get top, if not in first row
        # Top cell is a row-worth to the left
        not_top = self.index >= self._dish.width
        top_index = self.index - self._dish.width if not_top else self.index + self._dish.width*(self._dish.height-1)
        top = self._dish.cells[top_index].state[1]

        # Get bottom, same idea but row worth to the right
        not_bottom = self.index < (self._dish.height-1)*self._dish.width
        bottom_index = self.index + self._dish.width if not_bottom else self.index - self._dish.width*(self._dish.height-1)
        bottom = self._dish.cells[bottom_index].state[1]

        # Get left, if not left-most
        not_left = self.index % self._dish.width != 0
        left_index = self.index - 1 if not_left else self.index + self._dish.width - 1
        left = self._dish.cells[left_index].state[1]

        # Get right, if not right-most
        not_right = (self.index+1) % self._dish.width != 0
        right_index = self.index + 1 if not_right else self.index - self._dish.width + 1
        right = self._dish.cells[right_index].state[1]

        new_state = (self.state[0], None)

        # Flip color and change next direction
        direction_mutator = self.state[0]*2+1

        if bottom == 0:
            new_state = ((1-self.state[0]), (bottom+direction_mutator)%4)
        if left == 1:
            new_state = ((1-self.state[0]), (left+direction_mutator)%4)
        if top == 2:
            new_state = ((1-self.state[0]), (top+direction_mutator)%4)
        if right == 3:
            new_state = ((1-self.state[0]), (right+direction_mutator)%4)

        return Cell(self.index, new_state, self._dish)

    def __str__(self):
        return f"{self.state[0]:4}, {self.state[1]:4}"

    def __repr__(self):
        return str(self)

class Dish:

    def __init__(self, width=None, height=None, initial=None):
        if initial is not None:
            for color, direction in initial:
                if color != 1 or color != 0:
                    raise ValueError(f"{color} is not a valid color code")
                if direction < 0 or direction > 3:
                    raise ValueError(f"{direction} is not a valid direction code")

        if width is None and height is not None and initial is not None:
            print(height)
            width = int(len(initial)/height)

        self.width = width

        self.cells = []

        # Just checking for consistency if both are supplied
        if height is not None and initial is not None:
            if height != len(initial) / width:
                raise ValueError(f"Inconsistent height and initial values")

            # Let the initial value handle everything
            height = None

        if height is None:
            if initial is None:
                raise ValueError(
                    "If an initial value is not passed, height must be explicitly specified")
            else:
                height = int(len(initial) / width)
                # Check for bad division
                if (height % 1 != 0):
                    raise ValueError(
                        f"Cannot draw rectangle from {len(initial)} cells with a width of {width}")
        else:
            initial = [(0, None)]*(height*width)
        
        initial[random.randint(0, len(initial)-1)] = (0, random.randint(0, 3))

        self.cells.extend([Cell(i, state, self)
                           for (i, state) in enumerate(initial)])

        
        self.height = height

    def __str__(self):
        return ' ' + ' '.join([str(cell.state) + ("\n" if (i+1) % self.width == 0 else '') for i, cell in enumerate(self.cells)]) + ' '

    def __repr__(self):
        return ' ' + ' '.join([repr(cell) + ("\n" if (i+1) % self.width == 0 else '') for i, cell in enumerate(self.cells)]) + ' '

    def reset(self):
        for cell in self.cells:
            cell.state = (0, None)

    def next_tick(self):
        self.cells = [cell.get_next_cell() for cell in self.cells]

    def move_ant(self, index):
        for i, cell in enumerate(self.cells):
            cell.state = (cell.state[0], random.randint(0, 3) if i == index else None)
        

    def toggle_cell(self, index):
        self.cells[index].toggle()

class DishDrawer:
    def __init__(self, canvas_height, canvas_width):
        self.previous_state = None
        self._canvas_height = canvas_height
        self._canvas_width = canvas_width
        self.pause()
        turtle.setup(self._canvas_width, 400)
        turtle.tracer(False)
        wn = turtle.Screen()
        wn.colormode(255)
        t = turtle.Turtle()
        self._turtle = t
        self._wn = wn
        size = askinteger("Universe Size", "Enter universe size:")
        if size is None:
            self.quit()

        self._dish = Dish(size, size)
        self.draw()
        wn.onkey(self.start, 's')
        wn.onkey(self.pause, 'p')
        # wn.onkey(self.draw_file, 'f')
        wn.onkey(self.random_fill, 'r')
        wn.onkey(self.draw_next, 'Right')
        wn.onkey(self.quit, 'q')
        wn.onclick(self.toggle_cell)
        wn.onclick(self.move_ant, btn=3)
        self.tick()
        wn.listen()
        wn.mainloop()

    def tick(self):
        if self.active:
            self.draw_next()
        self._wn.ontimer(self.tick, 500)

    def random_fill(self):
        self.pause()
        self._dish.reset()
        while sum(cell.state[0] for cell in self._dish.cells)/len(self._dish.cells) < 0.1:
            self._dish.toggle_cell(random.randint(0, len(self._dish.cells)-1))

        self._dish.move_ant(random.randint(0, len(self._dish.cells)))
        self.draw()

    def move_ant(self, x, y):
        self.pause()
        cell_width = self._canvas_width/self._dish.width
        cell_height = self._canvas_height/self._dish.height
        column_index = int((x+self._canvas_width/2)/cell_width)
        row_index = int((self._canvas_height/2-y)/cell_height)

        cell_index = column_index + row_index*self._dish.width
        self._dish.move_ant(cell_index)
        self.draw()

    def toggle_cell(self, x, y):
        self.pause()
        cell_width = self._canvas_width/self._dish.width
        cell_height = self._canvas_height/self._dish.height
        column_index = int((x+self._canvas_width/2)/cell_width)
        row_index = int((self._canvas_height/2-y)/cell_height)

        cell_index = column_index + row_index*self._dish.width
        self._dish.toggle_cell(cell_index)
        self.draw()

    def quit(self):
        exit(0)

    def start(self):
        self.active = True

    def pause(self):
        self.active = False

    def draw(self):
        t = self._turtle
        cell_width = self._canvas_width/self._dish.width
        cell_height = self._canvas_height/self._dish.height
        
        # Draw all cells
        for i, cell in enumerate(self._dish.cells):

            # Why repaint when we can *not* repaint?
            ignore = False
            if self.previous_state is not None:
                ignore = cell.state == self.previous_state[i]

            if not ignore:
                column = i % self._dish.width
                row = int(i/self._dish.width)

                t.fillcolor((0, 0, 0) if cell.state[0] == 1 else (255, 255, 255))

                t.begin_fill()
                t.penup()
                t.goto(-self._canvas_width/2+cell_width*column, self._canvas_height/2-cell_height*row)
                t.pendown()
                t.forward(cell_width)
                t.right(90)
                t.forward(cell_height)
                t.right(90)
                t.forward(cell_width)
                t.right(90)
                t.forward(cell_height)
                t.right(90)
                t.end_fill()

                # Draw "ant"
                if cell.state[1] is not None:
                    t.penup()
                    t.goto(-self._canvas_width/2+cell_width*column+cell_width/2, self._canvas_height/2-cell_height*row-cell_height/2)
                    t.pendown()
                    t.color("red")
                    t.right((cell.state[1]-1)*90)
                    
                    t.forward(-10)
                    t.forward(20)
                    t.right(135)
                    t.forward(10)
                    t.forward(-10)
                    t.left(135)

                    t.left(135)
                    t.forward(10)
                    t.forward(-10)
                    t.right(135)

                    
                    # t.penup()
                    t.left((cell.state[1]-1)*90)
                    t.penup()
                    t.color("black")

        self.previous_state = [cell.state for cell in self._dish.cells]

    def draw_next(self):
        self._dish.next_tick()
        self.draw()


# Launch
DishDrawer(400, 400)

