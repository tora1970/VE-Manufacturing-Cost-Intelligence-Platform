from manufacturing_model.base_model import (
    BaseManufacturingModel
)

from utils.validators import (
    validate_common_inputs,
    validate_positive,
    validate_non_negative
)


class CNCModel(
    BaseManufacturingModel
):

    def calculate(
        self,
        part_weight,
        annual_volume,
        material_price,
        labour_rate,
        overhead_factor,
        **kwargs
    ):

        # ----------------------------------
        # COMMON VALIDATION
        # ----------------------------------

        validate_common_inputs(
            part_weight=part_weight,
            annual_volume=annual_volume,
            material_price=material_price,
            labour_rate=labour_rate,
            overhead_factor=overhead_factor
        )

        # ----------------------------------
        # CNC INPUTS
        # ----------------------------------

        raw_material_weight = kwargs.get(
            "raw_material_weight_kg",
            part_weight * 2.0
        )

        machining_time_min = kwargs.get(
            "machining_time_min",
            10
        )

        setup_time_min = kwargs.get(
            "setup_time_min",
            60
        )

        machine_rate_per_hour = kwargs.get(
            "machine_rate_per_hour",
            60
        )

        tooling_cost_per_part = kwargs.get(
            "tooling_cost_per_part",
            0.05
        )

        scrap_rate = kwargs.get(
            "scrap_rate",
            0.02
        )

        validate_positive(
            raw_material_weight,
            "Raw Material Weight"
        )

        validate_positive(
            machining_time_min,
            "Machining Time"
        )

        validate_non_negative(
            setup_time_min,
            "Setup Time"
        )

        validate_positive(
            machine_rate_per_hour,
            "Machine Rate"
        )

        validate_non_negative(
            tooling_cost_per_part,
            "Tooling Cost Per Part"
        )

        validate_non_negative(
            scrap_rate,
            "Scrap Rate"
        )

        # ----------------------------------
        # CREATE OUTPUT
        # ----------------------------------

        result = self.create_output()

        result["Technology"] = "CNC"

        # ----------------------------------
        # MATERIAL COST
        # ----------------------------------

        material_cost = (
            raw_material_weight
            * material_price
            * (1 + scrap_rate)
        )

        # ----------------------------------
        # MACHINE COST
        # ----------------------------------

        machine_cost = (
            machining_time_min
            / 60
            * machine_rate_per_hour
        )

        # ----------------------------------
        # LABOUR COST
        # ----------------------------------

        labour_cost = (
            machining_time_min
            / 60
            * labour_rate
        )

        # ----------------------------------
        # OVERHEAD COST
        # ----------------------------------

        overhead_cost = (
            labour_cost
            * overhead_factor
        )

        # ----------------------------------
        # TOOLING COST
        # ----------------------------------

        tooling_cost = (
            tooling_cost_per_part
        )

        # ----------------------------------
        # SETUP COST
        # ----------------------------------

        setup_cost = (
            (
                setup_time_min
                / 60
                * machine_rate_per_hour
            )
            / annual_volume
        )

        # ----------------------------------
        # MANUFACTURING COST
        # ----------------------------------

        manufacturing_cost = (
            machine_cost
            + labour_cost
            + overhead_cost
        )

        total_cost = (
            self.calculate_total_cost(
                material_cost=material_cost,
                setup_cost=setup_cost,
                machine_cost=machine_cost,
                labour_cost=labour_cost,
                overhead_cost=overhead_cost,
                tooling_cost=tooling_cost
            )
        )

        # ----------------------------------
        # OUTPUT
        # ----------------------------------

        result["Material Cost"] = material_cost
        result["Setup Cost"] = setup_cost
        result["Machine Cost"] = machine_cost
        result["Labour Cost"] = labour_cost
        result["Overhead Cost"] = overhead_cost
        result["Tooling Cost"] = tooling_cost

        result["Manufacturing Cost"] = (
            manufacturing_cost
        )

        result["Total Cost"] = total_cost

        # ----------------------------------
        # KPIs
        # ----------------------------------

        parts_per_hour = (
            60 / machining_time_min
        )

        material_utilization_pct = (
            part_weight
            / raw_material_weight
            * 100
        )

        chip_loss_pct = (
            100
            - material_utilization_pct
        )

        result["KPIs"] = {

            "cycle_time_sec":
                machining_time_min * 60,

            "parts_per_hour":
                parts_per_hour,

            "scrap_rate_pct":
                scrap_rate * 100,

            "material_utilization_pct":
                material_utilization_pct,

            "oee_pct":
                75.0,

            "machine_utilization_pct":
                75.0,

            "tool_cost_per_part":
                tooling_cost,

            "chip_loss_pct":
                chip_loss_pct
        }

        # ----------------------------------
        # WARNINGS
        # ----------------------------------

        if material_utilization_pct < 50:
            self.add_warning(
                result,
                "Low material utilization."
            )

        if machining_time_min > 30:
            self.add_warning(
                result,
                "Long machining cycle time."
            )

        if annual_volume > 100000:
            self.add_warning(
                result,
                "CNC may be uneconomical at very high volume."
            )

        if chip_loss_pct > 70:
            self.add_warning(
                result,
                "High material removal rate."
            )

        return result
