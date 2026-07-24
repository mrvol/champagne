"""WebAuthn (passkey) support, built directly on cryptography/cbor2 rather
than a WebAuthn-specific library. Scoped to ES256 (P-256), which is what
Safari's platform authenticator (Touch ID / Face ID passkeys) uses.
"""
import base64

import cbor2
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


def b64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')


def parse_attested_credential_data(auth_data: bytes):
    """authData layout: rpIdHash(32) | flags(1) | signCount(4) | aaguid(16) |
    credIdLen(2) | credId | COSE_Key(CBOR). Only called when the AT flag is set."""
    flags = auth_data[32]
    if not (flags & 0x40):
        raise ValueError('authData has no attested credential data')
    cred_id_len = int.from_bytes(auth_data[53:55], 'big')
    credential_id = auth_data[55:55 + cred_id_len]
    cose_key = cbor2.loads(auth_data[55 + cred_id_len:])
    if cose_key.get(1) != 2 or cose_key.get(3) != -7:
        raise ValueError('only ES256 (P-256) credentials are supported')
    x = int.from_bytes(cose_key[-2], 'big')
    y = int.from_bytes(cose_key[-3], 'big')
    return credential_id, x, y


def sign_count_from_auth_data(auth_data: bytes) -> int:
    return int.from_bytes(auth_data[33:37], 'big')


def verify_assertion_signature(auth_data: bytes, client_data_bytes: bytes, signature: bytes, x: int, y: int) -> bool:
    public_key = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()
    digest = hashes.Hash(hashes.SHA256())
    digest.update(client_data_bytes)
    signed_data = auth_data + digest.finalize()
    try:
        public_key.verify(signature, signed_data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
