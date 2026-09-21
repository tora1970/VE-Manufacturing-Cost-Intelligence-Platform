import pandas as pd


class CostEngine:

    def __init__(self, technology_cost_df):
        self.cost_library = technology_cost_df

    def calculate_cost(
        self,
        technology,
        weight_kg,
        material_price_eur_kg,
        annual_volume
    ):

        # --------------------------------------------------
        # Find technology in cost library
        # --------------------------------------------------

        tech_row = self.cost_library[
            self.cost_library["Technology_ID"] == technology
        ]

        if tech_row.empty:
            tech_row = self.cost_library[
                self.cost_library["Technology_Name"] == technology
            ]

        if tech_row.empty:
            raise ValueError(
                f"Technology not found in Technology Cost Library: {technology}"
            )

        tech_row = tech_row.iloc[0]

        # --------------------------------------------------
        # Input data
        # --------------------------------------------------

        machine_rate = float(tech_row["Machine_Rate_EUR_hr"])
        labour_rate = float(tech_row["Labour_Rate_EUR_hr"])
        overhead_factor = float(tech_row["Overhead_Factor"])

        setup_hours = float(tech_row["Setup_Hours"])
        tooling_cost = float(tech_row["Tooling_Cost_EUR"])
        tool_life = float(tech_row["Tool_Life_Pcs"])

        # --------------------------------------------------
        # Material Cost
        # --------------------------------------------------

        material_cost = weight_kg * material_price_eur_kg

        # --------------------------------------------------
        # Simplified cycle time model
        # --------------------------------------------------

        cycle_time_lookup = {
            "CNC Machining": 2.0,
            "Die Casting": 0.2,
            "HP Multi Jet Fusion": 5.0,
            "Investment Casting": 1.0,
            "Sand Casting": 0.8,
            "Injection Moulding": 0.1
        }

        cycle_time_minutes = cycle_time_lookup.get(
            technology,
            1.0
        )

        cycle_time_hours = cycle_time_minutes / 60

        # --------------------------------------------------
        # Machine Cost
        # --------------------------------------------------

        machine_cost = cycle_time_hours
