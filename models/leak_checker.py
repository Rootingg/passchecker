import hashlib
import requests

class LeakChecker:
    def __init__(self):
        self.api_url = "https://api.pwnedpasswords.com/range/"
    
    def check_password(self, password):
        """Vérifie si un mot de passe est compromis en utilisant l'API HaveIBeenPwned"""
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        hash_prefix = password_hash[:5]
        hash_suffix = password_hash[5:]
        
        try:
            response = requests.get(self.api_url + hash_prefix)
            if response.status_code == 200:
                return self._check_response(response.text, hash_suffix)
            return False
        except:
            return False
    
    def _check_response(self, response_text, hash_suffix):
        """Vérifie si le suffixe du hash est dans la réponse"""
        hash_list = (line.split(':') for line in response_text.splitlines())
        for h, count in hash_list:
            if h == hash_suffix:
                return True
        return False