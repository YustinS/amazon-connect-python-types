"""
Schema definitions for proficiency routing expressions and steps.
"""

from typing import Any, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class RangeSpec(BaseModel):
    """
    Range specification model.
    """

    MinProficiencyLevel: float = Field(
        ..., description="Minimum proficiency level for the range"
    )
    MaxProficiencyLevel: float = Field(
        ..., description="Maximum proficiency level for the range"
    )

    @property
    def min_proficiency_level(self) -> float:
        """Minimum proficiency level for the range."""
        return self.MinProficiencyLevel

    @property
    def max_proficiency_level(self) -> float:
        """Maximum proficiency level for the range."""
        return self.MaxProficiencyLevel

    @model_validator(mode="after")
    def check_min_le_max(self):
        """Ensure MinProficiencyLevel is not greater than MaxProficiencyLevel."""
        if self.MinProficiencyLevel > self.MaxProficiencyLevel:
            raise ValueError("MinProficiencyLevel must be <= MaxProficiencyLevel")
        return self


class AttributeCondition(BaseModel):
    """
    Attribute condition model for proficiency routing.
    """

    Name: str = Field(..., description="Name of the attribute to evaluate")
    Value: str = Field(..., description="Value to compare against the attribute")
    ProficiencyLevel: Optional[float] = Field(
        None, description="Proficiency level for numeric comparisons"
    )
    ComparisonOperator: Literal["Range", "NumberGreaterOrEqualTo"] = Field(
        ..., description="Type of comparison to perform"
    )
    Range: Optional[RangeSpec] = Field(
        None, description="Range specification for range-based comparisons"
    )

    @property
    def name(self) -> str:
        """Name of the attribute to evaluate."""
        return self.Name

    @property
    def value(self) -> str:
        """Value to compare against the attribute."""
        return self.Value

    @property
    def proficiency_level(self) -> Optional[float]:
        """Proficiency level for numeric comparisons."""
        return self.ProficiencyLevel

    @property
    def comparison_operator(self) -> Literal["Range", "NumberGreaterOrEqualTo"]:
        """Type of comparison to perform."""
        return self.ComparisonOperator

    @property
    def range(self) -> Optional[RangeSpec]:
        """Range specification for range-based comparisons."""
        return self.Range

    @model_validator(mode="after")
    def check_operator_field_consistency(self):
        """
        Enforce that Range is only present for 'Range' operator and
        ProficiencyLevel only present for numeric comparison operators.
        """
        # When operator is Range, Range must be provided and ProficiencyLevel must not be set
        if self.ComparisonOperator == "Range":
            if self.Range is None:
                raise ValueError(
                    "Range must be provided when ComparisonOperator is 'Range'"
                )
            if self.ProficiencyLevel is not None:
                raise ValueError(
                    "ProficiencyLevel must not be set when ComparisonOperator is 'Range'"
                )

        # When operator is a numeric comparison, ProficiencyLevel must be provided
        # and Range must not be set
        if self.ComparisonOperator == "NumberGreaterOrEqualTo":
            if self.ProficiencyLevel is None:
                raise ValueError(
                    "ProficiencyLevel must be provided when ComparisonOperator"
                    " is 'NumberGreaterOrEqualTo'"
                )
            if self.Range is not None:
                raise ValueError(
                    "Range must not be set when ComparisonOperator is 'NumberGreaterOrEqualTo'"
                )

        return self


class AttributeConditionExpr(BaseModel):
    """
    Attribute condition expression model.
    """

    AttributeCondition: AttributeCondition

    @property
    def attribute_condition(self) -> "AttributeCondition":
        """Attribute condition to evaluate."""
        return self.AttributeCondition


class NotAttributeConditionExpr(BaseModel):
    """
    Not condition expression model.
    """

    NotAttributeCondition: AttributeCondition

    @property
    def not_attribute_condition(self) -> AttributeCondition:
        """Attribute condition to negate."""
        return self.NotAttributeCondition


class CompoundExpr(BaseModel):
    """
    Model for compound expressions (And/Or).
    """

    AndExpression: Optional[List[Any]] = Field(
        None, description="List of expressions to evaluate with AND logic"
    )
    OrExpression: Optional[List[Any]] = Field(
        None, description="List of expressions to evaluate with OR logic"
    )

    @property
    def and_expression(self) -> Optional[List[Any]]:
        """List of expressions to evaluate with AND logic."""
        return self.AndExpression

    @property
    def or_expression(self) -> Optional[List[Any]]:
        """List of expressions to evaluate with OR logic."""
        return self.OrExpression

    @model_validator(mode="before")
    @classmethod
    def ensure_single_key(cls, values):
        """
        Ensure that only one of AndExpression or OrExpression is present.
        """
        if not isinstance(values, dict):
            return values
        keys = [
            k
            for k in ("AndExpression", "OrExpression")
            if k in values and values[k] is not None
        ]
        if len(keys) != 1:
            raise ValueError(
                "Compound expression must have exactly one of AndExpression or OrExpression"
            )
        return values

    @field_validator("AndExpression", mode="before")
    @classmethod
    def parse_and(cls, v):
        """
        Parse AndExpression list items.
        """
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("AndExpression must be a list")
        if len(v) == 0:
            raise ValueError("AndExpression must not be empty")
        return [parse_expression_item(item) for item in v]

    @field_validator("OrExpression", mode="before")
    @classmethod
    def parse_or(cls, v):
        """
        Parse OrExpression list items.
        """
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("OrExpression must be a list")
        if len(v) == 0:
            raise ValueError("OrExpression must not be empty")
        return [parse_expression_item(item) for item in v]


class ExpiryRule(BaseModel):
    """
    Model for expiry rules.
    """

    DurationInSeconds: int = Field(
        ..., description="Duration in seconds after which the step expires", gt=0
    )

    @property
    def duration_in_seconds(self) -> int:
        """Duration in seconds after which the step expires."""
        return self.DurationInSeconds

    @field_validator("DurationInSeconds")
    @classmethod
    def check_positive_duration(cls, v):
        """Ensure DurationInSeconds is positive."""
        if v <= 0:
            raise ValueError("DurationInSeconds must be positive")
        return v


def parse_expression_item(item: Any):
    """Helper to parse a single expression item (a dict with a single discriminator key)."""
    if not isinstance(item, dict):
        raise ValueError("Expression items must be objects")
    if "AttributeCondition" in item:
        return AttributeConditionExpr(**item)
    if "NotAttributeCondition" in item:
        return NotAttributeConditionExpr(**item)
    if "AndExpression" in item or "OrExpression" in item:
        return CompoundExpr(**item)
    raise ValueError(f"Unknown expression type in item: {item}")


class Step(BaseModel):
    """
    Schema for a single proficiency routing step.
    """

    Expression: Any = Field(..., description="Expression to evaluate for this step")
    Expiry: Optional[ExpiryRule] = Field(
        None, description="Optional expiry rule for this step"
    )

    @property
    def expression(self) -> Any:
        """Expression to evaluate for this step."""
        return self.Expression

    @property
    def expiry(self) -> Optional[ExpiryRule]:
        """Optional expiry rule for this step."""
        return self.Expiry

    @field_validator("Expression", mode="before")
    @classmethod
    def parse_expression(cls, v):
        """
        Parse the Expression field into the appropriate model.
        """
        if not isinstance(v, dict):
            raise ValueError("Expression must be an object")
        # delegate to the helper/child models
        if "AttributeCondition" in v:
            return AttributeConditionExpr(**v)
        if "NotAttributeCondition" in v:
            return NotAttributeConditionExpr(**v)
        if "AndExpression" in v or "OrExpression" in v:
            return CompoundExpr(**v)
        raise ValueError(f"Invalid Expression value: {v}")


class ProficiencyRoutingPayload(BaseModel):
    """
    Schema for proficiency routing payload.
    """

    Steps: List[Step] = Field(
        ..., description="List of proficiency routing steps to evaluate", min_length=1
    )

    @property
    def steps(self) -> List[Step]:
        """List of proficiency routing steps to evaluate."""
        return self.Steps

    @field_validator("Steps")
    @classmethod
    def check_steps_not_empty(cls, v):
        """Ensure Steps array is not empty."""
        if not v or len(v) == 0:
            raise ValueError("Steps must contain at least one step")
        return v

    @model_validator(mode="after")
    def validate_expiry_rules(self):
        """
        Ensure Expiry is present for all steps except the last one in the list.
        The last step may omit Expiry.
        """
        steps = self.Steps or []
        if len(steps) <= 1:
            # Single or no steps: last (or only) step may omit Expiry (signifying
            # that the step stays active indefinitely)
            return self
        for _, step in enumerate(steps[:-1]):
            if step.Expiry is None:
                raise ValueError("Expiry is required for all steps except the last one")
        return self
