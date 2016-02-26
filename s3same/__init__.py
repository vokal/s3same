import boto3
import travispy
import yaml

from .travis import travis_encrypt as _travis_encrypt
from .iam import credentials_for_new_user, IAMName

def artifact_yaml(
        repo, pro, github_token, github_owner, s3_bucket,
        aws_region=None, aws_key=None, aws_secret=None, aws_profile=None):
    travis = travispy.TravisPy.github_auth(
            github_token,
            uri=travispy.travispy.PRIVATE if pro else travispy.travispy.PUBLIC,
            )
    iam = boto3.session.Session(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
            profile_name=aws_profile,
            ).client('iam')
    access_key = credentials_for_new_user(
            iam,
            '{}__{}__{}'.format(IAMName, github_owner, repo),
            s3_bucket,
            )
    repo_slug = '{}/{}'.format(github_owner, repo)
    return yaml.safe_dump({
        'key': {
            'secure': _travis_encrypt(travis, repo_slug, access_key['AccessKeyId']),
            },
        'secret': {
            'secure': _travis_encrypt(travis, repo_slug, access_key['SecretAccessKey']),
            },
        },
        default_flow_style=False,
        allow_unicode=True,
        )
