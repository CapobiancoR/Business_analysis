from financial_model_app import *

assumptions_df, monthly_df, yearly_df = load_from_excel('ai_finance_dynamic_model_v6_social_views.xlsx')
monthly_updated, yearly_updated = recalc_model(assumptions_df, monthly_df)

print("Year 3 Summary:")
print(yearly_updated.iloc[2])

print("\nYear 3 Monthly Data:")
y3 = monthly_updated[monthly_updated['Year'] == 3]
print(f"Total New Customers: {y3['New_Paying_Users'].sum():.2f}")
print(f"Total Marketing Spend: {y3['Marketing_Spend'].sum():.2f}")
print(f"Calculated avg CAC: {y3['Marketing_Spend'].sum() / y3['New_Paying_Users'].sum():.2f}")
