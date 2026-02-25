import {Button} from "@/components/ui/button";
import Link from "next/link";
import React from "react";

const WhatIsThisTool = () => {
    return (
        <section aria-labelledby="what-is-this-tool-title" className="flex flex-col gap-2">

            <h2 id="what-is-this-tool-title" className="font-semibold text-lg">What is this tool?</h2>
            <p>
                This application allows you to generate an ASL parameter report to be copied into the Methods section of
                paper.
                The program will validate the ASL datasets by checking for inconsistencies, invalid values, and providing
                warnings for slight variations.
                Please ensure that your dataset is organized according to the BIDS standard before uploading or you can
                upload DICOM files and the program will convert them.
            </p>

            <div className="flex flex-col gap-2">
                <p className="mt-3">
                    Here are some sample folders for you to download and test:
                </p>
                <Button className="w-fit hover:cursor-pointer" aria-label="Download sample BDIS data">
                    <Link href="https://drive.google.com/drive/folders/1NuG_ofLbaLYswNlBN2aRDkxLOucYFQfg"
                          target="_blank" rel="noopener noreferrer">
                        Sample ASL BDIS data
                    </Link>
                </Button>
            </div>

        </section>
    )
}

export default WhatIsThisTool;