import pandas as pd


class CostEngine:

    def __init__(self, process_cost_df):

        self.process_cost_df = process_cost_df.copy()

        self.process_cost_df.columns = (
            self.process_cost_df.columns
            .str.strip()
        )

    def calculate_cost(
        self,
        technology,
        weight,
        material_price
    ):

        process = self.process_cost_df[
            self.process_cost_df["Technology"] == technology
        ].iloc[0]

        material_cost = (
            weight * material_price
        )

        machine_cost = (
            process["Machine_Rate_EUR_hr"]
            * process["Cycle_Time_min"]
            / 60
        )

        labour_cost = (
            process["Labour_Rate_EUR_hr"]
            * process["Cycle_Time_min"]
            / 60
        )

        overhead_cost = (
            machine_cost + labour_cost
        ) * (
            process["Overhead_Factor"] - 1
        )

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + overhead_cost
        )

        return {
            "Material Cost": round(material_cost, 2),
            "Machine Cost": round(machine_cost, 2),
            "Labour Cost": round(labour_cost, 2),
            "Overhead Cost": round(overhead_cost, 2),
            "Total Cost": round(total_cost, 2)
        }
