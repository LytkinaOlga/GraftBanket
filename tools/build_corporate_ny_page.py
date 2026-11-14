#!/usr/bin/env python3
"""Build site/novogodniy-korporativ-v-ofis/index.html — New Year office party offer.

A short commercial-offer page to send to office managers: ready sets for 10/15/20/30 guests
(boxes from the home page, set price below the sum of the boxes), hot dishes as an add-on,
terms for companies, reviews and FAQ. Set prices live in js/data.js (setny-*, set10-sparkling);
the struck-out price must equal the sum of the boxes. Run after any change to boxes or sets:
    python3 tools/build_corporate_ny_page.py
"""
import hashlib
import html
import json
import re
from datetime import date

from build_boxes_page import BASE, SITE, asset_version, home_shell, reviews_html, text
from build_furshet10_page import DELIVERY_PRICE, FREE_DELIVERY_FROM, cart_prices, grams, home_boxes, plural

PAGE_PATH = "/novogodniy-korporativ-v-ofis/"
PHONE = '<a href="tel:+375295704749">+375 29 570-47-49</a>'
LAST_DAY = "30 декабря"
# Boxes whose weight is not in the home page card markup (taken from js/data.js).
WEIGHTS = {"box-profiteroles": 750}

SETS = [
    {"id": "set10-sparkling", "anchor": "set-10", "guests": 10, "title": "Небольшая команда",
     "lead": "Нарезки к игристому, канапе, брускетты с лососем и креветкой, горячие тарталетки и профитроли.",
     "boxes": ["box-sparkling", "box-canapes", "box-bruschetta-salmon-shrimp", "box-baked-tartlets", "box-profiteroles-mini"]},
    {"id": "setny-15", "anchor": "set-15", "guests": 15, "title": "Отдел",
     "lead": "Бокс «Фуршетный» с лососем и крабом, нарезки к игристому, два бокса брускетт с лососем и креветкой, ассорти рулетиков и солёные «Наполеоны».",
     "boxes": ["box-salmon-crab", "box-sparkling", ("box-bruschetta-salmon-shrimp", 2), "box-assorted-rolls", ("box-napoleons", 2)]},
    {"id": "setny-20", "anchor": "set-20", "guests": 20, "title": "Весь офис",
     "lead": "Два бокса «Фуршетный» с лососем и крабом, нарезки к игристому, брускетты с лососем и креветкой, брускетты с профитролями и шпинатным рулетом, ассорти рулетиков и большие солёные «Наполеоны».",
     "boxes": [("box-salmon-crab", 2), "box-sparkling", ("box-bruschetta-salmon-shrimp", 2), "box-bruschetta-profiterole-roll",
               "box-assorted-rolls", ("box-napoleons-big", 2)]},
    {"id": "setny-30", "anchor": "set-30", "guests": 30, "title": "Большой корпоратив",
     "lead": "Самый полный стол: «Фуршетные» боксы и нарезки к игристому, канапе, брускетты с лососем и креветкой, мини-круассаны, горячие тарталетки, рулетики, кростини, солёные «Наполеоны» и профитроли.",
     "boxes": [("box-salmon-crab", 2), ("box-sparkling", 2), ("box-canapes", 2), "box-croissant-bruschetta-canape",
               ("box-bruschetta-salmon-shrimp", 2), ("box-baked-tartlets", 3), "box-assorted-rolls",
               ("box-napoleons-big", 2), "box-crostini", ("box-profiteroles", 2)]},
]

FAQ = [
    ("До какого числа можно заказать?",
     f"Новогодние заказы принимаем до {LAST_DAY}. Заказ на 20–30 человек лучше оформить заранее — в декабре даты быстро заканчиваются."),
    ("Можно поменять боксы в наборе или собрать свой?",
     f"Да. Напишите в комментарии к заявке или позвоните по номеру {PHONE} — администратор предложит замену и пересчитает стоимость. "
     "Можно собрать стол и самостоятельно из <a href=\"/gotovye-furshetnye-boksy/\">готовых боксов</a>."),
    ("Будут ли посуда и приборы?",
     "Боксы можно сразу ставить на стол. Дополнительно предоставим одноразовую посуду и приборы — отметьте это в комментарии к заявке, администратор уточнит количество."),
    ("Можно оплатить от компании?",
     "Да, работаем с компаниями: безналичный расчёт и документы обсудим при подтверждении заказа. Оплатить можно и наличными или картой."),
    ("Можно добавить горячее?",
     "Да, горячие блюда добавляются в ту же корзину: филе птицы с ананасом, мясо по-французски, рулет из птицы, лосось Веллингтон и другие."),
    ("Сколько стоит доставка?",
     f"По Минску в пределах МКАД — {DELIVERY_PRICE} BYN, при заказе от {FREE_DELIVERY_FROM} BYN — бесплатно. Наборы на 15, 20 и 30 человек доставляем бесплатно. "
     "Привезём к нужному времени; самовывоз — Минск, ул. Нововиленская, 51."),
]


def resolve():
    boxes = home_boxes()
    for s in SETS:
        s["price"], old = cart_prices(s["id"])
        s["items"], s["rows"] = [], []
        for b in s["boxes"]:
            box_id, qty = b if isinstance(b, tuple) else (b, 1)
            box = boxes[box_id] | {"id": box_id, "qty": 1}
            box["weight"] = box["weight"] or WEIGHTS[box_id]
            # Repeated boxes: separate photo tiles, one composition row "name × N".
            s["items"].extend(dict(box) for _ in range(qty))
            s.setdefault("rows", []).append(box | {"name": box["name"] + (f" × {qty}" if qty > 1 else ""), "weight": box["weight"] * qty})
        s["count"] = sum(i["qty"] for i in s["items"])
        s["weight"] = sum(i["weight"] for i in s["items"])
        s["full_price"] = sum(i["price"] for i in s["items"])
        s["per_guest"] = round(s["weight"] / s["guests"])
        assert old == s["full_price"], f'{s["id"]}: oldPrice {old} in js/data.js, boxes sum to {s["full_price"]}'
    return SETS


def money(x):
    return f'{x:.0f}' if x == int(x) else f'{x:.2f}'.replace('.', ',')


def compare_html(sets):
    e = html.escape
    cols = ''.join(
        f'<article class="compare-card"><h3>На {s["guests"]} человек</h3><p class="compare-tagline">{e(s["title"])}</p>'
        f'<p class="compare-price"><strong>{s["price"]} BYN</strong> <span>за набор</span></p>'
        f'<p class="compare-per">{money(s["price"] / s["guests"])} BYN на человека</p>'
        f'<p class="compare-row">{grams(s["per_guest"])} на гостя · {s["count"]} {plural(s["count"])}</p>'
        f'<p class="compare-row compare-delivery">Доставка {"бесплатно" if s["price"] >= FREE_DELIVERY_FROM else f"<strong>+{DELIVERY_PRICE} BYN</strong>"}</p>'
        f'<a class="compare-link" href="#{s["anchor"]}">Посмотреть состав <span aria-hidden="true">→</span></a></article>'
        for s in sets)
    return ('<section class="sets-compare" id="sets-compare" aria-labelledby="compare-title"><div class="wrap">'
            '<h2 id="compare-title">Наборы на 10, 15, 20 и 30 человек</h2>'
            '<p class="compare-lead">Цена набора ниже, чем те же боксы по отдельности</p>'
            f'<div class="compare-grid">{cols}</div>'
            f'<p class="compare-terms">Заказы до {LAST_DAY} · Доставка к нужному времени · Посуда и приборы — по запросу</p>'
            '</div></section>\n')


def set_card(s):
    e = html.escape
    tiles = ''.join(f'<figure class="set-tile"><img src="{e(i["img"])}" alt="{e(i["alt"])}" loading="lazy"><figcaption>{e(i["name"])}</figcaption></figure>'
                    for i in s["items"])
    rows = ''.join(f'<li><a href="/gotovye-furshetnye-boksy/#{e(i["id"])}">{e(i["name"])}</a><span>{grams(i["weight"])}</span></li>' for i in s["rows"])
    count = s["count"]
    odd = (' set-mosaic-odd' if len(s["items"]) % 2 else '') + (' set-mosaic-wide' if len(s["items"]) > 5 else '')
    return f'''        <article id="{s["anchor"]}" class="ready-box set-box">
          <div class="set-mosaic{odd}">{tiles}</div>
          <div class="ready-box-content">
            <span class="ready-box-kicker">На {s["guests"]} человек · <span class="ready-box-weight">{grams(s["weight"])}</span></span>
            <h2 class="ready-box-title"><span>{e(s["title"])}</span></h2>
            <p class="set-per-guest"><strong>{grams(s["per_guest"])}</strong> на гостя · {money(s["price"] / s["guests"])} BYN на человека · {count} {plural(count)}</p>
            <p>{e(s["lead"])}</p>
            <ul class="set-items">{rows}</ul>
            <div class="ready-box-order"><div class="ready-box-price"><strong>{s["price"]} BYN</strong><div class="ready-box-price-meta"><s class="ready-box-old-price" aria-label="Цена без скидки">{s["full_price"]} BYN</s><span class="ready-box-saving">скидка {s["full_price"] - s["price"]} BYN</span></div></div><div class="ready-box-action" data-control="{s["id"]}"></div></div>
          </div>
        </article>
'''


def build():
    sets = resolve()
    e = html.escape
    url = BASE + PAGE_PATH
    title = "Новогодний корпоратив в офис — фуршетные наборы с доставкой в Минске | Draft Catering"
    description = (f"Новогодний стол для офиса: готовые фуршетные наборы на 10, 15, 20 и 30 человек от {min(s['price'] for s in sets)} BYN, "
                   f"горячее, посуда и приборы по запросу. Доставка по Минску, заказы до {LAST_DAY}.")
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Новогодний корпоратив в офис", "item": url}]},
        {"@type": "ItemList", "@id": url + "#sets", "name": "Новогодние наборы для офиса", "numberOfItems": len(sets),
         "itemListElement": [
             {"@type": "ListItem", "position": n, "item": {
                 "@type": "Product", "@id": f'{url}#{s["anchor"]}', "name": f'Новогодний набор на {s["guests"]} человек',
                 "description": f'{s["weight"]} г, {s["per_guest"]} г на гостя: ' + '; '.join(i["name"] for i in s["items"]),
                 "image": [BASE + i["img"] for i in s["items"]], "brand": {"@type": "Brand", "name": "Draft Catering"},
                 "offers": {"@type": "Offer", "price": f'{s["price"]:.2f}', "priceCurrency": "BYN", "availability": "https://schema.org/InStock",
                            "url": f'{url}#{s["anchor"]}', "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}}}
             for n, s in enumerate(sets, 1)]},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in FAQ]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    version = lambda name: hashlib.md5((SITE / 'css' / name).read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    header = header.replace('href="/#faq"', 'href="#faq"').replace('href="/#reviews"', 'href="#reviews"')
    faq_html = ('<section class="section faq-page" id="faq"><div class="wrap"><h2>Вопросы о заказе</h2><div class="faq-page-list">'
                + ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in FAQ) + '</div></div></section>')
    terms = (f'<li><strong>Заказы до {LAST_DAY}:</strong> большие заказы лучше оформить заранее.</li>'
             '<li><strong>Для компаний:</strong> безналичный расчёт и документы — обсудим при подтверждении.</li>'
             f'<li><strong>Доставка:</strong> к нужному времени; от {FREE_DELIVERY_FROM} BYN по Минску бесплатно.</li>'
             '<li><strong>Посуда и приборы:</strong> одноразовые — по запросу.</li>')
    cards = ''.join(set_card(s) for s in sets)
    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="Новогодний корпоратив в офис — наборы на 10–30 человек"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE + sets[1]["items"][0]["img"]}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20261104b"><link rel="stylesheet" href="/css/boxes-page.css?v={version('boxes-page.css')}"><link rel="stylesheet" href="/css/sets-page.css?v={version('sets-page.css')}"><link rel="stylesheet" href="/css/reviews.css?v={asset_version('css/reviews.css')}"><link rel="stylesheet" href="/css/occasion-pages.css?v={asset_version('css/occasion-pages.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Новогодний корпоратив в офис</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>НОВЫЙ ГОД · ДЛЯ ОФИСА · МИНСК</span></div><h1>Новогодний корпоратив <span>в офис</span></h1><p>Готовый праздничный стол для команды: фуршетные наборы на 10, 15, 20 и 30 человек — с весом на гостя и ценой на человека. Привезём к нужному времени, боксы можно сразу ставить на стол. Заказы принимаем до {LAST_DAY}.</p><div class="boxes-hero-actions"><a class="primary-link" href="#sets-compare"><strong>Выбрать набор</strong><span aria-hidden="true">↓</span></a><a class="secondary-link" href="tel:+375295704749"><strong>+375 29 570-47-49</strong><span aria-hidden="true">→</span></a></div></div></div></section>
<section class="boxes-guide" aria-labelledby="guide-title"><div class="wrap boxes-guide-layout"><div class="boxes-guide-offer"><h2 id="guide-title">Как это работает</h2><p>Выберите набор под число гостей, добавьте горячее или отдельные боксы и оформите заявку на сайте. Администратор перезвонит, подтвердит состав, время доставки и способ оплаты.</p></div><ul class="boxes-terms" aria-label="Условия заказа">{terms}</ul></div></section>
{compare_html(sets)}<section class="boxes-list" id="sets" aria-label="Состав наборов"><div class="wrap"><div class="ready-grid">
{cards}</div></div></section>
<section class="section" id="hot" aria-labelledby="hot-title"><div class="wrap"><h2 id="hot-title">Горячее к столу</h2><p class="occasion-note">Добавьте к набору горячее — оно попадёт в ту же заявку.</p><div class="ready-grid hot-grid" data-menu-category="hot"></div>
<aside class="occasion-more" aria-labelledby="more-title"><div><h2 id="more-title">Нужен другой состав?</h2><p>Соберите стол из готовых боксов: канапе, брускетты, тарталетки, рулетики, пироги и десерты. Или позвоните — подберём набор под ваш бюджет и число гостей.</p></div><div class="occasion-more-actions"><a class="primary-link" href="/gotovye-furshetnye-boksy/"><strong>Все готовые боксы</strong><span aria-hidden="true">→</span></a><a class="secondary-link" href="tel:+375295704749"><strong>Позвонить</strong><span aria-hidden="true">→</span></a></div></aside></div></section>
{reviews_html('wrap')}
{faq_html}
<section class="section facts"><div class="wrap"><h2>Другие форматы</h2><div class="links"><a href="/novogodniy-furshet/">Новогодний фуршет</a><a href="/keytering-na-korporativ/">Кейтеринг на корпоратив</a><a href="/furshet-v-ofis-na-den-rozhdeniya/">День рождения в офисе</a><a href="/furshet-na-10-chelovek/">Фуршет на 10 человек</a><a href="/goryachee-na-prazdnichnyy-stol/">Горячее на праздничный стол</a><a href="/dostavka-i-oplata/">Доставка и оплата</a></div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / PAGE_PATH.strip('/') / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    loc = f'<loc>{url}</loc>'
    if loc not in sm:
        sm = sm.replace('</urlset>', f'  <url>{loc}<lastmod>{date.today():%Y-%m-%d}</lastmod></url>\n</urlset>')
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    for s in sets:
        print(f'{s["guests"]} чел.: {s["weight"]} г, {s["per_guest"]} г/гость, {s["price"]} BYN (без скидки {s["full_price"]}), {money(s["price"]/s["guests"])} BYN/чел.')


if __name__ == "__main__":
    build()
