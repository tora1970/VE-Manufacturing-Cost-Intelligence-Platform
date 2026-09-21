import pandas as pd


class CostEngine:

    def __init__(self, technology_cost_df):

        self.df = technology_cost_df.copy()
        self.df.columns = self.df.columns.str.strip()

    def calculate_cost(
        self,
        technology,
        weight,
        material_price,
        annual_volume,
        labour_rate,
        overhead_factor
    ):

        process = self.df[
            self.df["Technology_Name"] == technology
        ]

        if process.empty:
            raise ValueError(
                f"Technology not found: {technology}"
            )

        process = process.iloc[0]

        # ---------------------------------
        # Input data
        # ---------------------------------

        machine_rate = float(
            process["Machine_Rate_EUR_hr"]
        )

        setup_hours = float(
            process["Setup_Hours"]
        )

        tool_cost = float(
            process["Tooling_Cost_EUR"]
        )

        tool_life = float(
            process["Tool_Life_Pcs"]
        )

        project_life = float(
            process["Project_Life_Years"]
        )

        # ---------------------------------
        # Material Cost
        # ---------------------------------

        material_cost = (
            weight * material_price
        )

        # ---------------------------------
        # Setup Cost per Piece
        # ---------------------------------

        annual_volume = max(
            annual_volume,
            1
        )

        machine_setup_cost = (
            machine_rate
            * setup_hours
            / annual_volume
        )

        labour_setup_cost = (
            labour_rate
            * setup_hours
            / annual_volume
        )

        # ---------------------------------
        # Overhead
        # ---------------------------------

        # Hvis Regions.xlsx indeholder
        # 1.20 = 20 %
        # 1.50 = 50 %

        overhead_cost = (
            machine_setup_cost
            + labour_setup_cost
        ) * (
            overhead_factor - 1
        )

        # ---------------------------------
        # Tooling
        # ---------------------------------

        tooling_cost = 0

        if (
            tool_cost > 0
            and project_life > 0
            and tool_life > 0
        ):

            lifetime_volume = (
                annual_volume
                * project_life
            )

            amortization_volume = min(
                lifetime_volume,
                tool_life
            )

            tooling_cost = (
                tool_cost
                / amortization_volume
            )

        # ---------------------------------
        # Total Cost
        # ---------------------------------

        total_cost = (
            material_cost
            + machine_setup_cost
            + labour_setup_cost
            + overhead_cost
            + tooling_cost
        )

        return {
            "Material Cost": round(material_cost, 2),
            "Machine Cost": round(machine_setup_cost, 2),
            "Labour Cost": round(labour_setup_cost, 2),
            "Overhead Cost": round(overhead_cost, 2),
            "Tooling Cost": round(tooling_cost, 2),
            "Total Cost": round(total_cost, 2)
        }
