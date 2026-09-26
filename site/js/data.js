// Данные о блюдах — ЗАГЛУШКИ. Заменить на реальные фото/цены/описания перед запуском.
// Фото — временные (SVG-плейсхолдеры с эмодзи по теме блюда), заменить на реальные при наполнении контентом.

const CATEGORIES = [
  { id: "bruschette", title: "Брускетты" },
  { id: "profiteroles", title: "Профитроли" },
  { id: "rolls", title: "Рулетики из ветчины" },
  { id: "croissants", title: "Мини-круассаны" },
  { id: "crostini", title: "Кростини" },
  { id: "tartlets", title: "Тарталетки" },
  { id: "napoleons", title: "Солёные наполеоны" },
  { id: "sandwiches", title: "Мини сэндвичи" },
  { id: "salads", title: "Салаты" },
  { id: "burgers", title: "Мини бургеры" },
  { id: "quiches", title: "Киши" },
  { id: "cheesecakes", title: "Чизкейки" },
  { id: "biscuit-rolls", title: "Закусочные рулеты" },
  { id: "pies", title: "Пироги" },
  { id: "desserts", title: "Десерты" },
  { id: "sets", title: "Сеты" },
];

function placeholderImg(emoji, bg) {
  var svg =
    "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300'>" +
    "<rect width='100%' height='100%' fill='" + bg + "'/>" +
    "<text x='50%' y='53%' font-size='118' text-anchor='middle' dominant-baseline='middle'>" + emoji + "</text>" +
    "</svg>";
  return "data:image/svg+xml," + encodeURIComponent(svg);
}

const ITEMS = [
  // Брускетты
  { id: "b1", category: "bruschette", name: "Брускетта с лососем и крем-сыром", weight: "60 г", price: 5.50, composition: "Хрустящая чиабатта, слабосолёный лосось, крем-сыр", description: "Нежный лосось и сливочный крем-сыр на хрустящей чиабатте.", img: "assets/bruschette/salmon-cream-cheese.jpg" },
  { id: "b2", category: "bruschette", name: "Брускетта с креветкой и муссом из авокадо", weight: "60 г", price: 5.00, composition: "Хрустящая чиабатта, креветка, мусс из авокадо", description: "Свежая закуска с нежным муссом из авокадо и креветкой.", img: "assets/bruschette/shrimp-avocado-green.jpg" },
  { id: "b3", category: "bruschette", name: "Брускетта с ростбифом, вялеными томатами и медово-горчичным соусом", weight: "60 г", price: 4.00, composition: "Хрустящая чиабатта, ростбиф, вяленые томаты, медово-горчичный соус", description: "Сытное сочетание ростбифа, вяленых томатов и пикантного соуса.", img: "assets/bruschette/roast-beef-tomatoes.jpg?v=2" },
  { id: "b4", category: "bruschette", name: "Брускетта с риетом из утки, вишнёвым конфитюром и лепестками миндаля", weight: "60 г", price: 4.00, composition: "Хрустящая чиабатта, риет из утки, вишнёвый конфитюр, лепестки миндаля", description: "Насыщенный утиный риет с вишнёвой нотой и лепестками миндаля.", img: "assets/bruschette/duck-rillette-cherry.jpg?v=2" },
  { id: "b5", category: "bruschette", name: "Брускетта с жареным куриным бедром, сельдереем, виноградом и беконом", weight: "60 г", price: 4.00, composition: "Хрустящая чиабатта, жареное куриное бедро, сельдерей, виноград, бекон", description: "Сочная курица с виноградом, сельдереем и хрустящим беконом.", img: "assets/bruschette/chicken-grape-bacon.jpg?v=2" },
  { id: "b6", category: "bruschette", name: "Брускетта с тартаром из говядины", weight: "60 г", price: 4.20, composition: "Хрустящая чиабатта, тартар из говядины", description: "Выразительная мясная закуска в аккуратной порционной подаче.", img: "assets/bruschette/beef-tartare.jpg" },
  { id: "b7", category: "bruschette", name: "Брускетта с тартаром из сыровяленой колбасы", weight: "60 г", price: 4.20, composition: "Хрустящая чиабатта, тартар из сыровяленой колбасы", description: "Пикантный тартар из сыровяленой колбасы на хрустящей чиабатте.", img: "assets/bruschette/salami-tartare.jpg" },

  // Профитроли
  { id: "p1", category: "profiteroles", name: "Профитроли с курицей и сыром", weight: "25 г", price: 2.60, composition: "Заварное тесто, куриное филе, сыр, соус", description: "Мини-профитроли с сытной начинкой.", img: placeholderImg("🍗", "#F3E8FF") },
  { id: "p2", category: "profiteroles", name: "Профитроли с лососем", weight: "25 г", price: 3.20, composition: "Заварное тесто, лосось, крем-сыр", description: "Изысканная закуска для фуршета.", img: placeholderImg("🐟", "#F3E8FF") },
  { id: "p3", category: "profiteroles", name: "Профитроли с ветчиной и грибами", weight: "25 г", price: 2.80, composition: "Заварное тесто, ветчина, грибы, сливочный соус", description: "Насыщенная начинка в нежном тесте.", img: placeholderImg("🍄", "#F3E8FF") },
  { id: "p4", category: "profiteroles", name: "Профитроли сладкие (крем)", weight: "25 г", price: 2.40, composition: "Заварное тесто, заварной крем, сахарная пудра", description: "Десертный вариант для сладкого стола.", img: placeholderImg("🍮", "#F3E8FF") },

  // Рулетики из ветчины
  { id: "r1", category: "rolls", name: "Рулетик из ветчины с крем-сыром и вялеными томатами", weight: "50 г", price: 75 / 21, bundlePrice: 75, img: "assets/boxes/ham-rolls-appetizing-mobile.jpg" },
  { id: "r2", category: "rolls", name: "Рулетик из ветчины с чесноком и грецким орехом", weight: "50 г", price: 75 / 21, bundlePrice: 75, img: "assets/boxes/ham-rolls-appetizing-mobile.jpg" },
  { id: "r3", category: "rolls", name: "Рулетик из ветчины с фетой и зеленью", weight: "50 г", price: 75 / 21, bundlePrice: 75, img: "assets/boxes/ham-rolls-appetizing-mobile.jpg" },

  // Мини-круассаны
  { id: "cr1", category: "croissants", name: "Мини-круассан с ростбифом, маринованным огурцом и вялеными томатами", weight: "90 г", price: 8.00, img: "assets/croissants/croissant-roast-beef.jpg" },
  { id: "cr2", category: "croissants", name: "Мини-круассан с крем-сыром и слабосолёной форелью", weight: "90 г", price: 8.00, img: "assets/croissants/croissant-trout.jpg" },
  { id: "cr3", category: "croissants", name: "Мини-круассан «Цезарь» с куриным филе и томатом", weight: "90 г", price: 8.00, img: "assets/croissants/croissant-caesar.jpg" },

  // Кростини
  { id: "kr1", category: "crostini", name: "Кростини с грудинкой и корнишонами", weight: "55 г", price: 3.25, img: "assets/boxes/crostini-detail-mobile.jpg" },
  { id: "kr2", category: "crostini", name: "Кростини с сельдью и сладким перцем", weight: "55 г", price: 3.25, img: "assets/boxes/crostini-overview-mobile.jpg" },

  // Тарталетки
  { id: "t1", category: "tartlets", name: "Запечённая тарталетка с курицей и грибами", weight: "60 г", price: 4.00, img: "assets/tartlets/tartlet-chicken-mushrooms.jpg" },
  { id: "t2", category: "tartlets", name: "Запечённая тарталетка с лососем и брокколи", weight: "60 г", price: 5.50, img: "assets/tartlets/tartlet-salmon-broccoli.jpg" },
  { id: "t3", category: "tartlets", name: "Запечённая тарталетка с белыми грибами", weight: "60 г", price: 4.00, img: "assets/tartlets/tartlet-porcini.jpg" },
  { id: "t4", category: "tartlets", name: "Запечённая тарталетка со снежным крабом и соусом терияки", weight: "60 г", price: 4.00, img: "assets/tartlets/tartlet-snow-crab-teriyaki.jpg" },

  // Солёные наполеоны
  { id: "napoleon-duck", category: "napoleons", name: "Наполеон с утиным паштетом и клюквенным конфитюром", weight: "1 шт. ≈ 40 г", price: 55 / 18, img: "assets/napoleons/duck-cranberry-box.png?v=20260926-natural" },
  { id: "napoleon-chicken", category: "napoleons", name: "Наполеон с курицей и грибами", weight: "1 шт. ≈ 40 г", price: 55 / 18, img: "assets/napoleons/chicken-mushroom-box.png?v=20260926-natural" },
  { id: "napoleon-tuna", category: "napoleons", name: "Наполеон с тунцом и сыром", weight: "1 шт. ≈ 40 г", price: 55 / 18, img: "assets/napoleons/tuna-cheese-box.png?v=20260926-natural" },

  // Мини сэндвичи
  { id: "s1", category: "sandwiches", name: "Мини сэндвич с ростбифом", weight: "45 г", price: 3.80, composition: "Хлеб, ростбиф, руккола, соус", description: "Сытный и аккуратный мини-формат.", img: placeholderImg("🥩", "#E3F2FD") },
  { id: "s2", category: "sandwiches", name: "Мини сэндвич с индейкой и авокадо", weight: "45 г", price: 3.60, composition: "Хлеб, индейка, авокадо, листовой салат", description: "Лёгкий вариант с нежной начинкой.", img: placeholderImg("🥑", "#E3F2FD") },
  { id: "s3", category: "sandwiches", name: "Мини сэндвич с лососем", weight: "45 г", price: 4.40, composition: "Хлеб, лосось, крем-сыр, огурец", description: "Праздничный вариант мини-сэндвича.", img: placeholderImg("🐟", "#E3F2FD") },
  { id: "s4", category: "sandwiches", name: "Мини сэндвич вегетарианский", weight: "45 г", price: 3.20, composition: "Хлеб, овощи, хумус, зелень", description: "Свежий вегетарианский выбор.", img: placeholderImg("🥬", "#E3F2FD") },

  // Салаты
  { id: "sl1", category: "salads", name: "«Цезарь» с курицей", weight: "130 г", price: 9.00, img: "assets/boxes/caesar-portion-mobile.jpg" },
  { id: "sl2", category: "salads", name: "«Цезарь» с креветками", weight: "130 г", price: 11.00, note: "В каждой порции — 2 креветки", img: "assets/boxes/caesar-shrimp-detail-mobile.jpg" },
  { id: "sl3", category: "salads", name: "Греческий салат", weight: "130 г", price: 8.00, img: "assets/salads/greek-salad-portion-box.jpg" },

  // Мини бургеры
  { id: "bg1", category: "burgers", name: "Мини бургер classic", weight: "70 г", price: 5.20, composition: "Булочка бриошь, говяжья котлета, сыр, соус", description: "Мини-версия классического бургера.", img: placeholderImg("🍔", "#FDEBEB") },
  { id: "bg2", category: "burgers", name: "Мини бургер с курицей", weight: "70 г", price: 4.60, composition: "Булочка бриошь, куриная котлета, соус, салат", description: "Нежная курица в хрустящей панировке.", img: placeholderImg("🍗", "#FDEBEB") },
  { id: "bg3", category: "burgers", name: "Мини бургер вегетарианский", weight: "70 г", price: 4.30, composition: "Булочка бриошь, овощная котлета, соус, салат", description: "Сытный вегетарианский вариант.", img: placeholderImg("🥦", "#FDEBEB") },
  { id: "bg4", category: "burgers", name: "Мини бургер с лососем", weight: "70 г", price: 5.80, composition: "Булочка бриошь, котлета из лосося, соус тар-тар", description: "Необычный рыбный мини-бургер.", img: placeholderImg("🐟", "#FDEBEB") },

  // Киши
  { id: "q1", category: "quiches", name: "Киш с курицей и грибами", weight: "80 г", price: 4.90, composition: "Песочное тесто, курица, грибы, сливочная заливка", description: "Порционный тёплый пирог.", img: placeholderImg("🍗", "#FFF8E1") },
  { id: "q2", category: "quiches", name: "Киш лорен (бекон, сыр)", weight: "80 г", price: 5.20, composition: "Песочное тесто, бекон, сыр, заливка из яиц и сливок", description: "Классический французский киш.", img: placeholderImg("🥓", "#FFF8E1") },
  { id: "q3", category: "quiches", name: "Киш со шпинатом и сыром фета", weight: "80 г", price: 4.70, composition: "Песочное тесто, шпинат, фета, заливка", description: "Лёгкий вегетарианский вариант киша.", img: placeholderImg("🥬", "#FFF8E1") },
  { id: "q4", category: "quiches", name: "Киш с лососем", weight: "80 г", price: 5.80, composition: "Песочное тесто, лосось, укроп, заливка", description: "Праздничный вариант с красной рыбой.", img: placeholderImg("🐟", "#FFF8E1") },

  // Чизкейки
  { id: "c1", category: "cheesecakes", name: "Чизкейк Нью-Йорк порционный", weight: "60 г", price: 4.30, composition: "Творожный сыр, песочная основа, сливки", description: "Классический нью-йоркский чизкейк.", img: placeholderImg("🍰", "#FCE4EC") },
  { id: "c2", category: "cheesecakes", name: "Чизкейк с ягодами", weight: "60 г", price: 4.70, composition: "Творожный сыр, песочная основа, ягодный соус", description: "Свежая ягодная нота в десерте.", img: placeholderImg("🍓", "#FCE4EC") },
  { id: "c3", category: "cheesecakes", name: "Чизкейк шоколадный", weight: "60 г", price: 4.70, composition: "Творожный сыр, какао, шоколадная основа", description: "Насыщенный шоколадный вкус.", img: placeholderImg("🍫", "#FCE4EC") },
  { id: "c4", category: "cheesecakes", name: "Чизкейк с манго и маракуйей", weight: "60 г", price: 5.00, composition: "Творожный сыр, манго, маракуйя, песочная основа", description: "Яркий тропический десерт.", img: placeholderImg("🥭", "#FCE4EC") },

  // Закусочные рулеты
  { id: "br1", category: "biscuit-rolls", name: "Шпинатный рулет", weight: "450 г", price: 55.00, priceUnit: "рулет", orderLabel: "Нарежем на любое количество кусков", img: "assets/rolls/spinach-roll.jpg" },
  { id: "br2", category: "biscuit-rolls", name: "Свекольный рулет с сыром, чесноком и зеленью", weight: "450 г", price: 40.00, priceUnit: "рулет", orderLabel: "Нарежем на любое количество кусков", img: "assets/rolls/beetroot-roll.jpg" },
  { id: "br3", category: "biscuit-rolls", name: "Морковный рулет с курицей, грибами и грецким орехом", weight: "450 г", price: 45.00, priceUnit: "рулет", orderLabel: "Нарежем на любое количество кусков", img: "assets/rolls/carrot-roll.jpg" },

  // Пироги
  { id: "pie-chicken", category: "pies", name: "Пирог с курицей, сыром фета и томатами черри", weight: "1 кг", price: 45.00, priceUnit: "пирог", hideOrderLabel: true, img: "assets/boxes/chicken-feta-cherry-pie-whole.jpg" },
  { id: "pie-cabbage", category: "pies", name: "Пирог с капустой и грибами", weight: "1 кг", price: 40.00, priceUnit: "пирог", hideOrderLabel: true, img: "assets/boxes/cabbage-mushroom-pie-whole.jpg" },

  // Десерты
  { id: "d1", category: "desserts", name: "Шоколадное пирожное", price: 55.00, priceUnit: "кг", orderLabel: "Заказ кратно 1 кг. Разрежем на нужное количество кусочков", img: "assets/boxes/chocolate-cakes-detail.jpg" },
  { id: "d2", category: "desserts", name: "Басский чизкейк", weight: "900 г", price: 70.00, priceUnit: "чизкейк", hideOrderLabel: true, img: "assets/desserts/basque-cheesecake.jpg" },

  // Сеты
  { id: "set1", category: "sets", name: "Сет «Сыры и фрукты»", weight: "на 10 персон", price: 105.00, composition: "Ассорти сыров, виноград, орехи, мёд, крекеры", description: "Изысканная сырная тарелка для гостей.", img: placeholderImg("🧀", "#F1F8E9") },
  { id: "set2", category: "sets", name: "Сет «Мясные нарезки»", weight: "на 10 персон", price: 115.00, composition: "Ассорти колбас и мясных деликатесов, маслины, зелень", description: "Насыщенное мясное ассорти.", img: placeholderImg("🥩", "#F1F8E9") },
  { id: "set3", category: "sets", name: "Фритюрный сет", weight: "на 10 персон", price: 95.00, composition: "Ассорти закусок во фритюре: наггетсы, кольца кальмара, сырные шарики, соусы", description: "Горячие закуски для активного банкета.", img: placeholderImg("🍤", "#F1F8E9") },
  { id: "set4", category: "sets", name: "Сет «Под крепкие напитки»", weight: "на 10 персон", price: 110.00, composition: "Солёности, маринады, мясная и сырная нарезка, хлеб", description: "Классическая закуска под крепкий алкоголь.", img: placeholderImg("🥃", "#F1F8E9") },
];

// Временные правила конструктора для локального прототипа. Перед публикацией
// minQty и qtyStep утверждаются отдельно для каждой реальной позиции.
const DEMO_RULES = {
  bruschette: [4, 4], profiteroles: [8, 8], rolls: [21, 21],
  croissants: [5, 5], crostini: [10, 10],
  tartlets: [4, 4], sandwiches: [6, 6], salads: [9, 9],
  burgers: [6, 6], quiches: [6, 6], cheesecakes: [4, 4],
  "biscuit-rolls": [1, 1], desserts: [1, 1],
  napoleons: [18, 18], pies: [1, 1]
};

ITEMS.push(
  { id: "box-croissants", type: "ready-box", name: "Мини-круассаны", weight: "Бокс №1 · 15 шт. · 1 350 г", price: 120, img: "assets/boxes/croissants-appetizing-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-salmon-crab", type: "ready-box", name: "Бокс «Фуршетный»", weight: "Бокс №2 · 44 шт. + рулет · 1 490 г", price: 180, img: "assets/boxes/salmon-crab-appetizing-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-crostini", type: "ready-box", name: "Кростини к крепким напиткам", weight: "Бокс №3 · 20 шт. · 1 100 г", price: 65, img: "assets/boxes/crostini-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-baked-tartlets", type: "ready-box", name: "Запечённые тарталетки", weight: "Бокс №4 · 16 шт. · 960 г", price: 65, img: "assets/boxes/baked-tartlets-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-napoleons", type: "ready-box", name: "Солёные «Наполеоны»", weight: "Бокс №5 · 18 шт. · 720 г", price: 55, img: "assets/boxes/napoleons-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-caesar", type: "ready-box", name: "«Цезарь» с курицей", weight: "Бокс №6 · 9 шт. · 1 170 г", price: 81, img: "assets/boxes/caesar-outdoor-box-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-caesar-shrimp", type: "ready-box", name: "«Цезарь» с креветками", weight: "Бокс №7 · 9 шт. · 1 170 г", price: 99, img: "assets/boxes/caesar-shrimp-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-greek", type: "ready-box", name: "Греческий салат", weight: "Бокс №8 · 9 шт. · 1 170 г", price: 72, img: "assets/boxes/greek-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-ham-rolls", type: "ready-box", name: "Рулетики из ветчины (три начинки)", weight: "Бокс №9 · 21 шт. · 1 050 г", price: 75, img: "assets/boxes/ham-rolls-appetizing-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-assorted-rolls", type: "ready-box", name: "Ассорти рулетиков", weight: "Бокс №10 · 30 шт. · 1 340 г", price: 110, img: "assets/boxes/assorted-rolls-box.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-eggplant-rolls", type: "ready-box", name: "Рулетики из баклажана", weight: "Бокс №11 · 18 шт. · 720 г", price: 65, img: "assets/boxes/eggplant-rolls-detail-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-three-rolls", type: "ready-box", name: "Три закусочных рулета", weight: "Бокс №12 · 3 рулета · 1 350 г", price: 120, img: "assets/boxes/three-savory-rolls-box.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-profiteroles-mini", type: "ready-box", name: "Малый бокс профитролей", weight: "Бокс №13 · 16 шт. · 480 г", price: 45, img: "assets/boxes/profiteroles-mini-box-overview.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-profiteroles", type: "ready-box", name: "Большой бокс профитролей", weight: "Бокс №14 · 25 шт. · 750 г", price: 70, img: "assets/boxes/profiteroles-overview.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-mini-tartlets", type: "ready-box", name: "Мини-тарталетки", weight: "Бокс №15 · 64 шт. · 1 280 г", price: 130, img: "assets/boxes/mini-tartlets-box.jpg?v=3", minQty: 1, qtyStep: 1 },
  { id: "box-canapes", type: "ready-box", name: "Канапе", weight: "Бокс №16 · 21 шт. · 630 г", price: 65, img: "assets/boxes/canapes-overview.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-bruschetta-salmon-shrimp", type: "ready-box", name: "Брускетты с лососем и креветкой", weight: "Бокс №17 · 20 шт. · 1 200 г", price: 90, img: "assets/boxes/bruschetta-box-salmon-shrimp-natural.png?v=20260926d", minQty: 1, qtyStep: 1 },
  { id: "box-chicken-pie", type: "ready-box", name: "Пирог с курицей, сыром фета и томатами черри", weight: "Бокс №18 · 1 пирог · 1 кг", price: 45, img: "assets/boxes/chicken-feta-cherry-pie-whole.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-cabbage-pie", type: "ready-box", name: "Пирог с капустой и грибами", weight: "Бокс №19 · 1 пирог · 1 кг", price: 40, img: "assets/boxes/cabbage-mushroom-pie-whole.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-chocolate-cakes", type: "ready-box", name: "Шоколадные пирожные", weight: "Бокс №20 · 18 шт. · 2 160 г", price: 108, img: "assets/boxes/chocolate-cakes-overview.jpg?v=3", minQty: 1, qtyStep: 1 },
  { id: "box-basque-cheesecake", type: "ready-box", name: "Басский чизкейк", weight: "Бокс №21 · 1 чизкейк · 900 г", price: 70, img: "assets/desserts/basque-cheesecake.jpg", minQty: 1, qtyStep: 1 }
);

ITEMS.forEach(function (item) {
  if (!item.type) item.type = item.category === "sets" ? "legacy-placeholder" : "snack";
  if (item.type === "snack") {
    item.minQty = DEMO_RULES[item.category][0];
    item.qtyStep = DEMO_RULES[item.category][1];
  }
});

if (typeof module !== "undefined") module.exports = { CATEGORIES, ITEMS };
