import os
import pandas as pd

# Directory containing the original CSV files
input_directory = 'football/csv'

# Directory to save the simplified CSV files
output_directory = 'football/simpified_csv'

# Number of samples to keep from each CSV
samples_to_keep = 1000  # Adjust 'x' to your desired number

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Loop through each CSV file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.csv'):
        # Construct the full file path
        input_file_path = os.path.join(input_directory, filename)
        
        # Read the CSV file
        df = pd.read_csv(input_file_path)
        
        # Replace NaN (missing values) with the string "None"
        df.fillna("None", inplace=True)
        
        # Keep only the first 'samples_to_keep' rows
        df_simplified = df.head(samples_to_keep)
        
        # Save the simplified DataFrame to the output directory
        output_file_path = os.path.join(output_directory, filename)
        df_simplified.to_csv(output_file_path, index=False)
        
        print(f"Simplified {filename}: {samples_to_keep} rows saved with 'None' for missing values.")

print(f"Simplification complete. Simplified files are saved in '{output_directory}'.")
