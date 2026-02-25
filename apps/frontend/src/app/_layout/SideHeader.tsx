"use client";

import {Button} from "@/components/ui/button"
import {Separator} from "@/components/ui/separator"
import {SidebarTrigger} from "@/components/ui/sidebar"
import { IconBrandGithub, IconFileTypeDoc, IconBriefcase2, IconFileTypeJs } from '@tabler/icons-react';
import ThemeToggle from "@/app/_layout/ThemeToggle"
import { getReportPdf, downloadUpdatedJson } from "@/services/apiReport";
import { useAppContext } from "@/providers/AppProvider";

const SiteHeader = () => {

    const { apiData, updatedJsonContent, updatedJsonFilename } = useAppContext();


    const handlePdfDownload = () => {

        const reportData = {
            basic_report: apiData?.basic_report,
            extended_report: apiData?.extended_report,
            asl_parameters: apiData?.asl_parameters || {},
            missing_parameters: apiData?.missing_required_parameters || []
        }

        getReportPdf(reportData)
    }

    const handleJsonDownload = () => {
        if (updatedJsonContent) {
            downloadUpdatedJson(updatedJsonContent, updatedJsonFilename);
        }
    }

    return (
        <header
            className="flex h-(--header-height) shrink-0 items-center gap-2 border-b transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-(--header-height)">
            <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
                <SidebarTrigger className="-ml-1"/>
                <Separator
                    orientation="vertical"
                    className="mx-2 data-[orientation=vertical]:h-4"
                />
                <h1 className="text-base font-medium">OSIPI ASL Reporting Tool</h1>
                <div className="ml-auto flex items-center gap-2">

                    {updatedJsonContent && (
                        <Button variant="ghost" asChild size="sm" className="hidden sm:flex hover:cursor-pointer" onClick={handleJsonDownload}>
                            <span>
                                <IconFileTypeJs />
                                Download Updated JSON
                            </span>
                        </Button>
                    )}

                    {apiData?.basic_report && (
                        <Button variant="ghost" asChild size="sm" className="hidden sm:flex hover:cursor-pointer" onClick={handlePdfDownload}>
                           <span>
                                <IconFileTypeDoc />
                                Download PDF Report
                           </span>
                        </Button>
                    )}

                    

                    <ThemeToggle/>

                    <Button variant="ghost" asChild size="sm" className="hidden sm:flex">

                        <a
                            href="https://docs.page/1brahimmohamed/ASL-Parameter-Generator"
                            rel="noopener noreferrer"
                            target="_blank"
                            className="dark:text-foreground"
                        >
                            <IconBriefcase2 />
                            Documentation
                        </a>
                    </Button>


                    <Button variant="ghost" asChild size="sm" className="hidden sm:flex">

                        <a
                            href="https://github.com/1brahimmohamed/ASL-Parameter-Generator"
                            rel="noopener noreferrer"
                            target="_blank"
                            className="dark:text-foreground"
                        >
                            <IconBrandGithub/>
                            GitHub
                        </a>
                    </Button>
                </div>
            </div>
        </header>
    )
}

export default SiteHeader
