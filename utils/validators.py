"""
utils/validators.py

Common validation functions for all manufacturing models.

Used by:
- HPDC
- Injection Molding
- Sand Casting
- CNC
- Machining
- Sheet Metal
"""


def validate_part_weight(part_weight):
    if part_weight <= 0:
        raise ValueError(
            "Part weight must be greater than 0 kg."
        )

    if part_weight > 500:
        raise ValueError(
            "Part weight exceeds supported range (500 kg)."
        )


def validate_annual_volume(annual_volume):
    if annual_volume <= 0:
        raise ValueError(
            "Annual volume must be greater than 0."
        )

    if annual_volume > 1_000_000_000:
        raise ValueError(
            "Annual volume exceeds supported range."
        )


def validate_material_price(material_price):
    if material_price <= 0:
        raise ValueError(
            "Material price must be greater than 0 €/kg."
        )

    if material_price > 1_000:
        raise ValueError(
            "Material price exceeds supported range."
        )


def validate_labour_rate(labour_rate):
    if labour_rate <= 0:
        raise ValueError(
            "Labour rate must be greater than 0 €/hr."
        )

    if labour_rate > 500:
        raise ValueError(
            "Labour rate exceeds supported range."
        )


def validate_overhead_factor(overhead_factor):
    if overhead_factor < 0:
        raise ValueError(
            "Overhead factor cannot be negative."
        )

    if overhead_factor > 10:
        raise ValueError(
            "Overhead factor exceeds supported range."
        )


def validate_scrap_rate(scrap_rate):
    if scrap_rate < 0:
        raise ValueError(
            "Scrap rate cannot be negative."
        )

    if scrap_rate > 1:
        raise ValueError(
            "Scrap rate must be between 0 and 1."
        )


def validate_cycle_time(cycle_time_sec):
    if cycle_time_sec <= 0:
        raise ValueError(
            "Cycle time must be greater than 0 seconds."
        )

    if cycle_time_sec > 86400:
        raise ValueError(
            "Cycle time exceeds supported range."
        )


def validate_tool_cost(tool_cost):
    if tool_cost < 0:
        raise ValueError(
            "Tool cost cannot be negative."
        )


def validate_tool_life(tool_life):
    if tool_life <= 0:
        raise ValueError(
            "Tool life must be greater than 0."
        )


def validate_machine_rate(machine_rate_per_hour):
    if machine_rate_per_hour <= 0:
        raise ValueError(
            "Machine rate must be greater than 0 €/hr."
        )

    if machine_rate_per_hour > 10_000:
        raise ValueError(
            "Machine rate exceeds supported range."
        )


def validate_positive(value, field_name):
    if value <= 0:
        raise ValueError(
            f"{field_name} must be greater than 0."
        )


def validate_non_negative(value, field_name):
    if value < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )
