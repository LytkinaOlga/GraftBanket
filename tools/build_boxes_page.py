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
     "Нажмите «Добавить» на карточке бокса — он попадёт в корзину. Затем оформите заявку: дата, время, способ получения и оплаты. Администратор свяжется с вами и подтвердит заказ."),
    ("Можно ли заменить начинки или изменить состав бокса?",
     "Да, можно обсудить индивидуальный состав или приготовить блюдо по вашему референсу. Позвоните по номеру <a href=\"tel:+375295704749\">+375 29 570-47-49</a> или напишите пожелания в комментарии к заявке — администратор предложит варианты. Если нужно учесть аллергены, тоже предупредите заранее: администратор расскажет о составе и согласует возможные замены."),
    ("За сколько дней нужно оформить заказ? Можно ли срочно?",
     "Желательно оформить заказ за 2–3 дня, а для крупных мероприятий — как можно раньше. Срочные заказы тоже возможны: позвоните нам, и мы проверим, что успеем приготовить к нужному времени."),
    ("Есть ли доставка и сколько она стоит?",
     "Самовывоз по адресу Минск, Нововиленская, 51 — бесплатно. Доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно. Доставку за пределы МКАД администратор рассчитает отдельно."),
    ("Есть ли минимальная сумма заказа?",
     "Нет, минимальной суммы нет — можно заказать даже одну позицию. Условия получения те же: самовывоз бесплатно, доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно."),
    ("Когда можно оставить заявку?",
     "Заявку на сайте можно оставить круглосуточно. Администратор работает каждый день с 10:00 до 22:00 и свяжется с вами в это время."),
    ("Как оплатить заказ?",
     "Наличными или картой — способ оплаты выбирается в форме заявки. Для компаний доступен безналичный расчёт, условия и документы согласует администратор."),
    ("Какие есть акции и суммируются ли они?",
     "При заказе от 300 BYN дарим малый бокс профитролей. Именинникам — скидка 10% за 5 дней до и 5 дней после дня рождения: отметьте «У меня день рождения» в заявке. Акции не суммируются — при заказе от 300 BYN имениннику предложим выбрать скидку или подарок."),
]


MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
PREVIEW_CHARS = 100
PREVIEW_CUT = 70


def reviews_html(wrap_class):
    """Client reviews carousel from tools/reviews.json (texts verbatim, see SEO/otzyvy).

    Shared by the home page and this page: css/reviews.css, js/reviews.js, images in assets/reviews/.
    """
    reviews = json.loads((Path(__file__).with_name("reviews.json")).read_text(encoding="utf-8"))
    if not reviews:
        return ''
    def paragraphs(parts):
        return ''.join('<p>' + html.escape(p).replace('\n', '<br>') + '</p>' for p in parts)
    def arrow(d):
        return ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"/></svg>')
    total = len(reviews)
    cards, dots = [], []
    for n, r in enumerate(reviews, 1):
        d = date.fromisoformat(r["date"])
        human = f'{d.day} {MONTHS[d.month - 1]} {d.year}'
        full = ' '.join(r["text"])
        if len(full) > PREVIEW_CHARS:
            cut = full[:PREVIEW_CUT].rsplit(' ', 1)[0].rstrip(',.;:!—- ')
            body = (f'<p class="review-preview">{html.escape(cut)}… '
                    '<button class="review-more" type="button" data-review-more>Читать полностью</button></p>'
                    f'<div class="review-full-text" hidden>{paragraphs(r["text"])}</div>')
        else:
            body = paragraphs(r["text"])
        img = f'/assets/reviews/review-{r["id"]}'
        cards.append(
            f'<li class="review-card" id="review-{r["id"]}" role="group" aria-roledescription="отзыв" aria-label="{n} из {total}">'
            '<span class="review-quote" aria-hidden="true">“</span>'
            f'<p class="review-date">{html.escape(r["date_label"])}: <time datetime="{r["date"]}">{human}</time></p>'
            f'<div class="review-text">{body}</div>'
            f'<a class="review-shot" href="{img}.jpg" data-review-shot aria-label="Увеличить скриншот отзыва ({human})">'
            f'<img src="{img}-thumb.jpg" srcset="{img}-thumb.jpg 400w, {img}.jpg 900w" sizes="(max-width:680px) 80vw, 400px" '
            f'alt="Скриншот переписки с отзывом, {human}" loading="lazy" decoding="async" width="400" height="240"></a></li>')
        dots.append(f'<button class="reviews-dot" type="button" data-review-dot="{n - 1}" aria-label="Отзыв {n} из {total}"></button>')
    return (f'<section class="reviews" id="reviews" aria-labelledby="reviews-title" aria-roledescription="карусель" data-reviews><div class="{wrap_class}">'
            '<div class="reviews-head"><div><span class="eyebrow">Ваши впечатления</span><h2 id="reviews-title">Отзывы наших клиентов</h2></div>'
            '<div class="reviews-arrows"><button class="reviews-arrow reviews-prev" type="button" aria-label="Предыдущий отзыв">' + arrow('M19 12H5m6-6-6 6 6 6') + '</button>'
            '<button class="reviews-arrow reviews-next" type="button" aria-label="Следующий отзыв">' + arrow('M5 12h14m-6-6 6 6-6 6') + '</button></div></div>'
            '<ul class="reviews-track" tabindex="0" aria-label="Отзывы, листайте стрелками">' + ''.join(cards) + '</ul>'
            '<div class="reviews-progress">' + ''.join(dots) + '</div>'
            f'<p class="reviews-count" aria-live="polite">1 / {total}</p></div></section>'
            '<dialog class="review-lightbox" aria-label="Скриншот отзыва"><form method="dialog">'
            '<button class="review-lightbox-close" aria-label="Закрыть">×</button></form><img alt=""></dialog>'
            '<dialog class="review-popup" aria-labelledby="review-popup-date"><form method="dialog">'
            '<button class="review-popup-close" aria-label="Закрыть">×</button></form>'
            '<p class="review-date" id="review-popup-date"></p><div class="review-popup-text"></div></dialog>')

def asset_version(rel):
    return hashlib.md5((SITE / rel).read_bytes()).hexdigest()[:8]


def sync_home_reviews():
    """Put the same reviews block on the home page, between "Как это работает" and "Меню и услуги"."""
    path = SITE / "index.html"
    page = path.read_text(encoding="utf-8")
    block = '    <!-- reviews:start (tools/build_boxes_page.py) -->\n    ' + reviews_html("container") + '\n    <!-- reviews:end -->\n'
    if '<!-- reviews:start' in page:
        page = re.sub(r'    <!-- reviews:start.*?<!-- reviews:end -->\n', lambda m: block, page, flags=re.S)
    else:
        anchor = '    <section class="container seo-services"'
        assert page.count(anchor) == 1
        page = page.replace(anchor, block + '\n' + anchor)
    css = f'<link rel="stylesheet" href="css/reviews.css?v={asset_version("css/reviews.css")}" />'
    page = re.sub(r'<link rel="stylesheet" href="css/reviews\.css\?v=[^"]*" />', css, page)
    if css not in page:
        page = page.replace('<link rel="stylesheet" href="css/styles.css', css + '\n<link rel="stylesheet" href="css/styles.css', 1)
    js = f'<script src="js/reviews.js?v={asset_version("js/reviews.js")}" defer></script>'
    page = re.sub(r'<script src="js/reviews\.js\?v=[^"]*" defer></script>', js, page)
    if js not in page:
        page = page.replace('</body>', '  ' + js + '\n</body>', 1)
    path.write_text(page, encoding="utf-8")

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
    sync_home_reviews()
    articles = ensure_home_ids()
    boxes = [box_data(a) for a in articles]
    cards = ''.join(to_seo_card(a, False) for i, a in enumerate(articles))
    count = len(boxes)
    min_price = min(b["price"] for b in boxes)
    title = "Готовые фуршетные боксы в Минске — цены и составы | Draft Catering"
    description = (f"Готовые фуршетные боксы в Минске: {count} вариантов с составом, весом и ценами. "
                   "Закуски для офиса и праздника. Доставка и самовывоз. Заказ в Draft Catering.")
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
    # The page has its own FAQ and reviews sections, so keep these header links on this page.
    header = header.replace('href="/#faq"', 'href="#faq"').replace('href="/#reviews"', 'href="#reviews"')
    e = html.escape
    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20260926"><link rel="stylesheet" href="/css/boxes-page.css?v={css_version}"><link rel="stylesheet" href="/css/reviews.css?v={asset_version('css/reviews.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → Готовые фуршетные боксы в Минске</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>ГОТОВЫЕ РЕШЕНИЯ · МИНСК</span></div><h1>Готовые <span>фуршетные боксы</span> в Минске</h1><p>{count} готовых боксов с закусками, салатами, пирогами и десертами — для офиса, дня рождения или домашней встречи. У каждого бокса указаны состав, количество, вес и цена. Добавляйте боксы в корзину прямо здесь — она общая для всего сайта.</p><div class="boxes-hero-actions"><a class="primary-link" href="#boxes"><strong>Смотреть боксы</strong><span aria-hidden="true">↓</span></a></div></div></div></section>
<section class="boxes-guide" aria-labelledby="guide-10-title"><div class="wrap boxes-guide-layout"><div class="boxes-guide-offer"><h2 id="guide-10-title">Выбираете угощение на 10 человек?</h2><p>Посмотрите предложения для компании из 10 гостей — так проще подобрать боксы для встречи, дня рождения или праздника в офисе.</p><a class="secondary-link" href="/furshet-na-10-chelovek/"><strong>Посмотреть предложения на 10 человек</strong><span aria-hidden="true">→</span></a></div><ul class="boxes-terms" aria-label="Условия заказа"><li><strong>Предзаказ:</strong> желательно за 2–3 дня. Срочный заказ — по согласованию.</li><li><strong>Доставка по Минску:</strong> в пределах МКАД — 20 BYN, от 500 BYN — бесплатно.</li><li><strong>Самовывоз:</strong> Минск, ул. Нововиленская, 51 — бесплатно.</li><li class="boxes-terms-more"><a href="/dostavka-i-oplata/">Доставка и оплата</a></li></ul></div></section>
<section class="boxes-list" id="boxes" aria-label="Все готовые боксы"><div class="wrap"><div class="ready-grid">
{cards}</div></div></section>
{reviews_html('wrap')}
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
