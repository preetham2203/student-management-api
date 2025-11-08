# student_api/utils/encryption.py
import base64

class SimplePasswordEncryption:
    def __init__(self):
        self.base_key = "django-insecure-5e*fh41jh246!lj$vai%k+ceqops"
    
    def encrypt_password(self, password, mobile_no):
        """Simple XOR-based encryption with mobile number as salt"""
        # Combine password with mobile number
        combined = f"{password}|{mobile_no}"
        
        # Simple XOR encryption
        key = self.base_key
        encrypted_chars = []
        
        for i, char in enumerate(combined):
            key_char = key[i % len(key)]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            encrypted_chars.append(encrypted_char)
        
        encrypted = ''.join(encrypted_chars)
        
        # Encode to base64 for safe storage
        encoded = base64.b64encode(encrypted.encode()).decode()
        return encoded
    
    def decrypt_password(self, encrypted_password, mobile_no):
        """Decrypt password and verify mobile number"""
        try:
            # Decode from base64
            decoded = base64.b64decode(encrypted_password.encode()).decode()
            
            # Simple XOR decryption
            key = self.base_key
            decrypted_chars = []
            
            for i, char in enumerate(decoded):
                key_char = key[i % len(key)]
                decrypted_char = chr(ord(char) ^ ord(key_char))
                decrypted_chars.append(decrypted_char)
            
            decrypted = ''.join(decrypted_chars)
            
            # Split and verify mobile number
            password, original_mobile = decrypted.split('|')
            
            if original_mobile != mobile_no:
                return None
                
            return password
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return None