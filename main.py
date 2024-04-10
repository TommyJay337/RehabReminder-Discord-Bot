from discord.ext import commands
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from datetime import datetime, timedelta

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize Google Sheets client in the bot constructor
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('discord-bot-data-419816-220342db7060.json', scope)
        gsheet_client = gspread.authorize(creds)
        self.sheet = gsheet_client.open('Mod 8 Tasks').sheet1

        # Set semester dates
        self.semester_start = datetime(2024, 4, 8)
        self.semester_end = datetime(2024, 6, 21)

    async def setup_hook(self):
        # Create a background task if needed, or perform other setup tasks
        pass

    async def check_weekly_tasks_manual(self):
        channel = self.get_channel(1227352261928292392)
        # Your existing task logic, modified for immediate execution or manual testing
        today = datetime.now()
        # Assume it's always "time to send" for testing
        current_week = (today - self.semester_start).days // 7 + 1
        weeks_remaining = (self.semester_end - today).days // 7

        tasks = self.sheet.findall(str(current_week), in_column=1)
        messages = [f"Tasks for Week {current_week}:"]
        for task in tasks:
            row = self.sheet.row_values(task.row)
            messages.append(f"- {row[1]} due on {row[2]}")
        
        messages.append(f"Weeks remaining in the semester: {weeks_remaining}")
        await channel.send("\n".join(messages))

# Instantiate MyBot with command prefix
intents = discord.Intents.default()
bot = MyBot(command_prefix="!", intents=intents)

@bot.command(name="testtasks")
async def test_tasks(ctx):
    await bot.check_weekly_tasks_manual()

with open('discord_token.txt', 'r') as file:
    token = file.read().strip()

bot.run(token)
