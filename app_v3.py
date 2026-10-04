# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import threading
import csv
import webbrowser

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
    ("Genderize - Guess Gender", "Data", "No Auth", "Not Tested", "https://api.genderize.io?name=michael"),
    ("Nationalize - Guess Nationality", "Data", "No Auth", "Not Tested", "https://api.nationalize.io?name=michael"),
    ("IPify - Get IP", "IP", "No Auth", "Not Tested", "https://api.ipify.org?format=json"),
    ("Zippopotam - ZipCode 90210", "Geo", "No Auth", "Not Tested", "https://api.zippopotam.us/us/90210"),
    ("Open-Meteo Weather", "Weather", "No Auth", "Not Tested", "https://api.open-meteo.com/v1/forecast?latitude=35.68&longitude=51.41&current_weather=true"),
    ("HTTPBin - Test Endpoint", "Test", "No Auth", "Not Tested", "https://httpbin.org/get"),
    ("GitHub User API", "GitHub", "No Auth", "Not Tested", "https://api.github.com/users/github"),
    ("Dictionary API", "Education", "No Auth", "Not Tested", "https://api.dictionaryapi.dev/api/v2/entries/en/hello"),
    ("Universities List", "Education", "No Auth", "Not Tested", "http://universities.hipolabs.com/search?country=United+States"),
    ("Public APIs - Via GitHub Raw", "Anthropic", "No Auth", "Not Tested", "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"),
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free API Finder VIP v2 - Extended Sources")
        self.geometry("1150x680")
        self.apis = []
        self.create_ui()

    def create_ui(self):
        top = tk.Frame(self, bg="#1a1a2e", height=60)
        top.pack(fill="x")
        tk.Label(top, text="Free API Finder VIP v2 - 70+ Working Free APIs", bg="#1a1a2e", fg="#00d9ff", font=("Arial", 14, "bold")).pack(pady=15)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)
        tk.Button(btn_frame, text="Start Search (Extended)", bg="#00b894", fg="white", width=22, command=self.start_search).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Health Check", bg="#6c5ce7", fg="white", width=15, command=self.start_health).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export JSON", command=self.export_json).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side="right", padx=5)

        self.search_var = tk.StringVar()
        tk.Entry(btn_frame, textvariable=self.search_var, width=20).pack(side="right", padx=10)
        tk.Label(btn_frame, text="Search:").pack(side="right")

        cols = ("name", "category", "auth", "status", "link")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        self.tree.heading("name", text="Name / Model")
        self.tree.heading("category", text="Category")
        self.tree.heading("auth", text="Auth")
        self.tree.heading("status", text="Status")
        self.tree.heading("link", text="Endpoint")
        self.tree.column("name", width=300)
        self.tree.column("category", width=110)
        self.tree.column("auth", width=110)
        self.tree.column("status", width=100)
        self.tree.column("link", width=420)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.open_link)

        self.status = tk.Label(self, text="Ready - Click Start Search", anchor="w", fg="gray")
        self.status.pack(fill="x", padx=10, pady=5)

    def open_link(self, event):
        sel = self.tree.selection()
        if sel:
            url = self.tree.item(sel[0], "values")[4]
            webbrowser.open(url)

    def start_search(self):
        self.status.config(text="Searching from 4 sources...")
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self.fetch_all, daemon=True).start()

    def fetch_all(self):
        apis = []
        # 1. Add curated list first - always works
        apis.extend(CURATED_APIS)

        # 2. Try OpenRouter Free Models
        try:
            r = requests.get("https://openrouter.ai/api/v1/models", timeout=12).json()
            for m in r.get("data", [])[:30]:
                mid = m.get("id", "")
                if ":free" in mid:
                    apis.append((mid, "AI - LLM", "Free Key", "Not Tested", "https://openrouter.ai/api/v1/chat/completions"))
        except Exception as ex:
            print("OpenRouter error:", ex)

        # 3. Try HuggingFace Top Models
        try:
            r = requests.get("https://huggingface.co/api/models?limit=15&sort=downloads&filter=text-generation", timeout=12).json()
            for m in r[:15]:
                mid = m.get("id", "")
                apis.append((mid, "AI - HF Free", "Free Key", "Not Tested", "https://api-inference.huggingface.co/models/" + mid))
        except Exception as ex:
            print("HF error:", ex)

        # 4. Try PublicAPIs with fallback
        try:
            r = requests.get("https://api.publicapis.org/entries", timeout=10).json()
            for e in r.get("entries", [])[:30]:
                auth = e.get("Auth")
                if not auth:
                    auth = "No Auth"
                apis.append((e.get("API"), e.get("Category"), auth, "Not Tested", e.get("Link")))
        except:
            pass

        self.apis = apis
        self.after(0, lambda: self.update_table(apis))

    def update_table(self, apis):
        q = self.search_var.get().lower()
        count = 0
        for row in apis:
            if q and q not in row[0].lower() and q not in row[1].lower():
                continue
            self.tree.insert("", "end", values=row)
            count += 1
        self.status.config(text="Found: " + str(count) + " APIs (Total " + str(len(apis)) + ") - Double click to open docs")

    def start_health(self):
        self.status.config(text="Checking health... please wait 10 sec")
        threading.Thread(target=self.health_check, daemon=True).start()

    def health_check(self):
        for item in self.tree.get_children():
            url = self.tree.item(item, "values")[4]
            try:
                res = requests.get(url, timeout=7)
                if res.status_code < 400:
                    status = "OK"
                else:
                    status = "Error " + str(res.status_code)
            except:
                status = "Offline"
            self.tree.set(item, column="status", value=status)
        self.after(0, lambda: self.status.config(text="Health check done - Green = Working"))

    def export_json(self):
        if not self.apis:
            messagebox.showwarning("Warning", "No data yet")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            data = [{"name": a[0], "category": a[1], "auth": a[2], "status": a[3], "link": a[4]} for a in self.apis]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "JSON saved!")

    def export_csv(self):
        if not self.apis:
            messagebox.showwarning("Warning", "No data yet")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["name", "category", "auth", "status", "link"])
                w.writerows(self.apis)
            messagebox.showinfo("Success", "CSV saved!")

if __name__ == "__main__":
    app = App()
    app.mainloop()