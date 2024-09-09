from cryptography.fernet import Fernet


def initialize_cipher(key):
    return Fernet(key)


def encrypt_password(cipher, password):
    return cipher.encrypt(password.encode())


def decrypt_password(cipher, encrypted_password):
    if not isinstance(encrypted_password, bytes) or not isinstance(
            encrypted_password, str
    ):
        encrypted_password = encrypted_password.tobytes()
    return cipher.decrypt(encrypted_password).decode()
