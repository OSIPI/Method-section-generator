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
  setIsLoading(true);
  try {
    const filesArray = Array.from(files);

    // DICOM files: .dcm, .img, or no extension
    const dicomFiles = filesArray.filter(
      (file) =>
        file.name.endsWith(".dcm") ||
        file.name.endsWith(".img") ||
        !file.name.includes(".")
    );

    const formData = new FormData();

    dicomFiles.forEach((file) => {
      formData.append("dcm_files", file);
    });

    formData.append("modality", activeModalityTypeOption);

    const data = await getReport(formData, UploadDataType.DICOM.toLowerCase());

    setIsLoading(false);

    return data;

  } catch (error) {

    setIsLoading(false);
    toast.error(
      `An unexpected error occurred during upload, please try again. Error: ${error}`
    );

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
  setUploadConfig: (config: any) => void;
  setUpdatedJsonContent: (content: any) => void;
  setUpdatedJsonFilename: (filename: string) => void;
  activeModalityTypeOption: UploadModalityType;
}) => {
  setIsLoading(true);

  try {
    const filesArray = Array.from(files);

    const niftiFile = findNiftiFile(filesArray);
    const aslRelevantFiles = findRelevantFiles(filesArray);

    const allRelevantFiles: IAllRelevantFilesType = {
      nifti_file: niftiFile,
      asl_files: aslRelevantFiles,
      dicom_files: [],
    };

    const formData = new FormData();

    if (niftiFile) {
      formData.append("nifti_file", niftiFile);
    }

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

    setUploadConfig({
      modalityType: activeModalityTypeOption,
      fileType: UploadDataType.BIDS,
    });

    setUpdatedJsonContent(null);
    setUpdatedJsonFilename('');

    formData.append("modality", activeModalityTypeOption);

    const data = await getReport(formData, UploadDataType.BIDS.toLowerCase());

    setIsLoading(false);

    return data;

  } catch (error) {
    setIsLoading(false);
    toast.error(
      `An unexpected error occurred during upload, please try again. Error: ${error}`
    );
  }
}

export {
  handleDicomUpload,
  handleBidsUpload
}