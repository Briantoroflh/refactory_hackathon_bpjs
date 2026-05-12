"""
Token encryption and decryption utilities for secure credential storage.
"""

import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
import base64
import os

logger = logging.getLogger(__name__)


class TokenEncryption:
    """
    Utility class for encrypting and decrypting sensitive tokens.
    Uses Fernet (symmetric encryption) for secure storage.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption helper.

        Args:
            encryption_key: Base64-encoded encryption key. If not provided,
                          will try to load from TOKEN_ENCRYPTION_KEY env var.
        """
        if encryption_key is None:
            encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY", "")

        if not encryption_key:
            logger.warning(
                "TOKEN_ENCRYPTION_KEY not set. Tokens will be stored in plaintext. "
                "Set TOKEN_ENCRYPTION_KEY in .env for production."
            )
            self.cipher = None
        else:
            try:
                self.cipher = Fernet(encryption_key.encode())
            except Exception as e:
                logger.error(f"Failed to initialize encryption cipher: {str(e)}")
                self.cipher = None

    @staticmethod
    def generate_encryption_key() -> str:
        """
        Generate a new Fernet encryption key suitable for TOKEN_ENCRYPTION_KEY.

        Returns:
            Base64-encoded encryption key
        """
        key = Fernet.generate_key()
        return key.decode()

    def encrypt(self, token: str) -> str:
        """
        Encrypt a token string.

        Args:
            token: The token to encrypt

        Returns:
            Encrypted token (base64-encoded), or plaintext if encryption not configured
        """
        if not self.cipher:
            logger.debug("Encryption not configured; returning plaintext token")
            return token

        try:
            encrypted = self.cipher.encrypt(token.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Token encryption failed: {str(e)}")
            # Fail-open: return plaintext if encryption fails
            return token

    def decrypt(self, encrypted_token: str) -> str:
        """
        Decrypt a token string.

        Args:
            encrypted_token: The encrypted token to decrypt

        Returns:
            Decrypted token, or plaintext if decryption fails/not configured
        """
        if not self.cipher:
            logger.debug("Encryption not configured; returning as-is")
            return encrypted_token

        try:
            decrypted = self.cipher.decrypt(encrypted_token.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {str(e)}")
            # Return as-is if decryption fails (may already be plaintext)
            return encrypted_token


def get_encryption_helper() -> TokenEncryption:
    """
    Get a global encryption helper instance.

    Returns:
        TokenEncryption instance
    """
    return TokenEncryption()
