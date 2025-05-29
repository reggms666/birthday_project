from asgiref.sync import sync_to_async
from friends.models import Profile, Friend
from django.contrib.auth.models import User
import uuid

async def get_or_create_profile_by_telegram_id(telegram_id):
    # 1. Пытаемся найти профиль по telegram_id
    profile = await sync_to_async(Profile.objects.filter(telegram_id=telegram_id).first)()
    if profile:
        return profile

    # 2. Пытаемся найти пользователя по username (tguser_<telegram_id>)
    username = f"tguser_{telegram_id}"
    user = await sync_to_async(User.objects.filter(username=username).first)()
    if not user:
        user = await sync_to_async(User.objects.create_user)(
            username=username,
            password=User.objects.make_random_password()
        )

    # 3. Пытаемся найти профиль по этому пользователю
    profile = await sync_to_async(Profile.objects.filter(user=user).first)()
    if not profile:
        profile = await sync_to_async(Profile.objects.create)(
            user=user, telegram_id=telegram_id, telegram_code=uuid.uuid4().hex[:16]
        )
    else:
        profile.telegram_id = telegram_id
        await sync_to_async(profile.save)()

    return profile

async def link_telegram(telegram_code, telegram_id):
    # Найти профиль по коду
    profile = await sync_to_async(Profile.objects.filter(telegram_code=telegram_code).first)()
    if not profile:
        return None

    # Найти "ботовский" профиль по telegram_id (если он есть)
    bot_profile = await sync_to_async(Profile.objects.filter(telegram_id=telegram_id).exclude(id=profile.id).first)()

    # Если есть бот-профиль, переносим друзей
    if bot_profile:
        # Копируем всех друзей (без дублей по имени и дате)
        friends_to_move = await sync_to_async(list)(Friend.objects.filter(profile=bot_profile))
        existing_friends = await sync_to_async(list)(Friend.objects.filter(profile=profile))
        for f in friends_to_move:
            if not any(f2.name == f.name and f2.birthday == f.birthday for f2 in existing_friends):
                f.profile = profile
                await sync_to_async(f.save)()
            else:
                await sync_to_async(f.delete)()
        # Удаляем bot_profile (или отвязываем telegram_id)
        bot_profile.telegram_id = None
        await sync_to_async(bot_profile.save)()

    # Привязываем telegram_id к основному профилю
    profile.telegram_id = telegram_id
    await sync_to_async(profile.save)()
    return profile

async def add_friend(profile, name, birthday):
    friend = await sync_to_async(Friend.objects.create)(profile=profile, name=name, birthday=birthday)
    return friend

async def get_friends(profile):
    return await sync_to_async(list)(Friend.objects.filter(profile=profile))

async def get_today_birthdays(profile):
    from datetime import date
    today = date.today()
    return await sync_to_async(list)(
        Friend.objects.filter(profile=profile, birthday__month=today.month, birthday__day=today.day)
    )