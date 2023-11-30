from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from construct.sagemaker_endpoint_construct import SageMakerEndpointConstruct
from constructs import Construct


class Txt2NluSagemakerStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, model_info, role: iam.Role, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        endpoint = SageMakerEndpointConstruct(
            self,
            "ProtoFoundationAITxt2Nlu",
            project_prefix="ProtoFoundationAI",
            role_arn=role.role_arn,
            model_name="HuggingfaceText2TextFlan",
            model_data_url=model_info["model_data_url"],
            model_docker_image=model_info["image"],
            variant_name="AllTraffic",
            variant_weight=1,
            instance_count=1,
            instance_type=model_info["instance_type"],
            environment={
                "MODEL_CACHE_ROOT": "/opt/ml/model",
                "SAGEMAKER_ENV": "1",
                "SAGEMAKER_MODEL_SERVER_TIMEOUT": "3600",
                "SAGEMAKER_MODEL_SERVER_WORKERS": "1",
                "SAGEMAKER_PROGRAM": "inference.py",
                "SAGEMAKER_SUBMIT_DIRECTORY": "/opt/ml/model/code/",
                "TS_DEFAULT_WORKERS_PER_MODEL": "1",
            },
            deploy_enable=True,
        )

        endpoint.node.add_dependency(role)

        ssm.StringParameter(
            self,
            "ProtoFoundationAITxt2NluSmEndpoint",
            parameter_name="proto-foundation-ai-txt2nlu-sm-endpoint",
            string_value=endpoint.endpoint_name,
        )
