class Cell:
    def __init__(self, index, state, dish):
        self.index = index
        self.state = state
        self._dish = dish
        
    def get_nearby(self):
        # Get top, if not in first row
        # Top cell is a row-worth to the left
        top = self._dish.cells[self.index - self._dish.width].state if (self.index >= self._dish.width) else 0

        # Get bottom, same idea but row worth to the right
        bottom = self._dish.cells[self.index + self._dish.width].state if (self.index < (self._dish.height-1)*self._dish.width) else 0
        
        # Get left, if not left-most
        left = self._dish.cells[self.index - 1].state if (self.index % self._dish.width != 0) else 0

        # Get right, if not right-most
        right = self._dish.cells[self.index + 1].state if ((self.index+1) % self._dish.width != 0) else 0
        
        return top+bottom+left+right

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
        
class Dish:

    def __init__(self, width, height=None, initial=None):
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
                raise ValueError("If an initial value is not passed, height must be explicitly specified")
            else:
                height = len(initial) / width
                # Check for bad division
                if (height%1!=0):
                    raise ValueError(f"Cannot draw rectangle from {len(initial)} cells with a width of {width}")
        else:
            initial = [0]*(height*width)

        self.cells.extend([Cell(i, state, self) for (i, state) in enumerate(initial)])

        self.height = height

    def __str__(self):
        return ' ' + ' '.join([str(cell.state) + ("\n" if (i+1)%self.width==0 else '') for i, cell in enumerate(self.cells)])

    def next_tick(self):
        self.cells = [cell.get_next_cell() for cell in self.cells]


initial = [0, 1]*8

dish = Dish(4, initial=initial)
print(dish)
dish.next_tick()

print(dish)
dish.next_tick()

print(dish)
dish.next_tick()
