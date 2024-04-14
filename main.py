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

def next_sunday_at_10am_cst():
    now = datetime.now(timezone.utc)  # Get the current UTC time
    target_hour_utc = 17  # 10 AM CST in UTC (10 + 6 = 16 during Standard Time)

    # Calculate how many days until next Sunday
    days_until_sunday = (6 - now.weekday() + 7) % 7
    if days_until_sunday == 0:
        # If today is Sunday, determine if it's before or after 10 AM CST
        if now.hour > target_hour_utc or (now.hour == target_hour_utc and now.minute > 0):
            days_until_sunday = 7  # Set for next Sunday if it's past 10 AM

    next_sunday = now + timedelta(days=days_until_sunday)
    next_sunday_at_10am = next_sunday.replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)

    # Check if we need to add an hour to account for Daylight Saving Time
    if next_sunday_at_10am.hour < target_hour_utc:
        next_sunday_at_10am += timedelta(hours=1)

    return next_sunday_at_10am

async def weekly_task():
    await client.wait_until_ready()
    channel_id = 1227352261928292395  #  channel ID
    channel = client.get_channel(channel_id)
    print(f"Channel found: {channel}")

    while not client.is_closed():
        # Calculate when next to run right before the sleep to ensure accuracy
        next_run = next_sunday_at_10am_cst()
        now = datetime.now(timezone.utc)
        wait_time_in_seconds = (next_run - now).total_seconds()

        print(f"Waiting for {wait_time_in_seconds} seconds for the next trigger.")
        await asyncio.sleep(wait_time_in_seconds)

        # Recalculate 'now' after waking up to ensure we are still on schedule
        now = datetime.now(timezone.utc)
        if now >= next_run:  # Only attempt to send the message if the current time is on or past the scheduled time
            print("Attempting to send message")
            tasks_message = get_current_week_tasks(week_number=get_semester_week_number() + 1)  # Get tasks for the upcoming week
            try:
                await channel.send(tasks_message)
                print("Message sent successfully.")
            except Exception as e:
                print(f"Failed to send message: {e}")

            # Immediately calculate and wait again for the next run to avoid multiple messages
            next_run = next_sunday_at_10am_cst()
            wait_time_in_seconds = (next_run - datetime.now(timezone.utc)).total_seconds()
            print(f"Re-waiting for {wait_time_in_seconds} seconds for the next trigger.")
            await asyncio.sleep(wait_time_in_seconds)


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
