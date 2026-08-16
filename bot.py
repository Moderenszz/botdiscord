import os
from datetime import datetime
import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot geus aktif, lur! Asup sebagai {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    # Command !tanggal
    if msg == '!tanggal':
        now = datetime.now()
        hari_list = ['Minggu', 'Senén', 'Selasa', 'Rabu', 'Kamis', 'Jumaah', 'Setu']
        bulan_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        
        hari = hari_list[now.weekday()]
        tanggal = now.strftime('%d')
        bulan = bulan_list[now.month - 1]
        tahun = now.strftime('%Y')
        jam = now.strftime('%H:%M:%S')

        balasan = (
            f"📅 **Wanci & Tanggal Ayeuna:**\n"
            f"> Dinten: **{hari}**, {tanggal} {bulan} {tahun}\n"
            f"> Tabuh: **{jam} WIB**\n"
            f"*(Mangga ulah poho ngopi, Lur! ☕)*"
        )
        await message.channel.send(balasan)

    # Command !cinfo
    elif msg == '!cinfo':
        balasan = (
            f"🤖 **Informasi Bot & Command:**\n"
            f"> • `!sunda` - Salam khas Sunda pisan\n"
            f"> • `!tanggal` - Cek wanci, tanggal, jeung jam ayeuna\n"
            f"> • `!ping` - Cek kecepatan respon bot\n"
            f"> • `!server` - Némbongkeun info server ieu\n"
            f"> • `!bantuan [soal]` - Mantuan hitung matematika (Contoh: `!bantuan 5*5` atawa `!bantuan 10+20`)ur\n"
            f"> • `!cinfo` - Némbongkeun daptar command ieu"
        )
        await message.channel.send(balasan)

    # Command !bantuan (Ngerjakeun Soal Matematika)
    elif msg.startswith('!bantuan'):
        # Nyokot éksprési matematika di tukangeun !bantuan
        soal = message.content[8:].strip()
        
        if not soal:
            await message.channel.send("⚠️ Masukin soal matematika na, Lur! Conto: `!bantuan 5*5` atau `!bantuan (10+5)*2`")
            return

        try:
            # Ngamankeun input supaya ngan ukur angka jeung operator matematika nu dibaca
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in soal):
                await message.channel.send("❌ Wah, éksprési teu dikenal! Ngan ukur bisa angka jeung operator (+, -, *, /) wungkul.")
                return

            # Ngitung hasil matematika sacara aman
            hasil = eval(soal)
            balasan = f"🧮 **Pangajian Soal MTK:**\n> Soal: `{soal}`\n> Hasilna: **{hasil}**\n*(Beres PR mah ulah poho rehat, Lur! ☕)*"
            await message.channel.send(balasan)
            
        except Exception:
            await message.channel.send("❌ Euy, siga nu salah nulis format soalna. Coba deui nu bener!")

    # Command !ping
    elif msg == '!ping':
        latency = round(client.latency * 1000)
        await message.channel.send(f"🏓 Pong! Latensi bot: **{latency}ms** (Lancar jaya, Lur!)")

    # Command !server
    elif msg == '!server':
        guild = message.guild
        balasan = (
            f"🏰 **Informasi Server:**\n"
            f"> Ngaran Server: **{guild.name}**\n"
            f"> Jumlah Anggota: **{guild.member_count} urang**\n"
            f"> Nu Punya: {guild.owner}"
        )
        await message.channel.send(balasan)

    # Command !sunda
    elif msg == '!sunda':
        await message.channel.send('Wilujeng sumping di server Sunda, Lur! ☕ Mejeh Euy!')

client.run(os.getenv('DISCORD_TOKEN'))
