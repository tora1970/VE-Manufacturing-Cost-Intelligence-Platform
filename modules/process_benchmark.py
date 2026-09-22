import pandas as pd

from engine.cost_engine import CostEngine
from engine.process_selector import ProcessSelector


class ProcessBenchmark:

    def __init__(self, technology_cost_df=None):

        self.cost_engine = CostEngine(
            technology_cost_df
        )

    def run_benchmark(
        self,
        part_weight,
        annual_volume,
        material_price,
        labour_rate,
        overhead_factor,
        technology_inputs=None
    ):
        """
        Benchmark all supported technologies.

        Parameters
        ----------
        technology_inputs : dict

        Example:

        {
            "HPDC": {...},
            "Injection Molding": {...},
            "CNC": {...}
        }
        """

        if technology_inputs is None:
            technology_inputs = {}

        benchmark_results = []

        technologies = (
            ProcessSelector
            .get_available_technologies()
        )

        for technology in technologies:

            try:

                process_inputs = (
                    technology_inputs.get(
                        technology,
                        {}
                    )
                )

                result = (
                    self.cost_engine
                    .calculate_cost(
                        technology=technology,
                        part_weight=part_weight,
                        annual_volume=annual_volume,
                        material_price=material_price,
                        labour_rate=labour_rate,
                        overhead_factor=overhead_factor,
                        **process_inputs
                    )
                )

                benchmark_results.append(

                    {
                        "Technology":
                            technology,

                        "Cost Per Part":
                            result["Total Cost"],

                        "Annual Cost":
                            result["Total Cost"]
                            * annual_volume,

                        "Tooling Cost":
                            result[
                                "Tooling Cost"
                            ],

                        "Material Cost":
                            result[
                                "Material Cost"
                            ],

                        "Machine Cost":
                            result[
                                "Machine Cost"
                            ],

                        "Labour Cost":
                            result[
                                "Labour Cost"
                            ],

                        "Overhead Cost":
                            result[
                                "Overhead Cost"
                            ],

                        "Setup Cost":
                            result[
                                "Setup Cost"
                            ],

                        "Validation Score":
                            result[
                                "Validation Score"
                            ],

                        "Warnings":
                            "; ".join(
                                result["Warnings"]
                            ),

                        "KPIs":
                            result["KPIs"]
                    }

                )

            except Exception as e:

                benchmark_results.append(
                    {
                        "Technology":
                            technology,

                        "Cost Per Part":
                            None,

                        "Annual Cost":
                            None,

                        "Tooling Cost":
                            None,

                        "Validation Score":
                            0,

                        "Warnings":
                            str(e),

                        "KPIs":
                            {}
                    }
                )

        benchmark_df = pd.DataFrame(
            benchmark_results
        )

        benchmark_df = (
            benchmark_df
            .sort_values(
                by="Cost Per Part",
                ascending=True,
                na_position="last"
            )
            .reset_index(
                drop=True
            )
        )

        benchmark_df.insert(
            0,
            "Rank",
            range(
                1,
                len(benchmark_df) + 1
            )
        )

        return benchmark_df
