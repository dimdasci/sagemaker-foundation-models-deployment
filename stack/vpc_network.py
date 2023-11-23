from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VpcNetworkStack(Stack):
    """
    Represents an AWS CloudFormation stack for deploying a VPC network for the project.

    This stack includes a VPC with public and private subnets.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes a new instance of the VpcNetworkStack.

        Args:
            scope (Construct): The construct scope within which this stack is defined.
            construct_id (str): The identifier for this construct. Must be unique within
                the scope of the parent construct.
            **kwargs (Any): Additional keyword arguments to pass to the base
                class constructor.

        Return:
            None
        """

        super().__init__(scope, construct_id, **kwargs)

        self.output_vpc = ec2.Vpc(
            self,
            "ProtoFoundationAIVPC",
            vpc_name="proto-foundation-ai-vpc",
            nat_gateways=1,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="proto-foundation-ai-public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="proto-foundation-ai-private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

    @property
    def vpc(self) -> ec2.Vpc:
        """
        Gets the VPC instance created by this stack.

        Return:
            ec2.Vpc: The VPC instance.
        """
        return self.output_vpc
