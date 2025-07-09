import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="🏭 Warehouse Digital Twin Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def generate_warehouse_data():
    """Generate large realistic warehouse layout with proper digital twin structure"""
    print("🏗️ Building digital warehouse twin...")
    
    locations = []
    
    # Warehouse parameters
    num_aisles = 40
    levels_per_aisle = 5
    bays_per_side = 10
    sides_per_aisle = 2
    
    # Physical dimensions (meters) - Proper warehouse spacing
    aisle_width = 4.0      # 4m between aisles (for forklifts)
    aisle_length = 100     # 100m long aisles
    bay_width = 1.5        # 1.5m per bay
    level_height = 2.5     # 2.5m per level
    side_spacing = 2.0     # 2m between A and B sides
    
    location_count = 0
    
    for aisle_num in range(1, num_aisles + 1):
        for side in ['A', 'B']:
            for level in range(1, levels_per_aisle + 1):
                for bay in range(1, bays_per_side + 1):
                    
                    # Calculate precise 3D coordinates for digital twin
                    x = aisle_num * aisle_width
                    
                    # Y coordinate: bay position + side offset
                    base_y = (bay - 1) * bay_width
                    if side == 'A':
                        y = base_y
                    else:  # Side B is on opposite side of aisle
                        y = base_y + aisle_length/2 + side_spacing
                    
                    z = (level - 1) * level_height
                    
                    # Zone assignment (4 zones, 10 aisles each)
                    zone_num = 1 + (aisle_num - 1) // 10
                    zone = f"Zone_{zone_num}"
                    
                    location_id = f"A{aisle_num:02d}{side}{level}{bay:02d}"
                    
                    locations.append({
                        'location_id': location_id,
                        'aisle': f"A{aisle_num:02d}",
                        'aisle_num': aisle_num,
                        'side': side,
                        'level': level,
                        'bay': bay,
                        'x': x,
                        'y': y,
                        'z': z,
                        'zone': zone
                    })
                    
                    location_count += 1
                    
                    if location_count % 2000 == 0:
                        print(f"   Generated {location_count:,} locations...")
    
    print(f"✅ Generated {len(locations):,} warehouse locations")
    return pd.DataFrame(locations)

@st.cache_data
def generate_pick_data_with_skus(locations_df, days=7, picks_per_day=2500):
    """Generate pick data with realistic SKU distribution"""
    print(f"📦 Generating {days * picks_per_day:,} picks with SKU data...")
    
    np.random.seed(42)
    picks = []
    
    # Generate SKU catalog with realistic distribution
    sku_categories = {
        'ELECTRONICS': {'count': 500, 'velocity': 'high'},
        'APPAREL': {'count': 800, 'velocity': 'medium'},
        'HOME_GOODS': {'count': 600, 'velocity': 'medium'},
        'BOOKS': {'count': 400, 'velocity': 'low'},
        'TOYS': {'count': 300, 'velocity': 'high'},
        'SPORTS': {'count': 400, 'velocity': 'low'}
    }
    
    # Create SKU master data
    skus = []
    for category, info in sku_categories.items():
        for i in range(info['count']):
            skus.append({
                'sku_id': f"{category}_{i+1:04d}",
                'category': category,
                'velocity': info['velocity']
            })
    
    skus_df = pd.DataFrame(skus)
    
    # ABC Analysis for locations
    total_locations = len(locations_df)
    locations_df_sorted = locations_df.sort_values(['level', 'aisle_num'])
    
    # A-class: 20% locations get 70% picks (lower levels, front aisles)
    a_class_size = int(total_locations * 0.2)
    a_class_locations = locations_df_sorted.head(a_class_size)
    
    # B-class: 30% locations get 25% picks
    b_class_size = int(total_locations * 0.3)
    b_class_locations = locations_df_sorted.iloc[a_class_size:a_class_size + b_class_size]
    
    # C-class: 50% locations get 5% picks
    c_class_locations = locations_df_sorted.tail(total_locations - a_class_size - b_class_size)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    pick_count = 0
    
    for day_idx, date in enumerate(dates):
        print(f"📅 Day {day_idx + 1}/{days}")
        
        for pick_id in range(picks_per_day):
            
            # Location selection based on ABC analysis
            rand = np.random.random()
            if rand < 0.7:  # 70% from A-class
                location = a_class_locations.sample(1).iloc[0]
            elif rand < 0.95:  # 25% from B-class
                location = b_class_locations.sample(1).iloc[0]
            else:  # 5% from C-class
                location = c_class_locations.sample(1).iloc[0]
            
            # SKU selection based on velocity
            sku_rand = np.random.random()
            if sku_rand < 0.6:  # 60% high velocity
                sku = skus_df[skus_df['velocity'] == 'high'].sample(1).iloc[0]
            elif sku_rand < 0.85:  # 25% medium velocity
                sku = skus_df[skus_df['velocity'] == 'medium'].sample(1).iloc[0]
            else:  # 15% low velocity
                sku = skus_df[skus_df['velocity'] == 'low'].sample(1).iloc[0]
            
            # Time distribution (realistic warehouse hours)
            hour_weights = [0.02, 0.03, 0.05, 0.08, 0.12, 0.15, 0.18, 0.15, 0.12, 0.06, 0.03, 0.01]
            hour = int(np.random.choice(range(6, 18), p=np.array(hour_weights)/sum(hour_weights)))
            minute = int(np.random.randint(0, 60))
            
            pick_time = datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=hour, minutes=minute)
            
            picks.append({
                'pick_id': f"{date.strftime('%Y%m%d')}_{pick_id:04d}",
                'location_id': location['location_id'],
                'timestamp': pick_time,
                'x': location['x'],
                'y': location['y'],
                'z': location['z'],
                'zone': location['zone'],
                'aisle': location['aisle'],
                'aisle_num': location['aisle_num'],
                'level': location['level'],
                'side': location['side'],
                'bay': location['bay'],
                'sku_id': sku['sku_id'],
                'category': sku['category'],
                'velocity': sku['velocity'],
                'quantity': np.random.randint(1, 8),
                'picker_id': f"PICKER_{np.random.randint(1, 30):02d}"
            })
            
            pick_count += 1
            if pick_count % 3000 == 0:
                print(f"   Generated {pick_count:,} picks...")
    
    print(f"✅ Generated {len(picks):,} picks")
    return pd.DataFrame(picks)

@st.cache_data
def create_3d_heatmap_data(picks_df, date_filter=None, zone_filter=None):
    """Create 3D heatmap data optimized for Plotly visualization"""
    filtered_picks = picks_df.copy()
    
    if date_filter:
        start_date, end_date = date_filter
        filtered_picks = filtered_picks[
            (filtered_picks['timestamp'].dt.date >= start_date) &
            (filtered_picks['timestamp'].dt.date <= end_date)
        ]
    
    if zone_filter:
        filtered_picks = filtered_picks[filtered_picks['zone'].isin(zone_filter)]
    
    # Aggregate by location
    heatmap = filtered_picks.groupby([
        'location_id', 'x', 'y', 'z', 'zone', 'aisle', 'aisle_num', 'level', 'side'
    ]).agg({
        'pick_id': 'count',
        'quantity': 'sum',
        'sku_id': 'nunique'
    }).round(2)
    
    heatmap.columns = ['pick_count', 'total_quantity', 'unique_skus']
    heatmap = heatmap.reset_index()
    
    if len(heatmap) == 0:
        return heatmap
    
    # Enhanced scaling for 3D visualization
    max_picks = heatmap['pick_count'].max()
    min_picks = heatmap['pick_count'].min()
    
    if max_picks > min_picks:
        heatmap['intensity'] = (heatmap['pick_count'] - min_picks) / (max_picks - min_picks)
    else:
        heatmap['intensity'] = 1.0
    
    # Size scaling for markers
    heatmap['marker_size'] = heatmap['intensity'] * 20 + 5  # Size 5-25
    
    return heatmap

@st.cache_data
def create_aisle_summary(picks_df):
    """Create aisle-level summary for top view"""
    aisle_summary = picks_df.groupby(['aisle', 'aisle_num']).agg({
        'pick_id': 'count',
        'quantity': 'sum',
        'sku_id': 'nunique',
        'location_id': 'nunique',
        'x': 'mean',
        'y': 'mean'
    }).round(2)
    
    aisle_summary.columns = ['total_picks', 'total_quantity', 'unique_skus', 'active_locations', 'center_x', 'center_y']
    aisle_summary = aisle_summary.reset_index()
    
    # Add intensity for visualization
    max_picks = aisle_summary['total_picks'].max()
    aisle_summary['intensity'] = aisle_summary['total_picks'] / max_picks
    
    return aisle_summary

def create_3d_warehouse_plotly(heatmap_data, title="3D Warehouse Digital Twin"):
    """Create 3D warehouse visualization using Plotly"""
    
    if len(heatmap_data) == 0:
        return go.Figure().add_annotation(text="No data available", x=0.5, y=0.5)
    
    # Performance optimization - sample large datasets
    display_data = heatmap_data
    if len(heatmap_data) > 3000:
        display_data = heatmap_data.nlargest(3000, 'pick_count')
        
    fig = go.Figure()
    
    # Add 3D scatter plot for warehouse locations
    fig.add_trace(go.Scatter3d(
        x=display_data['x'],
        y=display_data['y'],
        z=display_data['z'],
        mode='markers',
        marker=dict(
            size=display_data['marker_size'],
            color=display_data['pick_count'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Pick Count",
                x=1.02
            ),
            opacity=0.8,
            line=dict(width=0.5, color='DarkSlateGrey')
        ),
        text=display_data['location_id'],
        hovertemplate="<b>%{text}</b><br>" +
                     "📦 Picks: %{marker.color}<br>" +
                     "📋 SKUs: %{customdata[0]}<br>" +
                     "🏢 Zone: %{customdata[1]}<br>" +
                     "📏 Level: %{customdata[2]}<br>" +
                     "Position: (%{x:.1f}, %{y:.1f}, %{z:.1f}m)<br>" +
                     "<extra></extra>",
        customdata=np.column_stack((
            display_data['unique_skus'],
            display_data['zone'],
            display_data['level']
        )),
        name="Storage Locations"
    ))
    
    # Add warehouse structure (floor and basic framework)
    # Floor outline
    max_x, max_y = display_data['x'].max(), display_data['y'].max()
    min_x, min_y = display_data['x'].min(), display_data['y'].min()
    
    # Floor grid
    floor_x = [min_x, max_x, max_x, min_x, min_x]
    floor_y = [min_y, min_y, max_y, max_y, min_y]
    floor_z = [0, 0, 0, 0, 0]
    
    fig.add_trace(go.Scatter3d(
        x=floor_x,
        y=floor_y,
        z=floor_z,
        mode='lines',
        line=dict(color='gray', width=3),
        name="Warehouse Floor",
        hoverinfo='skip'
    ))
    
    # Add aisle markers
    aisle_centers = display_data.groupby('aisle_num').agg({
        'x': 'mean',
        'y': 'mean',
        'z': 'max'
    }).reset_index()
    
    fig.add_trace(go.Scatter3d(
        x=aisle_centers['x'],
        y=aisle_centers['y'],
        z=aisle_centers['z'] + 2,  # Above the racks
        mode='text',
        text=[f"A{num:02d}" for num in aisle_centers['aisle_num']],
        textfont=dict(size=10, color='white'),
        name="Aisle Labels",
        hoverinfo='skip'
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20)
        ),
        scene=dict(
            xaxis_title="Aisle Direction (m)",
            yaxis_title="Bay Direction (m)",
            zaxis_title="Height (m)",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='manual',
            aspectratio=dict(x=2, y=1, z=0.5),
            bgcolor='black'
        ),
        height=700,
        showlegend=True,
        legend=dict(x=0, y=1)
    )
    
    if len(heatmap_data) > 3000:
        fig.add_annotation(
            text=f"Showing top 3,000 locations out of {len(heatmap_data):,} total",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="yellow",
            opacity=0.8
        )
    
    return fig

def create_warehouse_structure_3d(locations_df):
    """Create a 3D wireframe of the warehouse structure"""
    fig = go.Figure()
    
    # Sample aisles for structure visualization
    sample_aisles = [1, 10, 20, 30, 40]
    
    for aisle_num in sample_aisles:
        aisle_data = locations_df[locations_df['aisle_num'] == aisle_num]
        
        if len(aisle_data) > 0:
            # Get aisle boundaries
            min_y, max_y = aisle_data['y'].min(), aisle_data['y'].max()
            x_pos = aisle_data['x'].iloc[0]
            max_z = aisle_data['z'].max() + 2.5
            
            # Vertical posts
            for y_pos in [min_y, max_y]:
                fig.add_trace(go.Scatter3d(
                    x=[x_pos, x_pos],
                    y=[y_pos, y_pos],
                    z=[0, max_z],
                    mode='lines',
                    line=dict(color='gray', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    # Add title and layout
    fig.update_layout(
        title="🏗️ Warehouse Structure Framework",
        scene=dict(
            xaxis_title="Aisle Direction (m)",
            yaxis_title="Bay Direction (m)",
            zaxis_title="Height (m)",
            bgcolor='black'
        ),
        height=500
    )
    
    return fig

# Session state for interactivity
if 'selected_aisle' not in st.session_state:
    st.session_state.selected_aisle = None
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = None

# Main app
st.title("🏭 Warehouse Digital Twin - Interactive Analytics")
st.markdown("**Advanced 3D Visualization with Plotly (Browser-Compatible)**")

# Warehouse specifications
st.info("🏗️ **Digital Twin Specs**: 40 aisles × 5 levels × 2 sides × 10 bays = 4,000 locations | 160m × 65m × 12.5m")

# Sidebar
st.sidebar.header("🎛️ Control Panel")

# Load data
with st.spinner("🏗️ Building warehouse digital twin..."):
    locations_df = generate_warehouse_data()
    
with st.spinner("📦 Generating pick data with SKUs..."):
    picks_df = generate_pick_data_with_skus(locations_df, days=7, picks_per_day=2500)

st.success(f"✅ **Loaded**: {len(locations_df):,} locations | {len(picks_df):,} picks | {picks_df['sku_id'].nunique():,} SKUs")

# Filters
date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(picks_df['timestamp'].dt.date.min(), picks_df['timestamp'].dt.date.max()),
    min_value=picks_df['timestamp'].dt.date.min(),
    max_value=picks_df['timestamp'].dt.date.max()
)

zones = sorted(picks_df['zone'].unique())
selected_zones = st.sidebar.multiselect("🏢 Zones", zones, default=zones)

# Apply basic filters
filtered_picks = picks_df[
    (picks_df['timestamp'].dt.date >= date_range[0]) &
    (picks_df['timestamp'].dt.date <= date_range[1]) &
    (picks_df['zone'].isin(selected_zones))
]

# Visualization selection
viz_options = [
    "🏗️ 3D Digital Twin (Plotly)",
    "🏢 Warehouse Structure",
    "🗺️ Aisle Heatmap (Top View)",
    "📊 Level Breakdown",
    "📦 SKU Analysis"
]

viz_type = st.sidebar.selectbox("📊 View Type", viz_options)

# KPIs
col1, col2, col3, col4 = st.columns(4)
total_picks = len(filtered_picks)
avg_daily = total_picks / 7
active_locs = filtered_picks['location_id'].nunique()
total_skus = filtered_picks['sku_id'].nunique()

col1.metric("📦 Total Picks", f"{total_picks:,}")
col2.metric("📊 Daily Average", f"{avg_daily:.0f}")
col3.metric("🎯 Active Locations", f"{active_locs:,}")
col4.metric("📋 Unique SKUs", f"{total_skus:,}")

# Main visualization
if viz_type == "🏗️ 3D Digital Twin (Plotly)":
    st.subheader("🏗️ 3D Warehouse Digital Twin")
    
    # Create 3D heatmap data
    heatmap_3d = create_3d_heatmap_data(filtered_picks, date_range, selected_zones)
    
    if len(heatmap_3d) > 0:
        st.info("🎮 **Controls**: Drag to rotate | Scroll to zoom | Click and drag to pan | Hover for details")
        
        # Create and display 3D visualization
        fig_3d = create_3d_warehouse_plotly(heatmap_3d, "3D Warehouse Activity Heatmap")
        st.plotly_chart(fig_3d, use_container_width=True)
        
        # Legend and controls
        with st.expander("🎨 Visualization Guide"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **🎯 Marker Size**: Pick frequency (larger = more picks)  
                **🌈 Color Scale**: Viridis (dark blue = low, yellow = high)  
                **📏 Height (Z-axis)**: Storage level  
                **🏷️ Labels**: Aisle numbers above racks  
                """)
            with col2:
                st.markdown("""
                **🖱️ Mouse Controls**:  
                - Left click + drag: Rotate view  
                - Scroll: Zoom in/out  
                - Right click + drag: Pan  
                - Hover: Show location details  
                """)
            
    else:
        st.warning("⚠️ No data available for selected filters")

elif viz_type == "🏢 Warehouse Structure":
    st.subheader("🏢 Warehouse Physical Structure")
    
    # Show warehouse framework
    structure_fig = create_warehouse_structure_3d(locations_df)
    st.plotly_chart(structure_fig, use_container_width=True)
    
    # Warehouse specifications
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📏 Physical Dimensions**:
        - Length: 160m (40 aisles × 4m)
        - Width: 65m (bays + spacing)
        - Height: 12.5m (5 levels × 2.5m)
        - Total Volume: 130,000 m³
        """)
    
    with col2:
        st.markdown("""
        **🏗️ Structure Details**:
        - Aisle Width: 4m (forklift access)
        - Bay Width: 1.5m
        - Level Height: 2.5m
        - Side Spacing: 2m (A/B sides)
        """)
    
    with col3:
        st.markdown("""
        **📦 Storage Capacity**:
        - Total Locations: 4,000
        - Aisles: 40 (A01-A40)
        - Levels per Aisle: 5
        - Bays per Side: 10
        """)

elif viz_type == "🗺️ Aisle Heatmap (Top View)":
    st.subheader("🗺️ Interactive Aisle Heatmap")
    
    # Create aisle summary
    aisle_summary = create_aisle_summary(filtered_picks)
    
    if len(aisle_summary) > 0:
        # Interactive aisle selection
        fig = px.scatter(
            aisle_summary,
            x='center_x',
            y='center_y',
            size='total_picks',
            color='total_picks',
            hover_data=['aisle', 'unique_skus', 'active_locations'],
            title="Warehouse Top View - Click on Aisle for Details",
            labels={'center_x': 'Aisle Direction (m)', 'center_y': 'Bay Direction (m)'},
            color_continuous_scale='Viridis',
            height=600
        )
        
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>" +
                         "Picks: %{marker.color}<br>" +
                         "SKUs: %{customdata[1]}<br>" +
                         "Locations: %{customdata[2]}<br>" +
                         "<extra></extra>",
            hovertext=aisle_summary['aisle']
        )
        
        fig.update_layout(showlegend=False)
        
        # Display interactive plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Aisle selection via dropdown
        selected_aisle = st.selectbox(
            "🛤️ Select Aisle for Detailed View:",
            options=[''] + sorted(aisle_summary['aisle'].tolist()),
            index=0
        )
        
        if selected_aisle:
            st.session_state.selected_aisle = selected_aisle
            
        # Show aisle details if selected
        if st.session_state.selected_aisle:
            aisle_data = filtered_picks[filtered_picks['aisle'] == st.session_state.selected_aisle]
            
            if len(aisle_data) > 0:
                st.subheader(f"📊 Aisle {st.session_state.selected_aisle} Details")
                
                # Aisle metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Picks", f"{len(aisle_data):,}")
                col2.metric("SKUs", f"{aisle_data['sku_id'].nunique():,}")
                col3.metric("Locations", f"{aisle_data['location_id'].nunique()}")
                col4.metric("Categories", f"{aisle_data['category'].nunique()}")
                
                # Level breakdown
                level_summary = aisle_data.groupby('level').agg({
                    'pick_id': 'count',
                    'sku_id': 'nunique',
                    'location_id': 'nunique'
                }).reset_index()
                level_summary.columns = ['level', 'picks', 'skus', 'locations']
                
                fig_levels = px.bar(
                    level_summary,
                    x='level',
                    y='picks',
                    title=f"Pick Distribution by Level - {st.session_state.selected_aisle}",
                    color='picks',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_levels, use_container_width=True)
                
    else:
        st.warning("⚠️ No aisle data available for selected filters")

elif viz_type == "📊 Level Breakdown":
    st.subheader("📊 Level Analysis")
    
    if st.session_state.selected_aisle:
        aisle_data = filtered_picks[filtered_picks['aisle'] == st.session_state.selected_aisle]
        
        if len(aisle_data) > 0:
            # Level selection
            levels = sorted(aisle_data['level'].unique())
            selected_level = st.selectbox("📶 Select Level:", levels)
            
            if selected_level:
                st.session_state.selected_level = selected_level
                level_data = aisle_data[aisle_data['level'] == selected_level]
                
                st.subheader(f"📶 {st.session_state.selected_aisle} - Level {selected_level}")
                
                # Level metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Picks", f"{len(level_data):,}")
                col2.metric("SKUs", f"{level_data['sku_id'].nunique():,}")
                col3.metric("Bays Used", f"{level_data['bay'].nunique()}")
                col4.metric("Avg Picks/Bay", f"{len(level_data)/level_data['bay'].nunique():.1f}")
                
                # SKU breakdown for this level
                sku_summary = level_data.groupby(['sku_id', 'category']).agg({
                    'pick_id': 'count',
                    'quantity': 'sum'
                }).reset_index()
                sku_summary.columns = ['sku_id', 'category', 'picks', 'quantity']
                sku_summary = sku_summary.sort_values('picks', ascending=False)
                
                # Top SKUs chart
                top_skus = sku_summary.head(20)
                fig_skus = px.bar(
                    top_skus,
                    x='picks',
                    y='sku_id',
                    color='category',
                    title=f"Top 20 SKUs - {st.session_state.selected_aisle} Level {selected_level}",
                    orientation='h'
                )
                st.plotly_chart(fig_skus, use_container_width=True)
                
                # Category breakdown
                cat_summary = level_data.groupby('category').agg({
                    'pick_id': 'count',
                    'sku_id': 'nunique'
                }).reset_index()
                cat_summary.columns = ['category', 'picks', 'unique_skus']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_cat_picks = px.pie(
                        cat_summary,
                        values='picks',
                        names='category',
                        title="Picks by Category"
                    )
                    st.plotly_chart(fig_cat_picks, use_container_width=True)
                
                with col2:
                    fig_cat_skus = px.pie(
                        cat_summary,
                        values='unique_skus',
                        names='category',
                        title="SKUs by Category"
                    )
                    st.plotly_chart(fig_cat_skus, use_container_width=True)
        else:
            st.warning(f"⚠️ No data for aisle {st.session_state.selected_aisle}")
    else:
        st.info("👆 Please select an aisle first from the 'Aisle Heatmap' view")

elif viz_type == "📦 SKU Analysis":
    st.subheader("📦 SKU Deep Dive")
    
    # Overall SKU analysis
    sku_analysis = filtered_picks.groupby(['sku_id', 'category', 'velocity']).agg({
        'pick_id': 'count',
        'quantity': 'sum',
        'location_id': 'nunique'
    }).reset_index()
    sku_analysis.columns = ['sku_id', 'category', 'velocity', 'picks', 'quantity', 'locations']
    sku_analysis = sku_analysis.sort_values('picks', ascending=False)
    
    # Top SKUs overall
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏆 Top 20 SKUs by Pick Frequency**")
        top_skus_overall = sku_analysis.head(20)
        
        fig_top_skus = px.bar(
            top_skus_overall,
            x='picks',
            y='sku_id',
            color='category',
            title="Most Picked SKUs",
            orientation='h',
            height=600
        )
        st.plotly_chart(fig_top_skus, use_container_width=True)
    
    with col2:
        st.write("**📊 SKU Velocity Distribution**")
        velocity_stats = sku_analysis.groupby('velocity').agg({
            'picks': 'sum',
            'sku_id': 'count'
        }).reset_index()
        
        fig_velocity = px.bar(
            velocity_stats,
            x='velocity',
            y='picks',
            title="Picks by SKU Velocity",
            color='velocity',
            color_discrete_map={'high': 'red', 'medium': 'orange', 'low': 'blue'}
        )
        st.plotly_chart(fig_velocity, use_container_width=True)
    
    # SKU search and details
    st.subheader("🔍 SKU Search")
    search_sku = st.text_input("Search for specific SKU:", placeholder="e.g., ELECTRONICS_0001")
    
    if search_sku:
        sku_details = filtered_picks[filtered_picks['sku_id'].str.contains(search_sku, case=False)]
        
        if len(sku_details) > 0:
            st.success(f"Found {len(sku_details)} picks for SKUs matching '{search_sku}'")
            
            # SKU location heatmap
            sku_locations = sku_details.groupby(['aisle', 'level']).size().reset_index()
            sku_locations.columns = ['aisle', 'level', 'picks']
            
            if len(sku_locations) > 0:
                fig_sku_heat = px.density_heatmap(
                    sku_locations,
                    x='aisle',
                    y='level',
                    z='picks',
                    title=f"Storage Locations for '{search_sku}'",
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_sku_heat, use_container_width=True)
                
                # Detailed breakdown
                with st.expander("📋 Detailed Breakdown"):
                    st.dataframe(sku_details.groupby(['location_id', 'aisle', 'level']).agg({
                        'pick_id': 'count',
                        'quantity': 'sum',
                        'timestamp': ['min', 'max']
                    }).round(2))
        else:
            st.warning(f"No SKUs found matching '{search_sku}'")

# Footer with navigation help
st.markdown("---")
st.markdown("""
**🧭 Navigation Guide:**
1. **3D Digital Twin**: Explore the complete warehouse using reliable Plotly 3D
2. **Warehouse Structure**: View the physical framework and dimensions
3. **Aisle Heatmap**: Click on aisles to drill down to level analysis  
4. **Level Breakdown**: Analyze specific levels and their SKUs
5. **SKU Analysis**: Deep dive into product-level insights

**✅ Browser Compatibility**: This version uses Plotly instead of PyDeck for better browser support
""")
