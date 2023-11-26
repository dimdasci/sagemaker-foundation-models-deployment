from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from construct.sagemaker_endpoint_construct import SageMakerEndpointConstruct
from constructs import Construct


class GenerativeAiTxt2imgSagemakerStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, model_info, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(
            self,
            "ProtoFoundationAISageMakerPolicy",
            role_name="proto-foundation-ai-sagemaker-policy",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )

        sts_policy = iam.Policy(
            self,
            "ProtoFoundationAIDeployPolicySts",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW, actions=["sts:AssumeRole"], resources=["*"]
                )
            ],
        )

        logs_policy = iam.Policy(
            self,
            "ProtoFoundationAIDeployPolicyLogs",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudwatch:PutMetricData",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:CreateLogGroup",
                        "logs:DescribeLogStreams",
                        "ecr:GetAuthorizationToken",
                    ],
                    resources=["*"],
                )
            ],
        )

        ecr_policy = iam.Policy(
            self,
            "ProtoFoundationAIDeployPolicyEcr",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ecr:*",
                    ],
                    resources=["*"],
                )
            ],
        )

        role.attach_inline_policy(sts_policy)
        role.attach_inline_policy(logs_policy)
        role.attach_inline_policy(ecr_policy)

        endpoint = SageMakerEndpointConstruct(
            self,
            "ProtoFoundationAITxt2Img",
            project_prefix="ProtoFoundationAI",
            role_arn=role.role_arn,
            model_name="StableDiffusionText2Img",
            model_bucket_name=model_info["model_bucket_name"],
            model_bucket_key=model_info["model_bucket_key"],
            model_docker_image=model_info["model_docker_image"],
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

        endpoint.node.add_dependency(sts_policy)
        endpoint.node.add_dependency(logs_policy)
        endpoint.node.add_dependency(ecr_policy)

        ssm.StringParameter(
            self,
            "ProtoFoundationAITxt2ImgSmEndpoint",
            parameter_name="proto-foundation-ai-txt2img-sm-endpoint",
            string_value=endpoint.endpoint_name,
        )
