# Updated by Garvit

import streamlit as st
from pathlib import Path
import json
import random
import string

# ----------------------------------------------------
# BACKEND (Your Bank Class)
# ----------------------------------------------------
class Bank():
    database = 'database.json'
    data = []

    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            with open(database, 'w') as fs:
                fs.write("[]")
    except:
        pass

    @classmethod
    def _update(cls):
        with open(cls.database, 'w') as fs:
            fs.write(json.dumps(cls.data, indent=4))

    @staticmethod
    def _accountno():
        alpha = random.choices(string.ascii_letters, k=5)
        digits = random.choices(string.digits, k=4)
        id = alpha + digits
        random.shuffle(id)
        return "".join(id)

    # ---- METHODS ----
    def create_account(self, name, email, phone, pin):
        d = {
            "name": name,
            "email": email,
            "phone": phone,
            "pin": pin,
            "Account No.": Bank._accountno(),
            "balance": 0
        }
        Bank.data.append(d)
        Bank._update()
        return d["Account No."]

    def get_user(self, accno, pin):
        return [i for i in Bank.data if i["Account No."] == accno and i["pin"] == pin]

    def deposit(self, accno, pin, amount):
        user = self.get_user(accno, pin)
        if not user:
            return False, "User not found"

        if amount <= 0:
            return False, "Invalid amount"
        if amount > 10000:
            return False, "Amount exceeds limit"

        user[0]['balance'] += amount
        Bank._update()
        return True, "Amount deposited successfully"

    def withdraw(self, accno, pin, amount):
        user = self.get_user(accno, pin)
        if not user:
            return False, "User not found"

        if amount <= 0:
            return False, "Invalid amount"
        if amount > 10000:
            return False, "Amount exceeds limit"

        if user[0]['balance'] < amount:
            return False, "Insufficient balance"

        user[0]['balance'] -= amount
        Bank._update()
        return True, "Amount withdrawn successfully"

    def get_details(self, accno, pin):
        return self.get_user(accno, pin)

    def delete(self, accno, pin):
        user = self.get_user(accno, pin)
        if not user:
            return False
        Bank.data.remove(user[0])
        Bank._update()
        return True

    def update_details(self, accno, pin, name, email, phone, newpin):
        user = self.get_user(accno, pin)
        if not user:
            return False, "User not found"

        u = user[0]

        if name:  u["name"] = name
        if email: u["email"] = email
        if phone: u["phone"] = phone
        if newpin: u["pin"] = newpin

        Bank._update()
        return True, "Details updated"


# ----------------------------------------------------
# STREAMLIT FRONTEND
# ----------------------------------------------------
st.set_page_config(page_title="Banking System", page_icon="🏦", layout="centered")

st.title("🏦 Simple Banking System (Streamlit)")
bank = Bank()

menu = ["Create Account", "Deposit Money", "Withdraw Money", "View Details", "Update Details", "Delete Account"]
choice = st.sidebar.selectbox("Menu", menu)

# ----------------------------------------------
# CREATE ACCOUNT
# ----------------------------------------------
if choice == "Create Account":
    st.header("📝 Create New Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    pin = st.text_input("Create 4-digit PIN", type="password")

    if st.button("Create Account"):
        if len(phone) != 10 or not phone.isnumeric():
            st.error("Invalid phone number")
        elif len(pin) != 4 or not pin.isnumeric():
            st.error("PIN must be 4 digits")
        else:
            acc = bank.create_account(name, email, phone, pin)
            st.success(f"Account created successfully! Your Account Number: **{acc}**")

# ----------------------------------------------
# DEPOSIT MONEY
# ----------------------------------------------
elif choice == "Deposit Money":
    st.header("💰 Deposit Money")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1, step=1)

    if st.button("Deposit"):
        ok, msg = bank.deposit(acc, pin, amount)
        st.success(msg) if ok else st.error(msg)

# ----------------------------------------------
# WITHDRAW MONEY
# ----------------------------------------------
elif choice == "Withdraw Money":
    st.header("💵 Withdraw Money")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1, step=1)

    if st.button("Withdraw"):
        ok, msg = bank.withdraw(acc, pin, amount)
        st.success(msg) if ok else st.error(msg)

# ----------------------------------------------
# VIEW DETAILS
# ----------------------------------------------
elif choice == "View Details":
    st.header("📄 Account Details")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    if st.button("Get Details"):
        details = bank.get_details(acc, pin)
        if details:
            st.json(details[0])
        else:
            st.error("No user found")

# ----------------------------------------------
# UPDATE DETAILS
# ----------------------------------------------
elif choice == "Update Details":
    st.header("⚙ Update Account Details")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    name = st.text_input("New Name (leave blank to skip)")
    email = st.text_input("New Email")
    phone = st.text_input("New Phone")
    newpin = st.text_input("New PIN", type="password")

    if st.button("Update"):
        ok, msg = bank.update_details(acc, pin, name, email, phone, newpin)
        st.success(msg) if ok else st.error(msg)

# ----------------------------------------------
# DELETE ACCOUNT:
# ----------------------------------------------
elif choice == "Delete Account":
    st.header("🗑 Delete Account")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    if st.button("Delete"):
        if bank.delete(acc, pin):
            st.success("Account deleted successfully")
        else:
            st.error("User not found")

