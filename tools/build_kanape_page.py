#!/usr/bin/env python3
"""Build site/kanape-na-zakaz/index.html — the canapé box plus other snacks for a buffet.

Count, weight, price and photos come from the ready boxes on the home page, and the
"add to cart" button uses the same cart item (js/data.js), so run this after any
change to those boxes:
    python3 tools/build_kanape_page.py
"""
import hashlib
import html
import json
import re
from datetime import date

from build_boxes_page import BASE, SITE, control_id, home_shell, split_articles, text

PAGE_PATH = "/kanape-na-zakaz/"
MAIN_BOX = "box-canapes"
# Alternatives and add-ons, shown with their real names; the button text names the category.
OTHER_SNACKS = [
    ("box-bruschetta-salmon-shrimp", "Посмотреть брускетты"),
    ("box-baked-tartlets", "Посмотреть тарталетки"),
    ("box-profiteroles-mini", "Посмотреть профитроли"),
]
FREE_DELIVERY_FROM, DELIVERY_PRICE = 500, 20

FAQ = [
    ("Можно ли заказать только один бокс?",
     "Да. Минимальной суммы заказа нет — можно заказать один бокс канапе. Условия получения те же: самовывоз бесплатно, доставка в пределах МКАД — 20 BYN, от 500 BYN — бесплатно."),
    ("Можно ли заменить виды канапе или заказать один вид?",
     "Обсудите это с администратором: он подскажет, какие замены возможны, и пересчитает стоимость. Напишите пожелание в комментарии к заявке или позвоните по номеру <a href=\"tel:+375295704749\">+375 29 570-47-49</a>."),
    ("Можно ли добавить другие закуски?",
     "Да. Корзина общая для всего сайта: добавьте бокс канапе, а затем выберите брускетты, тарталетки, профитроли или другие <a href=\"/gotovye-furshetnye-boksy/\">готовые боксы</a> — всё попадёт в одну заявку."),
    ("За сколько дней оформить заказ? Можно ли срочно?",
     "Желательно оформить заказ за 2–3 дня. Срочный заказ возможен по согласованию — позвоните, и администратор проверит, что мы успеем приготовить к нужному времени."),
    ("Как получить заказ и сколько стоит доставка?",
     "Самовывоз — Минск, ул. Нововиленская, 51, бесплатно. Доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно; за МКАД стоимость рассчитает администратор. Подробнее — на странице <a href=\"/dostavka-i-oplata/\">«Доставка и оплата»</a>."),
    ("Как уточнить аллергены и условия хранения?",
     "Напишите вопрос в комментарии к заявке или позвоните администратору — он расскажет о составе и подскажет, как хранить закуски до подачи."),
]


def home_box(article):
    first_img = re.search(r'<img[^>]+src="([^"]+)"', article).group(1)
    mobile = re.search(r'<source media="\(max-width: 680px\)" srcset="([^"]+)"', article)
    kicker = text(next(line for line in article.split('\n') if 'ready-box-kicker' in line))
    parts = [p.strip() for p in re.sub(r'\s+', ' ', kicker).split('·')]
    pieces = next((p for p in parts if p.endswith('шт.')), '')
    weight = parts[-1]
    imgs = re.findall(r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"', article)
    return {
        "id": control_id(article),
        "name": text(re.search(r'<h3>(.*?)</h3>', article, re.S).group(1)),
        "pieces": pieces, "weight": weight,
        "price": int(re.search(r'<strong>(\d+) BYN</strong>', article).group(1)),
        "img": '/' + first_img, "img_mobile": mobile and '/' + mobile.group(1),
        "photos": [('/' + src, html.unescape(alt)) for src, alt in imgs],
        "items": [re.sub(r'(?<!шт)\.$', '', text(li).rstrip(';')) for li in re.findall(r'<li>(.*?)</li>', article, re.S)],
        "note": (lambda m: m and text(m.group(1)))(re.search(r'<p class="ready-box-note">(.*?)</p>', article, re.S)),
    }


def boxes_by_id():
    _, articles, _ = split_articles((SITE / "index.html").read_text(encoding="utf-8"))
    return {b["id"]: b for b in map(home_box, articles)}


def pieces_word(n):
    return 'штука' if n % 10 == 1 and n % 100 != 11 else 'штуки' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'штук'

def delivery_line():
    return (f'Предзаказ желательно за 2–3 дня. Самовывоз: Нововиленская, 51. '
            f'Доставка в пределах МКАД — {DELIVERY_PRICE} BYN, от {FREE_DELIVERY_FROM} BYN бесплатно.')


def snack_card(box, button):
    e = html.escape
    source = f'<source media="(max-width: 680px)" srcset="{box["img_mobile"]}">' if box["img_mobile"] else ''
    facts = ' · '.join(x for x in (box["pieces"], box["weight"]) if x)
    return (f'<article class="snack-card"><picture>{source}<img src="{box["img"]}" alt="{e(box["photos"][0][1])}" loading="lazy" decoding="async" width="720" height="540"></picture>'
            f'<div class="snack-card-body"><h3>{e(box["name"])}</h3><p class="snack-card-facts">{e(facts)}</p>'
            f'<p class="snack-card-items">{e("; ".join(box["items"]))}</p>'
            f'<p class="snack-card-price"><strong>{box["price"]} BYN</strong> за бокс</p>'
            f'<a class="snack-card-link" href="/gotovye-furshetnye-boksy/#{box["id"]}">{e(button)} <span aria-hidden="true">→</span></a></div></article>')


def build():
    boxes = boxes_by_id()
    box = boxes[MAIN_BOX]
    count = int(re.match(r'\d+', box["pieces"]).group())
    kinds = len(box["items"])
    url = BASE + PAGE_PATH
    title = "Канапе на заказ в Минске — состав и цены | Draft Catering"
    description = (f"Бокс канапе в Минске: {count} штука {kinds} видов, состав и цена. Дополните заказ брускеттами, "
                   "тарталетками и профитролями. Доставка и самовывоз.")
    e = html.escape
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Канапе на заказ в Минске", "item": url}]},
        {"@type": "Product", "@id": url + "#box", "name": f"Бокс канапе — {count} шт.",
         "description": f'{box["pieces"]}, {box["weight"]}: ' + '; '.join(box["items"]),
         "image": [BASE + src for src, _ in box["photos"]], "brand": {"@type": "Brand", "name": "Draft Catering"},
         "offers": {"@type": "Offer", "price": f'{box["price"]:.2f}', "priceCurrency": "BYN",
                    "availability": "https://schema.org/InStock", "url": url + "#box",
                    "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in FAQ]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    version = lambda name: hashlib.md5((SITE / 'css' / name).read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    header = header.replace('href="/#faq"', 'href="#faq"')  # the page has its own FAQ

    kinds_html = ''.join(f'<li>{e(item.split(" — ")[0][:1].upper() + item.split(" — ")[0][1:])}'
                         f'<span>{e(item.split(" — ")[1]) if " — " in item else ""}</span></li>' for item in box["items"])
    per_piece = re.search(r'Одно канапе — (\d+) г', box["note"] or '')
    total_line = f'{count} канапе, общий вес {box["weight"].replace(" г", "")} г' + (f'. Около {per_piece.group(1)} г за штуку.' if per_piece else '.')
    photos = ''.join(f'<figure><img src="{src}" alt="{e(alt)}" loading="lazy" decoding="async" width="720" height="540"></figure>'
                     for src, alt in box["photos"])
    snacks = ''.join(snack_card(boxes[i], label) for i, label in OTHER_SNACKS)
    faq_html = ('<section class="section faq-page" id="faq"><div class="wrap"><h2>Вопросы о заказе канапе и закусок</h2><div class="faq-page-list">'
                + ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in FAQ) + '</div></div></section>')

    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE + box["img"]}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20261104b"><link rel="stylesheet" href="/css/boxes-page.css?v={version('boxes-page.css')}"><link rel="stylesheet" href="/css/kanape-page.css?v={version('kanape-page.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Канапе на заказ в Минске</nav>
<section class="kanape-hero" id="box"><div class="wrap kanape-hero-layout"><div class="kanape-hero-copy"><div class="boxes-hero-overline"><span>МИНИ-ЗАКУСКИ · МИНСК</span></div><h1>Канапе <span>на заказ</span> в Минске</h1><p>Готовый бокс из {count} канапе трёх видов: с креветкой, ростбифом и овощами с сыром. Ниже — состав, цена и другие закуски для вашего фуршета.</p>
<div class="kanape-price"><p class="kanape-facts">{count} {pieces_word(count)} · {e(box["weight"])}</p><p class="kanape-amount"><strong>{box["price"]} BYN</strong><span>за бокс</span></p></div>
<div class="kanape-actions"><div class="ready-box-action kanape-add" data-control="{MAIN_BOX}" data-add-label="Добавить в корзину"><a class="add-btn" href="/gotovye-furshetnye-boksy/#{MAIN_BOX}">Посмотреть бокс и заказать</a></div><a class="kanape-secondary" href="#other-snacks">Другие закуски <span aria-hidden="true">↓</span></a></div>
<p class="kanape-terms">{e(delivery_line())}</p></div>
<div class="kanape-hero-photo"><img src="{box["img"]}" alt="{e(box["photos"][0][1])}" width="900" height="900" fetchpriority="high" decoding="async"></div></div></section>
<section class="section kanape-inside" aria-labelledby="inside-title"><div class="wrap"><h2 id="inside-title">Что входит в бокс канапе</h2><p class="lead">В одном боксе — {kinds} вида канапе, по {count // kinds} штук каждого.</p>
<ul class="kanape-kinds">{kinds_html}</ul><p class="kanape-total">{e(total_line)}</p>
<div class="kanape-photos">{photos}</div></div></section>
<section class="section other-snacks" id="other-snacks" aria-labelledby="other-title"><div class="wrap"><h2 id="other-title">Другие закуски для фуршета</h2><p class="lead">Ищете разнообразные мини-закуски для праздничного стола? Помимо канапе, у нас есть брускетты, тарталетки и профитроли. Их можно добавить к боксу или выбрать вместо него.</p>
<div class="snack-grid">{snacks}</div><p class="other-snacks-all"><a class="primary-link" href="/gotovye-furshetnye-boksy/"><strong>Все готовые боксы</strong><span aria-hidden="true">→</span></a></p></div></section>
<section class="section kanape-guests" aria-labelledby="guests-title"><div class="wrap"><div class="kanape-guests-box"><div><h2 id="guests-title">Подбираете закуски на 10 человек?</h2><p>Если нужен разнообразный стол, посмотрите готовые сочетания боксов с составом, весом и ценой.</p></div><a class="kanape-guests-link" href="/furshet-na-10-chelovek/">Наборы на 10 человек <span aria-hidden="true">→</span></a></div></div></section>
{faq_html}
<section class="section facts"><div class="wrap"><h2>Другие категории и услуги</h2><div class="links"><a href="/gotovye-furshetnye-boksy/">Готовые боксы</a><a href="/furshet-na-10-chelovek/">Фуршет на 10 человек</a><a href="/furshet-na-zakaz/">Фуршет на заказ</a><a href="/dostavka-zakusok/">Доставка закусок</a><a href="/brusketty-na-zakaz/">Брускетты</a><a href="/tartaletki-na-zakaz/">Тарталетки</a><a href="/keytering-dlya-ofisa/">Для офиса и корпоратива</a><a href="/keytering-na-den-rozhdeniya/">На день рождения</a><a href="/dostavka-i-oplata/">Доставка и оплата</a></div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / PAGE_PATH.strip('/') / "index.html"
    out.write_text(page, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    print(f'{out.relative_to(SITE.parent)}: {box["pieces"]}, {box["weight"]}, {box["price"]} BYN; '
          + ', '.join(f'{boxes[i]["name"]} {boxes[i]["price"]} BYN' for i, _ in OTHER_SNACKS))


if __name__ == "__main__":
    build()
