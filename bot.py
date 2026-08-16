import os
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

    if message.content.lower() == '!sunda':
        await message.channel.send('Wilujeng sumping di server Sunda, Lur! ☕ Mejeh Euy!')

client.run(os.getenv('DISCORD_TOKEN'))
