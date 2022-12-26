import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('atm-system')

#users = SHEET.worksheet('users')
#data = users.get_all_values()
#print(data)

def check_id(msg, length):
    """
    Prompt the users to enter a number and check if the input
    is a whole number with the specified number of digits
    starting with bank code 1, 2 or 3.
    :param msg: prompt message
    :param length: the number of digits
    :return: the validated number
    :rtype: str
    """
    while True:
        id = input(msg)
        if id.isdigit() and len(id) == length:
            if id[0] in ["1", "2", "3"]:
                return id
        else:
            print("Please enter a valid ID.")


def get_user_info(user_id):
    """
    Get user Info of the given user ID.
    :argument: user_id: user ID
    :return: user info of the given user ID, or "None" if there's no data
             with the ID.
    :rtype: User or None
    """
    # Get all data from table "users"
    users = SHEET.worksheet("users").get_all_values()
    for user in users:    
        if user[2] == user_id:
            return user           
    else:
        return None

# print(get_user_info('1000001'))

# In real setting, the users will insert their cards, and the machine will
# read off their IDs, so there's no need to validate the values.
# But in this program I prepared validation since the users will input
# their IDs manually.
print("*****************")
print("     Hello!")
print("*****************")
while True:
    # Let the users enter their IDs and check if the input is
    # a 7-digit whole number starting with bank code 1, 2 or 3.
    user_id = check_id("Enter your user ID: \n", 7)
    # Get user info of the given ID from DB.
    # If no user with the ID is found, have the users reenter their IDs.
    user = get_user_info(user_id)
    if user:
        break
    else:
        print("Invalid entry.")
# If the card has been deactivated (if the flag value is set to "s" in table
# "Users," tell the users to call personnel, and terminate the program.
if user[8] == "s":
    print("\nYour card has been deactivatd.\nPlease call "
          "the number on the back of your card for assistance.")
    exit()

