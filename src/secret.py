# src/secret.py

import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes = None) -> tuple:
    """ 通过 PBKDF2 生成 256-bit (32 字节) AES 密钥和 16 字节 IV """
    if salt is None:
        salt = os.urandom(16)  # 生成随机盐值
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32 + 16,  # 32 字节密钥 + 16 字节 IV
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key_iv = kdf.derive(password.encode())  # 派生密钥和 IV
    return key_iv[:32], key_iv[32:], salt  # 返回 (密钥, IV, 盐值)

def encrypt(password: str, plaintext: str) -> str:
    """ 使用 AES-CBC 进行加密，返回 base64 编码的密文（包含盐值和 IV）"""
    key, iv, salt = derive_key(password)

    # PKCS7 填充
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    # AES 加密
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # 组合盐值、IV 和密文，并进行 base64 编码
    encrypted_data = base64.b64encode(salt + iv + ciphertext).decode()
    return encrypted_data

def decrypt(password: str, encrypted_data: str) -> str:
    """ 使用 AES-CBC 进行解密，返回原始明文 """
    raw_data = base64.b64decode(encrypted_data)

    # 提取盐值、IV 和密文
    salt, iv, ciphertext = raw_data[:16], raw_data[16:32], raw_data[32:]
    key, _, _ = derive_key(password, salt)

    # AES 解密
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # 移除填充
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext.decode()
