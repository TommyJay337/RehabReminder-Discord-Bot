from dotenv import load_dotenv
import asyncio
import discord
from datetime import datetime, timedelta,timezone
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()

intents = discord.Intents.default()
intents.messages = True  # Ensures the bot can receive messages
intents.message_content = True  # Allows the bot to see message content

client = discord.Client(intents=intents)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('discord-bot-data-419816-220342db7060.json', scope)
gsheet_client = gspread.authorize(creds)

# Assuming semester start date (YYYY, M, D)
semester_start_date = datetime(2024, 4, 8)

def get_semester_week_number():
    # Current date
    current_date = datetime.now()
    # Calculate the difference between the current date and the start date of the semester
    delta = current_date - semester_start_date
    # Calculate the week number; +1 to start the week count at 1
    week_number = (delta.days // 7) + 1
    return week_number

total_weeks_in_semester = 10

def get_current_week_tasks(week_number=None):
    if week_number is None:
        # If no week_number is provided, calculate it based on the semester start date
        week_number = get_semester_week_number()

    weeks_remaining = total_weeks_in_semester - week_number

    print(f"Searching for tasks in Week #: {week_number}")  # Debug print

    # Open the spreadsheet
    sheet = gsheet_client.open("Mod 8 Tasks").get_worksheet(0)  # Assuming you're using the first sheet
    # Get all records from the sheet
    records = sheet.get_all_records()

    # Filter tasks that match the given week number
    tasks_for_week = [record for record in records if record.get('Week #') == week_number]

    # Format the tasks into a message string
    if tasks_for_week:
        message = "Assignments/Tests for the upcoming week of the module:\n"
        for task in tasks_for_week:
            message += f"- {task.get('Tasks')} (Due: {task.get('Due Date')})\n"

        if weeks_remaining > 0:
            message += f"\nYou're crushing it! Only {weeks_remaining + 1} weeks left to go!"
        else: message += f"\nYou're almost there! This is the last week"

    else:
        message = "No assignments/tests found for the current week of the module. If this is a mistake, please let Thomas know."
        message += f"\nYou're crushing it! Only {weeks_remaining + 1} weeks left to go!"
        
    return message

def next_sunday_at_8pm_cst():
    now = datetime.now(timezone.utc)  # Current UTC time
    print(f"Current UTC time: {now.isoformat()}")

    # Convert current UTC time to CST (UTC-6)
    cst_now = now - timedelta(hours=6)
    print(f"Current CST time: {cst_now.isoformat()}")

    # Define the target hour in CST
    target_hour_cst = 20  # 8 PM CST

    # Calculate days until next Sunday (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
    days_until_sunday = (6 - cst_now.weekday()) % 7
    print(f"Days until next Sunday: {days_until_sunday}")

    # If today is Sunday and before 8 PM CST, set the target for today
    if days_until_sunday == 0 and cst_now.hour < target_hour_cst:
        next_run_cst = cst_now.replace(hour=target_hour_cst, minute=0, second=0, microsecond=0)
    else:
        # Calculate next Sunday's date
        next_sunday = cst_now + timedelta(days=days_until_sunday)
        next_run_cst = next_sunday.replace(hour=target_hour_cst, minute=0, second=0, microsecond=0)

    # Convert the next run time back to UTC
    next_run_utc = next_run_cst + timedelta(hours=6)
    print(f"Next run scheduled for (CST): {next_run_cst.isoformat()}")
    print(f"Next run scheduled for (UTC): {next_run_utc.isoformat()}")

    return next_run_utc

async def weekly_task():
    await client.wait_until_ready()
    channel_id = 1227352261928292395  # channel ID
    channel = client.get_channel(channel_id)
    print(f"Channel found: {channel}")

    next_run = next_sunday_at_8pm_cst()
    print(f"Initial next run scheduled for {next_run.isoformat()}")

    while not client.is_closed():
        now = datetime.now(timezone.utc)
        wait_time_in_seconds = (next_run - now).total_seconds()

        if wait_time_in_seconds > 0:
            print(f"Waiting for {wait_time_in_seconds} seconds for the next trigger.")
            await asyncio.sleep(wait_time_in_seconds)

        now = datetime.now(timezone.utc)  # Re-check current time after sleep
        if now >= next_run:
            print("Attempting to send message")
            tasks_message = get_current_week_tasks(week_number=get_semester_week_number() + 1)  # Get tasks for the upcoming week
            try:
                await channel.send(tasks_message)
                print("Message sent successfully.")
            except Exception as e:
                print(f"Failed to send message: {e}")

        next_run = next_sunday_at_8pm_cst()  # Recalculate the next run time after attempting to send the message
        print(f"Next run rescheduled for {next_run.isoformat()}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print("Servers:")
    for guild in client.guilds:
        print(f"- {guild.name}")
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    print(f"Current UTC time: {now_utc}")
    print(f"System local time: {now_local}")
    print(f"Time zone offset: {now_local.utcoffset()}")
    client.loop.create_task(weekly_task())

@client.event
async def on_message(message):
# Ignore messages from the bot itself
    if message.author == client.user:
        return


# Manual testing portion of the code
    if message.content.startswith('$test'):
        tasks_message = get_current_week_tasks(week_number=2)  # Change to your test week number
        await message.channel.send(tasks_message)


client.run(os.getenv('TOKEN'))
