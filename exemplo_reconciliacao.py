"""
Exemplo de uso dos serviços de reconciliação de pagamentos
Demonstra como buscar pagamentos, pedidos do Winthor e confrontá-los
"""
import os
from datetime import datetime
from dotenv import load_dotenv

from services.payment_service import PaymentService
from services.winthor_service import WinthorService
from services.reconciliation_service import ReconciliationService
from services.notification_service import NotificationService

# Carrega variáveis de ambiente
load_dotenv()


def main():
    """Executa o workflow completo de reconciliação"""

    print("\n🚀 Iniciando processo de reconciliação de pagamentos...\n")

    # ========== CONFIGURAÇÃO ==========
    # Credenciais da MaxPayment (Pagamentos)
    maxpayment_url = os.getenv("MAXPAYMENT_API_URL")
    maxima_token = os.getenv("MAXIMA_AUTH_TOKEN")

    # Credenciais do Winthor
    winthor_url = os.getenv("WINTHOR_API_URL")
    winthor_token = os.getenv("WINTHOR_AUTH_TOKEN")

    # Validação de variáveis de ambiente
    if not all([maxpayment_url, maxima_token, winthor_url, winthor_token]):
        print("❌ ERRO: Variáveis de ambiente não configuradas corretamente!")
        print("Verifique: MAXPAYMENT_API_URL, MAXIMA_AUTH_TOKEN, WINTHOR_API_URL, WINTHOR_AUTH_TOKEN")
        return

    # ========== INICIALIZAÇÃO DE SERVIÇOS ==========
    payment_service = PaymentService(maxpayment_url, maxima_token)
    winthor_service = WinthorService(winthor_url, winthor_token)

    # ========== BUSCA DE DADOS ==========
    print("📥 Buscando dados...\n")

    # Busca pagamentos dos últimos 0 dias (hoje)
    print("  ▶ Consultando pagamentos na MaxPayment...")
    pagamentos = payment_service.buscar_pagamentos_ultimos_dias(
        dias=0,
        itens_por_pagina=50,
        gateways="3"  # Cartão de crédito
    )
    print(f"  ✅ {len(pagamentos)} pagamentos encontrados\n")

    if not pagamentos:
        print("⚠️ Nenhum pagamento encontrado. Abortando.")
        return

    # Busca pedidos importados no Winthor
    print("  ▶ Consultando pedidos importados no Winthor...")
    pedidos_winthor = winthor_service.buscar_pedidos_importados()
    print(f"  ✅ {len(pedidos_winthor)} pedidos encontrados no Winthor\n")

    # ========== RECONCILIAÇÃO ==========
    print("🔄 Realizando reconciliação (confronto)...\n")

    resultado = ReconciliationService.confrontar_pagamentos(
        pagamentos=pagamentos,
        pedidos_winthor=pedidos_winthor
    )

    # ========== EXIBIÇÃO DE RESULTADOS ==========
    print(f"\n📊 RESULTADO: {resultado.resumo()}\n")

    # Exibe os rejeitados
    if resultado.pedidos_rejeitados:
        NotificationService.notificar_rejeitados_console(resultado)

    # ========== RELATÓRIOS ==========
    print("\n📄 Gerando relatórios...\n")

    # Salva relatório JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_json = f"logs/relatorio_confronto_{timestamp}.json"
    NotificationService.salvar_relatorio_json(resultado, arquivo_json)

    # Salva relatório em texto
    arquivo_txt = f"logs/relatorio_confronto_{timestamp}.txt"
    NotificationService.salvar_relatorio_texto(resultado, arquivo_txt)

    # ========== AGRUPAMENTO POR FILIAL ==========
    print("\n📋 Resumo por filial:\n")

    agrupado = ReconciliationService.agrupar_por_filial(resultado)

    for filial, dados in sorted(agrupado.items()):
        taxa = (dados["integrados"] / dados["total"] * 100) if dados["total"] > 0 else 0
        print(f"\nFilial {filial}:")
        print(f"  Total: {dados['total']} | "
              f"Integrados: {dados['integrados']} ✅ | "
              f"Rejeitados: {dados['rejeitados']} ❌ | "
              f"Taxa: {taxa:.1f}%")

        if dados["pedidos_rejeitados"]:
            print("  Pedidos rejeitados:")
            for p in dados["pedidos_rejeitados"]:
                print(f"    - {p['numero']}: {p['cliente'][:40]}")

    print("\n" + "=" * 80)
    print("✅ Processo de reconciliação concluído com sucesso!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
