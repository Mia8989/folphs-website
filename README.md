# folphs.org

Static website for Friends of Lincoln Park High School (FOLPHS), replacing the Wix site.

- Edit content in `build.py`, then run `python3 build.py`. Pages are written to `<page>/index.html` for clean URLs.
- Styles: `assets/site.css`. Images: `assets/img/`. Meeting minutes: `minutes/` (listed from `minutes/index.json`).
- Online donation link: set `DONATE_URL` in `build.py` when it's ready; every Donate button updates.
- Old Wix URLs redirect to the new pages (see `REDIRECTS` in `build.py`).
- When folphs.org points here: set `SITE_BASE = "/"` in `build.py`, add a `CNAME` file containing `www.folphs.org`, rebuild.
