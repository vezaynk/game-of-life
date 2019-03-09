import turtle
import random
import time
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askinteger


class Cell:
    def __init__(self, index, state, dish):
        self.index = index
        self.state = state
        self._dish = dish

    def toggle(self):
        self.state = abs(1 - self.state)
        
    def get_nearby(self):
        # Get top, if not in first row
        # Top cell is a row-worth to the left
        not_top = self.index >= self._dish.width
        top = self._dish.cells[self.index -
                               self._dish.width].state if not_top else 0

        # Get bottom, same idea but row worth to the right
        not_bottom = self.index < (self._dish.height-1)*self._dish.width
        bottom = self._dish.cells[self.index +
                                  self._dish.width].state if not_bottom else 0

        # Get left, if not left-most
        not_left = self.index % self._dish.width != 0
        left = self._dish.cells[self.index - 1].state if not_left else 0

        # Get right, if not right-most
        not_right = (self.index+1) % self._dish.width != 0
        right = self._dish.cells[self.index +
                                 1].state if not_right else 0

        # Diagonals
        top_right = self._dish.cells[self.index -
                                     self._dish.width + 1].state if not_top and not_right else 0

        top_left = self._dish.cells[self.index -
                                    self._dish.width - 1].state if not_top and not_left else 0

        bottom_right = self._dish.cells[self.index +
                                        self._dish.width + 1].state if not_bottom and not_right else 0

        bottom_left = self._dish.cells[self.index +
                                       self._dish.width - 1].state if not_bottom and not_left else 0
        return sum((top, bottom, left, right, top_right, top_left, bottom_right, bottom_left))

    def get_next_cell(self):
        nearby = self.get_nearby()

        # Statis
        new_state = self.state

        if nearby > 3:
            # Over population
            new_state = 0
        elif nearby < 2:
            # Underpopulation
            new_state = 0
        elif nearby == 3:
            # Reproduction
            new_state = 1

        return Cell(self.index, new_state, self._dish)

    def __str__(self):
        return "Alive" if self.state == 1 else "Dead"

    def __repr__(self):
        return str((self.__str__(), self.get_nearby()))

    def __eq__(self, compare):
        return self.state == compare.state

class Dish:

    def __init__(self, width=None, height=None, initial=None):
        if initial is not None:
            for n in initial:
                if n != 0 and n != 1:
                    raise ValueError(f"{n} not allowed in initial data")

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
            initial = [0]*(height*width)

        self.cells.extend([Cell(i, state, self)
                           for (i, state) in enumerate(initial)])

        self.height = height

    def __str__(self):
        return ' ' + ' '.join([str(cell.state) + ("\n" if (i+1) % self.width == 0 else '') for i, cell in enumerate(self.cells)]) + ' '

    def __repr__(self):
        return ' ' + ' '.join([repr(cell) + ("\n" if (i+1) % self.width == 0 else '') for i, cell in enumerate(self.cells)]) + ' '

    def reset(self):
        for cell in self.cells:
            cell.state = 0

    def next_tick(self):
        self.cells = [cell.get_next_cell() for cell in self.cells]

    def toggle_cell(self, index):
        self.cells[index].toggle()

class DishDrawer:
    def __init__(self, canvas_height, canvas_width):
        self.previous_state = None
        self.tick_counter = 0
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
        wn.onkey(self.draw_file, 'f')
        wn.onkey(self.random_fill, 'r')
        wn.onkey(self.draw_next, 'Right')
        wn.onkey(self.quit, 'q')
        wn.onclick(self.toggle_cell)
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
        while sum(cell.state for cell in self._dish.cells)/len(self._dish.cells) < 0.4:
            self._dish.toggle_cell(random.randint(0, len(self._dish.cells)-1))
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

    def draw_file(self):
        self.pause()
        self.previous_state = None
        filename = askopenfilename()
        print(filename)
        try:
            with open(filename) as file:
                lines = [line.strip() for line in file]
                self._dish = Dish(height=len(lines), initial=[
                                int(c) for line in lines for c in line])
        except Exception:
            messagebox.showerror("Error", "The selected file is invalid")
        
        
        self.draw()

    def start(self):
        self.active = True

    def pause(self):
        self.active = False

    def draw(self):
        t = self._turtle
        cell_width = self._canvas_width/self._dish.width
        cell_height = self._canvas_height/self._dish.height
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0)]
        active_fill = colors[self.tick_counter]
        self.tick_counter = (self.tick_counter+1)%len(colors)
        # Draw all cells
        for i, cell in enumerate(self._dish.cells):

            # Why repaint when we can *not* repaint?
            ignore = False
            if self.previous_state is not None:
                ignore = cell.state == self.previous_state[i]

            if not ignore:
                column = i % self._dish.width
                row = int(i/self._dish.width)

                t.fillcolor(active_fill if cell.state == 1 else (255, 255, 255))

                t.begin_fill()
                t.penup()
                t.goto(-200+cell_width*column, 200-cell_height*row)
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

        self.previous_state = [cell.state for cell in self._dish.cells]

    def draw_next(self):
        self._dish.next_tick()
        self.draw()


# Launch
DishDrawer(400, 400)

