'''
from dotenv import load_dotenv
import discord
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

from datetime import datetime, timedelta

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

     # Debug: Print the type of week numbers in records
    if records:
        print(f"Type of 'Week #' in records: {type(records[0].get('Week #'))}")

    # Filter tasks that match the given week number
    tasks_for_week = [record for record in records if record.get('Week #') == week_number]

    # Format the tasks into a message string
    if tasks_for_week:
        message = "Assignments/Tests for the current week of the module:\n"
        for task in tasks_for_week:
            message += f"- {task.get('Tasks')} (Due: {task.get('Due Date')})\n"

        if weeks_remaining > 0:
            message += f"\nYou're crushing it! Only {weeks_remaining} weeks left to go!"
        else: message += f"\nYou're almost there! This is the last week"

    else:
        message = "No assignments/tests found for the current week of the module."
        message += f"\nYou're crushing it! Only {weeks_remaining} weeks left to go!"
        
    return message


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
# Ignore messages from the bot itself
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        # Manually specify the week number here for testing
        tasks_message = get_current_week_tasks(week_number=5)  # Change 3 to your test week number
        await message.channel.send(tasks_message)

client.run(os.getenv('TOKEN'))
'''