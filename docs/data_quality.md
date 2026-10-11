# Data quality notes

Fill this in while you run sql/01_quality_checks.sql. One line per check.

| Check | Result | Is it a problem? | What I did |
|---|---|---|---|
| Rows = distinct users | 90,189 = 90,189 | No | No duplicates; unique index on userid working |
| Missing values | All columns = 0 nulls | No | No missing data; no imputation needed |
| Group labels | gate_30 (44,700) and gate_40 (45,489) | No | Both labels present; sizes ~50/50 (SRM test in Part 5) |
| Min and max game rounds | Min = 0, Max = 49,854 | Max is extreme outlier | Use medians/trimmed methods for game rounds per analysis plan |
| Players with zero rounds | gate_30: 1,937 (4.33%); gate_40: 2,057 (4.52%) | No | Kept them — removing would bias the sample |
| Retained day 7 but not day 1 | gate_30: 1,826; gate_40: 1,773 | No | Logically possible; day flags measure specific days |
| Retained with zero rounds | gate_30: 56; gate_40: 55 | No (unusual but explainable) | Kept them; app opened without playing|
