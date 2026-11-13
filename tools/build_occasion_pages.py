#!/usr/bin/env python3
"""Build occasion pages with real boxes and the shared cart:
    /novogodniy-furshet/, /keytering-na-korporativ/, /keytering-na-den-rozhdeniya/, /furshet-v-ofis-na-den-rozhdeniya/,
    /dostavka-zakusok/ (закуски на заказ), /furshet-na-zakaz/, /tartaletki-na-zakaz/

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
        "links": [("/goryachee-na-prazdnichnyy-stol/", "Горячее на праздничный стол"), ("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/keytering-na-korporativ/", "На корпоратив"), ("/keytering-dlya-ofisa/", "Для офиса"),
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
        "links": [("/goryachee-na-prazdnichnyy-stol/", "Горячее на праздничный стол"), ("/novogodniy-furshet/", "Новогодний фуршет"), ("/keytering-dlya-ofisa/", "Для офиса"), ("/gotovye-furshetnye-boksy/", "Готовые боксы"),
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
        "links": [("/goryachee-na-prazdnichnyy-stol/", "Горячее на праздничный стол"), ("/furshet-v-ofis-na-den-rozhdeniya/", "В офис на день рождения"), ("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/furshet-na-10-chelovek/", "На 10 человек"), ("/detskiy-keytering/", "Детский кейтеринг"),
                  ("/kanape-na-zakaz/", "Канапе"), ("/brusketty-na-zakaz/", "Брускетты"), ("/tartaletki-na-zakaz/", "Тарталетки"),
                  ("/novogodniy-furshet/", "Новогодний фуршет"), ("/keytering-dlya-ofisa/", "Для офиса"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
    {
        # Built from real office orders (16.11: офис 907, БЦ на Скорины, офис 609, Победителей) and reviews mentioning colleagues.
        "path": "/furshet-v-ofis-na-den-rozhdeniya/", "crumb": "Фуршет в офис на день рождения",
        "title": "Фуршет в офис на день рождения в Минске — угощение для коллег с доставкой | Draft Catering",
        "description": "Чем угостить коллег на день рождения: {n} готовых боксов с закусками и десертами от {min} BYN с доставкой в офис по Минску. Скидка имениннику 10%, безналичный расчёт для компаний.",
        "overline": "ДЕНЬ РОЖДЕНИЯ НА РАБОТЕ · МИНСК", "h1": 'Фуршет <span>в офис</span> на день рождения',
        "intro": "Чем угостить коллег на день рождения? Готовые боксы с закусками и десертами привозим в офис по Минску — их можно сразу поставить на стол в переговорной или на кухне, без тарелок и долгой подготовки. Подборку мы собрали по заказам, которые нам уже делали в офисы. Имениннику — скидка 10%.",
        "guide_title": "Сколько заказать на коллег?", "guide_text": "У готовых наборов на 10 человек указан вес на гостя — по ним удобно прикинуть угощение на отдел. Или напишите число коллег в комментарии к заявке — администратор подскажет.",
        "guide_link": ("/furshet-na-10-chelovek/", "Наборы на 10 человек"),
        "terms": ['<li><strong>Скидка 10% имениннику:</strong> за 5 дней до и 5 дней после дня рождения — отметьте «У меня день рождения» в заявке.</li>',
                  '<li><strong>Или подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г). Акции не суммируются.</li>',
                  '<li><strong>Оплата:</strong> наличными или картой; для компаний — безналичный расчёт.</li>',
                  '<li><strong>Время доставки</strong> указываете в заявке — администратор подтвердит.</li>'],
        "boxes": ["box-mini-tartlets", "box-profiteroles", "box-napoleons", "box-bruschetta-profiterole-roll", "box-bruschetta-salmon-shrimp",
                  "box-ham-rolls", "box-baked-tartlets", "box-crostini", "box-canapes"],
        "list_name": "Боксы для дня рождения в офисе", "for": "для дня рождения в офисе", "faq_title": "Вопросы о фуршете в офис на день рождения",
        "faq": [
            ("Чем угостить коллег на день рождения в офисе?",
             "Удобнее всего — порционные закуски, которые не нужно резать и раскладывать: мини-тарталетки, брускетты, солёные «Наполеоны», рулетики, канапе и профитроли. "
             "Чаще всего в офисы у нас заказывают мини-тарталетки, профитроли, «Наполеоны» и брускетты — они собраны на этой странице."),
            FAQ_GUESTS,
            ("Привезёте в офис к нужному времени?",
             "Да. Укажите в заявке дату, время и адрес офиса (этаж, кабинет) — администратор свяжется с вами и подтвердит доставку. "
             "Доставка по Минску в пределах МКАД — 20 BYN, при заказе от 500 BYN — бесплатно."),
            ("Действует ли скидка имениннику, если заказ в офис?",
             f"Да. Скидка 10% действует за 5 дней до и 5 дней после дня рождения — отметьте «У меня день рождения» при оформлении заявки. {NO_STACK}"),
            FAQ_TABLEWARE,
            ("Можно оплатить от компании?",
             f"Да. Можно оплатить наличными или картой, а для компаний — по безналичному расчёту. Документы согласуются с администратором — напишите об этом в комментарии к заявке или позвоните по номеру {PHONE}."),
            FAQ_COMBINE,
        ],
        "howto": "Добавьте боксы в корзину на этой странице или соберите набор из отдельных закусок в <a href=\"/#constructor\">меню</a>. В заявке укажите адрес офиса с этажом и кабинетом, время доставки, число коллег — и отметьте «У меня день рождения», чтобы получить скидку.",
        "links": [("/keytering-na-den-rozhdeniya/", "На день рождения"), ("/keytering-dlya-ofisa/", "Для офиса"), ("/keytering-na-korporativ/", "На корпоратив"),
                  ("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/furshet-na-10-chelovek/", "На 10 человек"), ("/kanape-na-zakaz/", "Канапе"),
                  ("/tartaletki-na-zakaz/", "Тарталетки"), ("/brusketty-na-zakaz/", "Брускетты"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
    {
        # Wordstat 13.11: «заказать закуски» 69, «закуски заказать минск» 22, «фуршетные закуски заказать» 17; URL kept (was «Доставка закусок»).
        "path": "/dostavka-zakusok/", "crumb": "Закуски на заказ в Минске",
        "title": "Закуски на заказ в Минске — доставка закусок, сеты и боксы | Draft Catering",
        "description": "Закуски на заказ в Минске: {n} готовых сетов и боксов закусок от {min} BYN — канапе, брускетты, тарталетки, рулетики, «Наполеоны». Доставка по Минску, в офис и домой, самовывоз.",
        "overline": "ЗАКУСКИ С ДОСТАВКОЙ · МИНСК", "h1": 'Закуски <span>на заказ</span> в Минске',
        "intro": "Готовые сеты закусок для праздника, офиса или встречи: канапе, брускетты, тарталетки, рулетики и солёные «Наполеоны» приезжают в боксах — их можно сразу ставить на стол. У каждого бокса указаны состав, количество, вес и цена; доставляем по Минску или отдаём самовывозом.",
        "guide_title": "Закуски на компанию?", "guide_text": "Готовые наборы на 10 человек с весом на гостя помогут рассчитать закуски для праздника или офиса.",
        "guide_link": ("/furshet-na-10-chelovek/", "Наборы на 10 человек"),
        "terms": ['<li><strong>Предзаказ:</strong> желательно за 2–3 дня; дата и удобный интервал доставки подтверждаются администратором.</li>',
                  '<li><strong>Подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г).</li>',
                  '<li><strong>За МКАД:</strong> возможность и стоимость доставки согласуются индивидуально.</li>'],
        "boxes": ["box-croissant-bruschetta-canape", "box-salmon-crab", "box-bruschetta-salmon-shrimp", "box-canapes", "box-mini-tartlets",
                  "box-baked-tartlets", "box-napoleons", "box-assorted-rolls", "box-ham-rolls", "box-eggplant-rolls", "box-crostini", "box-three-rolls"],
        "list_name": "Сеты и боксы закусок", "for": "с закусками", "faq_title": "Вопросы о заказе закусок",
        "faq": [
            ("Что такое сет закусок?",
             "Это готовый бокс с несколькими видами закусок, разложенных для подачи. У нас в каждом сете указаны состав, количество штук, вес и цена — выберите сет на этой странице или соберите свой из отдельных позиций в <a href=\"/#constructor\">меню</a>."),
            ("Сколько стоит доставка закусок по Минску?",
             "Доставка в пределах МКАД стоит 20 BYN, а при заказе от 500 BYN — бесплатно. Возможность и стоимость доставки за МКАД согласуются индивидуально."),
            ("Можно заказать закуски в офис?",
             f"Да. Укажите в заявке адрес офиса, этаж и время доставки. Для компаний доступен безналичный расчёт — напишите об этом в комментарии или позвоните по номеру {PHONE}. "
             "Посмотрите также подборку <a href=\"/furshet-v-ofis-na-den-rozhdeniya/\">«Фуршет в офис на день рождения»</a>."),
            ("Есть ли самовывоз?", "Да. Бесплатный самовывоз — Минск, ул. Нововиленская, 51."),
            FAQ_GUESTS, FAQ_COMBINE,
            ("Есть ли подарок или скидка?", f"{GIFT} {BIRTHDAY} {NO_STACK}"),
        ],
        "howto": "Добавьте сеты закусок в корзину на этой странице или соберите набор из отдельных позиций в <a href=\"/#constructor\">меню</a>, затем укажите дату, время и адрес доставки.",
        "links": [("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/furshet-na-zakaz/", "Фуршет на заказ"), ("/kanape-na-zakaz/", "Канапе"),
                  ("/brusketty-na-zakaz/", "Брускетты"), ("/tartaletki-na-zakaz/", "Тарталетки"), ("/furshet-na-10-chelovek/", "На 10 человек"),
                  ("/furshet-v-ofis-na-den-rozhdeniya/", "В офис на день рождения"), ("/keytering-na-den-rozhdeniya/", "На день рождения"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
    {
        # Wordstat 13.11: «заказать фуршет» 65, «фуршет с доставкой» 56, «фуршет на заказ» 30, «мини фуршет» 29, «заказать фуршет с доставкой минск» 17.
        "path": "/furshet-na-zakaz/", "crumb": "Фуршет на заказ в Минске",
        "title": "Фуршет на заказ в Минске — заказать с доставкой, меню и цены | Draft Catering",
        "description": "Фуршет на заказ в Минске: {n} готовых фуршетных боксов от {min} BYN и наборы на 10, 20 и 30 человек. Заказать фуршет с доставкой домой или в офис, самовывоз.",
        "overline": "ФУРШЕТ С ДОСТАВКОЙ · МИНСК", "h1": 'Фуршет <span>на заказ</span> в Минске',
        "intro": "Готовые закуски для дня рождения, офиса, домашнего праздника или деловой встречи — от мини-фуршета на несколько человек до стола на большую компанию. Боксы приезжают красиво разложенными, их можно сразу ставить на стол. В каждом указаны состав, вес, количество и цена, поэтому меню и бюджет видно заранее.",
        "guide_title": "Фуршет на 10, 20 или 30 человек?", "guide_text": "Посмотрите готовые наборы с весом на гостя — или соберите фуршет из боксов ниже.",
        "guide_link": ("/furshet-na-10-chelovek/", "Наборы на 10 человек"),
        "terms": ['<li><strong>Заказ за 2–3 дня:</strong> рекомендуемый срок; срочные заказы обсуждаются отдельно.</li>',
                  '<li><strong>Для компаний:</strong> безналичный расчёт, документы согласуются индивидуально.</li>',
                  '<li><strong>Подарок:</strong> при заказе от 200 BYN — шпинатный рулет (450 г).</li>'],
        "boxes": ["box-salmon-crab", "box-sparkling", "box-croissant-bruschetta-canape", "box-bruschetta-profiterole-roll", "box-mini-tartlets",
                  "box-canapes", "box-napoleons-big", "box-three-rolls", "box-assorted-rolls", "box-caesar", "box-chicken-pie",
                  "box-chocolate-cakes", "box-basque-cheesecake"],
        "list_name": "Боксы для фуршета", "for": "для фуршета", "faq_title": "Вопросы о заказе фуршета",
        "faq": [
            ("Что входит в меню для фуршета?",
             "В меню есть готовые боксы, брускетты, канапе, тарталетки, рулетики, салаты, пироги и десерты. Можно сочетать готовые наборы и отдельные позиции из разных категорий."),
            ("За сколько дней нужно заказать фуршет?",
             "Рекомендуем оформить заявку за 2–3 дня. Возможность срочного заказа уточняет администратор."),
            ("Можно заказать фуршет домой или в офис?",
             f"Да. Доставляем по Минску: в пределах МКАД — 20 BYN, от 500 BYN — бесплатно; за МКАД — по согласованию. Для офиса доступен безналичный расчёт. Самовывоз — Нововиленская, 51. Вопросы — {PHONE}."),
            FAQ_GUESTS,
            ("Можно ли собрать собственный набор?",
             "Да. На сайте можно выбрать отдельные позиции в <a href=\"/#constructor\">меню</a> и отправить заявку — администратор согласует состав."),
            FAQ_TABLEWARE,
            ("Есть ли подарок или скидка?", f"{GIFT} {BIRTHDAY} {NO_STACK}"),
        ],
        "howto": "Добавьте боксы в корзину на этой странице, посмотрите <a href=\"/furshet-na-10-chelovek/\">наборы на 10 человек</a> или соберите меню из отдельных позиций в <a href=\"/#constructor\">каталоге</a>. Число гостей и пожелания напишите в комментарии к заявке.",
        "links": [("/goryachee-na-prazdnichnyy-stol/", "Горячее на праздничный стол"), ("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/furshet-na-10-chelovek/", "На 10 человек"), ("/furshet-na-20-chelovek/", "На 20 человек"),
                  ("/furshet-na-30-chelovek/", "На 30 человек"), ("/dostavka-zakusok/", "Закуски на заказ"), ("/kanape-na-zakaz/", "Канапе"),
                  ("/tartaletki-na-zakaz/", "Тарталетки"), ("/keytering-na-korporativ/", "На корпоратив"), ("/keytering-na-den-rozhdeniya/", "На день рождения"),
                  ("/novogodniy-furshet/", "Новогодний фуршет"), ("/dostavka-i-oplata/", "Доставка и оплата")],
    },
    {
        # Wordstat 13.11: «заказать тарталетки» 32, «тарталетки заказать минск» 13, «фуршетные тарталетки на праздничный стол заказать» 11.
        "path": "/tartaletki-na-zakaz/", "crumb": "Тарталетки на заказ в Минске",
        "title": "Тарталетки на заказ в Минске — заказать для фуршета и праздника | Draft Catering",
        "description": "Заказать тарталетки в Минске: мини-тарталетки, запечённые тарталетки с курицей, лососем, грибами и снежным крабом — готовые боксы от {min} BYN. Для фуршета, офиса и праздничного стола.",
        "overline": "ПОРЦИОННЫЕ ЗАКУСКИ · МИНСК", "h1": 'Тарталетки <span>на заказ</span> в Минске',
        "intro": "Тарталетки легко сервировать и удобно есть без приборов — они подходят для фуршета, кофе-брейка, дня рождения и офисного мероприятия. Ниже — боксы с тарталетками и закуски, которые к ним обычно добавляют. Тарталетки можно заказать и поштучно в меню.",
        "guide_title": "Нужны отдельные вкусы?", "guide_text": "Запечённые тарталетки продаются и поштучно: 60 г, заказ одного вкуса кратно 4 штукам. Начинки — курица и грибы, лосось и брокколи, белые грибы, снежный краб с соусом терияки.",
        "guide_link": ("/#constructor", "Тарталетки в меню"),
        "terms": ['<li><strong>Поштучно:</strong> 60 г, заказ кратно 4 шт. одного вкуса.</li>',
                  '<li><strong>Готовый бокс:</strong> 16 запечённых тарталеток четырёх видов.</li>',
                  '<li><strong>Предзаказ:</strong> желательно за 2–3 дня.</li>'],
        "boxes": ["box-mini-tartlets", "box-baked-tartlets", "box-salmon-crab", "box-canapes", "box-bruschetta-salmon-shrimp", "box-profiteroles"],
        "list_name": "Боксы с тарталетками", "for": "с тарталетками и закусками к ним", "faq_title": "Вопросы о заказе тарталеток",
        "faq": [
            ("Какие тарталетки можно заказать?",
             "Мини-тарталетки в большом боксе, запечённые тарталетки с курицей и грибами, лососем и брокколи, белыми грибами, снежным крабом и соусом терияки, а также тарталетки в боксе «Фуршетный». Состав и вес каждого бокса указаны на карточке."),
            ("Можно заказать тарталетки поштучно?",
             "Да, запечённые тарталетки есть в <a href=\"/#constructor\">меню</a>: 60 г, заказ одного вкуса кратно 4 штукам. Можно заказать несколько вкусов или готовый бокс."),
            ("Можно заказать канапе и тарталетки вместе?",
             "Да. Корзина общая для всего сайта: добавьте боксы с тарталетками и <a href=\"/kanape-na-zakaz/\">канапе</a> — всё попадёт в одну заявку."),
            FAQ_DELIVERY,
            ("За сколько дней оформить заказ?",
             "Желательно за 2–3 дня. Актуальная цена и доступность подтверждаются администратором после оформления заявки."),
        ],
        "howto": "Добавьте боксы с тарталетками в корзину или выберите отдельные вкусы в <a href=\"/#constructor\">меню</a>, затем отправьте заявку.",
        "links": [("/kanape-na-zakaz/", "Канапе"), ("/brusketty-na-zakaz/", "Брускетты"), ("/dostavka-zakusok/", "Закуски на заказ"),
                  ("/gotovye-furshetnye-boksy/", "Готовые боксы"), ("/furshet-na-zakaz/", "Фуршет на заказ"), ("/keytering-dlya-ofisa/", "Для офиса и корпоратива"),
                  ("/keytering-na-den-rozhdeniya/", "На день рождения"), ("/dostavka-i-oplata/", "Доставка и оплата")],
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
