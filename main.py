from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import routeros_api
import threading

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class MikroTikHotspotApp(App):
    def build(self):
        self.title = "MikroTik Hotspot Manager"
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.ip_input = TextInput(hint_text='MikroTik IP (e.g. 192.168.88.1)', multiline=False, size_hint_y=None, height=50)
        self.user_input = TextInput(hint_text='Username', multiline=False, size_hint_y=None, height=50)
        self.pass_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=None, height=50)
        
        self.connect_btn = Button(text='Connect & Load Users', size_hint_y=None, height=60, background_color=(0, 0.5, 0.8, 1))
        self.connect_btn.bind(on_press=self.start_connection)
        
        self.result_label = Label(text='Status: Waiting for connection...', size_hint_y=None, halign='left', valign='top')
        self.result_label.bind(width=lambda *x: self.result_label.setter('text_size')(self.result_label, (self.result_label.width, None)))
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.result_label)
        
        layout.add_widget(self.ip_input)
        layout.add_widget(self.user_input)
        layout.add_widget(self.pass_input)
        layout.add_widget(self.connect_btn)
        layout.add_widget(scroll)
        
        return layout

    def start_connection(self, instance):
        self.result_label.text = "Connecting to MikroTik via API..."
        self.connect_btn.disabled = True
        threading.Thread(target=self.fetch_users, daemon=True).start()

    def fetch_users(self):
        ip = self.ip_input.text.strip()
        user = self.user_input.text.strip()
        password = self.pass_input.text.strip()
        
        if not all([ip, user, password]):
            self.update_ui("Error: All fields are required!")
            return
            
        try:
            pool = routeros_api.RouterOsApiPool(ip, username=user, password=password, plaintext_login=True)
            api = pool.get_api()
            users = api.get_resource('/ip/hotspot/user').get()
            
            res_text = f"Connected Successfully!\nTotal Users: {len(users)}\n\n"
            res_text += "-" * 30 + "\n"
            for u in users:
                res_text += f"User: {u.get('name', 'N/A')} | Profile: {u.get('profile', 'default')}\n"
                
            self.update_ui(res_text)
            pool.disconnect()
        except Exception as e:
            self.update_ui(f"Connection Failed:\n{str(e)}")

    def update_ui(self, text):
        self.result_label.text = text
        self.connect_btn.disabled = False

if __name__ == '__main__':
    MikroTikHotspotApp().run()
