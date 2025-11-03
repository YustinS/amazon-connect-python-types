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


class ConnectContactFlowEndpoint(BaseModel):
    """
    Contact endpoint information
    """

    Address: str = Field(..., description="The phone number")
    Type: ConnectContactFlowEndpointType = Field(..., description="The endpoint type")

    @property
    def address(self) -> str:
        """The address as contacted in Connect."""
        return self.Address

    @property
    def endpoint_type(self) -> ConnectContactFlowEndpointType:
        """The endpoint type."""
        return self.Type


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


class ConnectContactFlowData(BaseModel):
    """
    Contact flow data information
    """

    Attributes: dict[str, str] = Field(..., description="Contact attributes")
    Channel: ConnectContactFlowChannel = Field(
        ..., description="Contact channel method"
    )
    ContactId: str = Field(..., description="Unique contact identifier")
    CustomerEndpoint: Optional[ConnectContactFlowEndpoint] = Field(
        None, description="Customer endpoint information"
    )
    InitialContactId: str = Field(..., description="Initial contact identifier")
    InitiationMethod: ConnectContactFlowInitiationMethod = Field(
        ..., description="Contact initiation method"
    )
    InstanceARN: str = Field(..., description="Amazon Connect instance ARN")
    PreviousContactId: str = Field(..., description="Previous contact identifier")
    Queue: Optional[ConnectContactFlowQueue] = Field(
        None, description="Current queue information"
    )
    SystemEndpoint: Optional[ConnectContactFlowEndpoint] = Field(
        None, description="System endpoint information"
    )
    MediaStreams: ConnectContactFlowMediaStreams = Field(
        ..., description="Media streams information"
    )

    @property
    def attributes(self) -> dict[str, str]:
        """These are attributes that have been previously associated with a contact,
        such as when using a Set contact attributes block in a contact flow.
        This map may be empty if there aren't any saved attributes.
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
    def system_endpoint(self) -> ConnectContactFlowEndpoint | None:
        """Contains the address (number) the customer dialed to call your contact center and type of address."""
        return self.SystemEndpoint

    @property
    def media_streams(self) -> ConnectContactFlowMediaStreams:
        """The media streams for the contact."""
        return self.MediaStreams


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
