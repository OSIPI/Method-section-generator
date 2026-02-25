interface IAllRelevantFilesType {
  nifti_file: File | null;
  asl_files: File[];
  dicom_files: File[];
};


export default IAllRelevantFilesType