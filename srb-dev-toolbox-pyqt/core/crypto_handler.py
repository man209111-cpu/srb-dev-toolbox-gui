import hashlib
from typing import Optional


class HashHandler:
    SUPPORTED_ALGORITHMS = {
        'MD5': hashlib.md5,
        'SHA-1': hashlib.sha1,
        'SHA-224': hashlib.sha224,
        'SHA-256': hashlib.sha256,
        'SHA-384': hashlib.sha384,
        'SHA-512': hashlib.sha512,
        'SHA3-224': hashlib.sha3_224,
        'SHA3-256': hashlib.sha3_256,
        'SHA3-384': hashlib.sha3_384,
        'SHA3-512': hashlib.sha3_512,
    }

    @staticmethod
    def generate_hash(data: str, algorithm: str, encoding: str = 'utf-8', uppercase: bool = False) -> str:
        if algorithm not in HashHandler.SUPPORTED_ALGORITHMS:
            raise ValueError(f"不支持的哈希算法: {algorithm}\n支持的算法: {', '.join(HashHandler.SUPPORTED_ALGORITHMS.keys())}")
        
        try:
            hash_func = HashHandler.SUPPORTED_ALGORITHMS[algorithm]
            bytes_data = data.encode(encoding)
            hash_obj = hash_func(bytes_data)
            result = hash_obj.hexdigest()
            return result.upper() if uppercase else result
        except UnicodeEncodeError as e:
            raise ValueError(f"编码错误: {e}")

    @staticmethod
    def get_supported_algorithms() -> list[str]:
        return list(HashHandler.SUPPORTED_ALGORITHMS.keys())
