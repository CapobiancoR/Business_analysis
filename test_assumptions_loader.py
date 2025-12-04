"""Test rapido per verificare assumptions caricate correttamente."""

from financial_model_app_v2 import load_from_excel_v7, parse_assumptions

state = load_from_excel_v7('ai_finance_dynamic_model_v7_channels.xlsx')
params = parse_assumptions(state['assumptions'])

print('=' * 80)
print('VERIFICA ASSUMPTIONS CARICATE')
print('=' * 80)

print(f'\nTotale assumptions: {len(state["assumptions"])}')

print('\n✓ Parametri chiave dei FIX 1-4:')
print(f'  Follower_Threshold_For_Click_Ads: {params.get("Follower_Threshold_For_Click_Ads", "NON TROVATO")}')
print(f'  FollowerAds_CTR_to_Site: {params.get("FollowerAds_CTR_to_Site", "NON TROVATO")}')
print(f'  Inf_Avg_Followers: {params.get("Inf_Avg_Followers", "NON TROVATO")}')
print(f'  Inf_Reach_Rate: {params.get("Inf_Reach_Rate", "NON TROVATO")}')
print(f'  Inf_Click_Rate: {params.get("Inf_Click_Rate", "NON TROVATO")}')

print('\n📋 Tutte le assumptions caricate:')
for idx, row in state['assumptions'].iterrows():
    print(f'  {idx+1:2d}. {row["Parameter"]:35s} = {row["Value"]:>10}  ({row["Category"]})')

print('\n' + '=' * 80)
if len(state['assumptions']) < 60:
    print('✅ OK: Numero corretto di assumptions (no righe Monthly Model)')
else:
    print('❌ ERRORE: Troppe assumptions, include righe Monthly Model')
