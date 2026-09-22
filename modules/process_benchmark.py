import pandas as pd

from engine.cost_engine import CostEngine
from engine.process_selector import ProcessSelector


class ProcessBenchmark:

    def __init__(
        self,
        technology_cost_df=None
    ):
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

        if technology_inputs is None:
            technology_inputs = {}

        results = []

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

                cost_result = (
                    self.cost_engine.calculate_cost(
                        technology=technology,
                        part_weight=part_weight,
                        annual_volume=annual_volume,
                        material_price=material_price,
                        labour_rate=labour_rate,
                        overhead_factor=overhead_factor,
                        **process_inputs
                    )
                )

                results.append({
                    "Technology":
                        technology,

                    "Material Cost":
                        cost_result.get(
                            "Material Cost",
                            0
                        ),

                    "Setup Cost":
                        cost_result.get(
                            "Setup Cost",
                            0
                        ),

                    "Machine Cost":
                        cost_result.get(
                            "Machine Cost",
                            0
                        ),

                    "Labour Cost":
                        cost_result.get(
                            "Labour Cost",
                            0
                        ),

                    "Overhead Cost":
                        cost_result.get(
                            "Overhead Cost",
                            0
                        ),

                    "Tooling Cost":
                        cost_result.get(
                            "Tooling Cost",
                            0
                        ),

                    "Manufacturing Cost":
                        cost_result.get(
                            "Manufacturing Cost",
                            0
                        ),

                    "Cost Per Part":
                        cost_result.get(
                            "Total Cost",
                            0
                        ),

                    "Annual Cost":
                        cost_result.get(
                            "Total Cost",
                            0
                        ) * annual_volume,

                    "Validation Score":
                        cost_result.get(
                            "Validation Score",
                            100
                        ),

                    "Warnings":
                        "; ".join(
                            cost_result.get(
                                "Warnings",
                                []
                            )
                        ),

                    "KPIs":
                        cost_result.get(
                            "KPIs",
                            {}
                        )
                })

            except Exception as e:

                results.append({
                    "Technology": technology,
                    "Cost Per Part": None,
                    "Annual Cost": None,
                    "Validation Score": 0,
                    "Warnings": str(e),
                    "KPIs": {}
                })

        benchmark_df = pd.DataFrame(
            results
        )

        if benchmark_df.empty:
            return benchmark_df

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

    def calculate_savings(
        self,
        benchmark_df,
        baseline_technology
    ):

        benchmark_df = (
            benchmark_df.copy()
        )

        baseline_row = benchmark_df[
            benchmark_df["Technology"]
            == baseline_technology
        ]

        if baseline_row.empty:
            return benchmark_df

        baseline_cost = (
            baseline_row.iloc[0]
            ["Cost Per Part"]
        )

        benchmark_df[
            "Saving Per Part"
        ] = (
            baseline_cost
            - benchmark_df[
                "Cost Per Part"
            ]
        )

        benchmark_df[
            "Saving %"
        ] = (
            benchmark_df[
                "Saving Per Part"
            ]
            / baseline_cost
            * 100
        )

        return benchmark_df

    def calculate_annual_savings(
        self,
        benchmark_df,
        annual_volume
    ):

        benchmark_df = (
            benchmark_df.copy()
        )

        if (
            "Saving Per Part"
            not in benchmark_df.columns
        ):
            return benchmark_df

        benchmark_df[
            "Annual Saving"
        ] = (
            benchmark_df[
                "Saving Per Part"
            ]
            * annual_volume
        )

        return benchmark_df

    def calculate_payback(
        self,
        benchmark_df,
        baseline_technology
    ):

        benchmark_df = (
            benchmark_df.copy()
        )

        baseline_row = benchmark_df[
            benchmark_df["Technology"]
            == baseline_technology
        ]

        if baseline_row.empty:
            return benchmark_df

        baseline_tooling = (
            baseline_row.iloc[0]
            .get(
                "Tooling Cost",
                0
            )
        )

        payback_years = []

        for _, row in (
            benchmark_df.iterrows()
        ):

            annual_saving = row.get(
                "Annual Saving",
                0
            )

            tooling_cost = row.get(
                "Tooling Cost",
                0
            )

            if annual_saving <= 0:

                payback_years.append(
                    None
                )

                continue

            incremental_investment = max(
                0,
                tooling_cost
                - baseline_tooling
            )

            payback_years.append(
                incremental_investment
                / annual_saving
            )

        benchmark_df[
            "Payback 
