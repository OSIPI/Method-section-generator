"use client";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/providers/AppProvider";
import React, { useState } from "react";
import { Check, AlertCircle } from "lucide-react";
import { getReport } from "@/services/apiReport";
import {ASLRelevantFileNames} from '@/enums';

import { toast } from "sonner";

export default function MissingParameters() {
  const { apiData, uploadedFiles, uploadConfig, setIsLoading, setApiData, setUpdatedJsonContent, setUpdatedJsonFilename } =
    useAppContext();
  const missingParamsMap = apiData?.missing_required_parameters || {};
  const missingParams = Object.keys(missingParamsMap);
  const [paramValues, setParamValues] = useState<Record<string, string>>({});


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!uploadedFiles || !uploadConfig) {
      toast.error("No files found. Please upload files again.");
      return;
    }

    // Check if we have ASL files
    if (!uploadedFiles.asl_files || uploadedFiles.asl_files.length === 0) {
      toast.error("No ASL files found. Please upload files again.");
      return;
    }

    const filledParams = Object.fromEntries(
      Object.entries(paramValues).filter(
        ([k, v]) => v && missingParams.includes(k)
      )
    );

    // Convert string values to appropriate types
    const convertedParams = Object.fromEntries(
      Object.entries(filledParams).map(([key, value]) => {
        // Try to convert to number if it looks like a number
        const numValue = Number(value);
        if (!isNaN(numValue) && value.trim() !== "") {
          // Check if it's an integer or float
          return [
            key,
            value.includes(".") ? parseFloat(value) : parseInt(value, 10),
          ];
        }

        // Check if it's a JSON array string
        if (value.trim().startsWith("[") && value.trim().endsWith("]")) {
          try {
            const arrayValue = JSON.parse(value);
            if (Array.isArray(arrayValue)) {
              // Convert array elements to numbers if possible
              return [
                key,
                arrayValue.map((item) => {
                  const num = Number(item);
                  return !isNaN(num) ? num : item;
                }),
              ];
            }
          } catch {
            // If parsing fails, keep as string
          }
        }

        return [key, value];
      })
    );

    console.log("Missing params:", missingParams);
    console.log("Filled params:", filledParams);
    console.log("Converted params:", convertedParams);
    console.log("Upload config:", uploadConfig);
    console.log("Uploaded files structure:", uploadedFiles);

    setIsLoading(true);

    try {
      // Update ASL JSON file with missing parameters
      const updatedAslFiles = await Promise.all(
        uploadedFiles.asl_files.map(async (file) => {
          if (file.name.endsWith(ASLRelevantFileNames.ASL_JSON)) {
            console.log("Found ASL JSON file:", file.name);
            return new Promise<File>((resolve) => {
              const reader = new FileReader();
              reader.onload = (e) => {
                try {
                  const jsonContent = JSON.parse(e.target?.result as string);
                  console.log("Original JSON content:", jsonContent);

                  // Use the converted parameters instead of raw string values
                  const updatedContent = { ...jsonContent, ...convertedParams };
                  console.log("Updated JSON content:", updatedContent);

                  // Store the updated JSON content in context for download
                  setUpdatedJsonContent(updatedContent);
                  setUpdatedJsonFilename(file.name);

                  const updatedBlob = new Blob(
                    [JSON.stringify(updatedContent, null, 2)],
                    {
                      type: "application/json",
                    }
                  );

                  const updatedFile = new File([updatedBlob], file.name, {
                    type: "application/json",
                    lastModified: Date.now(),
                  });

                  resolve(updatedFile);
                } catch (error) {
                  console.error("Error parsing JSON:", error);
                  resolve(file);
                }
              };
              reader.readAsText(file);
            });
          }
          return file;
        })
      );

      // ...existing code for FormData creation and API call...

      // Create updated files structure
      const updatedFiles = {
        nifti_file: uploadedFiles.nifti_file,
        asl_files: updatedAslFiles,
        dicom_files: uploadedFiles.dicom_files || [],
      };

      // Prepare FormData for re-upload
      const formData = new FormData();

      // Add NIfTI file if present
      if (updatedFiles.nifti_file) {
        formData.append("nifti_file", updatedFiles.nifti_file);
      }

      // Add DICOM files if present
      if (updatedFiles.dicom_files && updatedFiles.dicom_files.length > 0) {
        updatedFiles.dicom_files.forEach((file) => {
          formData.append("dcm_files", file);
        });
      }

      // Add ASL files
      updatedFiles.asl_files.forEach((file) => {
        formData.append("files", file);
        formData.append("filenames", file.name);
      });

      formData.append("modality", uploadConfig.modalityType);
      formData.append("files_type", uploadConfig.fileType);

      console.log("FormData entries:");
      for (const [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(key, `File: ${value.name} (${value.size} bytes)`);
        } else {
          console.log(key, value);
        }
      }

      console.log("Uploaded formdata structure:", formData.entries());

      const data = await getReport(formData, uploadConfig.fileType.toLocaleLowerCase());
      setIsLoading(false);

      if (data) {
        setApiData(data);
        console.log("New API response:", data);

        // Check if there are still missing parameters
        if (
          data.missing_required_parameters &&
          Object.keys(data.missing_required_parameters).length > 0
        ) {
          const list = Object.entries(data.missing_required_parameters)
            .map(([param, unit]) => (unit && unit !== '-' ? `${param} (${unit})` : param))
            .join(', ');
          toast.info(`Some parameters are still missing: ${list}`);
        } else {
          toast.success(
            "Report regenerated successfully with updated parameters!"
          );
        }
      } else {
        toast.error("Failed to regenerate report. Please try again.");
      }
    } catch (error: unknown) {
      setIsLoading(false);
      console.error("Full error details:", error);

      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as {
          response: {
            data?: { detail?: string; message?: string };
            status: number;
          };
        };
        console.error("Response data:", axiosError.response.data);
        console.error("Response status:", axiosError.response.status);

        if (axiosError.response.data?.detail) {
          toast.error(`Server error: ${axiosError.response.data.detail}`);
        } else if (axiosError.response.data?.message) {
          toast.error(`Server error: ${axiosError.response.data.message}`);
        } else {
          toast.error(
            `Server error (${axiosError.response.status}): Please check the server logs`
          );
        }
      } else {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";
        toast.error(
          `An error occurred while updating parameters: ${errorMessage}`
        );
      }
    }
  };

  if (!missingParams.length) {
    return (
      <Card className="h-full p-2 bg-gray-50 dark:bg-secondary flex items-center justify-center text-muted-foreground">
        No missing parameters!
      </Card>
    );
  }

  return (
    <Card className="h-full p-2 bg-gray-50 dark:bg-secondary flex flex-col justify-between">
      <div>
        <h3 className="font-semibold mb-2 text-base">Missing Parameters</h3>
        <p className="text-sm text-muted-foreground mb-2">
          Fill in the missing parameters to regenerate the report:
        </p>
        <ul className="flex flex-col gap-1 max-h-48 overflow-y-auto pr-1 mb-2">
          {missingParams.map((param) => {
            const unit = missingParamsMap[param] || '-';
            const filled = paramValues[param] && paramValues[param].trim();
            return (
              <li
                key={param}
                className="flex justify-between items-center gap-2 p-1 rounded bg-white dark:bg-muted/30 border border-muted/30"
              >
                <div className="flex items-center gap-2">
                  {filled ? (
                    <Check className="text-green-600 w-4 h-4" />
                  ) : (
                    <AlertCircle className="text-red-500 w-4 h-4" />
                  )}
                  <span className="font-medium w-48 truncate" title={param}>
                    {param}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Input
                    className="border-none px-1 py-0 h-7 text-sm focus:ring-0 focus-visible:ring-0 focus:border-none focus:outline-none shadow-none max-w-52 text-left"
                    style={{ minWidth: 0 }}
                    placeholder="Enter value"
                    value={paramValues[param] || ""}
                    onChange={(e) =>
                      setParamValues((prev) => ({
                        ...prev,
                        [param]: e.target.value,
                      }))
                    }
                  />
                  <span className="text-xs text-muted-foreground w-10 text-right" title={unit}>
                    {unit}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
      <form className="flex flex-col gap-2 mt-2" onSubmit={handleSubmit}>
        <Button
          type="submit"
          disabled={missingParams.some(
            (param) => !(paramValues[param] && paramValues[param].trim())
          )}
          className="w-full mt-auto"
        >
          Regenerate Report with Parameters (
          {
            Object.keys(paramValues).filter(
              (k) => paramValues[k] && paramValues[k].trim()
            ).length
          }
          /{missingParams.length})
        </Button>
      </form>
    </Card>
  );
}
