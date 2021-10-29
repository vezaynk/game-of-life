import turtle
import random
import time
import tkinter
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askinteger


class Cell:
    """
        A Cell is a 'self-aware' unit. 
        It is responsible to determine it's own future state by hooking into the parent dish
    Attributes:
        state   The current state of cell, represented by a single integer, 1 for alive, 0 for dead
    """
    def __init__(self, index, state, dish):
        self.index = index
        self.state = state
        self._dish = dish

    def toggle(self):
        """
            Toggles the state of the cell, turning it from dead to alive or vice-versa 
        """
        self.state = abs(1 - self.state)
        
    def get_nearby(self):
        """
            Gets the number of living cells direction adjacent to it

            Returns an integer
        """
        not_top = self.index >= self._dish.width
        not_bottom = self.index < (self._dish.height-1)*self._dish.width
        not_left = self.index % self._dish.width != 0
        not_right = (self.index+1) % self._dish.width != 0

        # Get top, if not in first row
        # Top cell is a row-worth to the left
        top = self._dish.cells[self.index -
                               self._dish.width].state if not_top else 0

        # Get bottom, same idea but row worth to the right
        bottom = self._dish.cells[self.index +
                                  self._dish.width].state if not_bottom else 0

        # Get left, if not left-most
        left = self._dish.cells[self.index - 1].state if not_left else 0

        # Get right, if not right-most
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
        """
            Derives the next state of the cell by observing those around it

            Returns next Cell object
        """
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
    """
        The dish (petri dish) is responsible for managing the cells it contains
        Attributes:
            height  The height of the dish
            width:  The width of the dish
            cells:  The cells contained in the dish
    """
    def __init__(self, width, initial=[]):
        self.width = width
        self.cells = []

        for n in initial:
            if n != 0 and n != 1:
                raise ValueError(f"{n} not allowed in initial data")

        if (len(initial) % width != 0):
            raise ValueError(
                f"Cannot draw rectangle from {len(initial)} cells with a width of {width}")

        if len(initial) == 0:
            initial = [0]*(width**2)

        self.cells.extend([Cell(i, state, self)
                           for (i, state) in enumerate(initial)])

    @property
    def height(self):
        return len(self.cells)//self.width

    def __str__(self):
        return ' ' + ' '.join([str(cell.state) + ("\n" if (i+1) % self.width == 0 else '') for i, cell in enumerate(self.cells)]) + ' '

    def __repr__(self):
        return ' ' + ' '.join([repr(cell) + ("\n" if (i+1) % self.width == 0 else '') for i, cell in enumerate(self.cells)]) + ' '

    def reset(self):
        """
            Resets all the cell states to whites
        """
        for cell in self.cells:
            cell.state = 0

    def next_tick(self):
        """
            Replaces the current generation of cells with the next
        """
        self.cells = [cell.get_next_cell() for cell in self.cells]

    def toggle_cell(self, index):
        """
            Toggles a cell in a particular position
            See also: Cell.toggle()
        """
        self.cells[index].toggle()

class DishDrawer:
    def __init__(self, canvas_width, padding):
        self.previous_state = None
        self.tick_counter = 0
        self.tick_speed = 500
        self._canvas_width = canvas_width
        self.pause()
        turtle.setup(self._canvas_width+padding, self._canvas_width+padding)
        turtle.tracer(False)
        wn = turtle.Screen()
        wn.colormode(255)
        t = turtle.Turtle()
        t.hideturtle()
        # t.speed(0)
        self._turtle = t
        self._wn = wn
        size = askinteger("Universe Size", "Enter universe size:")
        if size is None:
            self.quit()

        self._dish = Dish(size)
        self.draw()
        wn.onkey(self.start, 's')
        wn.onkey(self.tick_speed_up, 'Up')
        wn.onkey(self.tick_speed_down, 'Down')
        wn.onkey(self.pause, 'p')
        wn.onkey(self.draw_file, 'f')
        wn.onkey(self.random_fill, 'r')
        wn.onkey(self.draw_next, 'Right')
        wn.onkey(self.quit, 'q')
        wn.onclick(self.toggle_cell)
        self.tick()
        wn.listen()
        wn.mainloop()

    def tick_speed_up(self):
        if self.tick_speed > 100:
            self.tick_speed -= 100

    def tick_speed_down(self):
        if self.tick_speed < 2000:
            self.tick_speed += 100

    def tick(self):
        if self.active:
            self.draw_next()
        self._wn.ontimer(self.tick, self.tick_speed)

    def random_fill(self):
        self.pause()
        self._dish.reset()
        while sum(cell.state for cell in self._dish.cells)/len(self._dish.cells) < 0.4:
            self._dish.toggle_cell(random.randint(0, len(self._dish.cells)-1))
        self.draw()

    def toggle_cell(self, x, y):
        self.pause()
        cell_width = self._canvas_width/self._dish.width
        column_index = (x+self._canvas_width/2)//cell_width
        row_index = (self._canvas_width/2-y)//cell_width
        cell_index = int(column_index + row_index*self._dish.width)
        # Do not toggle out-of-index cells
        if column_index < self._dish.width and row_index < self._dish.height and row_index >= 0 and column_index >= 0:
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
                self._dish = Dish(len(lines), [int(c) for line in lines for c in line])
                self.draw()
        except Exception as e:
            messagebox.showerror("Error", f"The selected file is invalid: {e}")

    def start(self):
        self.active = True

    def pause(self):
        self.active = False

    def draw(self):
        t = self._turtle
        cell_width = self._canvas_width/self._dish.width
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
                t.goto(-self._canvas_width/2+cell_width*column, self._canvas_width/2-cell_width*row)
                t.pendown()
                for _ in range(4):
                    t.forward(cell_width)
                    t.right(90)
                    
                t.end_fill()

        self.previous_state = [cell.state for cell in self._dish.cells]
        self._wn.update()

    def draw_next(self):
        self._dish.next_tick()
        self.draw()


# Launch
try:
    DishDrawer(400, 50)
except tkinter.TclError:
    print("Program Ended")


