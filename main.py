import tkinter
from tkinter.ttk import Style

import component.const
from component.app import MainApp
from stage import Stage

app = MainApp()
stage = Stage(app)

style = Style()
style.configure("leftimage.TButton", compound=tkinter.LEFT)

app.mainloop()
