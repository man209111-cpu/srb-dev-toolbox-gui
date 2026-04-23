import base64
import binascii
from urllib.parse import quote, unquote
from typing import Set


class Base64Handler:
    @staticmethod
    def encode(data: str, encoding: str = 'utf-8', url_safe: bool = False) -> str:
        try:
            bytes_data = data.encode(encoding)
            if url_safe:
                encoded = base64.urlsafe_b64encode(bytes_data)
            else:
                encoded = base64.b64encode(bytes_data)
            return encoded.decode('ascii')
        except UnicodeEncodeError as e:
            raise ValueError(f"编码错误: {e}")

    @staticmethod
    def decode(data: str, encoding: str = 'utf-8', url_safe: bool = False) -> str:
        try:
            if url_safe:
                decoded = base64.urlsafe_b64decode(data)
            else:
                decoded = base64.b64decode(data)
            return decoded.decode(encoding)
        except binascii.Error as e:
            raise ValueError(f"Base64 解码错误: 输入不是有效的 Base64 字符串\n{e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"解码后无法使用 {encoding} 编码解析: {e}")


class UrlHandler:
    _ALWAYS_SAFE: Set[int] = set(
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        b'abcdefghijklmnopqrstuvwxyz'
        b'0123456789'
        b'_.-~'
    )

    @staticmethod
    def _fast_url_encode(data: str, safe: str = '', encoding: str = 'utf-8') -> str:
        safe_bytes = set(safe.encode('ascii'))
        always_safe = UrlHandler._ALWAYS_SAFE | safe_bytes
        
        bytes_data = data.encode(encoding)
        result = []
        result_append = result.append
        
        for byte in bytes_data:
            if byte in always_safe:
                result_append(chr(byte))
            else:
                result_append(f'%{byte:02X}')
        
        return ''.join(result)

    @staticmethod
    def encode(data: str, encoding: str = 'utf-8', safe: str = '') -> str:
        try:
            data_size = len(data)
            if data_size > 100000:
                return UrlHandler._fast_url_encode(data, safe, encoding)
            return quote(data, safe=safe, encoding=encoding)
        except Exception as e:
            raise ValueError(f"URL 编码错误: {e}")

    @staticmethod
    def decode(data: str, encoding: str = 'utf-8') -> str:
        try:
            return unquote(data, encoding=encoding)
        except Exception as e:
            raise ValueError(f"URL 解码错误: {e}")
