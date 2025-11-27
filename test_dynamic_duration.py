#!/usr/bin/env python3
"""
Test script to verify dynamic simulation duration functionality.
"""

from financial_model_app_v2 import load_from_excel_v7, recalc_model

print("=" * 80)
print("TESTING DYNAMIC SIMULATION DURATION")
print("=" * 80)

# Load initial data
excel_path = 'ai_finance_dynamic_model_v7_channels.xlsx'
print(f"\nLoading data from {excel_path}...")
state = load_from_excel_v7(excel_path)

print(f"\n✓ Assumptions loaded: {len(state['assumptions'])} rows")
print(f"  Columns: {list(state['assumptions'].columns)}")
print(f"  First parameter: {state['assumptions'].iloc[0]['Parameter']} = {state['assumptions'].iloc[0]['Value']}")

# Test different durations
test_durations = [2, 3, 5, 10]

print("\n" + "=" * 80)
print("TESTING DIFFERENT SIMULATION DURATIONS")
print("=" * 80)

for n_years in test_durations:
    print(f"\n--- Testing {n_years} years ({n_years * 12} months) ---")
    
    monthly, yearly = recalc_model(state['assumptions'], state['monthly'], n_years=n_years)
    
    print(f"  Monthly data: {monthly.shape[0]} rows, {monthly.shape[1]} columns")
    print(f"  Yearly data: {yearly.shape[0]} rows, {yearly.shape[1]} columns")
    
    # Verify correct number of months and years
    assert monthly.shape[0] == n_years * 12, f"Expected {n_years * 12} monthly rows, got {monthly.shape[0]}"
    assert yearly.shape[0] == n_years, f"Expected {n_years} yearly rows, got {yearly.shape[0]}"
    
    # Check year values
    years_in_data = sorted(monthly['Year'].unique())
    expected_years = list(range(1, n_years + 1))
    assert years_in_data == expected_years, f"Expected years {expected_years}, got {years_in_data}"
    
    # Show some key metrics
    last_year = yearly.iloc[-1]
    print(f"  Year {int(last_year['Year'])} metrics:")
    print(f"    - End Paying Users: {int(last_year['End_Paying_Users']):,}")
    print(f"    - End MRR: €{int(last_year['End_MRR_EUR']):,}")
    print(f"    - ARR: €{int(last_year['ARR_EUR']):,}")
    print(f"    - Total New Customers: {int(last_year['Total_New_Customers']):,}")
    print(f"    - LTV/CAC Ratio: {last_year['LTV_CAC_Ratio']:.2f}x")
    print(f"  ✓ Test passed!")

print("\n" + "=" * 80)
print("ALL TESTS PASSED! ✓")
print("=" * 80)

print("\n📊 Summary:")
print("  - Assumptions: Single 'Value' column (same for all years)")
print("  - Monthly model: Dynamically generates n_years × 12 months")
print("  - Yearly model: Dynamically generates n_years summary rows")
print("  - Churn rates: Cycle through Y1/Y2/Y3 rates for years beyond 3")
print("  - Parameters: All use single value (no more Year 1/2/3 columns)")
print("\n✅ Ready to use in GUI with simulation duration control!")
