"""
Shared configs used in testing
"""

import os
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    """
    Create runtest report
    """
    outcome = yield
    report = outcome.get_result()

    test_fn = item.obj

    # VS Code managed tests doesn't like the test docstring output, preventing it from showing the
    # test status markers. Set the environment variable VSCODE_TESTING_ENABLED which will stop the
    # docstring output, making the VS Code managed tests work.
    vscode_testing = os.getenv("VSCODE_TESTING_ENABLED")

    docstring = getattr(test_fn, "__doc__")
    if docstring and not bool(vscode_testing):
        report.nodeid = docstring


#########
# Step Validator Fixtures
#########
@pytest.fixture
def and_expression_payload():
    """Test fixture for AND expression with multiple conditions"""
    return {
        "Steps": [
            {
                "Expression": {
                    "AndExpression": [
                        {
                            "AttributeCondition": {
                                "Name": "Language",
                                "Value": "English",
                                "ProficiencyLevel": 4,
                                "ComparisonOperator": "NumberGreaterOrEqualTo",
                            }
                        },
                        {
                            "AttributeCondition": {
                                "Name": "Technology",
                                "Value": "AWS Kinesis",
                                "ProficiencyLevel": 2,
                                "ComparisonOperator": "NumberGreaterOrEqualTo",
                            }
                        },
                    ]
                },
                "Expiry": {"DurationInSeconds": 30},
            },
            {
                "Expression": {
                    "AttributeCondition": {
                        "Name": "Language",
                        "Value": "English",
                        "ProficiencyLevel": 1,
                        "ComparisonOperator": "NumberGreaterOrEqualTo",
                    }
                }
            },
        ]
    }


@pytest.fixture
def not_with_range_payload():
    """Test fixture for NOT condition with range specification"""
    return {
        "Steps": [
            {
                "Expression": {
                    "NotAttributeCondition": {
                        "Name": "Language",
                        "Value": "English",
                        "ComparisonOperator": "Range",
                        "Range": {
                            "MinProficiencyLevel": 4.0,
                            "MaxProficiencyLevel": 5.0,
                        },
                    }
                },
                "Expiry": {"DurationInSeconds": 30},
            }
        ]
    }


@pytest.fixture
def complex_payload():
    """Test fixture for complex combination of OR, NOT, and simple conditions"""
    return {
        "Steps": [
            {
                "Expression": {
                    "OrExpression": [
                        {
                            "AttributeCondition": {
                                "Name": "Technology",
                                "Value": "AWS Kinesis Firehose",
                                "ProficiencyLevel": 2,
                                "ComparisonOperator": "NumberGreaterOrEqualTo",
                            }
                        },
                        {
                            "AttributeCondition": {
                                "Name": "Technology",
                                "Value": "AWS Kinesis",
                                "ProficiencyLevel": 2,
                                "ComparisonOperator": "NumberGreaterOrEqualTo",
                            }
                        },
                    ]
                },
                "Expiry": {"DurationInSeconds": 30},
            },
            {
                "Expression": {
                    "NotAttributeCondition": {
                        "Name": "Language",
                        "Value": "English",
                        "ComparisonOperator": "Range",
                        "Range": {
                            "MinProficiencyLevel": 4.0,
                            "MaxProficiencyLevel": 5.0,
                        },
                    }
                },
                "Expiry": {"DurationInSeconds": 30},
            },
            {
                "Expression": {
                    "AttributeCondition": {
                        "Name": "Language",
                        "Value": "English",
                        "ProficiencyLevel": 1,
                        "ComparisonOperator": "NumberGreaterOrEqualTo",
                    }
                }
            },
        ]
    }
