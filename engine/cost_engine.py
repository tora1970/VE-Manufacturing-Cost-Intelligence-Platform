import pandas as pd

from services.process_selector import ProcessSelector


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
        overhead_factor,
        **kwargs
    ):

        # ==================================================
        # HPDC PROCESS MODEL
        # ==================================================

        if str(technology).strip().upper() == "HPDC":

            hpdc_result = ProcessSelector.calculate(
                technology="HPDC",
                process_inputs={
                    "part_weight_kg": weight,

                    "shot_weight_kg": kwargs.get(
                        "shot_weight_kg",
                        weight * 1.5
                    ),

                    "material_price_per_kg": material_price,

                    "cycle_time_sec": kwargs.get(
                        "cycle_time_sec",
                        45.0
                    ),

                    "machine_rate_per_hour": kwargs.get(
                        "machine_rate_per_hour",
                        75.0
                    ),

                    "labour_rate_per_hour": labour_rate,

                    "tool_cost": kwargs.get(
                        "tool_cost",
                        120000.0
                    ),

                    "tool_life_shots": kwargs.get(
                        "tool_life_shots",
                        750000
                    ),

                    "scrap_rate": kwargs.get(
                        "scrap_rate",
                        0.03
                    ),

                    "overhead_factor": (
                        overhead_factor - 1
                        if overhead_factor > 1
                        else overhead_factor
                    )
                }
            )

            return {
                "Technology": "HPDC",
                "Material Cost": round(
                    hpdc_result["material_cost"],
                    2
                ),
                "Setup Cost": 0.0,
                "Cycle Cost": round(
                    hpdc_result["machine_cost"]
                    + hpdc_result["labour_cost"],
                    2
                ),
                "Manufacturing Cost": round(
                    hpdc_result["machine_cost"]
                    + hpdc_result["labour_cost"],
                    2
                ),
                "Machine Cost": round(
                    hpdc_result["machine_cost"],
                    2
                ),
                "Labour Cost": round(
        
