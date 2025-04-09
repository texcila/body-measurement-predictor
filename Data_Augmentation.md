
# 🧪 Data Augmentation – Body Measurement Predictor

## 🎯 Objective
Expand the original dataset of **200 real body measurements** to **1,000 samples** using **domain-guided augmentation** to:
- Reduce overfitting in machine learning models.
- Simulate natural measurement variability (±2 cm).
- Maintain anthropometric realism (e.g., `hip > waist`).

---

## 🛠️ Method

### 📈 Noise-Based Augmentation
1. **Duplication**: Create 4 copies of each original row (200 → 800).  
2. **Controlled Noise**:  
   - Add ±2 cm to all measurements (e.g., `bust_cm`, `waist_cm`).  
   - **Why ±2 cm?**: Mirrors real-world tailoring measurement tolerances.  
3. **Reproducibility**:  
   ```python
   np.random.seed(42)  # Ensures identical "random" results every time
   ```

### 🧮 Domain Rules
| Rule | Formula | Purpose |  
|------|---------|---------|  
| Hip Limitation | `Hip ≤ 0.65 × Height` | Prevents unrealistic hip proportions |  
| Waist Floor | `Waist ≥ 0.7 × Hip` | Avoids anatomically impossible waist sizes |  

---

## 🗂️ Files & Folders
```text
body-measurement-predictor/  
├── data/  
│   ├── model_ready_measurements.xlsx    # Original cleaned data (200 rows)  
│   └── augmented_measurements_v1.xlsx   # Augmented dataset (1,000 rows)  
├── notebooks/  
│   └── body_measurement_augmentation.ipynb  # Full augmentation code  
└── DATA_AUGMENTATION.md                # This document  
```

---

## ✅ Validation Protocol

### 1. Automated Checks (Code)
```python
# Check rules are followed
assert (augmented_data["hip_cm"] <= augmented_data["height_cm"] * 0.65).all()
assert (augmented_data["waist_cm"] >= augmented_data["hip_cm"] * 0.7).all()

# Verify dataset size
assert len(augmented_data) == 1000, "Incorrect row count!"
```

### 2. Manual Checks (Excel)
1. Open `data/augmented_measurements_v1.xlsx`.  
2. Spot-check random rows for:  
   - `Hip ≤ Height × 0.65`  
   - `Waist ≥ Hip × 0.7`  

---

## 🔄 Reproducibility
1. **Environment**:  
   ```bash
   pip install -r requirements.txt  # Contains pandas==2.0.3, numpy==1.24.3
   ```
2. **Version Control**:  
   ```bash
   git add data/augmented_measurements_v1.xlsx
   git commit -m "DATA: Augmented dataset v1 (noise + rules)"
   ```

---

## 🚀 Next Steps
1. **Model Training**:  
   - Use `augmented_measurements_v1.xlsx` to train XGBoost models.  
   - Target: Mean Absolute Error (MAE) < 2 cm.  
2. **Documentation**:  
   - Add a `MODEL_TRAINING.md` with hyperparameters and accuracy metrics.  

---

*Last updated: [April 09, 2025]]*  
```

