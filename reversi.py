import pyglet

from pyglet.shapes import RoundedRectangle

window = pyglet.window.Window(resizable=True)
batch = pyglet.graphics.Batch()


class Board:

    background_color = (200, 200, 200)
    cell_color = (50, 50, 50)
    cell_highlight_color = (80, 80, 80)
    white = (255, 255, 255)
    black = (0, 0, 0)

    def __init__(self, window, batch, num_cells=8):
        self.window = window
        self.batch = batch
        self.num_cells = num_cells

        # Calculated on resize:
        self.x = 0
        self.y = 0
        self.size = 0
        self.border = 0
        self.sectorsize = 1

        self.bg_group = pyglet.graphics.Group(order=0)
        self.fg_group = pyglet.graphics.Group(order=1)
        self.pc_group = pyglet.graphics.Group(order=2)
        self.hl_group = pyglet.graphics.Group(order=3)

        # Shapes:
        self.background = None
        self.cell_shapes = []
        self.piece_shapes = []
        self.cell_map = {}
        self.piece_map = {}
        self.selected_cell = None

        self.current_color = self.white
        self.color_map = {}

        self.create_board()

    def create_board(self):
        # Calculate the background
        r = 8
        self.background = RoundedRectangle(self.x, self.y, self.size, self.size, r, color=self.background_color, group=self.bg_group, batch=self.batch)

        # Calculate the Cells:
        gapsize = self.size * 0.01
        cellsize = (self.size - gapsize * (self.num_cells + 1)) / self.num_cells
        startx = self.x + gapsize
        starty = self.y + gapsize
        r = max(2.0, gapsize)

        for row in range(self.num_cells):
            y = starty + row * (cellsize + gapsize)
            for column in range(self.num_cells):
                x = startx + column * (cellsize + gapsize)
                cell = RoundedRectangle(x, y, cellsize, cellsize, r,
                                        color=self.cell_color, group=self.fg_group, batch=self.batch)
                self.cell_map[(column, row)] = cell
                self.cell_shapes.append(cell)

        # Calculate the Pieces:
        sectorsize = self.sectorsize
        radius = sectorsize / 3
        for column, row in self.piece_map.keys():
            x = self.x + (column * sectorsize + sectorsize / 2)
            y = self.y + (row * sectorsize + sectorsize / 2)
            circle = pyglet.shapes.Circle(x, y, radius, color=self.current_color, group=self.pc_group, batch=self.batch)
            self.piece_map[(column, row)] = circle


    def delete_board(self):
        for shape in self.cell_shapes + self.piece_shapes:
            shape.delete()
        self.cell_shapes.clear()
        self.piece_shapes.clear()
        self.background.delete()
        self.background = None
        self.selected_cell = None

    def _in_bounds(self, x, y) -> bool:
        """Check if the mouse is within the board area."""
        return self.x < x < self.x + self.size and self.y < y < self.y + self.size

    def _get_sector(self, x, y):
        """Spatial hash to find the sector id from the x,y coordinates of the mouse."""
        return int((x - self.x) / self.sectorsize), int((y - self.y) / self.sectorsize)

    def _handle_mouse_motion(self, x, y):
        if self._in_bounds(x, y):
            column, row = self._get_sector(x, y)
            cell = self.cell_map.get((column, row))

            if self.selected_cell:
                self.selected_cell.color = self.cell_color

            cell.color = self.cell_highlight_color
            self.selected_cell = cell
            return

        if self.selected_cell:
            self.selected_cell.color = self.cell_color

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        self.border = height * 0.05
        self.size = height - self.border * 2
        self.x =  self.window.width / 2 - self.size / 2
        self.y = self.border
        self.sectorsize = self.size / self.num_cells

        self.delete_board()
        self.create_board()

    def on_mouse_motion(self, x, y, dx, dy):
        self._handle_mouse_motion(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._handle_mouse_motion(x, y)

    def on_mouse_press(self, x, y, mouse, modifiers):
        if not self._in_bounds(x, y):
            return

        column, row = self._get_sector(x, y)
        sectorsize = self.sectorsize
        radius = sectorsize / 3
        x = self.x + (column * sectorsize + sectorsize / 2)
        y = self.y + (row * sectorsize + sectorsize / 2)
        circle = pyglet.shapes.Circle(x, y, radius, color=self.current_color, group=self.pc_group, batch=self.batch)
        self.piece_map[(column, row)] = circle
        self.color_map[(column, row)] = self.current_color

        # TODO: handle player changeover, move checking, etc.
        self.current_color = {self.white: self.black, self.black: self.white}[self.current_color]

if __name__ == "__main__":
    board = Board(window=window, batch=batch)
    window.push_handlers(board)

    window.context.set_clear_color(0.5, 0.5, 0.5, 1.0)
    pyglet.app.run()
