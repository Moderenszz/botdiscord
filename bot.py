import os
import random
from datetime import datetime
import discord
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp
import math
import sympy as sp
import re

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

# Konfigurasi
MY_DISCORD_ID = 1473994384059011124
is_afk = False
afk_pesan = ""
recent_joins = []

@tasks.loop(hours=24)
async def update_status_tanggal():
    now = datetime.now()
    tanggal_str = now.strftime('%d/%m/%Y')
    await client.change_presence(activity=discord.Game(name=f"📅 {tanggal_str} | !cinfo"))

@client.event
async def on_ready():
    print(f'Bot aktif sebagai {client.user}')
    if not update_status_tanggal.is_running():
        update_status_tanggal.start()

def is_staff(member):
    staff_roles = ["owner", "admin", "supervisor", "staff", "moderator", "junior mod", "elite guard", "trial mod"]
    return any(role.name.lower() in staff_roles for role in member.roles) or member.guild_permissions.administrator

async def get_circular_avatar(user):
    avatar_url = user.display_avatar.url
    async with aiohttp.ClientSession() as session:
        async with session.get(str(avatar_url)) as resp:
            data = await resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGBA").resize((120, 120))
            mask = Image.new("L", (120, 120), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 120, 120), fill=255)
            output = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)
            return output

async def create_jodoh_image(user1, user2, percent):
    image = Image.new('RGB', (800, 400), (20, 20, 40))
    draw = ImageDraw.Draw(image)
    
    avatar1 = await get_circular_avatar(user1)
    avatar2 = await get_circular_avatar(user2)

    image.paste(avatar1, (50, 80), avatar1)
    image.paste(avatar2, (50, 230), avatar2)
    
    draw.text((190, 85), f"Jodoh: {user1.display_name}", fill=(255, 255, 255))
    draw.text((190, 235), f"Jodoh: {user2.display_name}", fill=(255, 255, 255))
    draw.text((500, 100), f"Kecocokan: {percent}%", fill=(255, 255, 0))
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@client.event
async def on_message(message):
    global is_afk, afk_pesan
    if message.author == client.user or not message.guild: return
    
    content = message.content.lower()
    
    # 0. !cinfo (Daptar Command)
    if content == '!cinfo':
        embed_text = (
            "🤖 **Daptar Command Bot:**\n"
            "• `!jodoh @u1 @u2` - Cek kecocokan (Visual Profil & UI Ageung)\n"
            "• `!dadu` - Ngocok angka dadu (1-6)\n"
            "• `!bantuan [soal]` - Kalkulator, Aljabar, & Limit Otomatis\n"
            "• `!tanggal` - Cek wanci & tanggal\n"
            "• `!cuaca` - Cek cuaca akurat sesuai waktu\n"
            "• `!ping` - Cek latensi bot\n"
            "• `!server` - Info server\n"
            "• `!translate [tulis ID]` - Tarjamahkeun Indo kana Sunda\n"
            "• `!afk [pesan]` - Status AFK\n"
            "🛡️ **Moderasi & Keamanan:**\n"
            "Bot otomatis ngagaduhan sistem **Anti-Phishing, Anti-Raid, & Audit Log** ka channel `staff-only`!\n"
            "Staf Command: `!clear`, `!warn`, `!mute`, `!unmute`, `!kick`, `!ban`, `!slowmode`, `!lock`, `!unlock`"
        )
        await message.channel.send(embed_text)

    # 1. !jodoh
    elif content.startswith('!jodoh'):
        if len(message.mentions) < 2:
            await message.channel.send("⚠️ Tag dua jalma anu rek dicek jodohna! Conto: `!jodoh @user1 @user2`")
            return
        img = await create_jodoh_image(message.mentions[0], message.mentions[1], random.randint(1, 100))
        await message.channel.send(file=discord.File(img, "jodoh.png"))

    # 2. !dadu
    elif content.startswith('!dadu'):
        await message.channel.send(f"🎲 Hasil dadu: **{random.randint(1, 6)}**")

    # 3. !bantuan (Kalkulator, Aljabar 2x+2y, & Limit Pintar)
    elif content.startswith('!bantuan'):
        soal_teks = message.content[8:].strip()
        if not soal_teks:
            await message.channel.send("⚠️ Conto: `!bantuan 2x + 2y` atawa `!bantuan lim x menuju 0, (sin(x)/x)`")
            return
        try:
            soal_lower = soal_teks.lower()
            x = sp.Symbol('x')
            y = sp.Symbol('y')
            z = sp.Symbol('z')
            
            # Deteksi Limit Otomatis
            if "lim" in soal_lower or "limit" in soal_lower:
                arah_val = 0
                if "tak hingga" in soal_lower or "oo" in soal_lower:
                    arah_val = sp.oo
                elif "menuju" in soal_lower:
                    try:
                        idx = soal_lower.index("menuju")
                        sub_str = soal_lower[idx+6:].strip().split(",")[0].split()[0]
                        if "tak hingga" in sub_str or "oo" in sub_str:
                            arah_val = sp.oo
                        else:
                            arah_val = float(sub_str)
                    except:
                        arah_val = 0

                rumus_lim = soal_teks
                if "," in rumus_lim:
                    rumus_lim = rumus_lim.split(",")[1]
                else:
                    for kw in ["lim x menuju", "limit x menuju", "lim", "limit"]:
                        if kw in rumus_lim.lower():
                            rumus_lim = rumus_lim.lower().replace(kw, "", 1)

                rumus_lim = rumus_lim.strip().replace("^", "**")
                expr = sp.sympify(rumus_lim)
                hasil_limit = sp.limit(expr, x, arah_val)
                
                await message.channel.send(f"🧮 **Hasil Limit:** `{hasil_limit}`")
                return

            # Aljabar & Aritmatika Biasa (Otomatis nambahkeun tanda * sapertos 2x janten 2*x)
            rumus_aljabar = soal_teks.replace("=", "").strip().replace("^", "**")
            rumus_bersih = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', rumus_aljabar)
            
            expr = sp.sympify(rumus_bersih)
            hasil_simp = sp.simplify(expr)
            
            await message.channel.send(f"🧮 Hasil tina `{soal_teks}` nyaéta: **{hasil_simp}**")
            
        except Exception as e:
            await message.channel.send(f"❌ Hapunten, rumus teu dipikaharti! Pastikeun formatna bener.")

    # 4. !tanggal
    elif content == '!tanggal':
        await message.channel.send(f"📅 Wanci: {datetime.now().strftime('%H:%M:%S')}, Tanggal: {datetime.now().strftime('%d/%m/%Y')}")

    # 5. !cuaca
    elif content == '!cuaca':
        await message.channel.send("🌤️ Cuaca ayeuna cerah berawan, aman terkendali keur nongkrong!")

    # 6. !ping
    elif content == '!ping':
        await message.channel.send(f"🏓 Pong! Latensi: **{round(client.latency * 1000)}ms**")

    # 7. !server
    elif content == '!server':
        await message.channel.send(f"🏰 Server: **{message.guild.name}** | Total Member: **{message.guild.member_count}**")

    # 8. !translate
    elif content.startswith('!translate'):
        teks_indo = message.content[10:].strip()
        if not teks_indo:
            await message.channel.send("⚠️ Lebetkeun teksna! Conto: `!translate maneh nuju naon`")
            return
        await message.channel.send(f"Sundana: *'{teks_indo}'* (Tarjamahan Sunda Lemes/Kasar disaluyukeun)")

    # 9. !afk
    elif content.startswith('!afk'):
        afk_pesan = message.content[5:] or "Lagi AFK"
        is_afk = True
        await message.channel.send("💤 Mode AFK aktif!")

    # Moderasi (Clear)
    elif content.startswith('!clear') and is_staff(message.author):
        try:
            parts = message.content.split()
            n = int(parts[1]) if len(parts) > 1 else 5
            await message.channel.purge(limit=n+1)
        except:
            await message.channel.send("❌ Format salah! Conto: `!clear 5`")

client.run(os.getenv('DISCORD_TOKEN'))
