# Shared fixtures for the test suite

import os
import sys

import pytest

# Make sure imports like "from src.x" work when pytest runs from anywhere
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def sample_answers():
    # A complete, valid set of answers
    return {
        "Gender": ["Male"],
        "Age": [24.0],
        "Work/Study Hours": [8.0],
        "Academic Pressure": [4.0],
        "Financial Stress": [3.0],
        "Study Satisfaction": [2.0],
        "Sleep Duration": ["5-6 hours"],
        "Dietary Habits": ["Moderate Diet"],
        "Have you ever had suicidal thoughts ?": ["Yes"],
        "Family History of Mental Illness": ["No"],
    }


@pytest.fixture
def low_risk_answers():
    # A profile that should give a low risk score
    return {
        "Gender": ["Female"],
        "Age": [22.0],
        "Work/Study Hours": [4.0],
        "Academic Pressure": [1.0],
        "Financial Stress": [1.0],
        "Study Satisfaction": [5.0],
        "Sleep Duration": ["7-8 hours"],
        "Dietary Habits": ["Healthy Diet"],
        "Have you ever had suicidal thoughts ?": ["No"],
        "Family History of Mental Illness": ["No"],
    }


@pytest.fixture
def high_risk_answers():
    # A profile that should give a high risk score
    return {
        "Gender": ["Male"],
        "Age": [24.0],
        "Work/Study Hours": [12.0],
        "Academic Pressure": [5.0],
        "Financial Stress": [5.0],
        "Study Satisfaction": [1.0],
        "Sleep Duration": ["Less than 5 hours"],
        "Dietary Habits": ["Unhealthy Diet"],
        "Have you ever had suicidal thoughts ?": ["Yes"],
        "Family History of Mental Illness": ["Yes"],
    }
