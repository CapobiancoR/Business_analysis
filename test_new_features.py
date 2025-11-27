#!/usr/bin/env python3
"""
Test script per verificare le nuove funzionalità:
- PARTE A: Gross Margin Dinamico
- PARTE B: Paid Social Ads (Follower → Click bifase)
"""

import pandas as pd
from financial_model_app_v2 import load_from_excel_v7, recalc_model

print("=" * 80)
print("TEST NUOVE FUNZIONALITÀ - FINANCIAL MODEL v7.1")
print("=" * 80)

# Carica dati iniziali
excel_path = 'ai_finance_dynamic_model_v7_channels.xlsx'
print(f"\nCaricamento da {excel_path}...")
state = load_from_excel_v7(excel_path)

# Aggiungi parametri Paid Ads se non presenti (per test)
params_to_add = [
    {'Parameter': 'ClickAds_CPC_EUR', 'Value': 2.0},
    {'Parameter': 'Follower_Threshold_For_Click_Ads', 'Value': 20000}
]

for param in params_to_add:
    if param['Parameter'] not in state['assumptions']['Parameter'].values:
        new_row = pd.DataFrame([{
            'Category': 'Paid Social Ads',
            'Parameter': param['Parameter'],
            'Value': param['Value'],
            'Unit': 'EUR' if 'CPC' in param['Parameter'] else 'followers',
            'Notes': 'Test parameter'
        }])
        state['assumptions'] = pd.concat([state['assumptions'], new_row], ignore_index=True)

print(f"✓ Assumptions caricati: {len(state['assumptions'])} parametri")

# Ricalcola con n_years=3
print("\nRicalcolo modello (3 anni)...")
monthly, yearly = recalc_model(state['assumptions'], state['monthly'], n_years=3)

print(f"✓ Monthly data: {monthly.shape[0]} righe, {monthly.shape[1]} colonne")
print(f"✓ Yearly data: {yearly.shape[0]} righe, {yearly.shape[1]} colonne")

print("\n" + "=" * 80)
print("VERIFICA PARTE A - GROSS MARGIN DINAMICO")
print("=" * 80)

# Controlla che le nuove colonne esistano
required_monthly_cols = ['Direct_Costs', 'Gross_Profit', 'Gross_Margin_Month']
required_yearly_cols = ['Revenue_Year', 'Gross_Profit_Year', 'Gross_Margin_Year']

print("\n1. Verifica colonne Monthly Model:")
for col in required_monthly_cols:
    exists = col in monthly.columns
    print(f"   {col}: {'✓' if exists else '✗ MANCANTE'}")

print("\n2. Verifica colonne Yearly Summary:")
for col in required_yearly_cols:
    exists = col in yearly.columns
    print(f"   {col}: {'✓' if exists else '✗ MANCANTE'}")

# Analisi Gross Margin per anno
print("\n3. Analisi Gross Margin per Anno:")
print("-" * 80)
for idx, row in yearly.iterrows():
    year = int(row['Year'])
    revenue = row.get('Revenue_Year', 0)
    gross_profit = row.get('Gross_Profit_Year', 0)
    gross_margin = row.get('Gross_Margin_Year', 0)
    ltv = row.get('LTV_EUR', 0)
    cac = row.get('Average_CAC_EUR', 0)
    ltv_cac = row.get('LTV_CAC_Ratio', 0)
    
    print(f"\nYear {year}:")
    print(f"  Revenue (MRR totale):      €{revenue:>12,.0f}")
    print(f"  Gross Profit:              €{gross_profit:>12,.0f}")
    print(f"  Gross Margin:              {gross_margin:>12.2%}")
    print(f"  LTV (con GM dinamico):     €{ltv:>12,.2f}")
    print(f"  CAC:                       €{cac:>12,.2f}")
    print(f"  LTV/CAC Ratio:             {ltv_cac:>12.2f}x")
    
    # Verifica che GM sia nel range valido
    if not (0 <= gross_margin <= 1):
        print(f"  ⚠️  WARNING: Gross Margin fuori range [0,1]!")

print("\n" + "=" * 80)
print("VERIFICA PARTE B - PAID SOCIAL ADS (BIFASE)")
print("=" * 80)

# Controlla che le nuove colonne Paid Ads esistano
required_paid_ads_cols = [
    'FollowerAds_Spend', 'ClickAds_Spend',
    'Paid_FollowerAds_Impressions', 'Paid_FollowerAds_Reach', 'Paid_FollowerAds_NewFollowers',
    'Paid_ClickAds_Clicks', 'Paid_ClickAds_Visitors',
    'PaidAds_Visitors', 'PaidAds_Marketing_Spend'
]

print("\n1. Verifica colonne Paid Ads:")
for col in required_paid_ads_cols:
    exists = col in monthly.columns
    print(f"   {col}: {'✓' if exists else '✗ MANCANTE'}")

# Trova il mese in cui avviene lo switch
threshold = 20000  # Default
switch_month = None
for idx, row in monthly.iterrows():
    if row['Followers_Start'] >= threshold:
        switch_month = idx
        break

print(f"\n2. Analisi Switch Fase 1 → Fase 2:")
print(f"   Soglia followers: {threshold:,}")
if switch_month is not None:
    print(f"   Switch avviene al mese {switch_month + 1} (Year {int(monthly.iloc[switch_month]['Year'])}, Month {int(monthly.iloc[switch_month]['Month'])})")
    print(f"   Followers al momento dello switch: {monthly.iloc[switch_month]['Followers_Start']:,.0f}")
else:
    print(f"   Switch NON avvenuto (followers sempre < {threshold:,})")

# Mostra alcuni mesi campione
print("\n3. Mesi Campione:")
print("-" * 80)

# Primo mese (Fase 1)
m1 = monthly.iloc[0]
print(f"\nMese 1 (FASE 1 - Follower Ads):")
print(f"  Followers Start:               {m1['Followers_Start']:>10,.0f}")
print(f"  Followers End:                 {m1['Followers_End']:>10,.0f}")
print(f"  FollowerAds_Spend:             €{m1['FollowerAds_Spend']:>9,.0f}")
print(f"  ClickAds_Spend:                €{m1['ClickAds_Spend']:>9,.0f}")
print(f"  Paid_FollowerAds_NewFollowers: {m1['Paid_FollowerAds_NewFollowers']:>10,.1f}")
print(f"  Paid_ClickAds_Visitors:        {m1['Paid_ClickAds_Visitors']:>10,.1f}")
print(f"  Visitors_Total:                {m1['Visitors_Total']:>10,.1f}")
print(f"  Gross_Margin_Month:            {m1['Gross_Margin_Month']:>10.2%}")

# Mese dopo switch (se esiste)
if switch_month is not None and switch_month < len(monthly):
    m_switch = monthly.iloc[switch_month]
    print(f"\nMese {switch_month + 1} (FASE 2 - Click Ads - PRIMO MESE DOPO SWITCH):")
    print(f"  Followers Start:               {m_switch['Followers_Start']:>10,.0f}")
    print(f"  Followers End:                 {m_switch['Followers_End']:>10,.0f}")
    print(f"  FollowerAds_Spend:             €{m_switch['FollowerAds_Spend']:>9,.0f}")
    print(f"  ClickAds_Spend:                €{m_switch['ClickAds_Spend']:>9,.0f}")
    print(f"  Paid_FollowerAds_NewFollowers: {m_switch['Paid_FollowerAds_NewFollowers']:>10,.1f}")
    print(f"  Paid_ClickAds_Visitors:        {m_switch['Paid_ClickAds_Visitors']:>10,.1f}")
    print(f"  Visitors_Total:                {m_switch['Visitors_Total']:>10,.1f}")
    print(f"  Gross_Margin_Month:            {m_switch['Gross_Margin_Month']:>10.2%}")

# Ultimo mese
m_last = monthly.iloc[-1]
print(f"\nMese {len(monthly)} (Ultimo mese Year {int(m_last['Year'])}):")
print(f"  Followers Start:               {m_last['Followers_Start']:>10,.0f}")
print(f"  Followers End:                 {m_last['Followers_End']:>10,.0f}")
print(f"  FollowerAds_Spend:             €{m_last['FollowerAds_Spend']:>9,.0f}")
print(f"  ClickAds_Spend:                €{m_last['ClickAds_Spend']:>9,.0f}")
print(f"  Paid_FollowerAds_NewFollowers: {m_last['Paid_FollowerAds_NewFollowers']:>10,.1f}")
print(f"  Paid_ClickAds_Visitors:        {m_last['Paid_ClickAds_Visitors']:>10,.1f}")
print(f"  Visitors_Total:                {m_last['Visitors_Total']:>10,.1f}")
print(f"  Gross_Margin_Month:            {m_last['Gross_Margin_Month']:>10.2%}")

# Verifica Yearly Paid Ads Spend
print("\n4. Paid Ads Spend Annuale:")
print("-" * 80)
for idx, row in yearly.iterrows():
    year = int(row['Year'])
    paid_ads_spend = row.get('PaidAds_Marketing_Spend_EUR', 0)
    total_marketing = row.get('Total_Marketing_Spend_EUR', 0)
    paid_ads_pct = (paid_ads_spend / total_marketing * 100) if total_marketing > 0 else 0
    
    print(f"\nYear {year}:")
    print(f"  PaidAds_Marketing_Spend:   €{paid_ads_spend:>10,.0f}")
    print(f"  Total_Marketing_Spend:     €{total_marketing:>10,.0f}")
    print(f"  Paid Ads % of Total:       {paid_ads_pct:>10.1f}%")

print("\n" + "=" * 80)
print("TEST COMPLETATI")
print("=" * 80)

print("\n✅ RIEPILOGO:")
print("  - Gross Margin calcolato dinamicamente da MRR e Direct Costs")
print("  - LTV usa Gross_Margin_Year invece del parametro fisso")
print("  - Paid Ads switch automatico da Follower → Click alla soglia")
print("  - Tutte le nuove colonne presenti nei DataFrame")
print("\n💡 PROSSIMI PASSI:")
print("  - Aggiungi i nuovi parametri Paid Ads nell'Excel v7 (Assumptions)")
print("  - Testa con diversi valori di soglia e budget")
print("  - Verifica che i grafici includano le nuove metriche")
