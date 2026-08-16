import os
import random
import discord
from kamus import daftar_kamus

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

    # Pariksa lamun pesen diawali ku !sw
    if message.content.lower().startswith('!sw'):
        kata_kunci = message.content[3:].strip()
        
        if not kata_kunci:
            await message.channel.send("Naon nu rek ditéang dina Kamus Gaul Sunda? Contoh: `!sw ganteng` atanapi `!sw budak baong`")
            return

        # Milih definisi roasting sacara acak tina file kamus.py
        arti_gaul = random.choice(daftar_kamus)
        
        # Format balasan bot
        balasan = f"📖 **Kamus Gaul Sunda (Edisi Roasting):**\n> **{kata_kunci.upper()}** *(n)*\n> Artinya: {arti_gaul}"
        await message.channel.send(balasan)

    elif message.content.lower() == '!sunda':
        await message.channel.send('Wilujeng sumping di server Sunda, Lur! ☕ Mejeh Euy!')

client.run(os.getenv('DISCORD_TOKEN'))
