from src.Simulation.solver import Solver
import argparse
import toml
import os
import logging


class TomlProcessor:
    """
    Processes TOML configuration files for the simulation.

    This class provides methods to read, validate, and process TOML files.
    It also manages batch processing of multiple files and
    handles logging setup.
    """

    def __init__(self):
        """
        Initializes the TomlProcessor.

        Ensures the logs directory exists for storing log files.
        """
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)

    def setup_logging(self, config=None):
        """
        Configures logging for the simulation.

        Parameters:
            config (dict, optional):
            Configuration dictionary containing logging information.
                                    If None, defaults to "logfile".
        """
        log_name = "logfile"  # Default log name
        if config:
            log_name = config.get("IO", {}).get("logName", log_name)

        log_file = os.path.join(self.log_dir, f"{log_name}.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file)]
        )

    def read_toml_file(self, filename):
        """
        Reads and validates a TOML configuration file.

        Parameters:
            filename (str): Path to the TOML file.

        Returns:
            dict: Parsed configuration data.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the TOML file is invalid or missing required keys.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} does not exist")

        required_structure = {
            "settings": ["nSteps", "tStart", "tEnd"],
            "geometry": ["meshName", "borders"],
            "IO": ["logName", "restartFile"]
        }

        try:
            with open(filename, "r") as file:
                config = toml.load(file)
        except toml.TOMLDecodeError as e:
            raise ValueError(f"Error while reading {filename}: {e}")

        for section, keys in required_structure.items():
            if section not in config:
                raise ValueError(f"Missing section: '{section}' in {filename}")
            for key in keys:
                if key not in config[section]:
                    raise ValueError(f"Missing key: '{section}.{key}' in {filename}")

        # Validate and adjust `nSteps`
        nSteps = config["settings"].get("nSteps", 0)
        if nSteps < 100:
            print(f"Warning: 'nSteps' in {filename} is too low ({nSteps}), simulation may be inaccurate.")
            logging.info(f"'nSteps' in {filename} is too low ({nSteps}), simulation may be inaccurate.")
        elif nSteps > 500:
            print(f"Warning: 'nSteps' in {filename} exceeds the limit ({nSteps}), simulation takes too long. Adjusting to 500.")
            logging.info(f"'nSteps' in {filename} exceeds the limit ({nSteps}), simulation takes too long. Adjusting to 500.")
            config["settings"]["nSteps"] = 500

        config["IO"]["writeFrequency"] = config["IO"].get("writeFrequency", -1)
        if not config["IO"].get("logName"):
            config["IO"]["logName"] = "logfile"

        return config
      
    def process_single_file(self, file_path):
        """
        Processes a single TOML file and runs the simulation.

        Parameters:
            file_path (str): Path to the TOML file.

        Raises:
            Exception: If there is an error during simulation processing.
        """
        try:
            config = self.read_toml_file(file_path)
            print(f"Starting simulation for {file_path}...")
            logging.info(f"Processing {file_path}")

            config_name = os.path.basename(file_path)
            solver = Solver(config)
            solver.run_simulation(config_name=config_name)

            print(f"Simulation for {file_path} completed successfully.")
            logging.info(f"Simulation for {file_path} completed successfully.")
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            print(f"Error processing {file_path}: {e}")

    def process_multiple_files(self, folder="user_data"):
        """
        Processes all TOML files in a specified folder.

        Parameters:
            folder (str): Directory containing TOML files (default: "user_data").

        Raises:
            Exception: If an error occurs during batch processing.
        """
        print(f"Finding all TOML files in folder: {folder}...")
        if not os.path.exists(folder):
            print(f"Error: Folder '{folder}' does not exist.")
            return

        toml_files = [f for f in os.listdir(folder) if f.endswith(".toml")]
        if not toml_files:
            print(f"No TOML files found in folder '{folder}'.")
            return

        print(f"Found {len(toml_files)} TOML file(s) in folder '{folder}'.")
        for idx, tom_file in enumerate(toml_files, start=1):
            file_path = os.path.join(folder, tom_file)
            print(f"[{idx}/{len(toml_files)}] Processing {tom_file}...")
            self.process_single_file(file_path)


def parse_input():
    """
    Parse command-line arguments for the simulation.
    """
    parser = argparse.ArgumentParser(description="Run simulation")
    parser.add_argument("-c", "--config_file", help="Input a specific config file (e.g., example.toml)")
    parser.add_argument("-f", "--folder", help="Specify a folder containing config files")
    parser.add_argument("--find_all", action="store_true", help="Find and process all TOML files")
    return parser.parse_args()


def main():
    """
    Main function to run the simulation based on user input.
    """
    args = parse_input()
    processor = TomlProcessor()

    # Default behavior for no arguments
    if not args.config_file and not args.folder and not args.find_all:
        print("No specific input provided. Using default: user_data/input.toml")
        config = processor.read_toml_file("user_data/input.toml")
        processor.setup_logging(config=config)
        print("Starting simulation process...")
        processor.process_single_file("user_data/input.toml")
        print("Simulation process complete.")
        return

    # Single file processing
    if args.config_file:
        print(f"Processing single configuration file: {args.config_file}")
        config = processor.read_toml_file(args.config_file)
        processor.setup_logging(config=config)
        print("Starting simulation...")
        processor.process_single_file(args.config_file)
        print("Simulation complete.")
        return

    # Handle `--find_all` or files in a specific folder (`-f`)
    folder = args.folder or "user_data"
    if args.find_all:
        print(f"Finding all TOML files in folder: {folder}")
        mock_config = {"IO": {"logName": "find_all_simulation"}}  # Mock config for logging
        processor.setup_logging(config=mock_config)
        processor.process_multiple_files(folder=folder)
        print("Simulation process complete.")
    elif args.folder:
        print(f"Processing all TOML files in specified folder: {folder}")
        mock_config = {"IO": {"logName": "folder_simulation"}}  # Mock config for logging
        processor.setup_logging(config=mock_config)
        processor.process_multiple_files(folder=folder)
        print("Simulation process complete.")


if __name__ == "__main__":
    main()
