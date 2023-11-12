import tkinter
from tkinter import ttk
from component import const
from component.images import get_pokemon_icon


class MyLabel(ttk.Label):

    def __init__(self, master=None, size: tuple[int, int] = None, font=None, **kwargs):
        super().__init__(master,
                         font=font if font is not None else (const.FONT_FAMILY, 10),
                         **kwargs)
        self._size = size
        self._image = None
        if "image" not in kwargs and size is not None:
            self.set_image(tkinter.PhotoImage(width=size[0], height=size[1]))

    def set_image(self, image):
        self._image = image
        self["image"] = self._image

    def set_pokemon_icon(self, pid: str, size: tuple[int, int] = None):
        image_size = size if size is None else self._size
        self.set_image(get_pokemon_icon(pid, image_size))
