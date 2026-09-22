# services/process_selector.py

from manufacturing_model.hpdc import HPDCInputs, HPDCModel


class ProcessSelector:

    @staticmethod
    def calculate(
        technology: str,
        process_inputs: dict
    ):

        technology = technology.upper()

        if technology == "HPDC":

            inputs = HPDCInputs(
                part_weight_kg=process_inputs["part_weight_kg"],
                shot_weight_kg=process_inputs["shot_weight_kg"],
                material_price_per_kg=process_inputs["material_price_per_kg"],
                cycle_time_sec=process_inputs["cycle_time_sec"],
                machine_rate_per_hour=process_inputs["machine_rate_per_hour"],
                labour_rate_per_hour=process_inputs["labour_rate_per_hour"],
                tool_cost=process_inputs["tool_cost"],
                tool_life_shots=process_inputs["tool_life_shots"],
                scrap_rate=process_inputs.get("scrap_rate", 0.03),
                overhead_factor=process_inputs.get("overhead_factor", 0.15)
            )

            return HPDCModel(inputs).calculate()

        raise ValueError(
            f"Technology '{technology}' not implemented."
        )
