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

        # ------------------------------------------
        # Find Technology
        # ------------------------------------------

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

        process = tech_row.iloc[0]

        # ------------------------------------------
        # Safe Field Reader
        # ------------------------------------------

        def get_value(column_name, default_value):

            if column_name not in process.index:
                return default_value

            value = process[column_name]

            if pd.isna(value):
                return default_value

            return value

        # ------------------------------------------
        # Read Master Data
        # ------------------------------------------

        machine_rate = float(
            get_value(
                "Machine_Rate_EUR_hr",
                0
            )
        )

        setup_hours = float(
            get_value(
                "Setup_Hours",
                0
            )
        )

        tooling_cost_total = float(
            get_value(
                "Tooling_Cost_EUR",
                0
            )
        )

        tool_life = float(
            get_value(
                "Tool_Life_Pcs",
                0
            )
        )

        cycle_time_sec = float(
            get_value(
                "Cycle_Time_sec",
                60
            )
        )

        scrap_rate = float(
            get_value(
                "Scrap_Rate",
                0
            )
        )

        yield_rate = float(
            get_value(
                "Yield_Rate",
                1
            )
        )

        batch_size = float(
            get_value(
                "Batch_Size",
                annual_volume
            )
        )

        oee = float(
            get_value(
                "OEE",
                1
            )
        )

        # ------------------------------------------
        # Validation
        # ------------------------------------------

        warnings = []

        for field in [
            "Cycle_Time_sec",
            "Scrap_Rate",
            "Yield_Rate",
            "Batch_Size",
            "OEE"
        \]:

            if field not in process.index:

                warnings.append(
                    f"Missing field: {field}"
                )

        if yield_rate <= 0:
            warnings.append("Yield <= 0")

        if yield_rate > 1:
            warnings.append("Yield > 1")

        if oee <= 0:
            warnings.append("OEE <= 0")
            oee = 1

        if oee > 1:
            warnings.append("OEE > 1")

        if scrap_rate < 0:
            warnings.append("Negative Scrap Rate")

        if batch_size <= 0:
            warnings.append("Batch Size <= 0")
            batch_size = annual_volume

        # ------------------------------------------
        # Material Cost
        # ------------------------------------------

        material_cost = (
            weight
            * material_price
            * (1 + scrap_rate)
        )

        material_cost = (
            material_cost / max(yield_rate, 0.01)
        )

        # ------------------------------------------
        # Setup Cost
        # ------------------------------------------

        setup_cost = 0

        if annual_volume > 0:

            batches_per_year = max(
                annual_volume / batch_size,
                1
            )

            total_setup_cost = (
                setup_hours
                * labour_rate
                * batches_per_year
            )

            setup_cost = (
                total_setup_cost
                / annual_volume
            )

        # ------------------------------------------
        # Cycle Costs
        # ------------------------------------------

        cycle_time_hours = (
            cycle_time_sec
            / 3600
        )

        machine_cost = (
            machine_rate
            * cycle_time_hours
            / oee
        )

        labour_cost = (
            labour_rate
            * cycle_time_hours
        )

        cycle_cost = (
            machine_cost
            + labour_cost
        )

        # ------------------------------------------
        # Tooling Cost
        # ------------------------------------------

        tooling_cost = 0

        if tool_life > 0:

            tooling_cost = (
                tooling_cost_total
                / tool_life
            )

        else:

            if tooling_cost_total > 0:

                warnings.append(
                    "Tool life is zero"
                )

        # ------------------------------------------
        # Direct Cost
        # ------------------------------------------

        direct_cost = (
            material_cost
            + setup_cost
            + cycle_cost
       )

        # ------------------------------------------
        # Overhead
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
            + setup_cost
            + machine_cost
            + labour_cost
            + overhead_cost
            + tooling_cost
        )

        if total_cost <= 0:

            warnings.append(
                "Total cost is zero or negative"
            )

        # ------------------------------------------
        # Validation Score
        # ------------------------------------------

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
            "Cycle Cost": round(cycle_cost, 2),
            "Machine Cost": round(machine_cost, 2),
            "Labour Cost": round(labour_cost, 2),
            "Overhead Cost": round(overhead_cost, 2),
            "Tooling Cost": round(tooling_cost, 2),
            "Total Cost": round(total_cost, 2),
            "Validation Score": validation_score,
            "Warnings": warnings
        }
