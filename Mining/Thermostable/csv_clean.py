import pandas as pd
import re

def extract_stability_percentage(csv_file, output_file):
    # Load the CSV file
    data = pd.read_csv(csv_file)

    # Define a function to extract the stability percentage
    def extract_percentage(stability_string):
        match = re.search(r"\d+\.\d+", stability_string)
        return float(match.group()) if match else None

    # Apply the function to the 'Stability' column and create a new column 'stable_percent'
    data['stable_percent'] = data['Stability'].apply(extract_percentage)

    # Save the updated DataFrame to a new CSV file
    data.to_csv(output_file, index=False)

# Example usage
csv_file = '/Users/moinkhwaja/Documents/GitHub/H/results.csv'  # Replace with the actual path to your CSV file
output_file = '/Users/moinkhwaja/Documents/GitHub/H/output.csv'  # Replace with the desired path for the output CSV
extract_stability_percentage(csv_file, output_file)
