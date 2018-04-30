import pandas as pd

# Written by Apollon
# This converts excel MDI files to pickled dataframes
# And saves them in current working directory

dep_df = pd.ExcelFile("./sutton-deprivation-data.xlsx")
dep_full = dep_df.parse("Sheet1")
dep_full.to_pickle('../sutton-deprivation-data.pkl')

dep_df = pd.ExcelFile("./Deprivation_Index_2016.xlsx")
dep_full = dep_df.parse("All postcodes")
dep_full.to_pickle('../edinburgh-deprivation-data.pkl')
