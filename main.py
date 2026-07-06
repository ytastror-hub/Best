import os
import discord
import random
from discord.ext import commands
from datetime import datetime, timedelta

# --- الإعدادات ---
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_CHANNEL_IDS = [1523325684498563244, 1523325684498563245, 1523515227910701146]
OWNER_ROLE_ID = 1523325683344998515
CREATOR_ROLE_ID = 1523325683344998516
BOOSTER_ROLE_ID = 1523325683294670945
PREMIUM_ROLE_ID = 1523498644702101644

user_cooldowns = {}

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
    return ctx.channel.id in ALLOWED_CHANNEL_IDS

# --- الأوامر المودرن ---

@bot.command()
async def stock(ctx):
    services = ["minecraft", "hytale", "steam"]
    embed = discord.Embed(title="📦 | مخزون الحسابات الحالي", color=0x7289da)
    embed.set_thumbnail(url=bot.user.avatar.url)
    
    for service in services:
        count = len(get_accounts(service))
        status = "✅ متاح" if count > 0 else "❌ نافذ"
        embed.add_field(name=f"🎮 {service.upper()}", value=f"**الكمية:** {count}\n**الحالة:** {status}", inline=True)
    
    embed.set_footer(text="Blaze Cloud System | المتاجر الآلية")
    await ctx.send(embed=embed)

@bot.command()
async def gen(ctx, service: str = None):
    # 1. التحقق من الحالة
    if not has_status(ctx.author):
        return await ctx.send("🚫 | يجب وضع `Blaze Cloud On Top` في حالتك!")

    # 2. فحص الرتب
    user_role_ids = [role.id for role in ctx.author.roles]
    is_admin = (OWNER_ROLE_ID in user_role_ids) or (CREATOR_ROLE_ID in user_role_ids)
    
    # 3. نظام الـ Cooldown
    if not is_admin:
        now = datetime.now()
        if ctx.author.id in user_cooldowns:
            last_gen = user_cooldowns[ctx.author.id]
            if now - last_gen < timedelta(minutes=60):
                remaining = int((timedelta(minutes=60) - (now - last_gen)).total_seconds() // 60)
                return await ctx.send(f"⏳ | يرجى الانتظار **{remaining}** دقيقة للسحب.")

    if not service:
        return await ctx.send("⚠️ | يرجى تحديد الخدمة: `!gen [minecraft/hytale/steam]`")

    service = service.lower()
    
    # 4. فحص المخزون (منع السحب إذا كانت 0)
    accounts = get_accounts(service)
    if not accounts:
        embed = discord.Embed(title="📉 | عذراً الكمية نافذة!", description=f"الحسابات من نوع **{service.upper()}** غير متوفرة حالياً، يرجى مراجعة `!stock` لاحقاً.", color=0xed4245)
        return await ctx.send(embed=embed)

    # 5. التحقق من الرتب للخدمات
    if (service == "steam" and PREMIUM_ROLE_ID not in user_role_ids) or \
       (service == "hytale" and BOOSTER_ROLE_ID not in user_role_ids):
        return await ctx.send("🔒 | هذه الخدمة تتطلب رتبة خاصة!")

    # 6. عملية السحب
    account = accounts.pop(0) if service == "minecraft" else random.choice(accounts)
    with open(f"{service}.txt", "w") as f: f.write("\n".join(accounts))

    if not is_admin:
        user_cooldowns[ctx.author.id] = datetime.now()
    
    embed = discord.Embed(title="🎉 | تم السحب بنجاح!", description=f"تم استخراج حساب **{service.upper()}** لك:", color=0x57f287)
    embed.add_field(name="🔑 الحساب:", value=f"||`{account}`||", inline=False)
    embed.set_footer(text="يرجى الحفاظ على سرية الحساب")
    
    try:
        await ctx.author.send(embed=embed)
        await ctx.send(f"✅ | تم إرسال الحساب في الخاص يا {ctx.author.mention}")
    except discord.Forbidden:
        await ctx.send("⚠️ | **يرجى فتح الخاص لاستلام الحساب!**")

bot.run(os.environ.get('TOKEN'))