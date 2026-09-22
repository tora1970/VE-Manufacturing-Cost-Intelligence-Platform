from manufacturing_model.base_model import (
    BaseManufacturingModel
)

from utils.validators import (
    validate_common_inputs,
    validate_positive,
    validate_non_negative
)


class SheetMetalModel(
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
        # PROCESS INPUTS
        # ----------------------------------

        blank_weight_kg = kwargs.get(
            "blank_weight_kg",
            part_weight * 1.15
        )

        cutting_time_min = kwargs.get(
            "cutting_time_min",
            1.0
        )

        bending_time_min = kwargs.get(
            "bending_time_min",
            0.5
        )

        setup_time_min = kwargs.get(
            "setup_time_min",
            30.0
        )

        machine_rate_per_hour = kwargs.get(
            "machine_rate_per_hour",
            50.0
        )

        tooling_cost_per_part = kwargs.get(
            "tooling_cost_per_part",
            0.01
        )

        scrap_rate = kwargs.get(
            "scrap_rate",
            0.05
        )

        validate_positive(
            blank_weight_kg,
            "Blank Weight"
        )

        validate_positive(
            cutting_time_min,
            "Cutting Time"
        )

        validate_non_negative(
            bending_time_min,
            "Bending Time"
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

        result["Technology"] = "Sheet Metal"

        # ----------------------------------
        # PROCESS TIME
        # ----------------------------------

        process_time_min = (
            cutting_time_min
            + bending_time_min
        )

        # ----------------------------------
        # MATERIAL COST
        # ----------------------------------

        material_cost = (
            blank_weight_kg
            * material_price
            * (1 + scrap_rate)
        )

        # ----------------------------------
        # MACHINE COST
        # ----------------------------------

        machine_cost = (
            process_time_min
            / 60
            * machine_rate_per_hour
        )

        # ----------------------------------
        # LABOUR COST
        # ----------------------------------

        labour_cost = (
            process_time_min
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

        total_cost = self.calculate_total_cost(
            material_cost=material_cost,
            setup_cost=setup_cost,
            machine_cost=machine_cost,
            labour_cost=labour_cost,
            overhead_cost=overhead_cost,
            tooling_cost=tooling_cost
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
            60 / process_time_min
        )

        material_utilization_pct = (
            part_weight
            / blank_weight_kg
            * 100
        )

        nesting_loss_pct = (
            100
            - material_utilization_pct
        )

        result["KPIs"] = {

            "cycle_time_sec":
                process_time_min * 60,

            "parts_per_hour":
                parts_per_hour,

            "scrap_rate_pct":
                scrap_rate * 100,

            "material_utilization_pct":
                material_utilization_pct,

            "oee_pct":
                85.0,

            "machine_utilization_pct":
                85.0,

            "tool_cost_per_part":
                tooling_cost,

            "nesting_loss_pct":
                nesting_loss_pct
        }

        # ----------------------------------
        # WARNINGS
        # ----------------------------------

        if material_utilization_pct < 75:
            self.add_warning(
                result,
                "Low nesting efficiency."
            )

        if scrap_rate > 0.10:
            self.add_warning(
                result,
                "High material scrap."
            )

        if process_time_min > 5:
            self.add_warning(
                result,
                "Long fabrication cycle time."
            )

        if annual_volume > 250000:
            self.add_warning(
                result,
                "Consider progressive tooling for very high volumes."
            )

        return result

