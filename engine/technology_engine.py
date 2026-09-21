import pandas as pd


class TechnologyEngine:

    def __init__(self, rules_df):
        self.rules_df = rules_df.copy()

        # Fjern evt. skjulte mellemrum
        self.rules_df.columns = (
            self.rules_df.columns.str.strip()
        )

    def recommend(
        self,
        weight,
        volume,
        material,
        region=None,
        complexity="Medium"
    ):

        recommendations = []

        for _, row in self.rules_df.iterrows():

            score = 0

            weight_score = 0
            volume_score = 0
            material_score = 0
            complexity_score = 0

            # --------------------------
            # Weight Evaluation
            # --------------------------

            if (
                row["Min_Weight_kg"]
                <= weight
                <= row["Max_Weight_kg"]
            ):
                weight_score = 30

            # --------------------------
            # Volume Evaluation
            # --------------------------

            if (
                row["Min_Volume"]
                <= volume
                <= row["Max_Volume"]
            ):
                volume_score = 30

            # --------------------------
            # Material Evaluation
            # --------------------------

            material_group = str(
                row["Material_Group"]
            ).lower()

            if material_group in material.lower():
                material_score = 30

            # --------------------------
            # Complexity Evaluation
            # --------------------------

            supported = str(
                row["Complexity_Supported"]
            ).strip().lower()

            if supported == "all":
                complexity_score = 20

            elif supported == complexity.lower():
                complexity_score = 20

            # --------------------------
            # Base Score
            # --------------------------

            score = (
                row["Base_Score"]
                + weight_score
                + volume_score
                + material_score
                + complexity_score
            )

            recommendations.append(
                {
                    "Technology":
                        row["Technology_Name"],

                    "Score":
                        score,

                    "Weight Score":
                        weight_score,

                    "Volume Score":
                        volume_score,

                    "Material Score":
                        material_score,

                    "Complexity Score":
                        complexity_score
                }
            )

        result_df = pd.DataFrame(
            recommendations
        )

        result_df = (
            result_df
            .sort_values(
                by="Score",
                ascending=False
            )
            .reset_index(drop=True)
        )

        result_df.index = result_df.index + 1

        return result_df
