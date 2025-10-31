"""
Lifetime Risk Projection Module

This module provides comprehensive lifetime risk projections for genetic conditions,
incorporating age-specific incidence rates, PRS modifiers, and competing risks.
"""

import os
import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from scipy.integrate import cumulative_trapezoid


class LifetimeRiskCalculator:
    """
    Main class for calculating lifetime risk projections
    """

    def __init__(self, risk_data_path: str = "datasets/age_specific_risks.tsv"):
        """
        Initialize lifetime risk calculator

        Args:
            risk_data_path: Path to age-specific risk data
        """
        self.risk_data_path = risk_data_path
        self.risk_data = None
        self.life_expectancy_data = None
        self._load_risk_data()

    def _load_risk_data(self):
        """Load age-specific risk data and life expectancy tables."""
        try:
            if os.path.exists(self.risk_data_path):
                self.risk_data = pd.read_csv(self.risk_data_path, sep="\t")
            else:
                # Create default risk data if file doesn't exist
                self._create_default_risk_data()
        except Exception as e:
            print(f"Error loading risk data: {e}")
            self._create_default_risk_data()

        # Load life expectancy data
        self._load_life_expectancy_data()

    def _create_default_risk_data(self):
        """Create default age-specific risk data for common conditions."""
        # Age ranges and conditions
        ages = list(range(20, 101, 5))  # 20, 25, 30, ..., 100
        conditions = [
            "breast_cancer",
            "prostate_cancer",
            "colorectal_cancer",
            "coronary_artery_disease",
            "type_2_diabetes",
            "alzheimers_disease",
        ]

        risk_data = []

        # Base incidence rates (per 100,000 person-years) - approximate values
        base_rates = {
            "breast_cancer": {
                "female": [
                    25,
                    50,
                    100,
                    200,
                    350,
                    500,
                    600,
                    550,
                    400,
                    250,
                    150,
                    80,
                    40,
                    20,
                    10,
                    5,
                ],
                "male": [0.5, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1, 0.5, 0.2, 0.1, 0.05],
            },
            "prostate_cancer": {
                "male": [
                    10,
                    20,
                    50,
                    150,
                    300,
                    600,
                    1000,
                    1200,
                    1000,
                    800,
                    600,
                    400,
                    200,
                    100,
                    50,
                    20,
                ],
                "female": [
                    0.1,
                    0.2,
                    0.5,
                    1,
                    1.5,
                    2,
                    2.5,
                    2,
                    1.5,
                    1,
                    0.5,
                    0.2,
                    0.1,
                    0.05,
                    0.02,
                    0.01,
                ],
            },
            "colorectal_cancer": {
                "female": [
                    5,
                    10,
                    20,
                    40,
                    80,
                    120,
                    150,
                    140,
                    120,
                    100,
                    80,
                    60,
                    40,
                    25,
                    15,
                    8,
                ],
                "male": [
                    8,
                    15,
                    30,
                    60,
                    120,
                    180,
                    220,
                    200,
                    170,
                    140,
                    110,
                    80,
                    50,
                    30,
                    18,
                    10,
                ],
            },
            "coronary_artery_disease": {
                "female": [
                    20,
                    30,
                    50,
                    100,
                    200,
                    400,
                    600,
                    700,
                    600,
                    500,
                    400,
                    300,
                    200,
                    100,
                    50,
                    20,
                ],
                "male": [
                    50,
                    80,
                    150,
                    300,
                    600,
                    1000,
                    1400,
                    1500,
                    1300,
                    1100,
                    900,
                    700,
                    500,
                    300,
                    150,
                    50,
                ],
            },
            "type_2_diabetes": {
                "female": [
                    50,
                    80,
                    120,
                    200,
                    350,
                    500,
                    600,
                    550,
                    450,
                    350,
                    250,
                    150,
                    80,
                    40,
                    20,
                    10,
                ],
                "male": [
                    60,
                    100,
                    150,
                    250,
                    450,
                    650,
                    800,
                    750,
                    600,
                    450,
                    300,
                    180,
                    100,
                    50,
                    25,
                    12,
                ],
            },
            "alzheimers_disease": {
                "female": [
                    10,
                    15,
                    25,
                    50,
                    100,
                    200,
                    400,
                    600,
                    700,
                    600,
                    400,
                    200,
                    100,
                    50,
                    25,
                    10,
                ],
                "male": [
                    8,
                    12,
                    20,
                    40,
                    80,
                    150,
                    300,
                    450,
                    550,
                    500,
                    350,
                    200,
                    100,
                    50,
                    25,
                    10,
                ],
            },
        }

        for condition in conditions:
            for i, age in enumerate(ages):
                for sex in ["male", "female"]:
                    if sex in base_rates[condition]:
                        rate = (
                            base_rates[condition][sex][i] / 100000
                        )  # Convert to proportion
                        risk_data.append(
                            {
                                "condition": condition,
                                "sex": sex,
                                "age_start": age,
                                "age_end": age + 4,
                                "incidence_rate": rate,
                                "cumulative_risk": 0.0,  # Will be calculated
                            }
                        )

        self.risk_data = pd.DataFrame(risk_data)

    def _load_life_expectancy_data(self):
        """Load life expectancy data by age and sex."""
        # Simplified life expectancy data (years remaining)
        life_expectancy = {
            "male": {
                20: 58.2,
                25: 53.8,
                30: 49.4,
                35: 45.0,
                40: 40.7,
                45: 36.4,
                50: 32.2,
                55: 28.1,
                60: 24.1,
                65: 20.3,
                70: 16.6,
                75: 13.1,
                80: 9.9,
                85: 7.1,
                90: 4.9,
                95: 3.2,
                100: 2.0,
            },
            "female": {
                20: 61.8,
                25: 57.2,
                30: 52.6,
                35: 48.0,
                40: 43.5,
                45: 39.0,
                50: 34.6,
                55: 30.3,
                60: 26.1,
                65: 22.1,
                70: 18.2,
                75: 14.4,
                80: 11.0,
                85: 8.0,
                90: 5.6,
                95: 3.7,
                100: 2.3,
            },
        }
        self.life_expectancy_data = life_expectancy

    def calculate_lifetime_risk(
        self,
        condition: str,
        current_age: int,
        sex: str,
        prs_percentile: float = 50.0,
        ancestry: str = "European",
        lifestyle_modifier: float = 1.0,
        competing_risks: bool = True,
    ) -> Dict:
        """
        Calculate lifetime risk projection for a specific condition

        Args:
            condition: Condition name (e.g., 'breast_cancer')
            current_age: Current age in years
            sex: 'male' or 'female'
            prs_percentile: PRS percentile (0-100)
            ancestry: Ancestry group
            lifestyle_modifier: Lifestyle risk modifier (0.5-2.0)
            competing_risks: Whether to account for competing mortality

        Returns:
            Dictionary with lifetime risk results
        """
        if self.risk_data is None:
            return {"success": False, "error": "Risk data not available"}

        try:
            # Get age-specific rates for the condition
            condition_data = self.risk_data[
                (self.risk_data["condition"] == condition)
                & (self.risk_data["sex"] == sex)
            ].copy()

            if condition_data.empty:
                return {
                    "success": False,
                    "error": f"No data available for {condition} in {sex}s",
                }

            # Apply PRS modifier
            prs_modifier = self._calculate_prs_modifier(prs_percentile, condition)

            # Apply ancestry modifier
            ancestry_modifier = self._calculate_ancestry_modifier(ancestry, condition)

            # Apply lifestyle modifier
            total_modifier = prs_modifier * ancestry_modifier * lifestyle_modifier

            # Calculate age-specific risks
            condition_data["adjusted_rate"] = (
                condition_data["incidence_rate"] * total_modifier
            )

            # Calculate cumulative risk from current age
            risk_trajectory = self._calculate_risk_trajectory(
                condition_data, current_age, competing_risks
            )

            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                risk_trajectory, condition_data
            )

            # Calculate different scenarios
            scenarios = self._calculate_risk_scenarios(
                condition_data,
                current_age,
                competing_risks,
                prs_percentile,
                ancestry,
                lifestyle_modifier,
            )

            result = {
                "success": True,
                "condition": condition,
                "current_age": current_age,
                "sex": sex,
                "lifetime_risk": risk_trajectory["cumulative_risk"].iloc[-1],
                "risk_trajectory": risk_trajectory,
                "confidence_intervals": confidence_intervals,
                "scenarios": scenarios,
                "modifiers": {
                    "prs_modifier": prs_modifier,
                    "ancestry_modifier": ancestry_modifier,
                    "lifestyle_modifier": lifestyle_modifier,
                    "total_modifier": total_modifier,
                },
                "parameters": {
                    "prs_percentile": prs_percentile,
                    "ancestry": ancestry,
                    "competing_risks": competing_risks,
                },
            }

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_prs_modifier(self, prs_percentile: float, condition: str) -> float:
        """Calculate PRS-based risk modifier."""
        # PRS effect sizes vary by condition
        prs_effects = {
            "breast_cancer": 2.5,  # OR per SD increase
            "prostate_cancer": 2.8,
            "colorectal_cancer": 1.8,
            "coronary_artery_disease": 1.6,
            "type_2_diabetes": 1.7,
            "alzheimers_disease": 1.4,
        }

        effect_size = prs_effects.get(condition, 2.0)

        # Convert percentile to z-score
        if prs_percentile <= 0:
            z_score = -4.0
        elif prs_percentile >= 100:
            z_score = 4.0
        else:
            z_score = stats.norm.ppf(prs_percentile / 100)

        # Calculate odds ratio
        odds_ratio = effect_size**z_score

        # Convert OR to risk ratio (approximation for common diseases)
        risk_ratio = odds_ratio / (1 + odds_ratio - 1)

        return risk_ratio

    def _calculate_ancestry_modifier(self, ancestry: str, condition: str) -> float:
        """Calculate ancestry-based risk modifier."""
        # Ancestry-specific risk modifiers (relative to European)
        ancestry_modifiers = {
            "breast_cancer": {
                "European": 1.0,
                "African": 0.8,
                "East_Asian": 0.6,
                "South_Asian": 0.9,
                "American": 0.85,
            },
            "prostate_cancer": {
                "European": 1.0,
                "African": 1.8,
                "East_Asian": 0.5,
                "South_Asian": 0.8,
                "American": 1.2,
            },
            "colorectal_cancer": {
                "European": 1.0,
                "African": 0.9,
                "East_Asian": 0.7,
                "South_Asian": 1.2,
                "American": 1.0,
            },
            "coronary_artery_disease": {
                "European": 1.0,
                "African": 1.2,
                "East_Asian": 0.8,
                "South_Asian": 1.5,
                "American": 1.3,
            },
            "type_2_diabetes": {
                "European": 1.0,
                "African": 1.4,
                "East_Asian": 1.1,
                "South_Asian": 2.0,
                "American": 1.6,
            },
            "alzheimers_disease": {
                "European": 1.0,
                "African": 0.8,
                "East_Asian": 0.7,
                "South_Asian": 0.9,
                "American": 1.0,
            },
        }

        ancestry_key = ancestry.split()[0] if " " in ancestry else ancestry
        condition_modifiers = ancestry_modifiers.get(condition, {})
        return condition_modifiers.get(ancestry_key, 1.0)

    def _calculate_risk_trajectory(
        self, condition_data: pd.DataFrame, current_age: int, competing_risks: bool
    ) -> pd.DataFrame:
        """Calculate risk trajectory over lifetime."""
        # Filter data for ages >= current_age
        future_data = condition_data[condition_data["age_start"] >= current_age].copy()

        if future_data.empty:
            # If no data for future ages, extrapolate
            future_data = condition_data.copy()
            future_data["age_start"] = future_data["age_start"] + (
                current_age - future_data["age_start"].min()
            )

        # Sort by age
        future_data = future_data.sort_values("age_start")

        # Calculate cumulative risk
        ages = future_data["age_start"].values
        rates = future_data["adjusted_rate"].values

        # Calculate survival probabilities if competing risks
        if competing_risks:
            survival_probs = self._calculate_survival_probabilities(
                ages, future_data["sex"].iloc[0]
            )
            rates = rates * survival_probs

        # Calculate cumulative incidence
        cumulative_risk = np.zeros_like(rates)
        for i in range(len(rates)):
            if i == 0:
                cumulative_risk[i] = rates[i] * 5  # 5-year interval
            else:
                cumulative_risk[i] = cumulative_risk[i - 1] + rates[i] * 5

        # Cap at 1.0
        cumulative_risk = np.clip(cumulative_risk, 0, 1)

        # Create trajectory dataframe
        trajectory = pd.DataFrame(
            {
                "age": ages,
                "annual_risk": rates,
                "cumulative_risk": cumulative_risk,
                "survival_probability": (
                    survival_probs if competing_risks else np.ones_like(rates)
                ),
            }
        )

        return trajectory

    def _calculate_survival_probabilities(
        self, ages: np.ndarray, sex: str
    ) -> np.ndarray:
        """Calculate survival probabilities for competing risks adjustment."""
        survival_probs = np.ones_like(ages, dtype=float)

        for i, age in enumerate(ages):
            # Get life expectancy for this age
            life_exp = self.life_expectancy_data.get(sex, {}).get(int(age), 10)

            # Calculate annual mortality rate (simplified)
            annual_mortality = 1 - np.exp(-1 / life_exp) if life_exp > 0 else 0.01

            # Calculate survival probability for 5-year interval
            interval_survival = (1 - annual_mortality) ** 5
            survival_probs[i] = interval_survival

        return survival_probs

    def _calculate_confidence_intervals(
        self, risk_trajectory: pd.DataFrame, condition_data: pd.DataFrame
    ) -> Dict:
        """Calculate confidence intervals for risk projections."""
        # Simplified confidence interval calculation
        # In practice, this would use more sophisticated statistical methods

        base_risk = risk_trajectory["cumulative_risk"].iloc[-1]

        # Assume 20% uncertainty
        uncertainty_factor = 0.2

        lower_bound = max(0, base_risk * (1 - uncertainty_factor))
        upper_bound = min(1, base_risk * (1 + uncertainty_factor))

        # Age-specific confidence bands
        risk_values = risk_trajectory["cumulative_risk"].values
        lower_band = np.clip(risk_values * (1 - uncertainty_factor), 0, 1)
        upper_band = np.clip(risk_values * (1 + uncertainty_factor), 0, 1)

        return {
            "lifetime_risk_lower": lower_bound,
            "lifetime_risk_upper": upper_bound,
            "confidence_level": 0.8,  # 80% confidence
            "age_specific_lower": lower_band,
            "age_specific_upper": upper_band,
        }

    def _calculate_risk_scenarios(
        self,
        condition_data: pd.DataFrame,
        current_age: int,
        competing_risks: bool,
        prs_percentile: float,
        ancestry: str,
        lifestyle_modifier: float,
    ) -> Dict:
        """Calculate different risk scenarios (baseline, optimistic, pessimistic)."""

        scenarios = {}

        # Baseline scenario (current modifiers)
        baseline_trajectory = self._calculate_risk_trajectory(
            condition_data, current_age, competing_risks
        )
        scenarios["baseline"] = {
            "lifetime_risk": baseline_trajectory["cumulative_risk"].iloc[-1],
            "trajectory": baseline_trajectory,
        }

        # Optimistic scenario (lower risk)
        optimistic_data = condition_data.copy()
        optimistic_data["adjusted_rate"] = optimistic_data["adjusted_rate"] * 0.7
        optimistic_trajectory = self._calculate_risk_trajectory(
            optimistic_data, current_age, competing_risks
        )
        scenarios["optimistic"] = {
            "lifetime_risk": optimistic_trajectory["cumulative_risk"].iloc[-1],
            "trajectory": optimistic_trajectory,
        }

        # Pessimistic scenario (higher risk)
        pessimistic_data = condition_data.copy()
        pessimistic_data["adjusted_rate"] = pessimistic_data["adjusted_rate"] * 1.5
        pessimistic_trajectory = self._calculate_risk_trajectory(
            pessimistic_data, current_age, competing_risks
        )
        scenarios["pessimistic"] = {
            "lifetime_risk": pessimistic_trajectory["cumulative_risk"].iloc[-1],
            "trajectory": pessimistic_trajectory,
        }

        return scenarios

    def get_condition_list(self) -> List[str]:
        """Get list of available conditions."""
        if self.risk_data is None:
            return []
        return self.risk_data["condition"].unique().tolist()

    def get_risk_summary(self, results: Dict) -> Dict:
        """Generate human-readable risk summary."""
        if not results.get("success", False):
            return {
                "summary": "Unable to calculate lifetime risk",
                "details": results.get("error", "Unknown error"),
            }

        lifetime_risk = results["lifetime_risk"]
        condition = results["condition"]
        current_age = results["current_age"]

        # Risk level interpretation
        if lifetime_risk < 0.05:
            risk_level = "Very Low"
            interpretation = (
                f"Your lifetime risk of {condition.replace('_', ' ')} is below 5%."
            )
        elif lifetime_risk < 0.10:
            risk_level = "Low"
            interpretation = (
                f"Your lifetime risk of {condition.replace('_', ' ')} is between 5-10%."
            )
        elif lifetime_risk < 0.20:
            risk_level = "Moderate"
            interpretation = f"Your lifetime risk of {condition.replace('_', ' ')} is between 10-20%."
        elif lifetime_risk < 0.30:
            risk_level = "Elevated"
            interpretation = f"Your lifetime risk of {condition.replace('_', ' ')} is between 20-30%."
        else:
            risk_level = "High"
            interpretation = (
                f"Your lifetime risk of {condition.replace('_', ' ')} is above 30%."
            )

        confidence = results["confidence_intervals"]
        ci_lower = confidence["lifetime_risk_lower"]
        ci_upper = confidence["lifetime_risk_upper"]

        summary = {
            "condition": condition.replace("_", " ").title(),
            "current_age": current_age,
            "lifetime_risk": lifetime_risk,
            "risk_level": risk_level,
            "interpretation": interpretation,
            "confidence_interval": f"{ci_lower:.1%} - {ci_upper:.1%}",
            "scenarios": {
                "baseline": results["scenarios"]["baseline"]["lifetime_risk"],
                "optimistic": results["scenarios"]["optimistic"]["lifetime_risk"],
                "pessimistic": results["scenarios"]["pessimistic"]["lifetime_risk"],
            },
        }

        return summary


# Convenience functions
def calculate_lifetime_risk(
    condition: str,
    current_age: int,
    sex: str,
    prs_percentile: float = 50.0,
    ancestry: str = "European",
    lifestyle_modifier: float = 1.0,
) -> Dict:
    """Convenience function for lifetime risk calculation."""
    calculator = LifetimeRiskCalculator()
    return calculator.calculate_lifetime_risk(
        condition, current_age, sex, prs_percentile, ancestry, lifestyle_modifier
    )


def get_available_conditions() -> List[str]:
    """Get list of available conditions for lifetime risk calculation."""
    calculator = LifetimeRiskCalculator()
    return calculator.get_condition_list()
