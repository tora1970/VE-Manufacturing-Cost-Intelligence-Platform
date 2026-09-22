from engine.process_selector import (
    ProcessSelector
)


class CostEngine:

    def __init__(self, technology_cost_df=None):
        """
        technology_cost_df retained for backwards
        compatibility and future benchmark databases.
        """

        self.technology_cost_df = (
            technology_cost_df
        )

    def calculate_cost(
        self,
        technology,
        part_weight,
        annual_volume,
        material_price,
        labour_rate,
        overhead_factor,
        **process_inputs
    ):
        """
        Generic technology-independent cost calculation.

        Parameters
        ----------
        technology : str
            Technology name.

        part_weight : float
            Finished part weight (kg).

        annual_volume : int
            Annual production volume.

        material_price : float
            Material price per kg.

        labour_rate : float
            Labour rate per hour.

        overhead_factor : float
            Overhead multiplier.

        process_inputs : dict
            Technology specific parameters.
        """

        model = ProcessSelector.get_model(
            technology
        )

        return model.calculate(
            part_weight=part_weight,
            annual_volume=annual_volume,
            material_price=material_price,
            labour_rate=labour_rate,
            overhead_factor=overhead_factor,
            **process_inputs
        )

    def get_supported_technologies(
        self
    ):
        """
        Returns all supported technologies.
        """

        return (
            ProcessSelector
            .get_available_technologies()
        )
