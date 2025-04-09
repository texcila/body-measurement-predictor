# 🧪 Data Augmentation – Body Measurement Predictor

This document explains how we augmented our original dataset (~215 records) to 1,000 rows using controlled statistical variation. This ensures our model can generalize across diverse body shapes without overfitting.

---

## 🎯 Why Augmentation?

- Improve prediction accuracy on varied inputs
- Simulate real-world body diversity
- Boost training data for machine learning

---

## 🛠️ Method Used: Noise-Based Augmentation

| Parameter         | Value                        |
|------------------|------------------------------|
| Type             | Noise-based                  |
| Noise Applied    | ±2 cm or ±5% (random)        |
| Samples Added    | ~785                         |
| Source File      | model_ready_measurements.xlsx |
| Output File      | augmented_measurements_v1.xlsx |

- Each real row was randomly selected and copied
- Measurements were varied slightly using:
  - `np.random.uniform(-2, 2)` → absolute noise (in cm)
  - `np.random.uniform(-0.05, 0.05)` → percent-based noise
- Relationships like `Hip > Waist` were preserved through mild variation

---

## 🔁 Reproducibility

- Random seed set: `np.random.seed(42)`
- Columns excluded:
  - `ID`: unique identifiers
  - `Date Measured`: timestamp metadata
  - `Notes`: free text

```python
excluded_columns = ['ID', 'Date Measured (YYYY-MM-DD)', 'Notes']
