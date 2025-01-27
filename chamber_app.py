import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def calculate_parts_fitting(input_data):
    machine_type = input_data.get("machine_type", "").strip()
    if machine_type == "SF50":
        chamber_width, chamber_depth, chamber_height = 400, 300, 400
    elif machine_type == "SF100":
        chamber_width, chamber_depth, chamber_height = 400, 600, 400
    else:
        st.error("Invalid machine type! Please select 'SF50' or 'SF100'.")
        return None

    chamber_clearance_width, chamber_clearance_depth, chamber_clearance_height = 50, 50, 50
    solvent = input_data.get("solvent", "").strip()
    if solvent == "PURE":
        chamber_clearance_width += 50
        chamber_clearance_depth += 50
        chamber_clearance_height += 50

    effective_chamber_width = chamber_width - chamber_clearance_width
    effective_chamber_depth = chamber_depth - chamber_clearance_depth
    effective_chamber_height = chamber_height - chamber_clearance_height

    part_width = input_data.get("part_width", 0) + input_data.get("spacing_width", 0)
    part_depth = input_data.get("part_depth", 0) + input_data.get("spacing_depth", 0)
    part_height = input_data.get("part_height", 0) + input_data.get("spacing_height", 0)

    parts_along_width = int(effective_chamber_width // part_width)
    parts_along_depth = int(effective_chamber_depth // part_depth)
    parts_along_height = min(5, int(effective_chamber_height // part_height))

    return {
        "parts_along_width": parts_along_width,
        "parts_along_depth": parts_along_depth,
        "parts_along_height": parts_along_height,
        "total_parts": parts_along_width * parts_along_depth * parts_along_height,
        "effective_chamber_width": effective_chamber_width,
        "effective_chamber_depth": effective_chamber_depth,
        "effective_chamber_height": effective_chamber_height,
        "chamber_dimensions": (chamber_width, chamber_depth, chamber_height),
        "part_width_with_spacing": part_width,
        "part_depth_with_spacing": part_depth,
        "part_height_with_spacing": part_height,
    }


def visualize_chamber_3d(result, input_data):
    chamber_width, chamber_depth, chamber_height = result["chamber_dimensions"]
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    for z in [0, chamber_height]:
        ax.plot([0, chamber_width, chamber_width, 0, 0],
                [0, 0, chamber_depth, chamber_depth, 0],
                z, color="black")

    x_offset = (chamber_width - result["parts_along_width"] * result["part_width_with_spacing"]) / 2
    y_offset = (chamber_depth - result["parts_along_depth"] * result["part_depth_with_spacing"]) / 2
    z_offset = (chamber_height - result["parts_along_height"] * result["part_height_with_spacing"]) / 2

    for i in range(result["parts_along_width"]):
        for j in range(result["parts_along_depth"]):
            for k in range(result["parts_along_height"]):
                x_start = x_offset + i * result["part_width_with_spacing"]
                y_start = y_offset + j * result["part_depth_with_spacing"]
                z_start = z_offset + k * result["part_height_with_spacing"]

                vertices = [
                    [x_start, y_start, z_start],
                    [x_start + input_data["part_width"], y_start, z_start],
                    [x_start + input_data["part_width"], y_start + input_data["part_depth"], z_start],
                    [x_start, y_start + input_data["part_depth"], z_start],
                    [x_start, y_start, z_start + input_data["part_height"]],
                    [x_start + input_data["part_width"], y_start, z_start + input_data["part_height"]],
                    [x_start + input_data["part_width"], y_start + input_data["part_depth"], z_start + input_data["part_height"]],
                    [x_start, y_start + input_data["part_depth"], z_start + input_data["part_height"]]
                ]
                faces = [
                    [vertices[0], vertices[1], vertices[5], vertices[4]],
                    [vertices[1], vertices[2], vertices[6], vertices[5]],
                    [vertices[2], vertices[3], vertices[7], vertices[6]],
                    [vertices[3], vertices[0], vertices[4], vertices[7]],
                    [vertices[0], vertices[1], vertices[2], vertices[3]],
                    [vertices[4], vertices[5], vertices[6], vertices[7]]
                ]
                ax.add_collection3d(Poly3DCollection(faces, alpha=0.6, facecolors="green", edgecolors="black"))

    ax.set_xlim([0, chamber_width])
    ax.set_ylim([0, chamber_depth])
    ax.set_zlim([0, chamber_height])

    # Save the plot to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)
    return buffer


def generate_pdf(input_data, result, plot_buffer):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Title
    c.drawString(30, 750, "Chamber Parts Fitting Report")
    c.drawString(30, 730, f"Machine Type: {input_data['machine_type']}")
    c.drawString(30, 710, f"Solvent: {input_data['solvent']}")
    c.drawString(30, 690, f"Part Dimensions (mm):")
    c.drawString(50, 670, f"Width: {input_data['part_width']}")
    c.drawString(50, 650, f"Depth: {input_data['part_depth']}")
    c.drawString(50, 630, f"Height: {input_data['part_height']}")
    c.drawString(30, 610, f"Spacing Dimensions (mm):")
    c.drawString(50, 590, f"Width: {input_data['spacing_width']}")
    c.drawString(50, 570, f"Depth: {input_data['spacing_depth']}")
    c.drawString(50, 550, f"Height: {input_data['spacing_height']}")

    # Results
    c.drawString(30, 530, f"Total Parts Fitted: {result['total_parts']}")
    c.drawString(30, 510, f"Parts Along Width: {result['parts_along_width']}")
    c.drawString(30, 490, f"Parts Along Depth: {result['parts_along_depth']}")
    c.drawString(30, 470, f"Parts Along Height: {result['parts_along_height']}")

    # Add plot image
    c.drawImage(plot_buffer, 100, 200, width=400, height=250)
    c.save()
    buffer.seek(0)
    return buffer


# Streamlit App
st.title("Chamber Parts Fitting Visualizer with PDF Export")

# Input Fields
machine_type = st.selectbox("Select Machine Type", ["SF50", "SF100"])
part_width = st.number_input("Part Width (mm)", min_value=1, value=50)
part_depth = st.number_input("Part Depth (mm)", min_value=1, value=50)
part_height = st.number_input("Part Height (mm)", min_value=1, value=100)
solvent = st.selectbox("Select Solvent", ["FA326", "PURE"], index=0)

# Spacing Input
default_spacing = 10
if solvent == "PURE":
    default_spacing += 10
spacing_width = st.number_input("Spacing Width (mm)", min_value=0, value=default_spacing)
spacing_depth = st.number_input("Spacing Depth (mm)", min_value=0, value=default_spacing)
spacing_height = st.number_input("Spacing Height (mm)", min_value=0, value=default_spacing)

# Prepare Input Data
input_data = {
    "machine_type": machine_type,
    "part_width": part_width,
    "part_depth": part_depth,
    "part_height": part_height,
    "spacing_width": spacing_width,
    "spacing_depth": spacing_depth,
    "spacing_height": spacing_height,
    "solvent": solvent,
}

if st.button("Generate Report"):
    result = calculate_parts_fitting(input_data)
    if result:
        st.write(f"Total Parts: {result['total_parts']}")
        plot_buffer = visualize_chamber_3d(result, input_data)
        pdf_buffer = generate_pdf(input_data, result, plot_buffer)
        st.download_button("Download PDF Report", data=pdf_buffer, file_name="report.pdf", mime="application/pdf")
