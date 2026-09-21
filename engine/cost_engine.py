import pandas as pd


class CostEngine:

    def __init__(self, technology_cost_df):
        self.cost_library = technology_cost_df

    def calculate_cost(
        self,
        technology,
        weight,
        material_price,
        annual_volume,
        labour_rate=None,
        overhead_factor=None
    ):

        tech_row = self.cost_library[
            self.cost_library["Technology_Name"]
            .astype(str)
            .str.strip()
            == str(technology).strip()
        ]

        if tech_row.empty:

            tech_row = self.cost_library[
                self.cost_library["Technology_ID"]
                .astype(str)
                .str.strip()
                == str(technology).strip()
            ]

        if tech_row.empty:

            raise ValueError(
                f"Technology '{technology}' not found"
            )

        tech_row = tech_row.iloc[0]

        machine_rate = float(
            tech_row["Machine_Rate_EUR_hr"]
        )

        if labour_rate is None:
            labour_rate = float(
                tech_row["Labour_Rate_EUR_hr"]
            )

        if overhead_factor is None:
            overhead_factor = float(
                tech_row["Overhead_Factor"]
            )

        setup_hours = float(
            tech_row["Setup_Hours"]
        )

        tooling_cost = float(
            tech_row["Tooling_Cost_EUR"]
        )

        tool_life = float(
            tech_row["Tool_Life_Pcs"]
        )

        material_cost = (
            weight *
            material_price
        )

        cycle_time_lookup = {
            "CNC Machining": 2.0,
            "Die Casting": 0.2,
            "HP Multi Jet Fusion": 5.0,
            "Investment Casting": 1.0,
            "Sand Casting": 0.8,
            "Injection Moulding": 0.1,
            "CNC": 2.0,
            "HP MJF": 5.0
        }

        cycle_time_minutes = cycle_time_lookup.get(
            technology,
            1.0
        )

        cycle_time_hours = (
            cycle_time_minutes / 60
        )

        machine_cost = (
            cycle_time_hours *
            machine_rate
        )

        labour_cost = (
            cycle_time_hours *
            labour_rate
        )

        setup_cost = 0

        if annual_volume > 0:

            total_setup_cost = (
                setup_hours *
                labour_rate
            )

            setup_cost = (
                total_setup_cost /
                annual_volume
            )

        tooling_cost_per_piece = 0

        if tool_life > 0:

            tooling_cost_per_piece = (
                tooling_cost /
                tool_life
            )

        direct_cost = (
            material_cost
            + machine_cost
            + labour_cost
        )

        overhead_cost = (
            direct_cost *
            (overhead_factor - 1)
        )

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + overhead_cost
            + setup_cost
            + tooling_cost_per_piece
        )

        return {
            "Technology": technology,
            "Material Cost EUR": round(material
