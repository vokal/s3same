import boto3
import travispy
import yaml

from .travis import travis_encrypt as _travis_encrypt
from .iam import credentials_for_new_user, nuke_iam, IAMName

__all__ = [ 'artifact_yaml', 'travis_encrypt', 'iam_credentials', 'iam_nuke', ]

def artifact_yaml(
        repo, pro, github_token, github_owner, s3_bucket,
        aws_region=None, aws_key=None, aws_secret=None, aws_profile=None):
    credentials = iam_credentials(repo, github_owner, s3_bucket, aws_region, aws_key, aws_secret, aws_profile)
    enc_key, enc_secret = travis_encrypt(
            repo, pro, github_token, github_owner,
            (credentials['AccessKeyId'], credentials['SecretAccessKey'],),
            )
    return yaml.safe_dump({
        'key': { 'secure': enc_key.decode('latin-1'), },
        'secret': { 'secure': enc_secret.decode('latin-1'), },
        },
        default_flow_style=False,
        )

def travis_encrypt(repo, pro, github_token, github_owner, strings):
    travis = travispy.TravisPy.github_auth(
            github_token,
            uri=travispy.travispy.PRIVATE if pro else travispy.travispy.PUBLIC,
            )
    repo_slug = '{}/{}'.format(github_owner, repo)
    return (_travis_encrypt(travis, repo_slug, string) for string in strings)

def iam_credentials(
        repo, github_owner, s3_bucket,
        aws_region=None, aws_key=None, aws_secret=None, aws_profile=None):
    iam = boto3.session.Session(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
            profile_name=aws_profile,
            ).client('iam')
    return credentials_for_new_user(
            iam,
            '{}__{}__{}'.format(IAMName, github_owner, repo),
            s3_bucket,
            )

def iam_nuke(aws_region=None, aws_key=None, aws_secret=None, aws_profile=None):
    iam = boto3.session.Session(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
            profile_name=aws_profile,
            ).client('iam')
    nuke_iam(iam)
