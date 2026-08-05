from pyaslreport.sequences.base_sequence import BaseSequence
from pyaslreport.utils import dicom_tags_utils as dcm_tags

class SiemensBaseSequence(BaseSequence):
    @classmethod
    def is_siemens_manufacturer(cls, dicom_header):
        """
        Check if the manufacturer contains Siemens.
        
        Args:
            dicom_header: DICOM header dictionary
            
        Returns:
            bool: True if manufacturer contains Siemens
        """
        manufacturer = dicom_header.get(dcm_tags.MANUFACTURER, "").value.strip().upper()
        return "SIEMENS" in manufacturer or "SIEMENS HEALTHCARE" in manufacturer or "SIEMENS HEALTHINEERS" in manufacturer


    def _extract_siemens_common_metadata(self) -> dict:
        d = self.dicom_header
        bids = {}
        # Siemens-specific metadata extraction
        if dcm_tags.SIEMENS_BANDWIDTH_PER_PIXEL_PHASE_ENCODING in d:
            bids["BandwidthPerPixelPhaseEncode"] = d.get(dcm_tags.SIEMENS_BANDWIDTH_PER_PIXEL_PHASE_ENCODING, None).value

        if dcm_tags.SIEMENS_ROWS in d and dcm_tags.SIEMENS_COLUMNS in d:
            rows = d.get(dcm_tags.SIEMENS_ROWS, None).value
            cols = d.get(dcm_tags.SIEMENS_COLUMNS, None).value
            bids["AcquisitionMatrix"] = [rows, cols]

        if dcm_tags.SIEMENS_INPLANE_PHASE_ENCODING_DIRECTION in d:
            bids["InPlanePhaseEncodingDirection"] = d.get(dcm_tags.SIEMENS_INPLANE_PHASE_ENCODING_DIRECTION, None).value

        # Derive EffectiveEchoSpacing and TotalReadoutTime from BandwidthPerPixelPhaseEncode
        if dcm_tags.SIEMENS_BANDWIDTH_PER_PIXEL_PHASE_ENCODING in d and dcm_tags.SIEMENS_ROWS in d:
            try:
                bw = float(d.get(dcm_tags.SIEMENS_BANDWIDTH_PER_PIXEL_PHASE_ENCODING, None).value)
                rows = int(d.get(dcm_tags.SIEMENS_ROWS, None).value)
                if bw > 0:
                    bids["EffectiveEchoSpacing"] = 1.0 / (bw * rows)
                    bids["TotalReadoutTime"] = (rows - 1) * bids["EffectiveEchoSpacing"]
            except Exception:
                pass

        # MRAcquisitionType default is 3D if not present
        if dcm_tags.MR_ACQUISITION_TYPE in d:
            bids["MRAcquisitionType"] = d.get(dcm_tags.MR_ACQUISITION_TYPE, None).value
        else:
            bids["MRAcquisitionType"] = "3D"

        # PulseSequenceType default is spiral if not present
        if dcm_tags.MR_ACQUISITION_TYPE in d:
            bids["PulseSequenceType"] = d.get(dcm_tags.MR_ACQUISITION_TYPE, None).value
        else:
            bids["PulseSequenceType"] = "spiral"

        return bids