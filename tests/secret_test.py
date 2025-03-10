import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from secret import encrypt,decrypt

password = "myp@ssw0rd"
plaintext = '{"key":"value"}'

# 加密
encrypted_text = encrypt(password, plaintext)
print("加密后:", encrypted_text)

encrypted_text += "wechat_get"
# 解密
decrypted_text = decrypt(password, encrypted_text)
print("解密后:", decrypted_text)
