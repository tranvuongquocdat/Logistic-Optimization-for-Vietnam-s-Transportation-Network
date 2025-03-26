import pandas as pd
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.distance_function import haversine_distance

# Read the coordinates file
df = pd.read_csv('vietnam_provinces_coordinates.csv')

# Create a dictionary to store distances
DISTANCE = {}

# Calculate distances between all pairs of provinces
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        province1 = df.iloc[i]['Province']
        province2 = df.iloc[j]['Province']
        
        lat1 = df.iloc[i]['Latitude']
        lon1 = df.iloc[i]['Longitude']
        lat2 = df.iloc[j]['Latitude']
        lon2 = df.iloc[j]['Longitude']
        
        # Calculate distance using haversine formula
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Store the distance in the dictionary
        DISTANCE[(province1, province2)] = distance
        DISTANCE[(province2, province1)] = distance  # Store reverse direction as well

# Print the distances
print("\nDistances between provinces (in kilometers):")
print("-" * 50)
for (prov1, prov2), dist in DISTANCE.items():
    print(f"{prov1} - {prov2}: {dist:.2f} km")
