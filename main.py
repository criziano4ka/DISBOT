import disnake
from disnake.ext import commands
import random
import asyncio
import math
import aiohttp
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL)""")
conn.commit()

intents = disnake.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = 'MTA5MTk3NjI2NjkwNDc2ODYxMg.Gire-N.I03cEpNrlNNcAWzjqOVhhEjelN4sCZffJiov7A'


@bot.event
async def on_ready():
    print(f"{bot.user.name} готов к использованию!")


@bot.slash_command()
async def список_команд(ctx):
    f = list(map(lambda x: x.strip(), open('function_list.txt', encoding='utf-8').readlines()))
    embed = disnake.Embed(title='функции бота:', description="\n".join(f), color=disnake.Color.blue())
    msg = await ctx.send(embed=embed)
    await ctx.channel.fetch_message(msg.id)\



@bot.slash_command()
async def чит_код(ctx, код: str, участник: disnake.Member = None):
    code = '021206'
    if code == код:
        await участник.add_roles('админ')



# Повторяет сообщение, отправленное пользователем
@bot.slash_command()
async def echo(ctx, *, сообщение=None):
    if сообщение is None:
        await ctx.send("пустоооооо...")
    else:
        await ctx.send(сообщение)


# Выводит информацию о пользователе: ник, ID, роли и дату присоединения
@bot.slash_command()
async def user_info(ctx, участник: disnake.Member = None):
    if not участник:
        участник = ctx.author

    roles = []
    for role in участник.roles:
        if role != ctx.guild.default_role:
            roles.append(role.name)
    if roles:
        roles_str = ", ".join(roles)
    else:
        roles_str = "No roles"

    embed = disnake.Embed(title=f"Информация о {участник.name}", color=участник.color)
    embed.add_field(name="Основной ник", value=участник.name, inline=True)
    embed.add_field(name="ID", value=участник.id, inline=True)
    embed.add_field(name="Ник на сервере", value=участник.nick, inline=True)
    embed.add_field(name="Роли", value=roles_str, inline=True)
    embed.add_field(name="Присоединился", value=участник.joined_at.strftime("%d-%m-%Y"), inline=True)
    embed.set_thumbnail(url=участник.avatar.url)

    await ctx.send(embed=embed)


# Выбирает случайно между орлом и решкой
@bot.slash_command()
async def coin_flip(ctx):
    coin_sides = ['Решка', 'Орёл']
    win = random.choice(coin_sides)
    if win == 'Орёл':
        await ctx.send(f"Выпал {win}!")
    else:
        await ctx.send(f"Выпала {win}!")


# Бросает кость с заданным количеством граней и выводит результат
@bot.slash_command()
async def dice(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("Нужно хотя бы 2 грани.")
    else:
        result = random.randint(1, sides)
        await ctx.send(f"Выпало {result}")


# Отправляет аватар пользователя
@bot.slash_command()
async def avatar(ctx, участник: disnake.Member = None):
    if not участник:
        участник = ctx.author

    embed = disnake.Embed(title=f"Аватар {участник.name}", color=disnake.Color.blue())
    embed.set_image(url=участник.avatar.url)

    await ctx.send(embed=embed)


# Отправляет информацию о сервере: ID, владелец, регион, дата создания, количество участников и каналов
@bot.slash_command()
async def server_info(ctx):
    guild = ctx.guild

    embed = disnake.Embed(title=f"{guild.name} Server Information", color=disnake.Color.blue())
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Владелец", value=guild.owner, inline=True)
    embed.add_field(name="Регион", value=guild.region, inline=True)
    embed.add_field(name="Дата создания", value=guild.created_at.strftime("%d-%m-%Y"), inline=True)
    embed.add_field(name="Количество участников", value=guild.member_count, inline=True)
    embed.add_field(name="Текстовые каналы", value=len(guild.text_channels), inline=True)
    embed.add_field(name="Голосовые каналы", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="Роли", value=len(guild.roles), inline=True)
    embed.set_thumbnail(url=guild.icon.url)

    await ctx.send(embed=embed)


# Удаляет указанное количество сообщений (по умолчанию 5)
@bot.slash_command()
async def clear_messages(ctx, amount: int = 5):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Было удалено {amount} сообщений!", delete_after=5)
    else:
        await ctx.send("У вас нет доступа к этой команде.")


# Кикает указанного участника с указанной причиной
@bot.slash_command()
async def kick(ctx, участник: disnake.Member, *, причина=None):
    if ctx.author.guild_permissions.kick_members:
        await участник.kick(reason=причина)
        await ctx.send(f"{участник.name} был выгнан по причине: {причина}.")

    else:
        await ctx.send("У вас нет доступа к этой команде.")


# Банит указанного участника с указанной причиной
@bot.slash_command()
async def ban(ctx, участник: disnake.Member, *, причина=None):
    if ctx.author.guild_permissions.ban_members:
        await участник.ban(reason=причина)
        await ctx.send(f"{участник.name} был забанен по причине: {причина}.")
    else:
        await ctx.send("У вас нет доступа к этой команде.")


# Разбанивает указанного участника
@bot.slash_command()
async def unban(ctx, *, участник):
    if ctx.author.guild_permissions.ban_members:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = участник.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.name} был разбанен.")
                return

        await ctx.send("Пользователь не найден.")
    else:
        await ctx.send("У вас нет доступа к этой команде.")


# Создает опрос с указанными вариантами ответов
@bot.command()
async def poll(ctx, вопрос, *варианты):
    if len(варианты) > 10:
        await ctx.send("Не более 10 вариантов.")
        return

    emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    option_list = [f"{emoji_list[i]} {option}" for i, option in enumerate(варианты)]

    embed = disnake.Embed(title=вопрос, description="\n".join(option_list), color=disnake.Color.blue())
    poll_msg = await ctx.send(embed=embed)

    for emoji in emoji_list[:len(варианты)]:
        await poll_msg.add_reaction(emoji)

    await asyncio.sleep(60)

    poll_msg = await ctx.channel.fetch_message(poll_msg.id)

    reactions = dict()
    for reaction in poll_msg.reactions:
        if reaction.emoji in emoji_list:
            reactions[reaction.emoji] = reaction.count

    winner_emoji = max(reactions, key=reactions.get)
    winner_index = emoji_list.index(winner_emoji)
    winner_option = варианты[winner_index]

    await ctx.send(f"Голосование окончено! Победил вариант {winner_option}.")


# Отправляет случайную шутку
@bot.slash_command()
async def joke(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.jokeapi.dev/joke/Any") as response:
            json_response = await response.json()
            if json_response['type'] == 'single':
                await ctx.send(json_response['joke'])
            else:
                await ctx.send(f"{json_response['setup']}... {json_response['delivery']}")


# Отправляет случайный факт
@bot.slash_command()
async def fact(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://uselessfacts.jsph.pl/random.json?language=ru") as response:
            if response.status == 200:
                json_response = await response.json()
                r_fact = json_response['text']
                await ctx.send(r_fact)
            else:
                await ctx.send("Попробуйте снова.")


# Складывает два числа
@bot.slash_command()
async def add(ctx, число1: int, число2: int):
    result = число1 + число2
    await ctx.send(f"{число1} + {число2} = {result}")


# Вычитает второе число из первого
@bot.slash_command()
async def subtract(ctx, число1: int, число2: int):
    result = число1 - число2
    await ctx.send(f"{число1} - {число2} = {result}")


# Умножает два числа
@bot.slash_command()
async def multiply(ctx, число1: int, число2: int):
    result = число1 * число2
    await ctx.send(f"{число1} * {число2} = {result}")


# Делит первое число на второе
@bot.slash_command()
async def divide(ctx, число1: int, число2: int):
    if число2 == 0:
        await ctx.send("Ай, ай. Делить на 0 нельзя!")
    else:
        result = число1 / число2
        await ctx.send(f"{число1} / {число2} = {result}")


# Вычисляет квадратный корень числа
@bot.slash_command()
async def sqrt(ctx, число: float):
    if число < 0:
        await ctx.send("Число должно быть положительным.")
    else:
        result = math.sqrt(число)
        await ctx.send(f"Корень из числа {число} = {result}.")


# Ожидает заданное количество времени и отправляет сообщение
@bot.slash_command()
async def reminder(ctx, время: int, *, сообщение: str):
    if время <= 0:
        await ctx.send("Введите время в секундах > 0.")
    else:
        await ctx.send(f"Напоминание даст о себе знать через {время} секунд.")
        await asyncio.sleep(время)
        await ctx.send(f"{ctx.author.mention}, ВАШЕ НАПОМИНАНИЕ: {сообщение}")


# Отправляет ссылку для приглашения бота на сервер
@bot.slash_command()
async def invite(ctx):
    invite_link = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot"
    await ctx.send(f"Вы можете пригласить бота по этой ссылке: {invite_link}")


# Выбирает случайный элемент из вариантов
@bot.command()
async def choose(ctx, *варианты):
    if len(варианты) < 2:
        await ctx.send("Приведите хотя бы 2 варианта.")
    else:
        selected = random.choice(варианты)
        await ctx.send(f"Я выбрал: {selected}")


# Ожидает заданное количество секунд и отправляет сообщение об окончании отсчета
@bot.slash_command()
async def countdown(ctx, секунды: int):
    if секунды <= 0:
        await ctx.send("Введите положительное количество секунд.")
    else:
        for i in range(секунды, 0, -1):
            await ctx.send(i)
            await asyncio.sleep(1)
        await ctx.send("Отсчет окончен!")


# Изменение статуса бота
@bot.slash_command()
async def setstatus(ctx, *, статус: str):
    if ctx.author.guild_permissions.manage_guild:
        await bot.change_presence(activity=disnake.Game(name=статус))
        await ctx.send(f"Статус бота поменялся на '{статус}'.")
    else:
        await ctx.send("У вас нет доступа к этой команде.")


# Верификация новичков
@bot.event
async def on_member_join(участник):
    guild = участник.guild
    welcome_role = "не верифицирован"
    welcome_channel = "верификация"
    male_emoji = "♂️"
    female_emoji = "♀️"
    verified_role = "верифицирован"
    male_role = "♂️"
    female_role = "♀️"

    unverified_role = disnake.utils.get(guild.roles, name=welcome_role)

    verified_role = disnake.utils.get(guild.roles, name=verified_role)

    male_role = disnake.utils.get(guild.roles, name=male_role)

    female_role = disnake.utils.get(guild.roles, name=female_role)

    welcome_channel = disnake.utils.get(guild.text_channels, name=welcome_channel)
    if welcome_channel:
        await участник.add_roles(unverified_role)
        message = await welcome_channel.send(
            f"Добро пожаловать, {участник.mention}! Для верификации, отреагируйте одним из этих эмодзи. "
            f"Выберите ваш пол, отреагировав на соответствующий эмодзи: {male_emoji} или {female_emoji}.")
        await message.add_reaction(male_emoji)
        await message.add_reaction(female_emoji)

        def check(reaction, user):
            return user == участник and reaction.message.id == message.id \
                   and str(reaction.emoji) in [male_emoji, female_emoji]

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=300.0, check=check)
        except asyncio.TimeoutError:
            await welcome_channel.send(f"{участник.mention}, вы не успели верифицироваться, попробуйте снова.")
        else:
            if str(reaction.emoji) == male_emoji:
                await участник.add_roles(male_role)
                gender = "мужской"
            elif str(reaction.emoji) == female_emoji:
                await участник.add_roles(female_role)
                gender = "женский"

            await участник.remove_roles(unverified_role)
            await участник.add_roles(verified_role)
            await welcome_channel.send(f"{участник.mention} был успешно верифицирован как {gender}!")

            cursor.execute("INSERT INTO users (id, name, gender) VALUES (?, ?, ?)",
                           (участник.id, участник.name, gender))
            conn.commit()


@bot.event
async def on_disconnect():
    conn.close()


bot.run(TOKEN)
