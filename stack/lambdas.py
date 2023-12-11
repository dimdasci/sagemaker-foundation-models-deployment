from aws_cdk import Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class LambdasStack(Stack):
    """
    Lambdas to proxy requests to SageMaker endpoints
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        role: iam.Role,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Defines an AWS Lambda function for Image Generation service
        lambda_txt2img = _lambda.Function(
            self,
            "ProtoFoundationAILambdaTxt2Img",
            function_name="proto-foundation-ai-lambda-txt2img",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("src/lambda_txt2img"),
            handler="txt2img.lambda_handler",
            role=role,
            timeout=Duration.seconds(180),
            memory_size=512,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            vpc=vpc,
        )

        # Defines an Amazon API Gateway endpoint for Image Generation service
        txt2img_apigw_endpoint = apigw.LambdaRestApi(
            self, "ProtoFoundationAITxt2ImgEndpoint", handler=lambda_txt2img
        )

        # Defines an AWS Lambda function for NLU & Text Generation service
        lambda_txt2nlu = _lambda.Function(
            self,
            "ProtoFoundationAILambdaTxt2Nlu",
            function_name="proto-foundation-ai-lambda-txt2nlu",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("src/lambda_txt2nlu"),
            handler="txt2nlu.lambda_handler",
            role=role,
            timeout=Duration.seconds(180),
            memory_size=512,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            vpc=vpc,
        )

        # Defines an Amazon API Gateway endpoint for NLU & Text Generation service
        txt2nlu_apigw_endpoint = apigw.LambdaRestApi(
            self, "ProtoFoundationAITxt2NluEndpoint", handler=lambda_txt2nlu
        )

        ssm.StringParameter(
            self,
            "ProtoFoundationAITxt2ImgEndpointParameter",
            parameter_name="proto-foundation-ai-txt2img-endpoint",
            string_value=txt2img_apigw_endpoint.url,
        )
        ssm.StringParameter(
            self,
            "ProtoFoundationAITxt2NluEndpointParameter",
            parameter_name="proto-foundation-ai-txt2nlu-endpoint",
            string_value=txt2nlu_apigw_endpoint.url,
        )
