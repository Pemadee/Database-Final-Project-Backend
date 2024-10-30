import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import urllib

# โหลดข้อมูลจากไฟล์ CSV
file_path = r'D:\งาน\Database\Final Project\aihitdata-uk-10k.csv'
data = pd.read_csv(file_path)

database_path = r'D:\งาน\Database\Final Project\database\Final_Project.db'
connection_string = f'sqlite:///{database_path}'

# สร้าง engine สำหรับการเชื่อมต่อ
engine = create_engine(
    connection_string,
    connect_args={'check_same_thread': False, 'timeout': 30}
)

# เตรียมข้อมูลและโหลดลงฐานข้อมูลทีละตาราง
# Insert data into Company table
companies_df = data[['id', 'url', 'name', 'website', 'description_short']]
companies_df.columns = ['id', 'url', 'name', 'website', 'description_short']
companies_df.to_sql('Company', con=engine, if_exists='append', index=False)

# Insert data into People table
people_df = data[['id', 'people_count', 'senior_people_count']]
people_df.columns = ['company_id', 'people_count', 'senior_people_count']
people_df.to_sql('People', con=engine, if_exists='append', index=False)

# Insert data into Contacts table
contacts_df = data[['id', 'emails_count', 'personal_emails_count', 'phones_count', 'addresses_count']]
contacts_df.columns = ['company_id', 'emails_count', 'personal_emails_count', 'phones_count', 'addresses_count']
contacts_df.to_sql('Contacts', con=engine, if_exists='append', index=False)

# Insert data into Investments table
investments_df = data[['id', 'investors_count']]
investments_df.columns = ['company_id', 'investors_count']
investments_df.to_sql('Investments', con=engine, if_exists='append', index=False)

# Insert data into Clients table
clients_df = data[['id', 'clients_count']]
clients_df.columns = ['company_id', 'clients_count']
clients_df.to_sql('Clients', con=engine, if_exists='append', index=False)

# Insert data into Partners table
partners_df = data[['id', 'partners_count']]
partners_df.columns = ['company_id', 'partners_count']
partners_df.to_sql('Partners', con=engine, if_exists='append', index=False)

# Insert data into Changes table
changes_df = data[['id', 'changes_count', 'people_changes_count', 'contact_changes_count']]
changes_df.columns = ['company_id', 'changes_count', 'people_changes_count', 'contact_changes_count']
changes_df.to_sql('Changes', con=engine, if_exists='append', index=False)

print("Data imported successfully!")
