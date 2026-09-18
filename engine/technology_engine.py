import pandas as pd


class TechnologyEngine:

    def __init__(self, rules_df):
        self.rules = rules_df

    def recommend(self, volume):

        technology = "Unknown"

        for _, rule in self.rules.iterrows():

            if rule["Operator"] == "<":

                if volume < rule["Value"]:
                    technology = rule["Recommended Technology"]

            elif rule["Operator"] == ">=":

                if volume >= rule["Value"]:
                    technology = rule["Recommended Technology"]

        return technology
