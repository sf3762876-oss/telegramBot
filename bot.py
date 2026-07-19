import asyncio
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8732981892:AAGYHoCOoC7ySdyg-51dnT5Fq8PIt1xHH4I"

bot = Bot(token=TOKEN)
dp = Dispatcher()

db = sqlite3.connect("players.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players(
    tg_id INTEGER PRIMARY KEY,
    nickname TEXT UNIQUE,
    bio TEXT DEFAULT ''
)
""")
db.commit()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Команды:\n"
        "/setnick <ник> - установить ник Minecraft\n"
        "/setbio <описание> - установить описание\n"
        "/nimi <ник> - посмотреть описание игрока"
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer("📚 Команды:\n/start\n/help\n/rules\n/players\n/setnick <ник>\n/setbio <описание>\n/nimi <ник>")

@dp.message(Command("rules"))
async def rules(message: Message):
    await message.answer("📜 Правила сервера:\n1. Не использовать читы.\n2. Не гриферить.\n3. Не оскорблять игроков.\n4. Не использовать баги.\n5. Уважать администрацию.")

@dp.message(Command("players"))
async def players(message: Message):
    cur.execute("SELECT nickname FROM players ORDER BY nickname")
    rows=cur.fetchall()
    if not rows:
        await message.answer("❌ Пока нет зарегистрированных игроков.")
        return
    await message.answer("👥 Игроки:\n"+"\n".join(f"{i+1}. {r[0]}" for i,r in enumerate(rows)))

@dp.message(Command("setnick"))
async def setnick(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/setnick ВашНик")
        return

    nick = args[1]

    cur.execute("SELECT bio FROM players WHERE tg_id=?", (message.from_user.id,))
    row = cur.fetchone()
    bio = row[0] if row else ""

    cur.execute("""
    INSERT INTO players(tg_id, nickname, bio)
    VALUES(?,?,?)
    ON CONFLICT(tg_id)
    DO UPDATE SET nickname=excluded.nickname
    """, (message.from_user.id, nick, bio))

    db.commit()

    await message.answer(f"✅ Ник сохранён: {nick}")

@dp.message(Command("setbio"))
async def setbio(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/setbio Ваше описание")
        return

    bio = args[1]

    cur.execute("SELECT nickname FROM players WHERE tg_id=?", (message.from_user.id,))
    row = cur.fetchone()

    if not row:
        await message.answer("❌ Сначала укажите ник:\n/setnick ВашНик")
        return

    nick = row[0]

    cur.execute("""
    UPDATE players
    SET bio=?
    WHERE tg_id=?
    """, (bio, message.from_user.id))

    db.commit()

    await message.answer(f"✅ Описание для {nick} сохранено!")

@dp.message(Command("nimi"))
async def nimi(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("Использование:\n/nimi Ник")
        return

    nick = args[1]

    cur.execute("SELECT bio FROM players WHERE nickname=?", (nick,))
    row = cur.fetchone()

    if row:
        await message.answer(
            f"📜 Информация об игроке {nick}\n\n"
            f"{row[0]}"
        )
    else:
        await message.answer("❌ Игрок не найден.")

async def main():
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())