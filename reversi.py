import pyglet

from pyglet.shapes import RoundedRectangle

window = pyglet.window.Window(resizable=True)
batch = pyglet.graphics.Batch()


class Board:

    background_color = (200, 200, 200)
    cell_color = (50, 50, 50)

    def __init__(self, window, batch):
        self.window = window
        self.batch = batch

        self.cells = 8

        self.bg_group = pyglet.graphics.Group(order=0)
        self.fg_group = pyglet.graphics.Group(order=1)
        self.pc_group = pyglet.graphics.Group(order=2)

        self.background = None
        self.cell_shapes = []
        self.create_board()

    def create_board(self):
        # Calculate the background
        border = self.window.height * 0.05
        size = self.window.height - border * 2
        x =  self.window.width / 2 - size / 2
        y = border
        r = 8
        self.background = RoundedRectangle(x, y, size, size, r, color=self.background_color, group=self.bg_group, batch=self.batch)

        # Calculate the Cells:
        gapsize = size * 0.01
        cellsize = (size - gapsize * 9) / self.cells
        startx = x + gapsize
        starty = y + gapsize
        r = max(2, gapsize)

        for row in range(self.cells):
            y = starty + row * (cellsize + gapsize)
            for column in range(self.cells):
                x = startx + column * (cellsize + gapsize)
                self.cell_shapes.append(RoundedRectangle(x, y, cellsize, cellsize, r,
                                                         color=self.cell_color, group=self.fg_group, batch=self.batch))

    def delete_board(self):
        for shape in self.cell_shapes:
            shape.delete()
        self.cell_shapes.clear()
        self.background.delete()
        self.background = None

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        self.delete_board()
        self.create_board()


if __name__ == "__main__":
    board = Board(window=window, batch=batch)
    window.push_handlers(board)

    window.context.set_clear_color(0.5, 0.5, 0.5, 1.0)
    pyglet.app.run()
