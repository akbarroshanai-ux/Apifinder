# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import threading
import csv
import webbrowser
import os

CURATED_APIS = [
    ("Pollinations AI Chat - FREE No Key", "AI", "No Auth", "Not Tested", "https://text.pollinations.ai/hello"),
    ("Pollinations Image - FREE No Key", "AI Images", "No Auth", "Not Tested", "https://image.pollinations.ai/prompt/beautiful%20landscape"),
    ("Dog CEO - Random Dog", "Animals", "No Auth", "Not Tested", "https://dog.ceo/api/breeds/image/random"),
    ("TheCatAPI - Random Cat", "Animals", "No Auth", "Not Tested", "https://api.thecatapi.com/v1/images/search"),
    ("Jikan - Anime API", "Anime", "No Auth", "Not Tested", "https://api.jikan.moe/v4/anime/1"),
    ("CoinGecko Ping", "Crypto", "No Auth", "Not Tested", "https://api.coingecko.com/api/v3/ping"),
    ("CoinDesk Bitcoin Price", "Crypto", "No Auth", "Not Tested", "https://api.coindesk.com/v1/bpi/currentprice.json"),
    ("RestCountries - All Countries", "Data", "No Auth", "Not Tested", "https://restcountries.com/v3.1/all"),
    ("JSONPlaceholder - Posts", "Fake Data", "No Auth", "Not Tested", "https://jsonplaceholder.typicode.com/posts/1"),
    ("DummyJSON - Products", "Fake Data", "No Auth", "Not Tested", "https://dummyjson.com/products/1"),
    ("Quotable - Random Quote", "Quotes", "No Auth", "Not Tested", "https://api.quotable.io/random"),
    ("Official Joke API", "Jokes", "No Auth", "Not Tested", "https://official-joke-api.appspot.com/random_joke"),
    ("Bored API - Activity", "Fun", "No Auth", "Not Tested", "https://www.boredapi.com/api/activity"),
    ("Agify - Guess Age", "Data", "No Auth", "Not Tested", "https://api.agify.io?name=michael"),
    ("IPify - Get IP", "IP", "No Auth", "Not Tested", "https://api.ipify.org?format=json"),
    ("Open-Meteo Weather", "Weather", "No Auth", "Not Tested", "https://api.open-meteo.com/v1/forecast?latitude=35.68&longitude=51.41&current_weather=true"),
    ("HTTPBin - Test Endpoint", "Test", "No Auth", "Not Tested", "https://httpbin.org/get"),
    ("GitHub User API", "GitHub", "No Auth", "Not Tested", "https://api.github.com/users/github"),
    ("Dictionary API", "Education", "No Auth", "Not Tested", "https://api.dictionaryapi.dev/api/v2/entries/en/hello"),
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(BASE_DIR, "my_keys.json")
SOURCES_FILE = os.path.join(BASE_DIR, "custom_sources.json")

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("save error", e)
        return False

def mask_key(k):
    if len(k) <= 8:
        return "***"
    return k[:6] + "***" + k[-4:]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free API Finder VIP v3 - With Keys & Custom Sources")
        self.geometry("1180x700")
        self.apis = []
        self.my_keys = load_json(KEYS_FILE, [])
        self.custom_sources = load_json(SOURCES_FILE, [])
        self.create_ui()
        self.refresh_keys_table()
        self.refresh_sources_table()

    def create_ui(self):
        top = tk.Frame(self, bg="#1a1a2e", height=50)
        top.pack(fill="x")
        tk.Label(top, text="Free API Finder VIP v3 - Keys + Custom Sources", bg="#1a1a2e", fg="#00d9ff", font=("Arial", 13, "bold")).pack(pady=12)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_finder = tk.Frame(nb)
        self.tab_keys = tk.Frame(nb)
        self.tab_sources = tk.Frame(nb)
        nb.add(self.tab_finder, text="  Finder  ")
        nb.add(self.tab_keys, text="  My Keys  ")
        nb.add(self.tab_sources, text="  Custom Sources  ")

        self.build_finder()
        self.build_keys()
        self.build_sources()

    def build_finder(self):
        btn = tk.Frame(self.tab_finder)
        btn.pack(fill="x", pady=8)
        tk.Button(btn, text="Start Search (Extended)", bg="#00b894", fg="white", width=20, command=self.start_search).pack(side="left", padx=5)
        tk.Button(btn, text="Health Check", bg="#6c5ce7", fg="white", width=14, command=self.start_health).pack(side="left", padx=5)
        tk.Button(btn, text="Export JSON (+Keys)", command=self.export_json).pack(side="right", padx=5)
        tk.Button(btn, text="Export CSV (+Keys)", command=self.export_csv).pack(side="right", padx=5)

        self.search_var = tk.StringVar()
        tk.Entry(btn, textvariable=self.search_var, width=18).pack(side="right", padx=8)
        tk.Label(btn, text="Search:").pack(side="right")

        cols = ("name", "category", "auth", "key", "status", "link")
        self.tree = ttk.Treeview(self.tab_finder, columns=cols, show="headings")
        self.tree.heading("name", text="Name / Model")
        self.tree.heading("category", text="Category")
        self.tree.heading("auth", text="Auth")
        self.tree.heading("key", text="My Key")
        self.tree.heading("status", text="Status")
        self.tree.heading("link", text="Endpoint")
        self.tree.column("name", width=280)
        self.tree.column("category", width=100)
        self.tree.column("auth", width=100)
        self.tree.column("key", width=120)
        self.tree.column("status", width=90)
        self.tree.column("link", width=380)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.open_link)

        self.status = tk.Label(self.tab_finder, text="Ready - Click Start Search", anchor="w", fg="gray")
        self.status.pack(fill="x", padx=5, pady=4)

    def build_keys(self):
        tk.Label(self.tab_keys, text="کلیدهای خود را اینجا اضافه کنید - ذخیره دائمی میشود", fg="gray").pack(pady=5)
        f = tk.Frame(self.tab_keys)
        f.pack(fill="x", padx=10, pady=8)
        tk.Label(f, text="Provider:").pack(side="left")
        self.key_provider = ttk.Combobox(f, values=["OpenRouter", "Groq", "Gemini", "HuggingFace", "Other"], width=14)
        self.key_provider.set("OpenRouter")
        self.key_provider.pack(side="left", padx=5)
        tk.Label(f, text="API Key:").pack(side="left", padx=(10,2))
        self.key_entry = tk.Entry(f, width=45)
        self.key_entry.pack(side="left", padx=5)
        tk.Button(f, text="Add / Save Key", bg="#00b894", fg="white", command=self.add_key).pack(side="left", padx=5)
        tk.Button(f, text="Delete Selected", command=self.delete_key).pack(side="left", padx=5)
        tk.Button(f, text="Test Selected", bg="#6c5ce7", fg="white", command=self.test_selected_key).pack(side="left", padx=5)

        cols = ("provider", "key", "status")
        self.keys_tree = ttk.Treeview(self.tab_keys, columns=cols, show="headings", height=12)
        self.keys_tree.heading("provider", text="Provider")
        self.keys_tree.heading("key", text="Key (masked)")
        self.keys_tree.heading("status", text="Status")
        self.keys_tree.column("provider", width=150)
        self.keys_tree.column("key", width=400)
        self.keys_tree.column("status", width=150)
        self.keys_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.keys_log = tk.Text(self.tab_keys, height=6)
        self.keys_log.pack(fill="x", padx=10, pady=5)
        self.keys_log.insert("1.0", "Guide:\n- openrouter.ai/keys\n- console.groq.com/keys\n- aistudio.google.com/app/apikey\n")

    def build_sources(self):
        tk.Label(self.tab_sources, text="سایت یا URL خود را اضافه کن تا همیشه در جستجو باشد", fg="gray").pack(pady=5)
        f = tk.Frame(self.tab_sources)
        f.pack(fill="x", padx=10, pady=8)
        tk.Label(f, text="Name:").pack(side="left")
        self.src_name = tk.Entry(f, width=18)
        self.src_name.pack(side="left", padx=4)
        tk.Label(f, text="Category:").pack(side="left")
        self.src_cat = tk.Entry(f, width=12)
        self.src_cat.insert(0, "Custom")
        self.src_cat.pack(side="left", padx=4)
        tk.Label(f, text="URL:").pack(side="left")
        self.src_url = tk.Entry(f, width=40)
        self.src_url.pack(side="left", padx=4)
        tk.Button(f, text="Add Source", bg="#00b894", fg="white", command=self.add_source).pack(side="left", padx=5)
        tk.Button(f, text="Delete Selected", command=self.delete_source).pack(side="left", padx=5)

        cols = ("name", "category", "url")
        self.sources_tree = ttk.Treeview(self.tab_sources, columns=cols, show="headings", height=15)
        self.sources_tree.heading("name", text="Name")
        self.sources_tree.heading("category", text="Category")
        self.sources_tree.heading("url", text="URL")
        self.sources_tree.column("name", width=200)
        self.sources_tree.column("category", width=120)
        self.sources_tree.column("url", width=600)
        self.sources_tree.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(self.tab_sources, text="نکته: منابع اینجا در فایل custom_sources.json ذخیره میشوند و هر بار با Start Search لود میشوند.", fg="gray").pack(pady=4)

    def refresh_keys_table(self):
        for i in self.keys_tree.get_children():
            self.keys_tree.delete(i)
        for item in self.my_keys:
            self.keys_tree.insert("", "end", values=(item.get("provider"), mask_key(item.get("key","")), item.get("status","Saved")))

    def refresh_sources_table(self):
        for i in self.sources_tree.get_children():
            self.sources_tree.delete(i)
        for s in self.custom_sources:
            self.sources_tree.insert("", "end", values=(s.get("name"), s.get("category"), s.get("url")))

    def add_key(self):
        prov = self.key_provider.get().strip()
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Warning", "کلید را وارد کن")
            return
        self.my_keys.append({"provider": prov, "key": key, "status": "Saved"})
        save_json(KEYS_FILE, self.my_keys)
        self.refresh_keys_table()
        self.key_entry.delete(0, "end")
        self.keys_log.insert("end", "\nSaved key for " + prov + " : " + mask_key(key) + "\n")

    def delete_key(self):
        sel = self.keys_tree.selection()
        if not sel:
            return
        idx = self.keys_tree.index(sel[0])
        del self.my_keys[idx]
        save_json(KEYS_FILE, self.my_keys)
        self.refresh_keys_table()

    def test_selected_key(self):
        sel = self.keys_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "یک کلید را انتخاب کن")
            return
        idx = self.keys_tree.index(sel[0])
        item = self.my_keys[idx]
        prov = item.get("provider")
        key = item.get("key")
        self.keys_log.insert("end", "\nTesting " + prov + "...\n")
        headers = {"Authorization": "Bearer " + key}
        try:
            if prov == "OpenRouter":
                r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
                if r.status_code == 200:
                    cnt = len(r.json().get("data", []))
                    msg = "OK - Models: " + str(cnt)
                else:
                    msg = "Failed " + str(r.status_code)
            elif prov == "Groq":
                r = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
                if r.status_code == 200:
                    msg = "OK - Groq valid"
                else:
                    msg = "Failed " + str(r.status_code)
            else:
                msg = "Saved - Test manually"
            self.my_keys[idx]["status"] = msg
            save_json(KEYS_FILE, self.my_keys)
            self.refresh_keys_table()
            self.keys_log.insert("end", msg + "\n")
        except Exception as e:
            self.keys_log.insert("end", "Error: " + str(e) + "\n")

    def add_source(self):
        name = self.src_name.get().strip()
        cat = self.src_cat.get().strip()
        url = self.src_url.get().strip()
        if not name or not url:
            messagebox.showwarning("Warning", "نام و URL را وارد کن")
            return
        if not url.startswith("http"):
            messagebox.showwarning("Warning", "URL باید با http شروع شود")
            return
        self.custom_sources.append({"name": name, "category": cat, "url": url})
        save_json(SOURCES_FILE, self.custom_sources)
        self.refresh_sources_table()
        self.src_name.delete(0, "end")
        self.src_url.delete(0, "end")

    def delete_source(self):
        sel = self.sources_tree.selection()
        if not sel:
            return
        idx = self.sources_tree.index(sel[0])
        del self.custom_sources[idx]
        save_json(SOURCES_FILE, self.custom_sources)
        self.refresh_sources_table()

    def open_link(self, event):
        sel = self.tree.selection()
        if sel:
            url = self.tree.item(sel[0], "values")[5]
            webbrowser.open(url)

    def get_key_status(self, api_name, auth):
        if auth == "No Auth":
            return "-"
        for k in self.my_keys:
            prov = k.get("provider", "").lower()
            if prov in api_name.lower() or (prov == "openrouter" and "openrouter" in api_name.lower()):
                return mask_key(k.get("key",""))
        if auth == "No Auth":
            return "-"
        if len(self.my_keys) > 0:
            return "Has Key"
        return "No Key"

    def start_search(self):
        self.status.config(text="Searching from 4 sources + your custom sources...")
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self.fetch_all, daemon=True).start()

    def fetch_all(self):
        apis = []
        apis.extend(CURATED_APIS)
        for s in self.custom_sources:
            apis.append((s.get("name"), s.get("category"), "Custom", "Not Tested", s.get("url")))
        try:
            r = requests.get("https://openrouter.ai/api/v1/models", timeout=12).json()
            for m in r.get("data", [])[:25]:
                mid = m.get("id", "")
                if ":free" in mid:
                    apis.append((mid, "AI - LLM", "Free Key", "Not Tested", "https://openrouter.ai/api/v1/chat/completions"))
        except Exception as ex:
            print("OpenRouter error:", ex)
        try:
            r = requests.get("https://huggingface.co/api/models?limit=12&sort=downloads&filter=text-generation", timeout=12).json()
            for m in r[:12]:
                mid = m.get("id", "")
                apis.append((mid, "AI - HF Free", "Free Key", "Not Tested", "https://api-inference.huggingface.co/models/" + mid))
        except Exception as ex:
            print("HF error:", ex)

        self.apis = apis
        self.after(0, lambda: self.update_table(apis))

    def update_table(self, apis):
        q = self.search_var.get().lower()
        count = 0
        for row in apis:
            if q and q not in row[0].lower() and q not in row[1].lower():
                continue
            key_info = self.get_key_status(row[0], row[2])
            display = (row[0], row[1], row[2], key_info, row[3], row[4])
            self.tree.insert("", "end", values=display)
            count += 1
        self.status.config(text="Found: " + str(count) + " APIs (Total " + str(len(apis)) + ") - Double click to open")

    def start_health(self):
        self.status.config(text="Checking health...")
        threading.Thread(target=self.health_check, daemon=True).start()

    def health_check(self):
        for item in self.tree.get_children():
            url = self.tree.item(item, "values")[5]
            try:
                res = requests.get(url, timeout=7)
                if res.status_code < 400:
                    status = "OK"
                else:
                    status = "Error " + str(res.status_code)
            except:
                status = "Offline"
            self.tree.set(item, column="status", value=status)
        self.after(0, lambda: self.status.config(text="Health check done"))

    def export_json(self):
        if not self.apis:
            messagebox.showwarning("Warning", "No data yet")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            data = []
            for a in self.apis:
                key_info = self.get_key_status(a[0], a[2])
                data.append({"name": a[0], "category": a[1], "auth": a[2], "my_key": key_info, "status": a[3], "link": a[4]})
            out = {"apis": data, "my_keys": self.my_keys, "custom_sources": self.custom_sources}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "JSON with keys saved!")

    def export_csv(self):
        if not self.apis:
            messagebox.showwarning("Warning", "No data yet")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["name", "category", "auth", "my_key", "status", "link"])
                for a in self.apis:
                    w.writerow([a[0], a[1], a[2], self.get_key_status(a[0], a[2]), a[3], a[4]])
            messagebox.showinfo("Success", "CSV with keys saved!")

if __name__ == "__main__":
    app = App()
    app.mainloop()