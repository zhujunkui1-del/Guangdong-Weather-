# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading, urllib.request, urllib.parse, json
from datetime import datetime

# ==================== Translations ====================
T = {
    "en": {
        "title": "Guangdong Weather",
        "subtitle": "Data: wttr.in  |  Guangdong / Zhanjiang / Guangzhou / Jieyang",
        "city_frame": "City",
        "controls_frame": "Controls",
        "auto_cb": "Auto-refresh (60s)",
        "off": "OFF",
        "refresh_btn": "Refresh Now",
        "fetching": "Fetching...",
        "weather_frame": "Weather Info",
        "loading": "Loading...",
        "ready": "Ready",
        "fetching_status": "Fetching weather data...",
        "updated": "Last update: ",
        "next": "Next: ",
        "refreshing": "Refreshing...",
        "lang_btn": "中 文",
        # Weather labels
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
        "error_fetch": "Fetch failed",
        "sep": "=" * 50,
    },
    "zh": {
        "title": "广东省天气实时查询",
        "subtitle": "数据来源: wttr.in  |  广东 / 湛江 / 广州 / 揭阳",
        "city_frame": "选择城市",
        "controls_frame": "控制选项",
        "auto_cb": "自动刷新（60秒）",
        "off": "已关闭",
        "refresh_btn": "立即刷新",
        "fetching": "获取中...",
        "weather_frame": "天气信息",
        "loading": "加载中...",
        "ready": "就绪",
        "fetching_status": "正在获取天气数据...",
        "updated": "最后更新: ",
        "next": "下次刷新: ",
        "refreshing": "刷新中...",
        "lang_btn": "English",
        # Weather labels
        "location_label": "地点",
        "temp": "温度",
        "feels_like": "体感温度",
        "humidity": "湿度",
        "wind": "风力",
        "visibility": "能见度",
        "pressure": "气压",
        "weather": "天气",
        "forecast_title": "未来三日预报",
        "avg": "均温",
        "sunrise": "日出",
        "sunset": "日落",
        "error_network": "网络错误",
        "error_fetch": "获取失败",
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
    except urllib.error.URLError as e:
        return f"{t['error_network']}: {e}"
    except Exception as e:
        return f"{t['error_fetch']}: {e}"


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.lang = "en"
        self.root.title(T[self.lang]["title"])
        self.root.geometry("620x640")
        self.root.minsize(500, 480)
        self.auto_enabled = tk.BooleanVar(value=False)
        self.location = tk.StringVar(value="Guangdong")
        self.timer_id = None
        self.busy = False
        self._build()
        self.root.after(500, self.refresh)

    def _tr(self, key):
        return T[self.lang].get(key, key)

    def _build(self):
        t = T[self.lang]

        # --- Title ---
        self.title_label = ttk.Label(self.root, text=t["title"],
                                     font=("Microsoft YaHei", 16, "bold"))
        self.title_label.pack(pady=(12, 4))

        self.subtitle_label = ttk.Label(self.root, text=t["subtitle"],
                                        font=("Microsoft YaHei", 9), foreground="#666")
        self.subtitle_label.pack(pady=(0, 8))

        # --- Language toggle (top-right area via a frame) ---
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=12, pady=(0, 4))
        self.lang_btn = ttk.Button(top_frame, text=t["lang_btn"], width=8,
                                   command=self._switch_lang)
        self.lang_btn.pack(side="right")

        # --- City buttons ---
        self.city_frame = ttk.LabelFrame(self.root, text=t["city_frame"], padding=8)
        self.city_frame.pack(fill="x", padx=12, pady=(0, 8))
        inner = ttk.Frame(self.city_frame)
        inner.pack()
        self.city_buttons = []
        cities = [("Guangdong", "Guangdong"), ("Zhanjiang", "Zhanjiang"),
                  ("Guangzhou", "Guangzhou"), ("Jieyang", "Jieyang")]
        for label, q in cities:
            btn = ttk.Button(inner, text=label, width=12,
                             command=lambda v=q: self.select(v))
            btn.pack(side="left", padx=4)
            self.city_buttons.append((btn, label))

        # --- Controls ---
        self.ctrl_frame = ttk.LabelFrame(self.root, text=t["controls_frame"], padding=8)
        self.ctrl_frame.pack(fill="x", padx=12, pady=(0, 8))
        cl = ttk.Frame(self.ctrl_frame)
        cl.pack(side="left", fill="x", expand=True)
        self.cb = ttk.Checkbutton(cl, text=t["auto_cb"],
                                  variable=self.auto_enabled, command=self._toggle)
        self.cb.pack(side="left", padx=(0, 12))
        self.cd = ttk.Label(cl, text=t["off"], foreground="#999",
                            font=("Microsoft YaHei", 9))
        self.cd.pack(side="left")
        self.rb = ttk.Button(self.ctrl_frame, text=t["refresh_btn"], command=self.refresh)
        self.rb.pack(side="right", padx=4)

        # --- Weather info ---
        self.weather_frame = ttk.LabelFrame(self.root, text=t["weather_frame"], padding=6)
        self.weather_frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        self.ta = scrolledtext.ScrolledText(self.weather_frame, wrap="word",
                                             font=("Consolas", 10),
                                             bg="#1e1e2e", fg="#cdd6f4",
                                             relief="flat", borderwidth=0)
        self.ta.pack(fill="both", expand=True)
        self.ta.insert("1.0", t["loading"] + "\n")
        self.ta.config(state="disabled")

        # --- Status bar ---
        self.sb = ttk.Label(self.root, text=t["ready"], relief="sunken", anchor="w",
                            font=("Microsoft YaHei", 9), padding=(6, 2))
        self.sb.pack(side="bottom", fill="x")

    def _switch_lang(self):
        self.lang = "zh" if self.lang == "en" else "en"
        self._apply_lang()
        self.refresh()

    def _apply_lang(self):
        t = T[self.lang]
        self.root.title(t["title"])
        self.title_label.config(text=t["title"])
        self.subtitle_label.config(text=t["subtitle"])
        self.lang_btn.config(text=t["lang_btn"])
        self.city_frame.config(text=t["city_frame"])
        self.ctrl_frame.config(text=t["controls_frame"])
        self.cb.config(text=t["auto_cb"])
        self.weather_frame.config(text=t["weather_frame"])
        if self.auto_enabled.get():
            self.cd.config(text=self._countdown_text(self._countdown_value()))
        else:
            self.cd.config(text=t["off"])
        if not self.busy:
            self.rb.config(text=t["refresh_btn"])
            self.sb.config(text=t["ready"])
        self._set_text(t["loading"] + "\n", clear=True)

    def _countdown_value(self):
        return 60  # default, will be overridden by _schedule

    def _countdown_text(self, n):
        t = T[self.lang]
        return f"{t['next']}{n}s"

    def select(self, city):
        self.location.set(city)
        self.refresh()

    def refresh(self):
        if self.busy:
            return
        self.busy = True
        t = T[self.lang]
        self.rb.config(state="disabled", text=t["fetching"])
        self.sb.config(text=t["fetching_status"])
        self._set_text(t["fetching"] + "\n", clear=True)
        city = self.location.get()
        threading.Thread(target=self._worker, args=(city, self.lang), daemon=True).start()

    def _worker(self, city, lang):
        result = fetch_weather(city, lang)
        ts = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, self._show, result, ts)

    def _show(self, text, ts):
        t = T[self.lang]
        self._set_text(text, clear=True)
        self.rb.config(state="normal", text=t["refresh_btn"])
        self.sb.config(text=f"{t['updated']}{ts}")
        self.busy = False

    def _set_text(self, text, clear=False):
        self.ta.config(state="normal")
        if clear:
            self.ta.delete("1.0", "end")
        self.ta.insert("end", text)
        self.ta.see("1.0")
        self.ta.config(state="disabled")

    def _toggle(self):
        t = T[self.lang]
        if self.auto_enabled.get():
            self.cd.config(text=f"{t['next']}60s", foreground="#40a02b")
            self._schedule(60)
        else:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.cd.config(text=t["off"], foreground="#999")

    def _schedule(self, n):
        if not self.auto_enabled.get():
            return
        t = T[self.lang]
        if n <= 0:
            self.cd.config(text=t["refreshing"], foreground="#fe640b")
            self.refresh()
            self._schedule(60)
        else:
            self.cd.config(text=f"{t['next']}{n}s", foreground="#40a02b")
            self.timer_id = self.root.after(1000, self._schedule, n - 1)


if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
