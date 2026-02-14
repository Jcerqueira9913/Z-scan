# OptoSigma Stage & LeCroy Scope Automation Tool

This repository contains a Python-based Graphical User Interface (GUI) designed to automate linear scans for laboratory experiments. It integrates **OptoSigma** motorized stage controllers with **LeCroy** digital oscilloscopes to perform precise spatial measurements and high-fidelity data acquisition.

## 📋 Overview

The application automates the "Move-Measure-Save" cycle. It commands the motorized stage to specific positions and, at each step, captures raw waveforms from the oscilloscope, converting binary data into human-readable physical units (Volts and Seconds).

## 🚀 Key Features

* **Modern GUI**: Built with `CustomTkinter` for a responsive, dark-themed user experience.
* **Hardware Abstraction**:
* **OptoSigma GSC01**: Full motion control including speed adjustment, relative movement, and origin management.
* **LeCroy Oscilloscopes**: Uses VISA (PyVISA) to communicate and extract high-resolution 16-bit waveform data.


* **Smart Data Conversion**: Automatically parses the LeCroy `WAVEDESC` header (via `INSPECT` commands) to apply correct vertical gain, offset, and horizontal scaling.
* **Multithreaded Execution**: The scanning logic runs in a background thread, ensuring the UI remains responsive during long experiments.
* **Bidirectional Scanning**: Supports optional data collection during the return trip (Backward Scan) to check for hysteresis or reproducibility.

## 📊 User Interface

Below is a screenshot of the control panel:
![Screenshot da UI](assets/screenshot.png)
## 🛠️ Requirements & Installation

### Hardware

* **OptoSigma** GSC-01 Series Controller.
* **LeCroy** Oscilloscope with remote control support (tested via USB-VISA).
* **Linux/Windows** PC with NI-VISA or `pyvisa-py` installed.

### Software Dependencies

Install the required Python packages:

```bash
pip install customtkinter pyvisa optosigma

```

## ⚙️ How It Works

### Waveform Processing

The script forces the oscilloscope into a specific binary state to ensure data integrity:

1. **Stop Acquisition**: Freezes the trigger to synchronize Channel 1 and Channel 2.
2. **Binary Format**: Sets `COMM_FORMAT DEF9, WORD, BIN` for 16-bit precision.
3. **Scaling**: Calculations follow the LeCroy standard:



### Scan Workflow

1. **Connect**: Select the VISA resource for the scope and the serial port for the stage.
2. **Calibration**: Manually jog the stage and set your "Logical Zero."
3. **Parameter Entry**: Define total distance (mm), step size (mm), and measurements per step.
4. **Acquisition**: Click **START SCAN**. Data is saved as `forward-X_meas_Y_channel_Z.csv`.

## ⚠️ Technical Notes

* **Regex Parsing**: The script uses Regular Expressions to clean the scope's response when querying metadata, ensuring compatibility with various LeCroy firmware versions.
* **Safety**: Ensure the stage has clear travel paths; the script assumes the user has verified physical limits before starting a long-distance scan.

---

**Author:** Jcerqueira9913 (Owner of Topbar Ubuntu Project)

**Context:** Developed for Nonlinear Optics and Z-Scan Experimental Automation.
