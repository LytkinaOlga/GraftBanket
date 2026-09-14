const { ITEMS } = require('../js/data.js');
const catalog = Object.fromEntries(ITEMS.filter(item => item.type === 'snack').map(item => [item.id, item]));
const money = n => Number(n).toFixed(2) + ' BYN';
const clean = (value, limit = 200) => String(value || '').trim().slice(0, limit);

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chats = String(process.env.TELEGRAM_ADMIN_CHAT_ID || '').split(',').map(x => x.trim()).filter(Boolean);
  if (!token || !chats.length) return res.status(500).json({ error: 'Bot is not configured' });
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    if (!body || JSON.stringify(body).length > 12000) return res.status(400).json({ error: 'Invalid payload' });
    const name = clean(body.name, 80), phone = clean(body.phone, 40);
    const date = clean(body.eventDate, 10), time = clean(body.eventTime, 5);
    const method = clean(body.fulfillment, 12), address = clean(body.address, 200);
    const comment = clean(body.comment, 500), nick = clean(body.telegramNick, 80);
    const digits = phone.replace(/\D/g, '');
    if (name.length < 2 || digits.length < 10 || digits.length > 15 || !/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}$/.test(time) || !['pickup', 'minsk', 'other'].includes(method) || (method !== 'pickup' && address.length < 3)) return res.status(400).json({ error: 'Invalid contact details' });
    if (date < new Date().toISOString().slice(0, 10)) return res.status(400).json({ error: 'Date is in the past' });
    if (!Array.isArray(body.items) || !body.items.length || body.items.length > 50) return res.status(400).json({ error: 'Invalid items' });
    const seen = new Set();
    let subtotal = 0;
    const lines = body.items.map(row => {
      const item = catalog[row.id], qty = row.quantity;
      if (!item || seen.has(row.id) || !Number.isInteger(qty) || qty < item.minQty || qty > 1000 || (qty - item.minQty) % item.qtyStep !== 0) throw new Error('Invalid item or quantity');
      seen.add(row.id); subtotal += item.price * qty;
      return '• ' + item.name + ' — ' + qty + ' × ' + money(item.price) + ' = ' + money(item.price * qty);
    });
    const delivery = method === 'pickup' ? 0 : method === 'minsk' ? (subtotal >= 500 ? 0 : 20) : null;
    const orderId = 'DB-' + Date.now().toString(36).toUpperCase();
    const methodLabel = { pickup: 'Самовывоз', minsk: 'Доставка в пределах МКАД', other: 'Другое место, согласовать' }[method];
    const message = [
      '🆕 Заявка ' + orderId, 'Имя: ' + name, 'Телефон: ' + phone,
      nick ? 'Telegram: ' + nick : '', 'Дата и время: ' + date + ' ' + time,
      'Получение: ' + methodLabel, address ? 'Адрес/район: ' + address : '',
      comment ? 'Комментарий: ' + comment : '', 'Источник: ' + clean(body.source, 80),
      '', 'Состав:', ...lines, '', 'Товары: ' + money(subtotal),
      'Доставка: ' + (delivery === null ? 'уточнить' : money(delivery)),
      'Предварительный итог: ' + (delivery === null ? money(subtotal) + ' + доставка' : money(subtotal + delivery))
    ].filter(x => x !== '').join('\n');
    const results = await Promise.all(chats.map(async (chatId, index) => {
      try {
        const response = await fetch('https://api.telegram.org/bot' + token + '/sendMessage', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ chat_id: chatId, text: message }) });
        const result = await response.json();
        if (!response.ok || !result.ok) console.error('Telegram delivery failed for administrator ' + (index + 1) + ': ' + (result.description || 'HTTP ' + response.status));
        return Boolean(response.ok && result.ok);
      } catch (error) {
        console.error('Telegram delivery failed for administrator ' + (index + 1) + ':', error);
        return false;
      }
    }));
    if (!results.some(Boolean)) return res.status(502).json({ error: 'Telegram delivery failed' });
    return res.status(200).json({ ok: true, orderId });
  } catch (error) {
    if (error.message === 'Invalid item or quantity') return res.status(400).json({ error: error.message });
    console.error('Order request failed:', error);
    return res.status(500).json({ error: 'Server error' });
  }
};
