/**
 * Maps ASL parameters to a table format.
 * @param aslParameters
 * @returns An array of objects representing the ASL parameters in table format.
 */
function mapAslParametersToTable(aslParameters: [string, string | number][]) {
    return aslParameters.map(([parameter, value], index) => ({
        id: (index + 1).toString(),
        parameter,
        value: value === null ? "missing" : value.toString(),
    }));
}

export {
    mapAslParametersToTable
}