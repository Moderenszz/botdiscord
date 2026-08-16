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
            f"> • `!cinfo` - Némbongkeun daptar command ieu"
        )
        await message.channel.send(balasan)

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
