import sys
import tabula
import pandas as pd

# Path to the PDF file
pdf_path = sys.argv[1]

# Extract all tables from the PDF
all_tables = tabula.read_pdf(pdf_path, pages='all', area=(15,0,100,100), relative_area=True)
for table in all_tables:
    print(table)

# Initialize an empty DataFrame to collect all rows
results_data = pd.DataFrame()

# Expected columns in the results tables
expected_columns = ["Rank", "Name", "Init", "Place", "Cl-G", "Countout", "Score"]

# Process each table extracted from the PDF
for table in all_tables:
    if table.shape[1] >= len(expected_columns):
        # Rename the columns for consistency
        table.columns = expected_columns[:table.shape[1]]
        # Define the columns of interest (ensure they exist in the DataFrame)
        columns_of_interest = ["Name", "Init", "Cl-G", "Countout", "Score"]
        existing_columns_of_interest = [col for col in columns_of_interest if col in table.columns]
        # Filter the table to include only the columns of interest
        filtered_table = table[existing_columns_of_interest]
        # Append the filtered table to the main DataFrame
        results_data = pd.concat([results_data, filtered_table], ignore_index=True)

# Group the data by 'Cl-G' column
grouped = results_data.groupby('Cl-G')

# Save each group to a separate CSV file
for cl_g_value, group in grouped:
    if len(cl_g_value) > 8:
        print(f"Skipped incorrectly read row with class {cl_g_value}")
        continue
    file_name = f"{pdf_path}_Grade_{cl_g_value}.csv"
    group.to_csv(file_name, index=False)
    print(f"Data for {cl_g_value} saved to {file_name}")

print("Data successfully extracted and split into separate files based on 'Cl-G' column.")