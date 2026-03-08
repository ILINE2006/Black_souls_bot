import disnake
from disnake.ext import commands
import datetime

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.InteractionBot(intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} готов к работе!')

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
# 🧹 ОЧИСТКА ЧАТА
# ==========================================
@bot.slash_command(name="clear", description="Очистить чат")
@commands.default_member_permissions(manage_messages=True)
async def clear(inter: disnake.ApplicationCommandInteraction, amount: int):
    deleted = await inter.channel.purge(limit=amount)
    await inter.response.send_message(f"✅ Удалено {len(deleted)} сообщений.", ephemeral=True)

# ==========================================
# ⚖️ МОДЕРАЦИЯ
# ==========================================
@bot.slash_command(name="kick", description="Выгнать пользователя")
@commands.default_member_permissions(kick_members=True)
async def kick(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Не указана"):
    await member.kick(reason=reason)
    embed = disnake.Embed(title="👢 Участник изгнан", color=disnake.Color.orange())
    embed.add_field(name="Пользователь", value=member.mention)
    embed.add_field(name="Причина", value=reason)
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="ban", description="Забанить пользователя")
@commands.default_member_permissions(ban_members=True)
async def ban(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    embed = disnake.Embed(title="🔨 Участник забанен", color=disnake.Color.red())
    embed.add_field(name="Пользователь", value=member.mention)
    embed.add_field(name="Причина", value=reason)
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="mute", description="Заглушить пользователя")
@commands.default_member_permissions(moderate_members=True)
async def mute(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, minutes: int, reason: str = "Не указана"):
    await member.timeout(duration=datetime.timedelta(minutes=minutes), reason=reason)
    embed = disnake.Embed(title="🔇 Пользователь заглушен", color=disnake.Color.dark_grey())
    embed.add_field(name="Пользователь", value=member.mention)
    embed.add_field(name="Время", value=f"{minutes} минут")
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="unmute", description="Снять заглушение")
@commands.default_member_permissions(moderate_members=True)
async def unmute(inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
    await member.timeout(duration=None)
    await inter.response.send_message(f"🔊 С {member.mention} снят мьют.")

# ==========================================
# 📇 КАРТОЧКА И HELP
# ==========================================
@bot.slash_command(name="userinfo", description="Карточка пользователя")
async def userinfo(inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
    member = member or inter.author
    embed = disnake.Embed(title="Информация о пользователе", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Роль", value=member.top_role.mention, inline=False)
    embed.add_field(name="Создан", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="Зашел", value=f"<t:{int(member.joined_at.timestamp())}:D>", inline=True)
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="help", description="Список команд")
async def help_cmd(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="🤖 Справочник команд", color=disnake.Color.blurple())
    embed.add_field(name="Общие", value="`/userinfo` — карточка\n`/help` — меню", inline=False)
    embed.add_field(name="Модерация", value="`/clear <кол-во>`\n`/mute <юзер> <мин>`\n`/unmute <юзер>`\n`/kick <юзер>`\n`/ban <юзер>`", inline=False)
    await inter.response.send_message(embed=embed, ephemeral=True)

bot.run("токен бота")

