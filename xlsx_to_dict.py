import pandas as pd
import json
import numpy as np

def split_date(date_str):
    # Split the date string into parts
    parts = date_str.split(":")[1].split("/")

    # Ensure the year, month, and day are in the desired format
    year = f"20{parts[2]:02}"
    month = parts[1].zfill(2)
    day = parts[0].zfill(2)

    return {
        "year": year,
        "month": month,
        "day": day
    }
    
def xlsx_to_dict(file_path, sheet_name):
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Initialize the data dictionary
        data_dict = {
            "students": []
        }
        
        activity_code = {
            "O": "Contact Institution",
            "N": "Student have not answered in the QnA session"
        }
        # Extract the date from the first cell in the Excel sheet
        raw_date = df.columns[0]
        date_variable = split_date(raw_date)
        
        max_count_of_y = -1
        # Iterate through rows (excluding the header) and count "Y" values
        for index, row in df.iterrows():
            adm_no = row[0]  # Assuming the first column contains student names
            if pd.notna(adm_no) and adm_no != "AD NO":
                    
                student_data = {
                    "admission_no": adm_no,
                    "date": date_variable,
                    "on_time": True,
                    "voice": False if row[2] == "M" else True,
                    "nb_sub": False if row[2] == "B" else True,
                    "mob_net": False if row[2] == "R" else True,
                    "camera": False if row[2] == "V" else True,
                    "full_class": True,
                    "activities": sum(1 for val in row[3:] if val == "Y"),
                    "engagement": False if row[2] == "L" else True,
                    "remarks": activity_code[row[2]] if row[2] == "O" or row[2] == "N" else ""     
                }
                
                
                count_of_y = student_data["activities"]
                
                if count_of_y > max_count_of_y:
                    max_count_of_y = count_of_y
                    
                    
                data_dict["students"].append(student_data)
                
        for student in data_dict["students"]:
            student["overall_performance_percentage"] = int((int(student["activities"]) / int(max_count_of_y))* 50) + 25 if student['nb_sub'] else 0 + 25 if student['engagement'] else 0
            student["activities"] =  f"{student['activities']}/{max_count_of_y}"
            student["overall_performance"] = "EXCELLENT" if student["overall_performance_percentage"] >= 85 else "GOOD" if student["overall_performance_percentage"] >= 50 else "AVERAGE" if student["overall_performance_percentage"] > 25 else "POOR"
                
       
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
