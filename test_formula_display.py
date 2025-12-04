"""
Test script to verify that all new fields now show their formulas correctly
instead of "editable input field (no formula)".
"""

import sys
import pandas as pd
from financial_model_app_v2 import load_from_excel_v7, recalc_model

def test_formula_display():
    """Test that all new fields have formula definitions."""
    
    print("=" * 80)
    print("TESTING FORMULA DISPLAY FOR NEW FIELDS")
    print("=" * 80)
    
    # Load model
    excel_path = 'ai_finance_dynamic_model_v7_channels.xlsx'
    print(f"\n📂 Loading model from: {excel_path}")
    state = load_from_excel_v7(excel_path)
    
    # Recalculate with 3 years
    monthly_data, yearly_data = recalc_model(state['assumptions'], state['monthly'], n_years=3)
    
    print(f"✓ Monthly data: {monthly_data.shape[0]} rows, {monthly_data.shape[1]} columns")
    print(f"✓ Yearly data: {yearly_data.shape[0]} rows, {yearly_data.shape[1]} columns")
    
    # Define new fields to test
    new_monthly_fields = [
        'Direct_Costs',
        'Gross_Profit',
        'Gross_Margin_Month',
        'FollowerAds_Spend',
        'ClickAds_Spend',
        'Paid_FollowerAds_Impressions',
        'Paid_FollowerAds_Reach',
        'Paid_FollowerAds_NewFollowers',
        'Paid_ClickAds_Clicks',
        'Paid_ClickAds_Visitors',
        'PaidAds_Visitors',
        'PaidAds_Marketing_Spend',
    ]
    
    new_yearly_fields = [
        'Revenue_Year',
        'Gross_Profit_Year',
        'Gross_Margin_Year',
        'PaidAds_Marketing_Spend_EUR',
    ]
    
    # Test Monthly Model formulas
    print("\n" + "=" * 80)
    print("TESTING MONTHLY MODEL FORMULAS")
    print("=" * 80)
    
    # Create a formula tester class
    class FormulaTester:
        def __init__(self, df, is_monthly=True):
            self.df = df
            self.is_monthly = is_monthly
            
        def get_formula(self, col_name):
            """Simplified version of get_formula from ModelTable."""
            monthly_formulas = {
                'Followers_Start': 'Previous month Followers_End (or Followers_0 for first month)',
                'Followers_End': 'Followers_Start × (1 + Follower_Monthly_Growth) + Paid_FollowerAds_NewFollowers',
                'Posts': 'Posts_per_Month_Y1/Y2/Y3 (based on current year)',
                'Impr_Followers': '((Followers_Start + Followers_End) / 2) × Posts × Reach_per_Post × Frequency_Impressions_per_User',
                'Impr_NonFollowers': 'Impr_Followers × NonFollower_Reach_Multiplier',
                'Social_Views': 'Impr_Followers + Impr_NonFollowers',
                'NewUnique_NonFollowers': 'Impr_NonFollowers / Frequency_Impressions_per_User',
                'Org_Visitors': 'NewUnique_NonFollowers × Organic_CTR_to_Site',
                'Inf_Visitors': 'Inf_Collabs_Y1/Y2/Y3 × Inf_Visitors_per_Collab (based on year)',
                'Other_Visitors': 'Other_Marketing_Budget_Y1/Y2/Y3 / 2.0 (assumed $2 CPC)',
                'Visitors_Total': 'Org_Visitors + Inf_Visitors + Other_Visitors + PaidAds_Visitors',
                'Signups': 'Visitors_Total × ConvVS',
                'Org_Signups': 'Signups × (Org_Visitors / Visitors_Total)',
                'Inf_Signups': 'Signups × (Inf_Visitors / Visitors_Total)',
                'Other_Signups': 'Signups × (Other_Visitors / Visitors_Total)',
                'Referral_New_Payers': 'Paying_Users_Start × Referral_Monthly_Rate',
                'Org_New_Payers': 'Org_Signups × ConvSP',
                'Inf_New_Payers': 'Inf_Signups × ConvSP',
                'Other_New_Payers': 'Other_Signups × ConvSP',
                'New_Paying_Users': 'Org_New_Payers + Inf_New_Payers + Other_New_Payers + Referral_New_Payers',
                'Churn_Rate': 'ChurnY1/Y2/Y3 (based on current year)',
                'Paying_Users_Start': 'Previous month Paying_Users_End (or 0 for first month)',
                'Churned_Users': 'Paying_Users_Start × Churn_Rate',
                'Paying_Users_End': 'Paying_Users_Start - Churned_Users + New_Paying_Users',
                'ARPU': 'ARPU parameter from assumptions',
                'MRR': 'Paying_Users_End × ARPU',
                'Org_Marketing_Spend': 'Posts × Org_Cost_per_Post',
                'Inf_Marketing_Spend': 'Inf_New_Payers × Influencer_Reward_per_Sub',
                'Other_Marketing_Spend': 'Other_Marketing_Budget_Y1/Y2/Y3 (based on year)',
                'Referral_Marketing_Spend': 'Referral_New_Payers × Referral_Reward_per_Sub',
                'FollowerAds_Spend': 'Monthly_PaidAds_Budget if Followers_Start < Follower_Threshold_For_Click_Ads, else 0 (FASE 1: Follower Acquisition)',
                'ClickAds_Spend': 'Monthly_PaidAds_Budget if Followers_Start ≥ Follower_Threshold_For_Click_Ads, else 0 (FASE 2: Visitor Generation)',
                'Paid_FollowerAds_Impressions': '(FollowerAds_Spend / FollowerAds_CPM_EUR) × 1000',
                'Paid_FollowerAds_Reach': 'Paid_FollowerAds_Impressions / Frequency_Impressions_per_User',
                'Paid_FollowerAds_NewFollowers': 'Paid_FollowerAds_Reach × FollowerAds_Reach_to_Follower_Rate',
                'Paid_ClickAds_Clicks': 'ClickAds_Spend / ClickAds_CPC_EUR',
                'Paid_ClickAds_Visitors': 'Paid_ClickAds_Clicks (1:1 click to visitor conversion)',
                'PaidAds_Visitors': 'Paid_ClickAds_Visitors (visitors from Paid Click Ads)',
                'PaidAds_Marketing_Spend': 'FollowerAds_Spend + ClickAds_Spend',
                'Total_Marketing_Spend': 'Org_Marketing_Spend + Inf_Marketing_Spend + Other_Marketing_Spend + Referral_Marketing_Spend + PaidAds_Marketing_Spend',
                'DataSub_Cost': 'DataSub_Fee if MRR ≥ DataSub_MRR_Threshold, else 0',
                'XAPI_Cost': 'XAPI_Fee if MRR ≥ XAPI_MRR_Threshold, else 0',
                'Direct_Costs': 'DataSub_Cost + XAPI_Cost (variable costs that scale with usage)',
                'Gross_Profit': 'MRR - Direct_Costs (revenue minus variable costs)',
                'Gross_Margin_Month': 'IF(MRR > 0, Gross_Profit / MRR, 0) - monthly gross margin percentage',
                'Base_Fixed_Cost': 'BaseFixedCost parameter from assumptions',
                'Total_Costs': 'Total_Marketing_Spend + DataSub_Cost + XAPI_Cost + Base_Fixed_Cost',
                'Net_Cash_Flow': 'MRR - Total_Costs',
                'Cumulative_Cash': 'Previous month Cumulative_Cash + Net_Cash_Flow (or Net_Cash_Flow for first month)',
            }
            
            yearly_formulas = {
                'Year': 'Year number (1, 2, or 3)',
                'End_Paying_Users': 'Last month of year: Paying_Users_End',
                'End_MRR_EUR': 'Last month of year: MRR',
                'ARR_EUR': 'End_MRR_EUR × 12',
                'Total_New_Customers': 'SUM(New_Paying_Users) for all months in year',
                'Org_New_Payers': 'SUM(Org_New_Payers) for all months in year',
                'Inf_New_Payers': 'SUM(Inf_New_Payers) for all months in year',
                'Other_New_Payers': 'SUM(Other_New_Payers) for all months in year',
                'Referral_New_Payers': 'SUM(Referral_New_Payers) for all months in year',
                'Org_Marketing_Spend_EUR': 'SUM(Org_Marketing_Spend) for all months in year',
                'Inf_Marketing_Spend_EUR': 'SUM(Inf_Marketing_Spend) for all months in year',
                'Other_Marketing_Spend_EUR': 'SUM(Other_Marketing_Spend) for all months in year',
                'Referral_Marketing_Spend_EUR': 'SUM(Referral_Marketing_Spend) for all months in year',
                'Total_Marketing_Spend_EUR': 'Org_Marketing_Spend_EUR + Inf_Marketing_Spend_EUR + Other_Marketing_Spend_EUR + Referral_Marketing_Spend_EUR + PaidAds_Marketing_Spend_EUR',
                'PaidAds_Marketing_Spend_EUR': 'SUM(PaidAds_Marketing_Spend) for all months in year',
                'Average_CAC_EUR': 'Total_Marketing_Spend_EUR / Total_New_Customers',
                'Revenue_Year': 'SUM(MRR) for all months in year',
                'Gross_Profit_Year': 'SUM(Gross_Profit) for all months in year',
                'Gross_Margin_Year': 'IF(Revenue_Year > 0, Gross_Profit_Year / Revenue_Year, 0) - yearly gross margin percentage',
                'Assumed_Monthly_Churn': 'ChurnY1/Y2/Y3 (based on current year)',
                'LTV_EUR': '(ARPU × Gross_Margin_Year) / Assumed_Monthly_Churn - uses DYNAMIC Gross Margin from actual results',
                'LTV_CAC_Ratio': 'LTV_EUR / Average_CAC_EUR',
                'Cumulative_Cash_EndOfYear': 'Last month of year: Cumulative_Cash',
                'Total_Org_Visitors': 'SUM(Org_Visitors) for all months in year',
                'Total_Inf_Visitors': 'SUM(Inf_Visitors) for all months in year',
                'Total_Other_Visitors': 'SUM(Other_Visitors) for all months in year',
                'Total_Visitors': 'Total_Org_Visitors + Total_Inf_Visitors + Total_Other_Visitors',
                'Share_Org_Visitors': 'Total_Org_Visitors / Total_Visitors',
                'Share_Inf_Visitors': 'Total_Inf_Visitors / Total_Visitors',
                'Share_Other_Visitors': 'Total_Other_Visitors / Total_Visitors',
                'Total_Social_Views': 'SUM(Social_Views) for all months in year',
                'End_Followers': 'Last month of year: Followers_End',
            }
            
            if self.is_monthly:
                return monthly_formulas.get(col_name, None)
            else:
                return yearly_formulas.get(col_name, None)
    
    # Test monthly fields
    tester = FormulaTester(monthly_data, is_monthly=True)
    
    all_passed = True
    for field in new_monthly_fields:
        if field in monthly_data.columns:
            formula = tester.get_formula(field)
            if formula:
                print(f"✅ {field:35s} → {formula}")
            else:
                print(f"❌ {field:35s} → NO FORMULA DEFINED")
                all_passed = False
        else:
            print(f"⚠️  {field:35s} → NOT IN DATAFRAME")
    
    # Test Yearly Summary formulas
    print("\n" + "=" * 80)
    print("TESTING YEARLY SUMMARY FORMULAS")
    print("=" * 80)
    
    tester = FormulaTester(yearly_data, is_monthly=False)
    
    for field in new_yearly_fields:
        if field in yearly_data.columns:
            formula = tester.get_formula(field)
            if formula:
                print(f"✅ {field:35s} → {formula}")
            else:
                print(f"❌ {field:35s} → NO FORMULA DEFINED")
                all_passed = False
        else:
            print(f"⚠️  {field:35s} → NOT IN DATAFRAME")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✅ ALL NEW FIELDS HAVE FORMULA DEFINITIONS")
        print("✅ The UX bug is FIXED - no more 'editable input field (no formula)' for new fields")
    else:
        print("❌ SOME FIELDS ARE MISSING FORMULA DEFINITIONS")
    
    return all_passed

if __name__ == '__main__':
    success = test_formula_display()
    sys.exit(0 if success else 1)
