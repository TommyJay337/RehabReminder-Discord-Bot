# test line

import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from datetime import datetime, timedelta

# Discord Bot Setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('discord-bot-data-419816-908e93647dd2.json', scope)
gsheet_client = gspread.authorize(creds)
sheet = gsheet_client.open('Mod 8 Tasks').sheet1

# Semester Dates (YYYY, MM, DD)
semester_start = datetime(2024, 4, 8)
semester_end = datetime(2024, 6, 21)

async def check_weekly_tasks():
    await client.wait_until_ready()
    channel = client.get_channel(1227352261928292392)
    
    while not client.is_closed():
        today = datetime.now()
        # Check if today is Sunday
        if today.weekday() == 6:  # Monday is 0, Sunday is 6
            # Determine the current week of the semester
            current_week = (today - semester_start).days // 7 + 1
            weeks_remaining = (semester_end - today).days // 7
            
            # Fetch tasks for the current week
            tasks = sheet.findall(str(current_week), in_column=1)  # Assuming week numbers are in the first column
            messages = [f"Tasks for Week {current_week}:"]

            for task in tasks:
                row = sheet.row_values(task.row)
                # Assuming tasks are in the second column and due dates in the third
                messages.append(f"- {row[1]} due on {row[2]}")
            
            messages.append(f"Weeks remaining in the semester: {weeks_remaining}")
            
            # Send the message to the Discord channel
            await channel.send("\n".join(messages))
            
            # Wait until next Sunday
            next_sunday = today + timedelta(days=(6-today.weekday()) % 7 + 1)
            await asyncio.sleep((next_sunday - datetime.now()).total_seconds())
        else:
            # Wait for a day and check again
            await asyncio.sleep(86400)  # 86400 seconds in a day

client.loop.create_task(check_weekly_tasks())

client.run('MTIyNzI5MTEwNTQwNjc1MDc4MA.GZMxfq.-FCpCI3dQXEZ3z3M2bmjH1i5SsVOJhYPTVqzDk')  #bot's token
