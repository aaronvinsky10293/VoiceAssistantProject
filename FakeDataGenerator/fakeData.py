from faker import Faker
import pandas as pd
import random

# Description: This script generates fake data for a CRM system. The data is written to a CSV file.

# Instantiate Faker
fake = Faker()

# Create empty list
data = []

# Possible case statuses
case_statuses = ['Opened', 'Approved', 'Pending', 'Closed']

# Generate 100 rows
for _ in range(100):
    row = [
        fake.unique.random_number(),  # Customer_ID
        fake.first_name(),  # First_Name
        fake.last_name(),  # Last_Name
        fake.email(),  # Email
        fake.phone_number(),  # Phone_Number
        fake.random_int(min=1, max=100),  # Section
        fake.random_int(min=100, max=500),  # Block
        fake.random_int(min=500, max=1000),  # Lot
        fake.street_address(),  # Street_Address
        fake.city(),  # City
        fake.zipcode(),  # Zip_Code
        random.choice(case_statuses),  # Case_Status
        round(random.gauss(3000, 500), 2)  # Expected_Savings
    ]
    data.append(row)

# Convert list to DataFrame
df = pd.DataFrame(data, columns=['Customer_ID', 'First_Name', 'Last_Name', 'Email', 'Phone_Number', 'Section',
                                 'Block', 'Lot', 'Street_Address', 'City', 'Zip_Code', 'Case_Status', 'Expected_Savings'])

# Write DataFrame to CSV
df.to_csv('crm_data.csv', index=False)
