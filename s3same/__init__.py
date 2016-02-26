import boto3
import travispy
import yaml

from .travis import travis_encrypt as _travis_encrypt
from .iam import credentials_for_new_user, IAMName

class S3same (object):
    def __init__(self, 
            repo, pro, github_token, github_owner, s3_bucket,
            aws_region=None, aws_key=None, aws_secret=None, aws_profile=None):
        uri = travispy.travispy.PRIVATE if pro else travispy.travispy.PUBLIC
        self._travis = travispy.TravisPy.github_auth(github_token, uri=uri)
        self._aws = boto3.session.Session(
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
                region_name=aws_region,
                profile_name=aws_profile)
        self._repo_slug = '{}/{}'.format(github_owner, repo)
        self._iam_user = '{}__{}__{}'.format(IAMName, github_owner, repo)
        self._s3_bucket = s3_bucket

    def artifact_yaml(self):
        iam = self._aws.client('iam')
        access_key = credentials_for_new_user(iam, self._iam_user, self._s3_bucket)
        return yaml.safe_dump({
            'key': {
                'secure': self.travis_encrypt(access_key['AccessKeyId']),
                },
            'secret': {
                'secure': self.travis_encrypt(access_key['SecretAccessKey']),
                },
            },
            default_flow_style=False,
            allow_unicode=True,
            )

    def travis_encrypt(self, string):
        return _travis_encrypt(self._travis, self._repo_slug, string)
