from abc import ABC, abstractmethod


class BaseManufacturingModel(ABC):

    def create_output(self):
        """
        Standard VECIP output schema.
        All manufacturing models must return this structure.
        """

        return {
            "Technology": "",

            "Material Cost": 0.0,
            "Setup Cost": 0.0,
            "Machine Cost": 0.0,
            "Labour Cost": 0.0,
            "Overhead Cost": 0.0,
            "Tooling Cost": 0.0,

            "Manufacturing Cost": 0.0,
            "Total Cost": 0.0,

            "Validation Score": 100,
            "Warnings": [],

            "KPIs": {
                "cycle_time_sec": 0.0,
                "parts_per_hour": 0.0,

                "scrap_rate_pct": 0.0,
                "material_utilization_pct": 0.0,

                "oee_pct": 0.0,
                "machine_utilization_pct": 0.0,

                "tool_cost_per_part": 0.0
            }
        }

    def calculate_total_cost(
        self,
        material_cost,
        setup_cost,
        machine_cost,
        labour_cost,
        overhead_cost,
        tooling_cost
    ):
        """
        Common total cost calculation.
        """

        return (
            material_cost
            + setup_cost
            + machine_cost
            + labour_cost
            + overhead_cost
            + tooling_cost
        )

    def add_warning(
        self,
        output,
        message
    ):
        """
        Add validation warning.
        """

        output["Warnings"].append(message)

        output["Validation Score"] = max(
            0,
            output["Validation Score"] - 10
        )

    @abstractmethod
    def calculate(
        self,
        part_weight,
        annual_volume,
        material_price,
        labour_rate,
        overhead_factor,
        **kwargs
    ):
        """
        Must be implemented by all manufacturing models.
        """
        pass
``
