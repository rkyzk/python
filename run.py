import gspread
from google.oauth2.service_account import Credentials
from decimal import Decimal
from datetime import datetime, timedelta
import hashlib

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('atm-system')

# Set worksheets to variables
USERS = SHEET.worksheet("users")
ACCOUNTS = SHEET.worksheet("accounts")
TRANSACTIONS = SHEET.worksheet("transactions")


def validate_pin(user_id, salt):
    if username == "admin963":
        stored_key = get_admin_pass_info(username)[0]
        salt = get_admin_pass_info(username)[1]
        new_key = hash_pin_with_salt(password, salt)
        if new_key == stored_key:
            return True
    return False

def hash_pin_with_salt(pin, salt):
    """Hash the pin with a given salt and return the key.

    :argument: pin
               salt
    :return: key: hashed key
    :rtype: byte
    """
    key = hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),  # convert the pin to bytes
        salt,
        100000,  # number of iterations of SHA256
        dklen=128  # get a 128-byte key
        )
    return key

pin = input('Enter your pin: ')
string_salt = b'\xc9.\xd5\\SE\xd9\x15\x9e\xad[2$R\xdf&K\xfa\xe4E@(MR\x8a\xab\x0b\xb7}\xd2\x93\xbe'
arr2 = bytes(string_salt, 'utf-8')
print(string_salt)
new_key = hash_pin_with_salt(pin, arr2)
str_stored_key = b'\xfe\x96\xd5\x08s\xf5\x07\xd3a\x7fm\x1b\x80\x8f\xf5a0\xa6V\xf6\x92,Y\xe9Y\xe2\xb0\x11.On\xfb\x7f\x1b/x^\xbbi\x91\xec\x13\xa3c5,1\xf1\xaa\xf6\xd4\x17G]\xba\xd0Z\xc6\xca\x1c<\xe3\x82f\xa2Hv\x1b\xa2W\xf0\x86HK#\x8d\xec\x8f\x95\xf9\xf7\xe0\xd7\x97\x1c\xc5pz\x97&\x07M}\xc4\xc2\xe3\x0c\xe69\xa3Z\xc8\x15f\x00\xff\x82\x1ez\x15\xaeMz\xfa\x9a\xbeO,3XZa\xc1\xbd\xeb\x1dF\xb9'


def get_user_info(user_id):
    """
    Gets user Info of the given user ID.
    :argument: user_id: user ID
    :return: user info of the given user ID, or "None" if there's no data
             with the ID.
    :rtype: list or None
    """
    # Get all data from table "users"
    users = USERS.get_all_values()
    for user in users:
        if user[2] == user_id:
            return user
    else:
        return None


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
        if (value.isdigit() and value not in ["", "0"]
            and value.endswith("0") and not value.startswith("0")):
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
    test = ACCOUNTS.col_values(1)
    row_num = test.index(user[7]) + 1
    row = ACCOUNTS.row_values(row_num)
    balance = row[5]
    if Decimal(balance) < Decimal(amount):
        print("There isn't sufficient money in the account."
              "The session will be terminated.")
        exit()
    # Calculate the new balance.
    new_balance = Decimal(balance) - Decimal(amount)
    # Update the balance
    ACCOUNTS.update(f"F{row_num}", str(new_balance))
    # Add transaction record
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    amt_minus = "".join(["-", amount])
    data = [user[7], "checking", user[2], "withdrawal",
            "NA", "NA", amt_minus, date]
    TRANSACTIONS.append_row(data)
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
    test = ACCOUNTS.col_values(1)
    row_num = test.index(user[7]) + 1
    row = ACCOUNTS.row_values(row_num)
    balance = row[5]
    # Calculate the new balance.
    new_balance = Decimal(balance) + Decimal(amount)
    # Update the balance
    ACCOUNTS.update(f"F{row_num}", str(new_balance))
    # Add transaction record
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    amt_plus = "".join(["+", amount])
    data = [user[7], "checking", user[2], "deposit",
            "NA", "NA", amt_plus, date]
    TRANSACTIONS.append_row(data)
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
    users = USERS.get_all_values()
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
    if val in ["0", "0.00"] or val.startswith("0"):
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
    with "validate_val" function.  If "False" is returned,
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
    test = ACCOUNTS.col_values(1)
    row_num = test.index(account_id) + 1
    row = ACCOUNTS.row_values(row_num)
    balance = row[5]
    # Calculate the new balance.
    new_balance = Decimal(balance) - Decimal(amount)
    # Update the balance
    ACCOUNTS.update(f"F{row_num}", str(new_balance))
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
    TRANSACTIONS.append_row(data)
    # Calculate and update the recipient's database
    test = ACCOUNTS.col_values(1)
    row_num = test.index(recip_acct_id) + 1
    row = ACCOUNTS.row_values(row_num)
    balance = row[5]
    # Calculate the new balance.
    new_balance = Decimal(balance) + Decimal(amount)
    # Update the balance
    ACCOUNTS.update(f"F{row_num}", str(new_balance))
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
    TRANSACTIONS.append_row(data)
    print(f"\n${amount} has been transferred.\n"
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
    test = ACCOUNTS.col_values(1)
    row_num = test.index(user[6]) + 1
    row = ACCOUNTS.row_values(row_num)
    svg_balance = [user[6], row[5]]
    row_num = test.index(user[7]) + 1
    row = ACCOUNTS.row_values(row_num)
    check_balance = [user[7], row[5]]
    list = [svg_balance, check_balance]
    return list


def display_with_spaces(item_list):
    """
    Prints items in the argument "list" with the numbers of spaces
    indicated in "list_num."

    :argument: item_list: a record in transaction history
    """
    list_num = [25, 20, 30, 35, 10]
    str = ""
    space = " "
    for n, item in enumerate(item_list):
        num = list_num[n] - len(item)
        str = "".join([str, item + space*num])
    print(str)


def print_row(transaction_list):
    """
    Using "display_with_spaces" function,
    prints each row in the argument "list."

    :argument: transaction_list: list of transactions
    """
    for item in transaction_list:
        print(item)


def get_transactions(user_id):
    """
    Gets all data from table "Transactions" of the given user.
    """
    # Get the date time of 30 days ago in string.
    start_datetime = datetime.now() - timedelta(days=30)
    start_date_str = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # Get all transaction records of the given user
    transactions = TRANSACTIONS.get_all_values()
    list_transactions = []
    for transaction in transactions:
        if transaction[2] == user_id and transaction[7] >= start_date_str:
            list = [transaction[1], transaction[7], transaction[3],
                    transaction[4], transaction[5], transaction[6]]
            list_transactions.append(list)
    return list_transactions


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
    user_id = input("Enter your user ID: \n")
    # Get user info of the given ID from DB.
    # If no user with the ID is found, have the users reenter their IDs.
    user = get_user_info(user_id)
    if user:
        break
    else:
        print("Invalid entry.")
# Set the user's full name into variable "name."
name = " ".join([user[0], user[1]])
# Have the users select the transaction they want to make.
while True:
    print(f"Hello {name},\nSelect the type of transaction "
          "you wish to make:\n")
    print('a. Withdrawal')
    print('b. Deposit')
    print('c. Transfer')
    print('d. View your account balances')
    print('f. Exit\n')
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
                test = ACCOUNTS.col_values(1)
                row_num = test.index(account_id) + 1
                row = ACCOUNTS.row_values(row_num)
                balance = row[5]
                if Decimal(balance) < Decimal(amount):
                    print("There isn't sufficient money in the account."
                          "The session will be terminated.")
                    exit()
                # Have the users enter transfer notes (max 35 characters).
                # Let them reenter the text if the length exceeds 35 char.
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
                    transfer(amount, user, account_id, recipient,
                             recip_acct_id, trs_notes)
                    break
            break
        if choice == "d":         # "View your balances" option
            # Get balances from DB and print them.
            list_balances = get_balances(user)
            print(f"\nYour savings account ID: {list_balances[0][0]}")
            print(f"Balance: ${list_balances[0][1]}")
            print(f"\nYour checking account ID: {list_balances[1][0]}")
            print(f"Balance: ${list_balances[1][1]}\n")
            break
        if choice == "e":  # Exit
            print("Bye.  Have a nice day!")
            exit()
        else:
            print('Invalid entry.  Please try again.')
    while True:
        # Ask if the users want to make further transactions.
        # If they do, send them back to the selections of transactions.
        # If not, terminate the program.
        choice = input("Would you like to make further transactions? "
                       "(y/n): \n").lower()
        if choice == "n":
            print("Thank you.  Have a nice day!")
            exit()
        elif choice == "y":
            break
        else:
            print("Invalid entry.  Please enter 'y' or 'n'")
