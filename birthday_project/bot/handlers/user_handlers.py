from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from birthday_project.bot.lexicon.lexicon import LEXICON
from birthday_project.bot.database.birthday_db import (
    get_or_create_profile_by_telegram_id,
    link_telegram,
    add_friend,
    get_friends,
    get_today_birthdays,
)

router = Router()

class AddFriendState(StatesGroup):
    name = State()
    birthday = State()

@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    args = message.text.split()
    if len(args) > 1:
        code = args[1]
        result = await link_telegram(code, message.from_user.id)
        if result is None:
            await message.answer(LEXICON["unknown_code"])
        elif result == "already_linked":
            await message.answer(LEXICON["already_linked"])
        else:
            await message.answer(LEXICON["linked"])
    else:
        await message.answer(LEXICON["start"])

@router.message(Command("help"))
async def help_cmd(message: types.Message, state: FSMContext):
    await message.answer(LEXICON["help"])

@router.message(Command("add"))
async def add_cmd(message: types.Message, state: FSMContext):
    await state.set_state(AddFriendState.name)
    await message.answer("Введите имя друга:")

@router.message(AddFriendState.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(friend_name=message.text.strip())
    await state.set_state(AddFriendState.birthday)
    await message.answer("Введите дату рождения друга в формате ГГГГ-ММ-ДД:")

@router.message(AddFriendState.birthday)
async def process_birthday(message: types.Message, state: FSMContext):
    from datetime import datetime
    data = await state.get_data()
    name = data.get("friend_name")
    try:
        birthday = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
    except Exception:
        await message.answer("Ошибка! Введите дату в формате ГГГГ-ММ-ДД.")
        return
    profile = await get_or_create_profile_by_telegram_id(message.from_user.id)
    await add_friend(profile, name, birthday)
    await message.answer("Друг добавлен!")
    await state.clear()

@router.message(Command("friends"))
async def friends_cmd(message: types.Message, state: FSMContext):
    profile = await get_or_create_profile_by_telegram_id(message.from_user.id)
    friends = await get_friends(profile)
    if not friends:
        await message.answer(LEXICON["no_friends"])
    else:
        text = "\n".join([f"{f.name} — {f.birthday.strftime('%d.%m')}" for f in friends])
        await message.answer(LEXICON["list_friends"] + text)

@router.message(Command("today"))
async def today_cmd(message: types.Message, state: FSMContext):
    profile = await get_or_create_profile_by_telegram_id(message.from_user.id)
    birthdays = await get_today_birthdays(profile)
    if not birthdays:
        await message.answer(LEXICON["no_birthdays_today"])
    else:
        text = "\n".join([f"{f.name} — {f.birthday.strftime('%Y-%m-%d')}" for f in birthdays])
        await message.answer(LEXICON["birthdays_today"] + text)