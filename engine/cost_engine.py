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
        # Inputs
        # ---------------------------------

        machine_rate = float(
            process["Machine_Rate_EUR_hr"]
        )

        setup_hours = float(
            process["Setup_Hours"]
        )

        cycle_time_sec = float(
            process["Cycle_Time_sec"]
        )

        scrap_rate = float(
            process["Scrap_Rate"]
        )

        tooling_cost_eur = float(
            process["Tooling_Cost_EUR"]
        )

        tool_life_pcs = float(
            process["Tool_Life_Pcs"]
        )

        project_life_years = float(
            process["Project_Life_Years"]
        )

        annual_volume = max(
            annual_volume,
            1
        )

        # ---------------------------------
        # Material Cost
        # ---------------------------------

        material_cost = (
            weight
            * material_price
            * (1 + scrap_rate)
        )

        # ---------------------------------
        # Setup Cost
        # ---------------------------------

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
        # Cycle Cost
        # ---------------------------------

        machine_cycle_cost = (
            machine_rate
            * cycle_time_sec
            / 3600
        )

        labour_cycle_cost = (
            labour_rate
            * cycle_time_sec
            / 3600
        )

        # ---------------------------------
        # Tooling Cost
        # ---------------------------------

        tooling_cost = 0

        if (
            tooling_cost_eur > 0
            and tool_life_pcs > 0
            and project_life_years > 0
        ):

            lifetime_volume = (
                annual_volume
                * project_life_years
            )

            amortization_volume = min(
                lifetime_volume,
                tool_life_pcs
            )

            tooling_cost = (
                tooling_cost_eur
                / amortization_volume
            )

        # ---------------------------------
        # Overhead
        # ---------------------------------

        direct_cost = (
            machine_setup_cost
            + labour_setup_cost
            + machine_cycle_cost
            + labour_cycle_cost
        )

        overhead_cost = (
            direct_cost
            * (overhead_factor - 1)
        )

        # ---------------------------------
        # Totals
        # ---------------------------------

        machine_cost = (
            machine_setup_cost
            + machine_cycle_cost
        )

        labour_cost = (
            labour_setup_cost
            + labour_cycle_cost
        )

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + overhead_cost
            + tooling_cost
        )

        return {
            "Material Cost": round(material_cost, 2),

            "Setup Cost": round(
                machine_setup_cost + labour_setup_cost,
                2
            ),

            "Cycle Cost": round(
                machine_cycle_cost + labour_cycle_cost,
                2
            ),

            "Machine Cost": round(machine_cost, 2),

            "Labour Cost": round(labour_cost, 2),

            "Overhead Cost": round(overhead_cost, 2),

            "Tooling Cost": round(tooling_cost, 2),

            "Total Cost": round(total_cost, 2)
        }
