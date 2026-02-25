"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import IReportApiResponse from "@/types/ReportResponseType";
import { IAllRelevantFilesType } from "@/types";

type AppContextType = {
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  apiData: IReportApiResponse;
  setApiData: (data: IReportApiResponse) => void;
  clearApiData: () => void;
  uploadedFiles: IAllRelevantFilesType;
  setUploadedFiles: (files: IAllRelevantFilesType) => void;
  uploadConfig: { modalityType: string; fileType: string } | null;
  setUploadConfig: (
    config: { modalityType: string; fileType: string } | null
  ) => void;
  updatedJsonContent: Record<string, unknown> | null;
  setUpdatedJsonContent: (content: Record<string, unknown> | null) => void;
  updatedJsonFilename: string;
  setUpdatedJsonFilename: (filename: string) => void;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [apiData, setApiDataState] = useState<IReportApiResponse>(
    {} as IReportApiResponse
  );
  const [uploadedFiles, setUploadedFiles] = useState<IAllRelevantFilesType>(
    {} as IAllRelevantFilesType
  );
  const [uploadConfig, setUploadConfig] = useState<{
    modalityType: string;
    fileType: string;
  } | null>(null);
  const [updatedJsonContent, setUpdatedJsonContent] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [updatedJsonFilename, setUpdatedJsonFilename] = useState<string>("");

  // Function to set new API data
  const setApiData = (data: IReportApiResponse) => {
    setApiDataState(data);
  };

  // Function to clear API data
  const clearApiData = () => {
    setApiDataState({} as IReportApiResponse);
    setUpdatedJsonContent(null);
    setUpdatedJsonFilename("");
  };

  return (
    <AppContext.Provider
      value={{
        isLoading,
        setIsLoading,
        apiData,
        setApiData,
        clearApiData,
        uploadedFiles,
        setUploadedFiles,
        uploadConfig,
        setUploadConfig,
        updatedJsonContent,
        setUpdatedJsonContent,
        updatedJsonFilename,
        setUpdatedJsonFilename,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useAppContext must be used within a AppProvider");
  }
  return context;
};
