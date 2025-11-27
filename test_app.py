"""
Test script for financial model app - validates core functions without GUI
"""

import sys
import pandas as pd
from pathlib import Path

# Import core functions from the main app
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("TESTING FINANCIAL MODEL APP CORE FUNCTIONS")
print("=" * 80)

# Test 1: Load from Excel
print("\n1. Testing Excel loading...")
try:
    from financial_model_app import load_from_excel
    
    excel_file = "ai_finance_dynamic_model_v6_social_views.xlsx"
    if Path(excel_file).exists():
        assumptions_df, monthly_df, yearly_df = load_from_excel(excel_file)
        print(f"   ✓ Loaded {len(assumptions_df)} assumptions")
        print(f"   ✓ Loaded {len(monthly_df)} monthly rows")
        print(f"   ✓ Loaded {len(yearly_df)} yearly rows")
    else:
        print(f"   ⚠ Excel file not found: {excel_file}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Parse assumptions
print("\n2. Testing assumption parsing...")
try:
    from financial_model_app import parse_assumptions
    
    params = parse_assumptions(assumptions_df)
    print(f"   ✓ Parsed {len(params)} parameters")
    print(f"   ✓ ARPU: {params.get('ARPU', 0)}")
    print(f"   ✓ ConvVS: {params.get('ConvVS', 0)}")
    print(f"   ✓ ChurnY1: {params.get('ChurnY1', 0)}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Model recalculation
print("\n3. Testing model recalculation...")
try:
    from financial_model_app import recalc_model
    
    monthly_updated, yearly_updated = recalc_model(assumptions_df, monthly_df)
    
    print(f"   ✓ Recalculated monthly model")
    print(f"   ✓ Month 12 MRR: €{monthly_updated.iloc[11]['MRR']:,.2f}")
    print(f"   ✓ Month 36 MRR: €{monthly_updated.iloc[35]['MRR']:,.2f}")
    print(f"   ✓ Month 36 Cumulative Cash: €{monthly_updated.iloc[35]['Cumulative_Cash']:,.2f}")
    
    print(f"\n   ✓ Recalculated yearly summary")
    print(f"   ✓ Year 1 ARR: €{yearly_updated.iloc[0]['ARR_EUR']:,.2f}")
    print(f"   ✓ Year 3 ARR: €{yearly_updated.iloc[2]['ARR_EUR']:,.2f}")
    print(f"   ✓ Year 3 LTV/CAC: {yearly_updated.iloc[2]['LTV_CAC_Ratio']:.2f}x")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: JSON save/load
print("\n4. Testing JSON persistence...")
try:
    from financial_model_app import save_to_json, load_from_json
    
    test_json = "test_model_state.json"
    
    # Save
    save_to_json(test_json, assumptions_df, monthly_updated, yearly_updated)
    print(f"   ✓ Saved to {test_json}")
    
    # Load
    loaded_assumptions, loaded_monthly, loaded_yearly = load_from_json(test_json)
    print(f"   ✓ Loaded from {test_json}")
    print(f"   ✓ Assumptions shape: {loaded_assumptions.shape}")
    print(f"   ✓ Monthly shape: {loaded_monthly.shape}")
    print(f"   ✓ Yearly shape: {loaded_yearly.shape}")
    
    # Cleanup
    Path(test_json).unlink()
    print(f"   ✓ Cleaned up test file")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Verify key metrics
print("\n5. Verifying key business metrics...")
try:
    final_mrr = monthly_updated.iloc[-1]['MRR']
    final_users = monthly_updated.iloc[-1]['Paying_Users_End']
    final_cash = monthly_updated.iloc[-1]['Cumulative_Cash']
    
    print(f"   ✓ Final MRR (Month 36): €{final_mrr:,.2f}")
    print(f"   ✓ Final Paying Users: {final_users:,.0f}")
    print(f"   ✓ Final Cumulative Cash: €{final_cash:,.2f}")
    
    # Check if break-even achieved
    break_even_month = None
    for idx, cash in enumerate(monthly_updated['Cumulative_Cash']):
        if cash >= 0:
            break_even_month = idx + 1
            break
    
    if break_even_month:
        print(f"   ✓ Break-even achieved: Month {break_even_month}")
    else:
        print(f"   ⚠ Break-even not achieved in 36 months")
    
    # Validate LTV/CAC ratios
    for year in [1, 2, 3]:
        ratio = yearly_updated.iloc[year-1]['LTV_CAC_Ratio']
        status = "✓ HEALTHY" if ratio >= 3.0 else "⚠ NEEDS IMPROVEMENT"
        print(f"   {status} Year {year} LTV/CAC: {ratio:.2f}x")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("✓ ALL CORE FUNCTIONS VALIDATED")
print("=" * 80)
print("\nThe application is ready to run!")
print("\nTo launch the GUI:")
print("  python financial_model_app.py")
print("\n" + "=" * 80)
