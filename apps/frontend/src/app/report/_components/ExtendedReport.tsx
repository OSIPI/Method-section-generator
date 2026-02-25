"use client";

import {useEffect, useState} from "react";
import {useAppContext} from "@/providers/AppProvider";
import GeneratedMethods from "@/app/report/_components/GeneratedMethods";

const ExtendedReport = () => {
    const [text, setText] = useState("");
    const {apiData} = useAppContext();


    useEffect(() => {
        if (apiData && apiData.extended_report) {
            setText(apiData.extended_report);
        }
    }, [apiData]);


    return (
        <GeneratedMethods text={text} type="extended" />
    )

}

export default ExtendedReport;