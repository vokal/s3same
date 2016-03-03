from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.py3compat import b
import travispy

def _get_key(travis, repo_slug):
    r = travis._session.get(
            '{}/repos/{}/key'.format(travis._session.uri, repo_slug)
            )
    r.raise_for_status()
    return r.json().get('key')

def travis_encrypt(travis, repo_slug, string):
    return b64encode(
            PKCS1_v1_5.new(
                RSA.importKey(_get_key(travis, repo_slug))
                ).encrypt(b(string)))
