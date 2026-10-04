# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import threading
import csv
import webbrowser

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free API Finder VIP - Clean Edition")
        self.geometry("1100x650")
        self.apis = []
        self.create_ui()

    def create_ui(self):
        top = tk.Frame(self, bg="#1a1a2e", height=60)
        top.pack(fill="x")
        tk.Label(top, text="Free API Finder VIP - Clean Edition", bg="#1a1a2e", fg="#00d9ff", font=("Arial", 16, "bold")).pack(pady=15)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)
        tk.Button(btn_frame, text="Start Search", bg="#00b894", fg="white", width=15, command=self.start_search).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Health Check", bg="#6c5ce7", fg="white", width=15, command=self.start_health).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export JSON", command=self.export_json).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side="right", padx=5)

        cols = ("name", "category", "auth", "status", "link")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        self.tree.heading("name", text="Name / Model")
        self.tree.heading("category", text="Category")
        self.tree.heading("auth", text="Auth")
        self.tree.heading("status", text="Status")
        self.tree.heading("link", text="Endpoint")
        self.tree.column("name", width=250)
        self.tree.column("category", width=100)
        self.tree.column("auth", width=120)
        self.tree.column("status", width=100)
        self.tree.column("link", width=400)
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
        self.status.config(text="Searching...")
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self.fetch_all, daemon=True).start()

    def fetch_all(self):
        apis = []
        try:
            r = requests.get("https://api.publicapis.org/entries", timeout=15).json()
            for e in r.get("entries", [])[:80]:
                auth = e.get("Auth")
                if not auth:
                    auth = "No Auth"
                apis.append((e.get("API"), e.get("Category"), auth, "Not Tested", e.get("Link")))
        except Exception as ex:
            print("Public API error:", ex)
        try:
            r = requests.get("https://openrouter.ai/api/v1/models", timeout=15).json()
            for m in r.get("data", []):
                mid = m.get("id", "")
                if ":free" in mid:
                    apis.append((mid, "AI - LLM", "Free Key", "Not Tested", "https://openrouter.ai/api/v1/chat/completions"))
        except Exception as ex:
            print("OpenRouter error:", ex)
        self.apis = apis
        self.after(0, lambda: self.update_table(apis))

    def update_table(self, apis):
        for row in apis:
            self.tree.insert("", "end", values=row)
        self.status.config(text="Found: " + str(len(apis)) + " free APIs - Double click to open docs")

    def start_health(self):
        self.status.config(text="Checking health...")
        threading.Thread(target=self.health_check, daemon=True).start()

    def health_check(self):
        for item in self.tree.get_children():
            url = self.tree.item(item, "values")[4]
            try:
                res = requests.get(url, timeout=8)
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
            data = [{"name": a[0], "category": a[1], "auth": a[2], "link": a[4]} for a in self.apis]
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
                w.writerow(["name", "category", "auth", "link"])
                w.writerows([(a[0], a[1], a[2], a[4]) for a in self.apis])
            messagebox.showinfo("Success", "CSV saved!")

if __name__ == "__main__":
    app = App()
    app.mainloop()