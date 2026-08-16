import os
import random
from datetime import datetime
import discord
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Fungsi background loop pikeun ngarobah status tanggal unggal poé (atawa per jam)
@tasks.loop(hours=24)
async def update_status_tanggal():
    now = datetime.now()
    tanggal_str = now.strftime('%d/%m/%Y')
    
    # Nyetél status bot jdi "Playing [Tanggal Ayeuna]"
    activity = discord.Game(name=f"📅 {tanggal_str} | !cinfo")
    await client.change_presence(activity=activity)

@client.event
async def on_ready():
    print(f'Bot geus aktif, lur! Asup sebagai {client.user}')
    # Mimitian ngajalankeun loop status tanggal pas bot mimiti nyala
    if not update_status_tanggal.is_running():
        update_status_tanggal.start()

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
            f"🤖 **Informasi Bot & Daptar Command:**\n"
            f"> • `!sunda` - Salam khas Sunda pisan\n"
            f"> • `!tanggal` - Cek wanci, tanggal, jeung jam ayeuna\n"
            f"> • `!ping` - Cek kecepatan respon bot\n"
            f"> • `!server` - Némbongkeun info server ieu\n"
            f"> • `!bantuan [soal]` - Ngitung matematika / PR sakola (Contoh: `!bantuan 5*5`)\n"
            f"> • `!tebak [angka]` - Game nebak angka 1 nepi ka 10\n"
            f"> • `!dadu` - Ngocok dadu maya (angka 1 - 6)\n"
            f"> • `!cuaca` - Cek perkiraan cuaca lokal\n"
            f"> • `!random [pilihan1], [pilihan2]` - Milih kaputusan acak\n"
            f"> • `!cinfo` - Némbongkeun daptar command ieu"
        )
        await message.channel.send(balasan)

    # Command !bantuan (Matematika)
    elif msg.startswith('!bantuan'):
        soal = message.content[8:].strip()
        if not soal:
            await message.channel.send("⚠️ Masukin soal matematika na, Lur! Conto: `!bantuan 5*5` atawa `!bantuan (10+5)*2`")
            return

        try:
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in soal):
                await message.channel.send("❌ Ngan ukur bisa angka jeung operator (+, -, *, /) wungkul, Lur!")
                return

            hasil = eval(soal)
            balasan = f"🧮 **Pangajian Soal MTK:**\n> Soal: `{soal}`\n> Hasilna: **{hasil}**\n*(Beres PR mah ulah poho rehat, Lur! ☕)*"
            await message.channel.send(balasan)
        except Exception:
            await message.channel.send("❌ Euy, salah nulis format soalna. Coba deui nu bener!")

    # Command !tebak (Game Angka 1-10)
    elif msg.startswith('!tebak'):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("🎮 Coba tebak angka ti 1 nepi ka 10! Ketik: `!tebak [angka]` (Contoh: `!tebak 7`)")
            return
        
        try:
            tebakan = int(parts[1])
            angka_bot = random.randint(1, 10)
            if tebakan == angka_bot:
                await message.channel.send(f"🎉 **HOREAM BNER!** Tebakan maneh bener **{angka_bot}**! Jago pisan euy!")
            else:
                await message.channel.send(f"❌ **SALAH!** Angka nu bener mah **{angka_bot}**, maneh nembak **{tebakan}**. Coba deui!")
        except ValueError:
            await message.channel.send("⚠️ Kudu angka, Lur! Conto: `!tebak 5`")

    # Command !dadu (Ngocok Dadu 1-6)
    elif msg == '!dadu':
        angka_dadu = random.randint(1, 6)
        dadu_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        await message.channel.send(f"🎲 **Kocokan Dadu:** {dadu_emoji[angka_dadu]} Hasilna nyaéta **{angka_dadu}**!")

    # Command !cuaca (Simulasi Cuaca Sunda)
    elif msg == '!cuaca':
        kondisi = [
            "Tiris pisan euy, siga di lembur subuh-subuh ❄️", 
            "Panas morongkol, ulah poho nginum cai tiis ☀️", 
            "Hujan ageung / keclak-keclak, siapkeun payung atawa sarung 🌧️", 
            "Hujan mintul sedeng, ngeunahna mah ngopi bari neda bala-bala ☕"
        ]
        pilih_cuaca = random.choice(kondisi)
        await message.channel.send(f"🌤️ **Perkiraan Cuaca Wilayah Sunda:**\n> Status: **{pilih_cuaca}**")

    # Command !random (Milih kaputusan)
    elif msg.startswith('!random'):
        pilihan_str = message.content[7:].strip()
        if not pilihan_str:
            await message.channel.send("🎲 Masukin pilihanna dipisah ku koma! Conto: `!random dahar bakso, dahar mie ayam`")
            return
        
        items = [item.strip() for item in pilihan_str.split(',')]
        if len(items) < 2:
            await message.channel.send("⚠️ Masukin minimal 2 pilihan dipisah ku koma, Lur!")
            return
        
        pilihan_terpilih = random.choice(items)
        await message.channel.send(f"🎲 **Hasil Keputusan AI:**\n> Pilihan nu kapilih nyaéta: **{pilihan_terpilih}** (Gasskeun ulah loba mikir!)")

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
