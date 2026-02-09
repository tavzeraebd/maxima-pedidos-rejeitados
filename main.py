import time
from services.browser_service import BrowserService
from models.token_model import TokenModel
from utils.logger import log  # Importando nosso novo utilitário

def run_automation():
    start_time = time.time()
    log.info("Iniciando processo de renovação de Token...")

    try:
        # Instancia o serviço
        browser = BrowserService()
        
        log.info("Abrindo navegador em modo silencioso (Headless)...")
        raw_token = browser.perform_login()

        if raw_token:
            final_token = TokenModel.save_token(raw_token)
            elapsed = time.time() - start_time
            log.info(f"✅ Sucesso! Token atualizado no .env em {elapsed:.2f}s")
        else:
            log.error("❌ Falha crítica: O token não foi interceptado no navegador.")

    except Exception as e:
        log.error(f"💥 Erro inesperado na execução: {str(e)}")

if __name__ == "__main__":
    run_automation()