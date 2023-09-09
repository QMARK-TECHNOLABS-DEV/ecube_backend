import pandas as pd

def extract_unique_combinations(file_path, sheet_name):
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        df['class_name']= df['class_name'].str.replace(' ', '').str.lower()
        df['division']= df['division'].str.replace(' ', '').str.lower()
        
        # Group the data by the specified columns and iterate through unique combinations
        unique_combinations = df.groupby(['batch_year', 'class_name', 'division']).size().reset_index()

        for _, row in unique_combinations.iterrows():
            batch_year = row['batch_year']
            class_name = row['class_name']
            division = row['division']
            
            table_name = f"{batch_year}_{class_name}_{division}"
            print(table_name)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:
file_path = 'test_student_detail_ecube.xlsx'
sheet_name = 'Sheet1'
extract_unique_combinations(file_path, sheet_name)
