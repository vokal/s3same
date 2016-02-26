import json
from botocore.exceptions import ClientError

IAMName = 's3same_travis'

def _policy_string(bucket):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:ListBucket",
                    ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::{}".format(bucket),
                    ],
                },
            {
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::{}/*".format(bucket),
                    ],
                },
            ],
        })

def _find_policy(iam):
    kwargs = {'Scope': 'Local'}
    while True:
        response = iam.list_policies(**kwargs)
        for policy in response.get('Policies', []):
            if policy.get('PolicyName') == IAMName:
                return policy
        kwargs['Marker'] = response.get('Marker')
        if not response.get('IsTruncated') or kwargs['Marker'] is None:
            return None
    
def _create_policy(iam, bucket):
    try:
        # Try creating the policy...
        response = iam.create_policy(
                PolicyName=IAMName,
                PolicyDocument=_policy_string(bucket),
                )
        return response.get('Policy')
    except ClientError as e:
        if e.response['Error']['Code'] != 'EntityAlreadyExists':
            raise
        # If the policy already exists, return None.
        return None

def _policy_arn(iam, bucket):
    policy = _create_policy(iam, bucket) or _find_policy(iam)
    try:
        return policy['Arn']
    except (TypeError, KeyError):
        raise ValueError  # TODO: more specific error?

def _create_group_if_needed(iam, bucket):
    try:
        iam.create_group(GroupName=IAMName)
    except ClientError as e:
        if e.response['Error']['Code'] != 'EntityAlreadyExists':
            raise
    iam.attach_group_policy(
            GroupName=IAMName,
            PolicyArn=_policy_arn(iam, bucket),
            )

def credentials_for_new_user(iam, username, bucket=IAMName):
    _create_group_if_needed(iam, bucket)
    try:
        iam.create_user(UserName=username)
    except ClientError as e:
        if e.response['Error']['Code'] != 'EntityAlreadyExists':
            raise
    iam.add_user_to_group(UserName=username, GroupName=IAMName)
    return iam.create_access_key(UserName=username).get('AccessKey')
