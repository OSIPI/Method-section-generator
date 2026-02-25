"use client";

import ErrorsCard from "@/app/report/errors/_components/ErrorsCard";
import {useAppContext} from "@/providers/AppProvider";

// Helper to flatten error objects to string array
function flattenErrors(obj: unknown): string[] {
    if (!obj) return [];
    if (Array.isArray(obj)) {
        return obj.flatMap(flattenErrors);
    }
    if (typeof obj === 'string') {
        return [obj];
    }
    if (typeof obj === 'object') {
        // For objects like {field: [error1, error2]}
        return Object.entries(obj as Record<string, unknown>).flatMap(([key, val]) => {
            if (Array.isArray(val)) {
                return val.map(v => `${key}: ${typeof v === 'string' ? v : JSON.stringify(v)}`);
            } else if (typeof val === 'string') {
                return [`${key}: ${val}`];
            } else {
                return [`${key}: ${JSON.stringify(val)}`];
            }
        });
    }
    return [];
}

const Page = () => {
    const {apiData} = useAppContext();

    // Prepare error arrays for each card
    const m0ConciseErrors = apiData.m0_concise_error ? [apiData.m0_concise_error] : [];
    const errorsConcise = flattenErrors(apiData.errors_concise);
    const majorErrors = flattenErrors(apiData.major_errors);
    const majorErrorsConcise = flattenErrors(apiData.major_errors_concise);

    // If all are empty, show NoErrors
    if (
        m0ConciseErrors.length === 0 &&
        errorsConcise.length === 0 &&
        majorErrors.length === 0 &&
        majorErrorsConcise.length === 0
    ) {
        return <NoErrors/>;
    }

    return (
        <div className="flex flex-col gap-4 h-full w-full p-5">
            <div className={"grid grid-cols-2 gap-4 h-full w-full"}>
                <ErrorsCard errors={m0ConciseErrors} title="M0 Concise Errors"/>
                <ErrorsCard errors={errorsConcise} title="Errors Concise"/>
                <ErrorsCard errors={majorErrors} title="Major Errors"/>
                <ErrorsCard errors={majorErrorsConcise} title="Major Errors Concise"/>
            </div>
        </div>
    );
}

const NoErrors = () => {
    return (
        <div className="flex flex-col items-center justify-center h-full">
            <h1 className="text-2xl font-bold mb-4">Errors</h1>
            <p className="text-gray-600">No errors found.</p>
        </div>
    );
}

export default Page;