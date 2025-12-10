#!/usr/bin/env python3
"""
AI Finance Platform - Interactive Financial Model Desktop App v2 (Updated for Excel v7)

COMPLETE INTERACTIVE DESKTOP APP with:
- Excel-like GUI (editable tables)
- Automatic recalculation engine
- Interactive charts with hover tooltips (mplcursors) and zoom/pan (NavigationToolbar)
- Social Ads channel with monthly budget and CPC
- JSON persistence (Excel used only first time)
- SUPPORTS EXCEL v7 FORMAT with flexible column structure

INSTALLATION:
    pip install pandas openpyxl matplotlib pyqt6 mplcursors

USAGE:
    python financial_model_app_v2.py
"""

import sys
import json
import os
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
import mplcursors

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTabWidget,
    QMessageBox, QFileDialog, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush


# =====================
# EXCEL v7 LOADER
# =====================

def load_from_excel_v7(excel_path: str) -> dict:
    """
    Load and parse Excel file v7 format.
    Returns dict with 'assumptions', 'monthly', 'yearly' DataFrames.
    
    v7 Structure:
    - Assumptions: rows 3-50 (0-indexed: 2-49), columns A-E (esteso per nuovi parametri)
      Format: Category | Parameter | Value | Unit | Notes
      
      NEW (v7.2): TAM/SAM/SOM Market Parameters
      -----------------------------------------
      - Market_Max_Followers_Local: tetto follower mercato nicchia (Zurigo/Svizzera) [default: 50,000]
      - Market_Max_Followers_Global: tetto follower mercato globale [default: 1,000,000]
      - Market_Max_PayingUsers_Local: tetto paying users nicchia [default: 2,000]
      - Market_Max_PayingUsers_Global: tetto paying users globale [default: 25,000]
      - Follower_Adoption_Ramp_Months: mesi per raggiungere crescita max [default: 24]
      
    - Monthly: row 55=header (0-indexed: 54), rows 56-91=data (0-indexed: 55-90)
    - Yearly: row 94=header (0-indexed: 93), rows 95-97=data (0-indexed: 94-96)
    """
    print(f"Loading Excel v7 file: {excel_path}")
    
    # Read the Model sheet
    df = pd.read_excel(excel_path, sheet_name='Model', header=None)
    
    # ===== PARSE ASSUMPTIONS =====
    # Row 3 is header (0-indexed: 2), skip it
    # Rows 4-50 (0-indexed: 3-49), Columns A-E (0-4) - esteso per nuovi parametri FIX 1-4
    assumptions_data = []
    for i in range(3, 100):  # Leggi fino a riga 100, ma fermati quando trova sezione vuota
        if i >= len(df):
            break
        row = df.iloc[i, 0:5].values  # columns A-E
        
        category = row[0] if pd.notna(row[0]) else ''
        parameter = row[1] if pd.notna(row[1]) else ''
        value = row[2] if pd.notna(row[2]) else 0
        unit = row[3] if pd.notna(row[3]) else ''
        notes = row[4] if pd.notna(row[4]) else ''
        
        # STOP CONDITIONS: fermati quando raggiungi sezione vuota o Monthly Model
        # 1. Se parameter E category sono vuoti → fine assumptions
        # 2. Se parameter contiene numeri tipo "1.00", "2.00" → è Monthly Model
        if not parameter or str(parameter).strip() == '':
            # Riga vuota, fine assumptions
            break
        
        # Skip header row
        if str(parameter).lower() == 'parameter':
            continue
            
        # Se value è stringa tipo "Year" o "Month" → è header Monthly Model
        if isinstance(parameter, str) and parameter.lower() in ['year', 'month']:
            break
        
        # FILTRO PARAMETRI DEPRECATI: GrossMargin e Inf_Visitors_per_Collab
        # Questi sono ora CALCOLATI DINAMICAMENTE, non parametri di input
        if parameter in ['GrossMargin', 'Inf_Visitors_per_Collab']:
            print(f"  [WARNING] Skipping deprecated parameter '{parameter}' (now calculated dynamically)")
            continue
        
        # Aggiungi solo se è un parametro valido
        assumptions_data.append({
            'Category': category,
            'Parameter': parameter,
            'Value': value,  # Single value for all years
            'Unit': unit,
            'Notes': notes
        })
    
    assumptions_df = pd.DataFrame(assumptions_data)
    
    # ===== PARSE MONTHLY MODEL =====
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
    
    print(f"Loaded {len(assumptions_df)} assumptions, {len(monthly_df)} monthly rows, {len(yearly_df)} yearly rows")
    
    return {
        'assumptions': assumptions_df,
        'monthly': monthly_df,
        'yearly': yearly_df
    }


def save_to_json(filepath: str, assumptions_df: pd.DataFrame, 
                 monthly_df: pd.DataFrame, yearly_df: pd.DataFrame):
    """Save all DataFrames to JSON file."""
    data = {
        'assumptions': {
            'columns': assumptions_df.columns.tolist(),
            'data': assumptions_df.values.tolist()
        },
        'monthly': {
            'columns': monthly_df.columns.tolist(),
            'data': monthly_df.values.tolist()
        },
        'yearly': {
            'columns': yearly_df.columns.tolist(),
            'data': yearly_df.values.tolist()
        }
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Saved to {filepath}")


def load_from_json(filepath: str) -> dict:
    """Load DataFrames from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assumptions_df = pd.DataFrame(data['assumptions']['data'], 
                                   columns=data['assumptions']['columns'])
    monthly_df = pd.DataFrame(data['monthly']['data'], 
                              columns=data['monthly']['columns'])
    yearly_df = pd.DataFrame(data['yearly']['data'], 
                             columns=data['yearly']['columns'])
    
    print(f"✓ Loaded from {filepath}")
    
    return {
        'assumptions': assumptions_df,
        'monthly': monthly_df,
        'yearly': yearly_df
    }


def parse_assumptions(df: pd.DataFrame) -> dict:
    """Parse assumptions DataFrame into a parameter dictionary."""
    params = {}
    for _, row in df.iterrows():
        param_name = row['Parameter']
        if pd.notna(param_name) and param_name != '':
            # Store single value (same for all years)
            value = row['Value'] if pd.notna(row['Value']) else 0
            params[param_name] = value
    return params


def recalc_model(assumptions_df: pd.DataFrame, 
                 monthly_df: pd.DataFrame,
                 n_years: int = 3) -> tuple:
    """
    Recalculate the financial model for Excel v7 format with dynamic duration.
    
    V7 has channel-specific breakdowns with social follower growth mechanics.
    This function recalculates key metrics while preserving the v7 structure.
    
    NEW FEATURES (v7.1):
    --------------------
    
    A) GROSS MARGIN DINAMICO:
       - Direct_Costs = DataSub_Cost + XAPI_Cost (costi variabili SaaS)
       - Gross_Profit = MRR - Direct_Costs
       - Gross_Margin_Month = Gross_Profit / MRR (gestisce MRR=0)
       - Yearly: Gross_Margin_Year = SUM(Gross_Profit) / SUM(MRR)
       - LTV usa Gross_Margin_Year invece del parametro fisso GrossMargin
    
    B) PAID SOCIAL ADS - LOGICA BIFASE:
       - FASE 1 (Followers < Soglia):
         * Budget → Follower Ads (CPM-based)
         * Genera: Impressions → Reach → NewFollowers
         * Aumenta Followers_End
    
    NEW FEATURES (v7.2): CRESCITA AD S CON SATURAZIONE
    ---------------------------------------------------
    
    C) MODELLO LOGISTICO PER FOLLOWER (no più crescita esponenziale infinita):
       - Parametri TAM/SAM/SOM: tetti di mercato per followers e paying users
       - Beachhead iniziale: Zurigo/Svizzera (max 50k followers, 2k paying users)
       - Crescita ad S: lenta all'inizio (brand nuovo), rapida al centro, plateau al tetto
       - Formula: Organic_NewFollowers = Followers × r_effective × (1 - Followers/Market_Max)
       - Adoption Ramp: primi 24 mesi con crescita ridotta (r_effective < r_base)
       - Cap sui paying users: non superano mai Market_Max_PayingUsers_Local
    
    NEW FEATURES (v7.3): NUOVA LOGICA REFERRAL
    ------------------------------------------
    
    D) REFERRAL CON SATURAZIONE E PROBABILITÀ ONE-TIME:
       - PRIMA: Referral_New_Payers = Paying_Users_Start × referral_rate
         → Problema: ricalcolava la probabilità ogni mese sugli stessi utenti
       
       - ADESSO: Referral_New_Payers = Signups × referral_rate × referral_capacity
         → Ogni NUOVO registrato ha 2% probabilità di invitare 1 amico (una volta sola)
         → La saturazione di mercato frena i referral quando ci si avvicina al tetto
       
       - Parametri:
         * Referral_Monthly_Rate (default 0.02): probabilità lifetime che un nuovo
           utente registrato inviti un amico (applicata alla coorte del mese)
         * referral_capacity = max(0, 1 - Paying_Users_Start / Market_Max_PayingUsers)
           Frena i referral quando il mercato è quasi pieno
    
    NEW FEATURES (v7.4): CONVERSIONE DA FREE ESISTENTI A PAID
    ---------------------------------------------------------
    
    E) SECONDA FONTE DI CONVERSIONE FREE → PAID:
       - PRIMA: Solo i nuovi signup del mese potevano convertire a paid
       
       - ADESSO: Anche gli utenti free GIÀ ESISTENTI convertono ogni mese
         → Una percentuale degli utenti free "attivi" diventa pagante
         → Riflette la dinamica reale SaaS dove utenti upgrade dopo mesi di utilizzo
       
       - Nuovi parametri:
         * Existing_Free_to_Paid_Monthly_Conv_Rate (default 0.0075): 0.75% al mese
         * Free_Active_Share (default 0.5): 50% dei free users sono "attivi"
       
       - Formula:
         * Free_Active_Users = Free_Users_Start × Free_Active_Share
         * New_Payers_from_Existing_Free = Free_Active_Users × Conv_Rate
       
       - Nuove colonne output:
         * New_Payers_from_New_Signups: conversione immediata da nuovi signup
         * New_Payers_from_Existing_Free: conversione ritardata da free esistenti
         * New_Payers_from_Referral: nuovi paganti da referral
         * Free_Active_Users: utenti free attivi (50% default)
       
       - New_Paying_Users ora = somma delle 3 componenti sopra

       - FASE 2 (Followers >= Soglia):
         * Budget → Click Ads (CPC-based)
         * Genera: Clicks → Visitors
         * Aumenta Visitors_Total → entra nel funnel conversione
       
       - Parametri chiave:
         * PaidAds_Monthly_Budget: budget mensile paid ads (uguale per tutti gli anni)
         * PaidAds_Max_Total_Budget: budget complessivo massimo (0 = illimitato)
           Quando raggiunto, le campagne si fermano automaticamente
         * FollowerAds_CPM_EUR: costo per 1000 impressions
         * FollowerAds_Reach_to_Follower_Rate: % reach che diventa follower
         * ClickAds_CPC_EUR: costo per click
         * Follower_Threshold_For_Click_Ads: soglia di switch (default 20k)
    
    Args:
        assumptions_df: DataFrame with assumptions (single Value column)
        monthly_df: DataFrame with monthly data (will be regenerated for n_years*12 months)
        n_years: Number of years to simulate (default 3)
    
    Returns:
        (monthly_df_recalc, yearly_df_recalc)
    """
    # Parse assumptions
    params = parse_assumptions(assumptions_df)
    
    # Extract core parameters (single value for all years)
    arpu = params.get('ARPU', 20)
    # NOTA: GrossMargin NON è più un parametro di input - è calcolato dinamicamente
    #       Gross_Margin_Month = Gross_Profit / MRR (mensile)
    #       Gross_Margin_Year = SUM(Gross_Profit) / SUM(MRR) (annuale)
    conv_vs = params.get('ConvVS', 0.13)
    conv_sp = params.get('ConvSP', 0.035)
    
    churn_y1 = params.get('Churn_Rate', params.get('ChurnY1', 0.06))  # Unified churn rate
    churn_y2 = churn_y1  # Same for all years
    churn_y3 = churn_y1  # Same for all years
    
    # ===== MARKET CAP PARAMETERS (TAM/SAM/SOM) - v7.2 =====
    # Calibrati su beachhead iniziale: Zurigo/Svizzera (nicchia investitori + high earners)
    # - Local: mercato di nicchia iniziale (hub finanziario come Zurigo)
    # - Global: espansione internazionale (inglese, piattaforme globali)
    market_max_followers_local = params.get('Market_Max_Followers_Local', 50000)
    market_max_followers_global = params.get('Market_Max_Followers_Global', 1000000)
    market_max_paying_local = params.get('Market_Max_PayingUsers_Local', 2000)
    market_max_paying_global = params.get('Market_Max_PayingUsers_Global', 25000)
    
    # Per ora usiamo solo i tetti LOCAL (primi 3 anni = fase beachhead)
    # NOTA: la logica passa automaticamente a GLOBAL quando i follower saturano il mercato locale
    market_max_followers = market_max_followers_local
    market_max_paying = market_max_paying_local
    
    # Adoption ramp: mesi necessari per raggiungere il massimo potenziale di crescita
    # (rallenta la crescita iniziale perché brand è nuovo)
    follower_adoption_ramp = params.get('Follower_Adoption_Ramp_Months', 24)
    
    # Global adoption ramp: quando si passa al mercato globale, la crescita riparte lentamente
    global_adoption_ramp = params.get('Global_Adoption_Ramp_Months', 12)
    
    # Follower growth parameters
    followers_0 = params.get('Followers_0', 1000)
    follower_growth = params.get('Follower_Monthly_Growth', 0.08)  # r_base per crescita logistica
    posts_per_month = params.get('Posts_per_Month_Y1', 120)  # Same for all years
    reach_per_post = params.get('Reach_per_Post', 0.04)
    non_follower_multiplier = params.get('NonFollower_Reach_Multiplier', 0.5)
    frequency = params.get('Frequency_Impressions_per_User', 1.5)
    ctr = params.get('Organic_CTR_to_Site', 0.015)
    
    # Influencer parameters
    # NOTA: Inf_Visitors_per_Collab NON è più un parametro di input - è SEMPRE calcolato
    #       Formula: Inf_Visitors_per_Collab = Inf_Avg_Followers × Inf_Reach_Rate × Inf_Click_Rate
    #       Questo valore viene usato per calcolare Inf_Visitors = Inf_Collabs × inf_vpc
    inf_avg_followers = params.get('Inf_Avg_Followers', 50000)
    inf_reach_rate = params.get('Inf_Reach_Rate', 0.3)
    inf_click_rate = params.get('Inf_Click_Rate', 0.02)
    inf_vpc = inf_avg_followers * inf_reach_rate * inf_click_rate  # CALCOLATO DINAMICAMENTE
    inf_collabs = params.get('Inf_Collabs_Y1', 1)  # Same for all years
    inf_reward = params.get('Influencer_Reward_per_Sub', 10)
    
    # Referral parameters
    referral_rate = params.get('Referral_Monthly_Rate', 0.02)
    referral_reward = params.get('Referral_Reward_per_Sub', 10)
    
    # ===== FREE TO PAID CONVERSION PARAMETERS =====
    # Conversione da utenti free ESISTENTI a paganti (non solo nuovi signups)
    existing_free_to_paid_rate = params.get('Existing_Free_to_Paid_Monthly_Conv_Rate', 0.0075)  # 0.75% al mese
    free_active_share = params.get('Free_Active_Share', 0.5)  # 50% dei free users sono attivi
    
    # Other channel parameters
    org_cost_per_post = params.get('Org_Cost_per_Post', 1)
    other_budget = params.get('Other_Marketing_Budget', params.get('Other_Marketing_Budget_Y1', 200))  # Unified for all years
    
    # Cost parameters
    base_fixed_cost = params.get('BaseFixedCost', 1000)
    fixed_cost_annual_growth = params.get('FixedCost_Annual_Growth', 0.05)  # 5% crescita annua default
    datasub_fee = params.get('DataSub_Fee', 2000)
    datasub_threshold = params.get('DataSub_MRR_Threshold', 5000)
    xapi_fee = params.get('XAPI_Fee', 5000)
    xapi_threshold = params.get('XAPI_MRR_Threshold', 15000)
    
    # ===== PAID SOCIAL ADS PARAMETERS =====
    # Budget mensile unico per tutte le campagne paid ads (uguale per tutti gli anni)
    paid_ads_monthly_budget = params.get('PaidAds_Monthly_Budget', 500)
    # Budget massimo ANNUALE: se > 0, le campagne si fermano quando raggiunto nell'anno
    paid_ads_max_annual_budget = params.get('PaidAds_Max_Annual_Budget', 0)  # 0 = illimitato
    # Budget massimo TOTALE (lifetime): se > 0, le campagne si fermano quando raggiunto complessivamente
    paid_ads_max_total_budget = params.get('PaidAds_Max_Total_Budget', 0)  # 0 = illimitato
    
    # Follower Ads (Fase 1: ottimizzazione per impressions/followers)
    follower_ads_cpm = params.get('FollowerAds_CPM_EUR', 7)
    follower_ads_reach_to_follower = params.get('FollowerAds_Reach_to_Follower_Rate', 0.1)
    follower_ads_ctr_to_site = params.get('FollowerAds_CTR_to_Site', 0.01)  # CTR follower ads → site
    
    # Click Ads (Fase 2: ottimizzazione per link click dopo soglia followers)
    click_ads_cpc = params.get('ClickAds_CPC_EUR', 2.0)
    follower_threshold_for_clicks = params.get('Follower_Threshold_For_Click_Ads', 20000)
    
    # Generate monthly data for n_years * 12 months
    n_months = n_years * 12
    monthly_data = []
    
    # Track cumulative paid ads spend for budget cap
    cumulative_paid_ads_spend = 0.0
    
    # Track annual paid ads spend (resets each year)
    annual_paid_ads_spend = 0.0
    current_tracking_year = 1
    
    # Track when global market phase starts (month index when local market saturated)
    global_phase_start_month = None
    
    # Track cumulative marketing spend and new customers for CAC calculation
    cumulative_marketing_spend = 0.0
    cumulative_new_customers = 0
    
    # Calculate all months
    for i in range(n_months):
        year = (i // 12) + 1
        month = (i % 12) + 1
        
        # ===== FOLLOWER GROWTH MECHANICS (MODELLO AD S) =====
        if i == 0:
            followers_start = followers_0
        else:
            followers_start = monthly_data[i-1]['Followers_End']
        
        # Month index (1-based): 1, 2, 3, ..., n_months
        month_index = i + 1
        
        # ===== DETECT LOCAL → GLOBAL MARKET TRANSITION =====
        # Quando i follower raggiungono ~95% del mercato locale, passiamo al mercato globale
        local_saturation_ratio = followers_start / market_max_followers_local
        is_in_global_phase = local_saturation_ratio >= 0.95
        
        # Registra quando inizia la fase globale (una volta sola)
        if is_in_global_phase and global_phase_start_month is None:
            global_phase_start_month = month_index
        
        # ===== CALCOLA IL TETTO DI MERCATO CORRENTE PER GLI ADS =====
        # - LOCAL: usa market_max_followers_local
        # - GLOBAL: usa market_max_followers_global (espansione internazionale)
        if is_in_global_phase:
            ads_market_max = market_max_followers_global
            # Mesi trascorsi dall'inizio della fase globale
            months_in_global = month_index - global_phase_start_month + 1
            # Nuova rampa di adozione per il mercato globale
            ads_adoption_factor = min(months_in_global / global_adoption_ramp, 1.0)
            # Saturazione rispetto al mercato GLOBALE
            ads_saturation_factor = max(0.0, 1.0 - followers_start / ads_market_max)
        else:
            ads_market_max = market_max_followers_local
            # Adoption factor normale (rampa locale)
            ads_adoption_factor = min(month_index / follower_adoption_ramp, 1.0)
            # Saturazione rispetto al mercato LOCALE
            ads_saturation_factor = max(0.0, 1.0 - followers_start / ads_market_max)
        
        # ===== CRESCITA ORGANICA (sempre rispetto al tetto attuale) =====
        # NOTA: La crescita organica rallenta quando raggiungiamo il tetto locale,
        # ma nel mercato globale c'è ancora spazio per crescere
        if is_in_global_phase:
            # Nel mercato globale: crescita organica rispetto al tetto globale
            organic_saturation_factor = max(0.0, 1.0 - followers_start / market_max_followers_global)
            organic_adoption_factor = min(months_in_global / global_adoption_ramp, 1.0)
        else:
            # Nel mercato locale: crescita organica rispetto al tetto locale
            organic_saturation_factor = max(0.0, 1.0 - followers_start / market_max_followers_local)
            organic_adoption_factor = min(month_index / follower_adoption_ramp, 1.0)
        
        # TASSO DI CRESCITA EFFETTIVO (modulato dalla rampa di adozione)
        follower_growth_effective = follower_growth * organic_adoption_factor
        
        # Nuovi follower organici del mese (crescita logistica ad S)
        organic_follower_growth = followers_start * follower_growth_effective * organic_saturation_factor
        
        # ===== PAID SOCIAL ADS - BIFASE LOGIC CON BUDGET CAP =====
        # Determina se siamo in Fase 1 (Follower Ads) o Fase 2 (Click Ads)
        # SPECIALE: Se follower_threshold_for_clicks = -1, rimani SEMPRE in Fase 1 (solo Follower Ads)
        
        # Reset annual spend tracker at the start of each new year
        if year != current_tracking_year:
            annual_paid_ads_spend = 0.0
            current_tracking_year = year
        
        # Calcola quanto budget è ancora disponibile questo mese
        # Considera ENTRAMBI i limiti: annuale e totale (lifetime)
        budget_this_month = paid_ads_monthly_budget
        
        # Applica limite ANNUALE (se configurato)
        if paid_ads_max_annual_budget > 0:
            annual_remaining = paid_ads_max_annual_budget - annual_paid_ads_spend
            budget_this_month = min(budget_this_month, max(0, annual_remaining))
        
        # Applica limite TOTALE lifetime (se configurato)
        if paid_ads_max_total_budget > 0:
            total_remaining = paid_ads_max_total_budget - cumulative_paid_ads_spend
            budget_this_month = min(budget_this_month, max(0, total_remaining))
        
        # STOP ADS SE MERCATO (corrente) È SATURO
        # Se ads_saturation_factor < 5%, non ha senso spendere per acquisire follower
        ads_market_saturated = ads_saturation_factor < 0.05
        
        if ads_market_saturated:
            # MERCATO SATURO: ferma tutte le campagne paid ads
            follower_ads_spend = 0.0
            click_ads_spend = 0.0
            paid_follower_ads_impressions = 0.0
            paid_follower_ads_reach = 0.0
            paid_follower_ads_new_followers = 0.0
            paid_follower_ads_visitors = 0.0
            paid_click_ads_visitors = 0.0
        elif budget_this_month > 0 and (follower_threshold_for_clicks < 0 or followers_start < follower_threshold_for_clicks):
            # FASE 1: Budget per acquisire followers/impressions
            follower_ads_spend = budget_this_month
            click_ads_spend = 0.0
            
            # Calcola impressions generate dalle campagne follower
            paid_follower_ads_impressions = (follower_ads_spend / follower_ads_cpm) * 1000.0
            
            # Calcola reach unica (dividi per frequenza)
            paid_follower_ads_reach = paid_follower_ads_impressions / frequency
            
            # Nuovi followers acquisiti dalle campagne paid
            paid_follower_ads_new_followers = paid_follower_ads_reach * follower_ads_reach_to_follower
            
            # Anche le follower ads generano visitors (CTR verso sito)
            paid_follower_ads_visitors = paid_follower_ads_reach * follower_ads_ctr_to_site
            
            # Click ads = 0 in Fase 1
            paid_click_ads_visitors = 0.0
        elif budget_this_month > 0:
            # FASE 2: Budget per generare click/visitors
            follower_ads_spend = 0.0
            click_ads_spend = budget_this_month  # Stesso budget, diversa ottimizzazione
            
            # Follower ads = 0 in Fase 2
            paid_follower_ads_impressions = 0.0
            paid_follower_ads_reach = 0.0
            paid_follower_ads_new_followers = 0.0
            paid_follower_ads_visitors = 0.0
            
            # Calcola visitors direttamente
            paid_click_ads_visitors = click_ads_spend / click_ads_cpc  # 1 click ≈ 1 visitor
        else:
            # BUDGET ESAURITO: campagne ferme
            follower_ads_spend = 0.0
            click_ads_spend = 0.0
            paid_follower_ads_impressions = 0.0
            paid_follower_ads_reach = 0.0
            paid_follower_ads_new_followers = 0.0
            paid_follower_ads_visitors = 0.0
            paid_click_ads_visitors = 0.0
        
        # Aggiorna spesa cumulativa (totale e annuale)
        month_ads_spend = follower_ads_spend + click_ads_spend
        cumulative_paid_ads_spend += month_ads_spend
        annual_paid_ads_spend += month_ads_spend
        
        # Follower end = start + crescita organica (logistica) + paid followers
        followers_end = followers_start + organic_follower_growth + paid_follower_ads_new_followers
        
        # CAP: non superare mai il tetto di mercato corrente (LOCAL o GLOBAL)
        current_market_cap = market_max_followers_global if is_in_global_phase else market_max_followers_local
        followers_end = min(followers_end, current_market_cap)
        
        # Posts per month (same for all years now)
        posts = posts_per_month
        
        # Social impressions and views
        avg_followers = (followers_start + followers_end) / 2
        impr_followers = avg_followers * posts * reach_per_post * frequency
        impr_non_followers = impr_followers * non_follower_multiplier
        social_views = impr_followers + impr_non_followers
        new_unique = impr_non_followers / frequency
        
        # Organic visitors from social
        org_visitors = new_unique * ctr
        
        # Influencer visitors (same for all years now)
        inf_visitors = inf_collabs * inf_vpc
        
        # Other channel visitors (same for all years now)
        other_visitors = other_budget / 2.0
        
        # FIX 3: Paid ads visitors (da ENTRAMBE le fasi: follower + click ads)
        paid_ads_visitors = paid_follower_ads_visitors + paid_click_ads_visitors
        
        # Total visitors (now includes paid ads)
        visitors_total = org_visitors + inf_visitors + other_visitors + paid_ads_visitors
        
        # Signups by channel
        signups_total = visitors_total * conv_vs
        
        # Channel-specific signups (proportional to traffic)
        if visitors_total > 0:
            org_signups = signups_total * (org_visitors / visitors_total)
            inf_signups = signups_total * (inf_visitors / visitors_total)
            other_signups = signups_total * (other_visitors / visitors_total)
            paid_ads_signups = signups_total * (paid_ads_visitors / visitors_total)  # NEW: signup da paid ads
        else:
            org_signups = inf_signups = other_signups = paid_ads_signups = 0
        
        # ===== REFERRAL - NUOVA LOGICA (v7.3) =====
        # Regole:
        # 1. Ogni NUOVO utente registrato (Signups) ha probabilità referral_rate di invitare 1 amico
        #    → applicata UNA SOLA VOLTA per utente (alla coorte del mese di registrazione)
        # 2. La saturazione di mercato frena i referral quando ci si avvicina al tetto
        #
        # Formula: Referral_New_Payers = Signups × referral_rate × referral_capacity
        #
        # PRIMA (vecchia logica): Referral_New_Payers = Paying_Users_Start × referral_rate
        #   → Problema: ricalcolava la probabilità ogni mese sugli stessi utenti
        
        if i == 0:
            paying_start = 0
        else:
            paying_start = monthly_data[i-1]['Paying_Users_End']
        
        # Tetto paying users corrente (LOCAL o GLOBAL)
        current_paying_cap = market_max_paying_global if is_in_global_phase else market_max_paying_local
        
        # Fattore di saturazione: quando il mercato è quasi pieno, i referral si spengono
        # referral_capacity ∈ [0, 1]: 1 = mercato vuoto, 0 = mercato pieno
        referral_capacity = max(0.0, 1.0 - paying_start / current_paying_cap) if current_paying_cap > 0 else 0.0
        
        # Utenti "potenziali inviter": nuovi registrati del mese × probabilità di invitare
        # Nota: referral_rate è ora la probabilità lifetime che un nuovo utente inviti un amico
        potential_referral_inviters = signups_total * referral_rate
        
        # Nuovi paying da referral = potenziali inviter × capacità di mercato residua
        referral_new_payers = potential_referral_inviters * referral_capacity
        
        # Channel-specific new payers
        org_new_payers = org_signups * conv_sp
        inf_new_payers = inf_signups * conv_sp
        other_new_payers = other_signups * conv_sp
        paid_ads_new_payers = paid_ads_signups * conv_sp  # NEW: paying users da paid ads
        
        # Churn (cycle through Y1/Y2/Y3 rates)
        year_mod = ((year - 1) % 3) + 1  # Cycles 1,2,3,1,2,3...
        if year_mod == 1:
            churn_rate = churn_y1
        elif year_mod == 2:
            churn_rate = churn_y2
        else:
            churn_rate = churn_y3
        
        # User cohort dynamics - la parte di paying_end viene calcolata DOPO free users tracking
        churned = paying_start * churn_rate
        
        # ===== FREE USERS TRACKING =====
        # Free users = utenti registrati che non pagano (ancora)
        # Signups cumulativi - Paying users = Free users
        if i == 0:
            cumulative_signups = signups_total
            free_users_start = 0
        else:
            cumulative_signups = monthly_data[i-1]['Cumulative_Signups'] + signups_total
            free_users_start = monthly_data[i-1]['Free_Users_End']
        
        # ===== CONVERSIONE DA FREE ESISTENTI A PAID (v7.4) =====
        # Logica: ogni mese, una percentuale degli utenti free ATTIVI converte a paid
        # Questo è ADDIZIONALE rispetto alla conversione immediata dei nuovi signup
        #
        # 1. Free users attivi = Free_Users_Start × Free_Active_Share
        # 2. Nuovi paid da free esistenti = Free_Active × Existing_Free_to_Paid_Monthly_Conv_Rate
        #
        # Esempio: 1000 free users, 50% attivi = 500 attivi
        #          500 × 0.75% = 3.75 → ~4 nuovi paying al mese da free esistenti
        
        free_active_users = free_users_start * free_active_share
        new_payers_from_existing_free = max(0, round(free_active_users * existing_free_to_paid_rate))
        
        # ===== COMPONENTI NUOVI PAGANTI SEPARATI =====
        # 1. Nuovi paganti da NUOVI signup (conversione immediata)
        new_payers_from_new_signups = org_new_payers + inf_new_payers + other_new_payers + paid_ads_new_payers
        
        # 2. Nuovi paganti da FREE ESISTENTI (conversione ritardata)
        # Già calcolato sopra: new_payers_from_existing_free
        
        # 3. Nuovi paganti da REFERRAL (già calcolato)
        new_payers_from_referral = referral_new_payers
        
        # TOTALE nuovi paying users del mese
        new_paying_total = new_payers_from_new_signups + new_payers_from_existing_free + new_payers_from_referral
        
        # Free users end = free users start + nuovi signups che NON convertono - free esistenti che convertono
        # - nuovi free = signups - nuovi paying da signups (quelli che convertono subito)
        # - sottrarre anche i free esistenti che convertono questo mese
        new_free_users = signups_total - new_payers_from_new_signups
        free_users_end = max(0, free_users_start + new_free_users - new_payers_from_existing_free)
        
        # ===== PAYING USERS END (aggiornato con new_paying_total) =====
        # Ora include anche i paganti da free esistenti
        paying_end = max(0, paying_start - churned + new_paying_total)
        
        # CAP: non superare mai il tetto di mercato per paying users (LOCAL o GLOBAL)
        paying_end = min(paying_end, current_paying_cap)
        
        # Total users = paying + free
        total_users_end = paying_end + free_users_end
        
        # Revenue
        mrr = paying_end * arpu
        
        # ===== MARKETING SPEND BY CHANNEL =====
        org_marketing = posts * org_cost_per_post
        inf_marketing = inf_new_payers * inf_reward
        other_marketing = other_budget
        referral_marketing = referral_new_payers * referral_reward
        paid_ads_marketing = follower_ads_spend + click_ads_spend
        total_marketing = org_marketing + inf_marketing + other_marketing + referral_marketing + paid_ads_marketing
        
        # ===== COSTS =====
        datasub_cost = datasub_fee if mrr >= datasub_threshold else 0
        xapi_cost = xapi_fee if mrr >= xapi_threshold else 0
        
        # Fixed costs con crescita annuale
        # Anno 1: base_fixed_cost, Anno 2: base × (1+growth), Anno 3: base × (1+growth)^2, ...
        current_fixed_cost = base_fixed_cost * ((1 + fixed_cost_annual_growth) ** (year - 1))
        
        # ===== GROSS MARGIN DINAMICO (PARTE A) =====
        # Direct costs = costi variabili direttamente legati al servizio SaaS
        direct_costs = datasub_cost + xapi_cost
        
        # Gross profit = MRR - Direct Costs
        gross_profit = mrr - direct_costs
        
        # Gross margin mensile (gestisce divisione per zero)
        gross_margin_month = (gross_profit / mrr) if mrr > 0 else 0.0
        
        # Total costs (include marketing + direct costs + fixed costs)
        total_costs = total_marketing + direct_costs + current_fixed_cost
        
        # Cash flow
        net_cash_flow = mrr - total_costs
        if i == 0:
            cumulative_cash = net_cash_flow
        else:
            cumulative_cash = monthly_data[i-1]['Cumulative_Cash'] + net_cash_flow
        
        # ===== CAC e LTV MENSILE (per grafici) =====
        # Aggiorna cumulativi
        cumulative_marketing_spend += total_marketing
        cumulative_new_customers += new_paying_total
        
        # CAC cumulativo = totale speso / totale nuovi clienti
        cumulative_cac = cumulative_marketing_spend / cumulative_new_customers if cumulative_new_customers > 0 else 0
        
        # CAC mensile = spesa marketing del mese / nuovi clienti del mese
        monthly_cac = total_marketing / new_paying_total if new_paying_total > 0 else 0
        
        # LTV = ARPU × Gross Margin / Churn (con gross margin mensile)
        # Se churn è 0, assumiamo cliente infinito ma cappato
        monthly_ltv = (arpu * gross_margin_month / churn_rate) if churn_rate > 0 else (arpu * gross_margin_month * 120)  # Cap a 10 anni
        
        # LTV/CAC ratio
        ltv_cac_ratio = monthly_ltv / cumulative_cac if cumulative_cac > 0 else 0
        
        # Store month data (includes all new Paid Ads and Gross Margin columns)
        # Calcola la saturazione rispetto al mercato CORRENTE (local o global)
        current_market_max_for_display = market_max_followers_global if is_in_global_phase else market_max_followers_local
        current_saturation_pct = (followers_start / current_market_max_for_display) * 100
        
        monthly_data.append({
            'Year': year,
            'Month': month,
            'Followers_Start': followers_start,
            'Followers_End': followers_end,
            # === MARKET PHASE TRACKING (LOCAL → GLOBAL) ===
            'Market_Phase': 'Global' if is_in_global_phase else 'Local',
            'Market_Saturation_Pct': current_saturation_pct,  # % del mercato CORRENTE (local o global) raggiunto
            'Ads_Saturation_Factor': ads_saturation_factor,  # Fattore saturazione per gli ads
            # ===========================
            'Posts': posts,
            'Impr_Followers': impr_followers,
            'Impr_NonFollowers': impr_non_followers,
            'Social_Views': social_views,
            'NewUnique_NonFollowers': new_unique,
            'Org_Visitors': org_visitors,
            'Inf_Visitors': inf_visitors,
            'Other_Visitors': other_visitors,
            # === PAID ADS COLUMNS ===
            'FollowerAds_Spend': follower_ads_spend,
            'ClickAds_Spend': click_ads_spend,
            'Annual_PaidAds_Spend': annual_paid_ads_spend,  # Budget speso nell'anno corrente
            'Cumulative_PaidAds_Spend': cumulative_paid_ads_spend,  # Budget speso cumulativo (lifetime)
            'Paid_FollowerAds_Impressions': paid_follower_ads_impressions,
            'Paid_FollowerAds_Reach': paid_follower_ads_reach,
            'Paid_FollowerAds_NewFollowers': paid_follower_ads_new_followers,
            'Paid_FollowerAds_Visitors': paid_follower_ads_visitors,
            'Paid_ClickAds_Visitors': paid_click_ads_visitors,
            'PaidAds_Visitors': paid_ads_visitors,  # Somma di entrambi
            # ===========================
            'Visitors_Total': visitors_total,
            'Signups': signups_total,
            'Org_Signups': org_signups,
            'Inf_Signups': inf_signups,
            'Other_Signups': other_signups,
            'PaidAds_Signups': paid_ads_signups,  # NEW: signup da paid ads
            # === NEW PAYERS BREAKDOWN (v7.4) ===
            'New_Payers_from_New_Signups': new_payers_from_new_signups,  # Conversione immediata da nuovi signup
            'New_Payers_from_Existing_Free': new_payers_from_existing_free,  # Conversione ritardata da free esistenti
            'New_Payers_from_Referral': new_payers_from_referral,  # Da referral
            'Referral_New_Payers': referral_new_payers,  # Legacy column (same as New_Payers_from_Referral)
            # ===========================
            'Org_New_Payers': org_new_payers,
            'Inf_New_Payers': inf_new_payers,
            'Other_New_Payers': other_new_payers,
            'PaidAds_New_Payers': paid_ads_new_payers,  # NEW: paying users da paid ads
            'New_Paying_Users': new_paying_total,  # UPDATED: ora include anche free esistenti convertiti
            'Churn_Rate': churn_rate,
            'Paying_Users_Start': paying_start,
            'Churned_Users': churned,
            'Paying_Users_End': paying_end,
            # === FREE USERS COLUMNS (v7.4) ===
            'Cumulative_Signups': cumulative_signups,
            'Free_Users_Start': free_users_start,
            'Free_Active_Users': free_active_users,  # NEW: free users attivi (50% default)
            'Free_Users_End': free_users_end,
            'Total_Users_End': total_users_end,
            # ===========================
            'ARPU': arpu,
            'MRR': mrr,
            'Org_Marketing_Spend': org_marketing,
            'Inf_Marketing_Spend': inf_marketing,
            'Other_Marketing_Spend': other_marketing,
            'Referral_Marketing_Spend': referral_marketing,
            'PaidAds_Marketing_Spend': paid_ads_marketing,  # NEW
            'Total_Marketing_Spend': total_marketing,
            # === GROSS MARGIN COLUMNS (NEW) ===
            'Direct_Costs': direct_costs,
            'Gross_Profit': gross_profit,
            'Gross_Margin_Month': gross_margin_month,
            # ===========================
            'DataSub_Cost': datasub_cost,
            'XAPI_Cost': xapi_cost,
            'Base_Fixed_Cost': current_fixed_cost,  # Con crescita annuale applicata
            'Total_Costs': total_costs,
            'Net_Cash_Flow': net_cash_flow,
            'Cumulative_Cash': cumulative_cash,
            # === CAC e LTV MENSILE ===
            'Monthly_CAC': monthly_cac,
            'Cumulative_CAC': cumulative_cac,
            'Monthly_LTV': monthly_ltv,
            'LTV_CAC_Ratio': ltv_cac_ratio
        })
    
    monthly = pd.DataFrame(monthly_data)
    
    # Recalculate yearly summary for n_years
    yearly_data = []
    for year in range(1, n_years + 1):
        year_rows = monthly[monthly['Year'] == year]
        
        if len(year_rows) == 0:
            continue
        
        last_month = year_rows.iloc[-1]
        
        # Aggregate metrics
        end_paying = last_month['Paying_Users_End']
        end_mrr = last_month['MRR']
        arr = end_mrr * 12
        total_new = year_rows['New_Paying_Users'].sum()
        
        # Marketing spend by channel (include Paid Ads)
        total_org_spend = year_rows['Org_Marketing_Spend'].sum()
        total_inf_spend = year_rows['Inf_Marketing_Spend'].sum()
        total_other_spend = year_rows['Other_Marketing_Spend'].sum()
        total_referral_spend = year_rows['Referral_Marketing_Spend'].sum()
        total_paid_ads_spend = year_rows['PaidAds_Marketing_Spend'].sum()  # NEW
        total_marketing = total_org_spend + total_inf_spend + total_other_spend + total_referral_spend + total_paid_ads_spend
        
        avg_cac = total_marketing / total_new if total_new > 0 else 0
        
        # ===== GROSS MARGIN DINAMICO ANNUALE (PARTE A) =====
        # Revenue annuale = somma MRR dei 12 mesi
        revenue_year = year_rows['MRR'].sum()
        
        # Gross profit annuale = somma gross profit dei 12 mesi
        gross_profit_year = year_rows['Gross_Profit'].sum()
        
        # Gross margin annuale (gestisce divisione per zero)
        gross_margin_year = (gross_profit_year / revenue_year) if revenue_year > 0 else 0.0
        
        # Get year-specific churn (cycle through Y1/Y2/Y3)
        year_mod = ((year - 1) % 3) + 1
        if year_mod == 1:
            churn = churn_y1
        elif year_mod == 2:
            churn = churn_y2
        else:
            churn = churn_y3
        
        # ===== LTV CON GROSS MARGIN DINAMICO (PARTE A) =====
        # Usa il Gross Margin calcolato dai risultati effettivi, non dalle Assumptions
        ltv = (arpu * gross_margin_year / churn) if churn > 0 else 0
        ltv_cac = ltv / avg_cac if avg_cac > 0 else 0
        
        cumulative_cash_eoy = last_month['Cumulative_Cash']
        
        # Channel metrics
        total_org_visitors = year_rows['Org_Visitors'].sum()
        total_inf_visitors = year_rows['Inf_Visitors'].sum()
        total_other_visitors = year_rows['Other_Visitors'].sum()
        total_visitors = year_rows['Visitors_Total'].sum()
        
        total_social_views = year_rows['Social_Views'].sum()
        end_followers = last_month['Followers_End']
        
        yearly_data.append({
            'Year': year,
            'End_Paying_Users': end_paying,
            'End_MRR_EUR': end_mrr,
            'ARR_EUR': arr,
            'Total_New_Customers': total_new,
            # === NEW PAYERS BREAKDOWN (v7.4) ===
            'New_Payers_from_New_Signups': year_rows['New_Payers_from_New_Signups'].sum(),
            'New_Payers_from_Existing_Free': year_rows['New_Payers_from_Existing_Free'].sum(),
            'New_Payers_from_Referral': year_rows['New_Payers_from_Referral'].sum(),
            # ===========================
            'Org_New_Payers': year_rows['Org_New_Payers'].sum(),
            'Inf_New_Payers': year_rows['Inf_New_Payers'].sum(),
            'Other_New_Payers': year_rows['Other_New_Payers'].sum(),
            'PaidAds_New_Payers': year_rows['PaidAds_New_Payers'].sum(),  # NEW: paying users da paid ads
            'Referral_New_Payers': year_rows['Referral_New_Payers'].sum(),
            'Org_Marketing_Spend_EUR': total_org_spend,
            'Inf_Marketing_Spend_EUR': total_inf_spend,
            'Other_Marketing_Spend_EUR': total_other_spend,
            'Referral_Marketing_Spend_EUR': total_referral_spend,
            'PaidAds_Marketing_Spend_EUR': total_paid_ads_spend,  # NEW
            'Total_Marketing_Spend_EUR': total_marketing,
            'Average_CAC_EUR': avg_cac,
            'Assumed_Monthly_Churn': churn,
            # === GROSS MARGIN DINAMICO (NEW) ===
            'Revenue_Year': revenue_year,
            'Gross_Profit_Year': gross_profit_year,
            'Gross_Margin_Year': gross_margin_year,
            # ===========================
            'LTV_EUR': ltv,
            'LTV_CAC_Ratio': ltv_cac,
            'Cumulative_Cash_EndOfYear': cumulative_cash_eoy,
            'Total_Org_Visitors': total_org_visitors,
            'Total_Inf_Visitors': total_inf_visitors,
            'Total_Other_Visitors': total_other_visitors,
            'Total_Visitors': total_visitors,
            'Share_Org_Visitors': total_org_visitors / total_visitors if total_visitors > 0 else 0,
            'Share_Inf_Visitors': total_inf_visitors / total_visitors if total_visitors > 0 else 0,
            'Share_Other_Visitors': total_other_visitors / total_visitors if total_visitors > 0 else 0,
            'Total_Social_Views': total_social_views,
            'End_Followers': end_followers
        })
    
    yearly = pd.DataFrame(yearly_data)
    
    return monthly, yearly


# =====================
# GUI WIDGETS
# =====================

class DataTableWidget(QWidget):
    """Custom widget for displaying and editing a DataFrame as a table."""
    
    def __init__(self, df: pd.DataFrame, title: str, editable_columns: list = None, format_as_integer: bool = False, show_formulas: bool = False):
        super().__init__()
        self.df = df.copy()
        self.editable_columns = editable_columns  # List of column names that are editable
        self.format_as_integer = format_as_integer  # Format numbers as integers
        self.show_formulas = show_formulas  # Whether to show formulas on cell click
        
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel(f"<b style='color: black;'>{title}</b>")
        self.title_label.setStyleSheet("font-size: 11pt; padding: 5px;")
        layout.addWidget(self.title_label)
        
        # Formula display label (shown when cell is clicked)
        if self.show_formulas:
            self.formula_label = QLabel("")
            self.formula_label.setStyleSheet("""
                QLabel {
                    background-color: #fffacd;
                    border: 1px solid #d0d0d0;
                    padding: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 9pt;
                    color: black;
                }
            """)
            self.formula_label.setWordWrap(True)
            self.formula_label.setMinimumHeight(50)
            layout.addWidget(self.formula_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        
        # Selezione intera riga quando clicchi su una cella
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Populate table
        self.update_from_dataframe(df, format_as_integer=self.format_as_integer)
        
        # Style - Excel-like (white background, black text)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #d0d0d0;
                font-size: 9pt;
            }
            QTableWidget::item {
                background-color: white;
                color: black;
                padding: 2px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                font-weight: bold;
                border: 1px solid #d0d0d0;
                padding: 3px;
                font-size: 9pt;
            }
        """)
        self.table.setAlternatingRowColors(False)  # Disable to have pure white
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)
        self.table.horizontalHeader().setFont(header_font)
        
        # Set default row height to be more compact
        self.table.verticalHeader().setDefaultSectionSize(22)
        
        # Connect cell click signal to show formula
        if self.show_formulas:
            self.table.cellClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def on_cell_clicked(self, row: int, col: int):
        """Handle cell click to show formula."""
        if not self.show_formulas:
            return
        
        col_name = self.df.columns[col]
        year = int(self.df.iloc[row, self.df.columns.get_loc('Year')]) if 'Year' in self.df.columns else None
        month = int(self.df.iloc[row, self.df.columns.get_loc('Month')]) if 'Month' in self.df.columns else None
        
        formula = self.get_formula(col_name, year, month, row)
        
        if formula:
            cell_ref = f"Row {row+1}, Column '{col_name}'"
            if year and month:
                cell_ref = f"Year {year}, Month {month} - '{col_name}'"
            elif year:
                cell_ref = f"Year {year} - '{col_name}'"
            
            self.formula_label.setText(f"<b>{cell_ref}</b><br><br>{formula}")
        else:
            self.formula_label.setText(f"<b>{col_name}</b><br><br><i>Editable input field (no formula)</i>")
    
    def get_formula(self, col_name: str, year: int, month: int, row: int) -> str:
        """Get the formula for a specific column."""
        # Monthly Model Formulas
        monthly_formulas = {
            'Followers_Start': 'Previous month Followers_End (or Followers_0 for first month)',
            'Followers_End': 'Followers_Start + Organic_Growth + Paid_FollowerAds_NewFollowers (capped at Market_Max)',
            'Market_Phase': 'Local se Followers < 95% Market_Max_Local, altrimenti Global',
            'Market_Saturation_Pct': '(Followers_Start / Current_Market_Max) × 100 - usa Market_Max_Local in fase Local, Market_Max_Global in fase Global',
            'Ads_Saturation_Factor': '1 - (Followers / Current_Market_Max) - usato per decidere se gli ads sono ancora efficaci',
            'Posts': 'Posts_per_Month_Y1/Y2/Y3 (based on current year)',
            'Impr_Followers': '((Followers_Start + Followers_End) / 2) × Posts × Reach_per_Post × Frequency_Impressions_per_User',
            'Impr_NonFollowers': 'Impr_Followers × NonFollower_Reach_Multiplier',
            'Social_Views': 'Impr_Followers + Impr_NonFollowers',
            'NewUnique_NonFollowers': 'Impr_NonFollowers / Frequency_Impressions_per_User',
            'Org_Visitors': 'NewUnique_NonFollowers × Organic_CTR_to_Site',
            'Inf_Visitors': 'Inf_Collabs × (Inf_Avg_Followers × Inf_Reach_Rate × Inf_Click_Rate) - FIX 1: calculated dynamically',
            'Other_Visitors': 'Other_Marketing_Budget / 2.0 (assumed $2 CPC)',
            'Visitors_Total': 'Org_Visitors + Inf_Visitors + Other_Visitors + PaidAds_Visitors',
            'Signups': 'Visitors_Total × ConvVS',
            'Org_Signups': 'Signups × (Org_Visitors / Visitors_Total)',
            'Inf_Signups': 'Signups × (Inf_Visitors / Visitors_Total)',
            'Other_Signups': 'Signups × (Other_Visitors / Visitors_Total)',
            'PaidAds_Signups': 'Signups × (PaidAds_Visitors / Visitors_Total) - NEW: signups da paid ads',
            # === NEW PAYERS BREAKDOWN (v7.4) ===
            'New_Payers_from_New_Signups': 'Org_New_Payers + Inf_New_Payers + Other_New_Payers + PaidAds_New_Payers - conversione immediata da nuovi signup',
            'New_Payers_from_Existing_Free': 'Free_Active_Users × Existing_Free_to_Paid_Monthly_Conv_Rate - conversione ritardata da free esistenti (0.75% default)',
            'New_Payers_from_Referral': 'Signups × Referral_Rate × (1 - Paying_Start/Market_Max) - nuovi paganti da referral',
            'Referral_New_Payers': 'Legacy column, same as New_Payers_from_Referral',
            'Org_New_Payers': 'Org_Signups × ConvSP',
            'Inf_New_Payers': 'Inf_Signups × ConvSP',
            'Other_New_Payers': 'Other_Signups × ConvSP',
            'PaidAds_New_Payers': 'PaidAds_Signups × ConvSP - NEW: paying users da paid ads',
            'New_Paying_Users': 'New_Payers_from_New_Signups + New_Payers_from_Existing_Free + New_Payers_from_Referral (v7.4: include free esistenti)',
            'Churn_Rate': 'Churn_Rate parameter (unified for all years)',
            'Paying_Users_Start': 'Previous month Paying_Users_End (or 0 for first month)',
            'Churned_Users': 'Paying_Users_Start × Churn_Rate',
            'Paying_Users_End': 'max(0, Paying_Users_Start - Churned_Users + New_Paying_Users) capped at Market_Max',
            'Cumulative_Signups': 'Somma cumulativa di tutti i Signups da inizio simulazione',
            'Free_Users_Start': 'Previous month Free_Users_End (or 0 for first month)',
            'Free_Active_Users': 'Free_Users_Start × Free_Active_Share (default 50%) - utenti free considerati attivi',
            'Free_Users_End': 'max(0, Free_Users_Start + Signups - New_Payers_from_New_Signups - New_Payers_from_Existing_Free)',
            'Total_Users_End': 'Paying_Users_End + Free_Users_End - totale utenti registrati',
            'ARPU': 'ARPU parameter from assumptions',
            'MRR': 'Paying_Users_End × ARPU',
            'Org_Marketing_Spend': 'Posts × Org_Cost_per_Post',
            'Inf_Marketing_Spend': 'Inf_New_Payers × Influencer_Reward_per_Sub',
            'Other_Marketing_Spend': 'Other_Marketing_Budget (unified for all years)',
            'Referral_Marketing_Spend': 'Referral_New_Payers × Referral_Reward_per_Sub',
            'FollowerAds_Spend': 'min(PaidAds_Monthly_Budget, Annual_Remaining, Total_Remaining) se Fase 1. Stop se raggiunto limite annuale o totale.',
            'ClickAds_Spend': 'min(PaidAds_Monthly_Budget, Annual_Remaining, Total_Remaining) se Fase 2. Stop se raggiunto limite annuale o totale.',
            'Annual_PaidAds_Spend': 'Somma spesa ads nell\'anno corrente. Si resetta a 0 ogni nuovo anno. Limite: PaidAds_Max_Annual_Budget.',
            'Cumulative_PaidAds_Spend': 'Somma cumulativa lifetime di tutti gli ads. Limite: PaidAds_Max_Total_Budget.',
            'Paid_FollowerAds_Impressions': '(FollowerAds_Spend / FollowerAds_CPM_EUR) × 1000',
            'Paid_FollowerAds_Reach': 'Paid_FollowerAds_Impressions / Frequency_Impressions_per_User',
            'Paid_FollowerAds_NewFollowers': 'Paid_FollowerAds_Reach × FollowerAds_Reach_to_Follower_Rate',
            'Paid_FollowerAds_Visitors': 'Paid_FollowerAds_Reach × FollowerAds_CTR_to_Site (FIX 3: visitors from follower ads)',
            'Paid_ClickAds_Visitors': 'ClickAds_Spend / ClickAds_CPC_EUR (FIX 4: direct calculation, 1 click ≈ 1 visitor)',
            'PaidAds_Visitors': 'Paid_FollowerAds_Visitors + Paid_ClickAds_Visitors (FIX 3: visitors from BOTH ad types)',
            'PaidAds_Marketing_Spend': 'FollowerAds_Spend + ClickAds_Spend',
            'Total_Marketing_Spend': 'Org_Marketing_Spend + Inf_Marketing_Spend + Other_Marketing_Spend + Referral_Marketing_Spend + PaidAds_Marketing_Spend',
            'DataSub_Cost': 'DataSub_Fee if MRR ≥ DataSub_MRR_Threshold, else 0',
            'XAPI_Cost': 'XAPI_Fee if MRR ≥ XAPI_MRR_Threshold, else 0',
            'Direct_Costs': 'DataSub_Cost + XAPI_Cost (variable costs that scale with usage)',
            'Gross_Profit': 'MRR - Direct_Costs (revenue minus variable costs)',
            'Gross_Margin_Month': 'IF(MRR > 0, Gross_Profit / MRR, 0) - monthly gross margin percentage',
            'Base_Fixed_Cost': 'BaseFixedCost × (1 + FixedCost_Annual_Growth)^(Year-1) - costi fissi con crescita annuale',
            'Total_Costs': 'Total_Marketing_Spend + DataSub_Cost + XAPI_Cost + Base_Fixed_Cost',
            'Net_Cash_Flow': 'MRR - Total_Costs',
            'Cumulative_Cash': 'Previous month Cumulative_Cash + Net_Cash_Flow (or Net_Cash_Flow for first month)',
        }
        
        # Yearly Summary Formulas
        yearly_formulas = {
            'Year': 'Year number (1, 2, or 3)',
            'End_Paying_Users': 'Last month of year: Paying_Users_End',
            'End_MRR_EUR': 'Last month of year: MRR',
            'ARR_EUR': 'End_MRR_EUR × 12',
            'Total_New_Customers': 'SUM(New_Paying_Users) for all months in year',
            'Org_New_Payers': 'SUM(Org_New_Payers) for all months in year',
            'Inf_New_Payers': 'SUM(Inf_New_Payers) for all months in year',
            'Other_New_Payers': 'SUM(Other_New_Payers) for all months in year',
            'PaidAds_New_Payers': 'SUM(PaidAds_New_Payers) for all months in year - NEW: paying users da paid ads',
            'Referral_New_Payers': 'SUM(Referral_New_Payers) for all months in year',
            # === NEW PAYERS BREAKDOWN (v7.4) ===
            'New_Payers_from_New_Signups': 'SUM(New_Payers_from_New_Signups) for all months in year',
            'New_Payers_from_Existing_Free': 'SUM(New_Payers_from_Existing_Free) for all months in year - conversione da free esistenti',
            'New_Payers_from_Referral': 'SUM(New_Payers_from_Referral) for all months in year',
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
            'Assumed_Monthly_Churn': 'Churn_Rate parameter (unified for all years)',
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
        
        # Check if it's a monthly or yearly table
        if 'Month' in self.df.columns:
            return monthly_formulas.get(col_name, None)
        else:
            return yearly_formulas.get(col_name, None)
    
    def update_from_dataframe(self, df: pd.DataFrame, format_as_integer: bool = None):
        """Update table contents from DataFrame.
        
        Args:
            df: DataFrame to display
            format_as_integer: If True, format numeric values as integers. 
                             If None, uses self.format_as_integer
        """
        if format_as_integer is None:
            format_as_integer = self.format_as_integer
            
        self.df = df.copy()
        
        # DEBUG: Print DataFrame info
        print(f"[DEBUG] update_from_dataframe called")
        print(f"[DEBUG] DataFrame shape: {df.shape}")
        print(f"[DEBUG] DataFrame columns: {df.columns.tolist()}")
        if len(df) > 0:
            print(f"[DEBUG] First row values: {df.iloc[0].tolist()}")
        
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        
        print(f"[DEBUG] Table row count: {self.table.rowCount()}")
        print(f"[DEBUG] Table column count: {self.table.columnCount()}")
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                value = df.iloc[i, j]
                
                # Colonne che devono mantenere i decimali anche nelle tabelle Monthly/Yearly
                # (ratios, percentuali, metriche unitarie)
                decimal_columns = {
                    'Churn_Rate', 'Churn', 'ChurnY1', 'ChurnY2', 'ChurnY3',
                    'ARPU', 'ConvVS', 'ConvSP',
                    'Gross_Margin_Month', 'Gross_Margin_Year',
                    'Follower_Monthly_Growth', 'Follower_Growth_Effective',
                    'CAC', 'LTV_EUR', 'LTV_CAC_Ratio',
                    'FollowerAds_CPM_EUR', 'ClickAds_CPC_EUR',
                    'Referral_Monthly_Rate', 'referral_capacity'
                }
                
                # Format value
                if isinstance(value, (int, float)):
                    if format_as_integer and col not in decimal_columns:
                        # Format as integer for Monthly/Yearly tables (non-ratio columns)
                        text = f"{int(round(value)):,}"
                    elif col in decimal_columns or not format_as_integer:
                        # Format with decimals for ratio/percentage columns or Assumptions
                        if abs(value) < 1 and value != 0:
                            # Small decimals (ratios): show 4 decimal places
                            text = f"{value:.4f}"
                        else:
                            # Larger numbers: show 2 decimal places
                            text = f"{value:.2f}"
                    else:
                        text = f"{value:.2f}"
                else:
                    text = str(value)
                
                item = QTableWidgetItem(text)
                
                # Make certain columns read-only (calculated fields)
                if self.editable_columns is not None and col not in self.editable_columns:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    # Light gray background for read-only cells (Excel-style)
                    from PyQt6.QtGui import QColor, QBrush
                    item.setBackground(QBrush(QColor(240, 240, 240)))
                    item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text
                else:
                    # White background for editable cells
                    from PyQt6.QtGui import QColor, QBrush
                    item.setBackground(QBrush(QColor(255, 255, 255)))
                    item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text
                
                self.table.setItem(i, j, item)
        
        # DEBUG: Print first row after population
        if self.table.rowCount() > 0:
            first_row_gui = [self.table.item(0, c).text() if self.table.item(0, c) else "None" 
                            for c in range(self.table.columnCount())]
            print(f"[DEBUG] First row in GUI table: {first_row_gui}")
        
        # Resize columns to content and ensure headers are fully visible
        self.table.resizeColumnsToContents()
        
        # Ensure column width is at least wide enough for header text
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header_text = self.table.horizontalHeaderItem(i).text() if self.table.horizontalHeaderItem(i) else ""
            # Calculate minimum width needed for header (approximate: 8 pixels per character + padding)
            min_width = len(header_text) * 8 + 20
            current_width = self.table.columnWidth(i)
            if current_width < min_width:
                self.table.setColumnWidth(i, min_width)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert table contents back to DataFrame."""
        data = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if item is not None:
                    text = item.text().replace(',', '')  # Remove thousand separators
                    row.append(text)
                else:
                    row.append('')
            data.append(row)
        
        df = pd.DataFrame(data, columns=self.df.columns)
        
        # Convert numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='ignore')
        
        return df
    
    def setTitle(self, title: str):
        """Update the title label."""
        self.title_label.setText(f"<b style='color: black;'>{title}</b>")


class ChartsWidget(QWidget):
    """Widget to display interactive matplotlib charts with scroll and hover support."""
    
    def __init__(self):
        super().__init__()
        
        from PyQt6.QtWidgets import QScrollArea
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area with mouse wheel support
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        
        # Create matplotlib figure - dimensioni ragionevoli (aumentata altezza per 8 grafici)
        self.figure = Figure(figsize=(12, 18), dpi=80)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(900, 1300)
        
        # Add navigation toolbar for zoom/pan
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        # Tooltip annotation (will be created per-axis in update_charts)
        self.annot = None
        self.monthly_df = None
        
        container_layout.addWidget(self.toolbar)
        container_layout.addWidget(self.canvas)
        container.setLayout(container_layout)
        
        self.scroll_area.setWidget(container)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
        
        # Connect mouse motion event for hover tooltips
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
    
    def on_hover(self, event):
        """Show tooltip with values when hovering over charts."""
        if event.inaxes is None or self.monthly_df is None:
            return
        
        ax = event.inaxes
        x = event.xdata
        
        if x is None:
            return
        
        # Get month index (1-based)
        month_idx = int(round(x))
        if month_idx < 1 or month_idx > len(self.monthly_df):
            return
        
        # Get data for this month
        row = self.monthly_df.iloc[month_idx - 1]
        
        # Build tooltip text based on which chart we're in
        title = ax.get_title()
        tooltip_lines = [f"Month {month_idx}"]
        
        if 'MRR' in title:
            tooltip_lines.append(f"MRR: €{row['MRR']:,.0f}")
        elif 'Paying Users' in title or 'Followers' in title:
            tooltip_lines.append(f"Paying Users: {row['Paying_Users_End']:,.0f}")
            tooltip_lines.append(f"Followers: {row['Followers_End']:,.0f}")
        elif 'Cumulative Cash' in title:
            tooltip_lines.append(f"Cash: €{row['Cumulative_Cash']:,.0f}")
        elif 'Marketing Spend' in title:
            tooltip_lines.append(f"Organic: €{row['Org_Marketing_Spend']:,.0f}")
            tooltip_lines.append(f"Paid Ads: €{row['PaidAds_Marketing_Spend']:,.0f}")
            tooltip_lines.append(f"Referral: €{row['Referral_Marketing_Spend']:,.0f}")
        elif 'Funnel' in title:
            tooltip_lines.append(f"Visitors: {row['Visitors_Total']:,.0f}")
            tooltip_lines.append(f"Signups: {row['Signups']:,.0f}")
            tooltip_lines.append(f"New Paying: {row['New_Paying_Users']:,.0f}")
        elif 'Unit Economics' in title or 'Gross Margin' in title:
            tooltip_lines.append(f"Gross Margin: {row['Gross_Margin_Month']*100:.1f}%")
            tooltip_lines.append(f"Net Cash Flow: €{row['Net_Cash_Flow']:,.0f}")
        elif 'Breakeven' in title or 'Expenses' in title:
            tooltip_lines.append(f"MRR: €{row['MRR']:,.0f}")
            tooltip_lines.append(f"Total Costs: €{row['Total_Costs']:,.0f}")
            diff = row['MRR'] - row['Total_Costs']
            tooltip_lines.append(f"Profit/Loss: €{diff:,.0f}")
        elif 'Users Breakdown' in title or 'Paying vs Free' in title:
            if 'Free_Users_End' in row:
                tooltip_lines.append(f"Paying Users: {row['Paying_Users_End']:,.0f}")
                tooltip_lines.append(f"Free Users: {row['Free_Users_End']:,.0f}")
                tooltip_lines.append(f"Total Users: {row['Total_Users_End']:,.0f}")
        
        tooltip_text = "\\n".join(tooltip_lines)
        
        # Update status bar with tooltip (simpler than annotation)
        self.setToolTip(tooltip_text.replace("\\n", "\n"))
    
    def wheelEvent(self, event):
        """Handle mouse wheel for scrolling."""
        # Get scroll delta
        delta = event.angleDelta().y()
        
        # Scroll the scroll area
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() - delta)
        
        event.accept()
    
    def update_charts(self, monthly_df: pd.DataFrame):
        """Update all charts with new data and hover support."""
        self.monthly_df = monthly_df  # Store for hover tooltips
        self.figure.clear()
        
        # Create 9 subplots (5 righe x 2 colonne, ultimo slot vuoto)
        ax1 = self.figure.add_subplot(5, 2, 1)
        ax2 = self.figure.add_subplot(5, 2, 2)
        ax3 = self.figure.add_subplot(5, 2, 3)
        ax4 = self.figure.add_subplot(5, 2, 4)
        ax5 = self.figure.add_subplot(5, 2, 5)
        ax6 = self.figure.add_subplot(5, 2, 6)
        ax7 = self.figure.add_subplot(5, 2, 7)
        ax8 = self.figure.add_subplot(5, 2, 8)
        ax9 = self.figure.add_subplot(5, 2, 9)
        ax10 = self.figure.add_subplot(5, 2, 10)
        
        # Create month index
        month_index = list(range(1, len(monthly_df) + 1))
        
        # ===== Chart 1: MRR over time =====
        ax1.plot(month_index, monthly_df['MRR'], linewidth=2, color='#2E86AB', label='MRR')
        ax1.set_title('Monthly Recurring Revenue (MRR)', fontweight='bold', fontsize=10)
        ax1.set_xlabel('Month', fontsize=8)
        ax1.set_ylabel('MRR (EUR)', fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax1.tick_params(axis='both', labelsize=7)
        
        # Linea verticale quando ARR raggiunge €1M (MRR >= 83,333)
        arr_target = 1_000_000  # €1M ARR
        mrr_target = arr_target / 12  # ~€83,333 MRR
        mrr_values = monthly_df['MRR'].values
        arr_1m_month = None
        for idx, mrr_val in enumerate(mrr_values):
            if mrr_val >= mrr_target:
                arr_1m_month = idx + 1  # Month index (1-based)
                break
        
        if arr_1m_month is not None:
            ax1.axvline(x=arr_1m_month, color='#ffd166', linestyle='--', linewidth=2, alpha=0.8)
            ax1.annotate(f'€1M ARR\n(Month {arr_1m_month})', 
                        xy=(arr_1m_month, mrr_values[arr_1m_month-1]), 
                        xytext=(arr_1m_month + 2, mrr_values[arr_1m_month-1] * 0.7),
                        fontsize=7, color='#e67e22', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1))
        
        # ===== Chart 2: Paying Users & Followers =====
        ax2.plot(month_index, monthly_df['Paying_Users_End'], linewidth=2, color='#06d6a0', label='Paying Users')
        ax2.set_xlabel('Month', fontsize=8)
        ax2.set_ylabel('Paying Users', color='#06d6a0', fontsize=8)
        ax2.tick_params(axis='y', labelcolor='#06d6a0', labelsize=7)
        ax2.tick_params(axis='x', labelsize=7)
        
        # Asse secondario per Followers
        ax2b = ax2.twinx()
        ax2b.plot(month_index, monthly_df['Followers_End'], linewidth=2, color='#9b59b6', label='Followers')
        ax2b.set_ylabel('Followers', color='#9b59b6', fontsize=8)
        ax2b.tick_params(axis='y', labelcolor='#9b59b6', labelsize=7)
        
        ax2.set_title('Paying Users & Followers Growth', fontweight='bold', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Legend manuale
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], color='#06d6a0', lw=2, label='Paying Users'),
                          Line2D([0], [0], color='#9b59b6', lw=2, label='Followers')]
        ax2.legend(handles=legend_elements, loc='upper left', fontsize=7)
        
        # ===== Chart 3: Cumulative Cash Flow =====
        cash_values = monthly_df['Cumulative_Cash'].values
        ax3.plot(month_index, cash_values, linewidth=2, color='#e63946', label='Cumulative Cash')
        ax3.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Break-even')
        ax3.set_title('Cumulative Cash Flow', fontweight='bold', fontsize=10)
        ax3.set_xlabel('Month', fontsize=8)
        ax3.set_ylabel('Cash (EUR)', fontsize=8)
        ax3.grid(True, alpha=0.3)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax3.legend(fontsize=7)
        ax3.tick_params(axis='both', labelsize=7)
        
        # Fill area sopra/sotto zero
        ax3.fill_between(month_index, cash_values, 0, 
                        where=[v >= 0 for v in cash_values], alpha=0.3, color='green', interpolate=True)
        ax3.fill_between(month_index, cash_values, 0, 
                        where=[v < 0 for v in cash_values], alpha=0.3, color='red', interpolate=True)
        
        # ===== Chart 4: Marketing Spend Breakdown (Stacked Area) =====
        ax4.stackplot(month_index, 
                     monthly_df['Org_Marketing_Spend'].values,
                     monthly_df['Inf_Marketing_Spend'].values,
                     monthly_df['PaidAds_Marketing_Spend'].values,
                     monthly_df['Referral_Marketing_Spend'].values,
                     monthly_df['Other_Marketing_Spend'].values,
                     labels=['Organic', 'Influencer', 'Paid Ads', 'Referral', 'Other'],
                     colors=['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6'],
                     alpha=0.7)
        ax4.set_title('Marketing Spend by Channel', fontweight='bold', fontsize=10)
        ax4.set_xlabel('Month', fontsize=8)
        ax4.set_ylabel('Spend (EUR)', fontsize=8)
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax4.legend(loc='upper left', fontsize=6)
        ax4.tick_params(axis='both', labelsize=7)
        
        # ===== Chart 5: Conversion Funnel (Visitors → Signups → New Payers) =====
        ax5.plot(month_index, monthly_df['Visitors_Total'].values, linewidth=2, 
                color='#3498db', label='Visitors', alpha=0.8)
        ax5.plot(month_index, monthly_df['Signups'].values, linewidth=2, 
                color='#f39c12', label='Signups', alpha=0.8)
        ax5.plot(month_index, monthly_df['New_Paying_Users'].values, linewidth=2, 
                color='#27ae60', label='New Paying', alpha=0.8)
        ax5.set_title('Conversion Funnel', fontweight='bold', fontsize=10)
        ax5.set_xlabel('Month', fontsize=8)
        ax5.set_ylabel('Count', fontsize=8)
        ax5.grid(True, alpha=0.3)
        ax5.legend(fontsize=7)
        # Usa scala log solo se i valori sono > 0
        if monthly_df['New_Paying_Users'].min() > 0:
            ax5.set_yscale('log')
        ax5.tick_params(axis='both', labelsize=7)
        
        # ===== Chart 6: Unit Economics (Gross Margin % & Net Cash Flow) =====
        gross_margin_pct = monthly_df['Gross_Margin_Month'].values * 100
        ax6.plot(month_index, gross_margin_pct, linewidth=2, color='#16a085', label='Gross Margin %')
        ax6.set_ylabel('Gross Margin (%)', color='#16a085', fontsize=8)
        ax6.tick_params(axis='y', labelcolor='#16a085', labelsize=7)
        ax6.tick_params(axis='x', labelsize=7)
        ax6.set_ylim(0, 105)
        
        # Net Cash Flow sull'asse destro
        ax6b = ax6.twinx()
        ax6b.plot(month_index, monthly_df['Net_Cash_Flow'].values, linewidth=2, color='#c0392b', label='Net Cash Flow')
        ax6b.axhline(y=0, color='black', linestyle='--', linewidth=0.5, alpha=0.5)
        ax6b.set_ylabel('Net Cash Flow (EUR)', color='#c0392b', fontsize=8)
        ax6b.tick_params(axis='y', labelcolor='#c0392b', labelsize=7)
        ax6b.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        
        ax6.set_title('Unit Economics: Gross Margin & Cash Flow', fontweight='bold', fontsize=10)
        ax6.set_xlabel('Month', fontsize=8)
        ax6.grid(True, alpha=0.3)
        
        legend_elements6 = [Line2D([0], [0], color='#16a085', lw=2, label='Gross Margin %'),
                           Line2D([0], [0], color='#c0392b', lw=2, label='Net Cash Flow')]
        ax6.legend(handles=legend_elements6, loc='lower right', fontsize=7)
        
        # ===== Chart 7: MRR vs Total Expenses (Breakeven) =====
        mrr_values_ch7 = monthly_df['MRR'].values
        expenses_values = monthly_df['Total_Costs'].values
        
        ax7.plot(month_index, mrr_values_ch7, linewidth=2, color='#2E86AB', label='MRR (Revenue)')
        ax7.plot(month_index, expenses_values, linewidth=2, color='#e63946', label='Total Costs')
        
        # Green fill where MRR > Expenses (profit zone)
        ax7.fill_between(month_index, mrr_values_ch7, expenses_values,
                        where=[m > e for m, e in zip(mrr_values_ch7, expenses_values)],
                        alpha=0.3, color='green', interpolate=True, label='Profit Zone')
        
        # Red fill where MRR <= Expenses (loss zone)
        ax7.fill_between(month_index, mrr_values_ch7, expenses_values,
                        where=[m <= e for m, e in zip(mrr_values_ch7, expenses_values)],
                        alpha=0.3, color='red', interpolate=True, label='Loss Zone')
        
        # Linea verticale quando ARR raggiunge €1M
        if arr_1m_month is not None:
            ax7.axvline(x=arr_1m_month, color='#ffd166', linestyle='--', linewidth=2, alpha=0.8)
            ax7.annotate(f'€1M ARR', 
                        xy=(arr_1m_month, mrr_values_ch7[arr_1m_month-1]), 
                        xytext=(arr_1m_month + 2, max(mrr_values_ch7) * 0.5),
                        fontsize=7, color='#e67e22', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1))
        
        ax7.set_title('Revenue vs Expenses (Breakeven)', fontweight='bold', fontsize=10)
        ax7.set_xlabel('Month', fontsize=8)
        ax7.set_ylabel('EUR', fontsize=8)
        ax7.grid(True, alpha=0.3)
        ax7.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax7.legend(fontsize=7, loc='upper left')
        ax7.tick_params(axis='both', labelsize=7)
        
        # ===== Chart 8: Users Breakdown (Paying vs Free vs Total) =====
        # Check if Free_Users_End column exists (new feature)
        if 'Free_Users_End' in monthly_df.columns:
            paying_users = monthly_df['Paying_Users_End'].values
            free_users = monthly_df['Free_Users_End'].values
            total_users = monthly_df['Total_Users_End'].values
            
            ax8.stackplot(month_index, paying_users, free_users,
                         labels=['Paying Users', 'Free Users'],
                         colors=['#06d6a0', '#95a5a6'], alpha=0.7)
            ax8.plot(month_index, total_users, linewidth=2, color='#2c3e50', 
                    linestyle='--', label='Total Users')
            
            ax8.set_title('Users Breakdown: Paying vs Free', fontweight='bold', fontsize=10)
            ax8.set_xlabel('Month', fontsize=8)
            ax8.set_ylabel('Users', fontsize=8)
            ax8.grid(True, alpha=0.3)
            ax8.legend(fontsize=7, loc='upper left')
            ax8.tick_params(axis='both', labelsize=7)
        else:
            # Fallback if columns don't exist yet
            ax8.text(0.5, 0.5, 'Recalculate to see\nUsers Breakdown', 
                    ha='center', va='center', transform=ax8.transAxes, fontsize=10)
            ax8.set_title('Users Breakdown: Paying vs Free', fontweight='bold', fontsize=10)
        
        # ===== Chart 9: New Payers by Channel =====
        # Show monthly new payers breakdown by acquisition channel
        if 'Org_New_Payers' in monthly_df.columns:
            org_new = monthly_df['Org_New_Payers'].values
            ads_new = monthly_df['PaidAds_New_Payers'].values
            inf_new = monthly_df['Inf_New_Payers'].values
            other_new = monthly_df['Other_New_Payers'].values
            
            ax9.stackplot(month_index, org_new, ads_new, inf_new, other_new,
                         labels=['Organic', 'Paid Ads', 'Influencer', 'Other'],
                         colors=['#06d6a0', '#ef476f', '#ffd166', '#118ab2'], alpha=0.7)
            
            # Line for total new payers
            total_new = org_new + ads_new + inf_new + other_new
            ax9.plot(month_index, total_new, linewidth=2, color='#2c3e50', 
                    linestyle='--', label='Total New Payers')
            
            ax9.set_title('New Payers by Channel', fontweight='bold', fontsize=10)
            ax9.set_xlabel('Month', fontsize=8)
            ax9.set_ylabel('New Payers', fontsize=8)
            ax9.grid(True, alpha=0.3)
            ax9.legend(fontsize=7, loc='upper left')
            ax9.tick_params(axis='both', labelsize=7)
        else:
            # Fallback if columns don't exist yet
            ax9.text(0.5, 0.5, 'Recalculate to see\nNew Payers by Channel', 
                    ha='center', va='center', transform=ax9.transAxes, fontsize=10)
            ax9.set_title('New Payers by Channel', fontweight='bold', fontsize=10)
        
        # ===== Chart 10: CAC e LTV nel tempo =====
        # Mostra l'andamento del CAC cumulativo e LTV con dual axis
        if 'Cumulative_CAC' in monthly_df.columns:
            cac_values = monthly_df['Cumulative_CAC'].values
            ltv_values = monthly_df['Monthly_LTV'].values
            ratio_values = monthly_df['LTV_CAC_Ratio'].values
            
            # Asse principale per CAC e LTV (in EUR)
            line1, = ax10.plot(month_index, cac_values, linewidth=2, color='#ef476f', label='CAC (cumulative)')
            line2, = ax10.plot(month_index, ltv_values, linewidth=2, color='#06d6a0', label='LTV')
            
            ax10.set_title('CAC vs LTV over Time', fontweight='bold', fontsize=10)
            ax10.set_xlabel('Month', fontsize=8)
            ax10.set_ylabel('EUR', fontsize=8, color='#2c3e50')
            ax10.grid(True, alpha=0.3)
            ax10.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
            ax10.tick_params(axis='both', labelsize=7)
            
            # Asse secondario per LTV/CAC ratio
            ax10_twin = ax10.twinx()
            line3, = ax10_twin.plot(month_index, ratio_values, linewidth=2, color='#118ab2', 
                                    linestyle='--', label='LTV/CAC Ratio')
            ax10_twin.set_ylabel('LTV/CAC Ratio', fontsize=8, color='#118ab2')
            ax10_twin.tick_params(axis='y', labelsize=7, labelcolor='#118ab2')
            
            # Linea orizzontale a ratio=3 (benchmark sano)
            ax10_twin.axhline(y=3, color='#ffd166', linestyle=':', linewidth=1.5, alpha=0.7)
            
            # Legenda combinata
            lines = [line1, line2, line3]
            labels = [l.get_label() for l in lines]
            ax10.legend(lines, labels, fontsize=7, loc='upper left')
        else:
            # Fallback if columns don't exist yet
            ax10.text(0.5, 0.5, 'Recalculate to see\nCAC vs LTV', 
                    ha='center', va='center', transform=ax10.transAxes, fontsize=10)
            ax10.set_title('CAC vs LTV over Time', fontweight='bold', fontsize=10)
        
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()


# =====================
# MAIN WINDOW
# =====================

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, state: dict, n_years: int = 3):
        super().__init__()
        
        self.assumptions_df = state['assumptions']
        self.monthly_df = state['monthly']
        self.yearly_df = state['yearly']
        self.n_years = n_years  # Store simulation duration
        
        self.json_path = 'model_state.json'
        self.excel_path = 'ai_finance_dynamic_model_v7_channels.xlsx'
        
        self.setWindowTitle('AI Finance Platform - Interactive Financial Model v2 (Excel v7 with Channels)')
        self.setGeometry(100, 100, 1400, 900)
        
        self.setup_ui()
        self.statusBar().showMessage('Ready')
    
    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set window background to white
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #d0d0d0;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #d0d0d0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h3 style='color: black;'>AI Finance Platform - Interactive Financial Model v2 (Excel v7 Channels)</h3>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Simulation duration control
        duration_layout = QHBoxLayout()
        duration_layout.addStretch()
        duration_label = QLabel("<b>Simulation Duration (Years):</b>")
        duration_label.setStyleSheet("color: black; font-size: 10pt;")
        duration_layout.addWidget(duration_label)
        
        self.years_spinbox = QSpinBox()
        self.years_spinbox.setRange(1, 10)
        self.years_spinbox.setValue(self.n_years)
        self.years_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: black;
                border: 2px solid #2E86AB;
                border-radius: 4px;
                padding: 4px;
                font-size: 10pt;
                font-weight: bold;
                min-width: 60px;
            }
        """)
        self.years_spinbox.valueChanged.connect(self.on_years_changed)
        duration_layout.addWidget(self.years_spinbox)
        duration_layout.addStretch()
        main_layout.addLayout(duration_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Assumptions (editable: Value, Notes columns)
        self.assumptions_table = DataTableWidget(
            self.assumptions_df, 
            "Model Assumptions",
            editable_columns=['Value', 'Notes'],
            format_as_integer=False
        )
        self.tabs.addTab(self.assumptions_table, "🔧 Assumptions")
        
        # Tab 2: Monthly Model (dynamically calculated based on n_years)
        self.monthly_table = DataTableWidget(
            self.monthly_df, 
            f"Monthly Model ({self.n_years * 12} Months)",
            editable_columns=[],  # v7 columns are mostly calculated
            format_as_integer=True,
            show_formulas=True
        )
        self.tabs.addTab(self.monthly_table, "📅 Monthly Model")
        
        # Tab 3: Yearly Summary (read-only)
        self.yearly_table = DataTableWidget(
            self.yearly_df, 
            "Yearly Summary",
            editable_columns=[],
            format_as_integer=True,
            show_formulas=True
        )
        self.tabs.addTab(self.yearly_table, "📊 Yearly Summary")
        
        # Tab 4: Charts (interactive with hover and zoom/pan)
        self.charts_widget = ChartsWidget()
        self.tabs.addTab(self.charts_widget, "📈 Interactive Charts")
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.recalc_button = QPushButton("🔄 Recalculate & Update Charts")
        self.recalc_button.setStyleSheet("""
            QPushButton { 
                background-color: #2E86AB; 
                color: white; 
                font-weight: bold; 
                font-size: 10pt;
                padding: 8px; 
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #247096;
            }
        """)
        self.recalc_button.clicked.connect(self.recalculate_model)
        button_layout.addWidget(self.recalc_button)
        
        self.save_button = QPushButton("💾 Save JSON")
        self.save_button.setStyleSheet("""
            QPushButton { 
                background-color: #06d6a0; 
                color: white; 
                font-weight: bold; 
                font-size: 10pt;
                padding: 8px; 
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #05b989;
            }
        """)
        self.save_button.clicked.connect(self.save_model)
        button_layout.addWidget(self.save_button)
        
        self.export_button = QPushButton("📤 Export JSON As...")
        self.export_button.setStyleSheet("""
            QPushButton { 
                background-color: white; 
                color: black; 
                font-weight: bold; 
                font-size: 9pt;
                padding: 8px; 
                border: 2px solid #d0d0d0;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #2E86AB;
            }
        """)
        self.export_button.clicked.connect(self.export_json)
        button_layout.addWidget(self.export_button)
        
        self.reload_excel_button = QPushButton("📥 Import from Excel...")
        self.reload_excel_button.setStyleSheet("""
            QPushButton { 
                background-color: white; 
                color: black; 
                font-weight: bold; 
                font-size: 9pt;
                padding: 8px; 
                border: 2px solid #d0d0d0;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #e63946;
            }
        """)
        self.reload_excel_button.clicked.connect(self.reload_from_excel)
        self.reload_excel_button.setToolTip("Select and import any Excel file with the same structure")
        button_layout.addWidget(self.reload_excel_button)
        
        main_layout.addLayout(button_layout)
        
        central_widget.setLayout(main_layout)
        
        # Initial chart update
        self.charts_widget.update_charts(self.monthly_df)
    
    def recalculate_model(self):
        """Recalculate the model based on current table values."""
        try:
            # Read current table data
            self.assumptions_df = self.assumptions_table.to_dataframe()
            self.monthly_df = self.monthly_table.to_dataframe()
            
            # Recalculate model with current n_years
            self.monthly_df, self.yearly_df = recalc_model(self.assumptions_df, self.monthly_df, self.n_years)
            
            # Update tables
            self.assumptions_table.update_from_dataframe(self.assumptions_df, format_as_integer=False)
            self.monthly_table.update_from_dataframe(self.monthly_df, format_as_integer=True)
            self.yearly_table.update_from_dataframe(self.yearly_df, format_as_integer=True)
            
            # Update monthly table title
            self.monthly_table.setTitle(f"Monthly Model ({self.n_years * 12} Months)")
            
            # Update charts
            self.charts_widget.update_charts(self.monthly_df)
            
            # Auto-save
            save_to_json(self.json_path, self.assumptions_df, self.monthly_df, self.yearly_df)
            
            self.statusBar().showMessage("✓ Model recalculated successfully", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Failed to recalculate model:\n{e}")
            self.statusBar().showMessage("✗ Recalculation failed", 3000)
    
    def on_years_changed(self, value):
        """Handle change in simulation duration."""
        self.n_years = value
        self.statusBar().showMessage(f"Simulation duration changed to {value} years. Click 'Recalculate' to update.", 5000)
    
    def save_model(self):
        """Save current state to JSON."""
        try:
            # Read current table data
            self.assumptions_df = self.assumptions_table.to_dataframe()
            self.monthly_df = self.monthly_table.to_dataframe()
            self.yearly_df = self.yearly_table.to_dataframe()
            
            # Save
            save_to_json(self.json_path, self.assumptions_df, self.monthly_df, self.yearly_df)
            
            QMessageBox.information(self, "Success", f"Model saved to {self.json_path}")
            self.statusBar().showMessage(f"✓ Saved to {self.json_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save model:\n{e}")
    
    def export_json(self):
        """Export state to a user-chosen JSON file."""
        try:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export JSON", "", "JSON Files (*.json)"
            )
            
            if filepath:
                self.assumptions_df = self.assumptions_table.to_dataframe()
                self.monthly_df = self.monthly_table.to_dataframe()
                self.yearly_df = self.yearly_table.to_dataframe()
                
                save_to_json(filepath, self.assumptions_df, self.monthly_df, self.yearly_df)
                
                QMessageBox.information(self, "Success", f"Exported to {filepath}")
                self.statusBar().showMessage(f"✓ Exported to {filepath}", 3000)
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{e}")
    
    def reload_from_excel(self):
        """Reload data from Excel file - allows user to choose any Excel file."""
        try:
            # Ask user to select Excel file
            filepath, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Excel File to Import", 
                "", 
                "Excel Files (*.xlsx *.xls);;All Files (*)"
            )
            
            if not filepath:
                # User cancelled
                return
            
            reply = QMessageBox.question(
                self, 'Confirm Import',
                f'Import data from:\n{filepath}\n\nThis will overwrite current state. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Load from selected Excel file (v7 format)
                state = load_from_excel_v7(filepath)
                
                # Recalculate to ensure consistency with current n_years
                state['monthly'], state['yearly'] = recalc_model(
                    state['assumptions'], state['monthly'], self.n_years
                )
                
                self.assumptions_df = state['assumptions']
                self.monthly_df = state['monthly']
                self.yearly_df = state['yearly']
                
                # Update the excel_path for future reference
                self.excel_path = filepath
                
                # Update tables
                self.assumptions_table.update_from_dataframe(self.assumptions_df, format_as_integer=False)
                self.monthly_table.update_from_dataframe(self.monthly_df, format_as_integer=True)
                self.yearly_table.update_from_dataframe(self.yearly_df, format_as_integer=True)
                
                # Update charts
                self.charts_widget.update_charts(self.monthly_df)
                
                # Save to JSON
                save_to_json(self.json_path, self.assumptions_df, self.monthly_df, self.yearly_df)
                
                QMessageBox.information(self, "Success", f"Imported from:\n{os.path.basename(filepath)}")
                self.statusBar().showMessage(f"✓ Imported from {os.path.basename(filepath)}", 3000)
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import from Excel:\n{e}\n\nMake sure the file has the correct structure (Model sheet with Assumptions, Monthly, Yearly data).")


# =====================
# MAIN ENTRY POINT
# =====================

def main():
    """Main entry point for the application."""
    
    json_path = 'model_state.json'
    excel_path = 'ai_finance_dynamic_model_v7_channels.xlsx'
    default_n_years = 3  # Default simulation duration
    
    # Load or import state
    if os.path.exists(json_path):
        print(f"Loading existing state from {json_path}")
        state = load_from_json(json_path)
    else:
        print(f"First run: importing from {excel_path}")
        state = load_from_excel_v7(excel_path)
        
        # Recalculate to ensure consistency with default duration
        state['monthly'], state['yearly'] = recalc_model(
            state['assumptions'], state['monthly'], default_n_years
        )
        
        # Save initial state
        save_to_json(json_path, state['assumptions'], state['monthly'], state['yearly'])
    
    # Create and run application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow(state, n_years=default_n_years)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
