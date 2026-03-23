# ai/predictor.py

import math
import random

def predict_resources(load):
    """
    Predict number of containers based on incoming load.
    Hybrid approach:
    - Rule-based logic (safe fallback)
    - Simulated ML behavior (for demo)
    """

    try:
        load = int(load)

        # -------------------------
        # 1. Basic Rule-Based Logic
        # -------------------------
        if load <= 0:
            return 1

        if load < 50:
            base_containers = 1
        elif load < 100:
            base_containers = 2
        elif load < 200:
            base_containers = 3
        else:
            base_containers = math.ceil(load / 75)

        # -------------------------
        # 2. Simulated ML Adjustment
        # -------------------------
        # Add slight variation to simulate prediction model
        variation = random.choice([0, 1])
        predicted = base_containers + variation

        # -------------------------
        # 3. Safety Limits
        # -------------------------
        predicted = max(1, predicted)     # minimum 1
        predicted = min(predicted, 10)    # cap at 10

        return predicted

    except Exception as e:
        print(f"Prediction Error: {e}")
        return 1  # fallback safety
