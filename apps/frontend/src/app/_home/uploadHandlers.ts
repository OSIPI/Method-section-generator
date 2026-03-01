import { getReport } from "@/services/apiReport";
import { toast } from "sonner";
import { UploadModalityType, UploadDataType } from "@/enums";
import { findNiftiFile, findRelevantFiles } from "@/utils";
import { IAllRelevantFilesType } from "@/types";

const handleDicomUpload = async ({
  files,
  setIsLoading,
  activeModalityTypeOption,
}: {
  files: FileList;
  setIsLoading: (v: boolean) => void;
  activeModalityTypeOption: UploadModalityType;
}) => {
  if (!files || files.length === 0) return;

    const filesArray = Array.from(files);

    // DICOM files: .dcm, .img, or no extension
    const dicomFiles = filesArray.filter(
      (file) =>
        file.name.endsWith(".dcm") ||
        file.name.endsWith(".img") ||
        !file.name.includes(".")
    );

    // PRE-FLIGHT VALIDATION: Fail fast if no valid files exist
    if (dicomFiles.length === 0) {
      toast.error("No valid DICOM files found in the selected folder. Please ensure the folder contains .dcm or .img files.");
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      dicomFiles.forEach((file) => formData.append("dcm_files", file));
      formData.append("modality", activeModalityTypeOption);

      const data = await getReport(formData, UploadDataType.DICOM.toLowerCase());
      setIsLoading(false);
      return data;

    } catch (error) {
      console.error("Upload error:", error);
      setIsLoading(false);
      toast.error(`Upload failed. Please check your network connection and try again.`);
    }
  }

const handleBidsUpload = async ({
  files,
  setIsLoading,
  setUploadedFiles,
  setUploadConfig,
  setUpdatedJsonContent,
  setUpdatedJsonFilename,
  activeModalityTypeOption,
}: {
  files: FileList;
  setIsLoading: (v: boolean) => void;
  setUploadedFiles: (files: IAllRelevantFilesType) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setUploadConfig: (config: any) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setUpdatedJsonContent: (content: any) => void;
  setUpdatedJsonFilename: (filename: string) => void;
  activeModalityTypeOption: UploadModalityType;
}) => {
  if (!files || files.length === 0) return;

    const filesArray = Array.from(files);

    const niftiFile = findNiftiFile(filesArray);
    const aslRelevantFiles = findRelevantFiles(filesArray);

    // PRE-FLIGHT VALIDATION: Prevent empty backend requests
    if (!niftiFile && aslRelevantFiles.length === 0) {
      toast.error("No valid BIDS format files found. Please check your dataset.");
      return;
    }

    setIsLoading(true);
    try {
      const allRelevantFiles: IAllRelevantFilesType = {
        nifti_file: niftiFile,
        asl_files: aslRelevantFiles,
        dicom_files: [],
      };

      const formData = new FormData();
      if (niftiFile) formData.append("nifti_file", niftiFile);

      filesArray.forEach((file) => {
        if (file.name.endsWith(".dcm")) {
          formData.append("dcm_files", file);
          allRelevantFiles.dicom_files.push(file);
        }
      });

      aslRelevantFiles.forEach((file) => {
        formData.append("files", file);
        formData.append("filenames", file.name);
      });

      setUploadedFiles(allRelevantFiles);
      setUploadConfig({ modalityType: activeModalityTypeOption, fileType: UploadDataType.BIDS });
      setUpdatedJsonContent(null);
      setUpdatedJsonFilename('');
      formData.append("modality", activeModalityTypeOption);

      const data = await getReport(formData, UploadDataType.BIDS.toLowerCase());
      setIsLoading(false);
      return data;

    } catch (error) {
      console.error("Upload error:", error);
      setIsLoading(false);
      toast.error(`Upload failed. Please check your network connection and try again.`);
    }
}

export { handleDicomUpload, handleBidsUpload }