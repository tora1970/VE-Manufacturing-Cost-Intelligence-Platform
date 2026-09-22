from manufacturing_model.hpdc import HPDCModel
from manufacturing_model.injection_molding import InjectionMoldingModel
from manufacturing_model.sand_casting import SandCastingModel
from manufacturing_model.cnc import CNCModel
from manufacturing_model.machining import MachiningModel
from manufacturing_model.sheet_metal import SheetMetalModel


PROCESS_MAP = {

    "HPDC": HPDCModel,

    "Injection Molding": InjectionMoldingModel,

    "Sand Casting": SandCastingModel,

    "CNC": CNCModel,

    "Machining": MachiningModel,

    "Sheet Metal": SheetMetalModel,
}


class ProcessSelector:

    @staticmethod
    def get_model(
        technology: str
    ):
        """
        Returns instantiated manufacturing model.
        """

        model_class = PROCESS_MAP.get(
            technology
        )

        if model_class is None:

            available = ", ".join(
                PROCESS_MAP.keys()
            )

            raise ValueError(
                f"Unsupported technology: "
                f"{technology}. "
                f"Available technologies: "
                f"{available}"
            )

        return model_class()

    @staticmethod
    def get_available_technologies():
        """
        Returns available process technologies.
        """

        return sorted(
            PROCESS_MAP.keys()
        )

    @staticmethod
    def technology_exists(
        technology: str
    ):
        """
        Check if technology is supported.
        """

        return technology in PROCESS_MAP
