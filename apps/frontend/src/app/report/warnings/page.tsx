"use client";

import {useAppContext} from "@/providers/AppProvider";
import WarningsCard from "@/app/report/warnings/_components/WarningsCard";

// Helper to flatten warning objects to string array
function flattenWarnings(obj: unknown): string[] {
    if (!obj) return [];
    if (Array.isArray(obj)) {
        return obj.flatMap(flattenWarnings);
    }
    if (typeof obj === 'string') {
        return [obj];
    }
    if (typeof obj === 'object') {
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

    const m0ConciseWarnings = apiData.m0_concise_warning ? [apiData.m0_concise_warning] : [];
    const warnings = flattenWarnings(apiData.warnings);
    const warningsConcise = flattenWarnings(apiData.warnings_concise);

    // If all are empty, show NoWarnings
    if (
        m0ConciseWarnings.length === 0 &&
        warnings.length === 0 &&
        warningsConcise.length === 0
    ) {
        return <NoWarnings/>;
    }

    return (
        <div className="flex flex-col gap-4 h-full w-full p-5">
            <div className={"grid grid-cols-3 gap-4 h-full w-full"}>
                <WarningsCard warnings={m0ConciseWarnings} title="M0 Concise Warnings"/>
                <WarningsCard warnings={warningsConcise} title="Warnings Concise"/>
                <WarningsCard warnings={warnings} title="Warnings"/>
            </div>
        </div>
    );
}

const NoWarnings = () => {
    return (
        <div className="flex flex-col items-center justify-center h-full">
            <h1 className="text-2xl font-bold mb-4">Warnings</h1>
            <p className="text-gray-600">No warnings to display.</p>
        </div>
    );
}

export default Page;