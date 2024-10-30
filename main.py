import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# SQL Connection
# Local host
# server = 'LAPTOP-1A7RJNVJ\SQLEXPRESS'
# database = 'Final_Project'
# connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

database_path = 'Final_Project.db'

class UserCreate(BaseModel):
    username: str
    password: str

def register_user(user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, hashed_password.decode('utf-8')))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("Error registering user:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(user: UserCreate):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (user.username,))
        result = cursor.fetchone()
        if result and bcrypt.checkpw(user.password.encode('utf-8'), result[0].encode('utf-8')):
            return True
        else:
            return False
    except sqlite3.Error as e:
        print("Error logging in user:", e)
        return False
    finally:
        cursor.close()
        conn.close()

# Function to get data from SQL Server
def get_companies_all():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, name, website, description_short FROM Company")
        rows = cursor.fetchall()
        return rows
    except pyodbc.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_company_details(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query for Company details
        cursor.execute("SELECT * FROM Company WHERE id = ?", (company_id,))
        company = cursor.fetchone()

        if not company:
            return None

        # Query for People
        cursor.execute("SELECT * FROM People WHERE company_id = ?", (company_id,))
        people = cursor.fetchone()

        # Query for Contacts
        cursor.execute("SELECT * FROM Contacts WHERE company_id = ?", (company_id,))
        contacts = cursor.fetchone()

        # Query for Investments
        cursor.execute("SELECT * FROM Investments WHERE company_id = ?", (company_id,))
        investments = cursor.fetchone()

        # Query for Clients
        cursor.execute("SELECT * FROM Clients WHERE company_id = ?", (company_id,))
        clients = cursor.fetchone()

        # Query for Partners
        cursor.execute("SELECT * FROM Partners WHERE company_id = ?", (company_id,))
        partners = cursor.fetchone()

        # Query for Changes
        cursor.execute("SELECT * FROM Changes WHERE company_id = ?", (company_id,))
        changes = cursor.fetchone()

        return {
            "company": {
                "id": company[0],
                "url": company[1],
                "name": company[2],
                "website": company[3],
                "description_short": company[4]
            },
            "people": {
                "people_count": people[1],
                "senior_people_count": people[2]
            } if people else None,
            "contacts": {
                "emails_count": contacts[1],
                "personal_emails_count": contacts[2],
                "phones_count": contacts[3],
                "addresses_count": contacts[4]
            } if contacts else None,
            "investments": {
                "investors_count": investments[1]
            } if investments else None,
            "clients": {
                "clients_count": clients[1]
            } if clients else None,
            "partners": {
                "partners_count": partners[1]
            } if partners else None,
            "changes": {
                "changes_count": changes[1],
                "people_changes_count": changes[2],
                "contact_changes_count": changes[3]
            } if changes else None
        }

    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_people(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query for People and Company details
        cursor.execute("""
            SELECT p.company_id, p.people_count, p.senior_people_count, c.name
            FROM People p
            LEFT JOIN Company c
            ON p.company_id = c.id
            WHERE p.company_id = ?
        """, (company_id,))  

        people = cursor.fetchone()
        if not people:
            return None

        return {
            "people": {
                "company_id": people[0],
                "company_name": people[3],
                "people_count": people[1],
                "senior_people_count": people[2]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()
    
def get_more_detail(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query for more details about the Company
        cursor.execute("""
            SELECT c.id, p.people_count, p.senior_people_count, ct.emails_count, ct.personal_emails_count,
                   ct.phones_count, ct.addresses_count, i.investors_count, cl.clients_count, pn.partners_count,
                   ch.changes_count, ch.people_changes_count, ch.contact_changes_count
            FROM Company AS c
            LEFT JOIN People AS p ON c.id = p.company_id
            LEFT JOIN Contacts AS ct ON c.id = ct.company_id
            LEFT JOIN Investments AS i ON c.id = i.company_id
            LEFT JOIN Clients AS cl ON c.id = cl.company_id
            LEFT JOIN Partners AS pn ON c.id = pn.company_id
            LEFT JOIN Changes AS ch ON c.id = ch.company_id
            WHERE c.id = ?
        """, (company_id,))
        more_detail = cursor.fetchone()

        if not more_detail:
            return None

        return {
            "more_detail": {
                "company_id": more_detail[0],
                "people_count": more_detail[1],
                "senior_people_count": more_detail[2],
                "emails_count": more_detail[3],
                "personal_emails_count": more_detail[4],
                "phones_count": more_detail[5],
                "addresses_count": more_detail[6],
                "investors_count": more_detail[7],
                "clients_count": more_detail[8],
                "partners_count": more_detail[9],
                "changes_count": more_detail[10],
                "people_changes_count": more_detail[11],
                "contact_changes_count": more_detail[12]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_contact(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query for Contact details
        cursor.execute("""
            SELECT ct.company_id, ct.addresses_count, ct.emails_count, ct.personal_emails_count, ct.phones_count, cp.name
            FROM Contacts AS ct
            LEFT JOIN Company AS cp ON ct.company_id = cp.id
            WHERE ct.company_id = ?
        """, (company_id,))
        contact = cursor.fetchone()

        if not contact:
            return None

        return {
            "contact": {
                "company_id": contact[0],
                'addresses_count': contact[1],
                "emails_count": contact[2],
                "personal_emails_count": contact[3],
                "phones_count": contact[4],
                "company_name": contact[5]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_investment(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query for Investment details
        cursor.execute("""
            SELECT i.company_id, i.investors_count, cp.name
            FROM Investments AS i
            LEFT JOIN Company AS cp ON i.company_id = cp.id
            WHERE i.company_id = ?
        """, (company_id,))
        investment = cursor.fetchone()

        if not investment:
            return None

        return {
            "investment": {
                "company_id": investment[0],
                'investors_count': investment[1],
                "company_name": investment[2]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_top_investment(top: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query for top investments
        query = f"""
            SELECT i.company_id, i.investors_count, cp.name
            FROM Investments AS i
            LEFT JOIN Company AS cp ON i.company_id = cp.id
            ORDER BY i.investors_count DESC
            LIMIT ?
        """
        cursor.execute(query, (top,))
        top_investment = cursor.fetchall()

        # Convert rows to a list of dictionaries
        result_top_investment = []
        for row in top_investment:
            company_data = {
                "company_id": row[0],
                "investors_count": row[1],
                "name": row[2]
            }
            result_top_investment.append(company_data)

        if not result_top_investment:
            return None

        return result_top_investment

    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_top_client(top: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        query = f"""
            SELECT c.company_id, c.clients_count, cp.name
            FROM Clients AS c
            LEFT JOIN Company AS cp ON c.company_id = cp.id
            ORDER BY c.clients_count DESC
            LIMIT ?
        """
        cursor.execute(query, (top,))
        top_client = cursor.fetchall()
        
        result_top_client = []
        for row in top_client:
            company_data = {
                "company_id": row[0],
                "clients_count": row[1],
                "name": row[2]
            }
            result_top_client.append(company_data)
        return result_top_client

    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_client(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.company_id, c.clients_count, cp.name
            FROM Clients AS c
            LEFT JOIN Company AS cp ON c.company_id = cp.id
            WHERE c.company_id = ?
        """, (company_id,))
        client = cursor.fetchone()
        if not client:
            return None
        return {
            "client": {
                "company_id": client[0],
                "clients_count": client[1],
                "company_name": client[2]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_partner(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pn.company_id, pn.partners_count, cp.name
            FROM Partners AS pn
            LEFT JOIN Company AS cp ON pn.company_id = cp.id
            WHERE pn.company_id = ?
        """, (company_id,))
        partner = cursor.fetchone()
        if not partner:
            return None
        return {
            "partner": {
                "company_id": partner[0],
                "partners_count": partner[1],
                "company_name": partner[2]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_top_partner(top: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        query = f"""
            SELECT p.company_id, p.partners_count, cp.name
            FROM Partners AS p
            LEFT JOIN Company AS cp ON p.company_id = cp.id
            ORDER BY p.partners_count DESC
            LIMIT ?
        """
        cursor.execute(query, (top,))
        top_partner = cursor.fetchall()
        
        result_top_partner = []
        for row in top_partner:
            company_data = {
                "company_id": row[0],
                "partners_count": row[1],
                "name": row[2]
            }
            result_top_partner.append(company_data)
        return result_top_partner

    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_change(company_id: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ch.company_id, ch.changes_count, ch.people_changes_count, ch.contact_changes_count, cp.name
            FROM Changes AS ch
            LEFT JOIN Company AS cp ON ch.company_id = cp.id
            WHERE ch.company_id = ?
        """, (company_id,))
        change = cursor.fetchone()
        if not change:
            return None
        return {
            "change": {
                "company_id": change[0],
                "changes_count": change[1],
                "people_changes_count": change[2],
                "contact_changes_count": change[3],
                "name": change[4]
            }
        }
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_top_change(top: int, mode: int):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        if mode == 1:
            query = f"""
                SELECT ch.company_id, ch.changes_count, ch.people_changes_count, ch.contact_changes_count, cp.name
                FROM Changes AS ch
                LEFT JOIN Company AS cp ON ch.company_id = cp.id
                ORDER BY ch.changes_count DESC
                LIMIT ?
            """
        elif mode == 2:
            query = f"""
                SELECT ch.company_id, ch.changes_count, ch.people_changes_count, ch.contact_changes_count, cp.name
                FROM Changes AS ch
                LEFT JOIN Company AS cp ON ch.company_id = cp.id
                ORDER BY ch.people_changes_count DESC
                LIMIT ?
            """
        elif mode == 3:
            query = f"""
                SELECT ch.company_id, ch.changes_count, ch.people_changes_count, ch.contact_changes_count, cp.name
                FROM Changes AS ch
                LEFT JOIN Company AS cp ON ch.company_id = cp.id
                ORDER BY ch.contact_changes_count DESC
                LIMIT ?
            """

        cursor.execute(query, (top,))
        top_change = cursor.fetchall()
        
        result_top_change = []
        for row in top_change:
            company_data = {
                "company_id": row[0],
                "changes_count": row[1],
                "people_changes_count": row[2],
                "contact_changes_count": row[3],
                "name": row[4]
            }
            result_top_change.append(company_data)
        return result_top_change

    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_detail():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        query = """
            SELECT c.id, c.url, c.name, c.website, c.description_short, p.people_count, p.senior_people_count, 
                   ct.emails_count, ct.personal_emails_count, ct.phones_count, ct.addresses_count, 
                   i.investors_count, cl.clients_count, pn.partners_count, ch.changes_count, 
                   ch.people_changes_count, ch.contact_changes_count
            FROM Company AS c
            LEFT JOIN People AS p ON c.id = p.company_id
            LEFT JOIN Contacts AS ct ON c.id = ct.company_id
            LEFT JOIN Investments AS i ON c.id = i.company_id
            LEFT JOIN Clients AS cl ON c.id = cl.company_id
            LEFT JOIN Partners AS pn ON c.id = pn.company_id
            LEFT JOIN Changes AS ch ON c.id = ch.company_id
            LIMIT 5
        """
        cursor.execute(query)
        get_all_detail = cursor.fetchall()

        result_all_detail = []
        for row in get_all_detail:
            all_detail = {
                "company_id": row[0],
                "url": row[1],
                "name": row[2],
                "website": row[3],
                "description_short": row[4],
                "people_count": row[5],
                "senior_people_count": row[6],
                "emails_count": row[7],
                "personal_emails_count": row[8],
                "phones_count": row[9],
                "addresses_count": row[10],
                "investors_count": row[11],
                "clients_count": row[12],
                "partners_count": row[13],
                "changes_count": row[14],
                "people_changes_count": row[15],
                "contact_changes_count": row[16]
            }
            result_all_detail.append(all_detail)
        return result_all_detail
    except sqlite3.Error as e:
        print("Error accessing database:", e)
        return None
    finally:
        cursor.close()
        conn.close()

@app.post("/register")
def register(user: UserCreate):
    success = register_user(user)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed or username already exists")
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserCreate):
    success = login_user(user)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful"}

# Route to show data
@app.get("/companies")
def read_companies():
    companies = get_companies_all()
    if companies is None:
        raise HTTPException(status_code=500, detail="Error fetching companies from the database")

    result = []
    for company in companies:
        result.append({
            "id": company[0],  # เข้าถึงข้อมูลผ่าน index ของ tuple
            "url": company[1],
            "name": company[2],
            "website": company[3],
            "description_short": company[4]
        })
    return result

# Route to show company details
@app.get("/companies/{company_id}")
def read_company_details(company_id: int):
    company_details = get_company_details(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company_details

@app.get("/more_detail/{company_id}")
def read_more_detail(company_id: int):
    company_details = get_more_detail(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company_details

@app.get("/people/{company_id}")
def read_people(company_id: int):
    company_details = get_people(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/contact/{company_id}")
def read_contact(company_id: int):
    company_details = get_contact(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/investment/{company_id}")
def read_investment(company_id: int):
    company_details = get_investment(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/top_investment/{top}")
def read_top_investment(top: int):
    company_details = get_top_investment(top)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/top_client/{top}")
def read_top_client(top: int):
    company_details = get_top_client(top)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/client/{company_id}")
def read_client(company_id: int):
    company_details = get_client(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/partner/{company_id}")
def read_partner(company_id: int):
    company_details = get_partner(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/top_partner/{toprank}")
def read_top_partner(toprank: int):
    company_details = get_top_partner(toprank)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/change/{company_id}")
def read_change(company_id: int):
    company_details = get_change(company_id)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/top_change/{toprank}/{mode}")
def read_top_change(toprank: int,mode: int):
    company_details = get_top_change(toprank,mode)
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details

@app.get("/all_detail")
def read_all_detail():
    company_details = get_all_detail()
    if company_details is None:
        raise HTTPException(status_code=404, detail="name not found")
    return company_details
