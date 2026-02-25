import {ASLRelevantFileNames} from '@/enums';

/**
 * Finds a file in the given folder items by its name.
 * @param folderItems
 * @param fileName
 */
const findFileInFolder = (folderItems: File[], fileName: string) => {
    return folderItems.find(item => item.name.endsWith(fileName));
};


/**
 * Finds relevant files from the provided items based on specific criteria.
 * It looks for files in the 'perf' folder with names ending in '_asl.json',
 * and also checks for related '_m0scan.json' and '_aslcontext.tsv' files.
 *
 * @param files - An array of File objects to search through.
 * @returns {Array} - An array of relevant file items.
 */
const findRelevantFiles = (files: File[]): File[] => {
    const relevantFiles = [];

    for (const file of files) {
        const relativePath = file.webkitRelativePath;
        const pathParts = relativePath.split('/');
        const parentFolder = pathParts[pathParts.length - 2];

        if (parentFolder === 'perf' && file.name.endsWith(ASLRelevantFileNames.ASL_JSON)) {
            relevantFiles.push(file);

            // Extract the base name before '_asl.json'
            const baseName = file.name.replace(`_${ASLRelevantFileNames.ASL_JSON}`, '');

            // Find related files in the same folder
            const folderItems = files.filter(i => i.webkitRelativePath.startsWith(relativePath.replace(/[^/]+$/, '')));

            // Check if the base name matches the '_run-*' pattern
            const runPatternMatch = baseName.match(/_run-\d+$/);

            if (runPatternMatch) {
                const m0ScanFile = findFileInFolder(folderItems, `${baseName}_${ASLRelevantFileNames.M0_SCAN_JSON}`);
                const aslContextFile = findFileInFolder(folderItems, `${baseName}_${ASLRelevantFileNames.ASL_CONTEXT_TSV}`);

                if (m0ScanFile) {
                    relevantFiles.push(m0ScanFile); // Push _run-*_m0scan.json if it exists
                }
                if (aslContextFile) {
                    relevantFiles.push(aslContextFile); // Push _run-*_aslcontext.tsv if it exists
                }

            } else {
                const m0ScanFile = findFileInFolder(folderItems, ASLRelevantFileNames.M0_SCAN_JSON);
                const aslContextFile = findFileInFolder(folderItems, ASLRelevantFileNames.ASL_CONTEXT_TSV);

                if (m0ScanFile) {
                    relevantFiles.push(m0ScanFile);
                }
                if (aslContextFile) {
                    relevantFiles.push(aslContextFile);
                }
            }
        }
    }

    return relevantFiles;
};


/**
 * Finds the first .nii.gz or .nii file in the 'perf' folder from the provided items.
 * It checks for files with names ending in 'asl.nii.gz' or 'asl.nii'.
 * @param items
 */
const findNiftiFile = (items: File[]) => {
    for (const item of items) {
        const relativePath = item.webkitRelativePath
        const pathParts = relativePath.split('/');
        const parentFolder = pathParts[pathParts.length - 2];

        if (parentFolder === 'perf' &&
            (item.name.endsWith('asl.nii.gz') || item.name.endsWith('asl.nii'))) {
            return item; // Return the first found .nii.gz or .nii file
        }
    }
    return null;
};

export {
    findFileInFolder,
    findRelevantFiles,
    findNiftiFile
};