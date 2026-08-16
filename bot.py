import os
import random
from datetime import datetime
import discord
from discord.ext import tasks
from PIL import Image, ImageDraw
import io

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# Variabel Global pikeun simpen status AFK
MY_DISCORD_ID = 0  # Ganti ku ID Discord anjeun
is_afk = False
afk_pesan = ""

@tasks.loop(hours=24)
async def update_status_tanggal():
    now = datetime.now()
    tanggal_str = now.strftime('%d/%m/%Y')
    activity = discord.Game(name=f"📅 {tanggal_str} | !cinfo")
    await client.change_presence(activity=activity)

@client.event
async def on_ready():
    print(f'Bot geus aktif, lur! Asup sebagai {client.user}')
    if not update_status_tanggal.is_running():
        update_status_tanggal.start()

# Helper Cek Hak Akses Staff dumasar roles
def is_staff(member):
    staff_roles = ["owner", "admin", "supervisor", "staff", "moderator", "junior mod", "elite guard", "trial mod"]
    return any(role.name.lower() in staff_roles for role in member.roles) or member.guild_permissions.administrator

# Fungsi Generate Gambar Jodoh Gradiasi Biru Tua ka Biru Muda
def create_jodoh_image(user1, user2, percent):
    width, height = 400, 200
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Gradiasi manual ti biru tua ka biru muda
    for y in range(height):
        r = int(0 + (135 - 0) * (y / height))
        g = int(0 + (206 - 0) * (y / height))
        b = int(139 + (235 - 139) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Teks kana gambar
    draw.text((20, 40), "❤️ Cek Jodoh:", fill=(255, 255, 255))
    draw.text((20, 70), f"{user1.name} & {user2.name}", fill=(255, 255, 255))
    draw.text((20, 120), f"Tingkat Kecocokan: {percent}%", fill=(255, 255, 0))
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@client.event
async def on_message(message):
    global is_afk, afk_pesan

    if message.author == client.user:
        return

    # --- FITUR AFK SYSTEM ---
    if is_afk and client.user.id != message.author.id:
        if message.mentions and any(m.id == MY_DISCORD_ID for m in message.mentions):
            await message.channel.send(f"⚠️ {message.author.mention}, dunungan kuring nuju **AFK**!\n> Alesanana: *\"{afk_pesan}\"*")

    msg = message.content.lower()

    if msg.startswith('!afk'):
        parts = message.content.split(maxsplit=1)
        if len(parts) > 1:
            is_afk = True
            afk_pesan = parts[1]
            await message.channel.send(f"💤 Status AFK diaktifkeun!\n> Pesan: *\"{afk_pesan}\"*")
        else:
            if is_afk:
                is_afk = False
                afk_pesan = ""
                await message.channel.send("✅ Status AFK ayeuna **Pareum**.")
            else:
                is_afk = True
                afk_pesan = "Keur sibuk / teu aya di tempat."
                await message.channel.send("💤 Status AFK diaktifkeun.")
        return

    # --- SERVER MANAGEMENT COMMANDS (HUSUS STAFF/ADMIN) ---
    if msg.startswith('!clear'):
        if not is_staff(message.author):
            await message.channel.send("❌ Hapunten, command ieu khusus kanggo Staf/Admin!")
            return
        parts = message.content.split()
        if len(parts) < 2 or not parts[1].isdigit():
            await message.channel.send("⚠️ Conto: `!clear 10`")
            return
        jumlah = int(parts[1])
        await message.channel.purge(limit=jumlah + 1)
        await message.channel.send(f"🧹 Berhasil mupus {jumlah} pesen, Lur!", delete_after=3)

    elif msg.startswith('!warn'):
        if not is_staff(message.author): return
        if not message.mentions:
            await message.channel.send("⚠️ Tag jalmana! Conto: `!warn @user spam`")
            return
        target = message.mentions[0]
        alasan = message.content.replace('!warn', '').replace(target.mention, '').strip()
        if not alasan: alasan = "Teu aya alesan khusus."
        await message.channel.send(f"⚠️ **WARNING:** {target.mention} di-warn!\n> Alesan: *{alasan}*")

    elif msg.startswith('!mute'):
        if not is_staff(message.author): return
        if not message.mentions: return
        target = message.mentions[0]
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await message.guild.create_role(name="Muted")
                for channel in message.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            except Exception: pass
        try:
            await target.add_roles(muted_role)
            await message.channel.send(f"🔇 Berhasil nge-mute {target.mention}!")
        except Exception:
            await message.channel.send("❌ Gagal nge-mute! Cek posisi role bot.")

    elif msg.startswith('!unmute'):
        if not is_staff(message.author): return
        if not message.mentions: return
        target = message.mentions[0]
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if muted_role and muted_role in target.roles:
            await target.remove_roles(muted_role)
            await message.channel.send(f"🔊 {target.mention} di-unmute!")

    elif msg.startswith('!kick'):
        if not is_staff(message.author): return
        if not message.mentions: return
        target = message.mentions[0]
        try:
            await target.kick(reason="Di-kick ku Staf.")
            await message.channel.send(f"👢 Berhasil ngaluarkeun {target.name}.")
        except Exception:
            await message.channel.send("❌ Gagal ngakick.")

    elif msg.startswith('!ban'):
        if not is_staff(message.author): return
        if not message.mentions: return
        target = message.mentions[0]
        try:
            await target.ban(reason="Di-ban ku Staf.")
            await message.channel.send(f"🔨 Berhasil ngabanned {target.name}!")
        except Exception:
            await message.channel.send("❌ Gagal ngaban.")

    elif msg.startswith('!slowmode'):
        if not is_staff(message.author): return
        parts = message.content.split()
        if len(parts) < 2 or not parts[1].isdigit(): return
        detik = int(parts[1])
        try:
            await message.channel.edit(slowmode_delay=detik)
            await message.channel.send(f"⏱️ Slowmode diset janten **{detik} detik**.")
        except Exception: pass

    elif msg == '!lock':
        if not is_staff(message.author): return
        try:
            await message.channel.set_permissions(message.guild.default_role, send_messages=False)
            await message.channel.send("🔒 Channel dikonci!")
        except Exception: pass

    elif msg == '!unlock':
        if not is_staff(message.author): return
        try:
            await message.channel.set_permissions(message.guild.default_role, send_messages=True)
            await message.channel.send("🔓 Channel dibuka deui!")
        except Exception: pass

    # --- COMMAND FUNGSIONAL & VISUAL ---
    elif msg.startswith('!jodoh'):
        if len(message.mentions) < 2:
            await message.channel.send("⚠️ Tag dua jalma! Conto: `!jodoh @user1 @user2`")
            return
        user1, user2 = message.mentions[0], message.mentions[1]
        percent = random.randint(1, 100)
        img_buffer = create_jodoh_image(user1, user2, percent)
        await message.channel.send(file=discord.File(img_buffer, filename="jodoh.png"))

    elif msg == '!tanggal':
        now = datetime.now()
        hari_list = ['Minggu', 'Senén', 'Selasa', 'Rabu', 'Kamis', 'Jumaah', 'Setu']
        bulan_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        balasan = f"📅 **Wanci & Tanggal:** {hari_list[now.weekday()]}, {now.strftime('%d')} {bulan_list[now.month - 1]} {now.strftime('%Y')} | {now.strftime('%H:%M:%S')} WIB"
        await message.channel.send(balasan)

    elif msg == '!cuaca':
        jam_ayeuna = datetime.now().hour
        if 18 <= jam_ayeuna or jam_ayeuna < 5:
            kondisi = [
                "Peuting-peuting kieu tiris pisan, ngeunahna mah ngopi bari disarungan ☕❄️",
                "Hujan keclak-keclak di luar, ulah hilap nutup jandéla 🌧️",
                "Angin peuting karasa tiris, ulah loba teuing kaluar 🌬️"
            ]
        else:
            kondisi = [
                "Panas morongkol, ulah poho nginum cai tiis ☀️",
                "Cuaca cerah, mantap pisan pikeun jalan-jalan 🌤️",
                "Hawana rada mendung, siapkeun payung bisi hujan ☁️"
            ]
        pilih_cuaca = random.choice(kondisi)
        await message.channel.send(f"🌤️ **Perkiraan Cuaca Bandung Ayeuna:**\n> Status: **{pilih_cuaca}**")

    elif msg == '!cinfo':
        balasan = (
            "🤖 **Daptar Command Bot:**\n"
            "> • `!jodoh @u1 @u2` - Cek kecocokan (Visual Gradiasi Biru)\n"
            "> • `!tanggal` - Cek wanci & tanggal\n"
            "> • `!cuaca` - Cek cuaca akurat sasuai waktu\n"
            "> • `!ping` - Cek latensi bot\n"
            "> • `!server` - Info server\n"
            "> • `!bantuan [soal]` - Ngitung matematika\n"
            "> • `!translate [tulis ID]` - Tarjamahkeun Indo kana Sunda\n"
            "> • `!afk [pesan]` - Status AFK\n"
            "> 🛡️ **Moderasi (Staf Only):**\n"
            "> `!clear`, `!warn`, `!mute`, `!unmute`, `!kick`, `!ban`, `!slowmode`, `!lock`, `!unlock`"
        )
        await message.channel.send(balasan)

    elif msg.startswith('!bantuan'):
        soal = message.content[8:].strip()
        if not soal: return
        try:
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in soal): return
            hasil = eval(soal)
            await message.channel.send(f"🧮 Hasilna: **{hasil}**")
        except Exception: pass

    elif msg.startswith('!translate'):
        teks_indo = message.content[10:].strip().lower()
        if not teks_indo:
            await message.channel.send("⚠️ Conto: `!translate saya mau makan`")
            return
        kamus_id_su = {
            "saya": "urang / sim kuring", "kamu": "maneh / anjeun", "dia": "manehna",
            "mau": "hayang / badé", "makan": "dahar / neda", "minum": "inum / leueut",
            "tidur": "saré", "pergi": "indit / angkat", "pulang": "balik",
            "tidak": "teu / henteu", "iya": "enya", "bagus": "alus / saé",
            "kenapa": "naha", "apa": "naon", "dimana": "di mana", "siapa": "saha"
        }
        hasil_translate = [kamus_id_su.get(kata, f"*{kata}*") for kata in teks_indo.split()]
        terjemahan_final = " ".join(hasil_translate)
        await message.channel.send(f"📖 **Translate Indo ➔ Sunda:**\n> Indonésia: *{teks_indo}*\n> Sunda: **{terjemahan_final}**")

    elif msg == '!ping':
        await message.channel.send(f"🏓 Pong! Latensi: **{round(client.latency * 1000)}ms**")

    elif msg == '!server':
        guild = message.guild
        await message.channel.send(f"🏰 **{guild.name}** | Anggota: **{guild.member_count} urang** | Owner: {guild.owner}")

    elif msg == '!sunda':
        await message.channel.send('Wilujeng sumping di server Sunda, Lur! ☕')

client.run(os.getenv('DISCORD_TOKEN'))
