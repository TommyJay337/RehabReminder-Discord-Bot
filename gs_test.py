import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('discord-bot-data-419816-220342db7060.json', scope)
gsheet_client = gspread.authorize(creds)

client_gspread = gspread.authorize(creds)

def test_google_sheet_access():
    # Open the spreadsheet by name using client_gspread
    sheet = client_gspread.open("Mod 8 Tasks").sheet1  # Use client_gspread here

    # Fetch a specific cell value
    test_cell_value = sheet.cell(1, 1).value  # This gets the value of the cell at row 1, column 1 (typically A1)
    print(f"Value in cell A1: {test_cell_value}")

    # Fetch the first row (useful for headers)
    headers = sheet.row_values(1)
    print(f"Headers: {headers}")

    # Fetch all records from the sheet (each row as a dictionary, assuming the first row has headers)
    records = sheet.get_all_records()
    print(f"First 5 records: {records[:5]}")  # Print the first 5 records for brevity

# Call the test function directly, no need to wait for Discord client
test_google_sheet_access()