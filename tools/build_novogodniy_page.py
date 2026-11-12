#!/usr/bin/env python3
"""Build site/novogodniy-furshet/index.html — New Year buffet page with real boxes and the shared cart.

Boxes (photos, composition, weight, price, "add to cart") are copied from the home page,
like on /gotovye-furshetnye-boksy/, so run this after any change to the ready boxes:
    python3 tools/build_novogodniy_page.py
"""
import hashlib
import html
import json
import re
from datetime import date

from build_boxes_page import (BASE, SITE, asset_version, box_data, control_id, ensure_home_ids,
                              home_shell, reviews_html, text, to_seo_card)

PAGE_PATH = "/novogodniy-furshet/"
# Boxes for a New Year table, in display order (ids from the home page).
FEATURED = [
    "box-sparkling", "box-salmon-crab", "box-canapes", "box-bruschetta-salmon-shrimp",
    "box-mini-tartlets", "box-baked-tartlets", "box-napoleons", "box-assorted-rolls",
    "box-three-rolls", "box-crostini", "box-profiteroles", "box-chocolate-cakes", "box-basque-cheesecake",
]

FAQ = [
    ("Когда заказывать новогодний фуршет?",
     "Обычно заказ оформляют за 2–3 дня, но даты перед Новым годом востребованы, поэтому лучше оставить заявку как можно раньше. "
     "Администратор подтвердит, что мы успеем приготовить всё к нужному дню и времени."),
    ("Можно заказать фуршет в офис на корпоратив?",
     "Да, принимаем корпоративные заказы и работаем по безналичному расчёту. Необходимые документы для компании согласуются индивидуально — "
     "напишите об этом в комментарии к заявке или позвоните по номеру <a href=\"tel:+375295704749\">+375 29 570-47-49</a>."),
    ("Сколько закусок нужно на компанию?",
     "Проще всего начать с готовых наборов: на странице <a href=\"/furshet-na-10-chelovek/\">«Фуршет на 10 человек»</a> у каждого набора указан вес на гостя. "
     "Для большой компании посмотрите варианты <a href=\"/furshet-na-20-chelovek/\">на 20</a> и <a href=\"/furshet-na-30-chelovek/\">на 30 человек</a> или напишите количество гостей в заявке — администратор подскажет."),
    ("Можно совместить несколько боксов и заказать один бокс?",
     "Да. Корзина общая для всего сайта: добавьте несколько боксов с этой страницы или из <a href=\"/#constructor\">меню</a> — всё попадёт в одну заявку. "
     "Минимальной суммы заказа нет."),
    ("Есть ли подарок или скидка?",
     "При заказе от 200 BYN дарим шпинатный рулет (450 г). Именинникам — скидка 10% за 5 дней до и 5 дней после дня рождения. "
     "Акции не суммируются: можно выбрать скидку или рулет в подарок."),
    ("Как получить заказ и сколько стоит доставка?",
     "Самовывоз — Минск, ул. Нововиленская, 51, бесплатно. Доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно; "
     "за МКАД стоимость рассчитает администратор. Подробнее — на странице <a href=\"/dostavka-i-oplata/\">«Доставка и оплата»</a>."),
]


def build():
    articles = {control_id(a): a for a in ensure_home_ids()}
    missing = [i for i in FEATURED if i not in articles]
    assert not missing, f"boxes not on the home page: {missing}"
    chosen = [articles[i] for i in FEATURED]
    boxes = [box_data(a) for a in chosen]
    cards = ''.join(to_seo_card(a, False) for a in chosen)
    min_price = min(b["price"] for b in boxes)
    url = BASE + PAGE_PATH
    title = "Новогодний фуршет в Минске — боксы и закуски с доставкой | Draft Catering"
    description = (f"Новогодний фуршет в Минске: {len(boxes)} готовых боксов от {min_price} BYN — канапе, брускетты, тарталетки, рулеты и десерты. "
                   "Для офиса и дома, безналичный расчёт, доставка и самовывоз.")
    og_image = BASE + boxes[0]["images"][0] if boxes[0]["images"][0].startswith('/') else boxes[0]["images"][0]
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Новогодний фуршет в Минске", "item": url}]},
        {"@type": "CollectionPage", "@id": url + "#page", "url": url, "name": "Новогодний фуршет в Минске",
         "description": description, "inLanguage": "ru-BY",
         "isPartOf": {"@type": "WebSite", "name": "Draft Catering", "url": BASE + "/"},
         "mainEntity": {"@id": url + "#boxes"}},
        {"@type": "ItemList", "@id": url + "#boxes", "name": "Боксы для новогоднего фуршета", "numberOfItems": len(boxes),
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "item": {
                 "@type": "Product", "@id": BASE + "/gotovye-furshetnye-boksy/#" + b["id"], "name": b["name"],
                 "description": b["description"], "image": b["images"], "brand": {"@type": "Brand", "name": "Draft Catering"},
                 "offers": {"@type": "Offer", "price": f'{b["price"]:.2f}', "priceCurrency": "BYN",
                            "availability": "https://schema.org/InStock", "url": url + "#" + b["id"],
                            "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}}}
             for i, b in enumerate(boxes)]},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in FAQ]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    css_version = hashlib.md5((SITE / 'css' / 'boxes-page.css').read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    header = header.replace('href="/#faq"', 'href="#faq"').replace('href="/#reviews"', 'href="#reviews"')
    e = html.escape
    faq_html = ('<section class="section faq-page" id="faq"><div class="wrap"><h2>Вопросы о новогоднем фуршете</h2><div class="faq-page-list">'
                + ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in FAQ) + '</div></div></section>')

    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20261104b"><link rel="stylesheet" href="/css/boxes-page.css?v={css_version}"><link rel="stylesheet" href="/css/reviews.css?v={asset_version('css/reviews.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Новогодний фуршет в Минске</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>НОВЫЙ ГОД · МИНСК</span></div><h1>Новогодний <span>фуршет</span> в Минске</h1><p>Готовые боксы с закусками и десертами для корпоратива в офисе, встречи с друзьями или домашнего Нового года. Закуски приезжают красиво разложенными — их можно сразу ставить на стол. У каждого бокса указаны состав, количество, вес и цена; добавляйте боксы в корзину прямо здесь.</p><div class="boxes-hero-actions"><a class="primary-link" href="#boxes"><strong>Смотреть боксы</strong><span aria-hidden="true">↓</span></a></div></div></div></section>
<section class="boxes-guide" aria-labelledby="guide-title"><div class="wrap boxes-guide-layout"><div class="boxes-guide-offer"><h2 id="guide-title">Фуршет на компанию?</h2><p>Посмотрите готовые наборы с весом на гостя — так проще рассчитать угощение на корпоратив или праздник.</p><a class="secondary-link" href="/furshet-na-10-chelovek/"><strong>Наборы на 10 человек</strong><span aria-hidden="true">→</span></a></div><ul class="boxes-terms" aria-label="Условия заказа"><li><strong>Предзаказ:</strong> обычно за 2–3 дня; даты перед Новым годом лучше бронировать заранее.</li><li><strong>Для компаний:</strong> безналичный расчёт, документы согласуются индивидуально.</li><li><strong>Подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г).</li><li><strong>Доставка по Минску:</strong> в пределах МКАД — 20 BYN, от 500 BYN — бесплатно. Самовывоз: ул. Нововиленская, 51.</li><li class="boxes-terms-more"><a href="/dostavka-i-oplata/">Доставка и оплата</a></li></ul></div></section>
<section class="boxes-list" id="boxes" aria-label="Боксы для новогоднего фуршета"><div class="wrap"><div class="ready-grid">
{cards}</div><p class="other-snacks-all"><a class="primary-link" href="/gotovye-furshetnye-boksy/"><strong>Все готовые боксы</strong><span aria-hidden="true">→</span></a></p></div></section>
{reviews_html('wrap')}
{faq_html}
<section class="section"><div class="wrap text-grid"><h2>Как оформить заказ</h2><p>Соберите заказ из боксов на этой странице, добавьте позиции из <a href="/#constructor">меню</a> и отправьте заявку — корзина общая для всего сайта. Количество гостей и пожелания напишите в комментарии.</p><p>Это заявка, а не автоматическое подтверждение: администратор свяжется с вами, подтвердит состав, дату, время и итоговую стоимость. Вопросы — по номеру <a href="tel:+375295704749">+375 29 570-47-49</a>.</p></div></section>
<section class="section facts"><div class="wrap"><h2>Другие категории и услуги</h2><div class="links"><a href="/gotovye-furshetnye-boksy/">Готовые боксы</a><a href="/keytering-na-korporativ/">На корпоратив</a><a href="/keytering-dlya-ofisa/">Для офиса</a><a href="/furshet-na-10-chelovek/">На 10 человек</a><a href="/furshet-na-20-chelovek/">На 20 человек</a><a href="/furshet-na-30-chelovek/">На 30 человек</a><a href="/kanape-na-zakaz/">Канапе</a><a href="/brusketty-na-zakaz/">Брускетты</a><a href="/tartaletki-na-zakaz/">Тарталетки</a><a href="/keytering-na-den-rozhdeniya/">На день рождения</a><a href="/dostavka-i-oplata/">Доставка и оплата</a></div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / PAGE_PATH.strip('/') / "index.html"
    out.write_text(page, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    print(f"{out.relative_to(SITE.parent)}: {len(boxes)} boxes, from {min_price} BYN")


if __name__ == "__main__":
    build()
