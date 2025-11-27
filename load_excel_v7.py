"""
Universal Excel loader for v7 format
This module can load the new Excel v7 structure
"""
import pandas as pd
import numpy as np


def load_from_excel_v7(excel_path: str) -> dict:
    """
    Load and parse Excel file v7 format.
    Returns dict with 'assumptions', 'monthly', 'yearly' DataFrames.
    
    v7 Structure:
    - Assumptions: rows 3-45 (0-indexed: 2-44), columns A-E
      Format: Category | Parameter | Value | Unit | Notes
    - Monthly: row 54=header (0-indexed: 53), rows 55-90=data (0-indexed: 54-89)
    - Yearly: row 93=header (0-indexed: 92), rows 94-96=data (0-indexed: 93-95)
    """
    print(f"Loading Excel v7 file: {excel_path}")
    
    # Read the Model sheet
    df = pd.read_excel(excel_path, sheet_name='Model', header=None)
    
    # ===== PARSE ASSUMPTIONS =====
    # Row 3 is header (0-indexed: 2), skip it
    # Rows 4-46 (0-indexed: 3-45), Columns A-E (0-4)
    assumptions_data = []
    for i in range(3, 46):  # rows 4-46 (skip row 3 which is header)
        if i >= len(df):
            break
        row = df.iloc[i, 0:5].values  # columns A-E
        
        category = row[0] if pd.notna(row[0]) else ''
        parameter = row[1] if pd.notna(row[1]) else ''
        value = row[2] if pd.notna(row[2]) else 0
        unit = row[3] if pd.notna(row[3]) else ''
        notes = row[4] if pd.notna(row[4]) else ''
        
        # Skip if parameter is empty or is the header row
        if parameter and str(parameter).lower() != 'parameter':
            assumptions_data.append({
                'Category': category,
                'Parameter': parameter,
                'Year 1': value,  # Keep as Year 1 for compatibility
                'Year 2': value,  # Duplicate value for Year 2
                'Year 3': value,  # Duplicate value for Year 3
                'Notes': notes    # Add notes column
            })
    
    assumptions_df = pd.DataFrame(assumptions_data)
    
    # ===== PARSE MONTHLY MODEL =====
    # Row 55 = header (0-indexed: 54)
    # Rows 56-91 = data (0-indexed: 55-90), 36 rows
    if len(df) > 55:
        # Get column names from row 55 (0-indexed: 54)
        monthly_columns = []
        for col_val in df.iloc[54, :]:
            if pd.notna(col_val) and str(col_val).strip() != '':
                monthly_columns.append(str(col_val))
        
        print(f"  Found {len(monthly_columns)} monthly columns")
        
        # Get data rows 56-91 (0-indexed: 55-90)
        monthly_data = []
        for i in range(55, 91):  # rows 56-91 (0-indexed 55-90)
            if i >= len(df):
                break
            row_values = df.iloc[i, :len(monthly_columns)].values
            row_dict = {}
            for j, col_name in enumerate(monthly_columns):
                value = row_values[j] if j < len(row_values) else 0
                row_dict[col_name] = value if pd.notna(value) else 0
            monthly_data.append(row_dict)
        
        monthly_df = pd.DataFrame(monthly_data)
    else:
        monthly_df = pd.DataFrame()
    
    # ===== PARSE YEARLY SUMMARY =====
    # Row 94 = header (0-indexed: 93)
    # Rows 95-97 = data (0-indexed: 94-96), 3 rows
    if len(df) > 94:
        # Get column names from row 94 (0-indexed: 93)
        yearly_columns = []
        for col_val in df.iloc[93, :]:
            if pd.notna(col_val) and str(col_val).strip() != '':
                yearly_columns.append(str(col_val))
        
        print(f"  Found {len(yearly_columns)} yearly columns")
        
        # Get data rows 95-97 (0-indexed: 94-96)
        yearly_data = []
        for i in range(94, 97):  # rows 95-97 (0-indexed 94-96)
            if i >= len(df):
                break
            row_values = df.iloc[i, :len(yearly_columns)].values
            row_dict = {}
            for j, col_name in enumerate(yearly_columns):
                value = row_values[j] if j < len(row_values) else 0
                row_dict[col_name] = value if pd.notna(value) else 0
            yearly_data.append(row_dict)
        
        yearly_df = pd.DataFrame(yearly_data)
    else:
        yearly_df = pd.DataFrame()
    
    print(f">>> Loaded {len(assumptions_df)} assumptions, {len(monthly_df)} monthly rows, {len(yearly_df)} yearly rows")
    
    return {
        'assumptions': assumptions_df,
        'monthly': monthly_df,
        'yearly': yearly_df
    }


if __name__ == '__main__':
    # Test the loader
    result = load_from_excel_v7('ai_finance_dynamic_model_v7_channels.xlsx')
    
    print("\n=== ASSUMPTIONS ===")
    print(result['assumptions'].head(10))
    print(f"Shape: {result['assumptions'].shape}")
    
    print("\n=== MONTHLY ===")
    print(result['monthly'].head(5))
    print(f"Shape: {result['monthly'].shape}")
    print(f"Columns: {list(result['monthly'].columns)}")
    
    print("\n=== YEARLY ===")
    print(result['yearly'])
    print(f"Shape: {result['yearly'].shape}")
