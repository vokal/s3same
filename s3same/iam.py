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

def _all_pages(iam_method, item_key, **kwargs):
    while True:
        response = iam_method(**kwargs)
        for key in response.get(item_key, []):
            yield key
        kwargs['Marker'] = response.get('Marker')
        if not response.get('IsTruncated') or kwargs['Marker'] is None:
            return

def _find_policy(iam):
    for policy in _all_pages(iam.list_policies, 'Policies', Scope='Local'):
        if policy.get('PolicyName') == IAMName:
            return policy
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

def _delete_policy(iam):
    policy = _find_policy(iam)
    try:
        policy_arn = policy['Arn']
    except:
        return
    iam.detach_group_policy(GroupName=IAMName, PolicyArn=policy_arn)
    iam.delete_policy(PolicyArn=policy_arn)

def _users_in_group(iam):
    return _all_pages(iam.get_group, 'Users', GroupName=IAMName)

def _keys_for_user(iam, username):
    return _all_pages(iam.list_access_keys, 'AccessKeyMetadata', UserName=username)

def nuke_iam(iam):
    try:
        users = list(_users_in_group(iam))
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchEntity':
            raise
        users = []
    for user in users:
        username = user.get('UserName')
        if not username:
            continue
        for key in _keys_for_user(iam, username):
            iam.delete_access_key(UserName=username, AccessKeyId=key.get('AccessKeyId'))
        iam.remove_user_from_group(GroupName=IAMName, UserName=username)
        iam.delete_user(UserName=username)
    _delete_policy(iam)
    try:
        iam.delete_group(GroupName=IAMName)
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchEntity':
            raise
    
