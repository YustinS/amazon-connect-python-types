"""
Unit tests for proficiency routing rule validation using Pydantic schemas.
"""

import pytest
from pydantic import ValidationError

from proficiency_routing.type import (
    ProficiencyRoutingPayload,
    CompoundExpr,
    AttributeConditionExpr,
    NotAttributeConditionExpr,
)


class TestSuccess:
    """
    Test valid parsing and validation of various proficiency routing rule payloads.
    """

    def test_and_expression_validation(self, and_expression_payload):
        """Test validation of AND expression with multiple conditions"""
        payload = ProficiencyRoutingPayload.model_validate(and_expression_payload)

        assert len(payload.Steps) == 2

        # Validate first step (AND expression)
        step1 = payload.Steps[0]
        assert isinstance(step1.Expression, CompoundExpr)
        assert step1.Expression.AndExpression is not None
        assert len(step1.Expression.AndExpression) == 2

        conditions = [x.AttributeCondition.Name for x in step1.Expression.AndExpression]
        assert "Language" in conditions
        assert "Technology" in conditions

        # Validate expiry
        assert step1.Expiry is not None
        assert step1.Expiry.DurationInSeconds == 30

        # Validate second step (simple condition)
        step2 = payload.Steps[1]
        assert isinstance(step2.Expression, AttributeConditionExpr)
        assert step2.Expression.AttributeCondition.Name == "Language"
        assert step2.Expression.AttributeCondition.ProficiencyLevel == 1

    def test_not_with_range_validation(self, not_with_range_payload):
        """Test validation of NOT condition with range specification"""
        payload = ProficiencyRoutingPayload.model_validate(not_with_range_payload)

        assert len(payload.Steps) == 1

        step = payload.Steps[0]
        assert isinstance(step.Expression, NotAttributeConditionExpr)

        not_condition = step.Expression.NotAttributeCondition
        assert not_condition.Name == "Language"
        assert not_condition.ComparisonOperator == "Range"

        range_spec = not_condition.Range
        assert range_spec is not None
        assert range_spec.MinProficiencyLevel == 4.0
        assert range_spec.MaxProficiencyLevel == 5.0

    def test_complex_validation(self, complex_payload):
        """Test validation of complex combination (OR/NOT/simple)"""
        payload = ProficiencyRoutingPayload.model_validate(complex_payload)

        assert len(payload.Steps) == 3

        # Validate step 1 (OR expression)
        step1 = payload.Steps[0]
        assert isinstance(step1.Expression, CompoundExpr)
        assert step1.Expression.OrExpression is not None
        technologies = [
            x.AttributeCondition.Value for x in step1.Expression.OrExpression
        ]
        assert "AWS Kinesis Firehose" in technologies
        assert "AWS Kinesis" in technologies

        # Validate step 2 (NOT with range)
        step2 = payload.Steps[1]
        assert isinstance(step2.Expression, NotAttributeConditionExpr)
        range_spec = step2.Expression.NotAttributeCondition.Range
        assert range_spec.MinProficiencyLevel == 4.0  # type: ignore
        assert range_spec.MaxProficiencyLevel == 5.0  # type: ignore

        # Validate step 3 (simple condition)
        step3 = payload.Steps[2]
        assert isinstance(step3.Expression, AttributeConditionExpr)
        condition = step3.Expression.AttributeCondition
        assert condition.Name == "Language"
        assert condition.Value == "English"
        assert condition.ProficiencyLevel == 1
        assert condition.ComparisonOperator == "NumberGreaterOrEqualTo"

    def test_allowed_and_disallowed_comparison_operators(self):
        """Ensure allowed ComparisonOperator literals validate and unknown operator fails."""
        # Allowed: Range
        payload_range = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ComparisonOperator": "Range",
                            "Range": {
                                "MinProficiencyLevel": 1.0,
                                "MaxProficiencyLevel": 2.0,
                            },
                        }
                    }
                }
            ]
        }
        ProficiencyRoutingPayload.model_validate(payload_range)

        # Allowed: NumberGreaterOrEqualTo
        payload_num = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                            "ProficiencyLevel": 1,
                        }
                    }
                }
            ]
        }
        ProficiencyRoutingPayload.model_validate(payload_num)

        # Disallowed operator
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ComparisonOperator": "INVALID_OP",
                            "ProficiencyLevel": 1,
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_expiry_optional_for_last_step(self):
        """Last step may omit Expiry while previous steps must include it."""
        payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 2,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    },
                    "Expiry": {"DurationInSeconds": 10},
                },
                {
                    # Last step intentionally without Expiry
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Technology",
                            "Value": "AWS Kinesis",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    },
                },
            ]
        }

        validated = ProficiencyRoutingPayload.model_validate(payload)
        assert len(validated.Steps) == 2
        assert validated.Steps[0].Expiry is not None
        assert validated.Steps[1].Expiry is None

    def test_single_step_expiry_optional(self):
        """Single-step payload may omit Expiry as that step is also the last step."""
        payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    }
                }
            ]
        }

        validated = ProficiencyRoutingPayload.model_validate(payload)
        assert len(validated.Steps) == 1
        assert validated.Steps[0].Expiry is None


class TestFailures:
    """
    Tests relating to failure cases in proficiency routing rule validation.
    """

    def test_invalid_compound_expression(self):
        """Test that having both AND and OR expressions raises validation error"""
        invalid_payload = {
            "Steps": [{"Expression": {"AndExpression": [], "OrExpression": []}}]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert (
            "Compound expression must have exactly one of AndExpression or OrExpression"
            in str(exc_info.value)
        )

    def test_invalid_range_values(self):
        """Test that invalid range values raise validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "NotAttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ComparisonOperator": "Range",
                            "Range": {
                                "MinProficiencyLevel": 5.0,  # Min > Max should fail
                                "MaxProficiencyLevel": 4.0,
                            },
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            # Missing required 'Name' field
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Name" in str(exc_info.value)  # Error should mention missing Name field

    def test_range_only_with_range_operator(self):
        """Range must only be present when ComparisonOperator == 'Range'"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                            "Range": {
                                "MinProficiencyLevel": 1.0,
                                "MaxProficiencyLevel": 2.0,
                            },
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_proficiencylevel_only_with_number_operator(self):
        """
        ProficiencyLevel must only be present when ComparisonOperator ==
        'NumberGreaterOrEqualTo'
        """
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "Range",
                            "Range": {
                                "MinProficiencyLevel": 1.0,
                                "MaxProficiencyLevel": 2.0,
                            },
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_expiry_required_for_non_last_step(self):
        """Expiry must be present for all steps except the last one."""
        invalid_payload = {
            "Steps": [
                {
                    # Missing Expiry on a non-last step should fail
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    },
                },
                {
                    # Last step with Expiry present (doesn't matter for the rule)
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Technology",
                            "Value": "AWS Kinesis",
                            "ProficiencyLevel": 2,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    },
                    "Expiry": {"DurationInSeconds": 30},
                },
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_empty_steps_array(self):
        """Test that an empty Steps array raises validation error"""
        invalid_payload = {"Steps": []}

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Steps" in str(exc_info.value)

    def test_missing_steps_field(self):
        """Test that missing Steps field raises validation error"""
        invalid_payload = {}

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Steps" in str(exc_info.value)

    def test_missing_expression_field(self):
        """Test that a step without Expression raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    # Missing Expression field
                    "Expiry": {"DurationInSeconds": 30}
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Expression" in str(exc_info.value)

    def test_invalid_expression_type(self):
        """Test that invalid Expression type raises validation error"""
        invalid_payload = {
            "Steps": [{"Expression": "not_an_object"}]  # Should be a dict
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Expression" in str(exc_info.value)

    def test_unknown_expression_discriminator(self):
        """Test that an expression with unknown discriminator raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "UnknownCondition": {
                            "Name": "Language",
                            "Value": "English",
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Invalid Expression" in str(exc_info.value) or "Unknown" in str(
            exc_info.value
        )

    def test_negative_expiry_duration(self):
        """Test that negative Expiry duration raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    },
                    "Expiry": {"DurationInSeconds": -10},  # Negative duration
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_invalid_expiry_type(self):
        """Test that invalid Expiry type raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    },
                    "Expiry": "not_an_object",  # Should be a dict
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_empty_and_expression(self):
        """Test that empty AndExpression array raises validation error"""
        invalid_payload = {
            "Steps": [{"Expression": {"AndExpression": []}}]  # Empty array should fail
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_empty_or_expression(self):
        """Test that empty OrExpression array raises validation error"""
        invalid_payload = {
            "Steps": [{"Expression": {"OrExpression": []}}]  # Empty array should fail
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_invalid_nested_expression_in_compound(self):
        """Test that invalid items in compound expressions raise validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AndExpression": [
                            {
                                "AttributeCondition": {
                                    "Name": "Language",
                                    "Value": "English",
                                    "ProficiencyLevel": 1,
                                    "ComparisonOperator": "NumberGreaterOrEqualTo",
                                }
                            },
                            "not_a_valid_expression",  # Invalid item
                        ]
                    }
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Expression" in str(exc_info.value) or "must be" in str(exc_info.value)

    def test_missing_value_field(self):
        """Test that missing Value field in AttributeCondition raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            # Missing 'Value' field
                            "ProficiencyLevel": 1,
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Value" in str(exc_info.value)

    def test_invalid_proficiency_level_type(self):
        """Test that invalid ProficiencyLevel type raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ProficiencyLevel": "not_a_number",  # Should be numeric
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError):
            ProficiencyRoutingPayload.model_validate(invalid_payload)

    def test_missing_range_when_operator_is_range(self):
        """Test that missing Range when operator is 'Range' raises validation error"""
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ComparisonOperator": "Range",
                            # Missing Range field
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "Range" in str(exc_info.value)

    def test_missing_proficiency_level_when_operator_is_number(self):
        """
        Test that missing ProficiencyLevel when operator is NumberGreaterOrEqualTo
        raises validation error
        """
        invalid_payload = {
            "Steps": [
                {
                    "Expression": {
                        "AttributeCondition": {
                            "Name": "Language",
                            "Value": "English",
                            "ComparisonOperator": "NumberGreaterOrEqualTo",
                            # Missing ProficiencyLevel field
                        }
                    }
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            ProficiencyRoutingPayload.model_validate(invalid_payload)

        assert "ProficiencyLevel" in str(exc_info.value)
