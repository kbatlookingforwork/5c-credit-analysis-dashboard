import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from credit_scoring import CreditScoringEngine
from data_processor import DataProcessor
from visualizations import CreditVisualizations

# Page configuration
st.set_page_config(
    page_title="5C Credit Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'scoring_engine' not in st.session_state:
    st.session_state.scoring_engine = None

def load_data():
    """Load and process SME dataset"""
    try:
        data_processor = DataProcessor()
        
       # Look for CSV files with flexible naming
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        
        # Try to identify consumer and SME files
        consumer_file = None
        sme_file = None
        
        for file in csv_files:
            if 'consumer' in file.lower() or 'credit' in file.lower():
                consumer_file = file
            elif 'sme' in file.lower() or 'business' in file.lower():
                sme_file = file
        
        # Fallback: use any two CSV files if specific names not found
        if not consumer_file or not sme_file:
            if len(csv_files) >= 2:
                consumer_file = csv_files[0]
                sme_file = csv_files[1]
            elif len(csv_files) == 1:
                # Use the same file for both (will be handled by the processor)
                consumer_file = sme_file = csv_files[0]

        if not consumer_file or not sme_file:
            st.error(
                "⚠️ Dataset files not found. Please ensure CSV files are available in the project directory."
            )
            st.info(
                "Looking for files containing 'consumer', 'credit', 'sme', or 'business' in their names, or any CSV files."
            )
            if csv_files:
                st.info(f"Found CSV files: {', '.join(csv_files)}")
            return None

        st.info(f"Loading data from: {consumer_file} and {sme_file}")
        
        # Load the CSV files
        df1 = pd.read_csv(consumer_file)
        df2 = pd.read_csv(sme_file)
        
        # Process and merge the data
        processed_data = data_processor.process_sme_data(df1, df2)
        
        return processed_data
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    # Header
    st.title("🏦 5C Credit Analysis Dashboard")
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px;">
        <p style="font-weight: bold; color: green;">Created by:</p>
        <a href="https://www.linkedin.com/in/danyyudha" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" 
                 style="width: 20px; height: 20px;">
        </a>
        <p><b>Dany Yudha Putra Haque</b></p>
    </div>
""", unsafe_allow_html=True)
    st.markdown("---")

    
    # Sidebar for controls
    st.sidebar.title("📋 Analysis Controls")
    
    # Data loading section
    if not st.session_state.data_loaded:
        st.sidebar.markdown("### 📁 Data Loading")
        if st.sidebar.button("Load SME Dataset", type="primary"):
            with st.spinner("Loading and processing SME data..."):
                data = load_data()
                if data is not None:
                    st.session_state.processed_data = data
                    st.session_state.scoring_engine = CreditScoringEngine(data)
                    st.session_state.data_loaded = True
                    st.success("✅ Data loaded successfully!")
                    st.rerun()
    
    if not st.session_state.data_loaded:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## Welcome to the 5C Credit Analysis System
            
            This comprehensive credit analysis dashboard performs deep evaluation based on the **5 C's of Credit**:
            
            - **Character**: Borrower's creditworthiness and reputation
            - **Capacity**: Ability to repay the loan
            - **Capital**: Owner's investment and financial strength
            - **Collateral**: Assets securing the loan
            - **Conditions**: Economic and industry factors
            
            ### Features:
            - 📊 Interactive risk assessment visualizations
            - 📈 Real-time credit scoring engine
            - 📋 Individual borrower profile analysis
            - 📉 Portfolio-level risk distribution
            - 📄 Exportable analysis reports
            
            **Click 'Load SME Dataset' in the sidebar to begin analysis.**
            """)
        return
    
    # Main analysis interface
    data = st.session_state.processed_data
    scoring_engine = st.session_state.scoring_engine
    visualizer = CreditVisualizations(data)
    
    # Sidebar controls for loaded data
    st.sidebar.markdown("### ⚙️ Analysis Parameters")
    
    # Economic Scenario Selection
    st.sidebar.markdown("#### Economic Scenario")
    
    scenario_options = {
        "Normal Conditions": {
            'character': 0.20, 'capacity': 0.30, 'capital': 0.25, 
            'collateral': 0.15, 'conditions': 0.10, 'threshold': 0.60
        },
        "Crisis/Recession": {
            'character': 0.25, 'capacity': 0.20, 'capital': 0.30, 
            'collateral': 0.10, 'conditions': 0.30, 'threshold': 0.70
        },
        "MSME Expansion (KUR Program)": {
            'character': 0.15, 'capacity': 0.25, 'capital': 0.20, 
            'collateral': 0.30, 'conditions': 0.10, 'threshold': 0.55
        },
        "Government Budget Efficiency": {
            'character': 0.20, 'capacity': 0.30, 'capital': 0.25, 
            'collateral': 0.10, 'conditions': 0.40, 'threshold': 0.70
        },
        "Custom Configuration": {
            'character': 0.20, 'capacity': 0.30, 'capital': 0.25, 
            'collateral': 0.15, 'conditions': 0.10, 'threshold': 0.60
        }
    }
    
    selected_scenario = st.sidebar.selectbox(
        "Select Economic Scenario",
        list(scenario_options.keys()),
        help="Choose predefined scenario or use custom configuration"
    )
    
    # Display scenario description
    scenario_descriptions = {
        "Normal Conditions": "Capacity as primary consideration. Capital > Collateral emphasizes capital strength before collateral. 60% threshold.",
        "Crisis/Recession": "Emphasis on borrower character as credibility becomes crucial during uncertainty. Capital becomes important for operational support during crisis.",
        "MSME Expansion (KUR Program)": "Collateral becomes more important as MSMEs typically lack large capital structure. More flexible approval standards to support MSMEs.",
        "Government Budget Efficiency": "Economic conditions and fiscal policy have major impact. Banks are more cautious with stricter risk standards."
    }
    
    if selected_scenario in scenario_descriptions:
        st.sidebar.info(scenario_descriptions[selected_scenario])
    
    # Get scenario values
    scenario_config = scenario_options[selected_scenario]
    
    if selected_scenario == "Custom Configuration":
        st.sidebar.markdown("#### Custom 5C Weights (Make sure total sum of 5C is 1.0)")
        character_weight = st.sidebar.slider("Character Weight", 0.0, 1.0, scenario_config['character'], 0.05)
        capacity_weight = st.sidebar.slider("Capacity Weight", 0.0, 1.0, scenario_config['capacity'], 0.05)
        capital_weight = st.sidebar.slider("Capital Weight", 0.0, 1.0, scenario_config['capital'], 0.05)
        collateral_weight = st.sidebar.slider("Collateral Weight", 0.0, 1.0, scenario_config['collateral'], 0.05)
        conditions_weight = st.sidebar.slider("Conditions Weight", 0.0, 1.0, scenario_config['conditions'], 0.05)
        risk_threshold = st.sidebar.slider("Risk Threshold", 0.1, 1.0, scenario_config['threshold'], 0.05)
        
        # Normalize weights to sum to 1
        total_weight = character_weight + capacity_weight + capital_weight + collateral_weight + conditions_weight
        if total_weight > 0:
            weights = {
                'character': character_weight / total_weight,
                'capacity': capacity_weight / total_weight,
                'capital': capital_weight / total_weight,
                'collateral': collateral_weight / total_weight,
                'conditions': conditions_weight / total_weight
            }
        else:
            weights = scenario_config
    else:
        weights = {
            'character': scenario_config['character'],
            'capacity': scenario_config['capacity'],
            'capital': scenario_config['capital'],
            'collateral': scenario_config['collateral'],
            'conditions': scenario_config['conditions']
        }
        risk_threshold = scenario_config['threshold']
        
        # Display current weights
        st.sidebar.markdown("#### Current Configuration")
        st.sidebar.write(f"Character: {weights['character']:.2f}")
        st.sidebar.write(f"Capacity: {weights['capacity']:.2f}")
        st.sidebar.write(f"Capital: {weights['capital']:.2f}")
        st.sidebar.write(f"Collateral: {weights['collateral']:.2f}")
        st.sidebar.write(f"Conditions: {weights['conditions']:.2f}")
        st.sidebar.write(f"Risk Threshold: {risk_threshold:.2f}")
    
    scoring_engine.update_weights(weights)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Portfolio Overview", 
        "🔍 Individual Analysis", 
        "📈 5C Deep Dive", 
        "⚠️ Risk Assessment", 
        "📄 Reports"
    ])
    
    with tab1:
        portfolio_overview(data, scoring_engine, visualizer, risk_threshold)
    
    with tab2:
        individual_analysis(data, scoring_engine, visualizer)
    
    with tab3:
        five_c_deep_dive(data, scoring_engine, visualizer)
    
    with tab4:
        risk_assessment(data, scoring_engine, visualizer, risk_threshold)
    
    with tab5:
        reports_section(data, scoring_engine)

def portfolio_overview(data, scoring_engine, visualizer, risk_threshold):
    """Portfolio-level overview and analytics"""
    st.header("📊 Portfolio Overview")
    
    # Calculate portfolio metrics
    scores = scoring_engine.calculate_portfolio_scores()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = scores['total_score'].mean()
        st.metric("Average Credit Score", f"{avg_score:.2f}", f"{avg_score - 0.5:.2f}")
    
    with col2:
        high_risk_count = (scores['total_score'] < risk_threshold).sum()
        total_count = len(scores)
        st.metric("High Risk Applications", f"{high_risk_count}", f"{high_risk_count/total_count*100:.1f}%")
    
    with col3:
        approved_count = (scores['total_score'] >= risk_threshold).sum()
        st.metric("Approved Applications", f"{approved_count}", f"{approved_count/total_count*100:.1f}%")
    
    with col4:
        portfolio_value = data['loan_amount'].sum() if 'loan_amount' in data.columns else 0
        st.metric("Total Portfolio Value", f"${portfolio_value:,.0f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Credit Score Distribution")
        fig = visualizer.plot_score_distribution(scores['total_score'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Analysis**: This histogram shows the distribution of credit scores across your portfolio. 
        A normal distribution suggests balanced risk, while skewed distributions may indicate 
        concentration in specific risk categories.
        """)
    
    with col2:
        st.subheader("5C Components Breakdown")
        fig = visualizer.plot_5c_radar(scores)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Analysis**: The radar chart displays average performance across all 5 C's. 
        Areas closer to the center indicate weaker performance and potential focus areas 
        for portfolio improvement.
        """)
    
    # Risk segmentation
    st.subheader("Risk Segmentation Analysis")
    fig = visualizer.plot_risk_segments(scores, risk_threshold)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    **Analysis**: Applications are segmented based on the risk threshold of {risk_threshold:.2f}:
    - **Low Risk** (Green): Scores above threshold - recommended for approval
    - **Medium Risk** (Yellow): Scores near threshold - require additional review
    - **High Risk** (Red): Scores below threshold - recommend rejection or additional collateral
    """)

def individual_analysis(data, scoring_engine, visualizer):
    """Individual borrower analysis"""
    st.header("🔍 Individual Borrower Analysis")
    
 # Create borrower selection options with names
    borrower_options = {}
    borrower_display_names = []
    
    for idx, row in data.iterrows():
        # Determine display name based on borrower type
        if 'borrower_type' in row and pd.notnull(row['borrower_type']):
            if row['borrower_type'].lower() == 'sme':
                # For SME, use Business Name
                if 'borrower_name' in row and pd.notnull(row['borrower_name']):
                    display_name = f"[SME] {row['borrower_name']}"
                else:
                    display_name = f"[SME] Business #{idx + 1}"
            else:
                # For Consumer, use Name
                if 'borrower_name' in row and pd.notnull(row['borrower_name']):
                    display_name = f"[Consumer] {row['borrower_name']}"
                else:
                    display_name = f"[Consumer] Customer #{idx + 1}"
        else:
            # Fallback if borrower_type is not available
            if 'borrower_name' in row and pd.notnull(row['borrower_name']):
                display_name = str(row['borrower_name'])
            else:
                display_name = f"Borrower #{idx + 1}"
        
        borrower_options[display_name] = idx
        borrower_display_names.append(display_name)
    
    if borrower_display_names:
        selected_display_name = st.selectbox("Select Borrower", borrower_display_names)
        selected_idx = borrower_options[selected_display_name]
        
        # Get borrower data
        borrower_data = data.iloc[selected_idx]
        scores = scoring_engine.calculate_individual_scores(borrower_data)

        # Display borrower information
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Borrower Profile")
            st.write(f"**Selected**: {selected_display_name}")
            if 'borrower_id' in borrower_data and pd.notnull(borrower_data['borrower_id']):
                st.write(f"**ID**: {borrower_data['borrower_id']}")
            if 'borrower_name' in borrower_data and pd.notnull(borrower_data['borrower_name']):
                if 'borrower_type' in borrower_data and borrower_data['borrower_type'].lower() == 'sme':
                    st.write(f"**Business Name**: {borrower_data['borrower_name']}")
                else:
                    st.write(f"**Name**: {borrower_data['borrower_name']}")
            if 'borrower_type' in borrower_data:
                st.write(f"**Type**: {borrower_data['borrower_type'].title()}")
            if 'industry' in borrower_data and pd.notnull(borrower_data['industry']):
                st.write(f"**Industry**: {borrower_data['industry'].title()}")
            if 'loan_amount' in borrower_data and pd.notnull(borrower_data['loan_amount']):
                st.write(
                    f"**Requested Amount**: ${borrower_data['loan_amount']:,.0f}"
                )
    
    else:
        st.error("No borrower data available for analysis. Please check data structure.")

def five_c_deep_dive(data, scoring_engine, visualizer):
    """Deep dive into 5C analysis"""
    st.header("📈 5C Deep Dive Analysis")
    
    scores = scoring_engine.calculate_portfolio_scores()
    
    # 5C Correlation Analysis
    st.subheader("5C Component Correlations")
    fig = visualizer.plot_5c_correlation(scores)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Analysis**: This correlation matrix shows relationships between the 5 C's:
    - **Strong positive correlations** suggest components move together (good for diversification)
    - **Strong negative correlations** may indicate trade-offs between components
    - **Weak correlations** suggest independent risk factors
    """)
    
    # Component distribution analysis
    st.subheader("Individual Component Distributions")
    
    components = ['character_score', 'capacity_score', 'capital_score', 'collateral_score', 'conditions_score']
    
    col1, col2 = st.columns(2)
    
    for i, component in enumerate(components):
        if i % 2 == 0:
            with col1:
                fig = visualizer.plot_component_distribution(scores, component)
                st.plotly_chart(fig, use_container_width=True)
        else:
            with col2:
                fig = visualizer.plot_component_distribution(scores, component)
                st.plotly_chart(fig, use_container_width=True)
    
    # 5C Performance Trends
    st.subheader("5C Performance Comparison")
    fig = visualizer.plot_5c_performance_comparison(scores)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Analysis**: This box plot comparison shows:
    - **Median performance** for each C (center line)
    - **Distribution spread** (box height)
    - **Outliers** (points beyond whiskers)
    - **Performance consistency** across components
    """)
    
    # Enhanced visualizations for deeper analysis
    st.subheader("Advanced 5C Analysis")
    
    # Borrower type comparison
    st.markdown("#### Consumer vs SME Credit Profiles")
    fig_comparison = visualizer.plot_borrower_type_comparison(scores, data)
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    st.markdown("""
    **Analysis**: Compare credit profiles between individual consumers and small businesses:
    - **Consumer patterns**: Individual financial behavior and stability
    - **SME patterns**: Business financial health and operational factors
    - **Risk differences**: How borrower types perform across the 5 C's
    """)
    
    # Credit score relationship analysis
    st.markdown("#### Credit Score vs 5C Components Relationship")
    fig_credit_relation = visualizer.plot_credit_score_vs_5c(scores, data)
    st.plotly_chart(fig_credit_relation, use_container_width=True)
    
    st.markdown("""
    **Analysis**: Examine how traditional credit scores correlate with 5C components:
    - **Strong correlations**: Components that align with credit bureau scores
    - **Weak correlations**: Areas where 5C analysis provides additional insights
    - **Outliers**: Applications where 5C and credit scores diverge significantly
    """)
    
    # Industry risk analysis
    st.markdown("#### Industry Risk Patterns")
    fig_industry = visualizer.plot_industry_risk_analysis(scores, data)
    st.plotly_chart(fig_industry, use_container_width=True)
    
    st.markdown("""
    **Analysis**: Industry-specific risk patterns reveal:
    - **Healthcare**: Generally stable with consistent performance
    - **Technology**: Higher growth potential but increased volatility
    - **Retail**: Moderate risk with seasonal considerations
    - **Other sectors**: Baseline risk assessment patterns
    """)
    
    # Payment behavior analysis
    st.markdown("#### Payment Behavior Impact Analysis")
    fig_payment = visualizer.plot_payment_behavior_analysis(scores, data)
    st.plotly_chart(fig_payment, use_container_width=True)
    
    st.markdown("""
    **Analysis**: Payment history strongly influences credit performance:
    - **No delays**: Consistently higher credit scores across all metrics
    - **1-2 delays**: Slight impact but manageable risk level
    - **3-5 delays**: Moderate risk requiring closer monitoring
    - **6+ delays**: High risk with potential for default
    """)

def risk_assessment(data, scoring_engine, visualizer, risk_threshold):
    """Risk assessment and monitoring"""
    st.header("⚠️ Risk Assessment Dashboard")
    
    scores = scoring_engine.calculate_portfolio_scores()
    
    # Risk metrics
    high_risk = (scores['total_score'] < risk_threshold).sum()
    medium_risk = ((scores['total_score'] >= risk_threshold) & (scores['total_score'] < risk_threshold + 0.2)).sum()
    low_risk = (scores['total_score'] >= risk_threshold + 0.2).sum()
    total = len(scores)
    
    # Risk distribution
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🔴 High Risk", 
            f"{high_risk} ({high_risk/total*100:.1f}%)",
            delta=f"Threshold: <{risk_threshold:.2f}"
        )
    
    with col2:
        st.metric(
            "🟡 Medium Risk", 
            f"{medium_risk} ({medium_risk/total*100:.1f}%)",
            delta=f"Range: {risk_threshold:.2f}-{risk_threshold+0.2:.2f}"
        )
    
    with col3:
        st.metric(
            "🟢 Low Risk", 
            f"{low_risk} ({low_risk/total*100:.1f}%)",
            delta=f"Threshold: >{risk_threshold+0.2:.2f}"
        )
    
    # Risk visualization
    st.subheader("Risk Distribution Analysis")
    fig = visualizer.plot_risk_heatmap(scores, risk_threshold)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Risk Heatmap Analysis**: This visualization shows risk concentration across different score ranges:
    - **Dark red areas**: High concentration of risky applications
    - **Light areas**: Lower risk concentrations
    - **Distribution patterns**: Help identify systematic risk factors
    """)
    
    # High-risk applications table
    st.subheader("High-Risk Applications Requiring Review")
    
    high_risk_data = scores[scores['total_score'] < risk_threshold].copy()
    
    if len(high_risk_data) > 0:
        # Add borrower information by using the index to map back to original data
        high_risk_indices = high_risk_data.index
        
        # Select relevant columns for display
        display_data = []
        for idx in high_risk_indices:
            if idx < len(data):
                row_data = {
                    'index': idx,
                    'total_score': high_risk_data.loc[idx, 'total_score'],
                    'character_score': high_risk_data.loc[idx, 'character_score'],
                    'capacity_score': high_risk_data.loc[idx, 'capacity_score'],
                    'capital_score': high_risk_data.loc[idx, 'capital_score'],
                    'collateral_score': high_risk_data.loc[idx, 'collateral_score'],
                    'conditions_score': high_risk_data.loc[idx, 'conditions_score']
                }
                
                # Add available borrower information
                if 'borrower_id' in data.columns:
                    row_data['borrower_id'] = data.iloc[idx]['borrower_id']
                if 'borrower_name' in data.columns:
                    row_data['borrower_name'] = data.iloc[idx]['borrower_name']
                if 'industry' in data.columns:
                    row_data['industry'] = data.iloc[idx]['industry']
                if 'loan_amount' in data.columns:
                    row_data['loan_amount'] = data.iloc[idx]['loan_amount']
                if 'borrower_type' in data.columns:
                    row_data['borrower_type'] = data.iloc[idx]['borrower_type']
                
                display_data.append(row_data)
        
        high_risk_display = pd.DataFrame(display_data)
        
        st.dataframe(
            high_risk_display.round(3),
            use_container_width=True,
            hide_index=True
        )
        
        # Risk factor analysis
        st.subheader("Primary Risk Factors")
        fig = visualizer.plot_risk_factors(high_risk_data)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Risk Factor Analysis**: Shows which of the 5 C's contribute most to high-risk classifications:
        - **Character issues**: Credit history, reputation concerns
        - **Capacity problems**: Insufficient cash flow or debt service ability
        - **Capital deficiencies**: Low owner investment or equity
        - **Collateral inadequacy**: Insufficient security for the loan
        - **Conditions concerns**: Adverse economic or industry factors
        """)
    
    else:
        st.success("🎉 No high-risk applications identified with current threshold!")

def reports_section(data, scoring_engine):
    """Export and reporting functionality"""
    st.header("📄 Analysis Reports")
    
    scores = scoring_engine.calculate_portfolio_scores()
    
    # Report generation options
    st.subheader("Generate Analysis Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Portfolio Summary Report")
        if st.button("Generate Portfolio Report", type="primary"):
            # Generate portfolio summary
            report_data = {
                'Total Applications': len(scores),
                'Average Credit Score': scores['total_score'].mean(),
                'Standard Deviation': scores['total_score'].std(),
                'High Risk Count': (scores['total_score'] < 0.6).sum(),
                'Approval Rate': (scores['total_score'] >= 0.6).mean() * 100,
                'Character Avg': scores['character_score'].mean(),
                'Capacity Avg': scores['capacity_score'].mean(),
                'Capital Avg': scores['capital_score'].mean(),
                'Collateral Avg': scores['collateral_score'].mean(),
                'Conditions Avg': scores['conditions_score'].mean()
            }
            
            report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
            
            # Display report
            st.dataframe(report_df, use_container_width=True, hide_index=True)
            
            # Download link
            csv = report_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Portfolio Report",
                data=csv,
                file_name="portfolio_credit_analysis.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown("#### Detailed Scores Export")
        if st.button("Export Detailed Scores", type="secondary"):
            # Prepare detailed export
            export_data = scores.round(4)
            
            if 'borrower_id' in data.columns:
                # Select available columns for export
                export_columns = ['borrower_id']
                if 'borrower_name' in data.columns:
                    export_columns.append('borrower_name')
                if 'industry' in data.columns:
                    export_columns.append('industry')
                if 'borrower_type' in data.columns:
                    export_columns.append('borrower_type')
                if 'loan_amount' in data.columns:
                    export_columns.append('loan_amount')
                
                # Add borrower info by index mapping
                export_data = export_data.reset_index()
                for idx in export_data.index:
                    if idx < len(data):
                        for col in export_columns:
                            if col in data.columns:
                                export_data.loc[idx, col] = data.iloc[idx][col]
            
            st.dataframe(export_data, use_container_width=True, hide_index=True)
            
            # Download link
            csv = export_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Detailed Scores",
                data=csv,
                file_name="detailed_credit_scores.csv",
                mime="text/csv"
            )
    
    # Analysis insights
    st.subheader("Key Insights & Recommendations")
    
    avg_score = scores['total_score'].mean()
    risk_rate = (scores['total_score'] < 0.6).mean()
    
    insights = []
    
    if avg_score >= 0.7:
        insights.append("✅ **Strong Portfolio**: Average credit score indicates low overall risk.")
    elif avg_score >= 0.5:
        insights.append("⚠️ **Moderate Portfolio**: Average risk levels require ongoing monitoring.")
    else:
        insights.append("🚨 **High-Risk Portfolio**: Consider tightening lending criteria.")
    
    if risk_rate > 0.3:
        insights.append(f"📊 **High Rejection Rate**: {risk_rate*100:.1f}% of applications are high risk.")
    elif risk_rate > 0.1:
        insights.append(f"📊 **Moderate Rejection Rate**: {risk_rate*100:.1f}% rejection rate is within normal range.")
    else:
        insights.append(f"📊 **Low Rejection Rate**: {risk_rate*100:.1f}% rejection rate suggests conservative underwriting.")
    
    # Component-specific insights
    weakest_component = scores[['character_score', 'capacity_score', 'capital_score', 'collateral_score', 'conditions_score']].mean().idxmin()
    component_names = {
        'character_score': 'Character',
        'capacity_score': 'Capacity', 
        'capital_score': 'Capital',
        'collateral_score': 'Collateral',
        'conditions_score': 'Conditions'
    }
    
    insights.append(f"🎯 **Focus Area**: {component_names[weakest_component]} shows the lowest average scores and may need attention.")
    
    for insight in insights:
        st.markdown(insight)

if __name__ == "__main__":
    main()
