from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy_gui.popup import PartyInputPopup, SpeedCheckPopup

class EditPartyWidget(BoxLayout):
    partyPokemonPanel = ListProperty()

    def __init__(self, **kwargs):
        super(EditPartyWidget, self).__init__(**kwargs)
