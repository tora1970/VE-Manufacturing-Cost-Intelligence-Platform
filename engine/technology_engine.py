import pandas as pd


class TechnologyEngine:

    def __init__(self, rules_df):
        self.rules_df = rules_df

    def recommend(
        self,
        weight,
        volume,
        material,
        region=None,
        complexity=None
    ):

        results = []

        for _, row in self.rules_df.iterrows():

            score = row["Base_Score"]

            if (
                row["Min_Weight_kg"]
                <= weight
                <= row["Max_Weight_kg"]
            ):
                score += 30

            if (
                row["Min_Volume"]
                <= volume
                <= row["Max_Volume"]
            ):
                score += 30

            if (
                str(row["Material_Group"]).lower()
                in str(material).lower()
            ):
                score += 30

            results.append(
                {
                    "Technology": row["Technology_Name"],
                    "Score": score
                }
            )

        result_df = pd.DataFrame(results)

        result_df = result_df.sort_values(
            "Score",
            ascending=False
        )

        return result_df
