from pyaslreport.sequences.ge.asl.ge_asl_base import GEASLBase
from pyaslreport.utils import dicom_tags_utils as dcm_tags


class GEBasicSinglePLD(GEASLBase):
    @classmethod
    def matches(cls, dicom_header):
        # Basic GE single-PLD is the fallback for any GE ASL header that is not
        # eASL, including headers missing the internal sequence name (0019,109E).
        # The factory checks the more specific eASL matcher first.
        return cls.is_ge_manufacturer(dicom_header)

    @classmethod
    def get_specificity_score(cls) -> int:
        """Lower specificity score because it only checks for manufacturer."""
        return 1

    def extract_bids_metadata(self):
        bids = self._extract_common_metadata()
        bids.update(self._extract_ge_common_metadata())
        bids.update(self._extract_ge_common_asl_metadata())

        dicom_header = self.dicom_header
        if dcm_tags.GE_LABEL_DURATION in dicom_header:
            bids["LabelingDuration"] = self._ms_to_seconds(
                dicom_header.get(dcm_tags.GE_LABEL_DURATION, None).value
            )
        if dcm_tags.GE_INVERSION_TIME in dicom_header:
            bids["PostLabelingDelay"] = self._ms_to_seconds(
                dicom_header.get(dcm_tags.GE_INVERSION_TIME, None).value
            )

        asl_context = self._generate_asl_context(1)

        return bids, asl_context
