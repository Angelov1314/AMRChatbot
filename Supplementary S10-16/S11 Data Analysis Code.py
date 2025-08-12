import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

# Function to censor email addresses for privacy
def censor_email(email):
    """
    Censor email addresses to format: first_letter*****@domain.com
    Example: 'hello@gmail.com' -> 'h*****@gmail.com'
    """
    if pd.isna(email) or email == '':
        return email
    
    email = str(email)
    if '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 1:
        return email
    
    censored_username = username[0] + '*' * (len(username) - 1)
    return f"{censored_username}@{domain}"

# Example: Generate hypothetical survey data
raw_data = pd.DataFrame({
    'Year of birth': [1995, 1982, 2001],
    'Education': ['College, university and above', 'Primary', 'Upper secondary'],
    'Occupation': ['Health worker', 'Farmer', 'Student'],
    'Email': ['hello@gmail.com', 'john.doe@yahoo.com', 'student123@university.edu'],
    'Symptoms can be treated by antibiotics': [
        'Diarrhoea; Pneumonia',
        'Flu; Pneumonia',
        'Diarrhoea; Flu'
    ],
    'Reported symptoms': [
        'Fever; Cough',
        'Cough; Diarrhoea',
        'Fever; Sore throat'
    ]
})

# Apply email censoring
raw_data['Email_censored'] = raw_data['Email'].apply(censor_email)
print("Original emails:", raw_data['Email'].tolist())
print("Censored emails:", raw_data['Email_censored'].tolist())

# 1. Data Cleaning: Age calculation and chunking
raw_data['Age'] = datetime.now().year - raw_data['Year of birth']
raw_data['Age group'] = pd.cut(raw_data['Age'], bins=[0, 29, 39, 100], labels=['20-29', '30-39', '40+'])

# 2. Dummy variable transformation for symptoms knowledge
symptom_list = ['Diarrhoea', 'Pneumonia', 'Flu']
for symptom in symptom_list:
    raw_data[f'Knowledge_{symptom}'] = raw_data['Symptoms can be treated by antibiotics'].apply(
        lambda x: int(symptom in x)
    )

# 3. Misuse/Knowledge scoring (example: Diarrhoea and Pneumonia are correct, Flu is not)
def score_knowledge(row):
    correct = {'Diarrhoea': 1, 'Pneumonia': 1, 'Flu': 0}
    score = 0
    for symptom in correct:
        if row[f'Knowledge_{symptom}'] == correct[symptom]:
            score += 1
        else:
            score -= 1
    return score
raw_data['Knowledge_score'] = raw_data.apply(score_knowledge, axis=1)

# 4. One-hot encoding for education and occupation
encoder = OneHotEncoder(sparse=False)
onehot = encoder.fit_transform(raw_data[['Education', 'Occupation']])
onehot_df = pd.DataFrame(onehot, columns=encoder.get_feature_names_out(['Education', 'Occupation']))
data = pd.concat([raw_data, onehot_df], axis=1)

# 5. Query: Mean knowledge score by age group and occupation
print('\nMean knowledge score by age group:')
print(data.groupby('Age group')['Knowledge_score'].mean())
print('\nMean knowledge score by occupation:')
print(data.groupby('Occupation')['Knowledge_score'].mean())

# 6. Simple regression: Predict knowledge score from demographics
X = data[['Age'] + list(onehot_df.columns)]
y = data['Knowledge_score']
reg = LogisticRegression(max_iter=1000)
reg.fit(X, y > y.median())  # Binary outcome for demonstration
print('\nFeature importance (regression coefficients):')
for name, coef in zip(X.columns, reg.coef_[0]):
    print(f'{name}: {coef:.2f}')