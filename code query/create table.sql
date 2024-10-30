-- Table: Company
CREATE TABLE Company (
    id INT PRIMARY KEY,
    url NVARCHAR(255),
    name NVARCHAR(255),
    website NVARCHAR(255),
    description_short NVARCHAR(MAX)
);

-- Table: People
CREATE TABLE People (
    company_id INT,
    people_count INT,
    senior_people_count INT,
    FOREIGN KEY (company_id) REFERENCES Company(id)
);

-- Table: Contacts
CREATE TABLE Contacts (
    company_id INT,
    emails_count INT,
    personal_emails_count INT,
    phones_count INT,
    addresses_count INT,
    FOREIGN KEY (company_id) REFERENCES Company(id)
);

-- Table: Investments
CREATE TABLE Investments (
    company_id INT,
    investors_count INT,
    FOREIGN KEY (company_id) REFERENCES Company(id)
);

-- Table: Clients
CREATE TABLE Clients (
    company_id INT,
    clients_count INT,
    FOREIGN KEY (company_id) REFERENCES Company(id)
);

-- Table: Partners
CREATE TABLE Partners (
    company_id INT,
    partners_count INT,
    FOREIGN KEY (company_id) REFERENCES Company(id)
);

-- Table: Changes
CREATE TABLE Changes (
    company_id INT,
    changes_count INT,
    people_changes_count INT,
    contact_changes_count INT,
    FOREIGN KEY (company_id) REFERENCES Company(id)
);

CREATE TABLE users (
    id INT IDENTITY(1, 1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);
