# Imports
import streamlit as st
import pandas as pd
import numpy as np
from py3dbp import Packer, Bin, Item
import plotly.graph_objects as go
import plotly.express as px
from styles import get_styles

# === CONFIGURATION ===
st.set_page_config(page_title="SmartPack - Athens Distribution Center", page_icon="📦", layout="wide")

# Apply custom styles
st.markdown(get_styles(), unsafe_allow_html=True)

# Header with Schneider Electric branding
st.markdown("""
<div class="se-header fade-in">
    <div class="se-header-content">
        <div>
            <h1>SmartPack</h1>
            <p>Warehouse Storage Optimization | Athens Distribution Center</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load configuration from CSV files
@st.cache_data
def load_configurations():
    try:
        locations_df = pd.read_csv('locations.csv')
        pallets_df = pd.read_csv('pallets.csv')
        
        locations = {}
        for _, row in locations_df.iterrows():
            locations[row['name']] = (row['width'], row['depth'], row['height'], row['max_weight'])
        
        pallets = {}
        for _, row in pallets_df.iterrows():
            pallets[row['name']] = (row['width'], row['depth'], row['height'], row['weight'])
        
        return locations, pallets
    except FileNotFoundError:
        # Fallback to hardcoded values if CSV files don't exist
        locations = {
            "Shelf Small": (36, 18, 60, 300),
            "Shelf Wide": (48, 24, 72, 350),
            "Bin Deep": (30, 30, 48, 200),
            "Pallet Rack 1": (48, 40, 60, 1000),
            "Pallet Rack 2": (96, 48, 72, 2500),
            "Floor Bulk 1": (72, 48, 60, 1200),
            "Floor Bulk 2": (84, 60, 72, 1500),
            "Mezzanine": (60, 36, 84, 700),
            "Cold Storage": (48, 48, 60, 1100),
            "Bin Tall": (24, 24, 96, 200)
        }
        pallets = {
            "Standard": (48, 40, 6, 30),
            "Euro": (32, 48, 6, 25),
            "Half": (24, 40, 6, 20)
        }
        return locations, pallets

LOCATION_TYPES, PALLET_TYPES = load_configurations()
LOCATION_TYPE_LIST = list(LOCATION_TYPES.keys())
PALLET_TYPE_LIST = list(PALLET_TYPES.keys())

# Color scheme - Schneider Electric Green
SCHNEIDER_GREEN = "#00954A"
PALLET_COLOR = "#8B4513"
FLOOR_COLOR = "#708090"
RACK_COLOR = "#2F4F4F"

# Function to determine orientation description
def get_orientation_description(original_dims, current_dims):
    orig_w, orig_d, orig_h = original_dims[:3]
    curr_w, curr_d, curr_h = current_dims
    
    if (orig_w, orig_d, orig_h) == (curr_w, curr_d, curr_h):
        return "Standard (W×D×H)"
    elif (orig_d, orig_w, orig_h) == (curr_w, curr_d, curr_h):
        return "Rotated 90° (D×W×H)"
    elif (orig_w, orig_h, orig_d) == (curr_w, curr_d, curr_h):
        return "On Side (W×H×D)"
    elif (orig_d, orig_h, orig_w) == (curr_w, curr_d, curr_h):
        return "On Side (D×H×W)"
    elif (orig_h, orig_w, orig_d) == (curr_w, curr_d, curr_h):
        return "Standing (H×W×D)"
    elif (orig_h, orig_d, orig_w) == (curr_w, curr_d, curr_h):
        return "Standing (H×D×W)"
    else:
        return "Custom Orientation"

# Function to create 3D box mesh for Plotly
def create_box_mesh(x, y, z, width, depth, height, color, name="", opacity=0.8):
    """Create a 3D box mesh for Plotly visualization"""
    # Define the 8 vertices of a box
    vertices_x = [x, x+width, x+width, x, x, x+width, x+width, x]
    vertices_y = [y, y, y+depth, y+depth, y, y, y+depth, y+depth]
    vertices_z = [z, z, z, z, z+height, z+height, z+height, z+height]
    
    # Define the 12 triangular faces of the box
    i = [0, 0, 0, 7, 7, 7, 4, 4, 1, 1, 2, 2]
    j = [1, 2, 4, 6, 4, 6, 5, 6, 5, 2, 6, 3]
    k = [2, 3, 5, 2, 5, 2, 6, 5, 4, 6, 7, 7]
    
    return go.Mesh3d(
        x=vertices_x, y=vertices_y, z=vertices_z,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        name=name,
        showscale=False
    )

# Function to create individual SKU inputs
def create_sku_inputs():
    st.sidebar.header("SKU Configuration")
    num_skus = st.sidebar.number_input("Number of SKU types", min_value=1, max_value=10, value=1)
    
    skus = []
    for i in range(num_skus):
        st.sidebar.subheader(f"SKU {i+1}")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            name = st.text_input(f"Name", key=f"name_{i}", value=f"SKU_{i+1}")
            width = st.number_input(f"Width (in)", min_value=0.1, key=f"width_{i}", value=10.0)
            height = st.number_input(f"Height (in)", min_value=0.1, key=f"height_{i}", value=10.0)
        
        with col2:
            depth = st.number_input(f"Depth (in)", min_value=0.1, key=f"depth_{i}", value=10.0)
            weight = st.number_input(f"Weight (lbs, optional)", min_value=0.0, key=f"weight_{i}", value=5.0)
        
        if name and width > 0 and depth > 0 and height > 0:
            skus.append({
                'name': name,
                'width': width,
                'depth': depth,
                'height': height,
                'weight': weight if weight > 0 else 1.0
            })
    
    return pd.DataFrame(skus) if skus else None

# Function to calculate pallet position (95% of location, centered)
def calculate_pallet_position(loc_w, loc_d, pallet_w, pallet_d):
    scale_factor = 0.95
    available_w = loc_w * scale_factor
    available_d = loc_d * scale_factor
    
    final_pallet_w = min(pallet_w, available_w)
    final_pallet_d = min(pallet_d, available_d)
    
    offset_x = (loc_w - final_pallet_w) / 2
    offset_y = (loc_d - final_pallet_d) / 2
    
    return final_pallet_w, final_pallet_d, offset_x, offset_y

# Enhanced packing function with better orientation support
def find_max_quantity_with_orientations(sku_dims, pallet_dims, available_height, max_weight):
    pallet_w, pallet_d = pallet_dims[0], pallet_dims[1]
    sku_w, sku_d, sku_h, sku_weight = sku_dims
    
    # Try all 6 main orientations
    orientations = [
        (sku_w, sku_d, sku_h),  # Original
        (sku_d, sku_w, sku_h),  # Rotated 90°
        (sku_w, sku_h, sku_d),  # On side (width-height base)
        (sku_d, sku_h, sku_w),  # On side (depth-height base)
        (sku_h, sku_w, sku_d),  # Standing (height-width base)
        (sku_h, sku_d, sku_w)   # Standing (height-depth base)
    ]
    
    best_result = None
    best_quantity = 0
    
    for orientation in orientations:
        w, d, h = orientation
        # Quick feasibility check
        if w <= pallet_w and d <= pallet_d and h <= available_height:
            # Estimate maximum possible
            layers_possible = int(available_height / h)
            items_per_layer = int((pallet_w / w)) * int((pallet_d / d))
            max_estimate = min(layers_possible * items_per_layer, int(max_weight / sku_weight), 300)
            
            if max_estimate > 0:
                # Binary search for this orientation
                quantity = binary_search_quantity((w, d, h, sku_weight), pallet_dims, available_height, max_weight, max_estimate)
                if quantity > best_quantity:
                    best_quantity = quantity
                    best_result = {
                        'quantity': quantity,
                        'orientation': orientation,
                        'original_dims': sku_dims
                    }
    
    return best_result

def binary_search_quantity(sku_dims, pallet_dims, available_height, max_weight, max_estimate):
    low, high = 1, max_estimate
    best_quantity = 0
    
    while low <= high:
        mid = (low + high) // 2
        if test_packing_orientation(sku_dims, mid, pallet_dims, available_height, max_weight):
            best_quantity = mid
            low = mid + 1
        else:
            high = mid - 1
    
    return best_quantity

def test_packing_orientation(sku_dims, quantity, pallet_dims, available_height, max_weight):
    packer = Packer()
    sku_w, sku_d, sku_h, sku_weight = sku_dims
    pallet_w, pallet_d = pallet_dims[0], pallet_dims[1]
    
    bin = Bin("TestBin", pallet_w, pallet_d, available_height, max_weight)
    packer.add_bin(bin)
    
    for i in range(quantity):
        item = Item(f"test_{i}", sku_w, sku_d, sku_h, sku_weight)
        packer.add_item(item)
    
    packer.pack(bigger_first=True, distribute_items=True)
    return len(packer.bins[0].items) == quantity if packer.bins else False

# Enhanced function to analyze layers and orientations
def analyze_packing_layers(packed_items, pallet_h, original_dims):
    if not packed_items:
        return []
    
    # Group items by Z position (layers)
    layers = {}
    for item in packed_items:
        z_pos = float(item.position[2])
        layer_key = round(z_pos, 1)  # Round to nearest 0.1 inch
        
        if layer_key not in layers:
            layers[layer_key] = []
        layers[layer_key].append(item)
    
    # Analyze each layer
    layer_analysis = []
    for z_pos in sorted(layers.keys()):
        items_in_layer = layers[z_pos]
        layer_height = pallet_h + z_pos
        
        # Get orientation for items in this layer
        if items_in_layer:
            item = items_in_layer[0]  # All items in layer should have same orientation
            w, d, h = [float(dim) for dim in item.get_dimension()]
            orientation_desc = get_orientation_description(original_dims, (w, d, h))
            
            layer_analysis.append({
                'layer_number': len(layer_analysis) + 1,
                'z_position': layer_height,
                'item_count': len(items_in_layer),
                'dimensions': f"{w:.1f}×{d:.1f}×{h:.1f}",
                'orientation': orientation_desc,
                'arrangement': f"{len(items_in_layer)} items in {orientation_desc.lower()} position"
            })
    
    return layer_analysis

# Main packing function
def pack_skus_max(skus, loc_dims, loc_max_weight, pallet_dims):
    loc_w, loc_d, loc_h = loc_dims
    
    actual_pallet_w, actual_pallet_d, offset_x, offset_y = calculate_pallet_position(
        loc_w, loc_d, pallet_dims[0], pallet_dims[1]
    )
    
    available_height = loc_h - pallet_dims[2]
    available_weight = loc_max_weight - pallet_dims[3]
    
    updated_pallet_dims = (actual_pallet_w, actual_pallet_d, pallet_dims[2], pallet_dims[3])
    
    results = []
    for _, sku in skus.iterrows():
        sku_dims = (sku['width'], sku['depth'], sku['height'], sku['weight'])
        best_result = find_max_quantity_with_orientations(sku_dims, updated_pallet_dims, available_height, available_weight)
        
        if best_result and best_result['quantity'] > 0:
            # Final packing with best orientation
            packer = Packer()
            bin = Bin("PalletBin", actual_pallet_w, actual_pallet_d, available_height, available_weight)
            packer.add_bin(bin)
            
            w, d, h = best_result['orientation']
            for i in range(best_result['quantity']):
                item = Item(f"{sku['name']}_{i}", w, d, h, sku['weight'])
                packer.add_item(item)
            
            packer.pack(bigger_first=True, distribute_items=True)
            
            # Analyze layers with enhanced descriptions
            layer_analysis = analyze_packing_layers(packer.bins[0].items, pallet_dims[2], best_result['original_dims'])
            
            results.append({
                'sku_name': sku['name'],
                'max_quantity': best_result['quantity'],
                'best_orientation': best_result['orientation'],
                'original_dims': best_result['original_dims'],
                'packed_bin': packer.bins[0] if packer.bins else None,
                'pallet_dims': updated_pallet_dims,
                'pallet_offset': (offset_x, offset_y),
                'layer_analysis': layer_analysis
            })
    
    return results

# Plotly 3D Visualization function
def create_plotly_visualization(result, loc_w, loc_d, loc_h, loc_choice, pallet_choice, view_type="aisle"):
    """Create 3D visualization using Plotly"""
    fig = go.Figure()
    
    pallet_w, pallet_d, pallet_h, pallet_weight = result['pallet_dims']
    offset_x, offset_y = result['pallet_offset']
    
    # Add warehouse context for aisle view
    if view_type == "aisle":
        # Floor
        floor = create_box_mesh(
            -loc_w*0.5, -loc_d*0.5, -2, 
            loc_w*2, loc_d*2, 2, 
            FLOOR_COLOR, "Floor", 0.3
        )
        fig.add_trace(floor)
        
        # Left and right racks
        left_rack = create_box_mesh(-15, 0, 0, 5, loc_d, loc_h, RACK_COLOR, "Left Rack", 0.6)
        right_rack = create_box_mesh(loc_w + 10, 0, 0, 5, loc_d, loc_h, RACK_COLOR, "Right Rack", 0.6)
        fig.add_trace(left_rack)
        fig.add_trace(right_rack)
    
    # Location boundary (wireframe effect using thin boxes)
    # Bottom edge
    bottom_edge = create_box_mesh(0, 0, 0, loc_w, loc_d, 1, "rgba(0,0,0,0.8)", "Location Boundary", 0.3)
    fig.add_trace(bottom_edge)
    
    # Pallet
    pallet_center_x = offset_x
    pallet_center_y = offset_y
    pallet_mesh = create_box_mesh(
        pallet_center_x, pallet_center_y, 0,
        pallet_w, pallet_d, pallet_h,
        PALLET_COLOR, f"{pallet_choice} Pallet", 0.8
    )
    fig.add_trace(pallet_mesh)
    
    # Add packed items with different colors for different layers
    packed_bin = result['packed_bin']
    if packed_bin and packed_bin.items:
        # Schneider Electric green color palette
        green_palette = ["#00954A", "#007C3E", "#4CAF50", "#66BB6A", "#81C784"]
        
        for i, item in enumerate(packed_bin.items):
            x, y, z = [float(p) for p in item.position]
            w, d, h = [float(dim) for dim in item.get_dimension()]
            
            # Adjust position to account for pallet offset
            box_x = offset_x + x
            box_y = offset_y + y
            box_z = pallet_h + z
            
            # Use different shades of green for different layers
            layer_index = int(z / 10)  # Rough layer grouping
            color = green_palette[layer_index % len(green_palette)]
            
            box_mesh = create_box_mesh(
                box_x, box_y, box_z,
                w, d, h,
                color, f"SKU Item {i+1}", 0.9
            )
            fig.add_trace(box_mesh)
    
    # Update layout
    fig.update_layout(
        title=f"3D Warehouse Visualization - {view_type.title()} View",
        scene=dict(
            xaxis_title="Width (inches)",
            yaxis_title="Depth (inches)",
            zaxis_title="Height (inches)",
            aspectmode='data',
            bgcolor="rgba(240, 240, 240, 0.8)",
            camera=dict(
                eye=dict(
                    x=1.5 if view_type == "aisle" else 1.2,
                    y=1.5 if view_type == "aisle" else 1.2,
                    z=1.2 if view_type != "top" else 2.5
                )
            )
        ),
        width=400,
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False
    )
    
    return fig

# === UI ===
st.caption("Advanced 3D optimization with intelligent orientation analysis and layer-by-layer planning")

skus = create_sku_inputs()

st.sidebar.header("Location & Pallet")
loc_choice = st.sidebar.selectbox("Location Type", LOCATION_TYPE_LIST)
loc_w, loc_d, loc_h, loc_maxw = LOCATION_TYPES[loc_choice]

pallet_choice = st.sidebar.selectbox("Pallet Type", PALLET_TYPE_LIST)
pallet_dims = PALLET_TYPES[pallet_choice]

if st.button("Optimize Storage Configuration"):
    if skus is None or skus.empty:
        st.error("Please enter at least one SKU.")
        st.stop()

    actual_pallet_w, actual_pallet_d, offset_x, offset_y = calculate_pallet_position(
        loc_w, loc_d, pallet_dims[0], pallet_dims[1]
    )

    results = pack_skus_max(skus, (loc_w, loc_d, loc_h), loc_maxw, pallet_dims)
    
    if not results:
        st.error("No items could be packed. Check SKU dimensions and location size.")
        st.stop()

    st.subheader("Storage Configuration Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="config-card">
            <h4>Location Details</h4>
            <p><strong>Type:</strong> {loc_choice}</p>
            <p><strong>Dimensions:</strong> {loc_w}×{loc_d}×{loc_h} inches</p>
            <p><strong>Max Weight:</strong> {loc_maxw} lbs</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="config-card">
            <h4>Pallet Configuration</h4>
            <p><strong>Type:</strong> {pallet_choice}</p>
            <p><strong>Size:</strong> {actual_pallet_w:.0f}×{actual_pallet_d:.0f}×{pallet_dims[2]} inches</p>
            <p><strong>Available Height:</strong> {loc_h - pallet_dims[2]} inches</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Optimization Results")
    
    for result in results:
        sku_name = result['sku_name']
        max_qty = result['max_quantity']
        best_orientation = result['best_orientation']
        original_dims = result['original_dims']
        packed_bin = result['packed_bin']
        layer_analysis = result['layer_analysis']
        
        if packed_bin and packed_bin.items:
            total_weight = sum(float(i.weight) for i in packed_bin.items) + pallet_dims[3]
            item_vol = sum(float(i.width) * float(i.depth) * float(i.height) for i in packed_bin.items)
            pallet_vol = actual_pallet_w * actual_pallet_d * (loc_h - pallet_dims[2])
            utilization = item_vol / pallet_vol if pallet_vol > 0 else 0
            
            st.success(f"**{sku_name}:** Maximum **{max_qty} units** | Space Utilization: **{utilization:.1%}** | Total Weight: **{total_weight:.1f} lbs**")
            
            # Orientation info
            orientation_desc = get_orientation_description(original_dims, best_orientation)
            st.info(f"**Optimal Orientation:** {orientation_desc} ({best_orientation[0]:.1f}×{best_orientation[1]:.1f}×{best_orientation[2]:.1f})")
            
            # Enhanced Layer-by-layer breakdown
            st.subheader(f"Detailed Layer Analysis - {sku_name}")
            
            for layer in layer_analysis:
                st.markdown(f"""
                <div class="layer-card fade-in">
                    <h4>Layer {layer['layer_number']} (Height: {layer['z_position']:.1f}")</h4>
                    <p><strong>Items:</strong> {layer['item_count']} units</p>
                    <p><strong>Dimensions:</strong> {layer['dimensions']} inches</p>
                    <p><strong>Orientation:</strong> <span class="orientation-badge">{layer['orientation']}</span></p>
                    <p><strong>Arrangement:</strong> {layer['arrangement']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 3D Visualizations using Plotly
            st.subheader(f"3D Visualization - {sku_name}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="viz-container"><h4>Aisle View</h4></div>', unsafe_allow_html=True)
                fig_aisle = create_plotly_visualization(result, loc_w, loc_d, loc_h, loc_choice, pallet_choice, "aisle")
                st.plotly_chart(fig_aisle, use_container_width=True)

            with col2:
                st.markdown('<div class="viz-container"><h4>Top View</h4></div>', unsafe_allow_html=True)
                fig_top = create_plotly_visualization(result, loc_w, loc_d, loc_h, loc_choice, pallet_choice, "top")
                st.plotly_chart(fig_top, use_container_width=True)

            with col3:
                st.markdown('<div class="viz-container"><h4>Side View</h4></div>', unsafe_allow_html=True)
                fig_side = create_plotly_visualization(result, loc_w, loc_d, loc_h, loc_choice, pallet_choice, "side")
                st.plotly_chart(fig_side, use_container_width=True)

else:
    st.info("Configure your SKU details in the sidebar and click **Optimize Storage Configuration** to begin the analysis.")

# Footer
st.markdown("""
<div class="footer">
    SmartPack - Athens DC | Intelligent Packing Tool
</div>
""", unsafe_allow_html=True)
