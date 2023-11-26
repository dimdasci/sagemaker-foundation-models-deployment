import boto3

region_name = boto3.Session().region_name
print(f"Config, Region: {region_name}")

# parameter name from GenerativeAiDemoWebStack
key_txt2img_api_endpoint = "proto-foundation-ai-txt2img-endpoint" 
# this value is from GenerativeAiTxt2ImgSagemakerStack
key_txt2img_sm_endpoint = "txt2img_sm_endpoint"   

# parameter name from GenerativeAiDemoWebStack
key_txt2nlu_api_endpoint = "proto-foundation-ai-txt2nlu-endpoint" 
# this value is from GenerativeAiTxt2nluSagemakerStack
key_txt2nlu_sm_endpoint = "txt2nlu_sm_endpoint"   

def get_parameter(name):
    """
    This function retrieves a specific value from Systems Manager"s ParameterStore.
    """     
    ssm_client = boto3.Session().client("ssm",region_name=region_name)
    response = ssm_client.get_parameter(Name=name)
    value = response["Parameter"]["Value"]
    
    return value