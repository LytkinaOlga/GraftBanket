#!/usr/bin/env python3
"""Build site/furshet-na-20-chelovek/ and site/furshet-na-30-chelovek/ — ready sets for 20 and 30 guests.

The set (boxes, weight, price, cart item) is the same as on /novogodniy-korporativ-v-ofis/
(tools/build_corporate_ny_page.py, cart items setny-20 / setny-30 in js/data.js). Titles and H1
keep the wording the pages already rank with. Run after any change to those sets:
    python3 tools/build_furshet2030_pages.py
"""
import hashlib
import html
import json
import re
from datetime import date

from build_boxes_page import offer_terms, BASE, SITE, asset_version, home_shell, reviews_html, text
from build_corporate_ny_page import PHONE, money, resolve, set_card
from build_furshet10_page import grams

CORP = "/novogodniy-korporativ-v-ofis/"

PAGES = [
    {"guests": 20, "path": "/furshet-na-20-chelovek/",
     "title": "Фуршет на 20 человек в Минске — готовый набор и меню | Draft Catering",
     "h1": "Фуршет <span>на 20 человек</span> в Минске", "crumb": "Фуршет на 20 человек в Минске",
     "overline": "ПРАЗДНИК СРЕДНЕЙ КОМПАНИИ · МИНСК",
     "lead": "Готовый набор на 20 гостей для дня рождения, семейного события, презентации или встречи команды: вес на гостя, цена на человека и скидка 27%. Можно дополнить любыми блюдами из меню.",
     "card_title": "Готовый фуршет на 20 человек",
     "faq": [
         ("Хватит ли набора на 20 человек?",
          "В наборе около {per_guest} г закусок на гостя — это полноценный фуршет без горячего. Для долгого вечера добавьте горячее или пирог из меню."),
         ("Можно ли заменить бокс в наборе?",
          f"Да. Напишите в комментарии к заявке или позвоните по номеру {PHONE} — администратор предложит замену и пересчитает стоимость."),
         ("Можно ли совместить набор и отдельные блюда?",
          "Да. Корзина общая для всего сайта: добавьте набор и любые позиции из <a href=\"/#constructor\">полного меню</a> — всё попадёт в одну заявку."),
         ("Есть ли доставка?", "Да. В пределах МКАД доставка стоит 20 BYN, при заказе от 500 BYN — бесплатно, поэтому набор на 20 человек доставляем бесплатно."),
     ]},
    {"guests": 30, "path": "/furshet-na-30-chelovek/",
     "title": "Фуршет на 30 человек в Минске — готовый набор, меню и доставка | Draft Catering",
     "h1": "Фуршет <span>на 30 человек</span> в Минске", "crumb": "Фуршет на 30 человек в Минске",
     "overline": "БОЛЬШАЯ КОМПАНИЯ · МИНСК",
     "lead": "Готовый набор на 30 гостей для корпоратива, презентации или семейного праздника: вес на гостя, цена на человека и скидка 20%. Для компаний — безналичный расчёт.",
     "card_title": "Готовый фуршет на 30 человек",
     "faq": [
         ("Хватит ли набора на 30 человек?",
          "В наборе около {per_guest} г закусок на гостя — это сытный фуршет даже без горячего. Если нужно, добавьте горячее из меню."),
         ("За сколько времени заказать фуршет на 30 человек?",
          "Желательно за 2–3 дня, а перед праздниками — раньше. Срочный заказ возможен по согласованию с администратором."),
         ("Можно ли оплатить безналично?",
          "Да, Draft Catering принимает заказы от компаний и организаций. Безналичный расчёт и документы обсуждаются при подтверждении заказа."),
         ("Можно ли совместить набор и отдельные блюда?",
          "Да. Корзина общая: добавьте набор и любые позиции из <a href=\"/#constructor\">полного меню</a> — всё попадёт в одну заявку."),
     ]},
]


def build_page(cfg, s):
    e = html.escape
    url = BASE + cfg["path"]
    faq = [(q, a.format(per_guest=s["per_guest"])) for q, a in cfg["faq"]]
    description = (f'Готовый фуршет на {cfg["guests"]} человек в Минске: {grams(s["weight"])}, {grams(s["per_guest"])} на гостя, '
                   f'{s["price"]} BYN вместо {s["full_price"]} BYN ({money(s["price"] / s["guests"])} BYN на человека). Доставка по Минску бесплатно.')
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": cfg["crumb"], "item": url}]},
        {"@type": "Product", "@id": url + "#set", "name": cfg["card_title"],
         "description": f'{s["weight"]} г, {s["per_guest"]} г на гостя: ' + '; '.join(i["name"] for i in s["rows"]),
         "image": [BASE + i["img"] for i in s["items"]], "brand": {"@type": "Brand", "name": "Draft Catering"},
         "offers": {"@type": "Offer", "price": f'{s["price"]:.2f}', "priceCurrency": "BYN", **offer_terms(s["price"]), "availability": "https://schema.org/InStock",
                    "url": url + "#set", "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in faq]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    version = lambda name: hashlib.md5((SITE / 'css' / name).read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    header = header.replace('href="/#faq"', 'href="#faq"')
    card = set_card(dict(s, anchor="set", title=cfg["card_title"]))
    faq_html = ('<section class="section faq-page" id="faq"><div class="wrap"><h2>Частые вопросы</h2><div class="faq-page-list">'
                + ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in faq) + '</div></div></section>')
    more = ('<aside class="occasion-more" aria-labelledby="more-title"><div><h2 id="more-title">Нужен другой состав?</h2>'
            '<p>Соберите стол сами из полного меню: готовые боксы, канапе, брускетты, тарталетки, салаты, горячее и десерты. '
            'Или добавьте к набору что-то ещё — корзина общая.</p></div><div class="occasion-more-actions">'
            '<a class="primary-link" href="/#constructor"><strong>Полное меню</strong><span aria-hidden="true">→</span></a>'
            f'<a class="secondary-link" href="{CORP}"><strong>Наборы на 10–30 человек</strong><span aria-hidden="true">→</span></a></div></aside>')
    links = ''.join(f'<a href="{h}">{e(l)}</a>' for h, l in [
        ("/", "Полное меню"), (CORP, "Новогодний корпоратив в офис"), ("/furshet-na-10-chelovek/", "На 10 человек"),
        ("/furshet-na-20-chelovek/", "На 20 человек"), ("/furshet-na-30-chelovek/", "На 30 человек"), ("/gotovye-furshetnye-boksy/", "Готовые боксы"),
        ("/furshet-na-zakaz/", "Фуршет на заказ"), ("/keytering-na-korporativ/", "На корпоратив"), ("/keytering-na-den-rozhdeniya/", "На день рождения"),
        ("/goryachee-na-prazdnichnyy-stol/", "Горячее"), ("/dostavka-i-oplata/", "Доставка и оплата")] if h != cfg["path"])
    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(cfg["title"])}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(cfg["title"])}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE + s["items"][0]["img"]}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20261104b"><link rel="stylesheet" href="/css/boxes-page.css?v={version('boxes-page.css')}"><link rel="stylesheet" href="/css/sets-page.css?v={version('sets-page.css')}"><link rel="stylesheet" href="/css/reviews.css?v={asset_version('css/reviews.css')}"><link rel="stylesheet" href="/css/occasion-pages.css?v={asset_version('css/occasion-pages.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → {e(cfg["crumb"])}</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>{cfg["overline"]}</span></div><h1>{cfg["h1"]}</h1><p>{e(cfg["lead"])}</p><div class="boxes-hero-actions"><a class="primary-link" href="#set"><strong>Смотреть набор</strong><span aria-hidden="true">↓</span></a><a class="secondary-link" href="/#constructor"><strong>Полное меню</strong><span aria-hidden="true">→</span></a></div></div></div></section>
<section class="boxes-list" aria-label="Готовый набор"><div class="wrap"><div class="ready-grid">
{card}</div>
{more}</div></section>
{reviews_html('wrap')}
{faq_html}
<section class="section"><div class="wrap text-grid"><h2>Как оформить заказ</h2><p>Добавьте набор в корзину и оформите заявку — корзина общая для всего сайта, к набору можно добавить любые блюда из <a href="/">полного меню</a>. Укажите число гостей и время; администратор перезвонит, подтвердит состав и доставку.</p><p>Посуда и приборы — одноразовые, по запросу. Самовывоз: Минск, ул. Нововиленская, 51. Доставка по Минску в пределах МКАД — 20 BYN, от 500 BYN — бесплатно. Подробнее — на странице <a href="/dostavka-i-oplata/">«Доставка и оплата»</a>.</p></div></section>
<section class="section facts"><div class="wrap"><h2>Меню и форматы мероприятий</h2><div class="links">{links}</div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / cfg["path"].strip('/') / "index.html"
    out.write_text(page, encoding="utf-8")
    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    print(f'{cfg["path"]}: {s["price"]} BYN, {s["per_guest"]} г/гость')


def build():
    sets = {s["guests"]: s for s in resolve()}
    for cfg in PAGES:
        build_page(cfg, sets[cfg["guests"]])


if __name__ == "__main__":
    build()
