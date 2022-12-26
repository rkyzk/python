import gspread
from google.oauth2.service_account import Credentials
import hashlib
from decimal import Decimal
from datetime import datetime, timedelta

import os
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
    Prompts the users to enter a number and checks if the input
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
    Gets user Info of the given user ID.
    :argument: user_id: user ID
    :return: user info of the given user ID, or "None" if there's no data
             with the ID.
    :rtype: list or None
    """
    # Get all data from table "users"
    users = SHEET.worksheet("users").get_all_values()
    for user in users:    
        if user[2] == user_id:
            return user           
    else:
        return None

users_sheet = SHEET.worksheet("users")
accounts_sheet = SHEET.worksheet("accounts")
transactions_sheet = SHEET.worksheet("transactions")


def validate_pin(user_id, unhashed):
    """
    Gets the salt and the stored key for the given user ID from the database,
    hashes the argument "unhashed," and compares the new key with the stored key.
    Returns "True" if they are identical, otherwise returns "False."
    :arguments: user_id: user ID
                unhashed: pin that was entered by the user
    :return: True or False
    :rtype: boolean
    """
    user = get_user_info(user_id)
    salt = user[5].encode('utf-8')
    new_key = hashlib.pbkdf2_hmac('sha256', unhashed.encode('utf-8'),
                                  salt, 100000, dklen=128)
    if new_key == user[4]:
        return True
    else:
        return False


def hash_pin_with_salt(pin, salt):
    """Hash the pin with a given salt and return the key.
    :argument: pin
               salt
    :return: key
    :rtype: str
    """
    key = hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),  # convert the pin to bytes
        salt,
        100000,  # number of iterations of SHA256
        dklen=128  # get a 128-byte key
        )
    return key


def collect_mult_of_10(msg):
    """
    Prompts users to enter a value.
    If the input is a multiple of 10, add two decimal digits ".00"
    and return the value.
    :argument: msg: prompt message
    :returns: validated value added with two decimal digits ".00"
    :rtype: str
    """
    while True:
        value = input(msg)
        if value.isdigit() and value not in ["", "0"] and value.endswith("0"):
            decimal_val = ".".join([value, "00"])
            return decimal_val
        else:
            print("\nInvalid entry.")




def withdraw(amount, user):
    """
    Gets the balance of the user from table "Accounts."
    If the balance is greater than "amount,"
    subtracts it by "amount" and sets the new balance to
    "balance" in table "Accounts."
    :arguments: amount: amount of money to withdraw
                user: the user information
    """
    # Get the balance of the user.
    test = accounts_sheet.col_values(1)
    row_num = test.index(user[7]) + 1
    row = accounts_sheet.row_values(row_num) 
    balance = row[5]
    if Decimal(balance) < Decimal(amount):
        print("There isn't sufficient money in the account."
              "The session will be terminated.")
        exit()
    # Calculate the new balance.
    new_balance = Decimal(balance) - Decimal(amount)
    # Update the balance
    accounts_sheet.update(f"F{row_num}", str(new_balance))
    # Add transaction record
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    amt_minus = "".join(["-", amount])
    data = [user[7], "checking", user[2], "withdrawal", 
            "NA", "NA", amt_minus, date]
    transactions_sheet.append_row(data)
    print(f"\n${amount} has been withdrawn from your checking"
          f"account.\nPlease take your money and card.")


def deposit(amount, user):
    """
    Gets the balance of the user from table "Accounts."
    Calculates the new balance and updates table "Accounts"
    and "Transactions."

    :arguments: amount: amount of money to withdraw
                user: the user information
    """
    # Get the balance of the user.
    test = accounts_sheet.col_values(1)
    row_num = test.index(user[7]) + 1
    row = accounts_sheet.row_values(row_num) 
    balance = row[5]
    # Calculate the new balance.
    new_balance = Decimal(balance) + Decimal(amount)
    # Update the balance
    accounts_sheet.update(f"F{row_num}", str(new_balance))
    # Add transaction record
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    amt_plus = "".join(["+", amount])
    data = [user[7], "checking", user[2], "deposit", 
            "NA", "NA", amt_plus, date]
    transactions_sheet.append_row(data)
    print(f"\n${amount} has been added to your checking"
          f"account.\nPlease take your card.")


def get_recipient(account_id):
    """
    Gets user Info of the given account ID.

    :argument: account_id: account ID
    :return: user info of the given user ID, or "None" if there's no data
             with the ID.
    :rtype: list or None
    """
    # Get all data from table "users"
    users = SHEET.worksheet("users").get_all_values()
    for user in users:    
        if account_id in [user[6], user[7]]:
            return user           
    else:
        return None


def validate_len(length):
    """
    Prompts users to input notes and check the length.
    If the length is equal to or less than 35 characters,
    returns the input.  Otherwise prompts them to reenter notes.

    :argument: length: max number of characters in trsfer notes
    :return: trs_notes: transfer notes
    :rtype: str
    """
    while True:
        trs_notes = input(f"Enter transfer notes (optional, "
                          f"max {length} characters): \n")
        if len(trs_notes) <= length:
            return trs_notes
        else:
            print(f"\nYou entered more than {length} characters.")


def validate_val(val):
    """
    Returns "True" if the argument "val" is a non-zero
    whole number or a positive number with two decimal digits.
    (e.g. '50' or '50.00')

    :argument: val: value to be validated
    :return: True or False
    :rtype: boolean
    """
    if val in ["0", "0.00"]:
        print("Please enter a non-zero value.")
        return False
    elif val.isdigit():
        return True
    elif len(val) < 4:
        return False
    elif val[-3] == "." and val[:-3].isdigit() and val[-2:].isdigit():
        return True
    else:
        return False


def collect_val(msg):
    """
    Prompts users to input a value and validates it
    with "validate_transfer_val" function.  If "False" is returned,
    prompts them to reenter a valid value.
    Otherwise, if the input "value" is an integer,
    adds two decimal digits ".00" and returns the value.  If "value"
    already has two decimal digits, returns it as is.

    :argument: msg: prompt message
    :returns: validated value as is, or adds two decimal digits ".00" to it
    :rtype: str
    """
    while True:
        value = input(msg)
        if validate_val(value):
            if value.isdigit():
                decimal_val = value + ".00"
                return decimal_val
            else:
                return value
        else:
            print("Invalid entry.  Enter values with or without "
                  "number of cents (e.g. '50' or '50.00').")


def transfer(amount, user, account_id, recipient, recip_acct_id, trs_notes):
    """
    Calculates the new balances of the sender and the recipient,
    and update the data in tables "Accounts" and "Transactions.

    :arguments: amount: transfer amount
                user: information of the sender
                account_id: the sender's account ID
                recipient: information of the recipienet
                recip_acct_id: the recipient's account ID
    """
    # Get the balance of the sender.
    test = accounts_sheet.col_values(1)
    row_num = test.index(account_id) + 1
    row = accounts_sheet.row_values(row_num) 
    balance = row[5]
    # Calculate the new balance.
    new_balance = Decimal(balance) - Decimal(amount)
    # Update the balance
    accounts_sheet.update(f"F{row_num}", str(new_balance))
    # Add transaction record
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    amt_minus = "".join(["-", amount])
    if account_id[1] == "1":
        account_type = "saving"
    else:
        account_type = "checking"
    recip_name = " ".join([recipient[0], recipient[1]])
    trs_person = " ".join(["to", recip_name])
    data = [account_id, account_type, user[2], "transfer sent", 
            trs_person, trs_notes, amt_minus, date]
    transactions_sheet.append_row(data)
    # Calculate and update the recipient's database
    test = accounts_sheet.col_values(1)
    row_num = test.index(recip_acct_id) + 1
    row = accounts_sheet.row_values(row_num) 
    balance = row[5]
    # Calculate the new balance.
    new_balance = Decimal(balance) + Decimal(amount)
    # Update the balance
    accounts_sheet.update(f"F{row_num}", str(new_balance))
    # Add transaction record
    amt_plus = "".join(["+", amount])
    if recip_acct_id[1] == "1":
        account_type = "saving"
    else:
        account_type = "checking"
    sender_name = " ".join([user[0], user[1]])
    trs_person = " ".join(["from", sender_name])
    data = [recip_acct_id, account_type, recipient[2], "transfer received", 
            trs_person, trs_notes, amt_plus, date]
    transactions_sheet.append_row(data)
    print(f"\n${amount} has been transferred.\n"\
          "Please take your card.")


def get_balances(user):
    """
    Gets the balance of the savings and checking accounts
    of the user.

    :argument: user_id: user ID
    :return: balances of savings and checking accounts
    :rtype: list
    """
    # Get savings account info
    test = accounts_sheet.col_values(1)
    row_num = test.index(user[6]) + 1
    row = accounts_sheet.row_values(row_num) 
    svg_balance = [user[6], row[5]]
    row_num = test.index(user[7]) + 1
    row = accounts_sheet.row_values(row_num) 
    check_balance = [user[7], row[5]]
    list = [svg_balance, check_balance]
    return list


pin = "111111"
salt = os.urandom(32)
key = hash_pin_with_salt(pin, salt)
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
# Let the users input their pin.  If they get it wrong 4 times,
# the card will be deactivated (the flag value of the user will be set to
# "s" -- "s" for "suspended")
"""
n = 0
while n < 4:
    unhashed = input('Enter your pin: \n')
    if validate_pin(user_id, unhashed):
        print('\nLogin Success\n')
        break
    if n < 3:
        print("The pin is wrong.  Please try again.")
        n += 1
    else:
        n += 1
"""
# Set the user's full name into variable "name."
name = " ".join([user[0], user[1]])
# Have the users select the transaction they want to make.
"""
while True:
    print(f"Hello {name},\nSelect the type of transaction "
          "you wish to make:\n")
    print('a. Withdrawal')
    print('b. Deposit')
    print('c. Transfer')
    print('d. View your account balances')
    print('e. View your recent transactions (from the past 30 days')
    print('f. Exit\n')
"""
while True:
    choice = input('Enter a-f: \n').lower()
    if choice == "a":         # Withdrawal
        amount = collect_mult_of_10("Enter how much you'd like "
                                    "to withdraw in a multiple of 10: $\n")
        # Update the balance and transaction history of the user.
        withdraw(amount, user)
        break
    if choice == "b":         # Deposit
        amount = collect_mult_of_10("Enter how much you are "
                                    "depositing in a multiple of 10: $\n")
        # Update the balance and transaction history of the user.
        deposit(amount, user)
        break
    if choice == "c":         # Transfer
        while True:
            option = input("\nDo you wish to make a transfer "
                           "from your savings account,\n"
                           "or from your checking account?\n"
                           "Enter 'a' for savings account\n"
                           "'b' for checking account: \n").lower()
            if option == 'a':
                account_id = user[6]
                break
            elif option == 'b':
                account_id = user[7]
                break
            else:
                print("\nInvalid entry.  Enter 'a' or 'b'.")
        while True:
            # Have the users enter the recipient's account ID
            # and check the validity of the input.
            recip_acct_id = input("\nEnter the recipient's "
                                         "account ID: \n")
            recipient = get_recipient(recip_acct_id)
            if not recipient:
                print(f"\nThe given account ID {recip_acct_id} "
                      "is not valid.")
                while True:
                    option = input("Enter 'a' to abort the transaction, "
                                   "'b' to continue: \n").lower()
                    if option == "a":
                        print("Bye.  Have a nice day!")
                        exit()
                    elif option == "b":
                        break
                    else:
                        print("\nInvalid entry.")
                continue
            # In case the account ID from which the users want
            # to transfer the money is entered, tell them to reenter
            # the right account ID of the recipient.
            elif recip_acct_id == account_id:
                print("\nYou entered the ID of the account from which "
                      "you will make a transfer.\nPlease enter "
                      "the account ID of the recipient.")
                continue
            # Collect transfer amount.
            amount = collect_val("Enter the amount "
                                 "you will transfer: \n")
            # If there isn't enough money in the account,
            # print the note below and terminate the program.
            # Get the balance of the user.
            test = accounts_sheet.col_values(1)
            row_num = test.index(account_id) + 1
            row = accounts_sheet.row_values(row_num) 
            balance = row[5]
            if Decimal(balance) < Decimal(amount):
                print("There isn't sufficient money in the account."
                      "The session will be terminated.")
                exit()
            # Have the users enter transfer notes (max 35 characters).
            # Let them reenter the text if the length exceeds 35 characters.
            trs_notes = validate_len(35)
            # Print the transfer detail for confirmation.
            print(f"\nYou will transfer ${amount} to\n"
                  + " ".join([recipient[0], recipient[1]])
                  + f"\nAccount ID: {recip_acct_id}\n"
                    f"Transaction notes: {trs_notes}")
            while True:
                # Ask the users if the transfer can be carried out,
                # or they want to make changes.
                option = input("\nEnter 'a' to proceed with this "
                               "transfer,\nenter 'b' to make "
                               "changes: \n").lower()
                if option in ["a", "b"]:
                    break
                else:
                    print("Invalid entry")
            if option == "a":
                # Make updates regarding this transfer
                transfer(amount, user, account_id, recipient, recip_acct_id, trs_notes)     
                break
    if choice == "d":         # "View your balances" option
        # Get balances from DB and print them.
        list_balances = get_balances(user)
        print(f"\nYour savings account ID: {list_balances[0][0]}")
        print(f"Balance: ${list_balances[0][1]}")
        print(f"\nYour checking account ID: {list_balances[1][0]}")
        print(f"Balance: ${list_balances[1][1]}\n")
        break