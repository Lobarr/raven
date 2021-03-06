import os
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.kdf import x963kdf
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from api.util import Bytes


class Crypt:
    @staticmethod
    def generate_key_pair() -> object:
        """
        generates key pair

        @returns: public and private key pair
        """
        private_key = ec.generate_private_key(
            ec.SECP256K1(), default_backend()
        )
        serialized_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        public_key = private_key.public_key()
        serialized_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return {
            'private_key': serialized_private_key,
            'public_key': serialized_public_key
        }

    @staticmethod
    def sign(message: object, private_key: str) -> str:
        """
        signs a message

        @param message: (object) message to sign
        @param private_key: (str) private key to sign with
        """
        private_key_bytes = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        message_bytes = Bytes.object_to_bytes(message)
        signature_bytes = private_key_bytes.sign(
            message_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return Bytes.encode_bytes(signature_bytes).decode('utf-8')

    @staticmethod
    def verify(message: object, signature: str, public_key: str) -> bool:
        """
        verfies message with digital signature

        @param message: (object) message to verify
        @param signature: (str) signature to verify message with
        @param public_key: (str) public key to verify message with
        """
        try:
            public_key_bytes = serialization.load_pem_public_key(
                public_key.encode('utf-8'),
                backend=default_backend()
            )
            signature_bytes = Bytes.decode_bytes(signature.encode('utf-8'))
            message_bytes = Bytes.object_to_bytes(message)
            public_key_bytes.verify(
                signature_bytes,
                message_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def encrypt(
            message: object,
            private_key: str,
            receiver_public_key: str) -> str:
        """
        encrypts message

        @param message: (object) message to encrypt
        @param private_key: (str) private key to encrypt message with
        @param receiver_public_key: (str) public key of person able to decrypt message
        """
        iv = '000000000000'.encode('utf-8')
        private_key_bytes = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        receiver_public_key = serialization.load_pem_public_key(
            receiver_public_key.encode('utf-8'),
            backend=default_backend()
        )
        shared_key = private_key_bytes.exchange(ec.ECDH(), receiver_public_key)
        point = private_key_bytes.public_key().public_numbers().encode_point()
        xkdf = x963kdf.X963KDF(
            algorithm=hashes.SHA256(),
            length=32,
            sharedinfo=''.encode('utf-8'),
            backend=default_backend()
        )
        key = xkdf.derive(shared_key)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        padded_message = Crypt._pad_data(json.dumps(message))
        ciphertext = encryptor.update(padded_message) + encryptor.finalize()
        complete_ciphertext = point + encryptor.tag + ciphertext
        return Bytes.encode_bytes(complete_ciphertext).decode('utf-8')

    @staticmethod
    def decrypt(message: str, receiver_private_key: str) -> str:
        """
        decrypts message

        @param message: (str) message to decrypt
        @param receiver_private_key: (str) private key to decrypt with
        """
        message = Bytes.decode_bytes(message.encode('utf-8'))
        point = message[0:65]
        tag = message[65:81]
        ciphertext = message[81:]
        receiver_private_key_bytes = serialization.load_pem_private_key(
            receiver_private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        sender_public_numbers = ec.EllipticCurvePublicNumbers.from_encoded_point(
            ec.SECP256K1(), point)
        sender_public_key = sender_public_numbers.public_key(default_backend())
        shared_key = receiver_private_key_bytes.exchange(
            ec.ECDH(),
            sender_public_key
        )
        iv = '000000000000'.encode('utf-8')
        xkdf = x963kdf.X963KDF(
            algorithm=hashes.SHA256(),
            length=32,
            sharedinfo=''.encode('utf-8'),
            backend=default_backend()
        )
        key = xkdf.derive(shared_key)
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        dt = decryptor.update(ciphertext) + decryptor.finalize()
        return Crypt._unpad_data(dt).decode('utf-8')

    @staticmethod
    def _pad_data(data: str):
        """
        appends padding to the provided data
        """
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(Bytes.str_to_bytes(data))
        padded_data += padder.finalize()
        return padded_data

    @staticmethod
    def _unpad_data(dt):
        """
        removes appended padding from the data
        """
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(dt)
        unpadded = data + unpadder.finalize()
        return unpadded
