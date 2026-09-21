import pandas as pd


class CostEngine:

    def __init__(self, technology_cost_df):

        self.df = technology_cost_df.copy()

        self.df.columns = (
            self.df.columns
            .str.strip()
        )

    def calculate_cost(
        self,
        technology,
        weight,
        material_price
    ):

        process = self.df[
            self.df["Technology_Name"] == technology
        ]

        if process.empty:
            raise ValueError(
                f"Technology not found in Technology Cost Library: {technology}"
            )

        process = process.iloc[0]

        # -------------------------
        # Material Cost
        # -------------------------

        material_cost = (
            weight * material_price
        )

        # -------------------------
        # Machine Cost
        # -------------------------

        machine_cost = (
            process["Machine_Rate_EUR_hr"]
            * process["Setup_Hours"]
        )

        # -------------------------
        # Labour Cost
        # -------------------------

        labour_cost = (
            process["Labour_Rate_EUR_hr"]
            * process["Setup_Hours"]
        )

        # -------------------------
        # Overhead
        # -------------------------

        overhead_cost = (
            machine_cost
            + labour_cost
        ) * (
            process["Overhead_Factor"] - 1
        )

        # -------------------------
        # Tooling
        # -------------------------

        tooling_cost = 0

        if (
            process["Tool_Life_Pcs"] > 0
            and process["Tooling_Cost_EUR"] > 0
        ):
            tooling_cost = (
                process["Tooling_Cost_EUR"]
                / process["Tool_Life_Pcs"]
            )

        # -------------------------
        # Total Cost
        # -------------------------

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + overhead_cost
            + tooling_cost
        )

        return {
            "Material Cost": round(material_cost, 2),
            "Machine Cost": round(machine_cost, 2),
            "Labour Cost": round(labour_cost, 2),
            "Overhead Cost": round(overhead_cost, 2),
            "Tooling Cost": round(tooling_cost, 2),
            "Total Cost": round(total_cost, 2)
        }
