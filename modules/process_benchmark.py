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

                benchmark_results.append({

                    "Technology":
                        technology,

                    "Cost Per Part":
                        result["Total Cost"],

                    "Annual Cost":
                        result["Total Cost"]
                        * annual_volume,

                    "Tooling Cost":
                        result["Tooling Cost"],

                    "Material Cost":
                        result["Material Cost"],

                    "Machine Cost":
                        result["Machine Cost"],

                    "Labour Cost":
                        result["Labour Cost"],

                    "Overhead Cost":
                        result["Overhead Cost"],

                    "Setup Cost":
                        result["Setup Cost"],

                    "Validation Score":
                        result["Validation Score"],

                    "Warnings":
                        "; ".join(
                            result["Warnings"]
                        ),

                    "KPIs":
                        result["KPIs"]
                })

            except Exception as e:

                benchmark_results.append({

                    "Technology":
                        technology,

                    "Cost Per Part":
                        None,

                    "Annual Cost":
                        None,

                    "Tooling Cost":
                        None,

                    "Material Cost":
                        None,

                    "Machine Cost":
                        None,

                    "Labour Cost":
                        None,

                    "Overhead Cost":
                        None,

                    "Setup Cost":
                        None,

                    "Validation Score":
                        0,

                    "Warnings":
                        str(e),

                    "KPIs":
                        {}
                })

        benchmark_df = pd.DataFrame(
            benchmark_results
        )

        benchmark_df = benchmark_df.sort_values(
            by="Cost Per Part",
            ascending=True,
            na_position="last"
        )

        benchmark_df = benchmark_df.reset_index(
            drop=True
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

        benchmark_df = benchmark_df.copy()

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
        baseline_technology,
        annual_volume
    ):

        benchmark_df = (
            self.calculate_savings(
                benchmark_df,
                baseline_technology
            )
        )

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

        benchmark_df = benchmark_df.copy()

        baseline_row = benchmark_df[
            benchmark_df["Technology"]
            == baseline_technology
        ]

        if baseline_row.empty:
            return benchmark_df

        baseline_tooling = (
            baseline_row.iloc[0]
            ["Tooling Cost"]
        )

        annual_saving_col = (
            "Annual Saving"
        )

        if annual_saving_col not in benchmark_df.columns:
            return benchmark_df

        paybacks = []

        for _, row in benchmark_df.iterrows():

            annual_saving = row[
                annual_saving_col
            ]

            alternative_tooling = row[
                "Tooling Cost"
            ]

            additional_investment = max(
                0,
                alternative_tooling
                - baseline_tooling
            )

            if annual_saving is None:
                paybacks.append(None)

            elif annual_saving <= 0:
                paybacks.append(None)

            else:
                paybacks.append(
                    additional_investment
                    / annual_saving
                )

        benchmark_df[
            "Payback (Years)"
        ] = paybacks

        return benchmark_df

    def get_best_technology(
        self,
        benchmark_df
    ):

        valid_df = benchmark_df.dropna(
            subset=["Cost Per Part"]
        )

        if valid_df.empty:
            return None

        return valid_df.iloc[0]

    def create_kpi_comparison(
        self,
        benchmark_df
    ):

        kpi_rows = []

        for _, row in benchmark_df.iterrows():

            technology = (
                row["Technology"]
            )

            kpis = row["KPIs"]

            for kpi_name, value in kpis.items():

                kpi_rows.append({

                    "Technology":
                        technology,

                    "KPI":
                        kpi_name,

                    "Value":
                        value
                })

        return pd.DataFrame(
            kpi_rows
        )

    def create_cost_breakdown(
        self,
        benchmark_df
    ):

        return benchmark_df[[
            "Technology",
            "Material Cost",
            "Machine Cost",
            "Labour Cost",
            "Overhead Cost",
            "Tooling Cost",
            "Setup Cost"
        ]].copy()
