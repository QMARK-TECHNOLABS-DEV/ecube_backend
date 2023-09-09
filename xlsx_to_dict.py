import pandas as pd
import json

def xlsx_to_dict(file_path, sheet_name):
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Create the dictionary structure
        data_dict = {
            "Date": df.columns[0],
            "Students": []
        }

        # Iterate through rows (excluding the header)
        for index, row in df.iterrows():
            student_data = {
                "adm_no": row[0],  # Assuming the first column contains student names
                "FB": row[2],    # Adjust column indices as needed
                "A1": row[3],
                "A2": row[4],
                "A3": row[5],
                "A4": row[6],
                "A5": row[7],
                "A6": row[8],
                "A7": row[9],
                "A8": row[10]
            }
            data_dict["Students"].append(student_data)

        # Convert the dictionary to a JSON response
        json_response = json.dumps(data_dict, indent=4)

        return json_response

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Example usage:
file_path = 'temp.xlsx'
sheet_name = 'Sheet1'
result_json = xlsx_to_dict(file_path, sheet_name)

if result_json:
    print(result_json)
else:
    print("Failed to convert XLSX to dictionary.")
