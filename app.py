# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import threading
import csv
import webbrowser
import os
import urllib.parse
import re

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
    except:
        return False

def mask_key(k):
    if len(k) <= 8:
        return "***"
    return k[:6] + "***" + k[-4:]

def standardize_url(raw_url):
    if not raw_url:
        return ""
    s = str(raw_url).strip()
    low = s.lower()
    i1 = low.find("https://")
    i2 = low.find("http://")
    start = -1
    if i1 != -1 and i2 != -1:
        start = i1 if i1 < i2 else i2
    elif i1 != -1:
        start = i1
    elif i2 != -1:
        start = i2
    else:
        return ""
    s = s[start:]
    m = re.search(r"https?://\S+", s)
    if not m:
        return ""
    url = m.group(0)
    bad_chars = chr(34) + chr(39) + ".,;!?)]}"
    while url and url[-1] in bad_chars:
        url = url[:-1]
    try:
        p = urllib.parse.urlparse(url)
        if not p.netloc:
            return url
        return p.scheme.lower() + "://" + p.netloc.lower() + "/"
    except:
        return url

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free API Finder VIP v6.2 - Fixed")
        self.geometry("1240x700")
        self.apis = []
        self.my_keys = load_json(KEYS_FILE, [])
        self.custom_sources = load_json(SOURCES_FILE, [])
        self.create_ui()
        self.refresh_keys_table()
        self.refresh_sources_table()

    def create_ui(self):
        top = tk.Frame(self, bg="#1a1a2e", height=50)
        top.pack(fill="x")
        tk.Label(top, text="Free API Finder VIP v6.2 - Standardized Link Fixed", bg="#1a1a2e", fg="#00d9ff", font=("Arial", 13, "bold")).pack(pady=12)
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
        tk.Button(btn, text="Start Search", bg="#00b894", fg="white", width=14, command=self.start_search).pack(side="left", padx=5)
        tk.Button(btn, text="Smart Health Check", bg="#6c5ce7", fg="white", width=16, command=self.start_health).pack(side="left", padx=5)
        tk.Button(btn, text="Export JSON", command=self.export_json).pack(side="right", padx=5)
        tk.Button(btn, text="Export CSV", command=self.export_csv).pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(btn, textvariable=self.search_var, width=16).pack(side="right", padx=8)
        tk.Label(btn, text="Search:").pack(side="right")
        cols = ("name", "category", "auth", "key", "status", "link", "share")
        self.tree = ttk.Treeview(self.tab_finder, columns=cols, show="headings")
        self.tree.heading("name", text="Name / Model")
        self.tree.heading("category", text="Category")
        self.tree.heading("auth", text="Auth")
        self.tree.heading("key", text="My Key")
        self.tree.heading("status", text="Smart Status")
        self.tree.heading("link", text="Endpoint (Click to Open)")
        self.tree.heading("share", text="Share")
        self.tree.column("name", width=240)
        self.tree.column("category", width=90)
        self.tree.column("auth", width=90)
        self.tree.column("key", width=110)
        self.tree.column("status", width=160)
        self.tree.column("link", width=360)
        self.tree.column("share", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.tag_configure("link", foreground="#00a8ff")
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Motion>", self.on_motion)
        self.status = tk.Label(self.tab_finder, text="Click BLUE link = opens https://domain/ | Share uses same clean link", anchor="w", fg="gray")
        self.status.pack(fill="x", padx=5, pady=2)

    def on_motion(self, event):
        col = self.tree.identify_column(event.x)
        if col in ("#6", "#7"):
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")

    def on_tree_click(self, event):
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id:
            return
        vals = self.tree.item(row_id, "values")
        if not vals or len(vals) < 7:
            return
        raw_url = vals[5]
        std_url = standardize_url(raw_url)
        name = vals[0]
        if col == "#6":
            if std_url.startswith("http"):
                webbrowser.open(std_url)
            else:
                messagebox.showwarning("Link Error", "لينک معتبر نيست: " + raw_url)
        elif col == "#7":
            self.show_share_popup(name, raw_url, std_url)

    def on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            if len(vals) >= 6:
                std_url = standardize_url(vals[5])
                if std_url.startswith("http"):
                    webbrowser.open(std_url)

    def show_share_popup(self, name, raw_url, std_url):
        win = tk.Toplevel(self)
        win.title("Share")
        win.geometry("520x300")
        win.transient(self)
        win.grab_set()
        tk.Label(win, text=name, font=("Arial", 10, "bold"), wraplength=480).pack(pady=8)
        tk.Label(win, text="Original:", fg="gray").pack()
        tk.Label(win, text=raw_url, fg="gray", wraplength=480, font=("Arial", 8)).pack()
        tk.Label(win, text="Standardized (will be shared):", fg="#00b894").pack(pady=(8,0))
        tk.Label(win, text=std_url, fg="#00a8ff", wraplength=480, font=("Arial", 9, "bold")).pack(pady=4)
        e = tk.Entry(win, width=62)
        e.insert(0, std_url)
        e.pack(pady=5)
        e.config(state="readonly")
        def do_copy():
            self.clipboard_clear()
            self.clipboard_append(std_url)
            messagebox.showinfo("Copied", "لينک استاندارد کپي شد:\n" + std_url)
        def do_whatsapp():
            text = urllib.parse.quote(name + " - " + std_url)
            webbrowser.open("https://wa.me/?text=" + text)
        def do_telegram():
            webbrowser.open("https://t.me/share/url?url=" + urllib.parse.quote(std_url) + "&text=" + urllib.parse.quote(name))
        def do_system():
            try:
                from plyer import share
                share.share(text=name + " - " + std_url)
            except:
                webbrowser.open("mailto:?subject=" + urllib.parse.quote(name) + "&body=" + urllib.parse.quote(std_url))
                messagebox.showinfo("Share", "On Android install plyer for native share. Opened Email instead.")
        btnf = tk.Frame(win)
        btnf.pack(pady=12)
        tk.Button(btnf, text="Copy Link", command=do_copy, width=12, bg="#2d3436", fg="white").pack(side="left", padx=5)
        tk.Button(btnf, text="WhatsApp", bg="#25D366", fg="white", width=12, command=do_whatsapp).pack(side="left", padx=5)
        tk.Button(btnf, text="Telegram", bg="#0088cc", fg="white", width=12, command=do_telegram).pack(side="left", padx=5)
        tk.Button(win, text="System Share (Android)", bg="#6c5ce7", fg="white", width=30, command=do_system).pack(pady=5)

    def build_keys(self):
        tk.Label(self.tab_keys, text="Add your free keys - saved forever", fg="gray").pack(pady=5)
        f = tk.Frame(self.tab_keys)
        f.pack(fill="x", padx=10, pady=8)
        tk.Label(f, text="Provider:").pack(side="left")
        self.key_provider = ttk.Combobox(f, values=["OpenRouter", "Groq", "Gemini", "HuggingFace", "Other"], width=14)
        self.key_provider.set("OpenRouter")
        self.key_provider.pack(side="left", padx=5)
        tk.Label(f, text="API Key:").pack(side="left", padx=(10,2))
        self.key_entry = tk.Entry(f, width=45)
        self.key_entry.pack(side="left", padx=5)
        tk.Button(f, text="Add / Save", bg="#00b894", fg="white", command=self.add_key).pack(side="left", padx=5)
        tk.Button(f, text="Delete", command=self.delete_key).pack(side="left", padx=5)
        tk.Button(f, text="Test Selected Key", bg="#6c5ce7", fg="white", command=self.test_selected_key).pack(side="left", padx=5)
        cols = ("provider", "key", "status")
        self.keys_tree = ttk.Treeview(self.tab_keys, columns=cols, show="headings", height=12)
        self.keys_tree.heading("provider", text="Provider")
        self.keys_tree.heading("key", text="Key (masked)")
        self.keys_tree.heading("status", text="Last Test Result")
        self.keys_tree.column("provider", width=150)
        self.keys_tree.column("key", width=400)
        self.keys_tree.column("status", width=200)
        self.keys_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.keys_log = tk.Text(self.tab_keys, height=7)
        self.keys_log.pack(fill="x", padx=10, pady=5)
        self.keys_log.insert("1.0", "Where to get FREE keys:\n- Groq: console.groq.com/keys\n- OpenRouter: openrouter.ai/keys\n- Gemini: aistudio.google.com/app/apikey\n- HuggingFace: huggingface.co/settings/tokens\n")

    def build_sources(self):
        tk.Label(self.tab_sources, text="Add your URL - will be standardized to https://domain/", fg="gray").pack(pady=5)
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
        tk.Button(f, text="Delete", command=self.delete_source).pack(side="left", padx=5)
        cols = ("name", "category", "url")
        self.sources_tree = ttk.Treeview(self.tab_sources, columns=cols, show="headings", height=15)
        self.sources_tree.heading("name", text="Name")
        self.sources_tree.heading("category", text="Category")
        self.sources_tree.heading("url", text="URL (Standardized)")
        self.sources_tree.column("name", width=200)
        self.sources_tree.column("category", width=120)
        self.sources_tree.column("url", width=600)
        self.sources_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_keys_table(self):
        for i in self.keys_tree.get_children():
            self.keys_tree.delete(i)
        for item in self.my_keys:
            self.keys_tree.insert("", "end", values=(item.get("provider"), mask_key(item.get("key","")), item.get("status","Saved")))

    def refresh_sources_table(self):
        for i in self.sources_tree.get_children():
            self.sources_tree.delete(i)
        for s in self.custom_sources:
            self.sources_tree.insert("", "end", values=(s.get("name"), s.get("category"), standardize_url(s.get("url"))))

    def add_key(self):
        prov = self.key_provider.get().strip()
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Warning", "Enter key")
            return
        self.my_keys.append({"provider": prov, "key": key, "status": "Saved - Click Test"})
        save_json(KEYS_FILE, self.my_keys)
        self.refresh_keys_table()
        self.key_entry.delete(0, "end")

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
            messagebox.showwarning("Warning", "Select a key first")
            return
        idx = self.keys_tree.index(sel[0])
        item = self.my_keys[idx]
        prov = item.get("provider")
        key = item.get("key")
        self.keys_log.insert("end", "\n>> Testing " + prov + " ...\n")
        self.keys_log.see("end")
        threading.Thread(target=self._test_key_thread, args=(idx, prov, key), daemon=True).start()

    def _test_key_thread(self, idx, prov, key):
        msg = "Unknown"
        try:
            if prov == "OpenRouter":
                r = requests.get("https://openrouter.ai/api/v1/models", headers={"Authorization": "Bearer " + key}, timeout=12)
                if r.status_code == 200:
                    msg = "Valid - Models: " + str(len(r.json().get("data", [])))
                elif r.status_code == 401:
                    msg = "Invalid Key (401)"
                else:
                    msg = "Failed " + str(r.status_code)
            elif prov == "Groq":
                r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": "Bearer " + key}, timeout=12)
                if r.status_code == 200:
                    msg = "Valid - Groq OK"
                elif r.status_code == 401:
                    msg = "Invalid Key (401)"
                else:
                    msg = "Failed " + str(r.status_code)
            elif prov == "Gemini":
                r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?key=" + key, timeout=12)
                if r.status_code == 200:
                    msg = "Valid - Gemini OK"
                else:
                    msg = "Invalid Key (" + str(r.status_code) + ")"
            elif prov == "HuggingFace":
                r = requests.get("https://huggingface.co/api/whoami-v2", headers={"Authorization": "Bearer " + key}, timeout=12)
                if r.status_code == 200:
                    msg = "Valid - HF"
                elif r.status_code == 401:
                    msg = "Invalid Token (401)"
                else:
                    msg = "Failed " + str(r.status_code)
            else:
                msg = "Saved - No auto test"
        except Exception as e:
            msg = "Error: " + str(e)
        self.my_keys[idx]["status"] = msg
        save_json(KEYS_FILE, self.my_keys)
        self.after(0, lambda: self.refresh_keys_table())
        self.after(0, lambda: self.keys_log.insert("end", msg + "\n"))

    def add_source(self):
        name = self.src_name.get().strip()
        cat = self.src_cat.get().strip()
        url = self.src_url.get().strip()
        if not name or not url:
            messagebox.showwarning("Warning", "Enter name and URL")
            return
        std = standardize_url(url)
        if not std.startswith("http"):
            messagebox.showwarning("Warning", "URL بايد با http شروع شود")
            return
        self.custom_sources.append({"name": name, "category": cat, "url": std})
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

    def find_key_for_api(self, name, category):
        name_low = (name + " " + category).lower()
        for k in self.my_keys:
            prov = k.get("provider","").lower()
            if prov == "other":
                continue
            if prov in name_low:
                return k.get("key")
            if prov == "huggingface" and "hf" in name_low:
                return k.get("key")
            if prov == "openrouter" and "openrouter" in name_low:
                return k.get("key")
        return None

    def start_search(self):
        self.status.config(text="Searching...")
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self.fetch_all, daemon=True).start()

    def fetch_all(self):
        apis = []
        for n,c,a,s,u in CURATED_APIS:
            apis.append((n,c,a,s,standardize_url(u)))
        for s in self.custom_sources:
            apis.append((s.get("name"), s.get("category"), "Custom", "Not Tested", standardize_url(s.get("url"))))
        try:
            r = requests.get("https://openrouter.ai/api/v1/models", timeout=12).json()
            for m in r.get("data", [])[:25]:
                mid = m.get("id", "")
                if ":free" in mid:
                    apis.append((mid, "AI - LLM", "Free Key", "Not Tested", "https://openrouter.ai/"))
        except: pass
        try:
            r = requests.get("https://huggingface.co/api/models?limit=12&sort=downloads&filter=text-generation", timeout=12).json()
            for m in r[:12]:
                mid = m.get("id", "")
                apis.append((mid, "AI - HF", "Free Key", "Not Tested", "https://huggingface.co/"))
        except: pass
        self.apis = apis
        self.after(0, lambda: self.update_table(apis))

    def update_table(self, apis):
        q = self.search_var.get().lower()
        count = 0
        for row in apis:
            if q and q not in row[0].lower() and q not in row[1].lower():
                continue
            std_link = standardize_url(row[4])
            key_info = self.find_key_for_api(row[0], row[1])
            if row[2] == "No Auth":
                key_disp = "- No Key Needed"
            elif key_info:
                key_disp = mask_key(key_info)
            else:
                key_disp = "No Key Saved"
            display = (row[0], row[1], row[2], key_disp, row[3], std_link, "Share")
            self.tree.insert("", "end", values=display, tags=("link",))
            count += 1
        self.status.config(text="Found: " + str(count) + " APIs (Standardized)")

    def start_health(self):
        self.status.config(text="Smart checking...")
        threading.Thread(target=self.health_check, daemon=True).start()

    def health_check(self):
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            name = vals[0]
            category = vals[1]
            auth = vals[2]
            url = standardize_url(vals[5])
            key = self.find_key_for_api(name, category)
            try:
                if auth == "No Auth":
                    r = requests.get(url, timeout=7)
                    if r.status_code < 400:
                        status = "Live - Free No Key"
                    else:
                        status = "Offline (" + str(r.status_code) + ")"
                else:
                    if key:
                        r = requests.get(url, headers={"Authorization": "Bearer " + key}, timeout=7)
                        if r.status_code < 400:
                            status = "Live - Your Key OK"
                        elif r.status_code in (401, 403):
                            status = "Key Invalid (401)"
                        else:
                            status = "Live but Error " + str(r.status_code)
                    else:
                        r = requests.get(url, timeout=7)
                        if r.status_code in (401, 403):
                            status = "Live - Needs Key"
                        elif r.status_code < 400:
                            status = "Live - Free?"
                        else:
                            status = "Offline (" + str(r.status_code) + ")"
            except:
                status = "Offline"
            self.tree.set(item, column="status", value=status)
        self.after(0, lambda: self.status.config(text="Smart check done - All links are standardized"))

    def export_json(self):
        if not self.apis:
            messagebox.showwarning("Warning", "No data yet")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            data = []
            for a in self.apis:
                ki = self.find_key_for_api(a[0], a[1])
                data.append({"name": a[0], "category": a[1], "auth": a[2], "my_key": mask_key(ki) if ki else "", "link": standardize_url(a[4]), "link_raw": a[4]})
            out = {"apis": data, "my_keys": self.my_keys, "custom_sources": self.custom_sources}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "JSON saved (Standardized links)!")

    def export_csv(self):
        if not self.apis:
            messagebox.showwarning("Warning", "No data yet")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["name", "category", "auth", "my_key", "link_standardized"])
                for a in self.apis:
                    ki = self.find_key_for_api(a[0], a[1])
                    w.writerow([a[0], a[1], a[2], mask_key(ki) if ki else "", standardize_url(a[4])])
            messagebox.showinfo("Success", "CSV saved!")

if __name__ == "__main__":
    app = App()
    app.mainloop()