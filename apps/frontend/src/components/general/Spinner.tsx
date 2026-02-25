"use client";

import React from 'react';
import RiseLoader from 'react-spinners/RiseLoader';
import {useAppContext} from "@/providers/AppProvider";

const Spinner: React.FC = () => {

    // use the custom hook to access the loading state
    const {isLoading} = useAppContext();

    if (!isLoading) {
        // If not loading, do not render the spinner
        return null;
    }

    return (
        <>
            {/* Semi-transparent background overlay */}
            <div className="fixed inset-0 bg-black opacity-20 z-[1000]"></div>
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[1001]">
                <RiseLoader size="20px" color="#19305CFF" />
            </div>
        </>
    );
};

export default Spinner;