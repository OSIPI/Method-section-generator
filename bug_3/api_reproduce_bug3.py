import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'package', 'src'))

from pyaslreport.modalities.asl.processor import ASLProcessor

# Create a payload mimicking what the JSON endpoint receives
payload = {
    "InversionTime": 1.5,
    "InitialPostLabelDelay": 2000.0,
    "RepetitionTime": 4000.0,
    "MagneticFieldStrength": 3.0,
    "MRAcquisitionType": "3D",
    "Manufacturer": "Generic"
}

# The endpoint uses ASLProcessor to normalize the data
# We initialize it bypassing the extensive initialization for a clean test
proc = object.__new__(ASLProcessor)

# Run the method that has Bug 3
proc._rename_fields(payload)

print("API/PROCESSOR NORMALIZED JSON OUTPUT:")
print(json.dumps(payload, indent=2))

pld = payload.get("PostLabelingDelay")
if pld == 2000.0:
    print("\n>> VERDICT: Bug is PRESENT. PlD is 2000.0, InversionTime (1.5) was silently overwritten.")
else:
    print(f"\n>> VERDICT: Bug is FIXED. PlD is {pld}.")
