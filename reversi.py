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

        self.x = 0
        self.y = 0
        self.size = 0
        self.border = 0

        self.cells = 8

        self.bg_group = pyglet.graphics.Group(order=0)
        self.fg_group = pyglet.graphics.Group(order=1)
        self.pc_group = pyglet.graphics.Group(order=2)

        self.background = None
        self.cell_shapes = []
        self.create_board()

    def create_board(self):
        # Calculate the background
        r = 8
        self.background = RoundedRectangle(self.x, self.y, self.size, self.size, r, color=self.background_color, group=self.bg_group, batch=self.batch)

        # Calculate the Cells:
        gapsize = self.size * 0.01
        cellsize = (self.size - gapsize * 9) / self.cells
        startx = self.x + gapsize
        starty = self.y + gapsize
        r = max(2.0, gapsize)

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
        self.border = height * 0.05
        self.size = height - self.border * 2
        self.x =  self.window.width / 2 - self.size / 2
        self.y = self.border

        self.delete_board()
        self.create_board()

    def on_mouse_motion(self, x, y, dx, dy):
        print(x, y, "    ", int(x // self.cells), int(y // self.cells))


if __name__ == "__main__":
    board = Board(window=window, batch=batch)
    window.push_handlers(board)

    window.context.set_clear_color(0.5, 0.5, 0.5, 1.0)
    pyglet.app.run()
