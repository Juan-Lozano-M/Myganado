"""Tests for the PredictionService 3-level risk classification."""
import sys
sys.path.insert(0, str(__import__('os').path.join(__file__, '..', '..', 'backend')))

import joblib
import pandas as pd
import unittest

from app.services.prediction_service import PredictionService
from app.models.schemas import PredictionRequest


class PredictionServiceTests(unittest.TestCase):
    def setUp(self):
        self.ps = PredictionService()

    def test_bajo_risk_with_high_confidence(self):
        """BAJO predicted with high probability should return BAJO risk level."""
        req = PredictionRequest(
            day=1, breed='Jersey', months_after_giving_birth=1,
            previous_mastitis_status=0, iu_fl=150, eu_fl=180, iu_fr=150, eu_fr=180,
            iu_rl=150, eu_rl=181, iu_rr=150, eu_rr=181,
            temperature=43, hardness=0, pain=0, milk_visibility=0
        )
        result = self.ps.predict(req)
        self.assertEqual(result.risk_level, "BAJO")
        self.assertEqual(result.model_label, "BAJO")

    def test_alto_risk_with_high_confidence(self):
        """ALTO predicted with high probability should return ALTO risk level."""
        req = PredictionRequest(
            day=10, breed='hostlene', months_after_giving_birth=2,
            previous_mastitis_status=0, iu_fl=300, eu_fl=350, iu_fr=151, eu_fr=181,
            iu_rl=152, eu_rl=183, iu_rr=152, eu_rr=181,
            temperature=44, hardness=1, pain=1, milk_visibility=1
        )
        result = self.ps.predict(req)
        self.assertEqual(result.risk_level, "ALTO")
        self.assertEqual(result.model_label, "ALTO")

    def test_medio_risk_with_low_confidence(self):
        """When model confidence is low, risk level should be MEDIO."""
        # Note: With the current DecisionTree model, probabilities are often 1.0.
        # This test verifies the classification logic works correctly.
        # To properly test MEDIO, we'd need a model with ~0.5 probability.
        # The logic is: if probability <= 0.5 and model says BAJO → MEDIO
        #              if probability <= 0.5 and model says ALTO → MEDIO
        # For now, we verify the method exists and returns a valid risk level.
        from app.services.prediction_service import PredictionService as PS
        # Test the classification method directly with low probability
        result = self.ps._classify_risk_level("BAJO", 0.3)
        self.assertEqual(result, "MEDIO")

        result2 = self.ps._classify_risk_level("ALTO", 0.3)
        self.assertEqual(result2, "MEDIO")

        result3 = self.ps._classify_risk_level("BAJO", 0.8)
        self.assertEqual(result3, "BAJO")

        result4 = self.ps._classify_risk_level("ALTO", 0.8)
        self.assertEqual(result4, "ALTO")

        self.assertEqual(self.ps._classify_risk_level("BAJO", 0.6), "MEDIO")


if __name__ == "__main__":
    unittest.main()
