"""
Unit tests for AI agent modules
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAgentInitialization(unittest.TestCase):
    """Test agent initialization without requiring API keys"""

    @patch('agents.validator.ExtractionValidatorAgent._create_agent')
    def test_validator_agent_init(self, mock_create):
        """Test validator agent can be initialized"""
        from agents.validator import ExtractionValidatorAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()

        agent = ExtractionValidatorAgent(mock_llm)

        self.assertIsNotNone(agent)
        self.assertEqual(agent.llm, mock_llm)

    @patch('agents.medical.MedicalInsightAgent._create_agent')
    def test_medical_agent_init(self, mock_create):
        """Test medical agent can be initialized"""
        from agents.medical import MedicalInsightAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()

        agent = MedicalInsightAgent(mock_llm)

        self.assertIsNotNone(agent)
        self.assertEqual(agent.llm, mock_llm)

    @patch('agents.compliance.ComplianceAgent._create_agent')
    def test_compliance_agent_init(self, mock_create):
        """Test compliance agent can be initialized"""
        from agents.compliance import ComplianceAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()

        agent = ComplianceAgent(mock_llm)

        self.assertIsNotNone(agent)
        self.assertEqual(agent.llm, mock_llm)

    @patch('agents.executive.ExecutiveSummaryAgent._create_agent')
    def test_executive_agent_init(self, mock_create):
        """Test executive agent can be initialized"""
        from agents.executive import ExecutiveSummaryAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()

        agent = ExecutiveSummaryAgent(mock_llm)

        self.assertIsNotNone(agent)
        self.assertEqual(agent.llm, mock_llm)


class TestValidatorAgent(unittest.TestCase):
    """Test validation agent functionality"""

    @patch('agents.validator.ExtractionValidatorAgent._create_agent')
    def setUp(self, mock_create):
        """Set up test fixtures"""
        from agents.validator import ExtractionValidatorAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()
        self.agent = ExtractionValidatorAgent(mock_llm)

    def test_validate_record_structure(self):
        """Test that validate_record returns expected structure"""
        # Mock the LLM response
        mock_response = Mock()
        mock_response.content = """
        QUALITY_SCORE: 95
        STATUS: PASS
        ISSUES: None
        CONFIDENCE: High
        COMMENTS: Drug information looks accurate
        """
        self.agent.llm.invoke = Mock(return_value=mock_response)

        drug_record = {
            "drug_name": "Test Drug",
            "approval_status": "Approved",
            "disease_category": "Antidiabetic"
        }

        result = self.agent.validate_record(drug_record)

        # Check result structure
        self.assertIn("drug_name", result)
        self.assertIn("quality_score", result)
        self.assertIn("validation_status", result)
        self.assertIn("confidence", result)

    def test_validate_record_fallback(self):
        """Test fallback behavior when AI fails"""
        # Mock AI failure
        self.agent.llm.invoke = Mock(side_effect=Exception("API Error"))

        drug_record = {
            "drug_name": "Test Drug",
            "approval_status": "Approved"
        }

        result = self.agent.validate_record(drug_record)

        # Should return fallback result
        self.assertEqual(result["quality_score"], 70)
        self.assertEqual(result["validation_status"], "NEEDS_REVIEW")


class TestMedicalAgent(unittest.TestCase):
    """Test medical insight agent functionality"""

    @patch('agents.medical.MedicalInsightAgent._create_agent')
    def setUp(self, mock_create):
        """Set up test fixtures"""
        from agents.medical import MedicalInsightAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()
        self.agent = MedicalInsightAgent(mock_llm)

    def test_analyze_drug_structure(self):
        """Test that analyze_drug returns expected structure"""
        mock_response = Mock()
        mock_response.content = """
        THERAPEUTIC_CATEGORY: Antidiabetic
        MECHANISM: GLP-1 receptor agonist
        COMPETITORS: Metformin; Insulin; Trulicity
        MARKET_IMPACT: High
        MARKET_SIZE: $60B annually
        TARGET_POPULATION: Type 2 diabetes patients
        CLINICAL_SIGNIFICANCE: Novel mechanism of action
        RECOMMENDATIONS: Monitor competitive response; Track real-world effectiveness
        """
        self.agent.llm.invoke = Mock(return_value=mock_response)

        drug_record = {
            "drug_name": "Test Drug",
            "disease_category": "Antidiabetic"
        }

        result = self.agent.analyze_drug(drug_record)

        # Check result structure
        self.assertIn("drug_name", result)
        self.assertIn("therapeutic_category", result)
        self.assertIn("mechanism_of_action", result)
        self.assertIn("competitors", result)
        self.assertIn("market_impact", result)

    def test_analyze_batch(self):
        """Test batch analysis functionality"""
        mock_response = Mock()
        mock_response.content = "THERAPEUTIC_CATEGORY: Test"
        self.agent.llm.invoke = Mock(return_value=mock_response)

        records = [
            {"drug_name": "Drug1", "disease_category": "Oncology"},
            {"drug_name": "Drug2", "disease_category": "Cardiovascular"}
        ]

        results = self.agent.analyze_batch(records)

        self.assertEqual(len(results), 2)
        self.assertIsInstance(results, list)


class TestComplianceAgent(unittest.TestCase):
    """Test compliance agent functionality"""

    @patch('agents.compliance.ComplianceAgent._create_agent')
    def setUp(self, mock_create):
        """Set up test fixtures"""
        from agents.compliance import ComplianceAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()
        self.agent = ComplianceAgent(mock_llm)

    def test_assess_compliance_structure(self):
        """Test that assess_compliance returns expected structure"""
        mock_response = Mock()
        mock_response.content = """
        REGULATORY_BODY: FDA (United States)
        RISK_LEVEL: Medium
        COMPLIANCE_REQUIREMENTS: Annual reporting; Adverse event tracking
        SAFETY_CONCERNS: Standard monitoring required
        POST_MARKET: Phase 4 studies
        RECOMMENDATIONS: Ensure FDA compliance; Implement pharmacovigilance
        """
        self.agent.llm.invoke = Mock(return_value=mock_response)

        drug_record = {
            "drug_name": "Test Drug",
            "region": "United States",
            "approval_status": "Approved"
        }

        result = self.agent.assess_compliance(drug_record)

        # Check result structure
        self.assertIn("drug_name", result)
        self.assertIn("regulatory_body", result)
        self.assertIn("risk_level", result)
        self.assertIn("compliance_requirements", result)
        self.assertIn("safety_concerns", result)


class TestExecutiveSummaryAgent(unittest.TestCase):
    """Test executive summary agent functionality"""

    @patch('agents.executive.ExecutiveSummaryAgent._create_agent')
    def setUp(self, mock_create):
        """Set up test fixtures"""
        from agents.executive import ExecutiveSummaryAgent

        mock_llm = Mock()
        mock_create.return_value = Mock()
        self.agent = ExecutiveSummaryAgent(mock_llm)

    def test_generate_summary_structure(self):
        """Test that generate_summary returns expected structure"""
        drug_record = {"drug_name": "Test Drug", "approval_status": "Approved"}
        validation = {"quality_score": 95, "validation_status": "PASS"}
        medical = {"market_impact": "High", "competitors": ["Drug1", "Drug2"]}
        compliance = {"risk_level": "Medium", "regulatory_body": "FDA"}

        result = self.agent.generate_summary(drug_record, validation, medical, compliance)

        # Check result structure
        self.assertIn("headline", result)
        self.assertIn("key_facts", result)
        self.assertIn("strategic_implications", result)
        self.assertIn("competitive_impact", result)
        self.assertIn("risk_factors", result)
        self.assertIn("recommended_actions", result)

    def test_generate_summary_handles_none_inputs(self):
        """Test that generate_summary handles None inputs gracefully"""
        drug_record = {"drug_name": "Test Drug"}

        result = self.agent.generate_summary(drug_record, None, None, None)

        # Should still return valid structure
        self.assertIsNotNone(result)
        self.assertIn("headline", result)


if __name__ == "__main__":
    unittest.main()
