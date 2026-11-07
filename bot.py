import asyncio
import random
import sqlite3
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

TOKEN = "9181799184:AAH4wru-BfbB2X2iVRr3zedonPPBtf8YBzA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ============ БАЗА ============
conn = sqlite3.connect("game.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    distance INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,
    last_walk TEXT DEFAULT NULL,
    inventory TEXT DEFAULT '',
    lvl_distance INTEGER DEFAULT 0,
    lvl_luck INTEGER DEFAULT 0,
    last_daily TEXT DEFAULT NULL
)
""")
conn.commit()

# ============ ПРЕДМЕТЫ ============
# (название, редкость, шанс, цена)
ITEMS = [
    # 🗑 МУСОР
    ("Ржавая гайка", "🗑 Мусор", 8, 1),
    ("Огрызок яблока", "🗑 Мусор", 8, 1),
    ("Камень", "🗑 Мусор", 8, 2),
    ("Порванный носок", "🗑 Мусор", 7, 1),
    ("Битая бутылка", "🗑 Мусор", 7, 2),
    ("Старая газета", "🗑 Мусор", 6, 1),
    ("Погнутая вилка", "🗑 Мусор", 6, 2),
    ("Крышка от банки", "🗑 Мусор", 6, 1),
    ("Мокрая картонка", "🗑 Мусор", 6, 1),
    ("Ржавый гвоздь", "🗑 Мусор", 6, 2),
    ("Сломанная ручка", "🗑 Мусор", 5, 1),
    ("Записка 'позвони мне'", "🗑 Мусор", 5, 1),
    ("Пакетик от чипсов", "🗑 Мусор", 5, 1),
    ("Обломок кирпича", "🗑 Мусор", 5, 2),
    ("Разряженная батарейка", "🗑 Мусор", 5, 3),
    ("Куриная косточка", "🗑 Мусор", 4, 1),
    ("Пустая жестянка", "🗑 Мусор", 4, 2),
    ("Порванный пакет", "🗑 Мусор", 4, 1),
    ("Скелет рыбы", "🗑 Мусор", 4, 2),
    ("Шнурок без пары", "🗑 Мусор", 4, 1),

    # ⚪ ОБЫЧНОЕ
    ("Медная монета", "⚪ Обычное", 4, 10),
    ("Старая книга", "⚪ Обычное", 3.5, 25),
    ("Керамическая чашка", "⚪ Обычное", 3.5, 40),
    ("Деревянная ложка", "⚪ Обычное", 3.5, 15),
    ("Кусок мыла", "⚪ Обычное", 3, 12),
    ("Перочинный нож", "⚪ Обычное", 3, 35),
    ("Стеклянный шарик", "⚪ Обычное", 3, 18),
    ("Оловянный солдатик", "⚪ Обычное", 3, 30),
    ("Ремень", "⚪ Обычное", 2.5, 20),
    ("Фонарик", "⚪ Обычное", 2.5, 28),
    ("Компас без стрелки", "⚪ Обычное", 2.5, 22),
    ("Глиняный горшок", "⚪ Обычное", 2.5, 26),
    ("Старая карта города", "⚪ Обычное", 2.5, 32),
    ("Кожаный кошелёк", "⚪ Обычное", 2.5, 45),
    ("Свеча", "⚪ Обычное", 2.5, 8),
    ("Клубок шерсти", "⚪ Обычное", 2, 14),
    ("Пряжка", "⚪ Обычное", 2, 16),
    ("Медный подсвечник", "⚪ Обычное", 2, 40),
    ("Жестяная кружка", "⚪ Обычное", 2, 24),
    ("Игральные кости", "⚪ Обычное", 2, 19),
    ("Кремень", "⚪ Обычное", 2, 11),
    ("Кухонный нож", "⚪ Обычное", 2, 30),
    ("Верёвка", "⚪ Обычное", 2, 9),
    ("Зеркальце", "⚪ Обычное", 1.8, 27),
    ("Табакерка", "⚪ Обычное", 1.8, 33),
    ("Рыболовный крючок", "⚪ Обычное", 1.8, 21),

    # 🔵 РЕДКОЕ
    ("Серебряное кольцо", "🔵 Редкое", 1.5, 150),
    ("Старинная карта", "🔵 Редкое", 1.4, 200),
    ("Бронзовый медальон", "🔵 Редкое", 1.3, 180),
    ("Хрустальный флакон", "🔵 Редкое", 1.2, 220),
    ("Кошель с монетами", "🔵 Редкое", 1.2, 260),
    ("Шкатулка с резьбой", "🔵 Редкое", 1.1, 300),
    ("Стальной клинок", "🔵 Редкое", 1.1, 280),
    ("Золотая монета", "🔵 Редкое", 1.0, 350),
    ("Янтарный амулет", "🔵 Редкое", 1.0, 400),
    ("Сапфировая брошь", "🔵 Редкое", 0.9, 450),
    ("Изумрудная серьга", "🔵 Редкое", 0.9, 500),
    ("Рубин в оправе", "🔵 Редкое", 0.8, 550),
    ("Пергамент с печатью", "🔵 Редкое", 0.8, 320),
    ("Орден старого рыцаря", "🔵 Редкое", 0.7, 600),
    ("Кинжал с гравировкой", "🔵 Редкое", 0.7, 520),
    ("Кубок из серебра", "🔵 Редкое", 0.6, 580),
    ("Шлем легионера", "🔵 Редкое", 0.6, 650),
    ("Астролябия", "🔵 Редкое", 0.5, 700),
    ("Часы карманные", "🔵 Редкое", 0.5, 480),
    ("Печатка с гербом", "🔵 Редкое", 0.5, 620),

    # 🟣 ЭПИК
    ("Золотой слиток", "🟣 Эпик", 0.4, 800),
    ("Кристалл света", "🟣 Эпик", 0.35, 1200),
    ("Свиток телепортации", "🟣 Эпик", 0.3, 1500),
    ("Сердце голема", "🟣 Эпик", 0.3, 1800),
    ("Корона падшего короля", "🟣 Эпик", 0.25, 2200),
    ("Амулет бессмертия", "🟣 Эпик", 0.25, 2600),
    ("Клык дракона", "🟣 Эпик", 0.22, 3000),
    ("Сфера предвидения", "🟣 Эпик", 0.2, 3500),
    ("Эльфийский лук", "🟣 Эпик", 0.2, 2800),
    ("Гримуар тёмной магии", "🟣 Эпик", 0.18, 4000),
    ("Доспех из мифрила", "🟣 Эпик", 0.15, 4500),
    ("Клинок зари", "🟣 Эпик", 0.15, 5000),
    ("Философский камень", "🟣 Эпик", 0.12, 5500),
    ("Око титана", "🟣 Эпик", 0.12, 6000),
    ("Плащ теней", "🟣 Эпик", 0.1, 6500),

    # 🟠 ЛЕГЕНДАРКА
    ("Клинок предков", "🟠 Легендарка", 0.08, 9000),
    ("Древняя реликвия", "🟠 Легендарка", 0.07, 12000),
    ("Посох архимага", "🟠 Легендарка", 0.06, 15000),
    ("Молот богов", "🟠 Легендарка", 0.05, 18000),
    ("Кольцо всевластия", "🟠 Легендарка", 0.05, 22000),
    ("Крылья феникса", "🟠 Легендарка", 0.04, 26000),
    ("Чаша Грааля", "🟠 Легендарка", 0.04, 30000),
    ("Слеза богини", "🟠 Легендарка", 0.03, 35000),
    ("Клык левиафана", "🟠 Легендарка", 0.03, 40000),
    ("Трон из костей", "🟠 Легендарка", 0.02, 45000),
    ("Сердце мира", "🟠 Легендарка", 0.02, 50000),
    ("Ковёр-самолёт (мини)", "🟠 Легендарка", 0.02, 38000),
    ("Ключ от всех дверей", "🟠 Легендарка", 0.015, 48000),

    # 🌈 РАДУЖКА
    ("🌈 Радужная фарфоровая призма", "🌈 РАДУЖКА", 0.01, 100000),
    ("🌈 Радужный единорог", "🌈 РАДУЖКА", 0.008, 120000),
    ("🌈 Радужное сердце мира", "🌈 РАДУЖКА", 0.006, 150000),
    ("🌈 Радужный кристалл вселенной", "🌈 РАДУЖКА", 0.004, 200000),
    ("🌈 Радужный трон богов", "🌈 РАДУЖКА", 0.002, 500000),
]

# ============ УЛУЧШЕНИЯ ============
UPGRADES = {
    "distance": {
        "name": "👟 Скорость ходьбы",
        "desc": "+1 км к каждому походу за уровень",
        "base_price": 100,
        "growth": 1.6,
        "max_lvl": 20,
    },
    "luck": {
        "name": "🍀 Удача",
        "desc": "+2% к шансу находки за уровень",
        "base_price": 150,
        "growth": 1.7,
        "max_lvl": 20,
    },
}

def upgrade_price(key, lvl):
    u = UPGRADES[key]
    return int(u["base_price"] * (u["growth"] ** lvl))

# ============ ХЕЛПЕРЫ ============
def get_player(user_id, username=None):
    cur.execute("SELECT distance, balance, last_walk, inventory, lvl_distance, lvl_luck, last_daily FROM players WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO players (user_id, username) VALUES (?, ?)", (user_id, username or ""))
        conn.commit()
        return 0, 0, None, "", 0, 0, None
    if username:
        cur.execute("UPDATE players SET username=? WHERE user_id=?", (username, user_id))
        conn.commit()
    return row

def update_player(user_id, distance, balance, last_walk, inventory, lvl_distance=0, lvl_luck=0, last_daily=None):
    cur.execute("UPDATE players SET distance=?, balance=?, last_walk=?, inventory=?, lvl_distance=?, lvl_luck=?, last_daily=? WHERE user_id=?",
                (distance, balance, last_walk, inventory, lvl_distance, lvl_luck, last_daily, user_id))
    conn.commit()

def roll_item(bonus_chance=0.0):
    weighted = []
    for it in ITEMS:
        weight = it[2]
        if it[2] < 1:
            weight *= (1 + bonus_chance)
        weighted.append(weight)

    total_w = sum(weighted)
    r = random.uniform(0, total_w)
    upto = 0
    for it, w in zip(ITEMS, weighted):
        upto += w
        if r <= upto:
            return it
    return ITEMS[0]

# ============ СТАРТ ============
@dp.message(Command("start"))
async def start(msg: Message):
    get_player(msg.from_user.id, msg.from_user.username)
    text = (
        "🎒 <b>Добро пожаловать в Искателя!</b>\n\n"
        "Ты — путешественник, который исследует мир и находит сокровища.\n\n"
        "<b>Команды:</b>\n"
        "🚶 /walk — отправиться в путь\n"
        "🎁 /daily — ежедневная награда (5–75 монет)\n"
        "📊 /stats — статистика\n"
        "🎒 /inventory — инвентарь\n"
        "💰 /sell — продать всё\n"
        "🛒 /shop — магазин улучшений\n"
        "🏆 /top — лидерборд\n\n"
        "Кулдаун прогулки: 30 мин."
    )
    await msg.answer(text, parse_mode="HTML")

# ============ ПРОГУЛКА ============
@dp.message(Command("walk"))
async def walk(msg: Message):
    user_id = msg.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id, msg.from_user.username)

    now = datetime.now()
    if last_walk:
        last = datetime.fromisoformat(last_walk)
        if now - last < timedelta(minutes=30):
            left = timedelta(minutes=30) - (now - last)
            minutes = left.seconds // 60
            seconds = left.seconds % 60
            await msg.answer(f"⏳ Отдохни {minutes} мин. {seconds} сек.")
            return
         
            
            

    base = random.randint(1, 10)
    walked = base + lvl_dist
    distance += walked

    base_chance = 0.60
    luck_chance = min(0.40, lvl_luck * 0.02)
    find_chance = base_chance + luck_chance

    found = None
    if random.random() < find_chance:
        found = roll_item(bonus_chance=lvl_luck * 0.10)

    new_inv = inventory
    if found:
        new_inv = inventory + f"{found[0]}|{found[3]};"
    update_player(user_id, distance, balance, now.isoformat(), new_inv, lvl_dist, lvl_luck, last_daily)

    text = f"🚶 Ты прошёл <b>{walked} км</b> (+{lvl_dist} от скорости).\n\n"
    if found:
        text += f"✨ <b>Находка!</b>\n{found[0]} — {found[1]}\n💰 Стоимость: <b>{found[3]}</b>"
    else:
        text += "Ничего не нашёл. В другой раз повезёт!"

    text += f"\n\n📍 Всего: <b>{distance} км</b>"
    await msg.answer(text, parse_mode="HTML")

# ============ СТАТИСТИКА ============
@dp.message(Command("stats"))
async def stats(msg: Message):
    user_id = msg.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id, msg.from_user.username)

    items = [x for x in inventory.split(";") if x]
    total_value = 0
    rarity_count = {}
    for item_str in items:
        name, price = item_str.rsplit("|", 1)
        total_value += int(price)
        for it in ITEMS:
            if it[0] == name:
                rarity_count[it[1]] = rarity_count.get(it[1], 0) + 1
                break

    text = (
        f"📊 <b>Статистика</b>\n\n"
        f"🛣 Пройдено: <b>{distance} км</b>\n"
        f"💰 Баланс: <b>{balance}</b>\n"
        f"🎒 Предметов: <b>{len(items)}</b>\n"
        f"💎 Стоимость сумки: <b>{total_value}</b>\n\n"
        f"<b>Улучшения:</b>\n"
        f"👟 Скорость: ур. {lvl_dist} (+{lvl_dist} км)\n"
        f"🍀 Удача: ур. {lvl_luck} (+{lvl_luck*2}% шанс)\n\n"
    )
    if rarity_count:
        text += "<b>По редкости:</b>\n"
        for r, c in rarity_count.items():
            text += f"{r}: {c}\n"

    await msg.answer(text, parse_mode="HTML")

# ============ ИНВЕНТАРЬ ============
@dp.message(Command("inventory"))
async def inventory(msg: Message):
    user_id = msg.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id)
    items = [x for x in inventory.split(";") if x]

    if not items:
        await msg.answer("🎒 Инвентарь пуст. Иди /walk")
        return

    grouped = {}
    for item_str in items:
        name, price = item_str.rsplit("|", 1)
        grouped[name] = grouped.get(name, 0) + 1

    text = "🎒 <b>Инвентарь:</b>\n\n"
    for name, count in grouped.items():
        text += f"• {name} ×{count}\n"
    text += "\n💰 Продать: /sell"

    await msg.answer(text, parse_mode="HTML")

# ============ ПРОДАЖА ============
@dp.message(Command("sell"))
async def sell(msg: Message):
    user_id = msg.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id)
    items = [x for x in inventory.split(";") if x]

    if not items:
        await msg.answer("Нечего продавать.")
        return

    total = 0
    for item_str in items:
        name, price = item_str.rsplit("|", 1)
        total += int(price)

    balance += total
    update_player(user_id, distance, balance, last_walk, "", lvl_dist, lvl_luck, last_daily)

    await msg.answer(f"💰 Продано {len(items)} предметов за <b>{total}</b>.\nБаланс: <b>{balance}</b>", parse_mode="HTML")

# ============ МАГАЗИН ============
@dp.message(Command("shop"))
async def shop(msg: Message):
    user_id = msg.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id, msg.from_user.username)

    text = f"🛒 <b>Магазин улучшений</b>\n💰 Твой баланс: <b>{balance}</b>\n\n"

    kb_buttons = []
    for key, u in UPGRADES.items():
        lvl = lvl_dist if key == "distance" else lvl_luck
        if lvl >= u["max_lvl"]:
            text += f"{u['name']} — <b>МАКС</b> (ур. {lvl})\n{u['desc']}\n\n"
        else:
            price = upgrade_price(key, lvl)
            text += f"{u['name']} — ур. {lvl}/{u['max_lvl']}\n{u['desc']}\nЦена: <b>{price}</b>\n\n"
            kb_buttons.append([InlineKeyboardButton(
                text=f"Купить {u['name']} за {price}",
                callback_data=f"buy_{key}"
            )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons) if kb_buttons else None
    await msg.answer(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def buy_upgrade(callback: CallbackQuery):
    key = callback.data.split("_")[1]
    user_id = callback.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id, callback.from_user.username)

    u = UPGRADES[key]
    lvl = lvl_dist if key == "distance" else lvl_luck

    if lvl >= u["max_lvl"]:
        await callback.answer("Уже максимум!", show_alert=True)
        return

    price = upgrade_price(key, lvl)
    if balance < price:
        await callback.answer(f"Не хватает {price - balance} монет!", show_alert=True)
        return

    balance -= price
    if key == "distance":
        lvl_dist += 1
    else:
        lvl_luck += 1
    update_player(user_id, distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily)

    await callback.answer(f"✅ Куплено! Уровень {lvl+1}", show_alert=True)
    await callback.message.delete()
    await shop(callback.message)

# ============ ЛИДЕРБОРД ============
@dp.message(Command("top"))
async def top(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛣 По расстоянию", callback_data="top_dist")],
        [InlineKeyboardButton(text="💰 По балансу", callback_data="top_bal")],
        [InlineKeyboardButton(text="🎒 По стоимости сумки", callback_data="top_inv")],
    ])
    await msg.answer("🏆 <b>Лидерборд</b>\nВыбери категорию:", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.startswith("top_"))
async def top_category(callback: CallbackQuery):
    cat = callback.data.split("_")[1]

    cur.execute("SELECT user_id, username, distance, balance, inventory FROM players")
    rows = cur.fetchall()

    players = []
    for uid, uname, dist, bal, inv in rows:
        items = [x for x in inv.split(";") if x] if inv else []
        inv_val = sum(int(x.rsplit("|", 1)[1]) for x in items)
        name = f"@{uname}" if uname else f"id{uid}"
        players.append((name, dist, bal, inv_val))

    if cat == "dist":
        players.sort(key=lambda x: x[1], reverse=True)
        title = "🛣 Топ по расстоянию"
        value_idx = 1
        suffix = " км"
    elif cat == "bal":
        players.sort(key=lambda x: x[2], reverse=True)
        title = "💰 Топ по балансу"
        value_idx = 2
        suffix = ""
    else:
        players.sort(key=lambda x: x[3], reverse=True)
        title = "🎒 Топ по стоимости сумки"
        value_idx = 3
        suffix = ""

    text = f"🏆 <b>{title}</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players[:15]):
        prefix = medals[i] if i < 3 else f"{i+1}."
        text += f"{prefix} {p[0]} — {p[value_idx]}{suffix}\n"

    if not players:
        text += "Пока никто не играл."

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛣 По расстоянию", callback_data="top_dist")],
        [InlineKeyboardButton(text="💰 По балансу", callback_data="top_bal")],
        [InlineKeyboardButton(text="🎒 По стоимости сумки", callback_data="top_inv")],
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

# ============ ЕЖЕДНЕВНАЯ НАГРАДА ============
@dp.message(Command("daily"))
async def daily(msg: Message):
    user_id = msg.from_user.id
    distance, balance, last_walk, inventory, lvl_dist, lvl_luck, last_daily = get_player(user_id, msg.from_user.username)

    now = datetime.now()

    if last_daily:
        last = datetime.fromisoformat(last_daily)
        delta = now - last
        if delta < timedelta(hours=24):
            left = timedelta(hours=24) - delta
            hours = left.seconds // 3600
            minutes = (left.seconds % 3600) // 60
            seconds = left.seconds % 60
            await msg.answer(
                f"⏳ Ты уже получал награду сегодня.\n"
                f"Следующая через: <b>{hours}ч {minutes}м {seconds}с</b>",
                parse_mode="HTML"
            )
            return

    reward = random.randint(5, 75)

    if lvl_luck > 0 and random.random() < lvl_luck * 0.02:
        bonus = random.randint(10, 50)
        reward += bonus
        bonus_text = f"\n🍀 <b>Бонус удачи!</b> +{bonus} монет"
    else:
        bonus_text = ""

    balance += reward
    update_player(user_id, distance, balance, last_walk, inventory, lvl_dist, lvl_luck, now.isoformat())

    await msg.answer(
        f"🎁 <b>Ежедневная награда!</b>\n\n"
        f"💰 Ты получил: <b>{reward}</b> монет{bonus_text}\n"
        f"💳 Новый баланс: <b>{balance}</b>\n\n"
        f"Возвращайся через 24 часа!",
        parse_mode="HTML"
    )

# ============ ЗАПУСК ============
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
