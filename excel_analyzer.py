import pandas as pd
from langchain_core.tools import tool

@tool
def analyze_blood_sugar_excel(file_path: str) -> str:
    """ Reads and analyzes the last 3 months blood sugar levels
        The file must have 'Blood_Sugar_mgDL' and 'Date' columns.
    """

    try:
        df = pd.read_excel(file_path)

        df.columns = [col.strip() for col in df.columns]

        if 'Blood_Sugar_mgDL' not in df.columns:
           return "Error: Could not find Blood_Sugar_mgDL column in the excel sheet"

        df['Blood_Sugar_mgDL'] = pd.to_numeric(df['Blood_Sugar_mgDL'], errors='coerce')
        
        clean_df = df.dropna(subset=['Blood_Sugar_mgDL'])

        if clean_df.empty:
           return "No Valid blood sugar data"

        total_readings = len(clean_df)

        avg_glucose = clean_df['Blood_Sugar_mgDL'].mean()
        max_glucose = clean_df['Blood_Sugar_mgDL'].max()
        min_glucose = clean_df['Blood_Sugar_mgDL'].min()

        estimated_hba1c = (avg_glucose + 46.7)/ 28.7

        high_readings = len(clean_df[clean_df['Blood_Sugar_mgDL'] > 180])
        low_readings = len(clean_df[clean_df['Blood_Sugar_mgDL'] < 70])
        normal_readings = total_readings - (high_readings + low_readings)

        #Return the summarized contextual block to the agent

        return (
            f"--- Spreadsheet Analysis Summary ({file_path}) ---\n"
            f"Total Logs Found: {total_readings} records\n"
            f"Average Blood Sugar: {round(avg_glucose, 1)} mg/dL\n"
            f"Estimated HbA1c from logs: {round(est_hba1c, 1)}%\n"
            f"Range: {int(min_glucose)} mg/dL to {int(max_glucose)} mg/dL\n"
            f"Time-in-Range Profile: Normal/Target: {normal_readings}, High (>180): {high_readings}, Low (<70): {low_readings}."

        )
    except FileNotFoundError:
        return f"Error: The file path '{file_path}' was not found. Please verify the filename and try again."
    except Exception as e:
        return f"Failed to parse Excel file due to an error: {str(e)}"
