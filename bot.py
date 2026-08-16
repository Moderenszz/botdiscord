import os
import random
from datetime import datetime
import discord
from PIL import Image, ImageDraw
import io

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# --- FUNGSI GENERATE GAMBAR JODOH ---
def create_jodoh_image(user1, user2, percent):
    width, height = 400, 200
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Logika gradiasi manual (Biru tua ka biru muda)
    for y in range(height):
        r = int(0 + (135 - 0) * (y / height))
        g = int(0 + (206 - 0) * (y / height))
        b = int(139 + (235 - 139) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Tambah teks kana gambar
    draw.text((20, 40), f"Cek Jodoh:", fill=(255, 255, 255))
    draw.text((20, 70), f"{user1.name} & {user2.name}", fill=(255, 255, 255))
    draw.text((20, 120), f"Tingkat Cocok: {percent}%", fill=(255, 255, 0))
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    # --- COMMAND JODOH (Visual Gradiasi) ---
    if msg.startswith('!jodoh'):
        if len(message.mentions) < 2:
            await message.channel.send("Tag dua jalma! Conto: `!jodoh @user1 @user2`")
            return
        
        user1, user2 = message.mentions[0], message.mentions[1]
        percent = random.randint(1, 100)
        
        img_buffer = create_jodoh_image(user1, user2, percent)
        await message.channel.send(file=discord.File(img_buffer, filename="jodoh.png"))

    # --- COMMAND UTILITAS (Fungsional) ---
    elif msg == '!tanggal':
        now = datetime.now()
        hari_list = ['Minggu', 'Senén', 'Selasa', 'Rabu', 'Kamis', 'Jumaah', 'Setu']
        bulan_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        balasan = f"Wanci & Tanggal: {hari_list[now.weekday()]}, {now.strftime('%d')} {bulan_list[now.month - 1]} {now.strftime('%Y')} | {now.strftime('%H:%M:%S')} WIB"
        await message.channel.send(balasan)

    elif msg == '!ping':
        await message.channel.send(f"Latensi: {round(client.latency * 1000)}ms")

    elif msg.startswith('!translate'):
        teks_indo = message.content[10:].strip().lower()
        if not teks_indo:
            await message.channel.send("Conto: `!translate saya mau makan`")
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
        await message.channel.send(f"Translate Indo ➔ Sunda:\nIndonésia: {teks_indo}\nSunda: {terjemahan_final}")

    elif msg == '!cinfo':
        balasan = (
            "Daptar Command Fungsional:\n"
            "• `!jodoh @u1 @u2` - Cek kecocokan (Visual Gradiasi)\n"
            "• `!tanggal` - Cek wanci & tanggal\n"
            "• `!ping` - Cek latensi\n"
            "• `!translate [teks]` - Tarjamahkeun Indo kana Sunda\n"
            "• Moderasi Staf: `!clear`, `!mute`, `!kick`, `!ban`"
        )
        await message.channel.send(balasan)

client.run(os.getenv('DISCORD_TOKEN'))
