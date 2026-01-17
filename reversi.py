import enum
import random

from collections import deque

import pyglet

from pyglet.enums import CompareOp
from pyglet.shapes import RoundedRectangle


pyglet.resource.path = ['game/resources/']
pyglet.resource.reindex()

window = pyglet.window.Window(resizable=True)
batch = pyglet.graphics.Batch()


def load_centered_texture(name):
    texture = pyglet.resource.texture(name)
    texture.anchor_x = texture.width / 2
    texture.anchor_y = texture.height / 2
    return texture


class COLORS(enum.StrEnum):
    WHITE = 'white'
    BLACK = 'black'


class Board:

    background_color = (200, 200, 200)
    cell_color = (50, 50, 50)
    cell_highlight_color = (80, 80, 80)

    white_faces = [f"white{i}.png" for i in range(1, 20 + 1)]
    black_faces = [f"black{i}.png" for i in range(1, 16 + 1)]

    def __init__(self, window, batch, num_cells=8):
        self.window = window
        self.batch = batch
        self.num_cells = num_cells

        self.white_textures = deque([load_centered_texture(face) for face in self.white_faces])
        self.black_textures = deque([load_centered_texture(face) for face in self.black_faces])

        # Calculated on resize:
        self.x = 0
        self.y = 0
        self.size = 0
        self.border = 0
        self.sectorsize = 1

        self.bg_group = pyglet.graphics.Group(order=0)
        self.bg_group.set_depth_test(CompareOp.LESS)
        self.pc_group = pyglet.graphics.Group(order=1)

        # Shapes:
        self.board_shapes = []
        self.face_sprites = []
        self.shape_map = {}
        self.texture_map = {}
        self.selected_cell = None

        self.current_color = COLORS.WHITE
        self.color_map = {}

        self.create_board()

    def _get_random_face(self, color):
        """Get a random face from the top of the deque, then rotate."""
        texture_list_name = f"{color}_textures"
        textures = getattr(self, texture_list_name)
        num_items = len(textures) - 1
        index = random.randint(num_items // 2, num_items)   # top half only
        choice = textures[index]
        textures.remove(choice)
        textures.insert(0, choice)
        textures.rotate(1)
        setattr(self, texture_list_name, textures)
        return choice

    def create_board(self):
        # Calculate the background
        background = RoundedRectangle(self.x, self.y, self.size, self.size, radius=8,
                                      color=self.background_color, group=self.bg_group, batch=self.batch)
        background.z = -1.0
        self.board_shapes.append(background)

        # Calculate the Cells:
        gapsize = self.size * 0.01
        cellsize = (self.size - gapsize * (self.num_cells + 1)) / self.num_cells
        startx = self.x + gapsize
        starty = self.y + gapsize
        radius = max(2.0, gapsize)

        for row in range(self.num_cells):
            y = starty + row * (cellsize + gapsize)
            for column in range(self.num_cells):
                x = startx + column * (cellsize + gapsize)
                cell = RoundedRectangle(x, y, cellsize, cellsize, radius,
                                        color=self.cell_color, group=self.bg_group, batch=self.batch)

                self.shape_map[(column, row)] = cell
                self.board_shapes.append(cell)

        # Calculate the Pieces:
        sectorsize = self.sectorsize
        for (column, row), texture in self.texture_map.items():
            x = self.x + (column * sectorsize + sectorsize / 2)
            y = self.y + (row * sectorsize + sectorsize / 2)
            face = pyglet.sprite.Sprite(texture, x, y, group=self.pc_group, batch=self.batch)
            face.scale = sectorsize / texture.height * 0.8
            self.face_sprites.append(face)

    def delete_board(self):
        for item in self.board_shapes + self.face_sprites:
            item.delete()
        self.board_shapes.clear()
        self.face_sprites.clear()
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
            cell = self.shape_map.get((column, row))

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

        if color := self.color_map.get((column, row)):
            # TODO: play a sound effect
            print(f"Already color: ", color)
            return

        sectorsize = self.sectorsize
        x = self.x + (column * sectorsize + sectorsize / 2)
        y = self.y + (row * sectorsize + sectorsize / 2)

        texture = self._get_random_face(color=self.current_color)
        face = pyglet.sprite.Sprite(texture, x, y, group=self.pc_group, batch = self.batch)
        face.scale = self.sectorsize / texture.height * 0.8
        self.face_sprites.append(face)

        self.texture_map[(column, row)] = texture
        self.color_map[(column, row)] = self.current_color

        # TODO: handle player changeover, move checking, etc.
        self.current_color = {COLORS.WHITE: COLORS.BLACK, COLORS.BLACK: COLORS.WHITE}[self.current_color]

if __name__ == "__main__":
    board = Board(window=window, batch=batch)
    window.push_handlers(board)

    window.context.set_clear_color(0.5, 0.5, 0.5, 1.0)
    pyglet.app.run()
