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

        # ------------------------------------------
        # Find Technology
        # ------------------------------------------

        tech_row = self.cost_library[
            self.cost_library["Technology_ID"].astype(str).str.strip()
            == str(technology).strip()
        ]

        if tech_row.empty:

            tech_row = self.cost_library[
                self.cost_library["Technology_Name"].astype(str).str.strip()
                == str(technology).strip()
            ]

        if tech_row.empty:

            available = self.cost_library[
                "Technology_ID"
            ].tolist()

            raise ValueError(
                f"Technology '{technology}' not found. "
                f"Available technologies: {available}"
            )

        tech_row = tech_row.iloc[0]

        # ------------------------------------------
        # Read Cost Data
        # ------------------------------------------

        machine_rate = float(
            tech_row["Machine_Rate_EUR_hr"]
        )

        labour_rate = float(
            tech_row["Labour_Rate_EUR_hr"]
        )

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

        # ------------------------------------------
        # Material Cost
        # ------------------------------------------

        material_cost = (
            weight_kg *
            material_price_eur_kg
        )

        # ------------------------------------------
        # Cycle Time Assumptions
        # Minutes per Piece
        # ------------------------------------------

        cycle_time_lookup = {

            "CNC Machining": 2.0,

            "Die Casting": 0.2,

            "HP Multi Jet Fusion": 5.0,

            "Investment Casting": 1.0,

            "Sand Casting": 0.8,

            "Injection Moulding": 0.1,

            # Alternate IDs

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

        # ------------------------------------------
        # Machine Cost
        # ------------------------------------------

        machine_cost = (
            cycle_time_hours *
            machine_rate
        )

        # ------------------------------------------
        # Labour Cost
        # ------------------------------------------

        labour_cost = (
            cycle_time_hours *
            labour_rate
        )

        # ------------------------------------------
        # Setup Cost Allocation
        # ------------------------------------------

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

        # ------------------------------------------
        # Tooling Cost Allocation
        # ------------------------------------------

        tooling_cost_per_piece = 0

        if tool_life > 0:

            tooling_cost_per_piece = (
                tooling_cost /
                tool_life
            )

        # ------------------------------------------
        # Direct Cost
        # ------------------------------------------

        direct_cost = (
            material_cost
            + machine_cost
            + labour_cost
        )

        # ------------------------------------------
        # Overhead
        # ------------------------------------------

        overhead_cost = (
            direct_cost *
            (overhead_factor - 1)
        )

        # ------------------------------------------
        # Total Cost
        # ------------------------------------------

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + overhead_cost
            + setup_cost
            + tooling_cost_per_piece
        )

        # ------------------------------------------
        # Return Results
        # ------------------------------------------

        return {

            "Technology": technology,

            "Material Cost EUR":
                round(material_cost, 2),

            "Machine Cost EUR":
                round(machine_cost, 2),

            "Labour Cost EUR":
                round(labour_cost, 2),

            "Overhead Cost EUR":
                round(overhead_cost, 2),

    
