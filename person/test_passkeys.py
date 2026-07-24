import hashlib
import os

import cbor2
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from django.test import TestCase

from person.models import User, WebAuthnCredential
from person.passkeys import (
    b64url_decode, b64url_encode, parse_attested_credential_data,
    sign_count_from_auth_data, verify_assertion_signature,
)

RP_ID = 'testserver'
ORIGIN = 'http://testserver'


def make_key_pair():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key().public_numbers()
    return priv, pub.x, pub.y


def make_cose_key(x, y, alg=-7, kty=2):
    return cbor2.dumps({1: kty, 3: alg, -1: 1, -2: x.to_bytes(32, 'big'), -3: y.to_bytes(32, 'big')})


def make_auth_data(rp_id=RP_ID, flags=0x41, sign_count=0, credential_id=None, cose_key_bytes=b''):
    rp_id_hash = hashlib.sha256(rp_id.encode()).digest()
    data = rp_id_hash + bytes([flags]) + sign_count.to_bytes(4, 'big')
    if flags & 0x40:
        data += b'\x00' * 16 + len(credential_id).to_bytes(2, 'big') + credential_id + cose_key_bytes
    return data


def sign(priv, auth_data, client_data_bytes):
    signed_data = auth_data + hashlib.sha256(client_data_bytes).digest()
    return priv.sign(signed_data, ec.ECDSA(hashes.SHA256()))


# --- unit tests: person/passkeys.py helpers, no DB needed ---

def test_b64url_round_trip():
    raw = os.urandom(37)
    assert b64url_decode(b64url_encode(raw)) == raw


def test_parse_attested_credential_data_extracts_id_and_key():
    priv, x, y = make_key_pair()
    credential_id = os.urandom(16)
    auth_data = make_auth_data(credential_id=credential_id, cose_key_bytes=make_cose_key(x, y))

    cred_id_out, x_out, y_out = parse_attested_credential_data(auth_data)

    assert cred_id_out == credential_id
    assert x_out == x
    assert y_out == y


def test_parse_attested_credential_data_requires_attested_flag():
    auth_data = make_auth_data(flags=0x01)  # UP only, no AT
    with pytest.raises(ValueError):
        parse_attested_credential_data(auth_data)


def test_parse_attested_credential_data_rejects_non_es256():
    _, x, y = make_key_pair()
    credential_id = os.urandom(16)
    bad_cose_key = cbor2.dumps({1: 3, 3: -257, -1: 1, -2: x.to_bytes(32, 'big'), -3: y.to_bytes(32, 'big')})
    auth_data = make_auth_data(credential_id=credential_id, cose_key_bytes=bad_cose_key)

    with pytest.raises(ValueError):
        parse_attested_credential_data(auth_data)


def test_sign_count_from_auth_data():
    auth_data = make_auth_data(flags=0x01, sign_count=42)
    assert sign_count_from_auth_data(auth_data) == 42


def test_verify_assertion_signature_accepts_valid_signature():
    priv, x, y = make_key_pair()
    auth_data = make_auth_data(flags=0x01, sign_count=1)
    client_data = b'{"type":"webauthn.get","challenge":"abc","origin":"http://testserver"}'
    signature = sign(priv, auth_data, client_data)

    assert verify_assertion_signature(auth_data, client_data, signature, x, y) is True


def test_verify_assertion_signature_rejects_tampered_signature():
    priv, x, y = make_key_pair()
    auth_data = make_auth_data(flags=0x01, sign_count=1)
    client_data = b'{"type":"webauthn.get","challenge":"abc","origin":"http://testserver"}'
    signature = bytearray(sign(priv, auth_data, client_data))
    signature[-1] ^= 0xFF

    assert verify_assertion_signature(auth_data, client_data, bytes(signature), x, y) is False


def test_verify_assertion_signature_rejects_wrong_key():
    priv, _, _ = make_key_pair()
    _, other_x, other_y = make_key_pair()
    auth_data = make_auth_data(flags=0x01, sign_count=1)
    client_data = b'{"type":"webauthn.get","challenge":"abc","origin":"http://testserver"}'
    signature = sign(priv, auth_data, client_data)

    assert verify_assertion_signature(auth_data, client_data, signature, other_x, other_y) is False


def test_verify_assertion_signature_rejects_tampered_client_data():
    priv, x, y = make_key_pair()
    auth_data = make_auth_data(flags=0x01, sign_count=1)
    client_data = b'{"type":"webauthn.get","challenge":"abc","origin":"http://testserver"}'
    signature = sign(priv, auth_data, client_data)
    tampered_client_data = client_data.replace(b'abc', b'xyz')

    assert verify_assertion_signature(auth_data, tampered_client_data, signature, x, y) is False


# --- integration tests: the four ceremony views, real DB required ---

class PasskeyRegisterViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='amelie@example.com', email='amelie@example.com',
                                              password='supersecret1')

    def test_options_requires_login(self):
        response = self.client.get('/passkey/register/options/')
        assert response.status_code == 400

    def test_options_returns_challenge_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/passkey/register/options/')
        assert response.status_code == 200
        body = response.json()
        assert body['rp']['id'] == RP_ID
        assert body['pubKeyCredParams'] == [{'type': 'public-key', 'alg': -7}]
        assert 'challenge' in body

    def test_verify_stores_credential(self):
        self.client.force_login(self.user)
        challenge = self.client.get('/passkey/register/options/').json()['challenge']

        priv, x, y = make_key_pair()
        credential_id = os.urandom(16)
        auth_data = make_auth_data(credential_id=credential_id, cose_key_bytes=make_cose_key(x, y))
        client_data = ('{"type":"webauthn.create","challenge":"%s","origin":"%s"}' % (challenge, ORIGIN)).encode()
        attestation_object = cbor2.dumps({'fmt': 'none', 'attStmt': {}, 'authData': auth_data})

        payload = {
            'id': b64url_encode(credential_id),
            'response': {
                'clientDataJSON': b64url_encode(client_data),
                'attestationObject': b64url_encode(attestation_object),
            },
        }
        response = self.client.post('/passkey/register/verify/', data=payload, content_type='application/json')

        assert response.status_code == 200
        credential = WebAuthnCredential.objects.get(user=self.user)
        assert bytes(credential.credential_id) == credential_id
        assert int.from_bytes(bytes(credential.public_key_x), 'big') == x
        assert int.from_bytes(bytes(credential.public_key_y), 'big') == y

    def test_verify_rejects_wrong_challenge(self):
        self.client.force_login(self.user)
        self.client.get('/passkey/register/options/')  # sets a real challenge in session

        priv, x, y = make_key_pair()
        credential_id = os.urandom(16)
        auth_data = make_auth_data(credential_id=credential_id, cose_key_bytes=make_cose_key(x, y))
        client_data = ('{"type":"webauthn.create","challenge":"%s","origin":"%s"}' % ('not-the-real-challenge', ORIGIN)).encode()
        attestation_object = cbor2.dumps({'fmt': 'none', 'attStmt': {}, 'authData': auth_data})

        payload = {
            'id': b64url_encode(credential_id),
            'response': {
                'clientDataJSON': b64url_encode(client_data),
                'attestationObject': b64url_encode(attestation_object),
            },
        }
        response = self.client.post('/passkey/register/verify/', data=payload, content_type='application/json')

        assert response.status_code == 400
        assert not WebAuthnCredential.objects.filter(user=self.user).exists()

    def test_verify_rejects_wrong_origin(self):
        self.client.force_login(self.user)
        challenge = self.client.get('/passkey/register/options/').json()['challenge']

        priv, x, y = make_key_pair()
        credential_id = os.urandom(16)
        auth_data = make_auth_data(credential_id=credential_id, cose_key_bytes=make_cose_key(x, y))
        client_data = ('{"type":"webauthn.create","challenge":"%s","origin":"https://evil.example"}' % challenge).encode()
        attestation_object = cbor2.dumps({'fmt': 'none', 'attStmt': {}, 'authData': auth_data})

        payload = {
            'id': b64url_encode(credential_id),
            'response': {
                'clientDataJSON': b64url_encode(client_data),
                'attestationObject': b64url_encode(attestation_object),
            },
        }
        response = self.client.post('/passkey/register/verify/', data=payload, content_type='application/json')

        assert response.status_code == 400
        assert not WebAuthnCredential.objects.filter(user=self.user).exists()


class PasskeyLoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='amelie@example.com', email='amelie@example.com',
                                              password='supersecret1')
        self.priv, self.x, self.y = make_key_pair()
        self.credential_id = os.urandom(16)
        self.credential = WebAuthnCredential.objects.create(
            user=self.user,
            credential_id=self.credential_id,
            public_key_x=self.x.to_bytes(32, 'big'),
            public_key_y=self.y.to_bytes(32, 'big'),
        )

    def _get_login_challenge(self):
        response = self.client.post('/passkey/login/options/', {'email': self.user.username})
        assert response.status_code == 200
        return response.json()

    def test_options_rejects_unknown_email(self):
        response = self.client.post('/passkey/login/options/', {'email': 'nobody@example.com'})
        assert response.status_code == 400

    def test_options_lists_registered_credential(self):
        body = self._get_login_challenge()
        assert body['allowCredentials'] == [{'type': 'public-key', 'id': b64url_encode(self.credential_id)}]

    def test_verify_logs_user_in_and_bumps_sign_count(self):
        challenge = self._get_login_challenge()['challenge']
        auth_data = make_auth_data(flags=0x01, sign_count=7)
        client_data = ('{"type":"webauthn.get","challenge":"%s","origin":"%s"}' % (challenge, ORIGIN)).encode()
        signature = sign(self.priv, auth_data, client_data)

        payload = {
            'id': b64url_encode(self.credential_id),
            'response': {
                'clientDataJSON': b64url_encode(client_data),
                'authenticatorData': b64url_encode(auth_data),
                'signature': b64url_encode(signature),
            },
        }
        response = self.client.post('/passkey/login/verify/', data=payload, content_type='application/json')

        assert response.status_code == 200
        assert response.json()['ok'] is True
        self.credential.refresh_from_db()
        assert self.credential.sign_count == 7

        home = self.client.get('/')
        assert b'Logout' in home.content

    def test_verify_rejects_bad_signature(self):
        challenge = self._get_login_challenge()['challenge']
        auth_data = make_auth_data(flags=0x01, sign_count=1)
        client_data = ('{"type":"webauthn.get","challenge":"%s","origin":"%s"}' % (challenge, ORIGIN)).encode()
        signature = bytearray(sign(self.priv, auth_data, client_data))
        signature[-1] ^= 0xFF

        payload = {
            'id': b64url_encode(self.credential_id),
            'response': {
                'clientDataJSON': b64url_encode(client_data),
                'authenticatorData': b64url_encode(auth_data),
                'signature': b64url_encode(bytes(signature)),
            },
        }
        response = self.client.post('/passkey/login/verify/', data=payload, content_type='application/json')

        assert response.status_code == 400

    def test_verify_rejects_replayed_sign_count(self):
        self.credential.sign_count = 10
        self.credential.save()
        challenge = self._get_login_challenge()['challenge']
        auth_data = make_auth_data(flags=0x01, sign_count=5)  # lower than stored -> replay
        client_data = ('{"type":"webauthn.get","challenge":"%s","origin":"%s"}' % (challenge, ORIGIN)).encode()
        signature = sign(self.priv, auth_data, client_data)

        payload = {
            'id': b64url_encode(self.credential_id),
            'response': {
                'clientDataJSON': b64url_encode(client_data),
                'authenticatorData': b64url_encode(auth_data),
                'signature': b64url_encode(signature),
            },
        }
        response = self.client.post('/passkey/login/verify/', data=payload, content_type='application/json')

        assert response.status_code == 400
        self.credential.refresh_from_db()
        assert self.credential.sign_count == 10
