#!/usr/bin/env python3
"""Build site/gotovye-furshetnye-boksy/index.html from the ready boxes on the home page.

Run after any change to ready boxes in site/index.html:
    python3 tools/build_boxes_page.py

The script also makes sure every box card on the home page has an id
(box-<id>), so "Заказать" links from the SEO page land on the right card.
"""
import hashlib
import html
import json
import re
from datetime import date
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
BASE = "https://www.draftcatering.by"
PAGE_PATH = "/gotovye-furshetnye-boksy/"
END = '        </article>\n'


def split_articles(page):
    parts = re.split(r'(?=        <article (?:id="[^"]*" )?class="ready-box)', page)
    head, articles = parts[0], parts[1:]
    last = articles[-1]
    cut = last.index(END) + len(END)
    tail, articles[-1] = last[cut:], last[:cut]
    for a in articles:
        assert a.endswith(END) and a.count('ready-box-kicker') == 1, a[:120]
    return head, articles, tail


def control_id(article):
    return re.search(r'data-control="([^"]+)"', article).group(1)


def is_hidden(article):
    return ' hidden>' in article.split('\n', 1)[0]


def ensure_home_ids():
    path = SITE / "index.html"
    page = path.read_text(encoding="utf-8")
    head, articles, tail = split_articles(page)
    changed = False
    for i, a in enumerate(articles):
        first, rest = a.split('\n', 1)
        if ' id="box-' not in first:
            cid = control_id(a)
            first = first.replace('<article class=', f'<article id="{cid}" class=', 1)
            articles[i] = first + '\n' + rest
            changed = True
    if changed:
        path.write_text(head + ''.join(articles) + tail, encoding="utf-8")
    return [a for a in articles if not is_hidden(a)]


def text(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def box_data(article):
    cid = control_id(article)
    name = text(re.search(r'<h3>(.*?)</h3>', article, re.S).group(1))
    kicker_line = next(line for line in article.split('\n') if 'ready-box-kicker' in line)
    kicker = re.sub(r'\s+', ' ', text(kicker_line))
    price = int(re.search(r'<strong>(\d+) BYN</strong>', article).group(1))
    items = [text(li).rstrip(';') for li in re.findall(r'<li>(.*?)</li>', article, re.S)]
    notes = [text(p) for p in re.findall(r'<p(?:\s[^>]*)?>(.*?)</p>', article, re.S)]
    images = [BASE + '/' + src.lstrip('/') for src in re.findall(r'<img[^>]+src="([^"]+)"', article)]
    description = kicker + ': ' + ('; '.join(items) if items else ' '.join(notes))
    return {"id": cid, "name": name, "price": price, "images": images, "description": description.strip()}

FAQ = [
    ("Как заказать готовый бокс?",
     "Нажмите «Добавить» на карточке бокса — он попадёт в корзину. Корзина общая для всего сайта, поэтому можно добавить боксы здесь и отдельные закуски из <a href=\"/#constructor\">меню</a>. Затем оформите заявку: дата, время, способ получения и оплаты. Администратор свяжется с вами и подтвердит заказ."),
    ("Можно ли заменить начинки или изменить состав бокса?",
     "Да, можно обсудить индивидуальный состав или приготовить блюдо по вашему референсу. Позвоните по номеру <a href=\"tel:+375295704749\">+375 29 570-47-49</a> или напишите пожелания в комментарии к заявке — администратор предложит варианты."),
    ("За сколько дней нужно оформить заказ? Можно ли срочно?",
     "Желательно оформить заказ за 2–3 дня, а для крупных мероприятий — как можно раньше. Срочные заказы тоже возможны: позвоните нам, и мы проверим, что успеем приготовить к нужному времени."),
    ("Есть ли доставка и сколько она стоит?",
     "Самовывоз по адресу Минск, Нововиленская, 51 — бесплатно. Доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно. Доставку за пределы МКАД администратор рассчитает отдельно."),
    ("Как оплатить заказ?",
     "Наличными или картой — способ оплаты выбирается в форме заявки. Для компаний доступен безналичный расчёт, условия и документы согласует администратор."),
    ("Какие есть акции и суммируются ли они?",
     "При заказе от 200 BYN дарим малый бокс профитролей. Именинникам — скидка 10% за 5 дней до и 5 дней после дня рождения: отметьте «У меня день рождения» в заявке. Акции не суммируются — при заказе от 200 BYN имениннику предложим выбрать скидку или подарок."),
    ("Как узнать состав, если есть аллергия?",
     "Основные ингредиенты указаны на карточке каждого бокса. Если у кого-то из гостей аллергия или особые предпочтения, напишите об этом в комментарии к заявке или позвоните — администратор уточнит состав."),
]


def home_shell():
    """Header, search, footer, cart overlay and scripts taken from the home page."""
    page = (SITE / "index.html").read_text(encoding="utf-8")
    def between(start, end):
        i = page.index(start)
        return page[i:page.index(end, i)]
    metrika = between('<script>window.dataLayer', '<meta charset')
    header = between('  <header class="site-header">', '    <nav class="category-nav">')
    bottom = between('  <footer class="site-footer">', '  <script src="js/data.js')
    scripts = between('  <script src="js/data.js', '</body>')
    styles = re.search(r'<link rel="stylesheet" href="(css/styles\.css\?v=[^"]+)"', page).group(1)
    def absolutize(fragment):
        fragment = re.sub(r'href="#', 'href="/#', fragment)
        fragment = re.sub(r'(src|href)="(assets|js|css)/', r'\1="/\2/', fragment)
        return fragment
    header = absolutize(header).replace('href="/#top"', 'href="/"')
    return metrika, header, absolutize(bottom), absolutize(scripts), '/' + styles


def to_seo_card(article, first):
    cid = control_id(article)
    card = article.split('\n', 1)
    card[0] = re.sub(r' id="[^"]*"', '', card[0])
    card = '\n'.join(card)
    card = card.replace('<article class=', f'<article id="{cid}" class=', 1)
    card = re.sub(r'((?:src|srcset)=")(?!/|https?:|data:)', r'\1/', card)
    if first:
        card = card.replace(' loading="lazy"', ' fetchpriority="high"', 1)
    card = card.replace('<h3>', '<h2 class="ready-box-title">', 1).replace('</h3>', '</h2>', 1)
    return card


def build():
    articles = ensure_home_ids()
    boxes = [box_data(a) for a in articles]
    cards = ''.join(to_seo_card(a, False) for i, a in enumerate(articles))
    count = len(boxes)
    min_price = min(b["price"] for b in boxes)
    title = "Готовые фуршетные боксы в Минске — цены и составы | Draft Catering"
    description = (f"{count} готовых фуршетных боксов Draft Catering: брускетты, канапе, тарталетки, "
                   f"наполеоны, салаты, пироги и десерты. Состав, вес и цены от {min_price} BYN, доставка по Минску.")
    url = BASE + PAGE_PATH
    og_image = BASE + "/assets/boxes/boxes-page-hero.jpg"
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Готовые фуршетные боксы в Минске", "item": url}]},
        {"@type": "CollectionPage", "@id": url + "#page", "url": url, "name": "Готовые фуршетные боксы в Минске",
         "description": description, "inLanguage": "ru-BY",
         "isPartOf": {"@type": "WebSite", "name": "Draft Catering", "url": BASE + "/"},
         "mainEntity": {"@id": url + "#boxes"}},
        {"@type": "ItemList", "@id": url + "#boxes", "name": "Готовые фуршетные боксы", "numberOfItems": count,
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "item": {
                 "@type": "Product", "@id": url + "#" + b["id"], "name": b["name"], "description": b["description"],
                 "image": b["images"], "brand": {"@type": "Brand", "name": "Draft Catering"},
                 "offers": {"@type": "Offer", "price": f'{b["price"]:.2f}', "priceCurrency": "BYN",
                            "availability": "https://schema.org/InStock", "url": url + "#" + b["id"],
                            "areaServed": {"@type": "City", "name": "Минск"},
                            "seller": {"@id": BASE + "/#business"}}}}
             for i, b in enumerate(boxes)]},
    ]
    graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in FAQ]})
    faq_html = '<section class="section faq-page" id="faq"><div class="wrap"><h2>Частые вопросы о готовых боксах</h2><div class="faq-page-list">' + ''.join(
        f'<details><summary>{html.escape(q)}</summary><p>{a}</p></details>' for q, a in FAQ) + '</div></div></section>'
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    css_version = hashlib.md5((SITE / 'css' / 'boxes-page.css').read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = home_shell()
    e = html.escape
    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20260926"><link rel="stylesheet" href="/css/boxes-page.css?v={css_version}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Готовые фуршетные боксы в Минске</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>ГОТОВЫЕ РЕШЕНИЯ · МИНСК</span></div><h1>Готовые <span>фуршетные боксы</span> в Минске</h1><p>{count} готовых боксов с закусками, салатами, пирогами и десертами — для офиса, дня рождения или домашней встречи. У каждого бокса указаны состав, количество, вес и цена. Добавляйте боксы в корзину прямо здесь — она общая для всего сайта.</p><div class="boxes-hero-actions"><a class="primary-link" href="#boxes"><strong>Смотреть боксы</strong><span aria-hidden="true">↓</span></a></div></div></div></section>
<section class="boxes-list" id="boxes" aria-label="Все готовые боксы"><div class="wrap"><div class="ready-grid">
{cards}</div></div></section>
{faq_html}
<section class="section facts"><div class="wrap"><div class="facts-grid"><div class="fact"><strong>{count} готовых боксов</strong><span>Составы, вес и актуальные цены — на этой странице и в основном меню.</span></div><div class="fact"><strong>От 2–3 дней</strong><span>Рекомендуемый срок оформления заказа; срочные заказы уточняются.</span></div><div class="fact"><strong>Доставка по Минску</strong><span>В пределах МКАД — 20 BYN, от 500 BYN — бесплатно.</span></div></div></div></section>
<section class="section"><div class="wrap text-grid"><h2>Как оформить заказ</h2><p>Все наборы собраны так, чтобы закуски было удобно подать без дополнительной сервировки. Можно выбрать готовый бокс или собрать собственный набор из отдельных позиций в <a href="/#constructor">меню</a>.</p><p>Оставьте заявку на сайте или позвоните по номеру <a href="tel:+375295704749">+375 29 570-47-49</a>. Администратор свяжется с вами, подтвердит состав, дату, способ получения и итоговую стоимость.</p><p><strong>Самовывоз:</strong> Минск, ул. Нововиленская, 51 — бесплатно.</p><p><strong>Доставка:</strong> по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно. Подробнее — на странице <a href="/dostavka-i-oplata/">«Доставка и оплата»</a>.</p></div></section>
<section class="section facts"><div class="wrap"><h2>Другие категории и услуги</h2><div class="links"><a href="/furshet-na-zakaz/">Фуршет на заказ</a><a href="/dostavka-zakusok/">Доставка закусок</a><a href="/brusketty-na-zakaz/">Брускетты</a><a href="/tartaletki-na-zakaz/">Тарталетки</a><a href="/kanape-na-zakaz/">Канапе</a><a href="/keytering-dlya-ofisa/">Для офиса и корпоратива</a><a href="/keytering-na-den-rozhdeniya/">На день рождения</a><a href="/o-nas/">О нас</a><a href="/dostavka-i-oplata/">Доставка и оплата</a></div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / PAGE_PATH.strip('/') / "index.html"
    out.write_text(page, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    print(f"{out.relative_to(SITE.parent)}: {count} boxes, from {min_price} BYN")


if __name__ == "__main__":
    build()
