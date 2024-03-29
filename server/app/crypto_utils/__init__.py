"""
Utility functions for Crypto Functionality like
RSA encryption, decryption, signature verification, etc.
"""
from datetime import datetime, timedelta
import logging
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID

from app.settings import RSA_SECRET_KEY, SERVER_RSA_KEY_SIZE, USER_RSA_KEY_SIZE


class ServerKeys:
    """
    Holder for server keys
    """
    public_key = None
    private_key = None

    @classmethod
    def serialized_public_key(cls):
        """To be shared to all users"""
        return serialize_public_key(cls.public_key)

def serialize_private_key(key):
    """
    Serialize private key encrypted with `RSA_SECRET`
    """
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(RSA_SECRET_KEY)
    )

def serialize_public_key(key):
    """
    Serialize public key
    """
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def create_pub_key_certificate(pub_key):
    """
    Create x.509 certificate of a user key issued by server
    """
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kerala"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Kochi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Users"),
        x509.NameAttribute(NameOID.COMMON_NAME, "User"),
    ])
    issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kerala"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Kochi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "XPay"),
        x509.NameAttribute(NameOID.COMMON_NAME, "xpay.com")
    ])
    one_day = timedelta(1, 0, 0)
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer)
    builder = builder.not_valid_before(datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.today() + (one_day * 30))
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(pub_key)
    builder = builder.add_extension(
        x509.SubjectAlternativeName(
            [x509.DNSName('uknowwhoim.me')]
        ),
        critical=False
    )
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    )
    certificate = builder.sign(
        private_key=ServerKeys.private_key, algorithm=hashes.SHA256(),
    )
    return certificate.public_bytes(serialization.Encoding.PEM)


def create_private_key():
    """
    Create a key pair for the server
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=SERVER_RSA_KEY_SIZE
    )
    return private_key


def create_user_key_pair():
    """
    Create a key pair for the user
    """
    private_key = create_private_key()
    private_bytes = serialize_private_key(private_key)
    public_bytes = serialize_public_key(private_key.public_key())
    return private_bytes, public_bytes


def deserialize_public_key(key_bytes):
    """
    Deserialize public key from storage
    """
    return serialization.load_pem_public_key(key_bytes)


def deserialize_private_key(key_bytes):
    """
    Deserialize private key from storage
    """
    return serialization.load_pem_private_key(key_bytes, RSA_SECRET_KEY)


def decrypt_private_key(key):
    """
    Decrypt private key stored in db to hand it over to user
    """
    private_key = serialization.load_pem_private_key(key, RSA_SECRET_KEY)
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )


def create_server_keys(filename):
    """
    Create a key pair and store in file for the server
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=SERVER_RSA_KEY_SIZE
    )
    public_key = private_key.public_key()
    private_bytes = serialize_private_key(private_key)
    public_bytes = serialize_public_key(public_key)
    with open(filename, "wb") as private_file:
        private_file.write(private_bytes)
    with open(filename + ".pub", "wb") as public_file:
        public_file.write(public_bytes)

    return private_key, public_key


def load_server_keys():
    """
    Load a key pair from the filesystem
    """
    filename = "server_key"
    try:
        with open(filename, "rb") as private_file:
            private_bytes = private_file.read()
        with open(filename + ".pub", "rb") as public_file:
            public_bytes = public_file.read()
        ServerKeys.private_key = serialization.load_pem_private_key(private_bytes, RSA_SECRET_KEY)
        ServerKeys.public_key = deserialize_public_key(public_bytes)
        logging.info("Loaded server keys")

    except (FileNotFoundError, ValueError) as exc:
        logging.info(exc)
        ServerKeys.private_key, ServerKeys.public_key = create_server_keys(filename)
