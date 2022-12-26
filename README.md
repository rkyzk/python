# General Overview of ATM System Application

Banking System Application is a Python ATM terminal application.  Users can make various imaginary transactions: withdrawals, deposits, transfers, viewing their balances and viewing recent transactions.  The data of the customers, accounts and transactions are stored in three separate tables named “Users,” “Accounts” and “Transactions” respectively in google spread sheet. 

### Notes about user and account IDs: 
- User IDs have 7 digits.  The first number tells which bank the customer belongs to.  (‘1’ indicates North Bank; ‘2’: East Bank; ‘3’: South Bank.)  The rest 6 digits are for identifying customers.  
- The account IDs have 8 digits.  The first number tells which bank the accounts belong to, just as user IDs, and the second number tells if the account is savings or checking account.  ‘1’ indicates savings account, and ‘2’ indicates checking account.  For example, 11000001 is an ID of a savings account at North Bank.  12000001 is an ID of a checking account at North Bank.
- Each customer should have unique user and account IDs.  


### How to use the program
- The users will be asked to choose choose which transactions they want to make
a.  Withdraw
b.  Deposit
c.  Transfer
d.  View the account balances
e.  View recent transactions (from the past 30 days)
f.  Exit

A. Withdraw
- Users are asked to enter the amount they want to withdraw in a multiple of 10.
- If the requested withdrawal amount is greater than the balance in their account, the system will tell the customers that there isn’t sufficient money for the transaction, and the program will be terminated.  
- Otherwise the new balance will be calculated by subtracting the withdrawal amount from the old balance.
- The balance will be updated, and the transaction record will be added to the database.  

B. Deposit
- In real scenario, users will insert money, and the machine will count the value of deposit.  In this program, the system asks the users to input the value manually. 
- The new balance will be calculated and will be updated in the database, and the transaction record will be added as well.

C. Transfer
- Users will input:
1. whether they are making the transfer from their savings account or checking account
2. the recipient’s account ID 
3. the amount of money to transfer 
4. transfer notes (optional, max 35 characters)

- They will be asked to reenter valid values if 
1. the recipient’s ID is not found in the database
2. the account ID from which the user wants to make the transfer is entered as recipient’s ID
3. empty strings or non-numeric values are entered as transfer amount

- The program will be terminated, if the specified account of the sender doesn’t have sufficient money for the transfer.

- Notes: Users can transfer money from their own checking account to their savings account, and vice versa.  
The money value should be entered in the form of an integer or with values of cents (e.g. “50” or “50.00”)

D. View your balances
- The system will obtain the balances of the user’s savings and checking accounts and will display the values in a table.  

E. View your transactions
- The system will get a list of transaction records of the user from the previous 30 days.  The transaction histories of savings and checking accounts will be shown in separate tables.

F. Exit
- The program will be terminated.  

Lastly, after each transaction, the system asks the users if they want to make further transactions.  Until they decide to exit the program, they can continue to make transactions.

## Future features:
- Currently I limited the length of transfer notes to 35 characters so the table of transaction history will not be distorted.  In the future, I will find a way to accommodate longer texts with line breaks in the column.  
- I will add a program to reset pin numbers in case customers forget their pins.

# Testing:
- I passed the code through CI Python Linter and confirmed there are no problems.
- I tested all possible input options and confirmed that the interaction between the system and the users flow well.
- I tested that if users enter invalid inputs, (such as characters, an empty string, spaces or 0 where a non-zero number is expected.) the system will ask the users to reenter a valid value.  
- I tested that all prompt messages are clear and that there’s no confusion for users as to how to use the program.  

## Bugs:


## Validator Testing: 
No errors were returned from https://pep8ci.herokuapp.com

## Deployment
This project was deployed using Code Institute's mock terminal for Heroku.
- Steps to deploy:
1. Fork or clone the repository
2. Create a new Heroku app
3. Set the buildpacks to Python and NodeJS in the order
4. Link the Heroku app to the repository
5. Click on Deploy

## Credits:
The code to hash the pin with salt was taken from the following site:

[How To Hash Passwords In Python]https://nitratine.net/blog/post/how-to-hash-passwords-in-python/

The section in this readme file "Deployment" was taken from the readme file of Love Sandwiches Project by Code Institute.