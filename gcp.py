from google.oauth2.service_account import Credentials
import gspread
import config


def gcp_init():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(
        config.CREDENTIAL_FILE, scopes=scopes
    )
    gc = gspread.authorize(credentials)
    spreadsheet_url = config.SPREADSHEET_URL
    spreadsheet = gc.open_by_url(spreadsheet_url)
    sheet_ic_log = spreadsheet.worksheet("IC Touch Log")
    sheet_program_log = spreadsheet.worksheet("Program Log")
    return sheet_ic_log, sheet_program_log
