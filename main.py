from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

import atexit

from page_battle import PageBattleWidget
from page_party import PagePartyWidget

Window.size = (2400, 1200)
resource_add_path("font")
LabelBase.register(DEFAULT_FONT, "NotoSansJP-Medium.otf")

class RootWidget(BoxLayout):
    pageBattleWidget = ObjectProperty()
    pagePartyWidget = ObjectProperty()

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.pageBattleWidget = PageBattleWidget()
        self.pagePartyWidget = PagePartyWidget()

class MainApp(App):
    pass

# 終了時処理
def cleanup():
    print("cleanup")

if __name__ == '__main__':
    atexit.register(cleanup)
    MainApp().run()
