// Серверная функция (Vercel Serverless Function).
// Принимает заявку с сайта и пересылает её администраторам в Telegram.
// Токен бота и chat_id берутся из переменных окружения — задать их в настройках
// хостинга (Vercel: Project Settings -> Environment Variables), НЕ хранить в коде.
//
// TELEGRAM_ADMIN_CHAT_ID может содержать несколько chat_id через запятую,
// например: "979287967,123456789" — заявка уйдёт всем указанным сразу.

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  var BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  var ADMIN_CHAT_IDS_RAW = process.env.TELEGRAM_ADMIN_CHAT_ID;

  var ADMIN_CHAT_IDS = String(ADMIN_CHAT_IDS_RAW || "")
    .split(",")
    .map(function (id) { return id.trim(); })
    .filter(Boolean);

  if (!BOT_TOKEN || ADMIN_CHAT_IDS.length === 0) {
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

    var results = await Promise.all(
      ADMIN_CHAT_IDS.map(function (chatId) {
        return fetch("https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chat_id: chatId, text: text }),
        })
          .then(function (r) { return r.json(); })
          .then(function (data) { return { chatId: chatId, data: data }; })
          .catch(function (err) { return { chatId: chatId, data: { ok: false, error: String(err) } }; });
      })
    );

    var failed = results.filter(function (r) { return !r.data.ok; });
    var succeeded = results.filter(function (r) { return r.data.ok; });

    if (succeeded.length === 0) {
      res.status(502).json({ error: "Telegram API error", details: failed });
      return;
    }

    // Хотя бы одному администратору сообщение доставлено — считаем заявку принятой.
    // Сбои по остальным chat_id (например, устаревший/неверный ID) видны в логах Vercel.
    if (failed.length > 0) {
      console.error("Не удалось отправить заявку части администраторов:", failed);
    }

    res.status(200).json({ ok: true, delivered: succeeded.length, failed: failed.length });
  } catch (err) {
    res.status(500).json({ error: "Server error", details: String(err) });
  }
};
