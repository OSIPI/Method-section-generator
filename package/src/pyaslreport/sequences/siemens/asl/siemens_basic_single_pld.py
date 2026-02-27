from pyaslreport.sequences.siemens.siemens_base import SiemensBaseSequence
from pyaslreport.utils import dicom_tags_utils as dcm_tags
from pydicom.tag import Tag

# Siemens uses standard DICOM InversionTime tag for PostLabelingDelay
SIEMENS_INVERSION_TIME = Tag(0x0018, 0x0082)

# TODO: LabelingDuration for Siemens should be extracted from the Phoenix protocol
# (private tag 0x0029,0x1020). For now, use the same tag address as GE_LABEL_DURATION
# since some Siemens sequences store it there.
SIEMENS_LABEL_DURATION = Tag(0x0043, 0x10A5)

class SiemensBasicSinglePLD(SiemensBaseSequence):
    @classmethod
    def matches(cls, dicom_header):
        return cls.is_siemens_manufacturer(dicom_header)
        
    @classmethod
    def get_specificity_score(cls) -> int:
        """Lower specificity score because it only checks for manufacturer."""
        return 1

    def extract_bids_metadata(self):
        bids = self._extract_common_metadata()
        bids.update(self._extract_siemens_common_metadata())
        d = self.dicom_header
        if SIEMENS_LABEL_DURATION in d:
            bids["LabelingDuration"] = d.get(SIEMENS_LABEL_DURATION, None).value
        if SIEMENS_INVERSION_TIME in d:
            bids["PostLabelingDelay"] = d.get(SIEMENS_INVERSION_TIME, None).value
        return bids 