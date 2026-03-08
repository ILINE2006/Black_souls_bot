import disnake
from disnake.ext import commands
import datetime
import io
from PIL import Image, ImageDraw, ImageFont

# Настройка намерений
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.InteractionBot(intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} успешно запущен и готов рисовать карточки!')


# ==========================================
# 👋 ПРИВЕТСТВИЕ (РИСУЕМ КАРТИНКУ)
# ==========================================
@bot.event
async def on_member_join(member: disnake.Member):
    # ВНИМАНИЕ: Замени цифры на ID твоего канала, куда бот будет писать приветствия!
    channel_id = 1383888441955188786
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    try:
        # Открываем фон
        background = Image.open("img/db.jpg").convert("RGBA")
        background = background.resize((800, 300))  # Подгоняем размер

        # Скачиваем аватарку
        avatar_asset = member.display_avatar.with_size(128)
        avatar_data = await avatar_asset.read()
        avatar = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        avatar = avatar.resize((150, 150))

        # Делаем аватарку круглой!
        mask = Image.new('L', (150, 150), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 150, 150), fill=255)

        # Накладываем круглую аватарку на фон (отступ 50 слева, 75 сверху)
        background.paste(avatar, (50, 75), mask)

        # Подключаем шрифт
        font_big = ImageFont.truetype("downcome.otf", 50)
        font_small = ImageFont.truetype("downcome.otf", 30)
        draw = ImageDraw.Draw(background)

        # Рисуем текст
        draw.text((230, 90), "Добро пожаловать,", font=font_small, fill="white")
        draw.text((230, 130), f"{member.name}!", font=font_big, fill="white")
        draw.text((230, 200), f"Ты наш {len(member.guild.members)}-й участник!", font=font_small, fill="lightgray")

        # Сохраняем результат в память и отправляем
        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)

        file = disnake.File(fp=buffer, filename="welcome.png")
        await channel.send(content=f"Привет, {member.mention}!", file=file)

    except Exception as e:
        print(f"Ошибка при создании картинки приветствия: {e}")


# ==========================================
# 📇 КАРТОЧКА ПОЛЬЗОВАТЕЛЯ (РИСУЕМ КАРТИНКУ)
# ==========================================
@bot.slash_command(name="userinfo", description="Показать красивую нарисованную карточку пользователя")
async def userinfo(inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
    # Отправляем сообщение "Бот думает...", так как рисование занимает секунду
    await inter.response.defer()

    member = member or inter.author

    try:
        # ВОТ ТУТ ИСПРАВЛЕН ПУТЬ К КАРТИНКЕ ФОНА!
        background = Image.open("img/db.jpg").convert("RGBA")
        background = background.resize((800, 300))

        # Скачиваем аватарку
        avatar_asset = member.display_avatar.with_size(128)
        avatar_data = await avatar_asset.read()
        avatar = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        avatar = avatar.resize((150, 150))

        # Делаем круглую маску для аватарки
        mask = Image.new('L', (150, 150), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 150, 150), fill=255)

        background.paste(avatar, (50, 75), mask)

        # ВОТ ТУТ ИСПРАВЛЕНЫ ШРИФТЫ!
        font_name = ImageFont.truetype("downcome.otf", 45)
        font_info = ImageFont.truetype("downcome.otf", 25)
        draw = ImageDraw.Draw(background)

        # Рисуем текст (имя, роль, дата)
        draw.text((230, 80), f"{member.name}", font=font_name, fill="white")
        draw.text((230, 140), f"Роль: {member.top_role.name}", font=font_info, fill="cyan")

        join_date = member.joined_at.strftime("%d.%m.%Y")
        draw.text((230, 180), f"На сервере с: {join_date}", font=font_info, fill="lightgray")

        # Сохраняем и отправляем
        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)

        file = disnake.File(fp=buffer, filename="profile.png")
        await inter.edit_original_response(file=file)

    except Exception as e:
        await inter.edit_original_response(
            content=f"❌ Ошибка при генерации карточки. Ошибка: {e}")

# ==========================================
# 🛡️ ФИЛЬТР ССЫЛОК
# ==========================================
@bot.event
async def on_message(message: disnake.Message):
    if message.author.bot:
        return
    links = ["http://", "https://", "www.", "discord.gg/"]
    if any(link in message.content.lower() for link in links):
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            warning = await message.channel.send(f"{message.author.mention}, отправка ссылок запрещена!")
            await warning.delete(delay=5)


# ==========================================
# 🧹 ОЧИСТКА ЧАТА И МОДЕРАЦИЯ
# ==========================================
@bot.slash_command(name="clear", description="Очистить чат")
@commands.default_member_permissions(manage_messages=True)
async def clear(inter: disnake.ApplicationCommandInteraction, amount: int):
    deleted = await inter.channel.purge(limit=amount)
    await inter.response.send_message(f"✅ Удалено {len(deleted)} сообщений.", ephemeral=True)


@bot.slash_command(name="kick", description="Выгнать пользователя")
@commands.default_member_permissions(kick_members=True)
async def kick(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Не указана"):
    await member.kick(reason=reason)
    await inter.response.send_message(f"👢 {member.mention} был изгнан. Причина: {reason}")


@bot.slash_command(name="ban", description="Забанить пользователя")
@commands.default_member_permissions(ban_members=True)
async def ban(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await inter.response.send_message(f"🔨 {member.mention} забанен. Причина: {reason}")


@bot.slash_command(name="mute", description="Заглушить пользователя")
@commands.default_member_permissions(moderate_members=True)
async def mute(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, minutes: int,
               reason: str = "Не указана"):
    await member.timeout(duration=datetime.timedelta(minutes=minutes), reason=reason)
    await inter.response.send_message(f"🔇 {member.mention} заглушен на {minutes} мин.")


@bot.slash_command(name="unmute", description="Снять заглушение")
@commands.default_member_permissions(moderate_members=True)
async def unmute(inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
    await member.timeout(duration=None)
    await inter.response.send_message(f"🔊 С {member.mention} снят мьют.")


@bot.slash_command(name="help", description="Список команд")
async def help_cmd(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="🤖 Справочник команд", color=disnake.Color.blurple())
    embed.add_field(name="Общие", value="`/userinfo` — нарисованная карточка\n`/help` — меню", inline=False)
    embed.add_field(name="Модерация",
                    value="`/clear <кол-во>`\n`/mute <юзер> <мин>`\n`/unmute <юзер>`\n`/kick <юзер>`\n`/ban <юзер>`",
                    inline=False)
    await inter.response.send_message(embed=embed, ephemeral=True)


bot.run("токен")

