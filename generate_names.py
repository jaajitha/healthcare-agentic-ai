import pandas as pd
from faker import Faker
import random

print("Loading dataset...")
df = pd.read_excel('data/raw/agentic_ai_patient_context_15000.csv.xlsx')
assert len(df) == 15000

fake = Faker('en_IN')
fake_us = Faker('en_US') # fallback for more entropy

print("Generating unique male names...")
names_male = set()
while len(names_male) < 15000:
    names_male.add(fake.name_male())
    # Add a fallback just in case en_IN doesn't have 15,000 unique male names
    if len(names_male) % 2000 == 0:
        names_male.add(fake.first_name_male() + " " + fake.last_name())

print("Generating unique female names...")
names_female = set()
while len(names_female) < 15000:
    names_female.add(fake.name_female())
    if len(names_female) % 2000 == 0:
        names_female.add(fake.first_name_female() + " " + fake.last_name())

names_male = list(names_male)
names_female = list(names_female)
random.shuffle(names_male)
random.shuffle(names_female)

patient_names = []
used_names = set()

m_idx = 0
f_idx = 0

print("Assigning names...")
for sex in df['sex']:
    if str(sex).lower().strip() == 'male':
        name = names_male[m_idx]
        while name in used_names:
            m_idx += 1
            name = names_male[m_idx]
        used_names.add(name)
        patient_names.append(name)
        m_idx += 1
    else:
        name = names_female[f_idx]
        while name in used_names:
            f_idx += 1
            name = names_female[f_idx]
        used_names.add(name)
        patient_names.append(name)
        f_idx += 1

print("Validating constraints...")
assert len(patient_names) == 15000
assert len(set(patient_names)) == 15000

df.insert(1, 'patient_name', patient_names)

print("Saving Excel...")
df.to_excel('data/raw/agentic_ai_patient_context_15000_with_names.xlsx', index=False)

print("Saving CSV...")
df.to_csv('data/raw/agentic_ai_patient_context_15000_with_names.csv', index=False)

print("Process completed successfully!")
