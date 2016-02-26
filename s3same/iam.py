import json
from botocore.exceptions import ClientError

IAMName = 's3same_travis'

def _policy_string(bucket):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:ListBucket"
                    ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::{}".format(bucket)
                    ]
                },
            {
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                    ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::{}/*".format(bucket)
                    ]
                }
            ]
        })

def _all_policies(iam, **kwargs):
    marker = None
    while True:
        if marker:
            kwargs['Marker'] = marker
        response = iam.list_policies(**kwargs)
        for policy in response.get('Policies', []):
            yield policy
        marker = response.get('Marker')
        if not response.get('IsTruncated') or marker is None:
            break
    
def _policy_arn(iam, bucket):
    policy_arn = None
    try:
        # Try creating the policy...
        response = iam.create_policy(
                PolicyName=IAMName,
                PolicyDocument=_policy_string(bucket),
                )
        # ... and getting its ARN from the response.
        policy_arn = response.get('Policy', {}).get('Arn')
    except ClientError as e:
        if e.response['Error']['Code'] != 'EntityAlreadyExists':
            raise
        # If the policy already exists, go find it and get its ARN.
        policy_arn = next(
                (p.get('Arn')
                    for p in _all_policies(iam, Scope='Local')
                    if p.get('PolicyName') == IAMName
                    ),
                None)
    # If we failed to get an ARN from creating or finding the policy, that's bad.
    if not policy_arn:
        raise ValueError  # TODO: FIXME
    return policy_arn

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
