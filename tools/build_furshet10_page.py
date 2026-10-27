#!/usr/bin/env python3
"""Build site/furshet-na-10-chelovek/index.html — ready sets for 10 guests.

Photos, weights and prices of the boxes are taken from the ready boxes on the
home page, so run this after any change to those boxes:
    python3 tools/build_furshet10_page.py

Set price and struck-out price live in js/data.js (the cart and /api/order use
them); the struck-out price must equal the sum of the set's boxes at site prices.
"""
import hashlib
import html
import json
import re
from datetime import date

from build_boxes_page import BASE, FAQ as BOXES_FAQ, SITE, control_id, home_shell, split_articles, text

PAGE_PATH = "/furshet-na-10-chelovek/"
GUESTS = 10

# "id" is the set's cart item in js/data.js; "boxes" are box ids from site/index.html,
# a dict overrides the box's own name/weight/price.
SETS = [
    {"id": "set10-sparkling", "title": "Фуршет к игристому",
     "lead": "Закуски к бокалу игристого: сыры и мясная нарезка, канапе, профитроли, брускетты и горячие тарталетки.",
     "boxes": ["box-sparkling", "box-canapes", "box-profiteroles-mini", "box-bruschetta-salmon-shrimp", "box-baked-tartlets"]},
    {"id": "set10-big", "title": "Большой фуршет с пирогом и круассанами",
     "lead": "Всё из набора к игристому плюс сытный пирог с курицей и бокс мини-круассанов — для долгого вечера.",
     "boxes": ["box-sparkling", "box-canapes", "box-profiteroles-mini", "box-bruschetta-salmon-shrimp", "box-baked-tartlets",
               "box-chicken-pie", "box-croissants"]},
    {"id": "set10-dessert", "title": "Закуски, пирог и десерт",
     "lead": "Брускетты, профитроли и шпинатный рулет, солёные «Наполеоны», пирог с курицей и шоколадные пирожные на десерт.",
     "boxes": ["box-bruschetta-profiterole-roll", "box-napoleons-big", "box-chicken-pie",
               {"id": "box-chocolate-cakes", "name": "Шоколадные пирожные", "weight": 1000, "price": 55}]},
]

FAQ = [
    ("Хватит ли набора на 10 человек?",
     "В каждом наборе указан общий вес и сколько граммов приходится на одного гостя. Для фуршета-перекуса подойдёт набор поменьше, для долгого вечера без горячего — набор с пирогом и круассанами."),
    ("Можно ли заменить бокс в наборе?",
     "Да. Позвоните по номеру <a href=\"tel:+375295704749\">+375 29 570-47-49</a> — администратор предложит замену и пересчитает стоимость."),
    ("Как заказать набор?",
     "Нажмите «Добавить» на карточке набора — он попадёт в корзину вместе с другими блюдами, если вы их выбрали. Затем оформите заявку: дата, время, способ получения и оплаты. Администратор свяжется с вами и подтвердит заказ."),] + [qa for qa in BOXES_FAQ if qa[0].startswith(("За сколько", "Есть ли доставка", "Как оплатить"))]


def weight_grams(label):
    value = label.replace('\xa0', ' ').strip()
    number = float(re.sub(r'[^\d,.]', '', value).replace(',', '.'))
    return int(round(number * 1000)) if 'кг' in value else int(number)


def grams(n):
    return f'{n:,}'.replace(',', '\xa0') + '\xa0г'


def home_boxes():
    _, articles, _ = split_articles((SITE / "index.html").read_text(encoding="utf-8"))
    boxes = {}
    for a in articles:
        img = re.search(r'<img[^>]*>', a).group(0)
        src, alt = re.search(r'src="([^"]+)"', img).group(1), re.search(r'alt="([^"]*)"', img).group(1)
        weight = re.search(r'ready-box-weight">([^<]+)<', a)
        boxes[control_id(a)] = {
            "name": text(re.search(r'<h3>(.*?)</h3>', a, re.S).group(1)),
            "weight": weight and weight_grams(text(weight.group(1))),
            "price": int(re.search(r'<strong>(\d+) BYN</strong>', a).group(1)),
            "img": '/' + src.lstrip('/'), "alt": html.unescape(alt),
        }
    return boxes


def cart_prices(set_id):
    data = (SITE / "js" / "data.js").read_text(encoding="utf-8")
    line = re.search(r'\{ id: "' + re.escape(set_id) + r'".*', data).group(0)
    return int(re.search(r'price: (\d+)', line).group(1)), int(re.search(r'oldPrice: (\d+)', line).group(1))


def resolve(sets):
    boxes = home_boxes()
    for s in sets:
        s["price"], old_price = cart_prices(s["id"])
        items = []
        for entry in s["boxes"]:
            spec = entry if isinstance(entry, dict) else {"id": entry}
            items.append({**boxes[spec["id"]], **spec})
        s["items"] = items
        s["weight"] = sum(i["weight"] for i in items)
        s["full_price"] = sum(i["price"] for i in items)
        s["per_guest"] = round(s["weight"] / GUESTS)
        assert old_price == s["full_price"], f'{s["id"]}: oldPrice {old_price} in js/data.js, boxes sum to {s["full_price"]}'
    return sets


def set_card(n, s):
    e = html.escape
    tiles = ''.join(
        f'<figure class="set-tile"><img src="{e(i["img"])}" alt="{e(i["alt"])}" loading="lazy"><figcaption>{e(i["name"])}</figcaption></figure>'
        for i in s["items"])
    rows = ''.join(
        f'<li><a href="/gotovye-furshetnye-boksy/#{e(i["id"])}">{e(i["name"])}</a><span>{grams(i["weight"])}</span></li>'
        for i in s["items"])
    saving = s["full_price"] - s["price"]
    count = len(s["items"])
    odd = (' set-mosaic-odd' if count % 2 else '') + (' set-mosaic-wide' if count > 5 else '')
    return f'''        <article id="set-{n}" class="ready-box set-box">
          <div class="set-mosaic{odd}">{tiles}</div>
          <div class="ready-box-content">
            <span class="ready-box-kicker">Набор №{n} · <span class="ready-box-weight">{grams(s["weight"])}</span></span>
            <h2 class="ready-box-title"><span>{e(s["title"])}</span></h2>
            <p class="set-per-guest"><strong>{grams(s["per_guest"])}</strong> на гостя · {GUESTS} человек · {len(s["items"])} {plural(len(s["items"]))}</p>
            <p>{e(s["lead"])}</p>
            <ul class="set-items">{rows}</ul>
            <div class="ready-box-order"><div class="ready-box-price"><strong>{s["price"]} BYN</strong><div class="ready-box-price-meta"><s class="ready-box-old-price" aria-label="Цена без скидки">{s["full_price"]} BYN</s><span class="ready-box-saving">скидка {saving} BYN</span></div></div><div class="ready-box-action" data-control="{s["id"]}"></div></div>
          </div>
        </article>
'''


def plural(n):
    return 'бокс' if n % 10 == 1 and n % 100 != 11 else 'бокса' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'боксов'


def build():
    sets = resolve(SETS)
    url = BASE + PAGE_PATH
    min_price = min(s["price"] for s in sets)
    title = "Фуршет на 10 человек в Минске — готовые наборы | Draft Catering"
    description = (f"{len(sets)} готовых фуршетных набора на 10 человек: состав, вес на гостя и цены от {min_price} BYN "
                   "со скидкой. Брускетты, канапе, тарталетки, пироги и десерты с доставкой по Минску.")
    og_image = BASE + sets[0]["items"][0]["img"]
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Фуршет на 10 человек в Минске", "item": url}]},
        {"@type": "Service", "@id": url + "#service", "name": "Фуршет на 10 человек в Минске", "description": description,
         "url": url, "areaServed": {"@type": "City", "name": "Минск"}, "provider": {"@id": BASE + "/#business"}},
        {"@type": "ItemList", "@id": url + "#sets", "name": "Фуршетные наборы на 10 человек", "numberOfItems": len(sets),
         "itemListElement": [
             {"@type": "ListItem", "position": n, "item": {
                 "@type": "Product", "@id": f"{url}#set-{n}", "name": f'Набор №{n} «{s["title"]}» на {GUESTS} человек',
                 "description": f'{s["weight"]} г, {s["per_guest"]} г на гостя: ' + '; '.join(i["name"] for i in s["items"]),
                 "image": [BASE + i["img"] for i in s["items"]], "brand": {"@type": "Brand", "name": "Draft Catering"},
                 "offers": {"@type": "Offer", "price": f'{s["price"]:.2f}', "priceCurrency": "BYN",
                            "availability": "https://schema.org/InStock", "url": f"{url}#set-{n}",
                            "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}}}
             for n, s in enumerate(sets, 1)]},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in FAQ]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    faq_html = '<section class="section faq-page" id="faq"><div class="wrap"><h2>Частые вопросы</h2><div class="faq-page-list">' + ''.join(
        f'<details><summary>{html.escape(q)}</summary><p>{a}</p></details>' for q, a in FAQ) + '</div></div></section>'
    version = lambda name: hashlib.md5((SITE / 'css' / name).read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    cards = ''.join(set_card(n, s) for n, s in enumerate(sets, 1))
    e = html.escape
    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20260926"><link rel="stylesheet" href="/css/boxes-page.css?v={version('boxes-page.css')}"><link rel="stylesheet" href="/css/sets-page.css?v={version('sets-page.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Фуршет на 10 человек в Минске</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>КАМЕРНЫЙ ПРАЗДНИК · МИНСК</span></div><h1>Фуршет <span>на 10 человек</span> в Минске</h1><p>{len(sets)} готовых набора из наших боксов для домашнего праздника, встречи друзей или небольшой команды. У каждого набора указан состав, общий вес и сколько приходится на одного гостя. Цена набора ниже, чем при заказе тех же боксов по отдельности.</p><div class="boxes-hero-actions"><a class="primary-link" href="#sets"><strong>Смотреть наборы</strong><span aria-hidden="true">↓</span></a></div></div></div></section>
<section class="boxes-list" id="sets" aria-label="Наборы на 10 человек"><div class="wrap"><div class="ready-grid">
{cards}</div></div></section>
{faq_html}
<section class="section facts"><div class="wrap"><div class="facts-grid"><div class="fact"><strong>{GUESTS} гостей</strong><span>Вес каждого набора рассчитан на компанию из {GUESTS} человек.</span></div><div class="fact"><strong>От 2–3 дней</strong><span>Рекомендуемый срок оформления заказа; срочные заказы уточняются.</span></div><div class="fact"><strong>Доставка по Минску</strong><span>В пределах МКАД — 20 BYN, от 500 BYN — бесплатно.</span></div></div></div></section>
<section class="section"><div class="wrap text-grid"><h2>Как оформить заказ</h2><p>Добавьте набор в корзину и оформите заявку — корзина общая для всего сайта, к набору можно добавить любые боксы и закуски. Если хотите заменить бокс в наборе, напишите об этом в комментарии или позвоните по номеру <a href="tel:+375295704749">+375 29 570-47-49</a>.</p><p>Можно собрать и свой набор из <a href="/gotovye-furshetnye-boksy/">готовых боксов</a> или отдельных позиций в <a href="/#constructor">меню</a>.</p><p><strong>Самовывоз:</strong> Минск, ул. Нововиленская, 51 — бесплатно.</p><p><strong>Доставка:</strong> по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно. Подробнее — на странице <a href="/dostavka-i-oplata/">«Доставка и оплата»</a>.</p></div></section>
<section class="section facts"><div class="wrap"><h2>Меню и форматы мероприятий</h2><div class="links"><a href="/gotovye-furshetnye-boksy/">Готовые боксы</a><a href="/furshet-na-zakaz/">Фуршет на заказ</a><a href="/furshet-na-20-chelovek/">На 20 человек</a><a href="/furshet-na-30-chelovek/">На 30 человек</a><a href="/keytering-na-korporativ/">На корпоратив</a><a href="/keytering-na-den-rozhdeniya/">На день рождения</a><a href="/dostavka-zakusok/">Доставка закусок</a><a href="/o-nas/">О нас</a><a href="/dostavka-i-oplata/">Доставка и оплата</a></div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / PAGE_PATH.strip('/') / "index.html"
    out.write_text(page, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    for n, s in enumerate(sets, 1):
        print(f'Набор №{n}: {s["weight"]} г, {s["per_guest"]} г/гость, {s["price"]} BYN (без скидки {s["full_price"]})')


if __name__ == "__main__":
    build()
