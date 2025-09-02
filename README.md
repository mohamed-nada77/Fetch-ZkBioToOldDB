# Fetch-ZkBioToOldDB

## 📌 Overview
**Fetch-ZkBioToOldDB** is a lightweight integration script designed to **fetch employee information from ZKBioTime** and push it into an **old legacy database**.  
This serves as a **temporary bridge** so that the ERP system can access the data until a permanent integration is established.  

---

## ⚙️ How It Works
1. Connects to **ZKBioTime** system.  
2. Extracts employee records (attendance / user info).  
3. Maps and inserts the data into the **old database schema**.  
4. ERP system then consumes the updated legacy database.  

---

## 🚀 Use Case
- Temporary solution to keep ERP functional.  
- Avoids manual data entry during migration.  
- Ensures employee data is consistent across systems.  

---

## 🛠️ Requirements
- Python 3.9+  
- Packages (install via `pip install -r requirements.txt`):  
  - `requests`  
  - `pyodbc`  
- ODBC driver installed (e.g., Microsoft ODBC Driver 17/18 for SQL Server).  

---

## ▶️ Usage
1. Clone the repository:  
   ```bash
   git clone https://github.com/your-org/Fetch-ZkBioToOldDB.git
   cd Fetch-ZkBioToOldDB
