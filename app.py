import aws_cdk as cdk
import boto3
import yaml
from stack.roles_stack import SageMakerRoles
from stack.txt2image_stack import Txt2ImgSagemakerStack
from stack.txt2nlu_stack import Txt2NluSagemakerStack
from stack.vpc_network import VpcNetworkStack
from stack.web_app import WebStack


app = cdk.App()

# read config file from ./models.yaml. If it doesn't exist, raise an error
try:
    with open("models.yaml", "r") as f:
        models = yaml.safe_load(f)
except FileNotFoundError:
    raise FileNotFoundError(
        "Please create a models.yaml file with the model information"
    )

TXT2IMG_MODEL_INFO = models["model-txt2img-stabilityai-stable-diffusion-v2"]
TXT2NLU_MODEL_INFO = models["huggingface-text2text-flan-t5-xl"]

network_stack = VpcNetworkStack(app, "ProtoFoundationAIVpcNetworkStack")
role_stack = SageMakerRoles(app, "ProtoFoundationAISageMakerRolesStack")
Txt2ImgSagemakerStack(
    app,
    "ProtoFoundationAITxt2ImgSagemakerStack",
    model_info=TXT2IMG_MODEL_INFO,
    role=role_stack.sm_role,
)
Txt2NluSagemakerStack(
    app,
    "ProtoFoundationAITxt2NluSagemakerStack",
    model_info=TXT2NLU_MODEL_INFO,
    role=role_stack.sm_role,
)
WebStack(
    app,
    "ProtoFoundationAIWebStack",
    vpc=network_stack.vpc,
    role=role_stack.lambda_role,
)


# add tag for project
cdk.Tags.of(app).add("created_by", "Dim Kharitonov")
cdk.Tags.of(app).add("project", "Foundation Models Demo")

app.synth()
