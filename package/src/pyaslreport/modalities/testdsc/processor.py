from pyaslreport.modalities.base_processor import BaseProcessor


class DSCProcessor(BaseProcessor):
    """
    Class for processing DSC (Dynamic Susceptibility Contrast) data.
    """

    def __init__(self, data) -> None:
        """
        Initialize the DSCProcessor with the input data.

        :param data: The input DSC data to be processed.
        """
        super().__init__(data)

    def process(self) -> dict:
        """
        Process the input DSC data.

        :return: Dictionary containing processing results.
        """
        # DSC processing is not yet implemented — return a structured placeholder
        # that matches the expected dict return type for all processors
        return {
            "status": "not_implemented",
            "message": "DSC processing is not yet implemented.",
            "modality": "DSC",
            "asl_parameters": [],
            "report": []
        }
