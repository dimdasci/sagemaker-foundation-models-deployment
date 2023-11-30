from aws_cdk import Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class WebStack(Stack):
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

        # Create ECS cluster
        cluster = ecs.Cluster(self, "ProtoFoundationAIWebCluster", vpc=vpc)

        # Add an AutoScalingGroup with spot instances to the existing cluster
        cluster.add_capacity(
            "AsgSpot",
            max_capacity=2,
            min_capacity=1,
            desired_capacity=2,
            instance_type=ec2.InstanceType("c5.xlarge"),
            spot_price="0.0735",
            # Enable the Automated Spot Draining support for Amazon ECS
            spot_instance_draining=True,
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset("web-app")

        # Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ProtoFoundationAIWebWebApplication",
            cluster=cluster,  # Required
            cpu=2048,  # Default is 256 (512 is 0.5 vCPU, 2048 is 2 vCPU)
            desired_count=1,  # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,
            ),
            load_balancer_name="proto-foundation-ai-web-balancer",
            memory_limit_mib=4096,  # Default is 512
            public_load_balancer=True,
        )  # Default is True

        fargate_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter"],
                resources=["arn:aws:ssm:*"],
            )
        )

        fargate_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["execute-api:Invoke", "execute-api:ManageConnections"],
                resources=["*"],
            )
        )

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=10)
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
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
