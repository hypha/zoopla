import pandas as pd


class Mdi(object):

    def __init__(self):
        dep_df = pd.ExcelFile("./sutton-deprivation-data.xlsx")
        dep_full = dep_df.parse("Sheet1")