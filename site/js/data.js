// Данные о блюдах — ЗАГЛУШКИ. Заменить на реальные фото/цены/описания перед запуском.
// Фото — временные (SVG-плейсхолдеры с эмодзи по теме блюда), заменить на реальные при наполнении контентом.

const CATEGORIES = [
  { id: "bruschette", title: "Брускетты" },
  { id: "profiteroles", title: "Профитроли" },
  { id: "rolls", title: "Рулетики" },
  { id: "tartlets", title: "Тарталетки" },
  { id: "sandwiches", title: "Мини сэндвичи" },
  { id: "salads", title: "Салаты" },
  { id: "burgers", title: "Мини бургеры" },
  { id: "quiches", title: "Киши" },
  { id: "cheesecakes", title: "Чизкейки" },
  { id: "biscuit-rolls", title: "Рулеты бисквитные" },
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
  { id: "b1", category: "bruschette", name: "Брускетта с томатами и базиликом", weight: "40 г", price: 3.20, composition: "Хлеб чиабатта, томаты, базилик, оливковое масло, чеснок", description: "Классика на хрустящей чиабатте.", img: placeholderImg("🍅", "#FCEEE0") },
  { id: "b2", category: "bruschette", name: "Брускетта с лососем", weight: "40 г", price: 4.50, composition: "Хлеб чиабатта, слабосолёный лосось, крем-сыр, укроп", description: "Нежный крем-сыр и лосось на поджаристом хлебе.", img: placeholderImg("🐟", "#FCEEE0") },
  { id: "b3", category: "bruschette", name: "Брускетта с прошутто и грушей", weight: "40 г", price: 4.80, composition: "Чиабатта, прошутто, груша, руккола, мёд", description: "Сладко-солёное сочетание для банкетного стола.", img: placeholderImg("🍐", "#FCEEE0") },
  { id: "b4", category: "bruschette", name: "Брускетта с грибами", weight: "40 г", price: 3.50, composition: "Чиабатта, шампиньоны, сливочный соус, пармезан", description: "Тёплая брускетта с ароматными грибами.", img: placeholderImg("🍄", "#FCEEE0") },

  // Профитроли
  { id: "p1", category: "profiteroles", name: "Профитроли с курицей и сыром", weight: "25 г", price: 2.60, composition: "Заварное тесто, куриное филе, сыр, соус", description: "Мини-профитроли с сытной начинкой.", img: placeholderImg("🍗", "#F3E8FF") },
  { id: "p2", category: "profiteroles", name: "Профитроли с лососем", weight: "25 г", price: 3.20, composition: "Заварное тесто, лосось, крем-сыр", description: "Изысканная закуска для фуршета.", img: placeholderImg("🐟", "#F3E8FF") },
  { id: "p3", category: "profiteroles", name: "Профитроли с ветчиной и грибами", weight: "25 г", price: 2.80, composition: "Заварное тесто, ветчина, грибы, сливочный соус", description: "Насыщенная начинка в нежном тесте.", img: placeholderImg("🍄", "#F3E8FF") },
  { id: "p4", category: "profiteroles", name: "Профитроли сладкие (крем)", weight: "25 г", price: 2.40, composition: "Заварное тесто, заварной крем, сахарная пудра", description: "Десертный вариант для сладкого стола.", img: placeholderImg("🍮", "#F3E8FF") },

  // Рулетики
  { id: "r1", category: "rolls", name: "Рулетики из лаваша с курицей", weight: "35 г", price: 2.90, composition: "Лаваш, куриное филе, овощи, соус", description: "Сочная начинка в тонком лаваше.", img: placeholderImg("🍗", "#E8F5E9") },
  { id: "r2", category: "rolls", name: "Рулетики с ветчиной и сыром", weight: "35 г", price: 3.00, composition: "Лаваш, ветчина, сыр, зелень", description: "Простое и любимое сочетание.", img: placeholderImg("🧀", "#E8F5E9") },
  { id: "r3", category: "rolls", name: "Рулетики с лососем и крем-сыром", weight: "35 г", price: 4.00, composition: "Лаваш, лосось, крем-сыр, укроп", description: "Праздничный вариант рулетиков.", img: placeholderImg("🐟", "#E8F5E9") },
  { id: "r4", category: "rolls", name: "Рулетики овощные", weight: "35 г", price: 2.60, composition: "Лаваш, овощи гриль, соус, зелень", description: "Лёгкий вегетарианский вариант.", img: placeholderImg("🥒", "#E8F5E9") },

  // Тарталетки
  { id: "t1", category: "tartlets", name: "Тарталетка с салатом «Оливье»", weight: "30 г", price: 2.70, composition: "Песочная тарталетка, салат оливье", description: "Порционная классика в удобном формате.", img: placeholderImg("🥗", "#FFF3E0") },
  { id: "t2", category: "tartlets", name: "Тарталетка с красной икрой", weight: "30 г", price: 5.50, composition: "Песочная тарталетка, сливочный сыр, красная икра", description: "Праздничная закуска для банкета.", img: placeholderImg("🍣", "#FFF3E0") },
  { id: "t3", category: "tartlets", name: "Тарталетка с грибным жюльеном", weight: "30 г", price: 3.50, composition: "Песочная тарталетка, грибы, сливочный соус, сыр", description: "Тёплая и ароматная закуска.", img: placeholderImg("🍄", "#FFF3E0") },
  { id: "t4", category: "tartlets", name: "Тарталетка с креветкой и авокадо", weight: "30 г", price: 4.60, composition: "Песочная тарталетка, креветка, авокадо, соус", description: "Свежий и лёгкий вкус.", img: placeholderImg("🍤", "#FFF3E0") },

  // Мини сэндвичи
  { id: "s1", category: "sandwiches", name: "Мини сэндвич с ростбифом", weight: "45 г", price: 3.80, composition: "Хлеб, ростбиф, руккола, соус", description: "Сытный и аккуратный мини-формат.", img: placeholderImg("🥩", "#E3F2FD") },
  { id: "s2", category: "sandwiches", name: "Мини сэндвич с индейкой и авокадо", weight: "45 г", price: 3.60, composition: "Хлеб, индейка, авокадо, листовой салат", description: "Лёгкий вариант с нежной начинкой.", img: placeholderImg("🥑", "#E3F2FD") },
  { id: "s3", category: "sandwiches", name: "Мини сэндвич с лососем", weight: "45 г", price: 4.40, composition: "Хлеб, лосось, крем-сыр, огурец", description: "Праздничный вариант мини-сэндвича.", img: placeholderImg("🐟", "#E3F2FD") },
  { id: "s4", category: "sandwiches", name: "Мини сэндвич вегетарианский", weight: "45 г", price: 3.20, composition: "Хлеб, овощи, хумус, зелень", description: "Свежий вегетарианский выбор.", img: placeholderImg("🥬", "#E3F2FD") },

  // Салаты
  { id: "sl1", category: "salads", name: "Салат «Цезарь» порционный", weight: "150 г", price: 6.50, composition: "Курица, салат ромэн, пармезан, соус цезарь, гренки", description: "Порционная подача классического салата.", img: placeholderImg("🥗", "#EAF7E9") },
  { id: "sl2", category: "salads", name: "Салат с креветками и авокадо", weight: "150 г", price: 7.80, composition: "Креветки, авокадо, микс салатов, соус", description: "Лёгкий салат для праздничного стола.", img: placeholderImg("🍤", "#EAF7E9") },
  { id: "sl3", category: "salads", name: "Греческий салат порционный", weight: "150 г", price: 5.60, composition: "Огурцы, томаты, перец, сыр фета, оливки", description: "Свежий средиземноморский вкус.", img: placeholderImg("🫒", "#EAF7E9") },
  { id: "sl4", category: "salads", name: "Салат со свёклой и козьим сыром", weight: "150 г", price: 6.20, composition: "Свёкла, козий сыр, грецкий орех, микс салатов", description: "Яркое сочетание вкусов и текстур.", img: placeholderImg("🧀", "#EAF7E9") },

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

  // Рулеты бисквитные
  { id: "br1", category: "biscuit-rolls", name: "Бисквитный рулет с вишней", weight: "60 г", price: 4.00, composition: "Бисквит, сливочный крем, вишня", description: "Классика в порционном формате.", img: placeholderImg("🍒", "#EDE7F6") },
  { id: "br2", category: "biscuit-rolls", name: "Бисквитный рулет с клубникой", weight: "60 г", price: 4.10, composition: "Бисквит, сливочный крем, клубника", description: "Лёгкий и свежий десерт.", img: placeholderImg("🍓", "#EDE7F6") },
  { id: "br3", category: "biscuit-rolls", name: "Бисквитный рулет шоколадный", weight: "60 г", price: 4.30, composition: "Шоколадный бисквит, шоколадный крем", description: "Для любителей насыщенного шоколада.", img: placeholderImg("🍫", "#EDE7F6") },
  { id: "br4", category: "biscuit-rolls", name: "Бисквитный рулет карамельный", weight: "60 г", price: 4.30, composition: "Бисквит, крем со сгущённым молоком, карамель", description: "Нежный вкус карамели и сливок.", img: placeholderImg("🍮", "#EDE7F6") },

  // Сеты
  { id: "set1", category: "sets", name: "Сет «Сыры и фрукты»", weight: "на 10 персон", price: 105.00, composition: "Ассорти сыров, виноград, орехи, мёд, крекеры", description: "Изысканная сырная тарелка для гостей.", img: placeholderImg("🧀", "#F1F8E9") },
  { id: "set2", category: "sets", name: "Сет «Мясные нарезки»", weight: "на 10 персон", price: 115.00, composition: "Ассорти колбас и мясных деликатесов, маслины, зелень", description: "Насыщенное мясное ассорти.", img: placeholderImg("🥩", "#F1F8E9") },
  { id: "set3", category: "sets", name: "Фритюрный сет", weight: "на 10 персон", price: 95.00, composition: "Ассорти закусок во фритюре: наггетсы, кольца кальмара, сырные шарики, соусы", description: "Горячие закуски для активного банкета.", img: placeholderImg("🍤", "#F1F8E9") },
  { id: "set4", category: "sets", name: "Сет «Под крепкие напитки»", weight: "на 10 персон", price: 110.00, composition: "Солёности, маринады, мясная и сырная нарезка, хлеб", description: "Классическая закуска под крепкий алкоголь.", img: placeholderImg("🥃", "#F1F8E9") },
];

// Временные правила конструктора для локального прототипа. Перед публикацией
// minQty и qtyStep утверждаются отдельно для каждой реальной позиции.
const DEMO_RULES = {
  bruschette: [6, 6], profiteroles: [8, 4], rolls: [6, 6],
  tartlets: [8, 4], sandwiches: [6, 6], salads: [2, 1],
  burgers: [6, 3], quiches: [6, 3], cheesecakes: [4, 2],
  "biscuit-rolls": [4, 2]
};

ITEMS.push(
  { id: "box-ham-rolls", type: "ready-box", name: "Рулетики из ветчины", weight: "Бокс №1 · 21 шт. · 1 050 г", price: 75, img: "assets/boxes/ham-rolls-appetizing-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-salmon-crab", type: "ready-box", name: "Лосось и краб", weight: "Бокс №2 · 44 шт. + рулет · 1 490 г", price: 180, img: "assets/boxes/salmon-crab-appetizing-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-assorted-rolls", type: "ready-box", name: "Ассорти рулетиков", weight: "Бокс №3 · 30 шт. · 1 340 г", price: 110, img: "assets/boxes/assorted-rolls-box.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-croissants", type: "ready-box", name: "Мини-круассаны", weight: "Бокс №4 · 15 шт. · 1 350 г", price: 120, img: "assets/boxes/croissants-appetizing-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-crostini", type: "ready-box", name: "Кростини к крепким напиткам", weight: "Бокс №5 · 20 шт. · 1 100 г", price: 65, img: "assets/boxes/crostini-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-baked-tartlets", type: "ready-box", name: "Запечённые тарталетки", weight: "Бокс №6 · 16 шт. · 960 г", price: 65, img: "assets/boxes/baked-tartlets-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-eggplant-rolls", type: "ready-box", name: "Рулетики из баклажана", weight: "Бокс №7 · 18 шт. · 720 г", price: 65, img: "assets/boxes/eggplant-rolls-detail-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-napoleons", type: "ready-box", name: "Солёные «Наполеоны»", weight: "Бокс №8 · 18 шт. · вес уточняется", price: 55, img: "assets/boxes/napoleons-overview-mobile.jpg", minQty: 1, qtyStep: 1 },
  { id: "box-caesar", type: "ready-box", name: "«Цезарь» с курицей", weight: "Бокс №9 · 9 шт. · 1 170 г", price: 81, img: "assets/boxes/caesar-outdoor-box-mobile.jpg", minQty: 1, qtyStep: 1 }
);

ITEMS.forEach(function (item) {
  if (!item.type) item.type = item.category === "sets" ? "legacy-placeholder" : "snack";
  if (item.type === "snack") {
    item.minQty = DEMO_RULES[item.category][0];
    item.qtyStep = DEMO_RULES[item.category][1];
  }
});

if (typeof module !== "undefined") module.exports = { CATEGORIES, ITEMS };
