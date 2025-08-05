import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.api
from statsmodels.api import Logit
from pysal.lib import weights
from pysal.explore import esda
from datetime import datetime
import numpy as np

# Step 1: Data Cleaning and Preparation
def load_and_clean_data(merged_data_file):
    """
    Load and clean the already merged data from Join.py
    """
    # Load the merged data
    data = pd.read_csv(merged_data_file)
    
    # Convert date columns to datetime
    if 'Date of interview' in data.columns:
        data['date'] = pd.to_datetime(data['Date of interview'], format='%d/%m/%Y', errors='coerce')
    
    # Calculate age if Year of birth is available
    if 'Year of birth' in data.columns:
        data['age'] = datetime.now().year - data['Year of birth']
    
    # Handle education encoding if available
    if 'Highest education' in data.columns:
        education_mapping = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
        data['education'] = data['Highest education'].map(education_mapping)
    
    # Handle missing values
    data = data.fillna({
        'Chronic illnesses': 0,  # Assume no chronic illnesses if missing
        'Symptoms': '',  # Empty string for text fields
        'Are you taking any medication today?': 'No',  # Default to No if missing
        'Do you think the medicine which you are currently taking contains antibiotics': 'No',  # Default to No if missing
    })
    
    # Create a simple geodataframe if coordinates are available
    # Note: This is optional and depends on your data structure
    if 'Longitude' in data.columns and 'Latitude' in data.columns:
        gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['Longitude'], data['Latitude']))
    else:
        # If no coordinates, create a regular dataframe
        gdf = data
    
    print(f"Loaded {len(data)} records from merged data")
    print(f"Columns available: {list(data.columns)}")
    
    return gdf

# Step 2: Descriptive Statistics
def descriptive_stats(data):
    """
    Generate descriptive statistics from the merged data
    """
    print("=== DESCRIPTIVE STATISTICS ===")
    
    # Check which columns are available and adapt accordingly
    available_columns = data.columns.tolist()
    print(f"Available columns: {available_columns}")
    
    # Medication usage analysis
    if 'Are you taking any medication today?' in data.columns:
        medication_use_freq = data['Are you taking any medication today?'].value_counts(normalize=True) * 100
        print("\nMedication Use Frequency:")
        print(medication_use_freq)
    else:
        medication_use_freq = None
        print("No medication usage data available")
    
    # Symptoms analysis
    if 'Symptoms' in data.columns:
        # Handle symptoms that might be comma-separated
        symptoms_data = data['Symptoms'].dropna()
        if len(symptoms_data) > 0:
            symptoms_summary = symptoms_data.str.split(',').explode().str.strip().value_counts()
            print("\nSymptoms Summary:")
            print(symptoms_summary.head(10))  # Show top 10 symptoms
        else:
            symptoms_summary = None
            print("No symptoms data available")
    else:
        symptoms_summary = None
        print("No symptoms column found")
    
    # Antibiotic awareness analysis
    if 'Do you think the medicine which you are currently taking contains antibiotics' in data.columns:
        antibiotic_awareness = data['Do you think the medicine which you are currently taking contains antibiotics'].value_counts(normalize=True) * 100
        print("\nAntibiotic Awareness:")
        print(antibiotic_awareness)
    else:
        antibiotic_awareness = None
        print("No antibiotic awareness data available")
    
    # Demographic analysis
    demographic_stats = {}
    
    if 'age' in data.columns:
        print(f"\nAge Statistics:")
        print(f"Mean age: {data['age'].mean():.1f}")
        print(f"Age range: {data['age'].min()} - {data['age'].max()}")
        demographic_stats['age'] = data['age'].describe()
    
    if 'education' in data.columns:
        education_dist = data['education'].value_counts(normalize=True) * 100
        print(f"\nEducation Distribution:")
        print(education_dist)
        demographic_stats['education'] = education_dist
    
    return medication_use_freq, symptoms_summary, antibiotic_awareness, demographic_stats

# Step 3: Spatial Analysis (Optional)
def spatial_analysis(gdf):
    """
    Perform spatial analysis if geographic data is available
    """
    print("=== SPATIAL ANALYSIS ===")
    
    # Check if we have a proper geodataframe with geometry
    if hasattr(gdf, 'geometry') and gdf.geometry is not None:
        try:
            # Spatial weights matrix
            w = weights.Queen.from_dataframe(gdf)
            
            # Check if we have medication data for spatial analysis
            if 'Are you taking any medication today?' in gdf.columns:
                # Convert to numeric for analysis
                medication_numeric = (gdf['Are you taking any medication today?'] == 'Yes').astype(int)
                
                # Moran's I for medication use
                moran = esda.Moran(medication_numeric, w)
                print(f"Moran's I: {moran.I:.4f}, p-value: {moran.p_sim:.4f}")
                
                # Hotspot mapping (Getis-Ord Gi*)
                gi = esda.GetisOrd_Local(medication_numeric, w)
                gdf['hotspot'] = gi.gi_stars
                
                # Visualize
                fig, ax = plt.subplots(1, 1, figsize=(10, 8))
                gdf.plot(column='hotspot', legend=True, ax=ax)
                plt.title('Medication Use Hotspots')
                plt.show()
                
            else:
                print("No medication data available for spatial analysis")
                
        except Exception as e:
            print(f"Spatial analysis failed: {e}")
            print("This might be due to insufficient geographic data or spatial structure")
    else:
        print("No geographic data available for spatial analysis")
        print("Skipping spatial analysis...")

# Step 4: Regression Analysis
def regression_analysis(data):
    """
    Perform regression analysis on available variables
    """
    print("=== REGRESSION ANALYSIS ===")
    
    # Check available columns for analysis
    available_cols = data.columns.tolist()
    print(f"Available columns for regression: {available_cols}")
    
    # Prepare variables for regression
    X_vars = []
    
    # Add demographic variables if available
    if 'age' in data.columns:
        X_vars.append('age')
    if 'education' in data.columns:
        X_vars.append('education')
    if 'Chronic illnesses' in data.columns:
        X_vars.append('Chronic illnesses')
    
    # Check for outcome variable
    outcome_var = None
    if 'Do you think the medicine which you are currently taking contains antibiotics' in data.columns:
        outcome_var = 'Do you think the medicine which you are currently taking contains antibiotics'
    elif 'Are you taking any medication today?' in data.columns:
        outcome_var = 'Are you taking any medication today?'
    
    if not X_vars:
        print("No suitable predictor variables found for regression")
        return None
    
    if not outcome_var:
        print("No suitable outcome variable found for regression")
        return None
    
    try:
        # Prepare data
        X = data[X_vars].copy()
        y = data[outcome_var].copy()
        
        # Handle missing values
        X = X.dropna()
        y = y[X.index]  # Align y with X
        
        # Convert outcome to binary if needed
        if y.dtype == 'object':
            y = (y == 'Yes').astype(int)
        
        # One-hot encode categorical variables
        X_encoded = pd.get_dummies(X, drop_first=True)
        
        # Add constant
        X_encoded = statsmodels.api.add_constant(X_encoded)
        
        # Fit logistic regression
        model = Logit(y, X_encoded).fit()
        print(f"\nLogistic Regression Results for: {outcome_var}")
        print(model.summary())
        
        return model
        
    except Exception as e:
        print(f"Regression analysis failed: {e}")
        return None

# Step 5: Visualization and Reporting
def visualize(data, medication_use_freq, symptoms_summary, antibiotic_awareness, demographic_stats):
    """
    Create visualizations based on available data
    """
    print("=== VISUALIZATION ===")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('CHATSCi-AMI Data Analysis Results', fontsize=16, fontweight='bold')
    
    # Plot 1: Medication Usage
    if medication_use_freq is not None:
        medication_use_freq.plot(kind='bar', ax=axes[0,0], color=['lightcoral', 'lightblue'])
        axes[0,0].set_title('Medication Usage Frequency')
        axes[0,0].set_ylabel('Percentage (%)')
        axes[0,0].tick_params(axis='x', rotation=45)
    else:
        axes[0,0].text(0.5, 0.5, 'No medication data available', ha='center', va='center', transform=axes[0,0].transAxes)
        axes[0,0].set_title('Medication Usage')
    
    # Plot 2: Antibiotic Awareness
    if antibiotic_awareness is not None:
        antibiotic_awareness.plot(kind='pie', autopct='%1.1f%%', ax=axes[0,1])
        axes[0,1].set_title('Antibiotic Awareness')
    else:
        axes[0,1].text(0.5, 0.5, 'No antibiotic awareness data available', ha='center', va='center', transform=axes[0,1].transAxes)
        axes[0,1].set_title('Antibiotic Awareness')
    
    # Plot 3: Age Distribution
    if 'age' in demographic_stats:
        data['age'].hist(bins=10, ax=axes[1,0], color='lightgreen', alpha=0.7)
        axes[1,0].set_title('Age Distribution')
        axes[1,0].set_xlabel('Age')
        axes[1,0].set_ylabel('Frequency')
    else:
        axes[1,0].text(0.5, 0.5, 'No age data available', ha='center', va='center', transform=axes[1,0].transAxes)
        axes[1,0].set_title('Age Distribution')
    
    # Plot 4: Education Distribution
    if 'education' in demographic_stats:
        demographic_stats['education'].plot(kind='bar', ax=axes[1,1], color='orange')
        axes[1,1].set_title('Education Level Distribution')
        axes[1,1].set_ylabel('Percentage (%)')
        axes[1,1].tick_params(axis='x', rotation=45)
    else:
        axes[1,1].text(0.5, 0.5, 'No education data available', ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('Education Distribution')
    
    plt.tight_layout()
    plt.show()
    
    # Additional symptoms plot if available
    if symptoms_summary is not None and len(symptoms_summary) > 0:
        plt.figure(figsize=(12, 8))
        symptoms_summary.head(10).plot(kind='barh', color='skyblue')
        plt.title('Top 10 Most Common Symptoms')
        plt.xlabel('Frequency')
        plt.tight_layout()
        plt.show()
    
    print("Visualizations completed!")

# Main Pipeline Execution
if __name__ == "__main__":
    print("=== CHATSCi-AMI DATA ANALYSIS PIPELINE ===")
    print("Loading merged data from Join.py output...")
    
    # Use the merged data file from Join.py
    merged_data_file = 'Data/merged_data.csv'
    
    try:
        # Load and clean the merged data
        cleaned_data = load_and_clean_data(merged_data_file)
        
        # Generate descriptive statistics
        stats = descriptive_stats(cleaned_data)
        
        # Perform spatial analysis (if geographic data available)
        spatial_analysis(cleaned_data)
        
        # Perform regression analysis
        regression = regression_analysis(cleaned_data)
        
        # Create visualizations
        visualize(cleaned_data, stats[0], stats[1], stats[2], stats[3])
        
        print("\n=== ANALYSIS COMPLETED ===")
        print("All analyses have been performed successfully!")
        
    except FileNotFoundError:
        print(f"Error: Could not find {merged_data_file}")
        print("Please run Join.py first to create the merged data file.")
        print("Or check if the file path is correct.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Please check your data format and try again.")