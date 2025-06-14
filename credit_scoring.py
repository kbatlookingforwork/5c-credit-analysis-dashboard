import pandas as pd
import numpy as np
from typing import Dict, Any

class CreditScoringEngine:
    """
    5C Credit Scoring Engine for SME credit analysis
    Implements Character, Capacity, Capital, Collateral, and Conditions scoring
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.weights = {
            'character': 0.20,
            'capacity': 0.30,
            'capital': 0.25,
            'collateral': 0.15,
            'conditions': 0.10
        }
        
    def update_weights(self, new_weights: Dict[str, float]):
        """Update scoring weights for 5C components"""
        self.weights = new_weights
    
    def calculate_character_score(self, row: pd.Series) -> float:
        """
        Calculate Character score based on:
        - Credit history
        - Business reputation
        - Management experience
        - Payment history
        """
        score = 0.0
        components = 0
        
        # Credit history score
        if 'credit_history_years' in row and pd.notnull(row['credit_history_years']):
            credit_years = float(row['credit_history_years'])
            score += min(credit_years / 10.0, 1.0) * 0.3
            components += 0.3
        
        # Payment history score - enhanced for your dataset
        if 'payment_delays' in row and pd.notnull(row['payment_delays']):
            delays = float(row['payment_delays'])
            if delays == 0:
                payment_score = 1.0  # Perfect payment history
            elif delays <= 2:
                payment_score = 0.8  # Good payment history
            elif delays <= 5:
                payment_score = 0.6  # Acceptable payment history
            else:
                payment_score = max(0.2, 1.0 - (delays / 10.0))  # Poor payment history
            score += payment_score * 0.35
            components += 0.35
        
        # Credit score factor - using raw credit score from your data
        if 'credit_score_raw' in row and pd.notnull(row['credit_score_raw']):
            raw_score = float(row['credit_score_raw'])
            # Normalize credit score (300-850 range typically)
            normalized_score = max(0, min(1, (raw_score - 300) / 550))
            score += normalized_score * 0.25
            components += 0.25
        
        # Management experience or business age
        if 'management_experience' in row and pd.notnull(row['management_experience']):
            experience = float(row['management_experience'])
            exp_score = min(experience / 15.0, 1.0)  # Normalize by 15 years
            score += exp_score * 0.1
            components += 0.1
        elif 'years_in_business' in row and pd.notnull(row['years_in_business']):
            business_years = float(row['years_in_business'])
            business_score = min(business_years / 10.0, 1.0)
            score += business_score * 0.1
            components += 0.1
        
        return score / components if components > 0 else 0.5
    
    def calculate_capacity_score(self, row: pd.Series) -> float:
        """
        Calculate Capacity score based on:
        - Income/Revenue adequacy
        - Transaction patterns
        - Loan amount relative to capacity
        - Financial stability indicators
        """
        score = 0.0
        components = 0
        
        # Income to loan ratio (capacity assessment)
        loan_amount = row.get('loan_amount', 0)
        if loan_amount > 0:
            # For consumers: use transaction amount as income proxy
            if 'transaction_amount' in row and pd.notnull(row['transaction_amount']):
                monthly_income = float(row['transaction_amount'])
                loan_to_income = loan_amount / (monthly_income * 12) if monthly_income > 0 else 999
                if loan_to_income <= 0.2:  # 20% or less
                    capacity_score = 1.0
                elif loan_to_income <= 0.4:  # 40% or less
                    capacity_score = 0.8
                elif loan_to_income <= 0.6:  # 60% or less
                    capacity_score = 0.6
                else:
                    capacity_score = max(0.2, 1.0 - (loan_to_income - 0.6) / 0.4 * 0.6)
                score += capacity_score * 0.4
                components += 0.4
            
            # For SMEs: use annual revenue
            elif 'annual_revenue' in row and pd.notnull(row['annual_revenue']):
                annual_revenue = float(row['annual_revenue'])
                loan_to_revenue = loan_amount / annual_revenue if annual_revenue > 0 else 999
                if loan_to_revenue <= 0.15:  # 15% or less
                    capacity_score = 1.0
                elif loan_to_revenue <= 0.25:  # 25% or less
                    capacity_score = 0.8
                elif loan_to_revenue <= 0.35:  # 35% or less
                    capacity_score = 0.6
                else:
                    capacity_score = max(0.2, 1.0 - (loan_to_revenue - 0.35) / 0.35 * 0.6)
                score += capacity_score * 0.4
                components += 0.4
        
        # Current Ratio (if available)
        if 'current_ratio' in row and pd.notnull(row['current_ratio']):
            current_ratio = float(row['current_ratio'])
            if current_ratio >= 2.0:
                cr_score = 1.0
            elif current_ratio >= 1.5:
                cr_score = 0.8
            elif current_ratio >= 1.0:
                cr_score = 0.6
            else:
                cr_score = max(0, current_ratio * 0.4)
            score += cr_score * 0.3
            components += 0.3
        
        # Age/Experience factor (stability indicator)
        if 'age' in row and pd.notnull(row['age']):
            age = float(row['age'])
            if age >= 45:  # Mature, stable
                age_score = 1.0
            elif age >= 35:  # Experienced
                age_score = 0.8
            elif age >= 25:  # Developing
                age_score = 0.6
            else:
                age_score = 0.4  # Young, less stable
            score += age_score * 0.2
            components += 0.2
        elif 'years_in_business' in row and pd.notnull(row['years_in_business']):
            years = float(row['years_in_business'])
            business_score = min(years / 10.0, 1.0)  # 10+ years = max score
            score += business_score * 0.2
            components += 0.2
        
        # Credit score influence on capacity
        if 'credit_score_raw' in row and pd.notnull(row['credit_score_raw']):
            raw_score = float(row['credit_score_raw'])
            # Higher credit score indicates better capacity management
            normalized_score = max(0, min(1, (raw_score - 300) / 550))
            score += normalized_score * 0.1
            components += 0.1
        
        return score / components if components > 0 else 0.5
    
    def calculate_capital_score(self, row: pd.Series) -> float:
        """
        Calculate Capital score based on:
        - Debt-to-equity ratio
        - Owner's investment
        - Retained earnings
        - Financial leverage
        """
        score = 0.0
        components = 0
        
        # Debt-to-equity ratio
        if 'debt_to_equity' in row and pd.notnull(row['debt_to_equity']):
            dte = float(row['debt_to_equity'])
            if dte <= 0.5:
                dte_score = 1.0
            elif dte <= 1.0:
                dte_score = 0.8
            elif dte <= 2.0:
                dte_score = 0.6
            else:
                dte_score = max(0, (4.0 - dte) / 4.0 * 0.4)
            score += dte_score * 0.4
            components += 0.4
        
        # Equity ratio
        if 'equity_ratio' in row and pd.notnull(row['equity_ratio']):
            equity_ratio = float(row['equity_ratio'])
            equity_score = min(equity_ratio * 2, 1.0)  # Normalize around 50%
            score += equity_score * 0.35
            components += 0.35
        
        # Working capital adequacy
        if 'working_capital' in row and 'total_assets' in row:
            if pd.notnull(row['working_capital']) and pd.notnull(row['total_assets']):
                wc_ratio = float(row['working_capital']) / float(row['total_assets'])
                wc_score = max(0, min(wc_ratio * 4, 1.0))  # Normalize around 25%
                score += wc_score * 0.25
                components += 0.25
        
        return score / components if components > 0 else 0.5
    
    def calculate_collateral_score(self, row: pd.Series) -> float:
        """
        Calculate Collateral score based on:
        - Loan-to-value ratio
        - Asset quality
        - Liquidation value
        - Security coverage
        """
        score = 0.0
        components = 0
        
        # Loan-to-value ratio
        if 'loan_to_value' in row and pd.notnull(row['loan_to_value']):
            ltv = float(row['loan_to_value'])
            if ltv <= 0.6:
                ltv_score = 1.0
            elif ltv <= 0.8:
                ltv_score = 0.8
            elif ltv <= 1.0:
                ltv_score = 0.6
            else:
                ltv_score = max(0, (1.5 - ltv) / 0.5 * 0.4)
            score += ltv_score * 0.5
            components += 0.5
        
        # Asset coverage ratio
        if 'asset_coverage_ratio' in row and pd.notnull(row['asset_coverage_ratio']):
            acr = float(row['asset_coverage_ratio'])
            if acr >= 2.0:
                acr_score = 1.0
            elif acr >= 1.5:
                acr_score = 0.8
            elif acr >= 1.0:
                acr_score = 0.6
            else:
                acr_score = max(0, acr * 0.4)
            score += acr_score * 0.3
            components += 0.3
        
        # Collateral quality
        if 'collateral_type' in row and pd.notnull(row['collateral_type']):
            collateral_type = str(row['collateral_type']).lower()
            if 'real_estate' in collateral_type or 'property' in collateral_type:
                quality_score = 1.0
            elif 'equipment' in collateral_type or 'machinery' in collateral_type:
                quality_score = 0.8
            elif 'inventory' in collateral_type:
                quality_score = 0.6
            elif 'receivables' in collateral_type:
                quality_score = 0.5
            else:
                quality_score = 0.4
            score += quality_score * 0.2
            components += 0.2
        
        return score / components if components > 0 else 0.5
    
    def calculate_conditions_score(self, row: pd.Series) -> float:
        """
        Calculate Conditions score based on:
        - Industry risk factors
        - Economic stability indicators
        - Market conditions
        - Borrower type considerations
        """
        score = 0.0
        components = 0
        
        # Industry risk assessment (from your SME data)
        if 'industry' in row and pd.notnull(row['industry']):
            industry = str(row['industry']).lower()
            if industry == 'healthcare':
                industry_score = 0.9  # Stable, essential services
            elif industry == 'technology':
                industry_score = 0.7  # Growth potential but volatile
            elif industry == 'retail':
                industry_score = 0.6  # Moderate risk, cyclical
            else:
                industry_score = 0.5  # Default for other industries
            score += industry_score * 0.4
            components += 0.4
        
        # Borrower type risk consideration
        if 'borrower_type' in row and pd.notnull(row['borrower_type']):
            borrower_type = str(row['borrower_type']).lower()
            if borrower_type == 'consumer':
                # Individual consumers generally have more stable employment
                type_score = 0.7
            elif borrower_type == 'sme':
                # SMEs face more market volatility
                type_score = 0.6
            else:
                type_score = 0.5
            score += type_score * 0.3
            components += 0.3
        
        # Economic stability based on credit score trends
        if 'credit_score_raw' in row and pd.notnull(row['credit_score_raw']):
            raw_score = float(row['credit_score_raw'])
            # Higher credit scores indicate better economic conditions for borrower
            if raw_score >= 750:
                econ_score = 0.9  # Excellent economic position
            elif raw_score >= 650:
                econ_score = 0.7  # Good economic position
            elif raw_score >= 550:
                econ_score = 0.5  # Fair economic position
            else:
                econ_score = 0.3  # Challenging economic position
            score += econ_score * 0.2
            components += 0.2
        
        # Transaction volume as market activity indicator
        if 'transaction_amount' in row and pd.notnull(row['transaction_amount']):
            transaction_amount = float(row['transaction_amount'])
            # Higher transaction amounts indicate active market participation
            if transaction_amount >= 7000:
                activity_score = 0.8
            elif transaction_amount >= 4000:
                activity_score = 0.6
            elif transaction_amount >= 2000:
                activity_score = 0.5
            else:
                activity_score = 0.3
            score += activity_score * 0.1
            components += 0.1
        elif 'annual_revenue' in row and pd.notnull(row['annual_revenue']):
            annual_revenue = float(row['annual_revenue'])
            # Higher revenue indicates better market conditions
            if annual_revenue >= 3000000:
                activity_score = 0.8
            elif annual_revenue >= 1500000:
                activity_score = 0.6
            elif annual_revenue >= 500000:
                activity_score = 0.5
            else:
                activity_score = 0.3
            score += activity_score * 0.1
            components += 0.1
        
        return score / components if components > 0 else 0.5
    
    def calculate_individual_scores(self, row: pd.Series) -> Dict[str, float]:
        """Calculate all 5C scores for an individual borrower"""
        scores = {
            'character_score': self.calculate_character_score(row),
            'capacity_score': self.calculate_capacity_score(row),
            'capital_score': self.calculate_capital_score(row),
            'collateral_score': self.calculate_collateral_score(row),
            'conditions_score': self.calculate_conditions_score(row)
        }
        
        # Calculate weighted total score
        total_score = sum(scores[f'{component}_score'] * weight 
                         for component, weight in self.weights.items())
        scores['total_score'] = total_score
        
        return scores
    
    def calculate_portfolio_scores(self) -> pd.DataFrame:
        """Calculate scores for entire portfolio"""
        portfolio_scores = []
        
        for idx, row in self.data.iterrows():
            scores = self.calculate_individual_scores(row)
            scores['index'] = idx
            portfolio_scores.append(scores)
        
        scores_df = pd.DataFrame(portfolio_scores)
        scores_df.set_index('index', inplace=True)
        
        return scores_df
    
    def get_risk_assessment(self, score: float) -> Dict[str, Any]:
        """Get risk assessment based on credit score"""
        if score >= 0.8:
            return {
                'risk_level': 'Very Low',
                'recommendation': 'Approve',
                'color': 'green',
                'description': 'Excellent creditworthiness with minimal risk'
            }
        elif score >= 0.7:
            return {
                'risk_level': 'Low',
                'recommendation': 'Approve',
                'color': 'lightgreen',
                'description': 'Good creditworthiness with low risk'
            }
        elif score >= 0.6:
            return {
                'risk_level': 'Medium',
                'recommendation': 'Approve with Conditions',
                'color': 'yellow',
                'description': 'Acceptable risk with monitoring required'
            }
        elif score >= 0.4:
            return {
                'risk_level': 'High',
                'recommendation': 'Additional Review Required',
                'color': 'orange',
                'description': 'Higher risk requiring additional analysis'
            }
        else:
            return {
                'risk_level': 'Very High',
                'recommendation': 'Reject or Require Additional Collateral',
                'color': 'red',
                'description': 'High risk of default'
            }
