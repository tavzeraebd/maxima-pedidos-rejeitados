from dotenv import set_key
from config import Config

class TokenModel:
    @staticmethod
    def save_token(raw_token):
        # Limpeza do token
        clean_token = raw_token.replace("Bearer ", "").replace("bearer ", "").strip()
        # Persistência - salva como MAXIMA_AUTH_TOKEN (variável correta)
        set_key(Config.ENV_PATH, "MAXIMA_AUTH_TOKEN", clean_token)
        return clean_token