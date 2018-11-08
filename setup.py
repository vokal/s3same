from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='s3same',
      version='0.2',
      description='Configure Travis-CI artifact uploading to S3',
      long_description=long_description,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
      ],
      keywords='travis ci s3 artifact',
      url='http://github.com/vokal/s3same',
      author='Vokal',
      author_email='pypi@vokal.io',
      use_2to3=True,
      license='MIT',
      packages=['s3same'],
      install_requires=[
          'click',
          'boto3',
          'pycrypto',
          'python-dotenv',
          'pyyaml',
          'travispy',
          ],
      include_package_data=True,
      scripts=[
          'bin/s3same',
          ],
      zip_safe=False)

