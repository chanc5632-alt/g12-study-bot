import asyncio
import logging
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

subjects = {
    "English": {
        "vocab": [
            ("abundant", "plentiful"),
            ("brief", "short"),
            ("accurate", "correct"),
            ("effort", "hard work"),
            ("advice", "suggestion"),
        ],
        "quiz": [
            {
                "q": "Choose the correct word: She gave me good ____.",
                "options": ["advice", "advise", "adviced", "advising"],
                "answer": "advice",
            },
            {
                "q": "Synonym of 'brief'?",
                "options": ["short", "long", "slow", "big"],
                "answer": "short",
            },
        ],
    },
    "Math": {
        "vocab": [
            ("Area of a rectangle", "length x width"),
            ("Triangle angle sum", "180 degrees"),
            ("Perimeter", "total boundary length"),
            ("Square of 5", "25"),
            ("Pi", "3.14159"),
        ],
        "quiz": [
            {
                "q": "What is 7 x 8?",
                "options": ["54", "56", "58", "48"],
                "answer": "56",
            },
            {
                "q": "Triangle angle sum is?",
                "options": ["90", "180", "270", "360"],
                "answer": "180",
            },
        ],
    },
    "Physics": {
        "vocab": [
            ("Speed", "distance / time"),
            ("Acceleration", "change of velocity / time"),
            ("Force", "mass x acceleration"),
            ("Work", "force x distance"),
            ("Power", "work / time"),
        ],
        "quiz": [
            {
                "q": "Formula of force?",
                "options": ["m/v", "m x a", "v/t", "d/t"],
                "answer": "m x a",
            },
            {
                "q": "Unit of force?",
                "options": ["Watt", "Newton", "Joule", "Volt"],
                "answer": "Newton",
            },
        ],
    },
    "Chemistry": {
        "vocab": [
            ("Atom", "smallest unit of element"),
            ("Molecule", "two or more atoms"),
            ("Acid", "donates H+"),
            ("Base", "accepts H+"),
            ("pH", "acidity scale"),
        ],
        "quiz": [
            {
                "q": "pH of neutral water?",
                "options": ["7", "1", "14", "0"],
                "answer": "7",
            },
            {
                "q": "Smallest unit of an element?",
                "options": ["Atom", "Ion", "Compound", "Molecule"],
                "answer": "Atom",
            },
        ],
    },
    "Biology": {
        "vocab": [
            ("Cell", "basic unit of life"),
            ("Tissue", "group of cells"),
            ("Organ", "group of tissues"),
            ("Photosynthesis", "food making process"),
            ("Respiration", "energy releasing process"),
        ],
        "quiz": [
            {
                "q": "Basic unit of life?",
                "options": ["Cell", "Organ", "Tissue", "System"],
                "answer": "Cell",
            },
            {
                "q": "Food-making process in plants?",
                "options": ["Respiration", "Photosynthesis", "Digestion", "Transpiration"],
                "answer": "Photosynthesis",
            },
        ],
    },
}

user_state = {}


def main_menu():
    kb = InlineKeyboardBuilder()
    for s in subjects.keys():
        kb.button(text=s, callback_data=f"subject:{s}")
    kb.button(text="📌 Reminder", callback_data="reminder")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def subject_menu(subject):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎴 Flashcard", callback_data=f"flash:{subject}")
    kb.button(text="📝 Quiz", callback_data=f"quiz:{subject}")
    kb.button(text="🔙 Back", callback_data="back")
    kb.adjust(2, 1)
    return kb.as_markup()


def quiz_keyboard(subject, options):
    kb = InlineKeyboardBuilder()
    for opt in options:
        kb.button(text=opt, callback_data=f"ans:{subject}:{opt}")
    kb.adjust(2)
    return kb.as_markup()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "မင်္ဂလာပါ။ G12 study bot ပါ။
Subject ရွေးပြီး flashcard, quiz, reminder သုံးနိုင်ပါတယ်။",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "/start - bot စတင်ရန်
"
        "/help - အသုံးပြုပုံ
"
        "/quiz - random quiz
"
        "/flash - random flashcard
"
        "/remind - reminder set"
    )


@dp.message(Command("quiz"))
async def random_quiz(message: Message):
    subject = random.choice(list(subjects.keys()))
    q = random.choice(subjects[subject]["quiz"])
    user_state[message.from_user.id] = {"mode": "quiz", "subject": subject, "q": q}
    await message.answer(f"[{subject}] {q['q']}", reply_markup=quiz_keyboard(subject, q["options"]))


@dp.message(Command("flash"))
async def random_flash(message: Message):
    subject = random.choice(list(subjects.keys()))
    term, meaning = random.choice(subjects[subject]["vocab"])
    await message.answer(f"[{subject}] {term}
= {meaning}")


@dp.message(Command("remind"))
async def remind_cmd(message: Message):
    await message.answer("Reminder format:
/reminder YYYY-MM-DD HH:MM message")


@dp.message(Command("reminder"))
async def reminder_set(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Format မမှန်ပါ။
ဥပမာ: /reminder 2026-07-26 19:00 Physics revision")
        return
    try:
        dt = datetime.strptime(parts[1] + " " + parts[2], "%Y-%m-%d %H:%M")
        note = parts[3]
        delay = (dt - datetime.now()).total_seconds()
        if delay <= 0:
            await message.answer("Future time တစ်ခုထည့်ပါ။")
            return
        await message.answer(f"Reminder set: {dt.strftime('%Y-%m-%d %H:%M')}")

        async def job():
            await asyncio.sleep(delay)
            await bot.send_message(message.chat.id, f"⏰ Reminder: {note}")

        asyncio.create_task(job())
    except Exception:
        await message.answer("Date/time format မှန်အောင်ထည့်ပါ။")


@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.message.edit_text("Subject ရွေးပါ။", reply_markup=main_menu())
    await call.answer()


@dp.callback_query(F.data == "reminder")
async def reminder_menu(call: CallbackQuery):
    await call.message.edit_text(
        "Reminder format:
/reminder YYYY-MM-DD HH:MM message",
        reply_markup=main_menu(),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("subject:"))
async def choose_subject(call: CallbackQuery):
    subject = call.data.split(":", 1)[1]
    await call.message.edit_text(f"{subject} ကိုရွေးထားပါတယ်။", reply_markup=subject_menu(subject))
    await call.answer()


@dp.callback_query(F.data.startswith("flash:"))
async def flashcard(call: CallbackQuery):
    subject = call.data.split(":", 1)[1]
    term, meaning = random.choice(subjects[subject]["vocab"])
    await call.message.answer(f"🎴 {subject} Flashcard

Term: {term}
Meaning: {meaning}", reply_markup=subject_menu(subject))
    await call.answer()


@dp.callback_query(F.data.startswith("quiz:"))
async def quiz(call: CallbackQuery):
    subject = call.data.split(":", 1)[1]
    q = random.choice(subjects[subject]["quiz"])
    user_state[call.from_user.id] = {"mode": "quiz", "subject": subject, "q": q}
    await call.message.answer(f"📝 {subject} Quiz

{q['q']}", reply_markup=quiz_keyboard(subject, q["options"]))
    await call.answer()


@dp.callback_query(F.data.startswith("ans:"))
async def answer(call: CallbackQuery):
    _, subject, picked = call.data.split(":", 2)
    state = user_state.get(call.from_user.id, {})
    q = state.get("q")
    if not q:
        await call.answer("Quiz state မတွေ့ပါ။", show_alert=True)
        return
    correct = q["answer"]
    if picked == correct:
        await call.message.answer("✅ မှန်ပါတယ်!")
    else:
        await call.message.answer(f"❌ မမှန်ပါ။ အဖြေမှန်: {correct}")
    await call.message.answer("နောက်တစ်ခုရွေးပါ။", reply_markup=subject_menu(subject))
    await call.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
