"""
Test script per verificare il nuovo modello di crescita ad S con saturazione.

Verifica:
1. Crescita lenta nei primi mesi (adoption ramp)
2. Crescita accelerata nella fase centrale
3. Saturazione verso market_max_followers
4. Cap sui paying users
"""

from financial_model_app_v2 import load_from_excel_v7, recalc_model, parse_assumptions
import pandas as pd

def test_s_curve_growth():
    print("=" * 80)
    print("TEST MODELLO AD S CON SATURAZIONE")
    print("=" * 80)
    
    # Carica dati
    excel_path = r'c:\Users\simia\Desktop\Business_analysis\ai_finance_dynamic_model_v7_channels.xlsx'
    data = load_from_excel_v7(excel_path)
    
    # Scenario 1: Default (con parametri esistenti)
    print("\n--- SCENARIO 1: Default (se parametri TAM/SAM esistono) ---")
    assumptions_df = data['assumptions'].copy()
    params = parse_assumptions(assumptions_df)
    
    # Mostra parametri di mercato
    market_max_followers_local = params.get('Market_Max_Followers_Local', 'NOT SET')
    market_max_paying_local = params.get('Market_Max_PayingUsers_Local', 'NOT SET')
    follower_adoption_ramp = params.get('Follower_Adoption_Ramp_Months', 'NOT SET')
    
    print(f"\nParametri TAM/SAM/SOM:")
    print(f"  Market_Max_Followers_Local: {market_max_followers_local}")
    print(f"  Market_Max_PayingUsers_Local: {market_max_paying_local}")
    print(f"  Follower_Adoption_Ramp_Months: {follower_adoption_ramp}")
    
    # Ricalcola per 10 anni (120 mesi) per vedere meglio la curva S
    print("\nCalcolo modello per 10 anni (120 mesi)...")
    monthly_df, yearly_df = recalc_model(assumptions_df, data['monthly'], n_years=10)
    
    # Analisi crescita follower
    print("\n" + "=" * 80)
    print("ANALISI CRESCITA FOLLOWER (campionamento)")
    print("=" * 80)
    
    # Mesi chiave: 1, 3, 6, 12, 24, 36, 60, 120
    key_months = [0, 2, 5, 11, 23, 35, 59, 119]
    
    print(f"\n{'Mese':<6} {'Followers':>12} {'Delta_vs_Prev':>15} {'% vs Max':>10}")
    print("-" * 50)
    
    prev_followers = 0
    for idx in key_months:
        if idx >= len(monthly_df):
            break
        row = monthly_df.iloc[idx]
        month = int(row['Month']) + (int(row['Year']) - 1) * 12
        followers = row['Followers_End']
        delta = followers - prev_followers if prev_followers > 0 else followers
        
        # Calcola % rispetto al max (usa default se non settato)
        max_followers = market_max_followers_local if isinstance(market_max_followers_local, (int, float)) else 50000
        pct_of_max = (followers / max_followers * 100) if max_followers > 0 else 0
        
        print(f"{month:<6} {followers:>12,.0f} {delta:>15,.0f} {pct_of_max:>9.1f}%")
        prev_followers = followers
    
    # Verifica saturazione
    final_followers = monthly_df.iloc[-1]['Followers_End']
    max_followers = market_max_followers_local if isinstance(market_max_followers_local, (int, float)) else 50000
    
    print(f"\n{'=' * 50}")
    print(f"Followers finali (mese 120): {final_followers:,.0f}")
    print(f"Market Max Followers Local: {max_followers:,}")
    
    if final_followers <= max_followers:
        print("✅ OK: Followers NON superano il tetto di mercato")
    else:
        print(f"❌ ERROR: Followers superano il tetto di {final_followers - max_followers:,.0f}")
    
    # Analisi paying users
    print("\n" + "=" * 80)
    print("ANALISI PAYING USERS")
    print("=" * 80)
    
    final_paying = monthly_df.iloc[-1]['Paying_Users_End']
    max_paying = market_max_paying_local if isinstance(market_max_paying_local, (int, float)) else 2000
    
    print(f"\nPaying Users finali (mese 120): {final_paying:,.0f}")
    print(f"Market Max Paying Users Local: {max_paying:,}")
    
    if final_paying <= max_paying:
        print("✅ OK: Paying Users NON superano il tetto di mercato")
    else:
        print(f"❌ ERROR: Paying Users superano il tetto di {final_paying - max_paying:,.0f}")
    
    # Verifica crescita iniziale rallentata
    print("\n" + "=" * 80)
    print("VERIFICA RAMPA INIZIALE (primi 6 mesi)")
    print("=" * 80)
    
    print(f"\n{'Mese':<6} {'Followers_Start':>15} {'Followers_End':>15} {'Crescita_Mese':>15}")
    print("-" * 55)
    
    for idx in range(min(6, len(monthly_df))):
        row = monthly_df.iloc[idx]
        month = int(row['Month'])
        f_start = row['Followers_Start']
        f_end = row['Followers_End']
        growth = f_end - f_start
        
        print(f"{month:<6} {f_start:>15,.0f} {f_end:>15,.0f} {growth:>15,.0f}")
    
    print("\nNOTA: La crescita nei primi mesi dovrebbe essere RIDOTTA")
    print("      (adoption factor < 1 per i primi 24 mesi)")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Calcola tasso di crescita medio primi 6 mesi vs ultimi 6 mesi
    first_6_growth = monthly_df.iloc[5]['Followers_End'] - monthly_df.iloc[0]['Followers_Start']
    last_6_start_idx = max(0, len(monthly_df) - 6)
    last_6_growth = monthly_df.iloc[-1]['Followers_End'] - monthly_df.iloc[last_6_start_idx]['Followers_Start']
    
    print(f"\nCrescita totale primi 6 mesi: {first_6_growth:,.0f} followers")
    print(f"Crescita totale ultimi 6 mesi: {last_6_growth:,.0f} followers")
    
    if last_6_growth < first_6_growth:
        print("✅ OK: Crescita rallenta verso la fine (saturazione funziona)")
    else:
        print("⚠️  WARNING: Crescita non rallenta come atteso")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_s_curve_growth()
