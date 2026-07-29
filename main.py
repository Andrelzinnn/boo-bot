import os

from discord import Intents, Permissions, utils
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

gif = "https://klipy.com/gifs/cat-hello-cat-peek"
client_id = os.getenv("CLIENT_ID")
token = os.getenv("TOKEN")
user_id = int(os.getenv("USER_ID"))

intents: Intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready() -> None:
    print("rodando")

@bot.event
async def on_message(message):
    if message.author == bot.user:
      return

    for user in message.mentions:
      if user.id == user_id:
        await message.channel.send(gif)

if(__name__ == "__main__"):
  if(token and client_id):
    url = utils.oauth_url(
        client_id=client_id,
        permissions=Permissions(send_messages=True, attach_files=True)
    )
    print(url)
    bot.run(token)
