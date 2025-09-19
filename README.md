# Oil Spill Simulation
Numerical modeling of oil dispersion in coastal waters.

## Description
This project simulates the dispersion of oil in a fictional coastal town, "Bay City." The model predicts oil movement over time, evaluates environmental impacts, and aids in mitigation planning. By leveraging computational algorithms, the simulation avoids the limitations and costs of physical experiments.

## Features
- Simulates oil spill dispersion in a coastal environment.
- Configurable parameters through TOML files.
- Logs detailed summaries, including oil distribution over time.
- Generates plots and optional video outputs of oil dispersion.
- Supports restart functionality for simulations.
- Handles error checking for configuration consistency.

## Installation
1. Extract the zipped project files to a folder on your system.
2. Open a terminal and navigate to the project folder (where the main.py file is located).
3. Install dependencies by running the following command:
   ```bash
   pip install -r requirements.txt

## User Guide
To run the simulation, follow these steps:
1. *Install Dependencies*: Ensure all necessary dependencies are installed.
2. *Prepare Configuration Files*:
   - Create or use an existing TOML configuration file to specify simulation parameters. Refer to the documentation for structure.
   - Run a specific configuration file: python main.py -c <foldername>/<filename>.toml
   - Process all TOML files in a folder: python main.py --find_all
   - By default, the program looks in the user_data folder. To use a different folder: python main.py -f <folder_name>
3. *Run the Simulation*:
   - Run the simulation with parameters from the TOML file: python main.py
   - If no file is specified, the program defaults to input.toml.
4. *Restart Functionality*:
   - Resume a simulation using the restartFile and start_time parameters in the TOML file.
   - Ensure both are specified to enable restart functionality.
5. *Output and Visualization*:
   - Generates plots of the oil distribution at the final time.
   - Optional parameter writeFrequency creates a video of the oil distribution over time.
   - Stores results in a folder named after the corresponding configuration file.
6. *Error Handling*:
   - Validates the TOML file for consistency. Errors are logged if issues are detected.
7. *Simulation Summary*:
   - Logs parameters and oil quantities in fishing grounds over time. Logs are stored in a file named logfile (default) or as specified in the configuration.

## Authors
- Iftikhar Amiri (iftikhar.amiri@nmbu.no)
- Magnus Vaslag Løvøy (magnus.vaslag.lovoy@nmbu.no)
- Tom-Christian Armes (tom-christian.armes@nmbu.no)