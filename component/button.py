from tkinter import ttk

from component import images
from pokedata.const import Types


class MyButton(ttk.Button):
    def __init__(self, master=None, size: tuple[int, int] = None, **kwargs):
        ttk.Button.__init__(self, master, **kwargs)
        self._size = size
        self._image = None
        if "image" in kwargs:
            self.set_image(kwargs.pop("image"))
        elif "image" not in kwargs and size is not None:
            self.set_image(images.get_blank_image(size))

    @property
    def text(self) -> str:
        return self["text"]

    @text.setter
    def text(self, value):
        self["text"] = value

    def set_image(self, image):
        self._image = image
        self["image"] = self._image

    def set_pokemon_icon(self, pid: str, size: tuple[int, int] = None):
        image_size = size if size is None else self._size
        self.set_image(images.get_pokemon_icon(pid, image_size))


# タイプアイコンボタン
class TypeIconButton(MyButton):
    def __init__(
        self,
        master=None,
        types: Types = Types.なし,
        size: tuple[int, int] = None,
        **kwargs,
    ):
        super().__init__(master, size, **kwargs)
        self._type = types
        self._icon = None
        self.set_type(types)

    @property
    def get_type(self) -> Types:
        return self._type

    def set_type(self, value: Types):
        self._type = value
        self._icon = images.get_type_icon(value)
        self["image"] = self._icon


class TypeButton(MyButton):
    def __init__(
        self,
        master=None,
        type_: Types = Types.なし,
        size: tuple[int, int] = None,
        **kwargs,
    ):
        super().__init__(master, size, style="leftimage.TButton", **kwargs)
        self._type = type_
        self._icon = None
        self.set_type(type_)

    @property
    def type_(self) -> Types:
        return self._type

    def set_type(self, value: Types):
        self._type = value
        self._icon = images.get_type_icon(value)
        self["image"] = self._icon
        self["text"] = value.name
