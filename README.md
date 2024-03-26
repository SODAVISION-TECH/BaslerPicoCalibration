# Basler Camera Color Calibration

This Python project serves as a comprehensive solution for calibrating Basler color cameras, particularly catering to the needs of applications with smaller field-of-view requirements. Traditionally, Basler color calibration has been limited to 24-color charts with a minimum size of 50mm x 70mm, which poses challenges for industries requiring finer color calibration in smaller areas, such as 2mm x 2mm micro-applications.

![image](https://github.com/SODAVISION-TECH/Color-Calibration-for-Basler-Camera/assets/22335180/eb963d62-374c-49af-80c5-b1e6c20719f9)

This project addresses these limitations by introducing support for the Pico Color Gauge Target, an ultra-compact calibration target measuring just 1.58mm x 1.58mm. By leveraging this target, the software captures high-resolution images using Basler cameras, allowing for precise calibration adjustments based on individual color patches. These adjustments are made by fine-tuning Basler camera parameters to match reference values stored in a reference file. This seamless integration with Basler color calibrator tools ensures accurate color calibration even in the most demanding applications.

## Key Features

- Capture Images: Utilize Basler cameras to capture images of the Pico Color Gauge Target.
- Extract Color Patches: Automatically extract individual color patches from the captured images.
- Calibrate Color Parameters: Fine-tune Basler color camera parameters using the Basler Pylon API to achieve accurate color reproduction.
- DeltaE Calculation: Calculate DeltaE values to quantify the color difference between reference LAB values and calibrated LAB values, providing insights into color accuracy and consistency.

## Calibration Procedure

1. Reset to Default Settings: Begin by resetting the camera color settings to default values to ensure a consistent starting point.
2. Monochrome Calibration: Calibrate the camera in monochrome space, referencing the grey color patch. The reference grey value should typically range between 200 to 230.
3. Collect Raw Images: Capture raw images of the Pico Color Gauge Target to facilitate Color Correction Matrix (CCM) calculation.
4. Patch-by-Patch Calibration: Calibrate the Basler camera by analyzing individual color patches on the calibration target, adjusting color parameters accordingly.
5. DeltaE Calculation: Calculate DeltaE values to assess color accuracy and consistency between reference LAB values and calibrated LAB values.

## Additional Information
For detailed instructions on setting up and running the calibration process, refer to the project documentation included in the repository. You can also explore the codebase to understand the implementation details and customize the calibration process to suit specific requirements.
