const { ITEMS } = require('../js/data.js');
const hiddenCategories = new Set(['profiteroles', 'sandwiches', 'burgers', 'quiches', 'cheesecakes']);
const catalog = Object.fromEntries(ITEMS.filter(item => item.type === 'ready-box' || item.type === 'set' || (item.type === 'snack' && !hiddenCategories.has(item.category))).map(item => [item.id, item]));
const lineTotal = (item, qty) => item.bundlePrice ? item.bundlePrice * qty / item.minQty : item.price * qty;
const money = n => Number(n).toFixed(2) + ' BYN';
const clean = (value, limit = 200) => String(value || '').trim().slice(0, limit);
const SITE_URL = 'https://www.draftcatering.by/';
// Откуда пришёл клиент — по меткам utm (Instagram сам ставит link_in_bio на ссылку в шапке профиля).
const channelLabel = (source, utm) => {
  const src = String(source || '').toLowerCase(), medium = String(utm.medium || '').toLowerCase();
  const campaign = String(utm.campaign || ''), content = String(utm.content || '').toLowerCase();
  if (!src || src === 'site') return 'сайт, без метки';
  if (src === 'ig' || src === 'instagram') {
    if (medium === 'paid' || /^\d{6,}$/.test(campaign)) return 'реклама Instagram' + (campaign && !/^\d+$/.test(campaign) ? ' (' + campaign + ')' : '');
    if (content === 'link_in_bio' || medium === 'bio') return 'ссылка в шапке Instagram';
    if (medium === 'stories') return 'сторис Instagram';
    return 'Instagram';
  }
  return [src, medium, campaign].filter(Boolean).join(' / ');
};
const imageUrl = item => item && item.img ? SITE_URL + String(item.img).replace(/^\/+/, '') : null;

// Photos of the ordered items, sent as a reply to the order card (like Slivki orders in the bot).
// Caption: "Name × qty"; pack-priced items by pack; the gift is marked. Up to 10 photos per album.
function orderPhotos(copyItems, gift) {
  const list = copyItems.filter(i => i.image).map(i => ({
    image: i.image,
    caption: i.pack > 1 && i.qty % i.pack === 0 ? i.title + ' (упаковка ' + i.pack + ' шт.) × ' + (i.qty / i.pack) : i.title + ' × ' + i.qty
  }));
  const giftImage = imageUrl(gift);
  if (gift && giftImage) list.push({ image: giftImage, caption: '🎁 ' + gift.name + ' — подарок' });
  return list;
}

// Photos are extra: any failure is only logged, the order itself was already delivered.
async function sendOrderPhotos(token, chatId, replyTo, photos) {
  if (!photos.length) return;
  const replyParameters = { message_id: replyTo, allow_sending_without_reply: true };
  for (let i = 0; i < photos.length; i += 10) {
    const chunk = photos.slice(i, i + 10);
    const single = chunk.length === 1;
    const body = single
      ? { chat_id: chatId, photo: chunk[0].image, caption: chunk[0].caption, reply_parameters: replyParameters }
      : { chat_id: chatId, media: chunk.map(p => ({ type: 'photo', media: p.image, caption: p.caption })), reply_parameters: replyParameters };
    try {
      const response = await fetch('https://api.telegram.org/bot' + token + (single ? '/sendPhoto' : '/sendMediaGroup'), {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(8000)
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) console.error('Order photos failed: ' + (result.description || 'HTTP ' + response.status));
    } catch (error) {
      console.error('Order photos failed:', error.message);
    }
  }
}

// Copy of the order for the shared orders database (calendar and the 10:00 summary in the admin bot).
// Telegram delivery stays the main path: if the copy fails, admins still get the order plus a warning.
// Disabled until ORDERS_API_URL and ORDERS_API_SECRET are set on Vercel.
async function copyOrder(payload) {
  const url = process.env.ORDERS_API_URL, secret = process.env.ORDERS_API_SECRET;
  if (!url || !secret) return null;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Orders-Secret': secret },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(6000)
    });
    const result = await response.json().catch(() => null);
    if (!response.ok || !result || !result.ok) {
      console.error('Order copy failed: ' + ((result && (result.field || result.error)) || 'HTTP ' + response.status));
      return false;
    }
    return true;
  } catch (error) {
    console.error('Order copy failed:', error.message);
    return false;
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chats = String(process.env.TELEGRAM_ADMIN_CHAT_ID || '').split(',').map(x => x.trim()).filter(Boolean);
  if (!token || !chats.length) return res.status(500).json({ error: 'Bot is not configured' });
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    if (!body || JSON.stringify(body).length > 12000) return res.status(400).json({ error: 'Invalid payload' });
    const name = clean(body.name, 80), phone = clean(body.phone, 40);
    const date = clean(body.eventDate, 10);
    const time = clean(body.eventTime, 5);
    const payment = clean(body.payment, 8);
    const guests = Number.isInteger(body.guests) && body.guests >= 1 && body.guests <= 1000 ? body.guests : null;
    const method = clean(body.fulfillment, 12), address = clean(body.address, 200);
    const comment = clean(body.comment, 500), nick = clean(body.telegramNick, 80);
    const digits = phone.replace(/\D/g, '');
    if (name.length < 2 || digits.length < 10 || digits.length > 15 || !/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^([01]\d|2[0-3]):[0-5]\d$/.test(time) || !['cash', 'card'].includes(payment) || !['pickup', 'minsk', 'other'].includes(method) || (method !== 'pickup' && address.length < 3)) return res.status(400).json({ error: 'Invalid contact details' });
    if (date < new Date().toISOString().slice(0, 10)) return res.status(400).json({ error: 'Date is in the past' });
    if (!Array.isArray(body.items) || !body.items.length || body.items.length > 50) return res.status(400).json({ error: 'Invalid items' });
    const seen = new Set();
    let subtotal = 0, giftSubtotal = 0;
    const copyItems = [];
    const lines = body.items.map(row => {
      const item = catalog[row.id], qty = row.quantity;
      if (!item || item.available === false || seen.has(row.id) || !Number.isInteger(qty) || qty < item.minQty || qty > 1000 || (qty - item.minQty) % item.qtyStep !== 0) throw new Error('Invalid item or quantity');
      seen.add(row.id); subtotal += lineTotal(item, qty);
      // Sets are already discounted, so they don't count towards the gift threshold (the birthday discount still applies).
      if (item.type !== 'set') giftSubtotal += lineTotal(item, qty);
      copyItems.push({ id: item.id, title: item.name, qty, pack: item.bundlePrice ? item.minQty : 1, total: lineTotal(item, qty), image: imageUrl(item) });
      return '• ' + item.name + ' — ' + qty + ' × ' + money(item.price) + ' = ' + money(lineTotal(item, qty));
    });
    const GIFT_THRESHOLD = 200;
    const GIFT_ITEM_ID = 'br1'; // spinach roll (from 10.11.2026; before: small profiterole box from 300 BYN)
    const BIRTHDAY_DISCOUNT_RATE = 0.10;
    const birthdayDiscount = Boolean(body.birthdayDiscount);
    const discount = birthdayDiscount ? Math.round(subtotal * BIRTHDAY_DISCOUNT_RATE * 100) / 100 : 0;
    const giftItem = catalog[GIFT_ITEM_ID];
    // Promos don't stack: no gift box when the birthday discount is applied.
    const giftApplied = giftSubtotal >= GIFT_THRESHOLD && Boolean(giftItem) && !birthdayDiscount;
    const discountedSubtotal = subtotal - discount;
    const delivery = method === 'pickup' ? 0 : method === 'minsk' ? (subtotal >= 500 ? 0 : 20) : null;
    const orderId = 'DB-' + Date.now().toString(36).toUpperCase();
    const source = clean(body.source, 80);
    const rawUtm = body.utm && typeof body.utm === 'object' ? body.utm : {};
    const utm = { medium: clean(rawUtm.medium, 120), campaign: clean(rawUtm.campaign, 120), content: clean(rawUtm.content, 120) };
    const methodLabel = { pickup: 'Самовывоз', minsk: 'Доставка в пределах МКАД', other: 'Другое место, согласовать' }[method];
    const message = [
      '🌐 Сайт · 🆕 Заявка ' + orderId, 'Имя: ' + name, 'Телефон: ' + phone,
      nick ? 'Telegram: ' + nick : '', 'Дата: ' + date.split('-').reverse().join('.'),
      (method === 'pickup' ? 'Время самовывоза: ' : 'Время доставки: ') + time,
      'Получение: ' + methodLabel, address ? 'Адрес/район: ' + address : '',
      'Оплата: ' + (payment === 'cash' ? 'наличными' : 'картой'),
      guests ? 'Гостей: ' + guests : '',
      comment ? 'Комментарий: ' + comment : '', 'Источник: ' + channelLabel(source, utm) + (source && source !== 'site' ? ' [' + [source, utm.medium, utm.campaign].filter(Boolean).join(' / ') + ']' : ''),
      '', 'Состав:', ...lines,
      giftApplied ? '🎁 Подарок: ' + giftItem.name + ' — ' + giftItem.weight.replace(/^Бокс №\d+ · /, '') + ' (бесплатно)' : '',
      '', 'Товары: ' + money(subtotal),
      birthdayDiscount ? 'Скидка (день рождения, −10%): −' + money(discount) : '',
      Boolean(body.birthday) && !birthdayDiscount && giftApplied ? '🎂 Именинник: выбрал подарок вместо скидки 10%' : '',
      'Доставка: ' + (delivery === null ? 'уточнить' : money(delivery)),
      'Предварительный итог: ' + (delivery === null ? money(discountedSubtotal) + ' + доставка' : money(discountedSubtotal + delivery))
    ].filter(x => x !== '').join('\n');
    const send = text => Promise.all(chats.map(async (chatId, index) => {
      try {
        const response = await fetch('https://api.telegram.org/bot' + token + '/sendMessage', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ chat_id: chatId, text }) });
        const result = await response.json();
        if (!response.ok || !result.ok) console.error('Telegram delivery failed for administrator ' + (index + 1) + ': ' + (result.description || 'HTTP ' + response.status));
        // message_id of the order card: photos are sent as a reply to it
        return response.ok && result.ok ? (result.result && result.result.message_id) || true : false;
      } catch (error) {
        console.error('Telegram delivery failed for administrator ' + (index + 1) + ':', error);
        return false;
      }
    }));
    const photos = orderPhotos(copyItems, giftApplied ? giftItem : null);
    const sendPhotos = cards => Promise.all(chats.map((chatId, index) =>
      typeof cards[index] === 'number' ? sendOrderPhotos(token, chatId, cards[index], photos) : null));
    const copy = copyOrder({
      order_id: orderId, name, phone, telegram: nick, date, time, method, address, payment, guests, comment,
      source, utm, channel: channelLabel(source, utm), items: copyItems, subtotal, discount, birthday: birthdayDiscount,
      gift: giftApplied ? { id: giftItem.id, title: giftItem.name, image: imageUrl(giftItem) } : null,
      delivery, total: delivery === null ? discountedSubtotal : discountedSubtotal + delivery
    });
    const [results, copied] = await Promise.all([send(message).then(async cards => { await sendPhotos(cards); return cards; }), copy]);
    if (!results.some(Boolean)) return res.status(502).json({ error: 'Telegram delivery failed' });
    if (copied === false) await send('⚠️ Заявка ' + orderId + ' не сохранилась в календарь (база недоступна). Сама заявка выше — обработайте её как обычно.');
    return res.status(200).json({ ok: true, orderId });
  } catch (error) {
    if (error.message === 'Invalid item or quantity') return res.status(400).json({ error: error.message });
    console.error('Order request failed:', error);
    return res.status(500).json({ error: 'Server error' });
  }
};
