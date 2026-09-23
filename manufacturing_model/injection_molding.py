from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class InjectionMoldingInputs:
    part_weight_kg: float
    runner_weight_kg: float

    material_price_per_kg: float

    cycle_time_sec: float

    machine_rate_per_hour: float
    labour_rate_per_hour: float

    tool_cost: float
    tool_life_cycles: int

    scrap_rate: float = 0.03
    overhead_factor: float = 0.15


class InjectionMoldingModel:

    def __init__(self, inputs: InjectionMoldingInputs):
        self.i = inputs

    def validate(self):

        if self.i.part_weight_kg <= 0:
            raise ValueError("part_weight_kg must be > 0")

        if self.i.runner_weight_kg < 0:
            raise ValueError("runner_weight_kg cannot be negative")

        if self.i.material_price_per_kg <= 0:
            raise ValueError("material_price_per_kg must be > 0")

        if self.i.cycle_time_sec <= 0:
            raise ValueError("cycle_time_sec must be > 0")

        if self.i.machine_rate_per_hour <= 0:
            raise ValueError("machine_rate_per_hour must be > 0")

        if self.i.labour_rate_per_hour <= 0:
            raise ValueError("labour_rate_per_hour must be > 0")

        if self.i.tool_cost < 0:
            raise ValueError("tool_cost cannot be negative")

        if self.i.tool_life_cycles <= 0:
            raise ValueError("tool_life_cycles must be > 0")

        if not 0 <= self.i.scrap_rate < 0.50:
            raise ValueError(
                "scrap_rate must be between 0 and 0.50"
            )

        if self.i.overhead_factor < 0:
            raise ValueError(
                "overhead_factor cannot be negative"
            )

    def calculate(self) -> Dict[str, Any]:

        self.validate()

        shot_weight = (
            self.i.part_weight_kg
            + self.i.runner_weight_kg
        )

        gross_material_cost = (
            shot_weight
            * self.i.material_price_per_kg
        )

        material_cost = (
            gross_material_cost
            / (1 - self.i.scrap_rate)
        )

        cycle_time_hr = (
            self.i.cycle_time_sec
            / 3600
        )

        machine_cost = (
            cycle_time_hr
            * self.i.machine_rate_per_hour
        )

        labour_cost = (
            cycle_time_hr
            * self.i.labour_rate_per_hour
        )

        tooling_cost = (
            self.i.tool_cost
            / self.i.tool_life_cycles
        )

        overhead_cost = (
            material_cost
            + machine_cost
            + labour_cost
        ) * self.i.overhead_factor

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + tooling_cost
            + overhead_cost
        )

        material_utilization = (
            self.i.part_weight_kg
            / shot_weight
        )

        yield_loss = (
            1 - material_utilization
        )

        parts_per_hour = (
            3600
            / self.i.cycle_time_sec
        )

        return {
            "technology": "Injection Molding",

            "material_cost": material_cost,
            "machine_cost": machine_cost,
            "labour_cost": labour_cost,
            "tooling_cost": tooling_cost,
            "overhead_cost": overhead_cost,

            "total_cost": total_cost,

            "kpis": {
                "material_utilization_pct": round(
                    material_utilization * 100,
                    2
                ),

                "yield_loss_pct": round(
                    yield_loss * 100,
                    2
                ),

                "parts_per_hour": round(
                    parts_per_hour,
                    1
                ),

                "tool_cost_per_part": round(
                    tooling_cost,
                    4
                )
            }
        }
