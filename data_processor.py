import pandas as pd
import numpy as np
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """
    Data processing pipeline for SME credit analysis
    Handles data cleaning, feature engineering, and financial ratio calculations
    """
    
    def __init__(self):
        self.processed_data = None
        
    def process_sme_data(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """
        Process and merge SME datasets
        """
        # Determine which dataset is credit consumers vs SMEs based on columns
        if 'CustomerID' in df1.columns and 'BusinessID' in df2.columns:
            consumers_df = df1
            smes_df = df2
        elif 'BusinessID' in df1.columns and 'CustomerID' in df2.columns:
            consumers_df = df2
            smes_df = df1
        else:
            # Default assignment if unclear
            consumers_df = df1
            smes_df = df2
        
        # Clean and prepare data
        consumers_clean = self._clean_dataframe(consumers_df)
        smes_clean = self._clean_dataframe(smes_df)
        
        # Process each dataset separately then combine
        consumers_processed = self._process_consumer_data(consumers_clean)
        smes_processed = self._process_sme_data_specific(smes_clean)
        
        # Combine both datasets for comprehensive analysis
        combined_data = self._combine_datasets(consumers_processed, smes_processed)
        
        # Calculate financial ratios
        processed_data = self._calculate_financial_ratios(combined_data)
        
        # Engineer additional features
        processed_data = self._engineer_features(processed_data)
        
        # Handle missing values
        processed_data = self._handle_missing_values(processed_data)
        
        self.processed_data = processed_data
        return processed_data
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean individual dataframe"""
        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Remove any completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Convert numeric columns
        numeric_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                converted = pd.to_numeric(df[col], errors='coerce')
                if not converted.isna().all():
                    df[col] = converted
                    numeric_columns.append(col)
        
        return df
    
    def _merge_datasets(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """Merge the two datasets intelligently"""
        # Look for common columns that could be used as keys
        common_cols = set(df1.columns).intersection(set(df2.columns))
        
        # Common ID-like column names
        id_candidates = ['id', 'borrower_id', 'company_id', 'application_id', 'customer_id']
        
        merge_key = None
        for candidate in id_candidates:
            if candidate in common_cols:
                merge_key = candidate
                break
        
        if merge_key and len(df1[merge_key].unique()) == len(df1) and len(df2[merge_key].unique()) == len(df2):
            # We have a unique key, perform inner merge
            merged = pd.merge(df1, df2, on=merge_key, how='inner', suffixes=('', '_y'))
            # Remove duplicate columns
            merged = merged.loc[:, ~merged.columns.str.endswith('_y')]
        else:
            # No clear merge key, concatenate horizontally if same number of rows
            if len(df1) == len(df2):
                # Reset indices and concatenate
                df1_reset = df1.reset_index(drop=True)
                df2_reset = df2.reset_index(drop=True)
                
                # Avoid column name conflicts
                df2_cols = {}
                for col in df2_reset.columns:
                    if col in df1_reset.columns:
                        df2_cols[col] = f"{col}_2"
                    else:
                        df2_cols[col] = col
                df2_reset = df2_reset.rename(columns=df2_cols)
                
                merged = pd.concat([df1_reset, df2_reset], axis=1)
            else:
                # Use the larger dataset and add summary info from smaller
                if len(df1) > len(df2):
                    merged = df1.copy()
                    # Add aggregate info from df2 if possible
                    for col in df2.select_dtypes(include=[np.number]).columns:
                        merged[f'{col}_market_avg'] = df2[col].mean()
                else:
                    merged = df2.copy()
                    # Add aggregate info from df1 if possible
                    for col in df1.select_dtypes(include=[np.number]).columns:
                        merged[f'{col}_market_avg'] = df1[col].mean()
        
        return merged
    
    def _process_consumer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process credit consumer data specifically"""
        # Map consumer columns to standard format
        column_mapping = {
            'customerid': 'borrower_id',
            'name': 'borrower_name',
            'age': 'age',
            'creditscore': 'credit_score_raw',
            'transactionamount': 'transaction_amount',
            'loanamount': 'loan_amount',
            'latepayments': 'payment_delays'
        }
        
        # Rename columns to standard format
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Create synthetic financial data for consumers based on their profile
        df['borrower_type'] = 'consumer'
        df['annual_income'] = df['transaction_amount'] * 12 * (1 + np.random.normal(0, 0.3, len(df)))
        df['current_assets'] = df['annual_income'] * np.random.uniform(0.1, 0.5, len(df))
        df['current_liabilities'] = df['loan_amount'] * np.random.uniform(0.8, 1.2, len(df))
        df['total_assets'] = df['current_assets'] * np.random.uniform(1.5, 3.0, len(df))
        df['total_equity'] = df['total_assets'] * np.random.uniform(0.2, 0.6, len(df))
        df['total_debt'] = df['total_assets'] - df['total_equity']
        
        # Consumer-specific credit metrics
        df['credit_history_years'] = np.maximum(1, df['age'] - 18 - np.random.poisson(3, len(df)))
        df['years_in_business'] = df['age'] - 18  # Working years for consumers
        df['management_experience'] = df['years_in_business'] * 0.6
        
        return df
    
    def _process_sme_data_specific(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process SME data specifically"""
        # Map SME columns to standard format
        column_mapping = {
            'businessid': 'borrower_id',
            'businessname': 'borrower_name',
            'annualrevenue': 'annual_revenue',
            'creditscore': 'credit_score_raw',
            'latepayments': 'payment_delays'
        }
        
        # Rename columns to standard format
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Create synthetic financial data for SMEs based on revenue
        df['borrower_type'] = 'sme'
        df['loan_amount'] = df['annual_revenue'] * np.random.uniform(0.1, 0.3, len(df))
        df['current_assets'] = df['annual_revenue'] * np.random.uniform(0.2, 0.8, len(df))
        df['current_liabilities'] = df['current_assets'] * np.random.uniform(0.4, 1.2, len(df))
        df['total_assets'] = df['annual_revenue'] * np.random.uniform(0.8, 2.5, len(df))
        df['total_equity'] = df['total_assets'] * np.random.uniform(0.2, 0.7, len(df))
        df['total_debt'] = df['total_assets'] - df['total_equity']
        
        # SME-specific metrics
        df['years_in_business'] = np.random.poisson(8, len(df)) + 1
        df['management_experience'] = df['years_in_business'] + np.random.poisson(3, len(df))
        df['credit_history_years'] = np.minimum(df['years_in_business'], np.random.poisson(5, len(df)) + 1)
        
        # Industry mapping
        df['industry'] = 'other'
        if 'industry_healthcare' in df.columns:
            df.loc[df['industry_healthcare'] == 1, 'industry'] = 'healthcare'
        if 'industry_retail' in df.columns:
            df.loc[df['industry_retail'] == 1, 'industry'] = 'retail'
        if 'industry_technology' in df.columns:
            df.loc[df['industry_technology'] == 1, 'industry'] = 'technology'
        
        return df
    
    def _combine_datasets(self, consumers_df: pd.DataFrame, smes_df: pd.DataFrame) -> pd.DataFrame:
        """Combine consumer and SME datasets"""
        # Ensure both datasets have the same columns
        all_columns = set(consumers_df.columns).union(set(smes_df.columns))
        
        # Add missing columns with appropriate defaults
        for col in all_columns:
            if col not in consumers_df.columns:
                if col in ['annual_revenue']:
                    consumers_df[col] = consumers_df.get('annual_income', 0)
                else:
                    consumers_df[col] = np.nan
            
            if col not in smes_df.columns:
                if col in ['annual_income']:
                    smes_df[col] = smes_df.get('annual_revenue', 0)
                elif col in ['age']:
                    smes_df[col] = 35  # Default business age
                else:
                    smes_df[col] = np.nan
        
        # Combine datasets
        combined_df = pd.concat([consumers_df, smes_df], ignore_index=True)
        return combined_df
    
    def _calculate_financial_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate key financial ratios for credit analysis"""
        # Current Ratio
        if 'current_assets' in df.columns and 'current_liabilities' in df.columns:
            df['current_ratio'] = np.where(
                df['current_liabilities'] != 0,
                df['current_assets'] / df['current_liabilities'],
                np.nan
            )
        
        # Quick Ratio
        if 'current_assets' in df.columns and 'inventory' in df.columns and 'current_liabilities' in df.columns:
            df['quick_ratio'] = np.where(
                df['current_liabilities'] != 0,
                (df['current_assets'] - df['inventory']) / df['current_liabilities'],
                np.nan
            )
        
        # Debt-to-Equity Ratio
        if 'total_debt' in df.columns and 'total_equity' in df.columns:
            df['debt_to_equity'] = np.where(
                df['total_equity'] != 0,
                df['total_debt'] / df['total_equity'],
                np.nan
            )
        elif 'total_liabilities' in df.columns and 'total_equity' in df.columns:
            df['debt_to_equity'] = np.where(
                df['total_equity'] != 0,
                df['total_liabilities'] / df['total_equity'],
                np.nan
            )
        
        # Debt Service Coverage Ratio
        if 'net_income' in df.columns and 'debt_service' in df.columns:
            df['debt_service_coverage_ratio'] = np.where(
                df['debt_service'] != 0,
                df['net_income'] / df['debt_service'],
                np.nan
            )
        elif 'ebitda' in df.columns and 'debt_service' in df.columns:
            df['debt_service_coverage_ratio'] = np.where(
                df['debt_service'] != 0,
                df['ebitda'] / df['debt_service'],
                np.nan
            )
        
        # Return on Assets
        if 'net_income' in df.columns and 'total_assets' in df.columns:
            df['return_on_assets'] = np.where(
                df['total_assets'] != 0,
                df['net_income'] / df['total_assets'],
                np.nan
            )
        
        # Return on Equity
        if 'net_income' in df.columns and 'total_equity' in df.columns:
            df['return_on_equity'] = np.where(
                df['total_equity'] != 0,
                df['net_income'] / df['total_equity'],
                np.nan
            )
        
        # Asset Turnover
        if 'revenue' in df.columns and 'total_assets' in df.columns:
            df['asset_turnover'] = np.where(
                df['total_assets'] != 0,
                df['revenue'] / df['total_assets'],
                np.nan
            )
        elif 'sales' in df.columns and 'total_assets' in df.columns:
            df['asset_turnover'] = np.where(
                df['total_assets'] != 0,
                df['sales'] / df['total_assets'],
                np.nan
            )
        
        # Working Capital
        if 'current_assets' in df.columns and 'current_liabilities' in df.columns:
            df['working_capital'] = df['current_assets'] - df['current_liabilities']
        
        # Equity Ratio
        if 'total_equity' in df.columns and 'total_assets' in df.columns:
            df['equity_ratio'] = np.where(
                df['total_assets'] != 0,
                df['total_equity'] / df['total_assets'],
                np.nan
            )
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features for credit analysis"""
        
        # Create borrower_id if not exists
        if 'borrower_id' not in df.columns:
            df['borrower_id'] = range(1, len(df) + 1)
        
        # Revenue growth calculation
        if 'revenue_current' in df.columns and 'revenue_previous' in df.columns:
            df['revenue_growth'] = np.where(
                df['revenue_previous'] != 0,
                (df['revenue_current'] - df['revenue_previous']) / df['revenue_previous'],
                np.nan
            )
        elif 'revenue' in df.columns and 'revenue_lag' in df.columns:
            df['revenue_growth'] = np.where(
                df['revenue_lag'] != 0,
                (df['revenue'] - df['revenue_lag']) / df['revenue_lag'],
                np.nan
            )
        
        # Loan-to-Value ratio
        if 'loan_amount' in df.columns and 'collateral_value' in df.columns:
            df['loan_to_value'] = np.where(
                df['collateral_value'] != 0,
                df['loan_amount'] / df['collateral_value'],
                np.nan
            )
        
        # Asset Coverage Ratio
        if 'total_assets' in df.columns and 'total_liabilities' in df.columns:
            df['asset_coverage_ratio'] = np.where(
                df['total_liabilities'] != 0,
                df['total_assets'] / df['total_liabilities'],
                np.nan
            )
        
        # Industry risk scoring (simplified)
        if 'industry' in df.columns:
            industry_risk_map = {
                'technology': 0.3,
                'healthcare': 0.2,
                'manufacturing': 0.4,
                'retail': 0.6,
                'construction': 0.7,
                'hospitality': 0.8,
                'oil_gas': 0.9
            }
            
            df['industry_risk'] = df['industry'].str.lower().map(
                lambda x: min([v for k, v in industry_risk_map.items() if k in str(x)] + [0.5])
                if pd.notnull(x) else 0.5
            )
        
        # Credit history normalization
        if 'credit_history' in df.columns:
            # Extract numeric years from credit history
            df['credit_history_years'] = pd.to_numeric(
                df['credit_history'].astype(str).str.extract('(\d+)')[0], 
                errors='coerce'
            ).fillna(0)
        
        # Management experience normalization
        if 'management_experience' in df.columns:
            df['management_experience'] = pd.to_numeric(
                df['management_experience'], errors='coerce'
            )
            if df['management_experience'].notna().any():
                df['management_experience'] = df['management_experience'].fillna(df['management_experience'].median())
            else:
                df['management_experience'] = df['management_experience'].fillna(5)
        
        # Payment delays normalization
        if 'payment_history' in df.columns:
            # Simple mapping of payment history to delay count
            payment_map = {
                'excellent': 0, 'good': 1, 'fair': 3, 'poor': 6, 'bad': 12
            }
            df['payment_delays'] = df['payment_history'].str.lower().map(payment_map).fillna(3)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        
        # For financial ratios, fill with industry medians or reasonable defaults
        ratio_columns = [
            'current_ratio', 'quick_ratio', 'debt_to_equity', 'debt_service_coverage_ratio',
            'return_on_assets', 'return_on_equity', 'asset_turnover', 'equity_ratio'
        ]
        
        for col in ratio_columns:
            if col in df.columns:
                if col == 'current_ratio':
                    df[col] = df[col].fillna(1.2)  # Conservative default
                elif col == 'debt_to_equity':
                    df[col] = df[col].fillna(1.0)  # Moderate leverage
                elif col == 'debt_service_coverage_ratio':
                    df[col] = df[col].fillna(1.1)  # Just above break-even
                elif col in ['return_on_assets', 'return_on_equity']:
                    df[col] = df[col].fillna(0.05)  # 5% return
                else:
                    df[col] = df[col].fillna(df[col].median())
        
        # For categorical variables
        categorical_defaults = {
            'industry': 'services',
            'collateral_type': 'business_assets',
            'market_position': 'moderate',
            'economic_outlook': 'stable'
        }
        
        for col, default_val in categorical_defaults.items():
            if col in df.columns:
                df[col] = df[col].fillna(default_val)
        
        # For numeric business metrics
        numeric_defaults = {
            'years_in_business': 5,
            'management_experience': 8,
            'credit_history_years': 3,
            'payment_delays': 2,
            'revenue_growth': 0.03,  # 3% growth
            'industry_growth': 0.02,  # 2% industry growth
            'loan_to_value': 0.8,
            'asset_coverage_ratio': 1.2
        }
        
        for col, default_val in numeric_defaults.items():
            if col in df.columns:
                df[col] = df[col].fillna(default_val)
        
        return df
    
    def get_data_summary(self) -> dict:
        """Get summary statistics of processed data"""
        if self.processed_data is None:
            return {"error": "No data processed yet"}
        
        df = self.processed_data
        
        summary = {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(df.select_dtypes(include=['object']).columns),
            "missing_values": df.isnull().sum().sum(),
            "key_metrics": {}
        }
        
        # Key financial metrics summary
        key_metrics = [
            'current_ratio', 'debt_to_equity', 'return_on_assets', 
            'revenue_growth', 'debt_service_coverage_ratio'
        ]
        
        for metric in key_metrics:
            if metric in df.columns:
                summary["key_metrics"][metric] = {
                    "mean": float(df[metric].mean()),
                    "median": float(df[metric].median()),
                    "std": float(df[metric].std())
                }
        
        return summary
