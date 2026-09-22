import pandas as pd


class CostEngine:

    def __init__(self, technology_cost_df):

        self.df = technology_cost_df.copy()
        self.df.columns = self.df.columns.str.strip()

    def ca**ulate_cost(
    self,
    technol**y,
    weight,
    material_price**    annual_volume,
    labour_rat**
    overhead_factor,
    **kwarg**):

        # ------------------------------------------
        # Find Technology
        # ------------------------------------------

        process = self.df[
            self.df["Technology_Name"].astype(str).str.strip()
            == str(technology).strip()
        ]

        if process.empty:

            process = self.df[
                self.df["Technology_ID"].astype(str).str.strip()
                == str(technology).strip()
            ]

        if process.empty:

            raise ValueError(
                f"Technology not found in Technology Cost Library: {technology}"
            )

        process = process.iloc[0]

        # ------------------------------------------
        # Material Cost
        # ------------------------------------------

        material_cost = (
            weight * material_price
        )

        # ------------------------------------------
        # Machine Data
        # ------------------------------------------

        machine_rate = float(
            process["Machine_Rate_EUR_hr"]
        )

        setup_hours = float(
            process["Setup_Hours"]
        )

        # ------------------------------------------
        # Cycle Time
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

        cycle_time_min = cycle_time_lookup.get(
            technology,
            1.0
        )

        cycle_time_hr = (
            cycle_time_min / 60
        )

        # ------------------------------------------
        # Machine Cost
        # ------------------------------------------

        machine_cost = (
            machine_rate
            * cycle_time_hr
        )

        # ------------------------------------------
        # Labour Cost
        # ------------------------------------------

        labour_cost = (
            labour_rate
            * cycle_time_hr
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

        tooling_cost = 0

        tool_cost = process.get(
            "Tooling_Cost_EUR",
            0
        )

        tool_life = process.get(
            "Tool_Life_Pcs",
            0
        )

        if (
            pd.notna(tool_cost)
            and pd.notna(tool_life)
            and tool_cost > 0
            and tool_life > 0
        ):

            tooling_cost = (
                tool_cost / tool_life
            )

        # ------------------------------------------
        # Overhead
        # ------------------------------------------

        direct_cost = (
            material_cost
            + machine_cost
            + labour_cost
        )

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
            + setup_cost
            + tooling_cost
            + overhead_cost
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

        validation_score = max(
            100 - len(warnings) * 10,
            0
        )

        # ------------------------------------------
        # Return
        # ------------------------------------------

        return {
            "Technology": technology,
            "Material Cost": round(material_cost, 2),
            "Setup Cost": round(setup_cost, 2),
            "Cycle Cost": round(machine_cost + labour_cost, 2),
            "Machine Cost": round(machine_cost, 2),
            "Labour Cost": round(labour_cost, 2),
            "Overhead Cost": round(overhead_cost, 2),
            "Tooling Cost": round(tooling_cost, 2),
            "Total Cost": round(total_cost, 2),
            "Validation Score": validation_score,
            "Warnings": warnings
        }

