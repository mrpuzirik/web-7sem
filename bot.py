"""Telegram-бот з меню: Студент / IT-технології / Контакти / Prompt AI (Groq)."""

import asyncio
import html
import logging
import os

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

STUDENT_NAME = os.getenv("STUDENT_NAME", "Прізвище Імʼя По батькові")
STUDENT_GROUP = os.getenv("STUDENT_GROUP", "Група")
STUDENT_INFO = os.getenv("STUDENT_INFO", "Спеціальність / курс / університет")
CONTACT_PHONE = os.getenv("CONTACT_PHONE", "+380 00 000 00 00")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "example@email.com")

SYSTEM_PROMPT = (
    "Ти — корисний AI-асистент у Telegram-боті. "
    "Відповідай українською, чітко і по суті, якщо користувач не просить іншої мови."
)

BTN_STUDENT = "👨‍🎓 Студент"
BTN_IT = "💻 IT-технології"
BTN_CONTACTS = "📞 Контакти"
BTN_AI = "🤖 Prompt AI"
BTN_BACK = "⬅️ Назад до меню"

IT_TOPICS = {
    "python": (
        "🐍 Python",
        "Мова програмування загального призначення з простим синтаксисом. "
        "Використовується у веб-розробці (Django, FastAPI), аналізі даних, "
        "автоматизації, машинному навчанні та створенні ботів.",
    ),
    "ai": (
        "🧠 Штучний інтелект",
        "Напрям, у якому комп'ютерні системи виконують задачі, що потребують "
        "інтелекту: розпізнавання мови й зображень, генерація тексту, рекомендації. "
        "Ключові технології: нейронні мережі, великі мовні моделі (LLM), "
        "промпт-інжиніринг.",
    ),
    "cloud": (
        "☁️ Хмарні технології",
        "Надання обчислювальних ресурсів, сховищ і сервісів через інтернет за "
        "потребою. Провайдери: AWS, Google Cloud, Microsoft Azure. "
        "Моделі: IaaS, PaaS, SaaS.",
    ),
    "web": (
        "🌐 Веб-технології",
        "HTML, CSS і JavaScript формують клієнтську частину сайтів, а серверна "
        "частина будується на Python, Node.js, PHP та інших. Сучасні підходи: "
        "REST API, SPA, PWA.",
    ),
    "devops": (
        "⚙️ DevOps",
        "Практики об'єднання розробки та експлуатації: Git, CI/CD, Docker, "
        "Kubernetes, моніторинг. Мета — швидко й надійно доставляти зміни в продакшн.",
    ),
}


class AIState(StatesGroup):
    waiting_prompt = State()


router = Router()


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_STUDENT), KeyboardButton(text=BTN_IT)],
            [KeyboardButton(text=BTN_CONTACTS), KeyboardButton(text=BTN_AI)],
        ],
        resize_keyboard=True,
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_BACK)]], resize_keyboard=True
    )


def it_topics_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"it:{key}")]
        for key, (title, _) in IT_TOPICS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def it_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ До тем", callback_data="it:list")]]
    )


FALLBACK_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.1-8b-instant"]


async def ask_groq(prompt: str) -> str:
    """Пробує GROQ_MODEL, а якщо модель недоступна (404) — резервні моделі."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    candidates = [GROQ_MODEL] + [m for m in FALLBACK_MODELS if m != GROQ_MODEL]
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for model in candidates:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
            }
            if model.startswith("openai/gpt-oss"):
                payload["reasoning_effort"] = "low"  # менше токенів на «роздуми»

            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 404:
                    logging.warning("Модель %s недоступна, пробую наступну", model)
                    continue
                if resp.status != 200:
                    body = await resp.text()
                    logging.error("Groq error %s: %s", resp.status, body)
                    raise RuntimeError(f"Groq API status {resp.status}")
                data = await resp.json()
                text = (data["choices"][0]["message"].get("content") or "").strip()
                return text or "Модель повернула порожню відповідь. Спробуйте ще раз."

    raise RuntimeError("Жодна з моделей Groq недоступна для цього ключа")


def split_text(text: str, limit: int = 4000) -> list[str]:
    """Telegram приймає до 4096 символів у одному повідомленні."""
    return [text[i : i + limit] for i in range(0, len(text), limit)] or [""]


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    name = html.escape(message.from_user.first_name or "друже")
    await message.answer(
        f"Привіт, <b>{name}</b>! 👋\nОберіть розділ у меню нижче.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_BACK)
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Головне меню:", reply_markup=main_menu())


@router.message(F.text == BTN_STUDENT)
async def student(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👨‍🎓 <b>Студент</b>\n\n"
        f"<b>Прізвище:</b> {html.escape(STUDENT_NAME)}\n"
        f"<b>Група:</b> {html.escape(STUDENT_GROUP)}\n"
        f"{html.escape(STUDENT_INFO)}",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_IT)
async def it_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "💻 <b>IT-технології</b>\nОберіть тему:",
        parse_mode="HTML",
        reply_markup=it_topics_kb(),
    )


@router.callback_query(F.data.startswith("it:"))
async def it_callback(call: CallbackQuery):
    key = call.data.split(":", 1)[1]
    if key == "list":
        await call.message.edit_text(
            "💻 <b>IT-технології</b>\nОберіть тему:",
            parse_mode="HTML",
            reply_markup=it_topics_kb(),
        )
    elif key in IT_TOPICS:
        title, text = IT_TOPICS[key]
        await call.message.edit_text(
            f"<b>{title}</b>\n\n{text}",
            parse_mode="HTML",
            reply_markup=it_back_kb(),
        )
    await call.answer()


@router.message(F.text == BTN_CONTACTS)
async def contacts(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📞 <b>Контакти</b>\n\n"
        f"<b>Телефон:</b> {html.escape(CONTACT_PHONE)}\n"
        f"<b>E-mail:</b> {html.escape(CONTACT_EMAIL)}",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_AI)
async def ai_start(message: Message, state: FSMContext):
    await state.set_state(AIState.waiting_prompt)
    await message.answer(
        "🤖 <b>Prompt AI</b>\n\nНадішліть будь-який запит — і я передам його "
        "AI-моделі. Щоб вийти, натисніть «Назад до меню».",
        parse_mode="HTML",
        reply_markup=back_menu(),
    )


@router.message(AIState.waiting_prompt, F.text)
async def ai_answer(message: Message):
    if not GROQ_API_KEY:
        await message.answer("⚠️ Не налаштовано GROQ_API_KEY.")
        return
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    try:
        answer = await ask_groq(message.text)
    except Exception:
        logging.exception("AI request failed")
        await message.answer("⚠️ Не вдалося отримати відповідь від AI. Спробуйте пізніше.")
        return
    for chunk in split_text(answer):
        # parse_mode=None — щоб спецсимволи у відповіді моделі не ламали розмітку
        await message.answer(chunk, parse_mode=None)


@router.message(AIState.waiting_prompt)
async def ai_non_text(message: Message):
    await message.answer("Будь ласка, надішліть текстовий запит.")


@router.message()
async def fallback(message: Message):
    await message.answer("Оберіть пункт у меню 👇", reply_markup=main_menu())


async def start_web_server():
    """Мінімальний HTTP-сервер: потрібен хмарним сервісам (Render та ін.),
    які очікують, що застосунок слухає порт PORT."""
    port = os.getenv("PORT")
    if not port:
        return
    app = web.Application()
    app.router.add_get("/", lambda _: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(port)).start()
    logging.info("Health server on port %s", port)


async def main():
    if not BOT_TOKEN:
        raise SystemExit("Не задано BOT_TOKEN")
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())