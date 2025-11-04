import pandas as pd

# Load original Excel
df_orig = pd.read_excel("data/26data.xlsx")  # replace with actual filename

# Check conventional fuel MPG
mpg_columns = ['City FE (Guide) - Conventional Fuel',
               'Hwy FE (Guide) - Conventional Fuel',
               'Comb FE (Guide) - Conventional Fuel']

print(df_orig[mpg_columns].head())

# Check PHEV MPGe
phev_columns = ['City PHEV Composite MPGe',
                'Hwy PHEV Composite MPGe',
                'Comb PHEV Composite MPGe']

print(df_orig[phev_columns].head())