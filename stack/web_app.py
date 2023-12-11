from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from constructs import Construct


class WebStack(Stack):
    """
    ECS Cluster and Fargate service for the web application
    """

    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECS cluster
        cluster = ecs.Cluster(self, "ProtoFoundationAIWebCluster", vpc=vpc)

        # Add an AutoScalingGroup with spot instances to the existing cluster
        cluster.add_capacity(
            "AsgSpot",
            max_capacity=2,
            min_capacity=1,
            desired_capacity=2,
            instance_type=ec2.InstanceType("m5.xlarge"),
            # deploy cluster on on-demand instances instead of spot
            # min spot price is 0.0753, on-demand price is 0.192 per hour
            # spot prices https://aws.amazon.com/ec2/spot/pricing/
            # on-demand prices https://aws.amazon.com/ec2/pricing/on-demand/
            # spot_price="0.1",
            # Enable the Automated Spot Draining support for Amazon ECS
            # spot_instance_draining=True,
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
