import boto3
import click
import yaml
from sagemaker import Session, image_uris, model_uris, script_uris, instance_types

@click.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["dev", "qa", "staging", "prod"]),
    required=True,
    help="AWS profile to use",
)
@click.option(
    "--model_id",
    "-m",
    type=click.STRING,
    required=True,
    help="Model ID to get configuration for",
)
@click.option(
    "--model_version",
    "-v",
    type=click.STRING,
    default="*",
    help="Model version to get configuration for, default to latest",
    show_default=True,
)
@click.option(
    "--instance_type",
    "-i",
    type=click.STRING,
    help="Instance type to get configuration for. If not specified, will use default instance type for the model",
)
@click.option(
    "--config_file",
    "-c",
    type=click.Path(
        file_okay=True, dir_okay=False, writable=True, readable=True
    ),
    required=True,
    help="Path to the config file to write to.",
)
def main(profile: str, model_id: str, model_version: str, instance_type: str, config_file: str):
    """
    Retrieves the configuration of a SageMaker model and stores it in the config file as YAML.
    """
    
    session = boto3.Session(profile_name=profile)
    region_name = session.region_name

    # Retrieve the URIs of the JumpStart resources
    base_model_uri: str = model_uris.retrieve(
        region=region_name,
        model_id=model_id,
        model_version=model_version,
        model_scope="inference",
        sagemaker_session=Session(boto_session=session),
    )

    if instance_type is None:
        instance_type: str = instance_types.retrieve_default(
            model_id=model_id,
            model_version=model_version,
            scope="inference",
            sagemaker_session=Session(boto_session=session)
        )

    script_uri: str = script_uris.retrieve(
        region=region_name,
        model_id=model_id,
        model_version=model_version,
        script_scope="inference",
        sagemaker_session=Session(boto_session=session),
    )

    image_uri: str = image_uris.retrieve(
        region=region_name,
        framework=None,
        image_scope="inference",
        model_id=model_id,
        model_version=model_version,
        instance_type=instance_type,
        sagemaker_session=Session(boto_session=session),
    )

    # Read config file if exists otherwise create empty dict
    config = {}
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        pass

    # Update config with new values
    config[model_id] = {
        "base_model_uri": base_model_uri,
        "script_uri": script_uri,
        "image_uri": image_uri,
        "instance_type": instance_type,
    }

    # Write config file
    with open(config_file, "w") as f:
        yaml.dump(config, f)

if __name__ == "__main__":
    main()