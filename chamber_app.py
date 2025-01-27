import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from io import BytesIO
from fpdf import FPDF

# Function to calculate parts fitting
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

# Function to visualize chamber in 3D
def visualize_chamber_3d(result, input_data):
    chamber_width, chamber_depth, chamber_height = result["chamber_dimensions"]
    part_color = "#4FC3CA"  # Hardcoded part color
    line_color = "#152E35"  # Hardcoded line color

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    for z in [0, chamber_height]:
        ax.plot([0, chamber_width, chamber_width, 0, 0],
                [0, 0, chamber_depth, chamber_depth, 0],
                z, color=line_color)

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
                ax.add_collection3d(Poly3DCollection(faces, alpha=0.6, facecolors=part_color, edgecolors=line_color))

    ax.set_xlim([0, chamber_width])
    ax.set_ylim([0, chamber_depth])
    ax.set_zlim([0, chamber_height])

    # Set label colors
    ax.set_xlabel("Width (mm)", color=line_color)
    ax.set_ylabel("Depth (mm)", color=line_color)
    ax.set_zlabel("Height (mm)", color=line_color)

    # Save the plot to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)
    return buffer

# Function to generate the PDF report
def generate_pdf(input_data, result, plot_buffer):
    pdf = FPDF()
    pdf.add_page()

    # Add custom font (Bebas Neue)
    pdf.add_font("BebasNeue", "", "BebasNeue-Regular.ttf", uni=True)
    pdf.set_font("BebasNeue", size=24)
    pdf.set_text_color(79, 195, 202)  # Set text color to #4FC3CA
    pdf.cell(200, 10, txt="Chamber Parts Fitting Report", ln=True, align="C")

    # Add Company Logo
    pdf.image("logo.png", x=10, y=15, w=30)  # Adjust the path to your logo

    pdf.ln(20)  # Add some space after the logo

    # Section: Parameters
    pdf.set_draw_color(79, 195, 202)  # Divider color
    pdf.set_line_width(0.5)
    pdf.line(10, 40, 200, 40)  # Add a horizontal line

    pdf.set_font("Arial", size=14)
    pdf.set_text_color(0, 0, 0)  # Reset text color to black
    pdf.cell(0, 10, txt="Parameters", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Machine Type: {input_data['machine_type']}", ln=True)
    pdf.cell(0, 10, f"Solvent: {input_data['solvent']}", ln=True)
    pdf.cell(0, 10, f"Part Dimensions (mm): {input_data['part_width']} x {input_data['part_depth']} x {input_data['part_height']}", ln=True)

    # Section: Results
    pdf.ln(10)
    pdf.set_draw_color(79, 195, 202)
    pdf.line(10, 80, 200, 80)

    pdf.set_font("BebasNeue", size=18)
    pdf.set_text_color(79, 195, 202)
    pdf.cell(0, 10, txt="Results", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Total Parts: {result['total_parts']}", ln=True)
    pdf.cell(0, 10, f"Parts Along Width: {result['parts_along_width']}", ln=True)
    pdf.cell(0, 10, f"Parts Along Depth: {result['parts_along_depth']}", ln=True)
    pdf.cell(0, 10, f"Parts Along Height: {result['parts_along_height']}", ln=True)

    # Section: Visualization
    pdf.ln(10)
    pdf.set_draw_color(79, 195, 202)
    pdf.line(10, 120, 200, 120)

    pdf.set_font("BebasNeue", size=18)
    pdf.set_text_color(79, 195, 202)
    pdf.cell(0, 10, txt="Visualization", ln=True, align="L")
    pdf.ln(5)

    # Add Visualization Plot
    plot_image = BytesIO(plot_buffer.getvalue())
    pdf.image(plot_image, x=10, y=140, w=190)

    # Footer Section
    pdf.set_y(-30)  # Position footer at the bottom
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(128, 128, 128)

    # Save to Buffer
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Streamlit App Logic
st.title("Chamber Parts Fitting Visualizer with PDF Export")

# Input Fields
machine_type = st.selectbox("Select Machine Type", ["SF50", "SF100"])
part_width = st.number_input("Part Width (mm)", min_value=1, value=50)
part_depth = st.number_input("Part Depth (mm)", min_value=1, value=50)
part_height = st.number_input("Part Height (mm)", min_value=1, value=100)
solvent = st.selectbox("Select Solvent", ["", "PURE", "FA326", "FA9202"], index=0)

# Spacing Input
spacing_width = st.number_input("Spacing Width (mm)", min_value=0, value=10 if solvent != "PURE" else 20)
spacing_depth = st.number_input("Spacing Depth (mm)", min_value=0, value=10 if solvent != "PURE" else 20)
spacing_height = st.number_input("Spacing Height (mm)", min_value=0, value=30)

password = st.text_input("Enter Password", type="password")

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

# Button Styles
st.markdown("""
    <style>
        div.stButton > button:first-child {
            background-color: #4FC3CA;
            color: white;
            font-weight: bold;
        }
        div.stButton > button:first-child:hover {
            background-color: #3BA2B0;
        }
        div.stDownloadButton > button {
            background-color: green;
            color: white;
        }
        div.stDownloadButton > button:hover {
            background-color: darkgreen;
        }
    </style>
""", unsafe_allow_html=True)

if st.button("Generate Report"):
    if password != "w6g2piZRbnjG1RF":
        st.error("Incorrect password. Please try again.")
    else:
        result = calculate_parts_fitting(input_data)
        if result:
            st.write(f"Total Parts: {result['total_parts']}")
            plot_buffer = visualize_chamber_3d(result, input_data)
            st.image(plot_buffer, caption="3D Visualization of Parts in Chamber", use_container_width=True)
            pdf_buffer = generate_pdf(input_data, result, plot_buffer)
            st.download_button("Download PDF Report", data=pdf_buffer, file_name="report.pdf", mime="application/pdf")
