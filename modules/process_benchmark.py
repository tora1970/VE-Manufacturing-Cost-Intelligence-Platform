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

                total_cost = (
                    cost_result["Total Cost"]
                )

                results.append({

                    "Technology":
                        technology,

                    "Cost Per Part":
                        total_cost,

                    "Annual Cost":
                        total_cost
                        * annual_volume,

                    "KPIs":
                        cost_result.get(
                            "KPIs",
                            {}
                        )
                })

            except Exception:

                continue

        benchmark_df = pd.DataFrame(
            results
        )

        if benchmark_df.empty:
            return benchmark_df

        benchmark_df = (
            benchmark_df
            .sort_values(
                by="Cost Per Part",
                ascending=True
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

    def get_best_technology(
        self,
        benchmark_df
    ):

        if benchmark_df.empty:
            return None

        return benchmark_df.iloc[0]

    def create_kpi_comparison(
        self,
        benchmark_df
    ):

        if benchmark_df.empty:
            return pd.DataFrame()

        kpi_rows = []

        for _, row in benchmark_df.iterrows():

            technology = (
                row["Technology"]
            )

            kpis = row.get(
                "KPIs",
                {}
            )

            if not isinstance(
                kpis,
                dict
            ):
                continue

            for (
                kpi_name,
                kpi_value
            ) in kpis.items():

                kpi_rows.append({

                    "Technology":
                        technology,

                    "KPI":
                        kpi_name,

                    "Value":
                        kpi_value
                })

        return pd.DataFrame(
            kpi_rows
        )
