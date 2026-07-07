import os
import discord
import random
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

# --- الإعدادات ---
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_CHANNEL_IDS = [1523805687036252233, 1523805689351508062, 1523805691251261653, 1523805685857390726, 1523805694065639475]
# الرابط المباشر لروم الفاوش الخاص بك
VOUCH_LINK = "https://discord.com/channels/1523805446748766349/1523805692639707208"
# الـ ID الخاص بروم الفاوش للتحقق (مستخرج من الرابط)
VOUCH_CHANNEL_ID = 1523805692639707208

OWNER_ROLE_ID = 1523805590072070257
CREATOR_ROLE_ID = 1523805589132808323
BOOSTER_ROLE_ID = 1523805618794922061
PREMIUM_ROLE_ID = 1523805617272262842

user_cooldowns = {}
vouch_pending = {} 
banned_from_bot = {} 

# --- الدوال ---
def get_accounts(service):
    try:
        with open(f"{service}.txt", "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return []

def has_status(member):
    for activity in member.activities:
        if isinstance(activity, discord.CustomActivity):
            if activity.name and "Blaze Cloud On Top" in activity.name:
                return True
    return False

@bot.check
async def globally_check(ctx):
    if ctx.author.id in banned_from_bot:
        if datetime.now() < banned_from_bot[ctx.author.id]:
            return False
        else:
            del banned_from_bot[ctx.author.id]
    return ctx.channel.id in ALLOWED_CHANNEL_IDS

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id == VOUCH_CHANNEL_ID:
        if "+rep vouch" in message.content.lower():
            user_id = message.author.id
            if user_id in vouch_pending:
                del vouch_pending[user_id]
                await message.add_reaction("✅")
                await message.channel.send(f"شكراً يا {message.author.mention} على الـ Vouch!")
    await bot.process_commands(message)

# --- الأوامر ---
@bot.command()
async def stock(ctx):
    services = ["minecraft", "hytale", "steam"]
    icons = {"minecraft": "⛏️", "hytale": "⚔️", "steam": "🎮"}
    
    embed = discord.Embed(title="📦 نظام المخزون المركزي | Blaze Cloud", description="استعرض حالة الأدوات والحسابات المتاحة لدينا:", color=0x5865F2)
    embed.set_thumbnail(url=bot.user.avatar.url)
    
    for s in services:
        count = len(get_accounts(s))
        term = "أداة" if s in ["steam", "hytale"] else "حساب"
        status = "✅ متاح للطلب" if count > 0 else "❌ غير متوفر حالياً"
        embed.add_field(name=f"{icons.get(s, '🔹')} {s.upper()}", value=f"**الكمية المتوفرة:** `{count}` {term}\n**الحالة:** {status}\n━━━━━━━━━━━━━━", inline=False)
    
    embed.set_footer(text="Blaze Cloud System | يتم تحديث المخزون تلقائياً", icon_url=ctx.guild.icon.url)
    embed.timestamp = datetime.now()
    await ctx.send(embed=embed)

@bot.command()
async def gen(ctx, service: str = None):
    if not has_status(ctx.author):
        return await ctx.send("🚫 | يجب وضع `Blaze Cloud On Top` في حالتك!")

    user_role_ids = [role.id for role in ctx.author.roles]
    is_admin = (OWNER_ROLE_ID in user_role_ids) or (CREATOR_ROLE_ID in user_role_ids)
    
    if not is_admin:
        now = datetime.now()
        if ctx.author.id in user_cooldowns and now - user_cooldowns[ctx.author.id] < timedelta(minutes=60):
            remaining = int((timedelta(minutes=60) - (now - user_cooldowns[ctx.author.id])).total_seconds() // 60)
            return await ctx.send(f"⏳ | يرجى الانتظار {remaining} دقيقة للسحب.")

    if not service: return await ctx.send("⚠️ | حدد الخدمة: `!gen [minecraft/hytale/steam]`")
    
    service = service.lower()
    accounts = get_accounts(service)
    if not accounts: return await ctx.send("📉 | عذراً الكمية نافذة! راجع `!stock`")

    term = "أداة" if service in ["steam", "hytale"] else "حساب"
    item = accounts.pop(0) if service == "minecraft" else random.choice(accounts)
    with open(f"{service}.txt", "w") as f: f.write("\n".join(accounts))
    
    user_cooldowns[ctx.author.id] = datetime.now()
    vouch_pending[ctx.author.id] = datetime.now()
    
    embed = discord.Embed(title="🎉 | تم الاستلام بنجاح!", description=f"إليك الـ {term} الخاص بك: ||`{item}`||\n\n**ملاحظة:** لديك 15 دقيقة لكتابة `+rep vouch {service}` في [روم الـ Vouch]({VOUCH_LINK}) لتجنب الحظر المؤقت!", color=0x57f287)
    
    try:
        await ctx.author.send(embed=embed)
        await ctx.send(f"✅ | أرسلت لك الـ {term} في الخاص! تذكر كتابة `+rep vouch {service}` في [روم الـ Vouch]({VOUCH_LINK}).")
        
        await asyncio.sleep(900) 
        if ctx.author.id in vouch_pending:
            banned_from_bot[ctx.author.id] = datetime.now() + timedelta(minutes=30)
            await ctx.send(f"⚠️ | {ctx.author.mention} لم تقم بكتابة الـ Vouch في [الروم المخصصة]({VOUCH_LINK}). تم حظرك من البوت لمدة 30 دقيقة!")
            del vouch_pending[ctx.author.id]
    except discord.Forbidden:
        await ctx.send("⚠️ | افتح الخاص لاستلام الـ " + term)

bot.run(os.environ.get('TOKEN'))
