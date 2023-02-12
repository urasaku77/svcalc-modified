from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

import atexit

from page_battle import CalcRecWidget
from page_party import EditPartyWidget

Window.size = (2400, 1200)
resource_add_path("font")
LabelBase.register(DEFAULT_FONT, "NotoSansJP-Medium.otf")

class RootWidget(BoxLayout):
    calcRecWidget = ObjectProperty()
    editPartyWidget = ObjectProperty()

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.calcRecWidget = CalcRecWidget()
        self.editPartyWidget = EditPartyWidget()

class MainApp(App):
    pass

# 終了時処理
def cleanup():
    print("cleanup")

if __name__ == '__main__':
    atexit.register(cleanup)
    MainApp().run()
