import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from statsmodels.api import Logit
from pysal.lib import weights
from pysal.explore import esda
from datetime import datetime
import numpy as np

# Step 1: Data Cleaning and Preparation
def load_and_clean_data(enrollment_file, survey_file):
    # Load enrollment data
    enrollment = pd.read_csv(enrollment_file)  # Assume CSV format
    enrollment['date'] = pd.to_datetime(enrollment['Date of interview'], format='%d/%m/%Y')
    enrollment['age'] = datetime.now().year - enrollment['Year of birth']
    enrollment['education'] = enrollment['Highest education'].map({0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5})  # Ordinal encoding

    # Load survey data
    survey = pd.read_csv(survey_file)
    survey['date'] = pd.to_datetime(survey['Date of interview'], format='%d/%m/%Y')

    # Merge on mobile phone number or other unique ID
    data = pd.merge(enrollment, survey, on='Mobile phone number', suffixes=('_enroll', '_survey'))

    # Handle missing values
    data = data.fillna({
        'Chronic illnesses': 0,  # Assume no chronic illnesses if missing
        'Symptoms': '',  # Empty string for text fields
    })

    # Geocode (assume a shapefile for regions; replace with actual geocoding if needed)
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['Longitude'], data['Latitude']))  # Add lat/long if available

    return gdf

# Step 2: Descriptive Statistics
def descriptive_stats(data):
    # Frequencies
    antibiotic_use_freq = data['Taking medication'].value_counts(normalize=True) * 100
    symptoms_summary = data['Symptoms'].str.split(',').explode().value_counts()
    
    # Stratified by demographics
    use_by_age = data.groupby('age')['Taking medication'].mean()
    use_by_occupation = data.groupby('Occupation')['Taking medication'].mean()
    
    print("Antibiotic Use Frequency:\n", antibiotic_use_freq)
    print("Symptoms Summary:\n", symptoms_summary)
    
    return antibiotic_use_freq, symptoms_summary, use_by_age, use_by_occupation

# Step 3: Spatial Analysis
def spatial_analysis(gdf):
    # Spatial weights matrix
    w = weights.Queen.from_dataframe(gdf)  # Assume polygon geometry; adjust if points
    
    # Moran's I for antibiotic use
    moran = esda.Moran(gdf['Taking medication'], w)
    print("Moran's I:", moran.I, "p-value:", moran.p_sim)
    
    # Hotspot mapping (Getis-Ord Gi*)
    from pysal.explore import esda
    gi = esda.GetisOrd_Local(gdf['Taking medication'], w)
    gdf['hotspot'] = gi.gi_stars
    
    # Visualize
    gdf.plot(column='hotspot', legend=True)
    plt.title('Antibiotic Use Hotspots')
    plt.show()

# Step 4: Regression Analysis
def regression_analysis(data):
    # Logistic regression: Antibiotic belief ~ Demographics + Chronic illnesses
    X = data[['age', 'education', 'Occupation', 'Chronic illnesses']]
    X = pd.get_dummies(X, drop_first=True)  # One-hot encode categorical
    y = data['Antibiotic belief']  # Assume binary (1=Yes, 0=No)
    
    model = Logit(y, X).fit()
    print(model.summary())
    
    return model

# Step 5: Visualization and Reporting
def visualize(data, antibiotic_use_freq, symptoms_summary):
    # Bar chart for antibiotic use
    antibiotic_use_freq.plot(kind='bar')
    plt.title('Antibiotic Use Frequency')
    plt.show()
    
    # Pie chart for symptoms
    symptoms_summary.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Symptoms Distribution')
    plt.show()

# Main Pipeline Execution
if __name__ == "__main__":
    enrollment_file = 'enrollment_data.csv'  # Replace with actual file
    survey_file = 'survey_data.csv'  # Replace with actual file
    
    cleaned_data = load_and_clean_data(enrollment_file, survey_file)
    stats = descriptive_stats(cleaned_data)
    spatial_analysis(cleaned_data)
    regression = regression_analysis(cleaned_data)
    visualize(cleaned_data, stats[0], stats[1])