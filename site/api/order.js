// Серверная функция (Vercel Serverless Function).
// Принимает заявку с сайта и пересылает её администратору в Telegram.
// Токен бота и chat_id берутся из переменных окружения — задать их в настройках
// хостинга (Vercel: Project Settings -> Environment Variables), НЕ хранить в коде.

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  var BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  var ADMIN_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID;

  if (!BOT_TOKEN || !ADMIN_CHAT_ID) {
    res.status(500).json({ error: "Bot is not configured on the server" });
    return;
  }

  try {
    var body = req.body;
    if (typeof body === "string") body = JSON.parse(body);

    var telegramNick = String((body && body.telegramNick) || "").trim();
    var phone = String((body && body.phone) || "").trim();
    var items = Array.isArray(body && body.items) ? body.items : [];
    var total = Number((body && body.total) || 0);

    if (!telegramNick || !phone || items.length === 0) {
      res.status(400).json({ error: "Invalid order payload" });
      return;
    }

    var fmt = function (n) { return Number(n).toFixed(2) + " BYN"; };

    var lines = items.map(function (it) {
      var name = String(it.name || "—");
      var qty = Number(it.quantity || 0);
      var price = Number(it.price || 0);
      var sum = Number(it.sum || price * qty);
      return "• " + name + " — " + qty + " × " + fmt(price) + " = " + fmt(sum);
    });

    var text =
      "🆕 Новая заявка Draft Banket\n\n" +
      "Ник в Telegram: " + telegramNick + "\n" +
      "Телефон: " + phone + "\n\n" +
      "Состав заказа:\n" +
      lines.join("\n") +
      "\n\nИтого: " + fmt(total);

    var tgRes = await fetch("https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: ADMIN_CHAT_ID, text: text }),
    });

    var tgData = await tgRes.json();

    if (!tgData.ok) {
      res.status(502).json({ error: "Telegram API error", details: tgData });
      return;
    }

    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: "Server error", details: String(err) });
  }
};
