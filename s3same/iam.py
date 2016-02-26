from botocore.exceptions import ClientError

IAMName = 's3same_travis'

def _policy_string(bucket):
    return """{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "s3:ListBucket"
          ],
          "Effect": "Allow",
          "Resource": [
            "arn:aws:s3:::%(bucket)s"
          ]
        },
        {
          "Action": [
            "s3:PutObject",
            "s3:PutObjectAcl"
          ],
          "Effect": "Allow",
          "Resource": [
            "arn:aws:s3:::%(bucket)s/*"
          ]
        }
      ]
    }""" % dict(bucket=bucket)

def _policy_arn(iam, bucket):
    policy_arn = None
    try:
        response = iam.create_policy(
                PolicyName=IAMName,
                PolicyDocument=_policy_string(bucket),
                )
        policy_arn = response.get('Policy', {}).get('Arn')
    except ClientError as e:
        if e.response['Error']['Code'] != 'EntityAlreadyExists':
            raise
        marker = None
        while not policy_arn:
            response = iam.list_policies(Scope='Local')
            policy_arn = next((p.get('Arn') for p in response.get('Policies', []) if p.get('PolicyName') == IAMName), None)
            if not response.get('IsTruncated'):
                break
            marker = response['Marker']
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
