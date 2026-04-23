import secrets
import string
from typing import Optional


class PasswordGenerator:
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    CONFUSING = '0O1lI'

    def __init__(self):
        pass

    @staticmethod
    def generate(
        length: int,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_confusing: bool = False,
        custom_chars: Optional[str] = None
    ) -> str:
        if length < 1:
            raise ValueError("密码长度必须至少为 1")
        
        if length > 1024:
            raise ValueError("密码长度不能超过 1024")

        if custom_chars:
            charset = custom_chars
        else:
            charset = ''
            if use_uppercase:
                charset += PasswordGenerator.UPPERCASE
            if use_lowercase:
                charset += PasswordGenerator.LOWERCASE
            if use_digits:
                charset += PasswordGenerator.DIGITS
            if use_special:
                charset += PasswordGenerator.SPECIAL
            
            if exclude_confusing:
                for char in PasswordGenerator.CONFUSING:
                    charset = charset.replace(char, '')
        
        if not charset:
            raise ValueError("至少需要选择一种字符类型")

        password = ''.join(secrets.choice(charset) for _ in range(length))
        
        return password

    @staticmethod
    def check_strength(password: str) -> tuple[int, str]:
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("密码长度应至少为 8 位")
        
        if len(password) >= 12:
            score += 1
        
        if len(password) >= 16:
            score += 1
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("建议包含大写字母")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("建议包含小写字母")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("建议包含数字")
        
        if any(not c.isalnum() for c in password):
            score += 1
        else:
            feedback.append("建议包含特殊字符")
        
        if score <= 3:
            strength = "弱"
        elif score <= 5:
            strength = "中等"
        elif score <= 7:
            strength = "强"
        else:
            strength = "非常强"
        
        feedback_str = "\n".join(feedback) if feedback else "密码强度良好"
        
        return score, f"强度: {strength} ({score}/8)\n\n{feedback_str}"
