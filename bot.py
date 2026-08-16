import os
import random
from datetime import datetime
import discord
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Penting pisan pikeun deteksi member & moderation

client = discord.Client(intents=intents)

# Variabel Global pikeun simpen status AFK (Puntten lebetkeun ID Discord anjeun di dieu, cth: 123456789)
MY_DISCORD_ID = 0  # Ganti ku User ID anjeun séwang-séwangan
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

@client.event
async def on_message(message):
    global is_afk, afk_pesan

    if message.author == client.user:
        return

    # --- FITUR AFK SYSTEM ---
    # Lamun aya nu mention anjeun sarta posisi nuju AFK
    if is_afk and client.user.id != message.author.id:
        if message.mentions and any(m.id == MY_DISCORD_ID for m in message.mentions):
            await message.channel.send(f"⚠️ {message.author.mention}, dunungan kuring (Zerry) nuju **AFK**!\n> Alesanana: *\"{afk_pesan}\"*")

    msg = message.content.lower()

    # Set AFK Command (!afk [pesan] / !afk hungkul)
    if msg.startswith('!afk'):
        # Pariksa naha nu ngetik téh bener anjeun atawa bebas (bisa diatur)
        parts = message.content.split(maxsplit=1)
        if len(parts) > 1:
            is_afk = True
            afk_pesan = parts[1]
            await message.channel.send(f"💤 Status AFK diaktifkeun!\n> Pesan: *\"{afk_pesan}\"*")
        else:
            if is_afk:
                is_afk = False
                afk_pesan = ""
                await message.channel.send("✅ Status AFK ayeuna **Pareum** (Kantos balik deui online).")
            else:
                is_afk = True
                afk_pesan = "Keur sibuk / teu aya di tempat."
                await message.channel.send("💤 Status AFK diaktifkeun (Tanpa pesan husus).")
        return

    # Helper Cek Hak Akses Staff (Roles: Owner, Admin, Supervisor, Moderator, Junior Mod, Elite Guard, Trial Mod)
    def is_staff(member):
        staff_roles = ["owner", "admin", "supervisor", "staff", "moderator", "junior mod", "elite guard", "trial mod"]
        return any(role.name.lower() in staff_roles for role in member.roles) or member.guild_permissions.administrator

    # --- SERVER MANAGEMENT COMMANDS (HUSUS STAFF/ADMIN) ---

    # !clear [jumlah]
    if msg.startswith('!clear'):
        if not is_staff(message.author):
            await message.channel.send("❌ Hapunten, command ieu khusus kanggo Staf/Admin!")
            return
        parts = message.content.split()
        if len(parts) < 2 or not parts[1].isdigit():
            await message.channel.send("⚠️ Conto: `!clear 10` (Hapus 10 pesen)")
            return
        jumlah = int(parts[1])
        await message.channel.purge(limit=jumlah + 1)
        await message.channel.send(f"🧹 Berhasil mupus {jumlah} pesen, Lur!", delete_after=3)

    # !warn @user [alasan]
    elif msg.startswith('!warn'):
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        if not message.mentions:
            await message.channel.send("⚠️ Tag jalmana! Conto: `!warn @user spam chat`")
            return
        target = message.mentions[0]
        alasan = message.content.replace('!warn', '').replace(target.mention, '').strip()
        if not alasan: alasan = "Teu aya alesan khusus."
        await message.channel.send(f"⚠️ **WARNING:** {target.mention} geus di-warn ku Staf!\n> Alesan: *{alasan}*")

    # !mute @user
    elif msg.startswith('!mute'):
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        if not message.mentions:
            await message.channel.send("⚠️ Tag jalmana nu rek di-mute! Conto: `!mute @user`")
            return
        target = message.mentions[0]
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await message.guild.create_role(name="Muted")
                for channel in message.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            except Exception:
                pass
        try:
            await target.add_roles(muted_role)
            await message.channel.send(f"🔇 Berhasil nge-mute {target.mention}!")
        except Exception:
            await message.channel.send("❌ Gagal nge-mute! Pastikeun posisi role bot di luhur jalma nu rek di-mute.")

    # !unmute @user
    elif msg.startswith('!unmute'):
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        if not message.mentions:
            await message.channel.send("⚠️ Tag jalmana! Conto: `!unmute @user`")
            return
        target = message.mentions[0]
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if muted_role and muted_role in target.roles:
            await target.remove_roles(muted_role)
            await message.channel.send(f"🔊 {target.mention} ayeuna geus di-unmute!")
        else:
            await message.channel.send("⚠️ Jalma éta teu gaduh status mute.")

    # !kick @user
    elif msg.startswith('!kick'):
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        if not message.mentions:
            await message.channel.send("⚠️ Tag jalmana! Conto: `!kick @user`")
            return
        target = message.mentions[0]
        try:
            await target.kick(reason="Di-kick ku Staf server.")
            await message.channel.send(f"👢 Berhasil ngaluarkeun (kick) {target.name} ti server.")
        except Exception:
            await message.channel.send("❌ Gagal ngakick! Cek permission bot.")

    # !ban @user
    elif msg.startswith('!ban'):
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        if not message.mentions:
            await message.channel.send("⚠️ Tag jalmana! Conto: `!ban @user`")
            return
        target = message.mentions[0]
        try:
            await target.ban(reason="Di-ban ku Staf server.")
            await message.channel.send(f"🔨 Berhasil ngabanned {target.name} ti server!")
        except Exception:
            await message.channel.send("❌ Gagal ngaban! Cek permission bot.")

    # !slowmode [detik]
    elif msg.startswith('!slowmode'):
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        parts = message.content.split()
        if len(parts) < 2 or not parts[1].isdigit():
            await message.channel.send("⚠️ Conto: `!slowmode 5` (Set slowmode 5 detik)")
            return
        detik = int(parts[1])
        try:
            await message.channel.edit(slowmode_delay=detik)
            await message.channel.send(f"⏱️ Slowmode di channel ieu diset janten **{detik} detik**.")
        except Exception:
            await message.channel.send("❌ Gagal ngeset slowmode!")

    # !lock
    elif msg == '!lock':
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        try:
            await message.channel.set_permissions(message.guild.default_role, send_messages=False)
            await message.channel.send("🔒 Channel ieu geus di-lock (dikonci) ku Staf!")
        except Exception:
            await message.channel.send("❌ Gagal mengunci channel!")

    # !unlock
    elif msg == '!unlock':
        if not is_staff(message.author):
            await message.channel.send("❌ Husus Staf/Admin, Lur!")
            return
        try:
            await message.channel.set_permissions(message.guild.default_role, send_messages=True)
            await message.channel.send("🔓 Channel ieu geus di-unlock (dibuka deui)!")
        except Exception:
            await message.channel.send("❌ Gagal membuka channel!")

    # --- COMMAND UMUM ---
    elif msg == '!tanggal':
        now = datetime.now()
        hari_list = ['Minggu', 'Senén', 'Selasa', 'Rabu', 'Kamis', 'Jumaah', 'Setu']
        bulan_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        balasan = f"📅 **Wanci & Tanggal:** {hari_list[now.weekday()]}, {now.strftime('%d')} {bulan_list[now.month - 1]} {now.strftime('%Y')} | {now.strftime('%H:%M:%S')} WIB"
        await message.channel.send(balasan)

    elif msg == '!cinfo':
        balasan = (
            f"🤖 **Daptar Command Bot Sunda:**\n"
            f"> • `!sunda` - Salam khas Sunda\n"
            f"> • `!tanggal` - Cek wanci & tanggal\n"
            f"> • `!ping` - Cek latensi bot\n"
            f"> • `!server` - Info server\n"
            f"> • `!bantuan [soal]` - Ngitung matematika\n"
            f"> • `!tebak [angka]` - Game nebak angka\n"
            f"> • `!dadu` - Kocok dadu (1-6)\n"
            f"> • `!cuaca` - Cek cuaca\n"
            f"> • `!afk [pesan]` - Aktifkeun status AFK anjeun\n"
            f"> 🛡️ **Moderasi (Staf Only):**\n"
            f"> `!clear`, `!warn`, `!mute`, `!unmute`, `!kick`, `!ban`, `!slowmode`, `!lock`, `!unlock`"
        )
        await message.channel.send(balasan)

    elif msg.startswith('!bantuan'):
        soal = message.content[8:].strip()
        if not soal:
            await message.channel.send("⚠️ Conto: `!bantuan 5*5`")
            return
        try:
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in soal):
                await message.channel.send("❌ Ngan ukur angka jeung operator (+, -, *, /)!")
                return
            hasil = eval(soal)
            await message.channel.send(f"🧮 Hasilna: **{hasil}**")
        except Exception:
            await message.channel.send("❌ Format soal salah!")

    elif msg.startswith('!tebak'):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("⚠️ Conto: `!tebak 7`")
            return
        try:
            tebakan = int(parts[1])
            bot_num = random.randint(1, 10)
            if tebakan == bot_num:
                await message.channel.send(f"🎉 Bener pisan! Angkana **{bot_num}**!")
            else:
                await message.channel.send(f"❌ Salah! Angka nu bener **{bot_num}**.")
        except ValueError:
            await message.channel.send("⚠️ Kudu angka, Lur!")

    elif msg == '!dadu':
        angka = random.randint(1, 6)
        emojis = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        await message.channel.send(f"🎲 Dadu: {emojis[angka]} ({angka})")

    elif msg == '!cuaca':
        kondisi = ["Tiris pisan ❄️", "Panas morongkol ☀️", "Hujan ageung 🌧️", "Hujan sedeng ngeunah ngopi ☕"]
        await message.channel.send(f"🌤️ Cuaca: **{random.choice(kondisi)}**")

    elif msg.startswith('!random'):
        pilihan = message.content[7:].strip()
        items = [i.strip() for i in pilihan.split(',')]
        if len(items) < 2:
            await message.channel.send("⚠️ Conto: `!random dahar bakso, dahar mie ayam`")
            return
        await message.channel.send(f"🎲 Pilihan kapilih: **{random.choice(items)}**")

    elif msg == '!ping':
        await message.channel.send(f"🏓 Pong! Latensi: **{round(client.latency * 1000)}ms**")

    elif msg == '!server':
        guild = message.guild
        await message.channel.send(f"🏰 **{guild.name}** | Anggota: **{guild.member_count} urang** | Owner: {guild.owner}")

    elif msg == '!sunda':
        await message.channel.send('Wilujeng sumping di server Sunda, Lur! ☕ Mejeh Euy!')

client.run(os.getenv('DISCORD_TOKEN'))
