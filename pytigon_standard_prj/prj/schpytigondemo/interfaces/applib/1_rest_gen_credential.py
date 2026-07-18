"""Generate a Base64-encoded credential string for OAuth2 client-credentials authentication.

This script encodes client_id and secret in Base64 format, producing a token
suitable for the HTTP Authorization header in OAuth2 token requests.
"""
import base64

# register application: http://127.0.0.1:8000/o/applications/
# Client type: confidential, Authorization Grant Type: lient-credentials
# Rewrite the parameters client_id, secret to the lines below
client_id = ""
secret = ""

credential = "{0}:{1}".format(client_id, secret)
b64_credential = base64.b64encode(credential.encode("utf-8"))

print(b64_credential.decode("utf-8"))
