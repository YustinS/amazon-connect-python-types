"""
Comprehensive test suite for the Pydantic Amazon Connect Contact Flow Event models.
Demonstrates validation capabilities and usage patterns.
"""

import pytest
from pydantic import ValidationError

from contact_flow_event.type import (
    ConnectContactFlowEvent,
    ConnectContactFlowChannel,
    ConnectContactFlowInitiationMethod,
)


class TestSuccess:
    """Test valid parsing and validation of Amazon Connect Contact Flow Event models."""

    def test_complete_valid_event(self, amazon_connect_contact_flow_event):
        """Test that a complete, valid event can be created and validated."""
        # Should create successfully
        event = ConnectContactFlowEvent(**amazon_connect_contact_flow_event)  # type: ignore

        # Test property access
        assert event.contact_data.contact_id == "12345678-1234-1234-1234-123456789012"
        assert event.contact_data.channel == ConnectContactFlowChannel.VOICE
        assert (
            event.contact_data.initiation_method
            == ConnectContactFlowInitiationMethod.INBOUND
        )
        assert event.contact_data.customer_endpoint.address == "+1234567890"  # type: ignore
        assert event.contact_data.queue.name == "BasicQueue"  # type: ignore
        assert event.parameters == {"param1": "value1", "param2": "value2"}

    def test_minimal_valid_event(self):
        """Test creating event with minimal required fields."""
        minimal_data = {
            "Details": {
                "ContactData": {
                    "Attributes": {},
                    "Channel": "CHAT",
                    "ContactId": "minimal-contact-id",
                    "InitialContactId": "minimal-initial-contact-id",
                    "InitiationMethod": "API",
                    "InstanceARN": "arn:aws:connect:us-east-1:123456789012:instance/minimal",
                    "PreviousContactId": "minimal-previous-contact-id",
                    "MediaStreams": {"Customer": {"Audio": {}}},
                },
                "Parameters": {},
            }
        }

        event = ConnectContactFlowEvent(**minimal_data)  # type: ignore
        assert event.contact_data.channel == ConnectContactFlowChannel.CHAT
        assert (
            event.contact_data.initiation_method
            == ConnectContactFlowInitiationMethod.API
        )
        assert event.contact_data.customer_endpoint is None
        assert event.contact_data.queue is None

    def test_json_serialization(self):
        """Test that models can be serialized to JSON."""
        event_data = {
            "Details": {
                "ContactData": {
                    "Attributes": {"test": "value"},
                    "Channel": "VOICE",
                    "ContactId": "test-contact-id",
                    "InitialContactId": "test-initial-contact-id",
                    "InitiationMethod": "INBOUND",
                    "InstanceARN": "arn:aws:connect:us-east-1:123456789012:instance/test",
                    "PreviousContactId": "test-previous-contact-id",
                    "MediaStreams": {"Customer": {"Audio": {}}},
                },
                "Parameters": {"key": "value"},
            }
        }

        event = ConnectContactFlowEvent(**event_data)  # type: ignore

        # Should be able to serialize to dict and JSON
        event_dict = event.model_dump(
            mode="json"
        )  # Use JSON mode for proper enum serialization
        assert event_dict["Details"]["ContactData"]["Channel"] == "VOICE"

        json_str = event.model_dump_json()
        assert '"Channel":"VOICE"' in json_str

    def test_model_copy_and_update(self):
        """Test that models support copying and updating."""
        event_data = {
            "Details": {
                "ContactData": {
                    "Attributes": {},
                    "Channel": "VOICE",
                    "ContactId": "original-contact-id",
                    "InitialContactId": "original-initial-contact-id",
                    "InitiationMethod": "INBOUND",
                    "InstanceARN": "arn:aws:connect:us-east-1:123456789012:instance/test",
                    "PreviousContactId": "original-previous-contact-id",
                    "MediaStreams": {"Customer": {"Audio": {}}},
                },
                "Parameters": {},
            }
        }

        original_event = ConnectContactFlowEvent(**event_data)  # type: ignore

        # Create a copy with updated contact ID
        updated_event = original_event.model_copy(
            update={
                "Details": original_event.Details.model_copy(
                    update={
                        "ContactData": original_event.Details.ContactData.model_copy(
                            update={"ContactId": "updated-contact-id"}
                        )
                    }
                )
            }
        )

        assert original_event.contact_data.contact_id == "original-contact-id"
        assert updated_event.contact_data.contact_id == "updated-contact-id"


class TestFailures:
    """Test validation error cases for Amazon Connect Contact Flow Event models."""

    def test_invalid_channel_validation(self):
        """Test that invalid channel values are rejected."""
        invalid_data = {
            "Details": {
                "ContactData": {
                    "Attributes": {},
                    "Channel": "INVALID_CHANNEL",  # Invalid value
                    "ContactId": "test-contact-id",
                    "InitialContactId": "test-initial-contact-id",
                    "InitiationMethod": "INBOUND",
                    "InstanceARN": "arn:aws:connect:us-east-1:123456789012:instance/test",
                    "PreviousContactId": "test-previous-contact-id",
                    "MediaStreams": {"Customer": {"Audio": {}}},
                },
                "Parameters": {},
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            ConnectContactFlowEvent(**invalid_data)  # type: ignore

        # Check that the error mentions the invalid enum value
        assert "Input should be" in str(exc_info.value)

    def test_invalid_initiation_method_validation(self):
        """Test that invalid initiation method values are rejected."""
        invalid_data = {
            "Details": {
                "ContactData": {
                    "Attributes": {},
                    "Channel": "VOICE",
                    "ContactId": "test-contact-id",
                    "InitialContactId": "test-initial-contact-id",
                    "InitiationMethod": "INVALID_METHOD",  # Invalid value
                    "InstanceARN": "arn:aws:connect:us-east-1:123456789012:instance/test",
                    "PreviousContactId": "test-previous-contact-id",
                    "MediaStreams": {"Customer": {"Audio": {}}},
                },
                "Parameters": {},
            }
        }

        with pytest.raises(ValidationError):
            ConnectContactFlowEvent(**invalid_data)  # type: ignore

    def test_missing_required_fields(self):
        """Test that missing required fields are caught."""
        incomplete_data = {
            "Details": {
                "ContactData": {
                    "Attributes": {},
                    "Channel": "VOICE",
                    # Missing ContactId - required field
                    "InitiationMethod": "INBOUND",
                    "InstanceARN": "arn:aws:connect:us-east-1:123456789012:instance/test",
                    "MediaStreams": {"Customer": {"Audio": {}}},
                },
                "Parameters": {},
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            ConnectContactFlowEvent(**incomplete_data)  # type: ignore

        # Should mention the missing field
        assert "Field required" in str(exc_info.value)
