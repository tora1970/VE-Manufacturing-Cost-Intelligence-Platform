from manufacturing_model.base_model import (
    BaseManufacturingModel
)

from utils.validators import (
    validate_common_inputs,
    validate_cycle_time,
    validate_machine_rate,
    validate_tool_cost,
    validate_tool_life,
    validate_scrap_rate
)


class InjectionMoldingModel(
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

        shot_weight_kg = kwargs.get(
            "shot_weight_kg",
            part_weight * 1.03
        )

        cycle_time_sec = kwargs.get(
            "cycle_time_sec",
            30
        )

        machine_rate_per_hour = kwargs.get(
            "machine_rate_per_hour",
            55
        )

        tool_cost = kwargs.get(
            "tool_cost",
            80000
        )

        tool_life_shots = kwargs.get(
            "tool_life_shots",
            1000000
        )

        scrap_rate = kwargs.get(
            "scrap_rate",
            0.015
        )

        cavities = kwargs.get(
            "cavities",
            1
        )

        validate_cycle_time(
            cycle_time_sec
        )

        validate_machine_rate(
            machine_rate_per_hour
        )

        validate_tool_cost(
            tool_cost
        )

        validate_tool_life(
            tool_life_shots
        )

        validate_scrap_rate(
            scrap_rate
        )

        # ----------------------------------
        # CREATE OUTPUT
        # ----------------------------------

        result = self.create_output()

        result["Technology"] = (
            "Injection Molding"
        )

        # ----------------------------------
        # EFFECTIVE CYCLE TIME
        # ----------------------------------

        cycle_time_per_part = (
            cycle_time_sec / cavities
        )

        # ----------------------------------
        # MATERIAL COST
        # ----------------------------------

        material_cost = (
            shot_weight_kg
            * material_price
            * (1 + scrap_rate)
        )

        # ----------------------------------
        # MACHINE COST
        # ----------------------------------

        machine_cost = (
            cycle_time_per_part
            / 3600
            * machine_rate_per_hour
        )

        # ----------------------------------
        # LABOUR COST
        # ----------------------------------

        labour_cost = (
            cycle_time_per_part
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
        # TOOLING COST
        # ----------------------------------

        tooling_cost = (
            tool_cost
            / tool_life_shots
        )

        # ----------------------------------
        # SETUP COST
        # ----------------------------------

        setup_cost = (
            tool_cost
            / annual_volume
            * 0.01
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
        # KPIs
        # ----------------------------------

        parts_per_hour = (
            cavities
            * 3600
            / cycle_time_sec
        )

        material_utilization_pct = (
            part_weight
            / shot_weight_kg
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
                85.0,

            "machine_utilization_pct":
                85.0,

            "tool_cost_per_part":
                tooling_cost,

            "cavities":
                cavities
        }

        # ----------------------------------
        # WARNINGS
        # ----------------------------------

        if cavities == 1 and annual_volume > 100000:
            self.add_warning(
                result,
                "Consider multi-cavity tooling."
            )

        if scrap_rate > 0.03:
            self.add_warning(
                result,
                "High scrap rate."
            )

        if annual_volume < 5000:
            self.add_warning(
                result,
                "Injection molding may not be economical at low volumes."
            )

        if material_utilization_pct < 95:
            self.add_warning(
                result,
                "Excessive runner or sprue material."
            )

        return result
