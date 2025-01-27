import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def calculate_parts_fitting(input_data):
    """
    Calculate the number of parts that fit in a chamber and remaining space.

    Parameters:
        input_data (dict): Dictionary containing:
            - machine_type (str): Type of machine ("SF50" or "SF100").
            - part_width (float): Part width in mm.
            - part_depth (float): Part depth in mm.
            - part_height (float): Part height in mm.
            - spacing_width (float): Spacing width in mm.
            - spacing_depth (float): Spacing depth in mm.
            - spacing_height (float): Spacing height in mm.
            - solvent (str): Type of solvent (e.g., "PURE").

    Returns:
        dict: Contains the total number of parts for both the original chamber depth
              and the chamber depth increased by 300mm, along with parts along height.
    """
    # Determine chamber dimensions based on machine_type
    machine_type = input_data.get('machine_type', "").strip()
    if machine_type == "SF50":
        chamber_width = 400
        chamber_depth = 300
        chamber_height = 400
    elif machine_type == "SF100":
        chamber_width = 400
        chamber_depth = 600
        chamber_height = 400
    else:
        return {"error": "Invalid machine_type. Must be 'SF50' or 'SF100'."}

    # Set clearance dimensions
    chamber_clearance_width = 50
    chamber_clearance_depth = 50
    chamber_clearance_height = 50

    # Adjust for solvent type
    solvent = input_data.get('solvent', "").strip()
    if solvent == "PURE":
        chamber_clearance_width += 50
        chamber_clearance_depth += 50
        chamber_clearance_height += 50
        input_data['spacing_width'] += 10
        input_data['spacing_depth'] += 10

    # Calculate effective chamber dimensions after clearance
    effective_chamber_width = chamber_width - chamber_clearance_width
    effective_chamber_depth = chamber_depth - chamber_clearance_depth
    effective_chamber_height = chamber_height - chamber_clearance_height

    # Extract part dimensions and spacing
    try:
        part_width = float(input_data.get('part_width', 0))
        part_depth = float(input_data.get('part_depth', 0))
        part_height = float(input_data.get('part_height', 0))
        spacing_width = float(input_data.get('spacing_width', 0))
        spacing_depth = float(input_data.get('spacing_depth', 0))
        spacing_height = float(input_data.get('spacing_height', 0))
    except ValueError:
        return {"error": "All input values must be numeric."}

    if None in (part_width, part_depth, part_height, spacing_width, spacing_depth, spacing_height):
        return {"error": "All input fields must be provided and non-null."}

    def calculate_total_parts(chamber_depth):
        # Calculate effective part dimensions including spacing
        effective_part_width = part_width + spacing_width
        effective_part_depth = part_depth + spacing_depth
        effective_part_height = part_height + spacing_height

        # Calculate number of parts that fit in each dimension
        parts_along_width = int(effective_chamber_width // effective_part_width)
        parts_along_depth = int(chamber_depth // effective_part_depth)

        # Height is constrained by the number of racks/shelves
        parts_along_height = min(5, int(effective_chamber_height // effective_part_height))

        # Total number of parts
        total_parts = parts_along_width * parts_along_depth * parts_along_height

        return total_parts, parts_along_width, parts_along_depth, parts_along_height

    # Calculate total parts for both depths
    total_parts_original, parts_along_width_original, parts_along_depth_original, parts_along_height_original = calculate_total_parts(effective_chamber_depth)
    total_parts_extended, parts_along_width_extended, parts_along_depth_extended, parts_along_height_extended = calculate_total_parts(effective_chamber_depth + 300)

    return {
        "total_parts_original": total_parts_original,
        "total_parts_extended": total_parts_extended,
        "parts_along_height_original": parts_along_height_original,
        "parts_along_height_extended": parts_along_height_extended,
        "parts_along_width_original": parts_along_width_original,
        "parts_along_depth_original": parts_along_depth_original
    }

def visualize_chamber_3d(input_data):
    """
    Visualize how parts fit into the chamber in 3D based on the given input data.

    Parameters:
        input_data (dict): Dictionary containing chamber and part dimensions.

    Returns:
        dict: Includes the total number of parts and a confirmation of the plot.
    """
    # Determine chamber dimensions based on machine_type
    machine_type = input_data.get('machine_type', "").strip()
    if machine_type == "SF50":
        chamber_width = 400
        chamber_depth = 300
        chamber_height = 400
    elif machine_type == "SF100":
        chamber_width = 400
        chamber_depth = 600
        chamber_height = 400
    else:
        raise ValueError("Invalid machine_type. Must be 'SF50' or 'SF100'.")

    # Clearance adjustments
    chamber_clearance_width = 50
    chamber_clearance_depth = 50
    chamber_clearance_height = 50

    solvent = input_data.get('solvent', "").strip()
    if solvent == "PURE":
        chamber_clearance_width += 50
        chamber_clearance_depth += 50
        chamber_clearance_height += 50

    # Calculate effective chamber dimensions after clearance
    effective_chamber_width = chamber_width - chamber_clearance_width
    effective_chamber_depth = chamber_depth - chamber_clearance_depth
    effective_chamber_height = chamber_height - chamber_clearance_height

    result = calculate_parts_fitting(input_data)

    # Extract necessary information
    part_width = float(input_data.get('part_width', 0))
    part_depth = float(input_data.get('part_depth', 0))
    part_height = float(input_data.get('part_height', 0))
    spacing_width = float(input_data.get('spacing_width', 0))
    spacing_depth = float(input_data.get('spacing_depth', 0))
    spacing_height = float(input_data.get('spacing_height', 0))

    parts_along_width = result["parts_along_width_original"]
    parts_along_depth = result["parts_along_depth_original"]
    parts_along_height = result["parts_along_height_original"]

    # Calculate effective part dimensions including spacing
    effective_part_width = part_width + spacing_width
    effective_part_depth = part_depth + spacing_depth
    effective_part_height = part_height + spacing_height

    # Offsets to center parts
    x_offset = (chamber_width - (parts_along_width * effective_part_width)) / 2
    y_offset = chamber_clearance_depth / 2
    z_offset = (chamber_clearance_height / 2) + ((effective_chamber_height - (parts_along_height * effective_part_height)) / 2)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Draw the chamber as a wireframe
    for z in [0, chamber_height]:
        ax.plot([0, chamber_width, chamber_width, 0, 0],
                [0, 0, chamber_depth, chamber_depth, 0],
                z, color='black')

    # Draw the parts
    for i in range(parts_along_width):
        for j in range(parts_along_depth):
            for k in range(parts_along_height):
                x_start = x_offset + i * effective_part_width
                y_start = y_offset + j * effective_part_depth
                z_start = z_offset + k * effective_part_height

                # Define cube vertices
                vertices = [
                    [x_start, y_start, z_start],
                    [x_start + part_width, y_start, z_start],
                    [x_start + part_width, y_start + part_depth, z_start],
                    [x_start, y_start + part_depth, z_start],
                    [x_start, y_start, z_start + part_height],
                    [x_start + part_width, y_start, z_start + part_height],
                    [x_start + part_width, y_start + part_depth, z_start + part_height],
                    [x_start, y_start + part_depth, z_start + part_height]
                ]

                # Define faces of the cube
                faces = [
                    [vertices[0], vertices[1], vertices[5], vertices[4]],
                    [vertices[1], vertices[2], vertices[6], vertices[5]],
                    [vertices[2], vertices[3], vertices[7], vertices[6]],
                    [vertices[3], vertices[0], vertices[4], vertices[7]],
                    [vertices[0], vertices[1], vertices[2], vertices[3]],
                    [vertices[4], vertices[5], vertices[6], vertices[7]]
                ]

                ax.add_collection3d(Poly3DCollection(faces, alpha=0.6, facecolors='green', edgecolors='black'))

    # Set labels and limits
    ax.set_xlabel("Width (mm)")
    ax.set_ylabel("Depth (mm)")
    ax.set_zlabel("Height (mm)")
    ax.set_xlim([0, chamber_width])
    ax.set_ylim([0, chamber_depth])
    ax.set_zlim([0, chamber_height])

    # Add a title
    ax.set_title("3D Visualization of Parts Fitting in the Chamber")

    # Show the plot
    plt.show()

    # Generate a front view
    fig, ax = plt.subplots(figsize=(8, 6))
    for i in range(parts_along_width):
        for k in range(parts_along_height):
            x_start = x_offset + i * effective_part_width
            z_start = z_offset + k * effective_part_height
            rect = plt.Rectangle((x_start, z_start), part_width, part_height, color='green', alpha=0.6, edgecolor='black')
            ax.add_patch(rect)

    ax.set_xlim([0, chamber_width])
    ax.set_ylim([0, chamber_height])
    ax.set_xlabel("Width (mm)")
    ax.set_ylabel("Height (mm)")
    ax.set_title("Front View of Parts in the Chamber")
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

    # Return output with results and plot status
    return {
        "total_parts_original": result["total_parts_original"],
        "total_parts_extended": result["total_parts_extended"],
        "plot_status": "3D and front view visualizations displayed successfully."
    }

# Example input data
input_data = {
    'machine_type': 'SF50',
    'part_width': 50,
    'part_depth': 50,
    'part_height': 100,
    'spacing_width': 10,
    'spacing_depth': 10,
    'spacing_height': 30,
    'solvent': ""
}

# Call the visualization function
result = visualize_chamber_3d(input_data)
print(result)
