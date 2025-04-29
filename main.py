import discord
from discord.ext import commands
import asyncio
from commands import setup_commands  # Import funkcji z pliku commands.py
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Flask serwer
app = Flask('')

@app.route('/')
def home():
    return "Bot działa!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Konfiguracja intentów
intents = discord.Intents.default()
intents.message_content = True  # Dla przetwarzania treści wiadomości
intents.members = True         # Dla danych członków serwera

# Inicjalizacja bota
bot = commands.Bot(command_prefix='!', intents=intents)

# Zdarzenie: Bot gotowy
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

# Ładowanie komend
setup_commands(bot)

# Uruchomienie bota
async def main():
    try:
        await bot.start(token)  # Wstaw token bota
    except Exception as e:
        print(f'Błąd: {e}')
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
