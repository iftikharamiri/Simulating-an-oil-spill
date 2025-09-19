import numpy as np
from src.Simulation.mesh import Mesh as Mesh
import logging
import matplotlib.pyplot as plt
import cv2
import os


class Solver:
    def __init__(self, config):
        """
        Initializes the solver and sets up the computational mesh and parameters.

        Parameters:
        - config (dict): Dictionary containing simulation parameters from a TOML file.
        """
        # Load mesh and compute neighbors
        self._meshName = config["geometry"]["meshName"]
        self._mesh = Mesh(self._meshName)
        self._mesh.find_neighbors()

        # Set simulation parameters
        self._xs_point = config["geometry"].get("xs_point", 0.0)
        self._ys_point = config["geometry"].get("ys_point", 0.0)
        self._tStart = config["settings"]["tStart"]
        self._tEnd = config["settings"]["tEnd"]
        self._nt = config["settings"]["nSteps"]
        self._log_name = config["IO"]["logName"]
        self._write_frequency = config["IO"]["writeFrequency"]

        self.dt = (self._tEnd - self._tStart) / float(self._nt)

        # Get fishing area borders
        self.fishing_borders = config["geometry"]["borders"]

        self.image_counter = 0  # Starts at 0 for image filenames

        # Restart logic
        self.restart_file = config["IO"].get("restartFile")
        if self.restart_file:
            self.load_state(self.restart_file)

        logging.info("Solver initialized.")

    def flux_function(self, a, b, n, v):
        """
        Calculate flux between cells based on normal vectors and velocity.

        Parameters:
        - a (float): Value in the current cell.
        - b (float): Value in the neighboring cell.
        - n (array): Normal vector.
        - v (array): Velocity vector.
        """
        angle = np.dot(n, v)
        return a * angle if angle > 0 else b * angle

    def calculate(self):
        """
        Perform one time step for the oil update:
          1. Compute flux for each triangle cell.
          2. Sum flux contributions.
          3. Update cell.oil_value.
        """
        u = [cell.oil_value for cell in self._mesh.cells()]
        u_new = np.zeros_like(u)
        for cell_idx, cell in enumerate(self._mesh.cells()):
            up = 0
            for i, ngh in enumerate(cell.neighbors):
                if ngh < 0:  # Skip boundary cells
                    continue
                normal = cell.normals[i]
                area = cell.area
                velocity = 0.5 * (cell.velocity + self._mesh.cells()[ngh].velocity)
                up -= (self.dt / area) * self.flux_function(u[cell_idx], u[ngh], normal, velocity)
            u_new[cell_idx] = u[cell_idx] + up

        for cell_idx, cell in enumerate(self._mesh.cells()):
            cell.oil_value = u_new[cell_idx]

    def run_simulation(self, config_name):
        """
        Run the simulation process.

        Parameters:
        - config_name (str): Name of the configuration file (used for naming outputs).
        """
        current_time = self._tStart
        interval = max(1, self._nt // self._write_frequency) if self._write_frequency > 0 else -1
        fishing_oil_data = []

        # Check writeFrequency validity
        if self._write_frequency <= 0:
            print("writeFrequency is invalid or not provided. Skipping video recording and image creation.")
            logging.warning("writeFrequency is invalid or not provided. Skipping video recording and image creation.")

        x_min, x_max = self.fishing_borders[0]
        y_min, y_max = self.fishing_borders[1]
        fishing_cells = self._mesh.fishing_cells(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

        logging.info(f"Running simulation for {config_name}.")
        print("Starting simulation...")

        # Skip image creation if writeFrequency <= 0
        if self._write_frequency > 0:
            self.create_image(timestep=0)

        fishing_oil_data.append((current_time, sum(cell.oil_value for cell in fishing_cells)))
        print("Calculating and plotting results...")

        for step in range(1, self._nt + 1):
            self.calculate()
            current_time = self._tStart + step * self.dt
            fishing_oil = sum(cell.oil_value for cell in fishing_cells)
            fishing_oil_data.append((current_time, fishing_oil))

            # Only create images at intervals if writeFrequency > 0
            if self._write_frequency > 0 and step % interval == 0:
                logging.info(f"Step {step}, time = {current_time:.3f}, Fishing Area Oil = {fishing_oil:.6f}")
                self.create_image(timestep=step)

         # Final image and video creation (if writeFrequency > 0)
        if self._write_frequency > 0:
            self.create_image(timestep="Final")
            self.create_video(output_folder="plots", output_video="simulation.avi")
            print("Simulation video created.")

            # Play the video after creation
            print("Playing simulation video...")
            self.play_video(video_path="simulation.avi")
            print("Video playback complete.")

        # Plotting and saving results
        self.plot_fishing_oil(fishing_oil_data, config_name=config_name)
        self.save_state(config_name=config_name)

        logging.info("Simulation complete.")
        print("Simulation complete.")

    def plot_fishing_oil(self, fishing_oil_data, config_name, output_folder="result_folder"):
        """
        Plot fishing area oil data and save it as an image.

        Parameters:
        - fishing_oil_data (list): Data for fishing oil over time.
        - config_name (str): Name of the configuration file (used for naming the subfolder).
        - output_folder (str): Path to the folder where the plot will be saved.
        """
        subfolder = os.path.join(output_folder, os.path.splitext(config_name)[0])
        os.makedirs(subfolder, exist_ok=True)

        times, oil_values = zip(*fishing_oil_data)
        plt.figure()
        plt.plot(times, oil_values, label="Fishing Area Oil", color="blue")
        plt.xlabel("Time")
        plt.ylabel("Total Oil in Fishing Area")
        plt.title("Oil Distribution in Fishing Area Over Time")
        plt.legend()
        plt.grid()

        output_file = os.path.join(subfolder, "fishing_oil_over_time.png")
        plt.savefig(output_file)
        plt.close()
        logging.info(f"Fishing area oil plot saved to {output_file}")

    def create_image(self, timestep=None, output_folder="plots"):
        """
        Create a plot of the oil distribution and save it as an image file.

        Parameters:
        - timestep (int, optional): The current timestep to include in the file name.
        - output_folder (str): Directory to save the images.
        """
        os.makedirs(output_folder, exist_ok=True)
        plt.figure()
        ax = plt.gca()

        # Fixed normalization range for oil values
        norm = plt.Normalize(vmin=0, vmax=1)
        for cell in self._mesh.cells():
            if cell.type == "triangle":
                coords = cell._points
                oil_value = cell.oil_value
                color = plt.cm.viridis(norm(oil_value))
                triangle = plt.Polygon(coords[:, :2], color=color, alpha=0.9)
                ax.add_patch(triangle)

        # Highlight the fishing area
        x_min, x_max = self.fishing_borders[0]
        y_min, y_max = self.fishing_borders[1]
        fishing_area = plt.Rectangle(
            (x_min, y_min),  # Bottom-left corner
            x_max - x_min,   # Width (x-range)
            y_max - y_min,   # Height (y-range)
            edgecolor="red", facecolor="none", linestyle="--", linewidth=2, label="Fishing Area"
        )
        ax.add_patch(fishing_area)

        # Set up colorbar
        sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
        sm.set_array([])  # Empty array to configure the colorbar
        cbar = plt.colorbar(sm, ax=ax, label="Oil Value")  # Add colorbar with label

        # Add labels and formatting
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.set_aspect("equal")
        ax.set_xlim(0, 1)  # Adjust these based on your mesh's extents
        ax.set_ylim(0, 1)  # Adjust these based on your mesh's extents
        ax.legend(loc="upper right")

        # Save the image with zero-padded sequential filenames
        self.image_counter += 1
        file_name = f"image_{self.image_counter:03d}.png"
        output_path = os.path.join(output_folder, file_name)
        plt.savefig(output_path)
        plt.close()
        logging.debug(f"Saved plot for timestep {timestep} as {output_path}")

    def create_video(self, output_folder="plots", output_video="simulation.avi", fps=5):
        """
        Creates a video from image files in the exact order they appear in the directory.

        Parameters:
        - output_folder (str): Directory where image files are stored.
        - output_video (str): Name of the output video file.
        - fps (int): Frames per second for the video.
        """
        images = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".png")]

        if not images:
            logging.warning("No images found for video creation.")
            return

        frame = cv2.imread(images[0])
        height, width, layers = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

        for image in images:
            video.write(cv2.imread(image))

        video.release()
        logging.info(f"Video saved as {output_video}")

    def play_video(self, video_path="simulation.avi", frame_delay=1000):
        """
        Plays the generated video using OpenCV.

        Parameters:
        - video_path (str): Path to the video file to be played.
        - frame_delay (int): Delay between frames in milliseconds (default is 100 ms).
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Unable to open video file {video_path}")
            return
        print("Video created, press q to exit.")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.info("End of video.")
                break

            cv2.imshow("Simulation Video", frame)
            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def load_state(self, folder):
        """
        Load the simulation state from the given folder.
        """
        oil_values_file = os.path.join(folder, "oil_values.txt")
        simulation_data_file = os.path.join(folder, "simulation_data.txt")

        if not os.path.exists(oil_values_file) or not os.path.exists(simulation_data_file):
            raise FileNotFoundError(f"Missing restart files in folder: {folder}")

        with open(oil_values_file, "r") as f:
            oil_values = [float(line.strip()) for line in f.readlines()]
        for cell, value in zip(self._mesh.cells(), oil_values):
            cell.oil_value = value

        with open(simulation_data_file, "r") as f:
            for line in f:
                key, value = line.strip().split(":")
                if key == "current_time":
                    self._tStart = float(value)
                elif key == "remaining_steps":
                    remaining_steps = int(value)

        self._nt = int((self._tEnd - self._tStart) / self.dt)
        logging.info(f"Restart state loaded. tStart: {self._tStart}, nSteps: {self._nt}")

    def save_state(self, config_name, output_folder="result_folder"):
        """
        Save the current simulation state to a subfolder under the result folder.

        Parameters:
        - config_name (str): Name of the configuration file (used for naming the subfolder).
        - output_folder (str): Path to the folder where the state will be saved.
        """
        subfolder = os.path.join(output_folder, os.path.splitext(config_name)[0])
        os.makedirs(subfolder, exist_ok=True)

        # Save oil values
        oil_values_file = os.path.join(subfolder, "oil_values.txt")
        with open(oil_values_file, "w") as f:
            for cell in self._mesh.cells():
                f.write(f"{cell.oil_value}\n")
        logging.info(f"Oil values saved to {oil_values_file}")

        # Save simulation metadata
        simulation_data_file = os.path.join(subfolder, "simulation_data.txt")
        with open(simulation_data_file, "w") as f:
            max_oil = max(cell.oil_value for cell in self._mesh.cells())
            min_oil = min(cell.oil_value for cell in self._mesh.cells())
            total_oil = sum(cell.oil_value for cell in self._mesh.cells())
            fishing_grounds_oil = sum(
                cell.oil_value for cell in self._mesh.fishing_cells(
                    x_min=self.fishing_borders[0][0],
                    x_max=self.fishing_borders[0][1],
                    y_min=self.fishing_borders[1][0],
                    y_max=self.fishing_borders[1][1]
                )
            )

            f.write(f"tStart: {self._tStart}\n")
            f.write(f"tEnd: {self._tEnd}\n")
            f.write(f"meshName: {self._meshName}\n")
            f.write(f"max_oil: {max_oil}\n")
            f.write(f"min_oil: {min_oil}\n")
            f.write(f"total_oil: {total_oil}\n")
            f.write(f"fishing_grounds_oil: {fishing_grounds_oil}\n")
            f.write(f"fishing_borders: {self.fishing_borders}\n")
        logging.info(f"Simulation data saved to {simulation_data_file}")