# Free API Finder VIP

Discover and health-check free public APIs — a `tkinter` desktop/Android app.

## Files

- **`app.py`** — latest version (v6.2). Start here.
- `app_v2.py` … `app_v6.py` — earlier iterations, kept for reference.
- `custom_sources.json` — user-added custom API sources.
- `FreeAPIFinder_PRO_VIP.spec` — PyInstaller build spec for packaging a Windows `.exe`.

## Run it

**Android (Pydroid 3):** open `app.py` → menu → Run → **Graphical program**.
Install `requests` first via the Pip menu if needed.

**Desktop:**

```bash
pip install requests
python app.py
```

## Security note

API keys you enter are stored locally in `my_keys.json` (plaintext) — that file
is gitignored and must never be committed to a public repo.

---
*Maintained with Husag.*
