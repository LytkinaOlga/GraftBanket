#!/usr/bin/env python3
"""Build site/gotovye-furshetnye-boksy/index.html from the ready boxes on the home page.

Run after any change to ready boxes in site/index.html:
    python3 tools/build_boxes_page.py

The script also makes sure every box card on the home page has an id
(box-<id>), so "Заказать" links from the SEO page land on the right card.
"""
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


def to_seo_card(article, first):
    cid = control_id(article)
    card = article.split('\n', 1)
    card[0] = re.sub(r' id="[^"]*"', '', card[0])
    card = '\n'.join(card)
    card = card.replace('<article class=', f'<article id="{cid}" class=', 1)
    card = re.sub(r'(<img[^>]+src=")(?!/|https?:)', r'\1/', card)
    if first:
        card = card.replace(' loading="lazy"', ' fetchpriority="high"', 1)
    button = f'<div class="ready-box-action"><a class="add-btn" href="/#{cid}">Заказать</a></div>'
    card = re.sub(r'<div class="ready-box-action" data-control="[^"]+"></div>', button, card)
    card = card.replace('<h3>', '<h2 class="ready-box-title">', 1).replace('</h3>', '</h2>', 1)
    return card


def build():
    articles = ensure_home_ids()
    boxes = [box_data(a) for a in articles]
    cards = ''.join(to_seo_card(a, i == 0) for i, a in enumerate(articles))
    count = len(boxes)
    min_price = min(b["price"] for b in boxes)
    title = "Готовые фуршетные боксы в Минске — цены и составы | Draft Catering"
    description = (f"{count} готовых фуршетных боксов Draft Catering: брускетты, канапе, тарталетки, "
                   f"наполеоны, салаты, пироги и десерты. Состав, вес и цены от {min_price} BYN, доставка по Минску.")
    url = BASE + PAGE_PATH
    og_image = boxes[0]["images"][0]
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
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    e = html.escape
    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){{if(document.scripts[j].src===r){{return;}}}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,'script','https://mc.yandex.ru/metrika/tag.js?id=113018653','ym');ym(113018653,'init',{{ssr:true,webvisor:true,clickmap:true,referrer:document.referrer,url:location.href,accurateTrackBounce:true,trackLinks:true}});</script>
<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="preload" as="image" href="{og_image.replace(BASE, '')}"><link rel="stylesheet" href="/css/seo-pages.css?v=20260926"><link rel="stylesheet" href="/css/boxes-page.css?v={date.today():%Y%m%d}">
<script type="application/ld+json">{ld}</script></head><body>
<noscript><div><img src="https://mc.yandex.ru/watch/113018653" style="position:absolute;left:-9999px" alt=""></div></noscript>
<header class="topbar"><div class="wrap"><a class="logo" href="/"><img src="/assets/draft-catering-logo.webp" alt="Draft Catering" width="180" height="180"></a><div class="top-contact"><a href="/">Всё меню</a><a href="tel:+375295704749">+375 29 570-47-49</a></div></div></header>
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Готовые фуршетные боксы в Минске</nav>
<section class="section boxes-intro"><div class="wrap"><span class="eyebrow">Готовые решения</span><h1>Готовые фуршетные боксы в Минске</h1><p class="lead">{count} готовых боксов с закусками, салатами, пирогами и десертами — для офиса, дня рождения или домашней встречи. У каждого бокса указаны состав, количество, вес и цена. Чтобы заказать, нажмите «Заказать» — бокс откроется в меню на главной странице, где его можно положить в корзину.</p></div></section>
<section class="boxes-list" aria-label="Все готовые боксы"><div class="wrap"><div class="ready-grid">
{cards}</div></div></section>
<section class="section facts"><div class="wrap"><div class="facts-grid"><div class="fact"><strong>{count} готовых боксов</strong><span>Составы, вес и актуальные цены — на этой странице и в основном меню.</span></div><div class="fact"><strong>От 2–3 дней</strong><span>Рекомендуемый срок оформления заказа; срочные заказы уточняются.</span></div><div class="fact"><strong>Доставка по Минску</strong><span>В пределах МКАД — 20 BYN, от 500 BYN — бесплатно.</span></div></div></div></section>
<section class="section"><div class="wrap text-grid"><h2>Как оформить заказ</h2><p>Все наборы собраны так, чтобы закуски было удобно подать без дополнительной сервировки. Можно выбрать готовый бокс или собрать собственный набор из отдельных позиций в <a href="/#constructor">меню</a>.</p><p>Оставьте заявку на сайте или позвоните по номеру <a href="tel:+375295704749">+375 29 570-47-49</a>. Администратор свяжется с вами, подтвердит состав, дату, способ получения и итоговую стоимость.</p><p><strong>Самовывоз:</strong> Минск, ул. Нововиленская, 51 — бесплатно.</p><p><strong>Доставка:</strong> по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно. Подробнее — на странице <a href="/dostavka-i-oplata/">«Доставка и оплата»</a>.</p></div></section>
<section class="section facts"><div class="wrap"><h2>Другие категории и услуги</h2><div class="links"><a href="/furshet-na-zakaz/">Фуршет на заказ</a><a href="/dostavka-zakusok/">Доставка закусок</a><a href="/brusketty-na-zakaz/">Брускетты</a><a href="/tartaletki-na-zakaz/">Тарталетки</a><a href="/kanape-na-zakaz/">Канапе</a><a href="/keytering-dlya-ofisa/">Для офиса и корпоратива</a><a href="/keytering-na-den-rozhdeniya/">На день рождения</a><a href="/o-nas/">О нас</a><a href="/dostavka-i-oplata/">Доставка и оплата</a></div></div></section></main>
<footer class="footer"><div class="wrap"><span>Draft Catering · Минск</span><span>ул. Нововиленская, 51 · +375 29 570-47-49</span></div></footer>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('[data-gallery-prev],[data-gallery-next]');if(!b)return;var t=b.closest('[data-gallery]').querySelector('.ready-box-gallery-track');t.scrollBy({{left:t.clientWidth*(b.hasAttribute('data-gallery-next')?1:-1),behavior:'smooth'}});}});document.querySelectorAll('[data-gallery]').forEach(function(g){{var t=g.querySelector('.ready-box-gallery-track'),d=g.querySelectorAll('.gallery-dots span');t.addEventListener('scroll',function(){{var a=Math.round(t.scrollLeft/Math.max(t.clientWidth,1));d.forEach(function(x,i){{x.classList.toggle('active',i===a);}});}},{{passive:true}});}});</script>
</body></html>
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
