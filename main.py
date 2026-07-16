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

# رابط صورتك الاحترافية
SERVER_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1C5sVTxubD9p2gSo-yBhU_hVaL4-f2IJNPd9o7KlE2A&s=10"

ALLOWED_CHANNEL_IDS = [1527348471227613406, 1527348422288605306, 1527348392198672545, 1527348363220095067, 1527348320257839176]
VOUCH_LINK = "https://discord.com/channels/1524767218875895968/1527348471227613406"

# الرتب
OWNER_ROLE_ID = 1524767522199572620
CREATOR_ROLE_ID = 1524767523269115977
BOOSTER_ROLE_ID = 1524767547663192117
PREMIUM_ROLE_ID = 1524767549684846712
FREEMIUM_ROLE_ID = 1527346929745264691

user_cooldowns = {}
vouch_pending = {} 
banned_from_bot = {} 

# --- الدوال ---
def get_accounts(service):
    try:
        with open(f"{service}.txt", "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError: return []

def has_cstatus(member):
    for activity in member.activities:
        if isinstance(activity, discord.CustomActivity):
            if activity.name and "Ender Cloud Best Mcfa Gen" in activity.name:
                return True
    return False

# --- الأوامر ---

@bot.command()
async def cstatus(ctx):
    allowed_roles = [OWNER_ROLE_ID, CREATOR_ROLE_ID, BOOSTER_ROLE_ID, PREMIUM_ROLE_ID, FREEMIUM_ROLE_ID]
    if not any(role.id in allowed_roles for role in ctx.author.roles):
        return await ctx.send("❌ **عذراً، لا تملك الرتبة المطلوبة.**")
    if not has_cstatus(ctx.author):
        return await ctx.send("⚠️ **يجب أن تكون حالتك:** `Ender Cloud Best Mcfa Gen`")

    embed = discord.Embed(title="✨ تم التحقق بنجاح | Ender Cloud", description=f"أهلاً {ctx.author.mention}، أنت الآن مؤهل للخدمة. 🚀", color=0x5865F2)
    embed.set_thumbnail(url=SERVER_IMAGE_URL)
    embed.set_footer(text="Ender Cloud System", icon_url=SERVER_IMAGE_URL)
    await ctx.send(embed=embed)

@bot.command()
async def restock(ctx, service: str = None, *, account: str = None):
    admin_roles = [OWNER_ROLE_ID, CREATOR_ROLE_ID]
    if not any(role.id in admin_roles for role in ctx.author.roles):
        return await ctx.send("❌ **للإدارة فقط!**")
    if not service or not account:
        return await ctx.send("⚠️ **استخدام:** `!restock [minecraft/hytale/steam] [الحساب]`")

    with open(f"{service.lower()}.txt", "a") as f: f.write(f"\n{account}")
    embed = discord.Embed(title="📥 تم الإضافة بنجاح", description=f"تمت إضافة الحساب لـ **{service.upper()}** ✅", color=0x00FF00)
    embed.set_thumbnail(url=SERVER_IMAGE_URL)
    await ctx.send(embed=embed)

@bot.command()
async def stock(ctx):
    services = ["minecraft", "hytale", "steam"]
    embed = discord.Embed(title="📦 نظام المخزون المركزي", color=0x5865F2)
    embed.set_thumbnail(url=SERVER_IMAGE_URL)
    for s in services:
        count = len(get_accounts(s))
        embed.add_field(name=f"🔹 {s.upper()}", value=f"**الكمية:** `{count}`", inline=False)
    embed.set_footer(text="Ender Cloud System", icon_url=SERVER_IMAGE_URL)
    await ctx.send(embed=embed)

@bot.command()
async def gen(ctx, service: str = None):
    if not has_cstatus(ctx.author): return await ctx.send("🚫 | ضع الحالة أولاً!")
    if not service or service.lower() not in ["minecraft", "hytale", "steam"]: return await ctx.send("⚠️ | `!gen [service]`")
    
    service = service.lower()
    accounts = get_accounts(service)
    if not accounts: return await ctx.send("📉 | الكمية نافذة!")

    item = accounts.pop(0) if service == "minecraft" else random.choice(accounts)
    with open(f"{service}.txt", "w") as f: f.write("\n".join(accounts))
    
    embed = discord.Embed(title="🎉 | تم الاستلام!", description=f"الحساب: ||`{item}`||", color=0x57f287)
    embed.set_thumbnail(url=SERVER_IMAGE_URL)
    embed.set_footer(text="Ender Cloud Gen System", icon_url=SERVER_IMAGE_URL)
    await ctx.author.send(embed=embed)
    await ctx.send("✅ | تم الإرسال للخاص! تذكر الـ Vouch.")

bot.run(os.environ.get('TOKEN'))
