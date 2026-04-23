import json


class JsonHandler:
    @staticmethod
    def format_json(input_str: str, indent: int = 2, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
        try:
            parsed = json.loads(input_str)
            return json.dumps(parsed, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式错误: 第 {e.lineno} 行, 第 {e.colno} 列\n{e.msg}")

    @staticmethod
    def minify_json(input_str: str) -> str:
        try:
            parsed = json.loads(input_str)
            return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式错误: {e}")

    @staticmethod
    def validate_json(input_str: str) -> tuple[bool, str]:
        try:
            json.loads(input_str)
            return True, "JSON 格式正确"
        except json.JSONDecodeError as e:
            return False, f"JSON 格式错误: 第 {e.lineno} 行, 第 {e.colno} 列\n{e.msg}"
