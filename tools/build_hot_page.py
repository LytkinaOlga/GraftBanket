#!/usr/bin/env python3
"""Build site/goryachee-na-prazdnichnyy-stol/index.html — hot dishes for the festive table.

Dishes (name, weight, price, photos) come from category "hot" in site/js/data.js; on the page
js/app.js re-renders them as interactive menu cards with the shared cart (<div data-menu-category="hot">),
the static markup below is the fallback for search engines. Run after any change to hot dishes:
    python3 tools/build_hot_page.py
"""
import hashlib
import html
import json
import re
import subprocess
from datetime import date

from build_boxes_page import BASE, SITE, asset_version, home_shell, reviews_html, text
from build_occasion_pages import BIRTHDAY, FAQ_DELIVERY, GIFT, NO_STACK, PHONE, TERM_DELIVERY, TERM_MORE

PAGE_PATH = "/goryachee-na-prazdnichnyy-stol/"


def hot_items():
    js = ("const {ITEMS}=require(process.argv[1]);"
          "console.log(JSON.stringify(ITEMS.filter(i=>i.category==='hot')"
          ".map(i=>({id:i.id,name:i.name,weight:i.weight,price:i.price,unit:i.priceUnit||'шт.',img:i.img,images:i.images||[i.img]}))))")
    out = subprocess.run(["node", "-e", js, str(SITE / "js" / "data.js")], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def build():
    items = hot_items()
    assert items, "no hot dishes in data.js"
    e = html.escape
    url = BASE + PAGE_PATH
    # The four biggest dishes for the intro: "Лосось Веллингтон, мясо по-французски, ..."
    top = [i["name"].split(" (")[0] for i in sorted(items, key=lambda i: -i["price"])[:4]]
    names = ", ".join([top[0]] + [n[:1].lower() + n[1:] for n in top[1:]])
    title = "Горячее на праздничный стол в Минске — заказать с доставкой | Draft Catering"
    description = (f"Горячее на праздничный стол в Минске: {names} и другие блюда от {min(i['price'] for i in items):g} BYN. "
                   "Заказ онлайн, доставка по Минску и самовывоз.")
    faq = [
        ("Какие горячие блюда можно заказать?",
         "Сейчас в меню: " + "; ".join(f"{i['name']} — {i['weight']}, {i['price']:g} BYN" for i in items) + ". Состав и вес указаны на карточках."),
        ("Можно заказать горячее вместе с закусками?",
         "Да. Корзина общая для всего сайта: добавьте горячее на этой странице, а закуски — из <a href=\"/gotovye-furshetnye-boksy/\">готовых боксов</a> "
         "или <a href=\"/#constructor\">меню</a>. Всё попадёт в одну заявку."),
        ("За сколько дней оформить заказ?",
         "Желательно за 2–3 дня, перед праздниками — раньше. Срочный заказ возможен по согласованию — администратор проверит, что мы успеем приготовить к нужному времени."),
        FAQ_DELIVERY,
        ("Есть ли подарок или скидка?", f"{GIFT} {BIRTHDAY} {NO_STACK}"),
        ("Как оплатить?",
         f"Наличными или картой — способ выбирается в заявке. Для компаний доступен безналичный расчёт. Вопросы — по номеру {PHONE}."),
    ]
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Горячее на праздничный стол", "item": url}]},
        {"@type": "ItemList", "@id": url + "#dishes", "name": "Горячее на праздничный стол", "numberOfItems": len(items),
         "itemListElement": [
             {"@type": "ListItem", "position": n + 1, "item": {
                 "@type": "Product", "@id": url + "#" + i["id"], "name": i["name"], "description": f'{i["name"]}, {i["weight"]}',
                 "image": [BASE + "/" + src for src in i["images"]], "brand": {"@type": "Brand", "name": "Draft Catering"},
                 "offers": {"@type": "Offer", "price": f'{i["price"]:.2f}', "priceCurrency": "BYN", "availability": "https://schema.org/InStock",
                            "url": url + "#" + i["id"], "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}}}
             for n, i in enumerate(items)]},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in faq]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    css_version = hashlib.md5((SITE / 'css' / 'boxes-page.css').read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    header = header.replace('href="/#faq"', 'href="#faq"').replace('href="/#reviews"', 'href="#reviews"')
    # Static fallback cards; js/app.js replaces them with interactive cards (photos, cart).
    cards = ''.join(
        f'<article class="card card-simple" id="{i["id"]}"><div class="card-photo"><span class="card-badge">Новинка</span>'
        f'<img src="/{i["img"]}" alt="{e(i["name"])}" loading="lazy" width="1200" height="900"></div>'
        f'<div class="card-body"><div class="card-name">{e(i["name"])}</div><div class="card-weight">Вес: {e(i["weight"])}</div>'
        f'<div class="card-footer"><div class="card-price-block" data-price-summary="{i["id"]}"><div class="card-price">{i["price"]:g} BYN / 1 {e(i["unit"])}</div></div>'
        f'<div class="card-action" data-control="{i["id"]}"></div></div></div></article>'
        for i in items)
    faq_html = ('<section class="section faq-page" id="faq"><div class="wrap"><h2>Вопросы о заказе горячего</h2><div class="faq-page-list">'
                + ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in faq) + '</div></div></section>')
    terms = ('<li><strong>Предзаказ:</strong> желательно за 2–3 дня; перед праздниками — раньше.</li>'
             '<li><strong>Подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г).</li>'
             '<li><strong>Для компаний:</strong> безналичный расчёт, документы согласуются индивидуально.</li>' + TERM_DELIVERY + TERM_MORE)
    links = ''.join(f'<a href="{h}">{e(l)}</a>' for h, l in [
        ("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/novogodniy-furshet/", "Новогодний фуршет"), ("/keytering-na-den-rozhdeniya/", "На день рождения"),
        ("/keytering-na-korporativ/", "На корпоратив"), ("/furshet-na-zakaz/", "Фуршет на заказ"), ("/dostavka-zakusok/", "Закуски на заказ"),
        ("/furshet-na-10-chelovek/", "На 10 человек"), ("/dostavka-i-oplata/", "Доставка и оплата")])
    hero_img = BASE + "/" + items[0]["img"]

    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{hero_img}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20261104b"><link rel="stylesheet" href="/css/boxes-page.css?v={css_version}"><link rel="stylesheet" href="/css/reviews.css?v={asset_version('css/reviews.css')}"><link rel="stylesheet" href="/css/occasion-pages.css?v={asset_version('css/occasion-pages.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Горячее на праздничный стол</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>НОВИНКА · МИНСК</span></div><h1>Горячее <span>на праздничный стол</span></h1><p>{e(names)} и другие блюда целиком — на всю компанию. Добавляйте горячее в корзину прямо здесь, а к нему — закуски из готовых боксов: заявка будет одна.</p><div class="boxes-hero-actions"><a class="primary-link" href="#dishes"><strong>Смотреть блюда</strong><span aria-hidden="true">↓</span></a><a class="secondary-link" href="/gotovye-furshetnye-boksy/"><strong>Закуски к горячему</strong><span aria-hidden="true">→</span></a></div></div></div></section>
<section class="boxes-guide" aria-labelledby="guide-title"><div class="wrap boxes-guide-layout"><div class="boxes-guide-offer"><h2 id="guide-title">Стол на компанию?</h2><p>Посмотрите готовые наборы на 10 человек с весом на гостя и добавьте к ним горячее.</p><a class="secondary-link" href="/furshet-na-10-chelovek/"><strong>Наборы на 10 человек</strong><span aria-hidden="true">→</span></a></div><ul class="boxes-terms" aria-label="Условия заказа">{terms}</ul></div></section>
<section class="section" id="dishes" aria-label="Горячие блюда"><div class="wrap"><div class="grid" data-menu-category="hot">{cards}</div>
<aside class="occasion-more" aria-labelledby="more-title"><div><h2 id="more-title">Добавьте закуски</h2><p>К горячему обычно берут закуски: в готовых боксах — канапе, брускетты, тарталетки, рулетики и десерты. Корзина общая: всё попадёт в одну заявку.</p></div><div class="occasion-more-actions"><a class="primary-link" href="/gotovye-furshetnye-boksy/"><strong>Готовые боксы</strong><span aria-hidden="true">→</span></a><a class="secondary-link" href="/#constructor"><strong>Всё меню</strong><span aria-hidden="true">→</span></a></div></aside></div></section>
{reviews_html('wrap')}
{faq_html}
<section class="section facts"><div class="wrap"><h2>Другие категории и услуги</h2><div class="links">{links}</div></div></section></main>
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
    print(f"{out.relative_to(SITE.parent)}: {len(items)} hot dishes")


if __name__ == "__main__":
    build()
