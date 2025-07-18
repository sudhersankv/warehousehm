def get_styles():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Reset and Base Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }

    /* Main Application Background */
    .stApp {
        background: linear-gradient(135deg, #fafcfb 0%, #f1f9f3 50%, #e8f5ed 100%);
        min-height: 100vh;
    }

    /* Header Container */
    .se-header {
        background: linear-gradient(135deg, #00954A 0%, #007C3E 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 32px;
        box-shadow: 
            0 8px 32px rgba(0, 149, 74, 0.25),
            0 2px 8px rgba(0, 149, 74, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }

    .se-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
        pointer-events: none;
    }

    .se-header-content {
        display: flex;
        align-items: center;
        gap: 20px;
        position: relative;
        z-index: 1;
    }

    .se-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .se-header p {
        color: rgba(255, 255, 255, 0.95) !important;
        margin: 4px 0 0 0;
        font-size: 1rem;
        font-weight: 400;
        letter-spacing: 0.2px;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #004A28 !important;
        font-weight: 600;
        letter-spacing: -0.3px;
    }

    .stMarkdown {
        color: #005A32;
    }

    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #00954A 0%, #007C3E 100%);
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 12px;
        height: 48px;
        padding: 0 24px;
        border: none;
        box-shadow: 
            0 4px 16px rgba(0, 149, 74, 0.35),
            0 2px 4px rgba(0, 149, 74, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.3px;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #007C3E 0%, #006432 100%);
        box-shadow: 
            0 6px 24px rgba(0, 149, 74, 0.45),
            0 4px 8px rgba(0, 149, 74, 0.3);
        transform: translateY(-2px);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Input Field Styles */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border: 2px solid #D6F0E1;
        border-radius: 10px;
        color: #004A28 !important;
        background-color: white;
        font-weight: 500;
        padding: 12px 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00954A;
        box-shadow: 
            0 0 0 4px rgba(0, 149, 74, 0.15),
            0 4px 12px rgba(0, 149, 74, 0.2);
        outline: none;
    }

    /* Label Styles */
    label {
        color: #004A28 !important;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.2px;
        margin-bottom: 8px;
    }

    /* Alert Boxes */
    .stSuccess {
        background: linear-gradient(135deg, #C8F0D6 0%, #B5E8C5 100%);
        border: 1px solid #00954A;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 149, 74, 0.15);
    }

    .stInfo {
        background: linear-gradient(135deg, #E8F5ED 0%, #D6F0E1 100%);
        border: 1px solid #4CAF50;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
    }

    .stError {
        background: linear-gradient(135deg, #ffe0e0 0%, #ffcdd2 100%);
        border: 1px solid #f44336;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(244, 67, 54, 0.1);
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #fafcfb 0%, #f1f9f3 100%);
        border-right: 1px solid #D6F0E1;
    }

    /* Section Headers in Sidebar */
    .css-1d391kg h2 {
        color: #004A28 !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #D6F0E1;
    }

    /* DataFrames */
    .stDataFrame {
        background-color: white;
        border-radius: 12px;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.08),
            0 2px 4px rgba(0, 0, 0, 0.04);
        border: 1px solid #D6F0E1;
        overflow: hidden;
    }

    /* Layer Analysis Cards */
    .layer-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #00954A;
        margin: 16px 0;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.06),
            0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #E8F5ED;
    }

    .layer-card:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.1),
            0 4px 8px rgba(0, 0, 0, 0.04);
    }

    .layer-card h4 {
        color: #004A28 !important;
        margin: 0 0 12px 0;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .layer-card p {
        margin: 8px 0;
        color: #005A32;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .orientation-badge {
        background: linear-gradient(135deg, #00954A 0%, #007C3E 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0 4px;
        box-shadow: 0 2px 8px rgba(0, 149, 74, 0.4);
        display: inline-block;
    }

    /* Configuration Summary Cards */
    .config-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.06),
            0 2px 4px rgba(0, 0, 0, 0.02);
        border: 1px solid #D6F0E1;
        margin: 16px 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #00954A;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
        margin-top: 48px;
        padding: 24px;
        border-top: 1px solid #D6F0E1;
        background: linear-gradient(135deg, #fafcfb 0%, #f1f9f3 100%);
    }

    /* Visualization Container */
    .viz-container {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.06),
            0 2px 4px rgba(0, 0, 0, 0.02);
        border: 1px solid #D6F0E1;
        margin: 8px 0;
    }

    .viz-container h4 {
        margin: 0 0 12px 0;
        text-align: center;
        color: #004A28;
        font-weight: 600;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f9f3;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: #00954A;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #007C3E;
    }

    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Remove default streamlit styling */
    .css-1v0mbdj {
        margin-top: -76px;
    }

    .css-18e3th9 {
        padding-top: 32px;
    }
    </style>
    """