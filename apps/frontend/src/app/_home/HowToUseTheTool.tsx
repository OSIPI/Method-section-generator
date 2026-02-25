import React from "react";

const HowToUseTheTool = () => {
    return (
        <section aria-labelledby="how-to-use-title">
            <h2 id="how-to-use-title" className="font-semibold text-lg">How to Use the Tool</h2>
            <p className="font-semibold mt-2">Steps:</p>
            <ol>
                <li className="mt-1">
                    Click the <strong>Choose Folder</strong> button and select the BIDS or DICOM folder containing your ASL
                    data.
                </li>
                <li className="mt-1">
                    The application will process your files and display the results below.
                </li>
                <li className="mt-1">
                   For uploaded DICOM files, the application will convert them to BIDS format and process them.
                </li>
                <li className="mt-1">
                    For BIDS the <code>xxx_asl.json</code> and <code>xxx_asl.nii</code> or <code>xxx_asl.nii.gz</code> files will be processed.
                </li>
            </ol>
            <p className="mt-1">
                <strong>Note:</strong> The following specific checks and summaries will be reported:
            </p>
            <ul className="list-disc pl-6 mt-1 space-y-1 text-sm">
                <li>
                    <strong>Inconsistency Check:</strong> Discrepancies between values across different sessions,
                    such as variations in PLD, labeling duration, echo time, and voxel sizes.
                </li>
                <li>
                    <strong>Invalid Values Check:</strong> Identifying values that do not meet predefined criteria,
                    such as incorrect numeric ranges, boolean values, and string values.
                </li>
                <li>
                    <strong>Slight Variation Warning:</strong> Highlighting values that might not constitute a major
                    error but are worth noting.
                </li>
                <li>
                    <strong>Generated Report:</strong> The software generates an ASL parameter report to be included
                    in the Methods section of paper.
                </li>
            </ul>
            <h3 className="mt-3 font-semibold text-base">Acknowledgments</h3>
            <p className="mt-1">
                This project has been developed under the mentorship and supervision of Jan Petr, David Thomas, and
                the OSIPI TF 4.1 ASL Lexicon. As Part of Google Summer of Code 2024 and 2025 by Hanliang Xu and Ibrahim Abdelazim.
                Their guidance and support have been invaluable throughout the development process.
            </p>
        </section>
    )
}

export default HowToUseTheTool;