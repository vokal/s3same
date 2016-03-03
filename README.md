# s3same
`s3same` ("sesame", like ["open sesame"](https://en.wikipedia.org/wiki/Open_Sesame_(phrase))) creates unique-per-repo AWS credentials for Travis CI artifact uploading to S3 and encrypts those credentials with the repo's public key.

## Installation

Running the command
```sh
sudo pip install s3same
```
will install the latest stable release of `s3same` as a command in `/usr/local/bin`.

## Usage

```
$ s3same --help
Usage: s3same [OPTIONS] REPO

Options:
  --pro               Use Travis CI Pro
  --github TEXT       GitHub token
  --owner TEXT        GitHub owner
  --s3-bucket TEXT    S3 bucket for artifacts
  --aws-region TEXT   AWS region
  --aws-key TEXT      AWS key
  --aws-secret TEXT   AWS secret
  --aws-profile TEXT  AWS profile
  --nuke              Nuke the entire s3same setup on IAM
  --help              Show this message and exit.
```

Let's assume you've got your AWS credentials in [`~/.aws/credentials`](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files).  Go to your GitHub settings and [create a personal access token](https://github.com/settings/tokens/new) for `s3same` (the token must have the `repo` permission).  Create `~/.s3same` with:
```
GITHUB_TOKEN=put your token here
S3_BUCKET=the bucket to which artifacts will be uploaded
AWS_PROFILE=some profile
AWS_REGION=your AWS region
```
If your AWS credentials are in the default profile, you can omit the `AWS_PROFILE` line.

With all the credentials in place, running
```
$ s3same some-repo-name --owner some-user --pro
```
will create an AWS IAM user unique to the repo (`s3same_travis__some-user__some-repo-name`), add that user to the `s3same_travis` AWS IAM group (creating the group if it doesn't exist) to give it the necessary permissions (defined by the `s3same_travis` policy, which will be created if it doesn't exist), generate an AWS key and secret for that user, use the public key for the given repo on Travis CI to encrypt the key and secret, and print out the YAML snippet to use for artifact uploading credentials.

## Configuration

Several configuration parameters can be specified by the environment, in the `~/.s3same` file, or on the command line.  The name/syntax for environment variables and within the `~/.s3same` file are the same.  Anything in the `~/.s3same` file overrides the corresponding environment variable and anything passed as a command-line parameter overrides the environment variables and the `~/.s3same` file.  Setting an AWS key/secret pair overrides specifying an AWS configuration profile.

Parameter | Variable Name | Command-Line
--- | --- | ---
GitHub Token | `GITHUB_TOKEN` | `--github`
GitHub Owner | `GITHUB_OWNER` | `--owner`
S3 Bucket | `S3_BUCKET` | `--s3-bucket`
AWS Region | `AWS_REGION` | `--aws-region`
AWS Key | `AWS_ACCESS_KEY_ID` | `--aws-key`
AWS Secret | `AWS_SECRET_ACCESS_KEY` | `--aws-secret`
AWS Profile | `AWS_PROFILE` | `--aws-profile`
