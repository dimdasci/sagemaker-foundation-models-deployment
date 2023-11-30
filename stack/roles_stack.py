from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class SageMakerRoles(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        ### Role for the SageMaker endpoints
        self.sm_role = iam.Role(
            self,
            "ProtoFoundationAISageMakerPolicy",
            role_name="proto-foundation-ai-sagemaker-policy",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )
        self.sm_role.add_managed_policy(
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

        self.sm_role.attach_inline_policy(sts_policy)
        self.sm_role.attach_inline_policy(logs_policy)
        self.sm_role.attach_inline_policy(ecr_policy)

        ### Role for the AWS Lambda functions
        self.lambda_role = iam.Role(
            self,
            "ProtoFoundationAILambdaPolicy",
            role_name="proto-foundation-ai-lambda-policy",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        self.lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        self.lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            )
        )
        self.lambda_role.attach_inline_policy(
            iam.Policy(
                self,
                "sagemaker-invoke-policy",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["sagemaker:InvokeEndpoint"],
                        resources=["*"],
                    )
                ],
            )
        )
