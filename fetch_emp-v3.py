import requests
import pyodbc
from collections import defaultdict
from datetime import datetime
import os
import json

# Configuration
MDB_FILE_PATH = r"C:\Users\User\AppData\Local\VirtualStore\Program Files (x86)\AttMid-east\att2000.mdb"  # Path to Access MDB file
ZK_BIO_EMPLOYEES_URL = 'http://x:x/personnel/api/employees/'
ZK_BIO_TRANSACTIONS_URL = 'http://x:x/iclock/api/transactions/'
AUTH_URL = "http://x:x/jwt-api-token-auth/"
USERNAME = "admin"   #username
PASSWORD = "admin@123" #password 

def get_zkbio_token():
    headers = {"Content-Type": "application/json"}
    data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(AUTH_URL, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            return f"JWT {token}"
        else:
            print("Failed to retrieve token.")
    else:
        print(f"Failed to authenticate: {response.status_code}, {response.text}")
    return None

def fetch_all_employees_from_zkbio(token):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    employees = []
    url = ZK_BIO_EMPLOYEES_URL
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                employees.extend(data['data'])
                url = data.get('next')
            else:
                break
        else:
            print(f"Failed to fetch employees: {response.status_code}, {response.text}")
            break
    return employees

def fetch_all_transactions_from_zkbio(token):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    transactions = []
    url = ZK_BIO_TRANSACTIONS_URL
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                transactions.extend(data['data'])
                url = data.get('next')
            else:
                break
        else:
            print(f"Failed to fetch transactions: {response.status_code}, {response.text}")
            break
    return transactions

def check_and_update_userinfo(employees):
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={MDB_FILE_PATH};"
    
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            # Fetch existing employees from USERINFO
            cursor.execute("SELECT USERID, Badgenumber, Name FROM USERINFO")
            existing_users = {row.Badgenumber: row.USERID for row in cursor.fetchall()}
            
            zk_employees = {emp['emp_code']: emp for emp in employees}
            
            # Add new employees and remove old ones
            for emp_code, employee in zk_employees.items():
                if emp_code not in existing_users:
                    cursor.execute("""
                        INSERT INTO USERINFO (Badgenumber, Name) VALUES (?, ?)
                    """, (emp_code, employee['first_name']))
                    print(f"Added new employee: {emp_code} - {employee['first_name']}")
            
            for badgenumber in existing_users:
                if badgenumber not in zk_employees:
                    cursor.execute("DELETE FROM USERINFO WHERE Badgenumber = ?", (badgenumber,))
                    print(f"Deleted employee with Badgenumber: {badgenumber}")
            
            conn.commit()

    except pyodbc.Error as e:
        print(f"Error accessing the Access database: {e}")

def update_checkinout(transactions):
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={MDB_FILE_PATH};"
    
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            for transaction in transactions:
                emp_code = transaction.get("emp_code", "")
                punch_time = datetime.strptime(transaction.get("punch_time", ""), "%Y-%m-%d %H:%M:%S")
                punch_type = transaction.get("punch_type", "I")  # Default to 'I' (check-in)
                
                # Get the USERID for the emp_code from USERINFO
                cursor.execute("SELECT USERID FROM USERINFO WHERE Badgenumber = ?", emp_code)
                row = cursor.fetchone()
                if row:
                    userid = row.USERID
                    
                    # Check if this transaction already exists in CHECKINOUT
                    cursor.execute("""
                        SELECT COUNT(*) FROM CHECKINOUT WHERE USERID = ? AND CHECKTIME = ? AND CHECKTYPE = ?
                    """, (userid, punch_time, punch_type))
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        # Insert new transaction if it doesn't already exist
                        cursor.execute("""
                            INSERT INTO CHECKINOUT (USERID, CHECKTIME, CHECKTYPE)
                            VALUES (?, ?, ?)
                        """, (userid, punch_time, punch_type))
                        print(f"Added new transaction for USERID {userid} at {punch_time}")
                    else:
                        print(f"Transaction for USERID {userid} at {punch_time} already exists, skipping.")
            
            conn.commit()
            print("Updated CHECKINOUT with new transactions.")
    
    except pyodbc.Error as e:
        print(f"Error updating CHECKINOUT: {e}")

def main():
    token = get_zkbio_token()
    if not token:
        return

    employees = fetch_all_employees_from_zkbio(token)
    transactions = fetch_all_transactions_from_zkbio(token)
    
    check_and_update_userinfo(employees)
    update_checkinout(transactions)

if __name__ == "__main__":
    if os.path.isfile(MDB_FILE_PATH):
        print(f"Database found at: {MDB_FILE_PATH}.")
        main()
    else:
        print(f"Database file not found at: {MDB_FILE_PATH}. Please check the path.")
