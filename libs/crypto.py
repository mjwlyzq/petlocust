import base64
import gzip

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = '2u@H3N*bEJW5pbDa'


class Crypto:

    # 用aes加密，再用base64  encode
    @staticmethod
    def aes_encrypt(data):
        data = data.encode("utf-8") if isinstance(data, str) else data
        b_data = gzip.compress(data)
        cipher = AES.new(AES_KEY.encode('utf-8'), AES.MODE_CBC)
        encrypted = cipher.encrypt(pad(b_data, AES.block_size))  # aes加密
        iv = base64.b64encode(cipher.iv).decode()
        result = base64.b64encode(encrypted).decode()  # base64 encode
        return f'{iv}:{result}'

    # 把加密的数据，用base64  decode，再用aes解密
    @staticmethod
    def aes_decrypt(data):
        if not data:
            pass
        e_items = data.split(":")
        if len(e_items) != 2:
            pass
        c_iv = base64.b64decode(e_items[0])
        result = base64.b64decode(e_items[1])
        cipher = AES.new(AES_KEY.encode('utf-8'), AES.MODE_CBC, c_iv)
        temp_text = unpad(cipher.decrypt(result), AES.block_size)
        text = gzip.decompress(temp_text).decode('utf-8')
        return text


if __name__ == '__main__':
    c = Crypto()
    print(c.aes_decrypt(
        'vSRLGgUQW0we5M0rOMWv2A==:S7hqdFNZ5IXR/aAP+2l258eLej7OcU9ph5y3aaRlgZJBKGrK1iG5myjYi6DLnp2Es+SYiEFJVlip6TwPCL/ID0d4qAAH2W8TlU0tHuFIeUuuXbECZ0nldK4eROSFC2+5UjMCZjUhWM9t71T3Z8MG2Uah6MVE1tCeg7IdGDZXcZBstoaC4bouytPU62ET9KK5ZgN6KYrXXxlFzbaMo+4H+JvctpYwkzjZy8ODOmyax4GLApzW59a8C8h9n37m+ohmLu2KZz91Vh1En3XlRBzPWGJuuscOpVURRfvGwqMtsoHNkqJHs/0/R9wM5HNJafKunxwQpaGf/oxCZtb2ENs//afo+9clTFex5cfj1LO8bF0xYNn9VTsWHSPFGs4YIP5qn2WE6i3YMfs/WzwMlzXoHq91Sm4/TRPKxfzq9sfFkHk='))
