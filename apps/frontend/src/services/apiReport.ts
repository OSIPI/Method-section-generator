import axios from 'axios';
import {IReportApiResponse} from '@/types';


const API_BASE_URL = `${process.env.NEXT_PUBLIC_API_BASE_URL}/report`;

const client = axios.create({
    baseURL: API_BASE_URL,
});

/**
 * Fetches a report based on the provided form data.
 * @param formData - The FormData object containing the files to be processed.
 * @return IReportApiResponse - A promise that resolves to the report data.
 */
const getReport = async (formData: FormData, type: string): Promise<IReportApiResponse> => {
    try {
        const response = await client.post(
            `/process/${type}`,
            formData
        );

        return response.data;
    } catch (error) {
        console.error('Error fetching report:', error);
        throw error;
    }
}

const getReportPdf = async (reportData: Partial<IReportApiResponse>) => {
    try {
        const response = await client.post(
            '/report-pdf',
            { report_data: reportData }, // body data
            { responseType: 'blob' } // config
          );

          const fileURL = window.URL.createObjectURL(new Blob([response.data]));
          const fileLink = document.createElement('a');
          fileLink.href = fileURL;
          fileLink.setAttribute('download', 'report.pdf'); // change filename as needed
          document.body.appendChild(fileLink);
          fileLink.click();
          document.body.removeChild(fileLink);
    } catch (error) {
        console.error('Error getting report PDF:', error);
        throw error;
    }
}

const downloadUpdatedJson = (jsonContent: Record<string, unknown>, filename: string = 'updated_asl_parameters.json') => {
    try {
        const jsonString = JSON.stringify(jsonContent, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const fileURL = window.URL.createObjectURL(blob);
        const fileLink = document.createElement('a');
        fileLink.href = fileURL;
        fileLink.setAttribute('download', filename);
        document.body.appendChild(fileLink);
        fileLink.click();
        document.body.removeChild(fileLink);
        window.URL.revokeObjectURL(fileURL);
    } catch (error) {
        console.error('Error downloading updated JSON:', error);
        throw error;
    }
}

export {
    getReport,
    getReportPdf,
    downloadUpdatedJson,
}