from financial_model_app import *

assumptions_df, monthly_df, yearly_df = load_from_excel('ai_finance_dynamic_model_v6_social_views.xlsx')
params = parse_assumptions(assumptions_df)

print("CAC Values:")
print(f"CAC_Y1: {params.get('CAC_Y1', 'MISSING')}")
print(f"CAC_Y2: {params.get('CAC_Y2', 'MISSING')}")
print(f"CAC_Y3: {params.get('CAC_Y3', 'MISSING')}")

print("\nChannel shares Y3:")
print(f"Org_Share_Y3: {params.get('Org_Share_Y3', 'MISSING')}")
print(f"Inf_Share_Y3: {params.get('Inf_Share_Y3', 'MISSING')}")
print(f"Ref_Share_Y3: {params.get('Ref_Share_Y3', 'MISSING')}")
print(f"Other_Share_Y3: {params.get('Other_Share_Y3', 'MISSING')}")

print("\nChannel CACs:")
print(f"CAC_Org: {params.get('CAC_Org', 'MISSING')}")
print(f"CAC_Inf: {params.get('CAC_Inf', 'MISSING')}")
print(f"CAC_Ref: {params.get('CAC_Ref', 'MISSING')}")
print(f"CAC_Other: {params.get('CAC_Other', 'MISSING')}")
