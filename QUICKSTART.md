# 🚀 QUICK START GUIDE
## AI Finance Platform - Interactive Financial Model App

---

## ✅ Installation (3 steps)

### 1. Install Python packages
```bash
pip install pandas openpyxl matplotlib pyqt6
```

### 2. Verify files in directory
- `financial_model_app.py` ✓
- `ai_finance_dynamic_model_v6_social_views.xlsx` ✓

### 3. Run the app
```bash
python financial_model_app.py
```

---

## 📊 First Time Use

The app will:
1. Load data from Excel (one-time operation)
2. Calculate all formulas
3. Save to `model_state.json` for fast future loading
4. Display 4 tabs:
   - **Assumptions** - Edit parameters
   - **Monthly Model** - 36 months of projections
   - **Yearly Summary** - Annual KPIs
   - **Charts** - Visual analytics

---

## 🎯 Common Tasks

### Task 1: Change ARPU (pricing)
1. Go to **Assumptions** tab
2. Find row with Parameter "ARPU"
3. Change Value from `30` to `40`
4. Click **🔄 Recalculate & Update Charts**
5. Check **Yearly Summary** → Year 3 ARR increases!

### Task 2: Test aggressive social media growth
1. Go to **Monthly Model** tab
2. Change `Social_Views` for Month 12 from `206,667` to `300,000`
3. Change subsequent months proportionally
4. Click **🔄 Recalculate & Update Charts**
5. See impact on MRR in **Charts** tab

### Task 3: Reduce churn (improve retention)
1. Go to **Assumptions** tab
2. Find `ChurnY3` (currently 0.05 = 5%)
3. Change to `0.04` (4% churn)
4. Click **🔄 Recalculate & Update Charts**
5. Check **Yearly Summary** → LTV increases!

### Task 4: Save your scenario
1. After making changes, click **💾 Save JSON**
2. Or use **📤 Export JSON As...** to save with custom name
3. Your changes are now persistent

### Task 5: Start fresh
1. Click **📥 Reload from Excel**
2. Confirm the prompt
3. All changes discarded, back to original Excel data

---

## 🎨 GUI Overview

```
┌─────────────────────────────────────────┐
│  [Assumptions] [Monthly] [Yearly] [Charts]
├─────────────────────────────────────────┤
│                                          │
│  Editable tables show all model data    │
│                                          │
│  - Green cells = Editable               │
│  - Gray cells = Auto-calculated         │
│                                          │
└─────────────────────────────────────────┘
│  [🔄 Recalc] [💾 Save] [📤 Export] [📥 Reload]
└─────────────────────────────────────────┘
```

---

## 🔧 What You Can Edit

### Assumptions Tab (Value column only)
- **ARPU** - Monthly price per user
- **ConvVS** - Visitor to signup conversion
- **ConvSP** - Signup to paid conversion
- **ChurnY1/Y2/Y3** - Monthly churn rates
- **CAC_Org/Inf/Ref/Other** - Cost per customer by channel
- **Inf_Collabs_Y1/Y2/Y3** - Influencer collaborations per month
- **All other parameters**

### Monthly Model Tab (Social_Views only)
- **Social_Views** - Number of social media impressions per month
- All other columns auto-calculate

### Yearly Summary Tab (Read-only)
- Everything auto-calculated from monthly data

---

## 📈 Key Metrics to Watch

After recalculation, check these in **Yearly Summary**:

| Metric | Year 3 Target | Current |
|--------|---------------|---------|
| ARR | > €1M | €1,023,229 ✅ |
| LTV/CAC Ratio | > 3.0x | 12.47x ✅ |
| End Paying Users | > 2,000 | 2,842 ✅ |
| Cumulative Cash | Positive | €612,650 ✅ |

---

## 🎯 Business Scenarios to Test

### Scenario A: Premium Pricing Strategy
- ARPU: 30 → **50**
- Expected: Higher MRR, better unit economics

### Scenario B: Aggressive Influencer Marketing
- Inf_Collabs_Y3: 6 → **12**
- Expected: More visitors, more customers, higher CAC

### Scenario C: Improved Product (Lower Churn)
- ChurnY3: 0.05 → **0.03**
- Expected: Much higher LTV, better retention

### Scenario D: Viral Social Growth
- Month 12 Social_Views: 206,667 → **500,000**
- Scale remaining months proportionally
- Expected: Exponential growth curve

---

## ⚠️ Important Notes

1. **Always click "🔄 Recalculate"** after edits
2. **Auto-save** happens after recalculation
3. **Social_Views** is the only editable monthly column (drives everything else)
4. **Derived parameters** (CAC_Y1/Y2/Y3, etc.) auto-update from base parameters
5. **Charts update** automatically after recalculation

---

## 🐛 Troubleshooting

**Problem:** Charts don't show
- **Solution:** Go to Charts tab AFTER clicking Recalculate

**Problem:** My edits don't take effect
- **Solution:** Click 🔄 Recalculate button after editing

**Problem:** App won't start
- **Solution:** Check Python packages: `pip list | grep -E "pandas|pyqt|matplotlib"`

**Problem:** Values look wrong
- **Solution:** Click 📥 Reload from Excel to reset

---

## 💾 Files Created

- **`model_state.json`** - Your current model (auto-saved)
- **`financial_model_app.py`** - The application code
- **`ai_finance_dynamic_model_v6_social_views.xlsx`** - Source data

---

## 🎓 For Power Users

### Export Multiple Scenarios
1. Make changes for Scenario A
2. **📤 Export JSON As...** → `scenario_a_premium.json`
3. **📥 Reload from Excel**
4. Make changes for Scenario B
5. **📤 Export JSON As...** → `scenario_b_influencer.json`

### Compare Results
Open exported JSON files in a text editor to see exact values.

### Batch Testing
Edit the Python code to add custom buttons for pre-defined scenarios.

---

## ✨ Pro Tips

1. **Test extremes:** Try ARPU = €100 to see "best case"
2. **Test downside:** Try ChurnY1 = 0.10 to see "worst case"
3. **Social growth is key:** Small changes in Social_Views compound heavily
4. **LTV/CAC is crucial:** Keep it above 3x, ideally 5x+
5. **Break-even month:** Check Cumulative Cash chart for when it crosses 0

---

## 📞 Support

For issues or questions about the model logic:
- Check the `APP_README.md` for technical details
- Review `ANALYSIS_SUMMARY.md` for business context

---

**Happy modeling! 🚀**

Last updated: November 26, 2025
