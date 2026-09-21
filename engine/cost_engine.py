import pandas as pd


class CostEngine:

    def __init__(self, technology_cost_df):

        self.cost_library = technology_cost_df.copy()
        self.cost_library.columns = (
            self.cost_library.columns.str.strip()
        )

    def calculate_cost(
        self,
        technology,
        weight,
        material_price,
        annual_volume,
        labour_rate,
        overhead_factor
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

        # ------------------------------------------
        # Read Master Data
        # ------------------------------------------

        machine_rate = float(
            tech_row["Machine_Rate_EUR_hr"]
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
            weight
            * material_price
        )

        # ------------------------------------------
        # Cycle Time Assumptions
        # minutes per piece
        # ------------------------------------------

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
            str(technology).strip(),
            1.0
        )

        cycle_time_hours = (
            cycle_time_minutes / 60
        )

        # ------------------------------------------
        # Machine Cost
        # ------------------------------------------

        machine_cost = (
            cycle_time_hours
            * machine_rate
        )

        # ------------------------------------------
        # Labour Cost
        # ------------------------------------------

        labour_cost = (
            cycle_time_hours
            * labour_rate
        )

        # ------------------------------------------
        # Setup Cost
        # ------------------------------------------

        setup_cost = 0

        if annual_volume > 0:

            setup_cost = (
                setup_hours
                * labour_rate
                / annual_volume
            )

        # ------------------------------------------
        # Tooling Cost
        # ------------------------------------------

        tooling_cost_per_piece = 0

        if tool_life > 0:

            tooling_cost_per_piece = (
                tooling_cost
                / tool_life
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
        # Overhead Cost
        # ------------------------------------------

        overhead_cost = (
            direct_cost
            * max(
                overhead_factor - 1,
                0
            )
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
        # Validation
        # ------------------------------------------

        warnings = []

        if total_cost <= 0:

            warnings.append(
                "Total cost is zero or negative"
            )

        if material_cost <= 0:

            warnings.append(
                "Material cost is zero"
            )

        if overhead_cost < 0:

            warnings.append(
                "Negative overhead cost"
            )

        if tool_life <= 0:

            warnings.append(
                "Tool life is zero"
            )

        validation_score = max(
            100 - len(warnings) * 10,
            0
        )

        # ------------------------------------------
        # Return
        # ------------------------------------------

        return {

            "Technology":
                technology,

            "Material Cost":
                round(material_cost, 2),

            "Setup Cost":
                round(setup_cost, 2),

            "Cycle Cost":
                round(
                    machine_cost + labour_cost,
                    2
                ),

            "Machine Cost":
                round(machine_cost, 2),

            "Labour Cost":
                round(labour_cost, 2),

            "Overhead Cost":
                round(overhead_cost, 2),

            "Tooling Cost":
                round(tooling_cost_per_piece, 2),

            "Total Cost":
                round(total_cost, 2),

            "Validation Score":
                validation_score,

            "Warnings":
                warnings
        }
