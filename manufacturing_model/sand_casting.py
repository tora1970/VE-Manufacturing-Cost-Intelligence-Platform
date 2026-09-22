from manufacturing_model.base_model import (
    BaseManufacturingModel
)

from utils.validators import (
    validate_common_inputs,
    validate_cycle_time,
    validate_scrap_rate,
    validate_positive
)


class SandCastingModel(
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

        raw_weight_kg = kwargs.get(
            "raw_weight_kg",
            part_weight * 1.8
        )

        cycle_time_sec = kwargs.get(
            "cycle_time_sec",
            300
        )

        pattern_cost = kwargs.get(
            "pattern_cost",
            5000
        )

        pattern_life = kwargs.get(
            "pattern_life",
            100000
        )

        scrap_rate = kwargs.get(
            "scrap_rate",
            0.05
        )

        machine_rate_per_hour = kwargs.get(
            "machine_rate_per_hour",
            20
        )

        validate_cycle_time(
            cycle_time_sec
        )

        validate_scrap_rate(
            scrap_rate
        )

        validate_positive(
            raw_weight_kg,
            "Raw Weight"
        )

        validate_positive(
            pattern_life,
            "Pattern Life"
        )

        # ----------------------------------
        # CREATE OUTPUT
        # ----------------------------------

        result = self.create_output()

        result["Technology"] = (
            "Sand Casting"
        )

        # ----------------------------------
        # MATERIAL COST
        # ----------------------------------

        material_cost = (
            raw_weight_kg
            * material_price
            * (1 + scrap_rate)
        )

        # ----------------------------------
        # MACHINE COST
        # ----------------------------------

        machine_cost = (
            cycle_time_sec
            / 3600
            * machine_rate_per_hour
        )

        # ----------------------------------
        # LABOUR COST
        # ----------------------------------

        labour_cost = (
            cycle_time_sec
            / 3600
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
        # TOOLING / PATTERN COST
        # ----------------------------------

        tooling_cost = (
            pattern_cost
            / pattern_life
        )

        # ----------------------------------
        # SETUP COST
        # ----------------------------------

        setup_cost = (
            pattern_cost
            / annual_volume
            * 0.05
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

        result["Material Cost"] = (
            material_cost
        )

        result["Setup Cost"] = (
            setup_cost
        )

        result["Machine Cost"] = (
            machine_cost
        )

        result["Labour Cost"] = (
            labour_cost
        )

        result["Overhead Cost"] = (
            overhead_cost
        )

        result["Tooling Cost"] = (
            tooling_cost
        )

        result["Manufacturing Cost"] = (
            manufacturing_cost
        )

        result["Total Cost"] = (
            total_cost
        )

        # ----------------------------------
        # KPI'S
        # ----------------------------------

        parts_per_hour = (
            3600
            / cycle_time_sec
        )

        material_utilization_pct = (
            part_weight
            / raw_weight_kg
            * 100
        )

        result["KPIs"] = {

            "cycle_time_sec":
                cycle_time_sec,

            "parts_per_hour":
                parts_per_hour,

            "scrap_rate_pct":
                scrap_rate * 100,

            "material_utilization_pct":
                material_utilization_pct,

            "oee_pct":
                70.0,

            "machine_utilization_pct":
                70.0,

            "tool_cost_per_part":
                tooling_cost
        }

        # ----------------------------------
        # WARNINGS
        # ----------------------------------

        if annual_volume > 50000:
            self.add_warning(
                result,
                "Sand casting may not be optimal at high volume."
            )

        if material_utilization_pct < 60:
            self.add_warning(
                result,
                "Low material utilization."
            )

        if scrap_rate > 0.08:
            self.add_warning(
                result,
                "High scrap rate."
            )

        if cycle_time_sec > 600:
            self.add_warning(
                result,
                "Long process cycle time."
            )

        return result
