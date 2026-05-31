# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
import threading, urllib.request, urllib.parse, json
from datetime import datetime

# ==================== Translations ====================
T = {
    "en": {
        "title": "Guangdong Weather",
        "city_frame": "City",
        "auto_cb": "Auto-refresh (60s)",
        "refresh_btn": "Refresh Now",
        "fetching": "Fetching...",
        "ready": "Ready",
        "updated": "Last update: ",
        "next": "Next: ",
        "refreshing": "Refreshing...",
        "loading": "Loading...",
        "lang_btn": "\u4e2d\u6587",
        "location_label": "Location",
        "temp": "Temp",
        "feels_like": "FeelsLike",
        "humidity": "Humidity",
        "wind": "Wind",
        "visibility": "Visibility",
        "pressure": "Pressure",
        "weather": "Weather",
        "forecast_title": "3-Day Forecast",
        "avg": "avg",
        "sunrise": "Sunrise",
        "sunset": "Sunset",
        "error_network": "Network error",
        "sep": "=" * 50,
    },
    "zh": {
        "title": "\u5e7f\u4e1c\u7701\u5929\u6c14\u5b9e\u65f6\u67e5\u8be2",
        "city_frame": "\u9009\u62e9\u57ce\u5e02",
        "auto_cb": "\u81ea\u52a8\u5237\u65b0(60\u79d2)",
        "refresh_btn": "\u7acb\u5373\u5237\u65b0",
        "fetching": "\u83b7\u53d6\u4e2d...",
        "ready": "\u5c31\u7eea",
        "updated": "\u6700\u540e\u66f4\u65b0: ",
        "next": "\u4e0b\u6b21: ",
        "refreshing": "\u5237\u65b0\u4e2d...",
        "loading": "\u52a0\u8f7d\u4e2d...",
        "lang_btn": "English",
        "location_label": "\u5730\u70b9",
        "temp": "\u6e29\u5ea6",
        "feels_like": "\u4f53\u611f",
        "humidity": "\u6e7f\u5ea6",
        "wind": "\u98ce\u529b",
        "visibility": "\u80fd\u89c1\u5ea6",
        "pressure": "\u6c14\u538b",
        "weather": "\u5929\u6c14",
        "forecast_title": "\u672a\u6765\u4e09\u65e5\u9884\u62a5",
        "avg": "\u5747\u6e29",
        "sunrise": "\u65e5\u51fa",
        "sunset": "\u65e5\u843d",
        "error_network": "\u7f51\u7edc\u9519\u8bef",
        "sep": "=" * 50,
    }
}

def fetch_weather(location, lang="en"):
    encoded = urllib.parse.quote(location)
    api_lang = "zh" if lang == "zh" else "en"
    url = f"https://wttr.in/{encoded}?format=j1&lang={api_lang}"
    t = T.get(lang, T["en"])
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        lines = []
        lines.append(t["sep"])
        lines.append(f"  {t['location_label']}: {location}")
        lines.append(t["sep"])
        cc = data.get("current_condition", [{}])[0]
        if cc:
            lines.append(f"  {t['temp']}: {cc.get('temp_C','?')}C  ({t['feels_like']}: {cc.get('FeelsLikeC','?')}C)")
            lines.append(f"  {t['humidity']}: {cc.get('humidity','?')}%")
            lines.append(f"  {t['wind']}: {cc.get('windspeedKmph','?')} km/h  {cc.get('winddir16Point','')}")
            lines.append(f"  {t['visibility']}: {cc.get('visibility','?')} km")
            lines.append(f"  {t['pressure']}: {cc.get('pressure','?')} hPa")
            desc = cc.get('weatherDesc', [{}])[0].get('value', '?')
            lines.append(f"  {t['weather']}: {desc}")
            lines.append("")
        lines.append("  " + "-" * 44)
        lines.append(f"  {t['forecast_title']}")
        lines.append("  " + "-" * 44)
        for day in data.get("weather", [])[:3]:
            d = day.get("date", "?")
            hi = day.get("maxtempC", "?")
            lo = day.get("mintempC", "?")
            avg = day.get("avgtempC", "?")
            hr = day.get("hourly", [])
            wd = hr[4].get("weatherDesc", [{}])[0].get("value", "") if len(hr) >= 4 else ""
            lines.append(f"  {d}  {lo}~{hi}C  ({t['avg']} {avg}C)  {wd}")
            astro = day.get("astronomy", [{}])[0] if day.get("astronomy") else {}
            if astro:
                lines.append(f"    {t['sunrise']}: {astro.get('sunrise','?')}  {t['sunset']}: {astro.get('sunset','?')}")
        lines.append(t["sep"])
        return "\n".join(lines)
    except Exception as e:
        return f"{t['error_network']}: {e}"


class WeatherRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [10, 10, 10, 10]
        self.spacing = 8
        self.lang = "en"
        self.auto_enabled = False
        self.busy = False
        self.location = "Guangdong"
        self.timer_event = None

        # --- Title ---
        self.title_label = Label(text=T[self.lang]["title"],
                                 font_size="18sp", bold=True,
                                 size_hint_y=None, height=40)
        self.add_widget(self.title_label)

        # --- Lang button ---
        self.lang_btn = Button(text=T[self.lang]["lang_btn"],
                                size_hint=(None, None), size=(100, 36),
                                pos_hint={"right": 1})
        self.lang_btn.bind(on_press=self._switch_lang)
        self.add_widget(self.lang_btn)

        # --- City buttons ---
        city_layout = GridLayout(cols=4, size_hint_y=None, height=44, spacing=6)
        self.city_btns = []
        for name, q in [("Guangdong", "Guangdong"), ("Zhanjiang", "Zhanjiang"),
                         ("Guangzhou", "Guangzhou"), ("Jieyang", "Jieyang")]:
            btn = Button(text=name, font_size="12sp")
            btn.bind(on_press=lambda x, v=q: self.select_city(v))
            city_layout.add_widget(btn)
            self.city_btns.append(btn)
        self.add_widget(city_layout)

        # --- Controls ---
        ctrl = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=6)
        self.auto_cb = CheckBox(active=False, size_hint=(None, None), size=(36, 36))
        self.auto_cb.bind(active=self._toggle_auto)
        ctrl.add_widget(self.auto_cb)
        self.auto_label = Label(text=T[self.lang]["auto_cb"], font_size="12sp",
                                size_hint_x=None, width=180, halign="left")
        ctrl.add_widget(self.auto_label)
        self.cd_label = Label(text="OFF", font_size="11sp",
                              size_hint_x=None, width=120, color=(0.6, 0.6, 0.6, 1))
        ctrl.add_widget(self.cd_label)
        self.refresh_btn = Button(text=T[self.lang]["refresh_btn"],
                                   font_size="12sp", size_hint_x=1)
        self.refresh_btn.bind(on_press=lambda x: self.refresh())
        ctrl.add_widget(self.refresh_btn)
        self.add_widget(ctrl)

        # --- Weather display (scrollable) ---
        self.sv = ScrollView()
        self.output = TextInput(text=T[self.lang]["loading"],
                                readonly=True,
                                background_color=(0.12, 0.12, 0.18, 1),
                                foreground_color=(0.8, 0.84, 0.96, 1),
                                font_name="Data/Fonts/DroidSansMono.ttf")
        self.sv.add_widget(self.output)
        self.add_widget(self.sv)

        # --- Status bar ---
        self.status = Label(text=T[self.lang]["ready"], font_size="11sp",
                            size_hint_y=None, height=28,
                            color=(0.5, 0.5, 0.5, 1))
        self.add_widget(self.status)

        Clock.schedule_once(lambda dt: self.refresh(), 0.5)

    def _switch_lang(self, instance):
        self.lang = "zh" if self.lang == "en" else "en"
        self._apply_lang()
        self.refresh()

    def _apply_lang(self):
        t = T[self.lang]
        self.title_label.text = t["title"]
        self.lang_btn.text = t["lang_btn"]
        self.auto_label.text = t["auto_cb"]
        self.refresh_btn.text = t["refresh_btn"]
        self.cd_label.text = "OFF" if not self.auto_enabled else f"{t['next']}60s"
        if not self.busy:
            self.status.text = t["ready"]
        self.output.text = t["loading"]

    def select_city(self, city):
        self.location = city
        self.refresh()

    def refresh(self):
        if self.busy:
            return
        self.busy = True
        t = T[self.lang]
        self.refresh_btn.text = t["fetching"]
        self.refresh_btn.disabled = True
        self.status.text = t["fetching"]
        self.output.text = t["fetching"]
        threading.Thread(target=self._worker, args=(self.location, self.lang), daemon=True).start()

    def _worker(self, city, lang):
        result = fetch_weather(city, lang)
        ts = datetime.now().strftime("%H:%M:%S")
        Clock.schedule_once(lambda dt: self._show(result, ts), 0)

    def _show(self, text, ts):
        t = T[self.lang]
        self.output.text = text
        self.refresh_btn.text = t["refresh_btn"]
        self.refresh_btn.disabled = False
        self.status.text = f"{t['updated']}{ts}"
        self.busy = False

    def _toggle_auto(self, cb, value):
        self.auto_enabled = value
        t = T[self.lang]
        if value:
            self.cd_label.text = f"{t['next']}60s"
            self.cd_label.color = (0.25, 0.63, 0.17, 1)
            self._schedule(60)
        else:
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None
            self.cd_label.text = "OFF"
            self.cd_label.color = (0.6, 0.6, 0.6, 1)

    def _schedule(self, n):
        t = T[self.lang]
        if n <= 0:
            self.cd_label.text = t["refreshing"]
            self.cd_label.color = (1, 0.39, 0.04, 1)
            self.refresh()
            self.timer_event = Clock.schedule_once(lambda dt: self._schedule(60), 0.5)
        else:
            self.cd_label.text = f"{t['next']}{n}s"
            self.cd_label.color = (0.25, 0.63, 0.17, 1)
            self.timer_event = Clock.schedule_once(lambda dt: self._schedule(n - 1), 1)


class WeatherApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.1, 1)
        return WeatherRoot()


if __name__ == "__main__":
    WeatherApp().run()
