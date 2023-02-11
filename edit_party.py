from kivy.app import App
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy_gui.popup import PartyInputPopup, SpeedCheckPopup

class EditPartyWidget(BoxLayout):
    partyPokemonPanel = ListProperty()
    title=StringProperty("")
    num=StringProperty("")
    sub_num=StringProperty("")
    using_csv=StringProperty("")

    def __init__(self, **kwargs):
        super(EditPartyWidget, self).__init__(**kwargs)
    
    def open_csv(self):
        pass

    def save_csv(self):
        pass

    def change_using_csv(self):
        pass