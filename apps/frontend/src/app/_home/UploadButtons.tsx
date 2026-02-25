"use client";

import React, { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { UploadDataType, UploadModalityType } from "@/enums";
import { Upload as UploadIcon } from "lucide-react";
import { useAppContext } from "@/providers/AppProvider";
import { findNiftiFile, findRelevantFiles } from "@/utils";
import { getReport } from "@/services/apiReport";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { IAllRelevantFilesType } from "@/types";
import { handleBidsUpload, handleDicomUpload } from "./uploadHandlers";

type TUploadDataOptions = (typeof UploadDataType)[keyof typeof UploadDataType];
type TUploadModalOptions =
  (typeof UploadModalityType)[keyof typeof UploadModalityType];


const UploadButtons = () => {
  const [activeFileTypeOption, setActiveFileTypeOption] =
    useState<TUploadDataOptions>(UploadDataType.BIDS);
  const [activeModalityTypeOption, setActiveModalityTypeOption] =
    useState<TUploadModalOptions>(UploadModalityType.ASL);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const { setIsLoading, setApiData, setUploadedFiles, setUploadConfig, setUpdatedJsonContent, setUpdatedJsonFilename } =
    useAppContext();
  const router = useRouter();

  const handleDirectoryUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files: FileList | null = e.target.files;
    let data = null;

    if (files && files.length > 0) {

      if (activeFileTypeOption === UploadDataType.DICOM) {
        data = await handleDicomUpload({
          files,
          setIsLoading,
          activeModalityTypeOption,
        });
      }

      else if (activeFileTypeOption === UploadDataType.BIDS) {
        data = await handleBidsUpload({
          files,
          setIsLoading,
          setUploadedFiles,
          setUploadConfig,
          setUpdatedJsonContent,
          setUpdatedJsonFilename,
          activeModalityTypeOption,
        });
      }
    }

    if (data) {
      console.log("Data received from upload:", data);
      setApiData(data);
      if (
        data.missing_required_parameters &&
        data.missing_required_parameters.length > 0
      ) {
        toast.info(
          "Report generated with missing parameters. Please provide the missing values."
        );
      } else {
        toast.success("Report generated successfully!");
      }
      router.push("/report");
    } else {
      toast.error(
        "Failed to generate report. Please check the files and try again."
      );
    }
  };

  const handleUploadClick = () => {
    folderInputRef.current?.click();
  };

  return (
    <div className={"flex items-center justify-between mb-4"}>
      <div className={"flex gap-4"}>
        {/* Modality Select */}
        <fieldset className="flex w-fit" aria-label="Select Modality Type">
          <legend className="sr-only">Modality Type</legend>
          <Button
            type="button"
            className={cn(
              "rounded-l-md rounded-r-none border border-input cursor-pointer",
              activeModalityTypeOption === UploadModalityType.ASL
                ? "bg-primary text-primary-foreground"
                : "bg-background text-foreground hover:bg-accent hover:text-accent-foreground"
            )}
            onClick={() => setActiveModalityTypeOption(UploadModalityType.ASL)}
          >
            ASL
          </Button>
          <Button
            type="button"
            className={cn(
              "rounded-r-md rounded-l-none border-t border-b border-r border-input -ml-px cursor-pointer",
              activeModalityTypeOption === UploadModalityType.DCE
                ? "bg-primary text-primary-foreground"
                : "bg-background text-foreground hover:bg-accent hover:text-accent-foreground"
            )}
            onClick={() => setActiveModalityTypeOption(UploadModalityType.DCE)}
          >
            DCE
          </Button>
        </fieldset>
        {/* Files Type Select */}
        <fieldset className="flex w-fit" aria-label="Select File Type">
          <legend className="sr-only">File Type</legend>
          <Button
            type="button"
            className={cn(
              "rounded-l-md rounded-r-none border border-input cursor-pointer",
              activeFileTypeOption === UploadDataType.BIDS
                ? "bg-primary text-primary-foreground"
                : "bg-background text-foreground hover:bg-accent hover:text-accent-foreground"
            )}
            onClick={() => setActiveFileTypeOption(UploadDataType.BIDS)}
          >
            BDIS
          </Button>
          <Button
            type="button"
            className={cn(
              "rounded-r-md rounded-l-none border-t border-b border-r border-input -ml-px cursor-pointer",
              activeFileTypeOption === UploadDataType.DICOM
                ? "bg-primary text-primary-foreground"
                : "bg-background text-foreground hover:bg-accent hover:text-accent-foreground"
            )}
            onClick={() => setActiveFileTypeOption(UploadDataType.DICOM)}
          >
            DICOM
          </Button>
        </fieldset>
      </div>
      <div>
        <input
          type="file"
          ref={folderInputRef}
          onChange={handleDirectoryUpload}
          style={{ display: "none" }}
          {...{ webkitdirectory: "", directory: "" }}
        />
        <Button
          className={"cursor-pointer"}
          onClick={handleUploadClick}
          aria-label={`Upload ${activeModalityTypeOption} ${activeFileTypeOption} files`}
        >
          <UploadIcon />
          Upload {activeModalityTypeOption} {activeFileTypeOption}
        </Button>
      </div>
    </div>
  );
};

export default UploadButtons;
