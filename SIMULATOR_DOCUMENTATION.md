# 📊 AI Finance Platform - Documentazione Completa del Simulatore

## Indice
1. [Panoramica](#1-panoramica)
2. [Architettura del Sistema](#2-architettura-del-sistema)
3. [Parametri di Input (Assumptions)](#3-parametri-di-input-assumptions)
4. [Modello di Crescita Follower](#4-modello-di-crescita-follower)
5. [Funnel di Acquisizione Clienti](#5-funnel-di-acquisizione-clienti)
6. [Canali di Marketing](#6-canali-di-marketing)
7. [Paid Social Ads - Sistema Bifase](#7-paid-social-ads---sistema-bifase)
8. [Modello di Revenue](#8-modello-di-revenue)
9. [Struttura dei Costi](#9-struttura-dei-costi)
10. [Unit Economics](#10-unit-economics)
11. [Output Mensili](#11-output-mensili)
12. [Output Annuali](#12-output-annuali)
13. [Grafici e Visualizzazioni](#13-grafici-e-visualizzazioni)

---

## 1. Panoramica

Il simulatore è un modello finanziario SaaS B2C che simula la crescita di una piattaforma fintech attraverso canali social. 

### Caratteristiche Principali:
- **Durata simulazione**: configurabile (default 3 anni = 36 mesi)
- **Granularità**: mensile
- **Modello di crescita**: S-curve (logistico) con saturazione di mercato
- **Canali acquisizione**: Organic Social, Influencer, Paid Ads, Referral, Other
- **Persistenza**: JSON (stato salvato automaticamente)

---

## 2. Architettura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    ASSUMPTIONS (Input)                       │
│  Parametri editabili: ARPU, Churn, Conversion rates, etc.   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   RECALC ENGINE                              │
│  Loop mensile: calcola tutte le metriche per ogni mese      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT                                    │
│  Monthly Model (36+ righe) + Yearly Summary (3+ righe)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHARTS (6 grafici)                        │
│  MRR, Users, Cash Flow, Marketing Mix, Funnel, Economics    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Parametri di Input (Assumptions)

### 3.1 Revenue
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `ARPU` | EUR/mese/user | 20 | Average Revenue Per User mensile |

### 3.2 Conversion Rates
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `ConvVS` | ratio | 0.13 | Conversion Visitor → Signup (13%) |
| `ConvSP` | ratio | 0.035 | Conversion Signup → Paying (3.5%) |

**Formula Conversion Totale:**
```
Conversion_Visitor_to_Paying = ConvVS × ConvSP
Esempio: 0.13 × 0.035 = 0.00455 (0.455%)
```

### 3.3 Retention / Churn
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `ChurnY1` | monthly | 0.06 | Churn mensile anno 1 (6%) |
| `ChurnY2` | monthly | 0.055 | Churn mensile anno 2 (5.5%) |
| `ChurnY3` | monthly | 0.05 | Churn mensile anno 3 (5%) |

**Logica Churn:**
- Anno 1: usa ChurnY1
- Anno 2: usa ChurnY2
- Anno 3+: usa ChurnY3
- Se simulazione > 3 anni: cicla Y1→Y2→Y3→Y1...

### 3.4 Social / Follower Growth
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `Followers_0` | followers | 1000 | Follower iniziali |
| `Follower_Monthly_Growth` | ratio | 0.08 | Tasso crescita base (8%/mese) |
| `Posts_per_Month_Y1` | posts/mese | 120 | Post pubblicati al mese |
| `Reach_per_Post` | ratio | 0.04 | Reach organica per post (4% dei follower) |
| `NonFollower_Reach_Multiplier` | ratio | 0.5 | Moltiplicatore reach non-follower |
| `Frequency_Impressions_per_User` | impressions | 1.5 | Frequenza media per utente |
| `Organic_CTR_to_Site` | ratio | 0.015 | CTR organico verso sito (1.5%) |

### 3.5 Market Size (TAM/SAM/SOM)
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `Market_Max_Followers_Local` | followers | 50,000 | Tetto follower mercato locale |
| `Market_Max_Followers_Global` | followers | 1,000,000 | Tetto follower mercato globale |
| `Market_Max_PayingUsers_Local` | users | 2,000 | Tetto paying users locale |
| `Market_Max_PayingUsers_Global` | users | 25,000 | Tetto paying users globale |
| `Follower_Adoption_Ramp_Months` | mesi | 24 | Mesi per raggiungere crescita max |

### 3.6 Influencer Marketing
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `Inf_Avg_Followers` | followers | 50,000 | Follower medi per influencer |
| `Inf_Reach_Rate` | ratio | 0.3 | Reach rate influencer (30%) |
| `Inf_Click_Rate` | ratio | 0.02 | CTR link influencer (2%) |
| `Inf_Collabs_Y1` | collabs/mese | 1 | Collaborazioni mensili |
| `Influencer_Reward_per_Sub` | EUR | 10 | Reward per nuovo subscriber |

### 3.7 Referral
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `Referral_Monthly_Rate` | ratio | 0.02 | Probabilità lifetime che un nuovo utente registrato inviti un amico (2%). Applicata una sola volta alla coorte di nuovi Signups del mese. |
| `Referral_Reward_per_Sub` | EUR | 10 | Reward per referral |

### 3.8 Paid Social Ads
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `PaidAds_Monthly_Budget` | EUR/mese | 500 | Budget mensile campagne |
| `PaidAds_Max_Total_Budget` | EUR | 0 | Budget max totale (0=illimitato) |
| `FollowerAds_CPM_EUR` | EUR/1000 impr | 7 | CPM campagne follower |
| `FollowerAds_Reach_to_Follower_Rate` | ratio | 0.01 | % reach che diventa follower |
| `FollowerAds_CTR_to_Site` | ratio | 0.01 | CTR ads verso sito |
| `ClickAds_CPC_EUR` | EUR/click | 2 | CPC campagne click |
| `Follower_Threshold_For_Click_Ads` | followers | 20,000 | Soglia switch Fase1→Fase2 |

### 3.9 Costs
| Parametro | Unità | Default | Descrizione |
|-----------|-------|---------|-------------|
| `BaseFixedCost` | EUR/mese | 1000 | Costi fissi base |
| `Org_Cost_per_Post` | EUR/post | 1 | Costo produzione contenuto |
| `Other_Marketing_Budget_Y1` | EUR/mese | 200 | Budget altri canali |
| `DataSub_Fee` | EUR/mese | 2000 | Fee data subscription |
| `DataSub_MRR_Threshold` | EUR MRR | 5000 | Soglia attivazione DataSub |
| `XAPI_Fee` | EUR/mese | 5000 | Fee X/Twitter API |
| `XAPI_MRR_Threshold` | EUR MRR | 15000 | Soglia attivazione XAPI |

---

## 4. Modello di Crescita Follower

### 4.1 Crescita Logistica (S-Curve)

Il modello usa una **crescita logistica** invece di esponenziale pura, per simulare la saturazione di mercato.

**Formula Base (Equazione Logistica):**
```
dF/dt = F × r × (1 - F/K)
```

Dove:
- `F` = Follower attuali
- `r` = Tasso di crescita base (`Follower_Monthly_Growth`)
- `K` = Capacità massima di mercato (`Market_Max_Followers_Local`)

**Implementazione Discreta (Mensile):**
```python
saturation_factor = max(0, 1 - Followers_Start / Market_Max_Followers)
organic_growth = Followers_Start × r_effective × saturation_factor
```

### 4.2 Adoption Ramp (Brand Nuovo)

Un brand nuovo non può crescere al massimo potenziale da subito. L'`adoption_factor` modula la crescita:

```python
adoption_factor = min(month_index / Follower_Adoption_Ramp_Months, 1.0)
r_effective = Follower_Monthly_Growth × adoption_factor
```

**Esempio con ramp di 24 mesi:**
- Mese 1: adoption_factor = 1/24 = 4.2% → crescita molto ridotta
- Mese 12: adoption_factor = 12/24 = 50% → crescita al 50%
- Mese 24+: adoption_factor = 1.0 → crescita al 100% potenziale

### 4.3 Formula Completa Follower End

```python
Followers_End = Followers_Start + organic_growth + paid_new_followers
Followers_End = min(Followers_End, Market_Max_Followers)  # Cap
```

---

## 5. Funnel di Acquisizione Clienti

### 5.1 Schema Funnel

```
┌─────────────────┐
│   IMPRESSIONS   │  Social_Views = Impr_Followers + Impr_NonFollowers
└────────┬────────┘
         │ ÷ Frequency
         ▼
┌─────────────────┐
│     REACH       │  NewUnique_NonFollowers = Impr_NonFollowers / Frequency
└────────┬────────┘
         │ × CTR
         ▼
┌─────────────────┐
│    VISITORS     │  Visitors_Total = Org + Inf + Other + PaidAds
└────────┬────────┘
         │ × ConvVS
         ▼
┌─────────────────┐
│    SIGNUPS      │  Signups = Visitors_Total × ConvVS
└────────┬────────┘
         │ × ConvSP
         ▼
┌─────────────────┐
│  NEW PAYERS     │  New_Paying = Signups × ConvSP + Referral_New_Payers
└────────┬────────┘
         │ - Churn
         ▼
┌─────────────────┐
│  PAYING USERS   │  Paying_End = Paying_Start - Churned + New_Paying
└─────────────────┘
```

### 5.2 Calcolo Impressions

```python
avg_followers = (Followers_Start + Followers_End) / 2
Impr_Followers = avg_followers × Posts × Reach_per_Post × Frequency
Impr_NonFollowers = Impr_Followers × NonFollower_Reach_Multiplier
Social_Views = Impr_Followers + Impr_NonFollowers
```

### 5.3 Calcolo Visitors per Canale

```python
# Organic (da social)
NewUnique = Impr_NonFollowers / Frequency
Org_Visitors = NewUnique × Organic_CTR_to_Site

# Influencer
Inf_Visitors_per_Collab = Inf_Avg_Followers × Inf_Reach_Rate × Inf_Click_Rate
Inf_Visitors = Inf_Collabs × Inf_Visitors_per_Collab

# Other channels
Other_Visitors = Other_Marketing_Budget / 2.0  # Assumed $2 CPC

# Paid Ads (vedi sezione 7)
PaidAds_Visitors = Paid_FollowerAds_Visitors + Paid_ClickAds_Visitors

# Totale
Visitors_Total = Org_Visitors + Inf_Visitors + Other_Visitors + PaidAds_Visitors
```

### 5.4 Conversione e Acquisizione

```python
# Signups totali
Signups = Visitors_Total × ConvVS

# Signups per canale (proporzionali al traffico)
Org_Signups = Signups × (Org_Visitors / Visitors_Total)
Inf_Signups = Signups × (Inf_Visitors / Visitors_Total)
Other_Signups = Signups × (Other_Visitors / Visitors_Total)

# New Payers per canale
Org_New_Payers = Org_Signups × ConvSP
Inf_New_Payers = Inf_Signups × ConvSP
Other_New_Payers = Other_Signups × ConvSP

# Referral (NUOVA LOGICA v7.3)
# Ogni nuovo utente registrato ha probabilità Referral_Monthly_Rate di invitare un amico
# La saturazione di mercato frena i referral quando ci si avvicina al tetto

# Base: nuovi registrati del mese (non più l'intera base utenti)
Referral_Eligible_Users = Signups

# Potenziali inviter = nuovi registrati × probabilità di invitare (2%)
Potential_Referral_Inviters = Referral_Eligible_Users × Referral_Monthly_Rate

# Fattore di saturazione: quando il mercato è quasi pieno, i referral si spengono
# referral_capacity ∈ [0, 1]: 1 = mercato vuoto, 0 = mercato pieno
referral_capacity = max(0.0, 1.0 - Paying_Users_Start / Market_Max_PayingUsers)

# Nuovi paying da referral
Referral_New_Payers = Potential_Referral_Inviters × referral_capacity

# Totale new payers
New_Paying_Users = Org_New_Payers + Inf_New_Payers + Other_New_Payers + Referral_New_Payers
```

### 5.5 Dinamica Utenti Paganti

```python
Churned_Users = Paying_Users_Start × Churn_Rate
Paying_Users_End = Paying_Users_Start - Churned_Users + New_Paying_Users
Paying_Users_End = min(Paying_Users_End, Market_Max_PayingUsers)  # Cap
```

---

## 6. Canali di Marketing

### 6.1 Organic Social
- **Input**: `Posts_per_Month`, `Org_Cost_per_Post`
- **Output**: `Org_Visitors`, `Org_Signups`, `Org_New_Payers`
- **Costo**: `Org_Marketing_Spend = Posts × Org_Cost_per_Post`

### 6.2 Influencer Marketing
- **Input**: `Inf_Collabs`, `Inf_Avg_Followers`, `Inf_Reach_Rate`, `Inf_Click_Rate`
- **Output**: `Inf_Visitors`, `Inf_Signups`, `Inf_New_Payers`
- **Costo**: `Inf_Marketing_Spend = Inf_New_Payers × Influencer_Reward_per_Sub`

### 6.3 Referral Program (NUOVA LOGICA v7.3)
- **Input**: `Referral_Monthly_Rate`, `Referral_Reward_per_Sub`, `Market_Max_PayingUsers`
- **Base calcolo**: `Signups` (nuovi registrati del mese, NON l'intera base utenti)
- **Logica**: 
  - Ogni nuovo registrato ha probabilità `Referral_Monthly_Rate` (2%) di invitare un amico
  - Probabilità applicata **una sola volta** per utente (alla coorte del mese di registrazione)
  - Saturazione: `referral_capacity = max(0, 1 - Paying_Users / Market_Max_PayingUsers)`
- **Output**: `Referral_New_Payers = Signups × Referral_Monthly_Rate × referral_capacity`
- **Costo**: `Referral_Marketing_Spend = Referral_New_Payers × Referral_Reward_per_Sub`

### 6.4 Other Channels (SEO, PR, Communities)
- **Input**: `Other_Marketing_Budget`
- **Output**: `Other_Visitors = Budget / 2.0` (assumed CPC $2)
- **Costo**: `Other_Marketing_Spend = Other_Marketing_Budget`

### 6.5 Paid Social Ads
Vedi sezione 7 per dettagli completi.

---

## 7. Paid Social Ads - Sistema Bifase

### 7.1 Panoramica

Il sistema Paid Ads ha due fasi:
- **Fase 1 (Follower Acquisition)**: quando hai pochi follower, spendi per acquisirne di nuovi
- **Fase 2 (Click Acquisition)**: quando hai molti follower, spendi per generare click/visitors

### 7.2 Logica di Switch

```python
if Follower_Threshold_For_Click_Ads < 0:
    # Valore speciale: rimani SEMPRE in Fase 1
    fase = 1
elif Followers_Start < Follower_Threshold_For_Click_Ads:
    fase = 1  # Sotto soglia: acquisisci follower
else:
    fase = 2  # Sopra soglia: genera click
```

### 7.3 Fase 1: Follower Ads (CPM-based)

```python
FollowerAds_Spend = PaidAds_Monthly_Budget

# Calcola impressions
Paid_FollowerAds_Impressions = (FollowerAds_Spend / FollowerAds_CPM_EUR) × 1000

# Calcola reach unica
Paid_FollowerAds_Reach = Paid_FollowerAds_Impressions / Frequency

# Nuovi follower acquisiti
Paid_FollowerAds_NewFollowers = Paid_FollowerAds_Reach × FollowerAds_Reach_to_Follower_Rate

# Visitors generati (CTR verso sito)
Paid_FollowerAds_Visitors = Paid_FollowerAds_Reach × FollowerAds_CTR_to_Site
```

### 7.4 Fase 2: Click Ads (CPC-based)

```python
ClickAds_Spend = PaidAds_Monthly_Budget

# Visitors diretti (1 click ≈ 1 visitor)
Paid_ClickAds_Visitors = ClickAds_Spend / ClickAds_CPC_EUR
```

### 7.5 Budget Cap e Stop Conditions

Le campagne si fermano automaticamente quando:

1. **Budget Totale Esaurito:**
```python
if PaidAds_Max_Total_Budget > 0:
    budget_remaining = PaidAds_Max_Total_Budget - Cumulative_PaidAds_Spend
    budget_this_month = min(PaidAds_Monthly_Budget, max(0, budget_remaining))
```

2. **Mercato Saturo (95%+ saturazione):**
```python
saturation_factor = 1 - Followers_Start / Market_Max_Followers
if saturation_factor < 0.05:
    # Stop tutte le campagne - mercato saturo
    FollowerAds_Spend = 0
    ClickAds_Spend = 0
```

---

## 8. Modello di Revenue

### 8.1 Monthly Recurring Revenue (MRR)

```python
MRR = Paying_Users_End × ARPU
```

### 8.2 Annual Recurring Revenue (ARR)

```python
ARR = End_MRR × 12
```

---

## 9. Struttura dei Costi

### 9.1 Marketing Costs

```python
Org_Marketing_Spend = Posts × Org_Cost_per_Post
Inf_Marketing_Spend = Inf_New_Payers × Influencer_Reward_per_Sub
Other_Marketing_Spend = Other_Marketing_Budget
Referral_Marketing_Spend = Referral_New_Payers × Referral_Reward_per_Sub
PaidAds_Marketing_Spend = FollowerAds_Spend + ClickAds_Spend

Total_Marketing_Spend = Org + Inf + Other + Referral + PaidAds
```

### 9.2 Direct Costs (Variabili)

Costi che si attivano quando MRR supera certe soglie:

```python
DataSub_Cost = DataSub_Fee if MRR >= DataSub_MRR_Threshold else 0
XAPI_Cost = XAPI_Fee if MRR >= XAPI_MRR_Threshold else 0

Direct_Costs = DataSub_Cost + XAPI_Cost
```

### 9.3 Fixed Costs

```python
Base_Fixed_Cost = BaseFixedCost  # Sempre presente
```

### 9.4 Total Costs

```python
Total_Costs = Total_Marketing_Spend + Direct_Costs + Base_Fixed_Cost
```

---

## 10. Unit Economics

### 10.1 Gross Margin (Dinamico)

Il Gross Margin è **calcolato dinamicamente** (non è un parametro di input):

```python
# Mensile
Gross_Profit = MRR - Direct_Costs
Gross_Margin_Month = Gross_Profit / MRR  (se MRR > 0, altrimenti 0)

# Annuale
Revenue_Year = SUM(MRR per tutti i mesi dell'anno)
Gross_Profit_Year = SUM(Gross_Profit per tutti i mesi dell'anno)
Gross_Margin_Year = Gross_Profit_Year / Revenue_Year
```

### 10.2 Customer Acquisition Cost (CAC)

```python
# Annuale
Total_New_Customers = SUM(New_Paying_Users per l'anno)
Total_Marketing_Spend_Year = SUM(Total_Marketing_Spend per l'anno)
Average_CAC = Total_Marketing_Spend_Year / Total_New_Customers
```

### 10.3 Lifetime Value (LTV)

```python
LTV = ARPU × Gross_Margin_Year / Monthly_Churn
```

**Nota**: usa il Gross Margin **calcolato** (non un parametro fisso).

### 10.4 LTV/CAC Ratio

```python
LTV_CAC_Ratio = LTV / Average_CAC
```

**Benchmark:**
- < 1.0: Insostenibile (perdi soldi su ogni cliente)
- 1.0 - 3.0: Rischio, margini bassi
- 3.0 - 5.0: Sano
- > 5.0: Ottimo, puoi investire di più in crescita

### 10.5 Cash Flow

```python
Net_Cash_Flow = MRR - Total_Costs
Cumulative_Cash = Previous_Cumulative_Cash + Net_Cash_Flow
```

---

## 11. Output Mensili

Il Monthly Model genera una riga per ogni mese con le seguenti colonne:

### 11.1 Identificatori
| Colonna | Descrizione |
|---------|-------------|
| `Year` | Anno (1, 2, 3, ...) |
| `Month` | Mese (1-12) |

### 11.2 Follower Metrics
| Colonna | Formula |
|---------|---------|
| `Followers_Start` | Followers_End del mese precedente |
| `Followers_End` | Start + organic_growth + paid_new_followers |
| `Posts` | Posts_per_Month |
| `Impr_Followers` | avg_followers × Posts × Reach × Frequency |
| `Impr_NonFollowers` | Impr_Followers × NonFollower_Multiplier |
| `Social_Views` | Impr_Followers + Impr_NonFollowers |
| `NewUnique_NonFollowers` | Impr_NonFollowers / Frequency |

### 11.3 Visitor Metrics
| Colonna | Formula |
|---------|---------|
| `Org_Visitors` | NewUnique × Organic_CTR |
| `Inf_Visitors` | Inf_Collabs × Inf_VPC |
| `Other_Visitors` | Other_Budget / 2 |
| `PaidAds_Visitors` | FollowerAds_Visitors + ClickAds_Visitors |
| `Visitors_Total` | Somma tutti i canali |

### 11.4 Paid Ads Metrics
| Colonna | Formula |
|---------|---------|
| `FollowerAds_Spend` | Budget Fase 1 |
| `ClickAds_Spend` | Budget Fase 2 |
| `Cumulative_PaidAds_Spend` | Spesa totale cumulativa |
| `Paid_FollowerAds_Impressions` | (Spend / CPM) × 1000 |
| `Paid_FollowerAds_Reach` | Impressions / Frequency |
| `Paid_FollowerAds_NewFollowers` | Reach × Conversion_Rate |
| `Paid_FollowerAds_Visitors` | Reach × CTR |
| `Paid_ClickAds_Visitors` | Spend / CPC |

### 11.5 Conversion Metrics
| Colonna | Formula |
|---------|---------|
| `Signups` | Visitors_Total × ConvVS |
| `Org_Signups` | Signups × (Org_Visitors / Total) |
| `Inf_Signups` | Signups × (Inf_Visitors / Total) |
| `Other_Signups` | Signups × (Other_Visitors / Total) |

### 11.6 User Metrics
| Colonna | Formula |
|---------|---------|
| `Referral_New_Payers` | Paying_Start × Referral_Rate |
| `Org_New_Payers` | Org_Signups × ConvSP |
| `Inf_New_Payers` | Inf_Signups × ConvSP |
| `Other_New_Payers` | Other_Signups × ConvSP |
| `New_Paying_Users` | Somma tutti i canali |
| `Churn_Rate` | ChurnY1/Y2/Y3 |
| `Paying_Users_Start` | End del mese precedente |
| `Churned_Users` | Start × Churn_Rate |
| `Paying_Users_End` | Start - Churned + New |

### 11.7 Revenue & Costs
| Colonna | Formula |
|---------|---------|
| `ARPU` | Parametro |
| `MRR` | Paying_Users_End × ARPU |
| `Org_Marketing_Spend` | Posts × Cost_per_Post |
| `Inf_Marketing_Spend` | Inf_New_Payers × Reward |
| `Other_Marketing_Spend` | Other_Budget |
| `Referral_Marketing_Spend` | Referral_New × Reward |
| `PaidAds_Marketing_Spend` | FollowerAds + ClickAds |
| `Total_Marketing_Spend` | Somma tutti |
| `Direct_Costs` | DataSub + XAPI |
| `Gross_Profit` | MRR - Direct_Costs |
| `Gross_Margin_Month` | Gross_Profit / MRR |
| `DataSub_Cost` | Fee se MRR ≥ soglia |
| `XAPI_Cost` | Fee se MRR ≥ soglia |
| `Base_Fixed_Cost` | BaseFixedCost |
| `Total_Costs` | Marketing + Direct + Fixed |
| `Net_Cash_Flow` | MRR - Total_Costs |
| `Cumulative_Cash` | Running total |

---

## 12. Output Annuali

Il Yearly Summary aggrega i dati mensili:

| Colonna | Calcolo |
|---------|---------|
| `Year` | 1, 2, 3, ... |
| `End_Paying_Users` | Ultimo mese dell'anno |
| `End_MRR_EUR` | MRR ultimo mese |
| `ARR_EUR` | End_MRR × 12 |
| `Total_New_Customers` | SUM(New_Paying_Users) |
| `Org_New_Payers` | SUM per canale |
| `Inf_New_Payers` | SUM per canale |
| `Other_New_Payers` | SUM per canale |
| `Referral_New_Payers` | SUM per canale |
| `*_Marketing_Spend_EUR` | SUM spese per canale |
| `Total_Marketing_Spend_EUR` | SUM totale |
| `Average_CAC_EUR` | Total_Spend / Total_New |
| `Revenue_Year` | SUM(MRR) |
| `Gross_Profit_Year` | SUM(Gross_Profit) |
| `Gross_Margin_Year` | GP_Year / Revenue_Year |
| `LTV_EUR` | ARPU × GM / Churn |
| `LTV_CAC_Ratio` | LTV / CAC |
| `Cumulative_Cash_EndOfYear` | Cash a fine anno |
| `Total_*_Visitors` | SUM per canale |
| `Share_*_Visitors` | % traffico per canale |
| `Total_Social_Views` | SUM impressions |
| `End_Followers` | Follower a fine anno |

---

## 13. Grafici e Visualizzazioni

L'app include 6 grafici interattivi:

### 13.1 MRR Over Time
- **Tipo**: Line chart
- **Metrica**: Monthly Recurring Revenue
- **Utilità**: Traccia la crescita revenue

### 13.2 Paying Users & Followers
- **Tipo**: Dual-axis line chart
- **Metriche**: Paying Users (sx), Followers (dx)
- **Utilità**: Correla crescita audience con conversioni

### 13.3 Cumulative Cash Flow
- **Tipo**: Line chart con fill
- **Metrica**: Cash cumulativo
- **Colori**: Verde (positivo), Rosso (negativo)
- **Utilità**: Identifica break-even point

### 13.4 Marketing Spend Breakdown
- **Tipo**: Stacked area chart
- **Metriche**: Spesa per canale (Organic, Influencer, Paid Ads, Referral, Other)
- **Utilità**: Analizza mix marketing nel tempo

### 13.5 Conversion Funnel
- **Tipo**: Multi-line chart (scala log)
- **Metriche**: Visitors → Signups → New Paying
- **Utilità**: Visualizza efficienza funnel

### 13.6 Unit Economics
- **Tipo**: Dual-axis chart
- **Metriche**: Gross Margin % (sx), Net Cash Flow (dx)
- **Utilità**: Monitora profittabilità

---

## Appendice A: Formule Riepilogative

### Crescita Follower (S-Curve)
```
adoption_factor = min(month / ramp_months, 1.0)
r_effective = r_base × adoption_factor
saturation = max(0, 1 - F/K)
organic_growth = F × r_effective × saturation
F_end = F_start + organic_growth + paid_new_followers
```

### Funnel Conversion
```
Visitors = Org + Inf + Other + PaidAds
Signups = Visitors × ConvVS
New_Payers = Signups × ConvSP + Referral
Paying_End = Paying_Start × (1 - Churn) + New_Payers
```

### Unit Economics
```
Gross_Margin = (MRR - Direct_Costs) / MRR
CAC = Total_Marketing / New_Customers
LTV = ARPU × Gross_Margin / Churn
LTV/CAC = LTV / CAC
```

### Cash Flow
```
Net_CF = MRR - (Marketing + Direct + Fixed)
Cumulative = Previous + Net_CF
```

---

## Appendice B: Valori Default Consigliati

| Scenario | ARPU | Churn | ConvVS | ConvSP | Growth |
|----------|------|-------|--------|--------|--------|
| Conservative | €15 | 8% | 10% | 3% | 5% |
| Base Case | €20 | 6% | 13% | 3.5% | 8% |
| Optimistic | €25 | 4% | 15% | 5% | 12% |

---

*Documento generato automaticamente - v7.2*
*Ultimo aggiornamento: Dicembre 2025*
