"""
🤖 Pedido Rejeitado v5 - Sistema de Reconciliação de Pagamentos
Entry point principal da aplicação

Uso:
    python main.py                      # Executa reconciliação completa
    python main.py --token              # Apenas renova o token
    python main.py --help               # Mostra ajuda
"""

import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from services.browser_service import BrowserService
from services.payment_service import PaymentService
from services.winthor_service import WinthorService
from services.reconciliation_service import ReconciliationService
from services.notification_service import NotificationService
from models.token_model import TokenModel
from utils.logger import log


def renovar_token():
    """Renova o token de autenticação MaxPayment"""
    print("\n" + "=" * 80)
    print("🔐 RENOVAÇÃO DE TOKEN")
    print("=" * 80)

    start_time = time.time()
    log.info("Iniciando processo de renovação de Token...")

    try:
        browser = BrowserService()
        log.info("Abrindo navegador em modo silencioso (Headless)...")
        
        raw_token = browser.perform_login()

        if raw_token:
            final_token = TokenModel.save_token(raw_token)
            elapsed = time.time() - start_time
            log.info(f"✅ Sucesso! Token atualizado no .env em {elapsed:.2f}s")
            print(f"\n✅ Token renovado com sucesso em {elapsed:.2f}s\n")
            return True
        else:
            log.error("❌ Falha crítica: O token não foi interceptado no navegador.")
            print("\n❌ Falha ao extrair token do navegador\n")
            return False

    except Exception as e:
        log.error(f"💥 Erro inesperado na execução: {str(e)}")
        print(f"\n❌ Erro: {str(e)}\n")
        return False


def reconciliar_pagamentos():
    """Executa a reconciliação completa de pagamentos"""
    print("\n" + "=" * 80)
    print("📊 RECONCILIAÇÃO DE PAGAMENTOS")
    print("=" * 80 + "\n")

    # Recarregar variáveis de ambiente
    load_dotenv(override=True)

    # Validar configurações
    maxpayment_url = os.getenv("MAXPAYMENT_API_URL")
    maxima_token = os.getenv("MAXIMA_AUTH_TOKEN")
    winthor_url = os.getenv("WINTHOR_API_URL")
    winthor_token = os.getenv("WINTHOR_AUTH_TOKEN")

    if not all([maxpayment_url, maxima_token, winthor_url, winthor_token]):
        print("❌ ERRO: Variáveis de ambiente não configuradas!")
        print("\nVariáveis necessárias:")
        print("  ✗ MAXPAYMENT_API_URL" if not maxpayment_url else "  ✓ MAXPAYMENT_API_URL")
        print("  ✗ MAXIMA_AUTH_TOKEN" if not maxima_token else "  ✓ MAXIMA_AUTH_TOKEN")
        print("  ✗ WINTHOR_API_URL" if not winthor_url else "  ✓ WINTHOR_API_URL")
        print("  ✗ WINTHOR_AUTH_TOKEN" if not winthor_token else "  ✓ WINTHOR_AUTH_TOKEN")
        print("\nConfigure estas variáveis no arquivo .env\n")
        return False

    try:
        # ========== 1. BUSCAR PAGAMENTOS ==========
        print("📥 Etapa 1: Buscando pagamentos na MaxPayment...")
        payment_service = PaymentService(maxpayment_url, maxima_token)
        pagamentos = payment_service.buscar_pagamentos_ultimos_dias(
            dias=0,
            itens_por_pagina=100,
            gateways="3"  # Cartão de crédito
        )
        print(f"   ✓ {len(pagamentos)} pagamentos encontrados\n")

        if not pagamentos:
            print("⚠️  Nenhum pagamento encontrado para o período.\n")
            return True

        # ========== 2. BUSCAR PEDIDOS WINTHOR ==========
        print("📥 Etapa 2: Buscando pedidos importados no Winthor...")
        winthor_service = WinthorService(winthor_url, winthor_token)
        pedidos_winthor = winthor_service.buscar_pedidos_importados()
        print(f"   ✓ {len(pedidos_winthor)} pedidos encontrados no Winthor\n")

        # ========== 3. RECONCILIAÇÃO ==========
        print("🔄 Etapa 3: Reconciliando pagamentos...")
        resultado = ReconciliationService.confrontar_pagamentos(
            pagamentos=pagamentos,
            pedidos_winthor=pedidos_winthor
        )
        print(f"   ✓ Reconciliação concluída\n")

        # ========== 4. EXIBIR RESULTADO ==========
        print("=" * 80)
        print(f"📊 RESULTADO: {resultado.resumo()}")
        print("=" * 80 + "\n")

        # Exibir rejeitados se houver
        if resultado.pedidos_rejeitados:
            NotificationService.notificar_rejeitados_console(resultado)

        # ========== 5. SALVAR RELATÓRIOS ==========
        print("💾 Gerando relatórios...\n")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        arquivo_json = f"logs/relatorio_confronto_{timestamp}.json"
        NotificationService.salvar_relatorio_json(resultado, arquivo_json)
        
        arquivo_txt = f"logs/relatorio_confronto_{timestamp}.txt"
        NotificationService.salvar_relatorio_texto(resultado, arquivo_txt)

        # ========== 6. RESUMO POR FILIAL ==========
        print("\n📋 Resumo por filial:\n")

        agrupado = ReconciliationService.agrupar_por_filial(resultado)

        for filial in sorted(agrupado.keys()):
            dados = agrupado[filial]
            taxa = (dados["integrados"] / dados["total"] * 100) if dados["total"] > 0 else 0
            
            print(f"  Filial {filial}: {dados['total']} total | "
                  f"{dados['integrados']} ✅ | {dados['rejeitados']} ❌ | {taxa:.1f}%")

            if dados["pedidos_rejeitados"] and len(dados["pedidos_rejeitados"]) <= 5:
                for p in dados["pedidos_rejeitados"]:
                    print(f"     └─ {p['numero']}: {p['cliente'][:40]}")

        print("\n" + "=" * 80)
        print("✅ Processo concluído com sucesso!")
        print("=" * 80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Erro durante reconciliação: {str(e)}\n")
        log.error(f"Erro: {str(e)}")
        return False


def main():
    """Função principal com argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description="Sistema de Reconciliação de Pagamentos - Pedido Rejeitado v5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py              # Executa reconciliação completa
  python main.py --token      # Apenas renova o token
  python main.py --help       # Mostra esta mensagem
        """
    )

    parser.add_argument(
        "--token",
        action="store_true",
        help="Apenas renova o token de autenticação"
    )

    args = parser.parse_args()

    # Carregar variáveis de ambiente
    load_dotenv()

    print("\n" + "=" * 80)
    print("🤖 PEDIDO REJEITADO v5 - Sistema de Reconciliação de Pagamentos")
    print(f"   Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)

    try:
        if args.token:
            # Apenas renova o token
            sucesso = renovar_token()
            sys.exit(0 if sucesso else 1)
        else:
            # Executa o workflow completo
            sucesso = reconciliar_pagamentos()
            sys.exit(0 if sucesso else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {str(e)}\n")
        log.error(f"Erro fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()