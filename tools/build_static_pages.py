#!/usr/bin/env python3
"""Put the hand-written info pages (/o-nas/, /dostavka-i-oplata/) into the shared site shell:
the same header with the dropdown menu, cart, search, footer and scripts as the home page.

The page's own <head> (title, description, canonical, JSON-LD) and <main> content are kept as they are,
so the script can be re-run after any change to the home page header:
    python3 tools/build_static_pages.py
"""
import re

from build_boxes_page import SITE, home_shell

PAGES = ["o-nas", "dostavka-i-oplata"]


def build():
    metrika, header, bottom, scripts, styles_css = home_shell()
    for slug in PAGES:
        path = SITE / slug / "index.html"
        page = path.read_text(encoding="utf-8")
        head = page[page.index("<title>"):page.index("</head>")]
        head = re.sub(r'<link rel="stylesheet" href="/css/styles\.css[^"]*">', "", head)
        head = head.replace('<link rel="stylesheet" href="/css/seo-pages.css',
                            f'<link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css', 1)
        main = page[page.index("<main"):page.index("</main>") + len("</main>")]
        out = ('<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
               f'{metrika}{head}</head><body>\n{header}\n{main}\n{bottom}{scripts}</body></html>\n')
        path.write_text(out, encoding="utf-8")
        print(f"site/{slug}/index.html")


if __name__ == "__main__":
    build()
