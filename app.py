import aws_cdk as cdk

from stack.vpc_network import VpcNetworkStack
import boto3

region_name = boto3.Session().region_name
env={"region": region_name}

app = cdk.App()

network_stack = VpcNetworkStack(app, "ProtoFoundationAIVpcNetworkStack", env=env)

# add tag for project
cdk.Tags.of(app).add("created_by", "Dim Kharitonov")

app.synth()
