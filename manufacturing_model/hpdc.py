# manufacturing_models/hpdc.py

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class HPDCInputs:
    part_weight_kg: float
    shot_weight_kg: float

    material_price_per_kg: float

    cycle_time_sec: float

    machine_rate_per_hour: float
    labour_rate_per_hour: float

    tool_cost: float
    tool_life_shots: int

    scrap_rate: float = 0.03
    overhead_factor: float = 0.15


class HPDCModel:
    """
    High Pressure Die Casting Process-Based Cost Model

    Cost Structure:
        - Material
        - Machine
        - Labour
        - Tooling
        - Overhead

    Outputs:
        - Total Manufacturing Cost
        - Cost Breakdown
        - Process KPIs
    """

    def __init__(self, inputs: HPDCInputs):
        self.i = inputs

    def validate(self):
        """Validate model inputs."""

        if self.i.part_weight_kg <= 0:
            raise ValueError("part_weight_kg must be > 0")

        if self.i.shot_weight_kg <= 0:
            raise ValueError("shot_weight_kg must be > 0")

        if self.i.shot_weight_kg < self.i.part_weight_kg:
            raise ValueError(
                "shot_weight_kg must be greater than or equal to part_weight_kg"
            )

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

        if self.i.tool_life_shots <= 0:
            raise ValueError("tool_life_shots must be > 0")

        if not 0 <= self.i.scrap_rate < 0.50:
            raise ValueError("scrap_rate must be between 0 and 0.50")

        if self.i.overhead_factor < 0:
            raise ValueError("overhead_factor cannot be negative")

    def calculate(self) -> Dict[str, Any\]:
        """Run complete HPDC cost calculation."""

        self.validate()

        # --------------------------------------------------
        # Material Cost
        # --------------------------------------------------

        gross_material_cost = (
            self.i.shot_weight_kg
            * self.i.material_price_per_kg
        )

        material_cost = (
            gross_material_cost
            / (1 - self.i.scrap_rate)
        )

        # --------------------------------------------------
        # Time Conversion
        # --------------------------------------------------

        cycle_time_hr = self.i.cycle_time_sec / 3600

        # --------------------------------------------------
        # Machine Cost
        # --------------------------------------------------

        machine_cost = (
            cycle_time_hr
            * self.i.machine_rate_per_hour
        )

        # --------------------------------------------------
        # Labour Cost
        # --------------------------------------------------

        labour_cost = (
            cycle_time_hr
            * self.i.labour_rate_per_hour
        )

        # --------------------------------------------------
        # Tooling Cost
        # --------------------------------------------------

        tooling_cost = (
            self.i.tool_cost
            / self.i.tool_life_shots
        )

        # --------------------------------------------------
        # Overhead Cost
        # --------------------------------------------------

        overhead_cost = (
            material_cost
            + machine_cost
            + labour_cost
        ) * self.i.overhead_factor

        # --------------------------------------------------
        # Total Cost
        # --------------------------------------------------

        total_cost = (
            material_cost
            + machine_cost
            + labour_cost
            + tooling_cost
            + overhead_cost
        )

        # --------------------------------------------------
        # KPIs
        # --------------------------------------------------

        material_utilization = (
            self.i.part_weight_kg
            / self.i.shot_weight_kg
        )

        yield_loss = (
            1 - material_utilization
        )

        parts_per_hour = (
            3600
            / self.i.cycle_time_sec
        )

        tool_cost_share = (
            tooling_cost / total_cost
            if total_cost > 0 else 0
        )

        material_share = (
            material_cost / total_cost
            if total_cost > 0 else 0
        )

        machine_share = (
            machine_cost / total_cost
            if total_cost > 0 else 0
        )

        labour_share = (
            labour_cost / total_cost
            if total_cost > 0 else 0
        )

        overhead_share = (
            overhead_cost / total_cost
            if total_cost > 0 else 0
        )

        return {
            "technology": "HPDC",

            "material_cost": round(material_cost, 4),
            "machine_cost": round(machine_cost, 4),
            "labour_cost": round(labour_cost, 4),
            "tooling_cost": round(tooling_cost, 4),
            "overhead_cost": round(overhead_cost, 4),

            "total_cost": round(total_cost, 4),

            "kpis": {
                "part_weight_kg": round(
                    self.i.part_weight_kg, 4
                ),
                "shot_weight_kg": round(
                    self.i.shot_weight_kg, 4
                ),

                "material_utilization_pct": round(
                    material_utilization * 100, 2
                ),

                "yield_loss_pct": round(
                    yield_loss * 100, 2
                ),

                "parts_per_hour": round(
                    parts_per_hour, 1
                ),

                "tool_cost_per_part": round(
                    tooling_cost, 4
                ),

                "material_share_pct": round(
                    material_share * 100, 2
                ),

                "machine_share_pct": round(
                    machine_share * 100, 2
                ),

                "labour_share_pct": round(
                    labour_share * 100, 2
                ),

                "tooling_share_pct": round(
                    tool_cost_share * 100, 2
                ),

                "overhead_share_pct": round(
                    overhead_share * 100, 2
                ),
            }
        }
