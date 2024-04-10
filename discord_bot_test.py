'''
from dotenv import load_dotenv
import discord
import os

load_dotenv()

intents = discord.Intents.default()
intents.messages = True  # Ensures the bot can receive messages
intents.message_content = True  # Allows the bot to see message content

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")  # Debugging print
    if message.author == client.user:
        return
    # Check if the bot has permission to send messages in the channel
    if not message.channel.permissions_for(message.guild.me).send_messages:
        print(f"Do not have permission to send messages in {message.channel.name}")
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello')

client.run(os.getenv('TOKEN'))
'''