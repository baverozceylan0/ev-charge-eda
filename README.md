# 🚗 EV-Charge-EDA

**Exploratory Data Analysis of EV Charging Session Data**, focused on large-scale electric vehicle charging facilities.  

🧪 This repository:
  - explores **usage patterns, user behavior, temporal trends, and engagement dynamics** using robust data preparation and statistical visualization methods.
  - serves as a foundation for EV load modeling, demand forecasting, and engagement segmentation.
  - provides replicable and consistent analysis across diverse EV charging datasets.
  - simplifies scaling to new datasets using a standardized schema and modular scripts.

---

## 🧩 Data Schema & Preparation

All analyses require a standardized **four-column** input dataframe:

| Column           | dtype              |
|------------------|--------------------|
| `EV_id_x`        | string            |
| `start_datetime` | datetime64[ns]    |
| `end_datetime`   | datetime64[ns]    |
| `total_energy`   | float64           |

The script `src/load_data.py` handles **formatting raw sources into this schema**, ensuring consistency across multiple datasets.

---

## 🔍 Included Datasets

- **ASR dataset (Netherlands):** Real EV charging sessions from the a.s.r. living lab of the SmoothEMS met GridShield project.  

  **Reference:** de Bont, Kevin; Hoogsteen, Gerwin; Hurink, Johann; Kokhuis, Richard; Kusche, Fabian et. al. (2025): Electric Vehicle Charging Session Data of Large Office Parking Lot . Version 2. 4TU.ResearchData. dataset. https://doi.org/10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13.v2

- **ACN-Data (Caltech, JPL & Office):** A well-known public workplace EV charging dataset with three different fields and over 30,000 sessions.

  **Reference:** Zachary J. Lee, Tongxin Li, and Steven H. Low. 2019. ACN-Data: Analysis and Applications of an Open EV Charging Dataset. In Proceedings of the Tenth ACM International Conference on Future Energy Systems (e-Energy '19). Association for Computing Machinery, New York, NY, USA, 139–149. https://doi.org/10.1145/3307772.3328313

---

## 📚 Key Analyses
Key features include:

- **Temporal analysis:**  
  - **Monthly trends** in arrival counts to detect stable/volatile periods.
  - **Daily session distributions** to assess operational consistency.

- **User-Level Analysis:**
  - Distribution of session counts per user.
  - Identification of one-time vs. recurring users.  
  - Pareto-like analysis of user engagement (e.g., top X% of users contributing Y% of sessions).  

- **Visualization outputs:**  
  - Clear charts for numerical and categorical features (histograms, boxplots, bar charts, heatmaps).  
  - Ready-to-use plots for inclusion in reports or further analysis.  

- **Univariate analysis:**  
  - Distributions of key numerical variables, including session duration, total energy delivered, start and end times, and average power.  
  - Distributions of categorical variables, including session counts by day of the week, and session counts by month of the year. 

- **Bivariate analysis:**  
  - Correlation heatmaps for numerical variables such as session duration, start and end times, and total energy delivered.  
  - Two-dimensional distributions (scatterplots) for key numerical relationships, e.g., start vs. end times or duration vs. total energy delivered.  
  - Box plots illustrating the distribution of session counts by day of the week and by month of the year.  

---
