from aws_cdk import CfnOutput
from aws_cdk import aws_sagemaker as sagemaker
from constructs import Construct


class SageMakerEndpointConstruct(Construct):
    """
    Represents an AWS CDK construct for defining and deploying a SageMaker endpoint
    along with associated configurations.

    Attributes:
        deploy_enable (bool): A flag indicating whether the SageMaker endpoint is set to deploy.
        endpoint (sagemaker.CfnEndpoint): The SageMaker endpoint resource, created when
            deploy_enable is True.

    Properties:
        endpoint_name (str): The name of the deployed SageMaker endpoint. Returns
            "not_yet_deployed" if deploy_enable is False.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        role_arn: str,
        model_name: str,
        model_data_url: str,
        model_docker_image: str,
        variant_name: str,
        variant_weight: int,
        instance_count: int,
        instance_type: str,
        environment: dict,
        deploy_enable: bool,
    ) -> None:
        """
        Initializes a new instance of the SageMakerEndpointConstruct.

        Args:
            scope (Construct): The construct scope within which this construct is defined.
            construct_id (str): The identifier for this construct. Must be unique within
                the scope of the parent construct.
            project_prefix (str): The prefix to be used for naming SageMaker resources.
            role_arn (str): The ARN of the IAM role that SageMaker will assume to create
                and deploy the model.
            model_name (str): The name of the SageMaker model.
            model_data_url (str): The name of the S3 bucket containing the SageMaker model.
            model_docker_image (str): The Docker image URI for the SageMaker model.
            variant_name (str): The name of the production variant for the model.
            variant_weight (int): The initial weight for the model variant.
            instance_count (int): The number of instances to deploy for the model variant.
            instance_type (str): The EC2 instance type for the deployed model instances.
            environment (dict): Environment variables to set for the SageMaker model.
            deploy_enable (bool): A flag indicating whether to deploy the SageMaker endpoint.

        Return:
            None
        """

        super().__init__(scope, construct_id)

        model = sagemaker.CfnModel(
            self,
            f"{model_name}-Model",
            execution_role_arn=role_arn,
            containers=[
                sagemaker.CfnModel.ContainerDefinitionProperty(
                    image=model_docker_image,
                    model_data_url=model_data_url,
                    environment=environment,
                )
            ],
            model_name=f"{project_prefix}-{model_name}-model",
        )

        config = sagemaker.CfnEndpointConfig(
            self,
            f"{model_name}-Config",
            endpoint_config_name=f"{project_prefix}-{model_name}-Config",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=model.attr_model_name,
                    variant_name=variant_name,
                    initial_variant_weight=variant_weight,
                    initial_instance_count=instance_count,
                    instance_type=instance_type,
                )
            ],
        )

        self.deploy_enable = deploy_enable
        if deploy_enable:
            self.endpoint = sagemaker.CfnEndpoint(
                self,
                f"{model_name}-Endpoint",
                endpoint_name=f"{project_prefix}-{model_name}-Endpoint",
                endpoint_config_name=config.attr_endpoint_config_name,
            )

            CfnOutput(
                scope=self,
                id=f"{model_name}EndpointName",
                value=self.endpoint.endpoint_name,
            )

    @property
    def endpoint_name(self) -> str:
        """
        Gets the name of the deployed SageMaker endpoint.

        Return:
            str: The name of the deployed SageMaker endpoint. Returns "not_yet_deployed"
            if deploy_enable is False.
        """

        return (
            self.endpoint.attr_endpoint_name
            if self.deploy_enable
            else "not_yet_deployed"
        )
