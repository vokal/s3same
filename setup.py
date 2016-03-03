from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(name='s3same',
      version='0.1',
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

