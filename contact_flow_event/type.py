"""
Pydantic models and enums for Amazon Connect contact flow event structure.
Based on the AWS Lambda Powertools structure

https://github.com/aws-powertools/powertools-lambda-python/blob/develop/aws_lambda_powertools/utilities/data_classes/connect_contact_flow_event.py
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ConnectContactFlowChannel(Enum):
    """
    The channel for the invoking contact
    """

    VOICE = "VOICE"
    CHAT = "CHAT"
    TASK = "TASK"
    EMAIL = "EMAIL"


class ConnectContactFlowEndpointType(Enum):
    """
    The endpoint type of the contact
    """

    TELEPHONE_NUMBER = "TELEPHONE_NUMBER"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"


class ConnectContactFlowInitiationMethod(Enum):
    """
    The initiation method of the contact
    """

    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    TRANSFER = "TRANSFER"
    CALLBACK = "CALLBACK"
    API = "API"
    DISCONNECT = "DISCONNECT"
    FLOW = "FLOW"


class ConnectContactReferenceType(Enum):
    """
    The reference type of the contact
    """

    URL = "URL"
    ATTACHMENT = "ATTACHMENT"
    STRING = "STRING"
    CONTACT_ANALYSIS = "CONTACT_ANALYSIS"
    NUMBER = "NUMBER"
    DATE = "DATE"
    EMAIL = "EMAIL"
    EMAIL_MESSAGE = "EMAIL_MESSAGE"


class ConnectContactReferenceStatus(Enum):
    """
    The reference status of the contact
    """

    AVAILABLE = "AVAILABLE"
    DELETED = "DELETED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"


class ConnectContactFlowEndpoint(BaseModel):
    """
    Contact endpoint information
    """

    Address: str = Field(..., description="The phone number")
    Type: ConnectContactFlowEndpointType = Field(..., description="The endpoint type")
    DisplayName: Optional[str] = Field(
        None,
        description="The display name for the endpoint. Primarily relevant for Email",
    )

    @property
    def address(self) -> str:
        """The address as contacted in Connect."""
        return self.Address

    @property
    def endpoint_type(self) -> ConnectContactFlowEndpointType:
        """The endpoint type."""
        return self.Type

    @property
    def display_name(self) -> str | None:
        """The display name for the endpoint."""
        return self.DisplayName


class ConnectContactFlowQueue(BaseModel):
    """
    Contact queue information (may be null depending on invocation context)
    """

    ARN: str = Field(..., description="The unique queue ARN")
    Name: str = Field(..., description="The queue name")

    @property
    def arn(self) -> str:
        """The unique queue ARN."""
        return self.ARN

    @property
    def name(self) -> str:
        """The queue name."""
        return self.Name


class ConnectContactFlowMediaStreamAudio(BaseModel):
    """
    Contact media stream audio information
    """

    StartFragmentNumber: Optional[str] = Field(
        None,
        description="The number that identifies the Kinesis Video Streams fragment",
    )
    StartTimestamp: Optional[str] = Field(
        None, description="When the customer audio stream started"
    )
    StreamARN: Optional[str] = Field(
        None, description="The ARN of the Kinesis Video stream"
    )

    @property
    def start_fragment_number(self) -> str | None:
        """
        The number that identifies the Kinesis Video Streams fragment, in the stream used for
        Live media streaming, in which the customer audio stream started.
        """
        return self.StartFragmentNumber

    @property
    def start_timestamp(self) -> str | None:
        """When the customer audio stream started."""
        return self.StartTimestamp

    @property
    def stream_arn(self) -> str | None:
        """
        The ARN of the Kinesis Video stream used for Live media streaming that includes the
        customer data to reference.
        """
        return self.StreamARN


class ConnectContactFlowMediaStreamCustomer(BaseModel):
    """
    Media stream information for the customer
    """

    Audio: ConnectContactFlowMediaStreamAudio = Field(
        ..., description="Audio stream information"
    )

    @property
    def audio(self) -> ConnectContactFlowMediaStreamAudio:
        """
        The audio stream information for the customer
        """
        return self.Audio


class ConnectContactFlowMediaStreams(BaseModel):
    """
    Media Streams informtion
    """

    Customer: ConnectContactFlowMediaStreamCustomer = Field(
        ..., description="Customer media stream information"
    )

    @property
    def customer(self) -> ConnectContactFlowMediaStreamCustomer:
        """
        Customer details
        """
        return self.Customer


class ConnectContactReferenceFields(BaseModel):
    """
    Contact reference fields
    """

    Arn: Optional[str] = Field(None, description="ARN reference")
    Status: Optional[ConnectContactReferenceStatus] = Field(
        None, description="Status reference"
    )
    StatusReason: Optional[str] = Field(None, description="Status reason reference")
    Type: Optional[ConnectContactReferenceType] = Field(
        None, description="Type reference"
    )
    Value: Optional[str] = Field(None, description="Value reference")

    @property
    def arn(self) -> str | None:
        """The ARN reference."""
        return self.Arn

    @property
    def status(self) -> ConnectContactReferenceStatus | None:
        """The status reference."""
        return self.Status
    
    @property
    def status_reason(self) -> str | None:
        """The status reason reference."""
        return self.StatusReason

    @property
    def type(self) -> ConnectContactReferenceType | None:
        """The type reference."""
        return self.Type

    @property
    def value(self) -> str | None:
        """The value reference."""
        return self.Value


class ConnectContactSegmentAttributes(BaseModel):
    """
    Contact segment attributes
    """

    ValueArn: Optional[str] = Field(
        None, description="Value ARN of the contact Attributes"
    )
    ValueInteger: Optional[float] = Field(
        None, description="Value integer of the contact Attributes"
    )
    ValueList: Optional[list[str]] = Field(
        None, description="Value list of the contact Attributes"
    )
    ValueMap: Optional[dict[str, str]] = Field(
        None, description="Value map of the contact Attributes"
    )
    ValueString: Optional[str] = Field(
        None, description="Value string of the contact Attributes"
    )

    @property
    def value_arn(self) -> str | None:
        """The value ARN of the contact Attributes."""
        return self.ValueArn

    @property
    def value_integer(self) -> float | None:
        """The value integer of the contact Attributes."""
        return self.ValueInteger

    @property
    def value_list(self) -> list[str] | None:
        """The value list of the contact Attributes."""
        return self.ValueList

    @property
    def value_map(self) -> dict[str, str] | None:
        """The value map of the contact Attributes."""
        return self.ValueMap

    @property
    def value_string(self) -> str | None:
        """The value string of the contact Attributes."""
        return self.ValueString


class ConnectContactFlowAdditionalEmailRecipients(BaseModel):
    """
    Additional email recipients information
    """

    CcList: list[str] = Field(
        ..., description="The email address of the CC recipients", min_length=0
    )
    ToList: list[str] = Field(
        ..., description="The email address of the to recipients", min_length=0
    )

    @property
    def cc_list(self) -> list[str]:
        """The email addresses of the CC recipients."""
        return self.CcList

    @property
    def to_list(self) -> list[str]:
        """The email addresses of the to recipients."""
        return self.ToList


class ConnectContactFlowData(BaseModel):
    """
    Contact flow data information
    """

    Attributes: dict[str, str] = Field(..., description="Contact attributes")
    AwsRegion: str = Field(..., description="AWS region of the contact")
    Channel: ConnectContactFlowChannel = Field(
        ..., description="Contact channel method"
    )
    ContactId: str = Field(..., description="Unique contact identifier")
    CustomerEndpoint: Optional[ConnectContactFlowEndpoint] = Field(
        None, description="Customer endpoint information"
    )
    CustomerId: Optional[str] = Field(None, description="Customer identifier")
    Description: Optional[str] = Field(None, description="Contact description")
    InitialContactId: str = Field(..., description="Initial contact identifier")
    InitiationMethod: ConnectContactFlowInitiationMethod = Field(
        ..., description="Contact initiation method"
    )
    InstanceARN: str = Field(..., description="Amazon Connect instance ARN")
    LanguageCode: Optional[str] = Field(
        None, description="Language code of the contact"
    )
    MediaStreams: ConnectContactFlowMediaStreams = Field(
        ..., description="Media streams information"
    )
    Name: Optional[str] = Field(None, description="Contact name")
    PreviousContactId: str = Field(..., description="Previous contact identifier")
    Queue: Optional[ConnectContactFlowQueue] = Field(
        None, description="Current queue information"
    )
    References: Optional[dict[str, ConnectContactReferenceFields]] = Field(
        None, description="Contact references"
    )
    RelatedContactId: Optional[str] = Field(
        None, description="Related contact identifier"
    )
    SegmentAttributes: Optional[ConnectContactSegmentAttributes] = Field(
        None, description="Contact segment attributes"
    )
    SystemEndpoint: Optional[ConnectContactFlowEndpoint] = Field(
        None, description="System endpoint information"
    )
    Tags: Optional[dict[str, str]] = Field(
        None, description="Tags associated with the contact"
    )

    # Email Specific
    AdditionalEmailRecipients: Optional[ConnectContactFlowAdditionalEmailRecipients] = (
        Field(
            None,
            description="Additional email recipients information. Only relevant for EMAIL channel",
        )
    )

    @property
    def aws_region(self) -> str:
        """The AWS region of the contact."""
        return self.AwsRegion

    @property
    def attributes(self) -> dict[str, str]:
        """
        These are attributes that have been previously associated with a contact.
        This map may be empty if there aren't any attributes.
        """
        return self.Attributes

    @property
    def channel(self) -> ConnectContactFlowChannel:
        """The method used to contact your contact center."""
        return self.Channel

    @property
    def contact_id(self) -> str:
        """The unique identifier of the contact."""
        return self.ContactId

    @property
    def customer_endpoint(self) -> ConnectContactFlowEndpoint | None:
        """Contains the customer's address (number) and type of address."""
        return self.CustomerEndpoint

    @property
    def customer_id(self) -> str | None:
        """The unique identifier of the customer."""
        return self.CustomerId

    @property
    def description(self) -> str | None:
        """The description of the contact."""
        return self.Description

    @property
    def initial_contact_id(self) -> str:
        """
        The unique identifier for the contact associated with the first interaction between
        the customer and your contact center. Use the initial contact ID to track contacts
        between contact flows.
        """
        return self.InitialContactId

    @property
    def initiation_method(self) -> ConnectContactFlowInitiationMethod:
        """How the contact was initiated."""
        return self.InitiationMethod

    @property
    def instance_arn(self) -> str:
        """The ARN for your Amazon Connect instance."""
        return self.InstanceARN

    @property
    def language_code(self) -> str | None:
        """The language code of the contact."""
        return self.LanguageCode

    @property
    def media_streams(self) -> ConnectContactFlowMediaStreams:
        """The media streams for the contact."""
        return self.MediaStreams

    @property
    def name(self) -> str | None:
        """The name of the contact."""
        return self.Name

    @property
    def previous_contact_id(self) -> str:
        """The unique identifier for the contact before it was transferred.
        Use the previous contact ID to trace contacts between contact flows.
        """
        return self.PreviousContactId

    @property
    def queue(self) -> ConnectContactFlowQueue | None:
        """The current queue."""
        return self.Queue

    @property
    def references(self) -> dict[str, ConnectContactReferenceFields] | None:
        """The contact references."""
        return self.References

    @property
    def related_contact_id(self) -> str | None:
        """The unique identifier for a related contact. This can be either link
        showing where this contact was created, or some other tie"""
        return self.RelatedContactId

    @property
    def segment_attributes(self) -> ConnectContactSegmentAttributes | None:
        """The contact segment attributes."""
        return self.SegmentAttributes

    @property
    def system_endpoint(self) -> ConnectContactFlowEndpoint | None:
        """
        Contains the details the customer contacted your contact
        center and type of address.
        """
        return self.SystemEndpoint

    @property
    def tags(self) -> dict[str, str] | None:
        """The tags associated with the contact."""
        return self.Tags

    # Email specific
    @property
    def additional_email_recipients(
        self,
    ) -> ConnectContactFlowAdditionalEmailRecipients | None:
        """Additional email recipients information"""
        return self.AdditionalEmailRecipients


class ConnectContactFlowEventDetails(BaseModel):
    """
    Contact flow event details
    """

    ContactData: ConnectContactFlowData = Field(
        ..., description="Contact data information"
    )
    Parameters: dict[str, str] = Field(
        ..., description="Lambda function parameters", min_length=0
    )


class ConnectContactFlowEvent(BaseModel):
    """
    Amazon Connect contact flow event

    Documentation:
    -------------
    - https://docs.aws.amazon.com/connect/latest/adminguide/connect-lambda-functions.html
    """

    Details: ConnectContactFlowEventDetails = Field(..., description="Event details")

    @property
    def contact_data(self) -> ConnectContactFlowData:
        """This is always passed by Amazon Connect for every contact. Some parameters are optional."""
        return self.Details.ContactData

    @property
    def parameters(self) -> dict[str, str]:
        """These are parameters specific to this call that were defined when you created the Lambda function."""
        return self.Details.Parameters
