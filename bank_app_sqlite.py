# bank_app_sqlite.py
import sqlite3
import bcrypt
import random

# Connect to SQLite DB (file-based)
conn = sqlite3.connect("nexbank.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS customerDataTable (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    fullName TEXT,
    lastName TEXT,
    age INTEGER,
    occupation TEXT,
    address TEXT,
    email TEXT UNIQUE,
    phoneNumber TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customerAcctTable (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    customerID INTEGER,
    accountNumber TEXT UNIQUE,
    Balance REAL DEFAULT 0.0,
    FOREIGN KEY (customerID) REFERENCES customerDataTable(ID)
)
""")
conn.commit()

def createAccountNum():
    return "".join([str(random.randint(0, 9)) for _ in range(10)])

def registerCustomer():
    fullName = input("Full Name: ")
    lastName = input("Last Name: ")
    age = int(input("Age: "))
    occupation = input("Occupation: ")
    address = input("Address: ")
    email = input("Email: ")
    phoneNumber = input("Phone Number: ")
    password = input("Password: ")

    # hash the password and store as string
    hashedPassword = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        cursor.execute("""
            INSERT INTO customerDataTable (fullName, lastName, age, occupation, address, email, phoneNumber, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fullName, lastName, age, occupation, address, email, phoneNumber, hashedPassword))
        conn.commit()

        customerID = cursor.lastrowid
        accountNum = createAccountNum()
        cursor.execute("INSERT INTO customerAcctTable (customerID, accountNumber) VALUES (?, ?)", (customerID, accountNum))
        conn.commit()

        print(f"✅ Registration successful! Your account number is: {accountNum}")
    except Exception as e:
        print("❌ Error:", e)

def login():
    email = input("Email: ")
    password = input("Password: ")
    cursor.execute("SELECT ID, password FROM customerDataTable WHERE email = ?", (email,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode("utf-8"), result[1].encode("utf-8")):
        print("✅ Login successful!")
        return result[0]
    else:
        print("❌ Invalid credentials.")
        return None

def checkBalance(customerID):
    cursor.execute("SELECT Balance FROM customerAcctTable WHERE customerID = ?", (customerID,))
    result = cursor.fetchone()
    if result:
        print(f"💰 Balance: {result[0]}")
    else:
        print("❌ Account not found.")

def deposit(customerID):
    amount = float(input("Deposit Amount: "))
    cursor.execute("UPDATE customerAcctTable SET Balance = Balance + ? WHERE customerID = ?", (amount, customerID))
    conn.commit()
    print("✅ Deposit successful!")

def withdraw(customerID):
    amount = float(input("Withdraw Amount: "))
    cursor.execute("SELECT Balance FROM customerAcctTable WHERE customerID = ?", (customerID,))
    result = cursor.fetchone()
    if result and result[0] >= amount:
        cursor.execute("UPDATE customerAcctTable SET Balance = Balance - ? WHERE customerID = ?", (amount, customerID))
        conn.commit()
        print("✅ Withdrawal successful!")
    else:
        print("❌ Insufficient balance.")

def transfer(senderID):
    receiverAcct = input("Receiver Account Number: ")
    amount = float(input("Amount to Transfer: "))

    cursor.execute("SELECT Balance FROM customerAcctTable WHERE customerID = ?", (senderID,))
    senderBalance = cursor.fetchone()

    if senderBalance and senderBalance[0] >= amount:
        cursor.execute("UPDATE customerAcctTable SET Balance = Balance - ? WHERE customerID = ?", (amount, senderID))
        cursor.execute("UPDATE customerAcctTable SET Balance = Balance + ? WHERE accountNumber = ?", (amount, receiverAcct))
        conn.commit()
        print("✅ Transfer successful!")
    else:
        print("❌ Insufficient funds.")

def menu():
    customerID = None
    while True:
        print("\n--- NexBank Menu ---")
        print("1. Register")
        print("2. Login")
        print("3. Check Balance")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Transfer")
        print("7. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            registerCustomer()
        elif choice == "2":
            customerID = login()
        elif choice == "3" and customerID:
            checkBalance(customerID)
        elif choice == "4" and customerID:
            deposit(customerID)
        elif choice == "5" and customerID:
            withdraw(customerID)
        elif choice == "6" and customerID:
            transfer(customerID)
        elif choice == "7":
            break
        else:
            print("❌ Invalid option or login required.")

if __name__ == "__main__":
    menu()