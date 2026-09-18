from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivy_garden.mapview import MapView, MapMarker

# NammaSpot: Nearby Help, Fast
# Prototype implementation in Python/Kivy.
# Replace demo provider data with Firebase/Firestore data when credentials are configured.

SERVICES = [
    ("🔧", "Mechanic"),
    ("🚑", "Ambulance"),
    ("🏥", "Hospital"),
    ("👮", "Police"),
    ("🚒", "Fire Station"),
    ("🌲", "Forest Office"),
]

DEMO_PROVIDERS = [
    {"name": "Namma Auto Care", "category": "Mechanic", "lat": 12.9300, "lon": 79.3300, "phone": "+919000000001"},
    {"name": "City Hospital", "category": "Hospital", "lat": 12.9250, "lon": 79.3350, "phone": "+919000000002"},
    {"name": "Emergency Police", "category": "Police", "lat": 12.9280, "lon": 79.3250, "phone": "100"},
    {"name": "Fire & Rescue", "category": "Fire Station", "lat": 12.9320, "lon": 79.3380, "phone": "101"},
]

class HomeScreen(Screen):
    pass

class MapScreen(Screen):
    selected_category = StringProperty("All")

    def on_enter(self):
        Clock.schedule_once(lambda *_: self.load_map(), 0.2)

    def load_map(self):
        if hasattr(self, "map_view"):
            return
        self.map_view = MapView(zoom=13, lat=12.9279, lon=79.3350)
        self.ids.map_container.add_widget(self.map_view)
        self.refresh_markers()

    def refresh_markers(self, category="All"):
        self.selected_category = category
        if not hasattr(self, "map_view"):
            return
        self.map_view.clear_widgets()
        for p in DEMO_PROVIDERS:
            if category != "All" and p["category"] != category:
                continue
            marker = MapMarker(lat=p["lat"], lon=p["lon"])
            self.map_view.add_widget(marker)

    def choose_category(self, category):
        self.refresh_markers(category)

class HelpScreen(Screen):
    def submit_request(self):
        service = self.ids.service.text.strip() or "General Help"
        self.ids.result.text = f"Request created: {service}\nStatus: Searching nearby provider"

class ProviderScreen(Screen):
    pass

class NammaSpotApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(MapScreen(name="map"))
        sm.add_widget(HelpScreen(name="help"))
        sm.add_widget(ProviderScreen(name="provider"))
        return sm

    def go(self, screen):
        self.root.current = screen

if __name__ == "__main__":
    NammaSpotApp().run()
