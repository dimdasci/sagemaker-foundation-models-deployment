from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from construct.sagemaker_endpoint_construct import SageMakerEndpointConstruct
from constructs import Construct


class Txt2ImgSagemakerStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, model_info, role: iam.Role, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        endpoint = SageMakerEndpointConstruct(
            self,
            "ProtoFoundationAITxt2Img",
            project_prefix="ProtoFoundationAI",
            role_arn=role.role_arn,
            model_name="StableDiffusionText2Img",
            model_data_url=model_info["model_data_url"],
            model_docker_image=model_info["image"],
            variant_name="AllTraffic",
            variant_weight=1,
            instance_count=1,
            instance_type=model_info["instance_type"],
            environment={
                "MMS_MAX_RESPONSE_SIZE": "20000000",
                "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
                "SAGEMAKER_PROGRAM": "inference.py",
                "SAGEMAKER_REGION": model_info["region_name"],
                "SAGEMAKER_SUBMIT_DIRECTORY": "/opt/ml/model/code",
            },
            deploy_enable=True,
        )

        endpoint.node.add_dependency(role)

        ssm.StringParameter(
            self,
            "ProtoFoundationAITxt2ImgSmEndpoint",
            parameter_name="proto-foundation-ai-txt2img-sm-endpoint",
            string_value=endpoint.endpoint_name,
        )
