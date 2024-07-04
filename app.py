import sys
import tabula
import pandas as pd

# Path to the PDF file
pdf_path = sys.argv[1]

# Extract all tables from the PDF
all_tables = tabula.read_pdf(pdf_path, pages='all', area=(15,0,100,100), relative_area=True)

# Initialize an empty DataFrame to collect all rows
results_data = pd.DataFrame()

# Expected columns in the results tables
expected_columns = ["Rank", "Name", "Init", "Place", "Cl-G", "Countout", "Score"]

# Function to preprocess a table to split Cl-G and Countout if they are merged
def preprocess_table(table):
    # Ensure the table has at least the expected number of columns
    if table.shape[1] >= len(expected_columns):
        table.columns = expected_columns[:table.shape[1]]
    else:
        table.columns = expected_columns[:table.shape[1]] + ["Unknown"] * (len(expected_columns) - table.shape[1])

    # Handle specific preprocessing for merged columns
    if "Cl-G" in table.columns and (table["Countout"].isnull().all() or table["Countout"].eq("").all()):
        # Identify the problematic column
        problem_col = table.columns.get_loc("Cl-G")
        # Split the problematic column into Cl-G and Countout
        # This regex handles the CFTR-O table
        new_cols = table.iloc[:, problem_col].str.extract(r'(?P<Cl_G>CFTR-O)(?P<Countout>[0-9X]+)')
        if new_cols["Cl_G"][1] != "CFTR-O":  
            new_cols = table.iloc[:, problem_col].str.extract(r'(?P<Cl_G>F(P|T)R-O) (?P<Countout>[0-9X]+)')
        table["Cl-G"] = new_cols["Cl_G"]
        table["Countout"] = new_cols["Countout"] 
    return table

# Process each table extracted from the PDF
for table in all_tables:
    table = preprocess_table(table)
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