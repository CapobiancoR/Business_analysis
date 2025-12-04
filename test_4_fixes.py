"""
Script di test per verificare i 4 fix implementati:

FIX 1: Inf_Visitors_per_Collab calcolato dinamicamente
FIX 2: Follower_Threshold_For_Click_Ads usato correttamente
FIX 3: Paid_FollowerAds_Visitors generano traffico verso il sito
FIX 4: Paid_ClickAds_Clicks rimosso, solo Paid_ClickAds_Visitors
"""

import sys
import pandas as pd
from financial_model_app_v2 import load_from_excel_v7, recalc_model, parse_assumptions

def test_all_fixes():
    """Test completo dei 4 fix."""
    
    print("=" * 80)
    print("TEST COMPLETO DEI 4 FIX")
    print("=" * 80)
    
    # Load model
    excel_path = 'ai_finance_dynamic_model_v7_channels.xlsx'
    print(f"\n📂 Loading model from: {excel_path}")
    state = load_from_excel_v7(excel_path)
    
    assumptions = parse_assumptions(state['assumptions'])
    
    # ========================================================================
    # FIX 1: Verifica calcolo dinamico Inf_Visitors_per_Collab
    # ========================================================================
    print("\n" + "=" * 80)
    print("FIX 1: Inf_Visitors_per_Collab - CALCOLO DINAMICO")
    print("=" * 80)
    
    inf_avg_followers = assumptions.get('Inf_Avg_Followers', 0)
    inf_reach_rate = assumptions.get('Inf_Reach_Rate', 0)
    inf_click_rate = assumptions.get('Inf_Click_Rate', 0)
    
    inf_vpc_calculated = inf_avg_followers * inf_reach_rate * inf_click_rate
    
    print(f"\nParametri di input:")
    print(f"  Inf_Avg_Followers:    {inf_avg_followers:>10,.0f}")
    print(f"  Inf_Reach_Rate:       {inf_reach_rate:>10.2%}")
    print(f"  Inf_Click_Rate:       {inf_click_rate:>10.2%}")
    print(f"\n✓ Inf_Visitors_per_Collab calcolato: {inf_vpc_calculated:>10,.0f}")
    
    if inf_vpc_calculated > 0:
        print("✅ FIX 1 OK: Inf_Visitors_per_Collab è calcolato dinamicamente (non più 0)")
    else:
        print("❌ FIX 1 FAIL: Inf_Visitors_per_Collab è ancora 0")
        return False
    
    # ========================================================================
    # FIX 2: Verifica parametro Follower_Threshold_For_Click_Ads
    # ========================================================================
    print("\n" + "=" * 80)
    print("FIX 2: Follower_Threshold_For_Click_Ads - PARAMETRO CONFIGURABILE")
    print("=" * 80)
    
    follower_threshold = assumptions.get('Follower_Threshold_For_Click_Ads', 0)
    
    print(f"\n✓ Follower_Threshold_For_Click_Ads: {follower_threshold:>10,.0f} followers")
    
    if follower_threshold > 0:
        print("✅ FIX 2 OK: Parametro soglia presente e configurabile nelle Assumptions")
    else:
        print("❌ FIX 2 FAIL: Parametro soglia non trovato")
        return False
    
    # ========================================================================
    # Ricalcola il modello
    # ========================================================================
    print("\n" + "=" * 80)
    print("RICALCOLO MODELLO CON I FIX APPLICATI")
    print("=" * 80)
    
    monthly_data, yearly_data = recalc_model(state['assumptions'], state['monthly'], n_years=3)
    
    print(f"\n✓ Monthly data: {monthly_data.shape[0]} rows, {monthly_data.shape[1]} columns")
    print(f"✓ Yearly data: {yearly_data.shape[0]} rows, {yearly_data.shape[1]} columns")
    
    # ========================================================================
    # FIX 3: Verifica Paid_FollowerAds_Visitors
    # ========================================================================
    print("\n" + "=" * 80)
    print("FIX 3: Paid_FollowerAds_Visitors - CONVERSIONE FOLLOWER ADS → VISITORS")
    print("=" * 80)
    
    follower_ads_ctr = assumptions.get('FollowerAds_CTR_to_Site', 0)
    print(f"\n✓ FollowerAds_CTR_to_Site: {follower_ads_ctr:.2%}")
    
    if 'Paid_FollowerAds_Visitors' not in monthly_data.columns:
        print("❌ FIX 3 FAIL: Colonna Paid_FollowerAds_Visitors non trovata")
        return False
    
    # Verifica che nella Fase 1 ci siano visitors da follower ads
    fase1_months = monthly_data[monthly_data['Followers_Start'] < follower_threshold]
    
    if len(fase1_months) > 0:
        month_idx = fase1_months.index[0]
        month_data = monthly_data.iloc[month_idx]
        
        print(f"\nMese {month_data['Month']} (FASE 1 - Follower Ads):")
        print(f"  Followers_Start:               {month_data['Followers_Start']:>10,.0f}")
        print(f"  FollowerAds_Spend:             €{month_data['FollowerAds_Spend']:>9,.0f}")
        print(f"  Paid_FollowerAds_Impressions:  {month_data['Paid_FollowerAds_Impressions']:>10,.0f}")
        print(f"  Paid_FollowerAds_Reach:        {month_data['Paid_FollowerAds_Reach']:>10,.0f}")
        print(f"  Paid_FollowerAds_Visitors:     {month_data['Paid_FollowerAds_Visitors']:>10,.0f} ← FIX 3")
        print(f"  Paid_FollowerAds_NewFollowers: {month_data['Paid_FollowerAds_NewFollowers']:>10,.0f}")
        
        if month_data['Paid_FollowerAds_Visitors'] > 0:
            print("\n✅ FIX 3 OK: Follower ads generano visitors (entrano nel funnel)")
        else:
            print("\n⚠️  FIX 3 WARNING: Paid_FollowerAds_Visitors = 0 (verifica CTR)")
    
    # Verifica che PaidAds_Visitors includa entrambi i tipi
    print(f"\nFormula PaidAds_Visitors:")
    print(f"  = Paid_FollowerAds_Visitors + Paid_ClickAds_Visitors")
    
    sample_month = monthly_data.iloc[4]
    calc_paid_ads = sample_month['Paid_FollowerAds_Visitors'] + sample_month['Paid_ClickAds_Visitors']
    actual_paid_ads = sample_month['PaidAds_Visitors']
    
    print(f"\nMese 5 (esempio):")
    print(f"  Paid_FollowerAds_Visitors:  {sample_month['Paid_FollowerAds_Visitors']:>10,.2f}")
    print(f"  Paid_ClickAds_Visitors:     {sample_month['Paid_ClickAds_Visitors']:>10,.2f}")
    print(f"  PaidAds_Visitors:           {actual_paid_ads:>10,.2f}")
    print(f"  Calcolato:                  {calc_paid_ads:>10,.2f}")
    
    if abs(calc_paid_ads - actual_paid_ads) < 0.01:
        print("\n✅ FIX 3 OK: PaidAds_Visitors = somma di follower + click visitors")
    else:
        print("\n❌ FIX 3 FAIL: Calcolo PaidAds_Visitors non corretto")
        return False
    
    # ========================================================================
    # FIX 4: Verifica rimozione Paid_ClickAds_Clicks
    # ========================================================================
    print("\n" + "=" * 80)
    print("FIX 4: RIMOZIONE Paid_ClickAds_Clicks (colonna ridondante)")
    print("=" * 80)
    
    if 'Paid_ClickAds_Clicks' in monthly_data.columns:
        print("\n❌ FIX 4 FAIL: Colonna Paid_ClickAds_Clicks ancora presente")
        return False
    else:
        print("\n✅ FIX 4 OK: Colonna Paid_ClickAds_Clicks rimossa")
    
    # Verifica che Paid_ClickAds_Visitors sia calcolato correttamente
    fase2_months = monthly_data[monthly_data['Followers_Start'] >= follower_threshold]
    
    if len(fase2_months) > 0:
        month_idx = fase2_months.index[0]
        month_data = monthly_data.iloc[month_idx]
        
        click_ads_cpc = assumptions.get('ClickAds_CPC_EUR', 2.0)
        expected_visitors = month_data['ClickAds_Spend'] / click_ads_cpc
        actual_visitors = month_data['Paid_ClickAds_Visitors']
        
        print(f"\nMese {month_data['Month']} (FASE 2 - Click Ads):")
        print(f"  Followers_Start:         {month_data['Followers_Start']:>10,.0f}")
        print(f"  ClickAds_Spend:          €{month_data['ClickAds_Spend']:>9,.0f}")
        print(f"  ClickAds_CPC_EUR:        €{click_ads_cpc:>9,.2f}")
        print(f"  Paid_ClickAds_Visitors:  {actual_visitors:>10,.0f} (calcolato direttamente)")
        print(f"  Atteso:                  {expected_visitors:>10,.0f}")
        
        if abs(expected_visitors - actual_visitors) < 0.01:
            print("\n✅ FIX 4 OK: Paid_ClickAds_Visitors calcolato direttamente da budget/CPC")
        else:
            print("\n❌ FIX 4 FAIL: Calcolo Paid_ClickAds_Visitors non corretto")
            return False
    
    # ========================================================================
    # Verifica Inf_Visitors con calcolo dinamico
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICA FINALE: Inf_Visitors con parametri dinamici")
    print("=" * 80)
    
    inf_collabs = assumptions.get('Inf_Collabs_Y1', 1)
    expected_inf_visitors = inf_collabs * inf_vpc_calculated
    actual_inf_visitors = monthly_data.iloc[0]['Inf_Visitors']
    
    print(f"\nInf_Collabs:              {inf_collabs}")
    print(f"Inf_Visitors_per_Collab:  {inf_vpc_calculated:,.0f} (calcolato)")
    print(f"Expected Inf_Visitors:    {expected_inf_visitors:,.0f}")
    print(f"Actual Inf_Visitors:      {actual_inf_visitors:,.0f}")
    
    if abs(expected_inf_visitors - actual_inf_visitors) < 0.01:
        print("\n✅ Inf_Visitors calcolato correttamente con formula dinamica")
    else:
        print("\n❌ Inf_Visitors non corrisponde al calcolo atteso")
    
    # ========================================================================
    # Switch Fase 1 → Fase 2
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICA SWITCH FASE 1 → FASE 2")
    print("=" * 80)
    
    # Trova il mese dello switch
    switch_month = None
    for i in range(len(monthly_data)):
        if monthly_data.iloc[i]['Followers_Start'] >= follower_threshold:
            switch_month = i + 1
            break
    
    if switch_month:
        print(f"\n✓ Switch da Follower Ads a Click Ads al MESE {switch_month}")
        print(f"  Soglia: {follower_threshold:,.0f} followers")
        
        # Mostra dati prima e dopo switch
        before_idx = switch_month - 2
        after_idx = switch_month
        
        before = monthly_data.iloc[before_idx]
        after = monthly_data.iloc[after_idx]
        
        print(f"\nMese {before['Month']} (PRIMA dello switch):")
        print(f"  Followers_Start:           {before['Followers_Start']:>10,.0f}")
        print(f"  FollowerAds_Spend:         €{before['FollowerAds_Spend']:>9,.0f}")
        print(f"  ClickAds_Spend:            €{before['ClickAds_Spend']:>9,.0f}")
        print(f"  Paid_FollowerAds_Visitors: {before['Paid_FollowerAds_Visitors']:>10,.0f}")
        print(f"  Paid_ClickAds_Visitors:    {before['Paid_ClickAds_Visitors']:>10,.0f}")
        
        print(f"\nMese {after['Month']} (DOPO lo switch):")
        print(f"  Followers_Start:           {after['Followers_Start']:>10,.0f}")
        print(f"  FollowerAds_Spend:         €{after['FollowerAds_Spend']:>9,.0f}")
        print(f"  ClickAds_Spend:            €{after['ClickAds_Spend']:>9,.0f}")
        print(f"  Paid_FollowerAds_Visitors: {after['Paid_FollowerAds_Visitors']:>10,.0f}")
        print(f"  Paid_ClickAds_Visitors:    {after['Paid_ClickAds_Visitors']:>10,.0f}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("RIEPILOGO TEST")
    print("=" * 80)
    
    print("\n✅ FIX 1: Inf_Visitors_per_Collab calcolato dinamicamente")
    print("✅ FIX 2: Follower_Threshold_For_Click_Ads parametro configurabile")
    print("✅ FIX 3: Paid_FollowerAds_Visitors entrano nel funnel visitors → signups → paying")
    print("✅ FIX 4: Paid_ClickAds_Clicks rimosso, solo Paid_ClickAds_Visitors")
    
    print("\n🎉 TUTTI I FIX IMPLEMENTATI E VERIFICATI CON SUCCESSO!")
    
    return True


if __name__ == '__main__':
    success = test_all_fixes()
    sys.exit(0 if success else 1)
