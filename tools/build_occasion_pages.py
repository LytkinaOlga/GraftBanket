#!/usr/bin/env python3
"""Build occasion pages with real boxes and the shared cart:
    /novogodniy-furshet/, /keytering-na-korporativ/, /keytering-na-den-rozhdeniya/

Boxes (photos, composition, weight, price, "add to cart") are copied from the home page,
like on /gotovye-furshetnye-boksy/, so run this after any change to the ready boxes:
    python3 tools/build_occasion_pages.py
Texts use only facts already stated on the site (terms, promos, payment) — don't invent schedules or services.
"""
import hashlib
import html
import json
import re
from datetime import date

from build_boxes_page import (BASE, SITE, asset_version, box_data, control_id, ensure_home_ids,
                              home_shell, reviews_html, text, to_seo_card)

PHONE = '<a href="tel:+375295704749">+375 29 570-47-49</a>'
GIFT = "При заказе от 200 BYN дарим шпинатный рулет (450 г)."
BIRTHDAY = "Именинникам — скидка 10% за 5 дней до и 5 дней после дня рождения."
NO_STACK = "Акции не суммируются: можно выбрать скидку или рулет в подарок."
FAQ_COMBINE = ("Можно совместить несколько боксов и заказать один бокс?",
               "Да. Корзина общая для всего сайта: добавьте несколько боксов с этой страницы или из <a href=\"/#constructor\">меню</a> — всё попадёт в одну заявку. Минимальной суммы заказа нет.")
FAQ_DELIVERY = ("Как получить заказ и сколько стоит доставка?",
                "Самовывоз — Минск, ул. Нововиленская, 51, бесплатно. Доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно; "
                "за МКАД стоимость рассчитает администратор. Подробнее — на странице <a href=\"/dostavka-i-oplata/\">«Доставка и оплата»</a>.")
FAQ_GUESTS = ("Сколько закусок нужно на компанию?",
              "Проще всего начать с готовых наборов: на странице <a href=\"/furshet-na-10-chelovek/\">«Фуршет на 10 человек»</a> у каждого набора указан вес на гостя. "
              "Для большой компании посмотрите варианты <a href=\"/furshet-na-20-chelovek/\">на 20</a> и <a href=\"/furshet-na-30-chelovek/\">на 30 человек</a> или напишите количество гостей в заявке — администратор подскажет.")
FAQ_TABLEWARE = ("Можно заказать приборы, салфетки и посуду?",
                 "Боксы можно поставить на стол как есть. Приборы, салфетки и посуду можем предоставить за дополнительную плату — количество и формат согласуются с администратором.")
TERM_DELIVERY = '<li><strong>Доставка по Минску:</strong> в пределах МКАД — 20 BYN, от 500 BYN — бесплатно. Самовывоз: ул. Нововиленская, 51.</li>'
TERM_MORE = '<li class="boxes-terms-more"><a href="/dostavka-i-oplata/">Доставка и оплата</a></li>'

PAGES = [
    {
        "path": "/novogodniy-furshet/", "crumb": "Новогодний фуршет в Минске",
        "title": "Новогодний фуршет в Минске — боксы и закуски с доставкой | Draft Catering",
        "description": "Новогодний фуршет в Минске: {n} готовых боксов от {min} BYN — канапе, брускетты, тарталетки, рулеты и десерты. Для офиса и дома, безналичный расчёт, доставка и самовывоз.",
        "overline": "НОВЫЙ ГОД · МИНСК", "h1": 'Новогодний <span>фуршет</span> в Минске',
        "intro": "Готовые боксы с закусками и десертами для корпоратива в офисе, встречи с друзьями или домашнего Нового года. Закуски приезжают красиво разложенными — их можно сразу ставить на стол. У каждого бокса указаны состав, количество, вес и цена; добавляйте боксы в корзину прямо здесь.",
        "guide_title": "Фуршет на компанию?", "guide_text": "Посмотрите готовые наборы с весом на гостя — так проще рассчитать угощение на корпоратив или праздник.",
        "guide_link": ("/furshet-na-10-chelovek/", "Наборы на 10 человек"),
        "terms": ['<li><strong>Предзаказ:</strong> обычно за 2–3 дня; даты перед Новым годом лучше бронировать заранее.</li>',
                  '<li><strong>Для компаний:</strong> безналичный расчёт, документы согласуются индивидуально.</li>',
                  '<li><strong>Подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г).</li>'],
        "boxes": ["box-sparkling", "box-salmon-crab", "box-canapes", "box-bruschetta-salmon-shrimp", "box-mini-tartlets",
                  "box-baked-tartlets", "box-napoleons", "box-assorted-rolls", "box-three-rolls", "box-crostini",
                  "box-profiteroles", "box-chocolate-cakes", "box-basque-cheesecake"],
        "list_name": "Боксы для новогоднего фуршета", "for": "к новогоднему столу", "faq_title": "Вопросы о новогоднем фуршете",
        "faq": [
            ("Когда заказывать новогодний фуршет?",
             "Обычно заказ оформляют за 2–3 дня, но даты перед Новым годом востребованы, поэтому лучше оставить заявку как можно раньше. "
             "Администратор подтвердит, что мы успеем приготовить всё к нужному дню и времени."),
            ("Можно заказать фуршет в офис на корпоратив?",
             "Да, принимаем корпоративные заказы и работаем по безналичному расчёту. Необходимые документы для компании согласуются индивидуально — "
             f"напишите об этом в комментарии к заявке или позвоните по номеру {PHONE}."),
            FAQ_GUESTS, FAQ_COMBINE,
            ("Есть ли подарок или скидка?", f"{GIFT} {BIRTHDAY} {NO_STACK}"),
            FAQ_DELIVERY,
        ],
        "howto": "Соберите заказ из боксов на этой странице, добавьте позиции из <a href=\"/#constructor\">меню</a> и отправьте заявку — корзина общая для всего сайта. Количество гостей и пожелания напишите в комментарии.",
        "links": [("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/keytering-na-korporativ/", "На корпоратив"), ("/keytering-dlya-ofisa/", "Для офиса"),
                  ("/furshet-na-10-chelovek/", "На 10 человек"), ("/furshet-na-20-chelovek/", "На 20 человек"), ("/furshet-na-30-chelovek/", "На 30 человек"),
                  ("/kanape-na-zakaz/", "Канапе"), ("/brusketty-na-zakaz/", "Брускетты"), ("/tartaletki-na-zakaz/", "Тарталетки"),
                  ("/keytering-na-den-rozhdeniya/", "На день рождения"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
    {
        "path": "/keytering-na-korporativ/", "crumb": "Кейтеринг на корпоратив в Минске",
        "title": "Кейтеринг на корпоратив в Минске — фуршетные боксы для офиса | Draft Catering",
        "description": "Кейтеринг на корпоратив в Минске: {n} готовых фуршетных боксов от {min} BYN с составом, весом и ценой. Безналичный расчёт для компаний, доставка в офис по Минску.",
        "overline": "ДЛЯ КОМАНДЫ · МИНСК", "h1": 'Кейтеринг <span>на корпоратив</span> в Минске',
        "intro": "Фуршетные боксы и порционные закуски для праздника команды, презентации, деловой встречи или корпоративного Нового года. Закуски приезжают красиво разложенными — их можно сразу поставить в офисе или переговорной. Цены и количество указаны заранее, поэтому бюджет легко посчитать до заявки.",
        "guide_title": "Сколько заказать на команду?", "guide_text": "Готовые наборы с весом на гостя помогут рассчитать фуршет на 10, 20 или 30 человек.",
        "guide_link": ("/furshet-na-10-chelovek/", "Наборы на 10 человек"),
        "terms": ['<li><strong>Для юридических лиц:</strong> безналичный расчёт, документы согласуются при подтверждении заказа.</li>',
                  '<li><strong>Предзаказ:</strong> желательно за 2–3 дня; срочный заказ — по согласованию.</li>',
                  '<li><strong>Посуда и приборы:</strong> за дополнительную плату, по согласованию.</li>'],
        "boxes": ["box-salmon-crab", "box-sparkling", "box-croissant-bruschetta-canape", "box-bruschetta-salmon-shrimp", "box-mini-tartlets",
                  "box-napoleons-big", "box-assorted-rolls", "box-croissants", "box-caesar", "box-chicken-pie",
                  "box-profiteroles", "box-chocolate-cakes"],
        "list_name": "Боксы для корпоративного фуршета", "for": "для корпоратива", "faq_title": "Вопросы о корпоративном фуршете",
        "faq": [
            ("Работаете ли вы с юридическими лицами и по безналичному расчёту?",
             f"Да. Принимаем заказы от компаний и организаций, оплата по безналичному расчёту. Реквизиты и необходимые документы согласуются с администратором при подтверждении заказа — напишите об этом в комментарии к заявке или позвоните по номеру {PHONE}."),
            ("Подходит ли меню для офисного корпоратива?",
             "Да. Порционные закуски и готовые боксы удобно подать в офисе, переговорной или на площадке мероприятия. Боксы можно поставить на стол как есть."),
            FAQ_GUESTS, FAQ_TABLEWARE,
            ("За сколько дней оформить заказ?",
             "Желательно за 2–3 дня; перед праздниками — раньше. Срочный заказ возможен по согласованию: администратор проверит, что мы успеем приготовить к нужному времени."),
            FAQ_COMBINE, FAQ_DELIVERY,
        ],
        "howto": "Добавьте боксы в корзину на этой странице или соберите меню из отдельных позиций в <a href=\"/#constructor\">каталоге</a>. В заявке укажите число участников, дату, время, адрес и что нужен безналичный расчёт.",
        "links": [("/novogodniy-furshet/", "Новогодний фуршет"), ("/keytering-dlya-ofisa/", "Для офиса"), ("/gotovye-furshetnye-boksy/", "Готовые боксы"),
                  ("/furshet-na-10-chelovek/", "На 10 человек"), ("/furshet-na-20-chelovek/", "На 20 человек"), ("/furshet-na-30-chelovek/", "На 30 человек"),
                  ("/furshet-na-zakaz/", "Фуршет на заказ"), ("/kanape-na-zakaz/", "Канапе"), ("/brusketty-na-zakaz/", "Брускетты"),
                  ("/tartaletki-na-zakaz/", "Тарталетки"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
    {
        "path": "/keytering-na-den-rozhdeniya/", "crumb": "Кейтеринг на день рождения в Минске",
        "title": "Кейтеринг на день рождения в Минске — праздничные боксы, скидка 10% | Draft Catering",
        "description": "Праздничный стол на день рождения в Минске: {n} готовых боксов от {min} BYN — закуски, салаты и десерты. Скидка имениннику 10%, доставка и самовывоз.",
        "overline": "ДЛЯ ПРАЗДНИКА · МИНСК", "h1": 'Кейтеринг <span>на день рождения</span> в Минске',
        "intro": "Готовые боксы с закусками и десертами, чтобы накрыть праздничный стол без долгой подготовки — дома или в офисе. Закуски приезжают красиво разложенными, их можно сразу ставить на стол. Имениннику — скидка 10%.",
        "guide_title": "Скидка 10% имениннику", "guide_text": "Действует за 5 дней до и 5 дней после дня рождения. Отметьте «У меня день рождения» при оформлении заявки — скидка посчитается автоматически.",
        "guide_link": ("/furshet-na-10-chelovek/", "Наборы на 10 человек"),
        "terms": ['<li><strong>Скидка 10%:</strong> за 5 дней до и 5 дней после дня рождения, в том числе на наборы.</li>',
                  '<li><strong>Или подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г). Акции не суммируются.</li>',
                  '<li><strong>Предзаказ:</strong> желательно за 2–3 дня; срочный заказ — по согласованию.</li>'],
        "boxes": ["box-bruschetta-profiterole-roll", "box-sparkling", "box-canapes", "box-bruschetta-salmon-shrimp", "box-baked-tartlets",
                  "box-napoleons", "box-ham-rolls", "box-three-rolls", "box-crostini", "box-greek",
                  "box-basque-cheesecake", "box-chocolate-cakes", "box-profiteroles-mini"],
        "list_name": "Боксы для дня рождения", "for": "для дня рождения", "faq_title": "Вопросы о заказе на день рождения",
        "faq": [
            ("Как получить скидку 10% имениннику?",
             "Скидка действует за 5 дней до и 5 дней после дня рождения. При оформлении заявки отметьте «У меня день рождения» — скидка посчитается автоматически. "),
            ("Можно выбрать подарок вместо скидки?",
             f"{GIFT} {NO_STACK} Подарок не распространяется на готовые наборы на 10 человек — они уже продаются со скидкой; скидка имениннику на них действует."),
            FAQ_GUESTS, FAQ_COMBINE,
            ("За сколько дней оформить заказ?",
             "Желательно за 2–3 дня. Срочный заказ возможен по согласованию — позвоните, и администратор проверит, что мы успеем приготовить к нужному времени."),
            FAQ_DELIVERY,
        ],
        "howto": "Добавьте боксы в корзину на этой странице или соберите набор из любимых закусок и десертов в <a href=\"/#constructor\">меню</a>. Не забудьте отметить «У меня день рождения», чтобы получить скидку.",
        "links": [("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/furshet-na-10-chelovek/", "На 10 человек"), ("/detskiy-keytering/", "Детский кейтеринг"),
                  ("/kanape-na-zakaz/", "Канапе"), ("/brusketty-na-zakaz/", "Брускетты"), ("/tartaletki-na-zakaz/", "Тарталетки"),
                  ("/novogodniy-furshet/", "Новогодний фуршет"), ("/keytering-dlya-ofisa/", "Для офиса"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
]


def build_page(cfg, articles, shell, total):
    missing = [i for i in cfg["boxes"] if i not in articles]
    assert not missing, f'{cfg["path"]}: boxes not on the home page: {missing}'
    chosen = [articles[i] for i in cfg["boxes"]]
    boxes = [box_data(a) for a in chosen]
    cards = ''.join(to_seo_card(a, False) for a in chosen)
    # Home page numbering («Бокс №10») jumps in a selection — drop it here.
    cards = re.sub(r'Бокс №\d+ · ', '', cards)
    min_price = min(b["price"] for b in boxes)
    url = BASE + cfg["path"]
    title = cfg["title"]
    description = cfg["description"].format(n=len(boxes), min=min_price)
    og_image = boxes[0]["images"][0]
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": cfg["crumb"], "item": url}]},
        {"@type": "CollectionPage", "@id": url + "#page", "url": url, "name": cfg["crumb"],
         "description": description, "inLanguage": "ru-BY",
         "isPartOf": {"@type": "WebSite", "name": "Draft Catering", "url": BASE + "/"},
         "mainEntity": {"@id": url + "#boxes"}},
        {"@type": "ItemList", "@id": url + "#boxes", "name": cfg["list_name"], "numberOfItems": len(boxes),
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "item": {
                 "@type": "Product", "@id": BASE + "/gotovye-furshetnye-boksy/#" + b["id"], "name": b["name"],
                 "description": b["description"], "image": b["images"], "brand": {"@type": "Brand", "name": "Draft Catering"},
                 "offers": {"@type": "Offer", "price": f'{b["price"]:.2f}', "priceCurrency": "BYN",
                            "availability": "https://schema.org/InStock", "url": url + "#" + b["id"],
                            "areaServed": {"@type": "City", "name": "Минск"}, "seller": {"@id": BASE + "/#business"}}}}
             for i, b in enumerate(boxes)]},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in cfg["faq"]]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':'))
    css_version = hashlib.md5((SITE / 'css' / 'boxes-page.css').read_bytes()).hexdigest()[:8]
    metrika, header, bottom, scripts, styles_css = shell
    header = header.replace('href="/#faq"', 'href="#faq"').replace('href="/#reviews"', 'href="#reviews"')
    e = html.escape
    faq_html = (f'<section class="section faq-page" id="faq"><div class="wrap"><h2>{e(cfg["faq_title"])}</h2><div class="faq-page-list">'
                + ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in cfg["faq"]) + '</div></div></section>')
    terms = ''.join(cfg["terms"]) + TERM_DELIVERY + TERM_MORE
    links = ''.join(f'<a href="{href}">{e(label)}</a>' for href, label in cfg["links"])
    guide_href, guide_label = cfg["guide_link"]

    page = f'''<!doctype html><html lang="ru-BY"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{metrika}<title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#f3ca52"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ru-BY" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><meta property="og:locale" content="ru_BY"><meta property="og:type" content="website"><meta property="og:site_name" content="Draft Catering"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="stylesheet" href="{styles_css}"><link rel="stylesheet" href="/css/seo-pages.css?v=20261104b"><link rel="stylesheet" href="/css/boxes-page.css?v={css_version}"><link rel="stylesheet" href="/css/reviews.css?v={asset_version('css/reviews.css')}"><link rel="stylesheet" href="/css/occasion-pages.css?v={asset_version('css/occasion-pages.css')}">
<script type="application/ld+json">{ld}</script></head><body>
{header}
<main><nav class="wrap crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a> → {e(cfg["crumb"])}</nav>
<section class="boxes-hero"><div class="wrap boxes-hero-layout"><div class="boxes-hero-copy"><div class="boxes-hero-overline"><span>{e(cfg["overline"])}</span></div><h1>{cfg["h1"]}</h1><p>{e(cfg["intro"])}</p><p class="occasion-note">Ниже — подборка из <strong>{len(boxes)} боксов {e(cfg["for"])}</strong>. Всего у нас {total} готовых боксов, а в меню ещё отдельные закуски, салаты, пироги и десерты.</p><div class="boxes-hero-actions"><a class="primary-link" href="#boxes"><strong>Смотреть подборку</strong><span aria-hidden="true">↓</span></a><a class="secondary-link" href="/gotovye-furshetnye-boksy/"><strong>Все {total} готовых боксов</strong><span aria-hidden="true">→</span></a></div></div></div></section>
<section class="boxes-guide" aria-labelledby="guide-title"><div class="wrap boxes-guide-layout"><div class="boxes-guide-offer"><h2 id="guide-title">{e(cfg["guide_title"])}</h2><p>{e(cfg["guide_text"])}</p><a class="secondary-link" href="{guide_href}"><strong>{e(guide_label)}</strong><span aria-hidden="true">→</span></a></div><ul class="boxes-terms" aria-label="Условия заказа">{terms}</ul></div></section>
<section class="boxes-list" id="boxes" aria-label="{e(cfg["list_name"])}"><div class="wrap"><div class="ready-grid">
{cards}</div><aside class="occasion-more" aria-labelledby="more-title"><div><h2 id="more-title">Это не всё меню</h2><p>Здесь {len(boxes)} боксов {e(cfg["for"])}. Ещё {total - len(boxes)} готовых боксов — на отдельной странице, а в меню можно собрать заказ из отдельных закусок, салатов, пирогов и десертов. Корзина общая: всё попадёт в одну заявку.</p></div><div class="occasion-more-actions"><a class="primary-link" href="/gotovye-furshetnye-boksy/"><strong>Все {total} готовых боксов</strong><span aria-hidden="true">→</span></a><a class="secondary-link" href="/#constructor"><strong>Всё меню</strong><span aria-hidden="true">→</span></a></div></aside></div></section>
{reviews_html('wrap')}
{faq_html}
<section class="section"><div class="wrap text-grid"><h2>Как оформить заказ</h2><p>{cfg["howto"]}</p><p>Это заявка, а не автоматическое подтверждение: администратор свяжется с вами, подтвердит состав, дату, время и итоговую стоимость. Вопросы — по номеру {PHONE}.</p></div></section>
<section class="section facts"><div class="wrap"><h2>Другие категории и услуги</h2><div class="links">{links}</div></div></section></main>
{bottom}{scripts}</body></html>
'''
    out = SITE / cfg["path"].strip('/') / "index.html"
    out.write_text(page, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    sm = re.sub(r'(<loc>' + re.escape(url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + f'{date.today():%Y-%m-%d}', sm)
    sitemap.write_text(sm, encoding="utf-8")
    print(f"{out.relative_to(SITE.parent)}: {len(boxes)} boxes, from {min_price} BYN")


def build():
    articles = {control_id(a): a for a in ensure_home_ids()}
    shell = home_shell()
    for cfg in PAGES:
        build_page(cfg, articles, shell, len(articles))


if __name__ == "__main__":
    build()
