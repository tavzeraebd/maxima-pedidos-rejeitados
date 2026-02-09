import json
from typing import List, Optional
from datetime import datetime
from models.pagamento import Pagamento
from models.resultado_confronto import ResultadoConfrontoPagamentos


class NotificationService:
    """Serviço para notificar sobre pedidos rejeitados e problemas de integração"""

    @staticmethod
    def notificar_rejeitados_console(resultado: ResultadoConfrontoPagamentos) -> None:
        """
        Exibe no console os pedidos rejeitados (não encontrados no Winthor)
        
        Args:
            resultado: Resultado do confronto
        """
        rejeitados = resultado.pedidos_rejeitados

        if not rejeitados:
            print("\n✅ Nenhum pedido rejeitado encontrado!")
            return

        print(f"\n❌ PEDIDOS REJEITADOS - {resultado.data_processamento}")
        print("=" * 80)
        print(f"{'FILIAL':<8} | {'PEDIDO':<15} | {'CLIENTE':<30}")
        print("-" * 80)

        for pedido in rejeitados:
            cliente_truncado = pedido.cliente[:30] if pedido.cliente else "N/A"
            print(
                f"{pedido.codigo_filial:<8} | "
                f"{pedido.numero_pedido:<15} | "
                f"{cliente_truncado:<30}"
            )

        print("-" * 80)
        print(f"Total de rejeitados: {len(rejeitados)}")

    @staticmethod
    def salvar_relatorio_json(
        resultado: ResultadoConfrontoPagamentos,
        caminho_arquivo: str
    ) -> bool:
        """
        Salva o resultado do confronto em um arquivo JSON
        
        Args:
            resultado: Resultado do confronto
            caminho_arquivo: Caminho para salvar o arquivo
        
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            dados = resultado.to_dict()

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)

            print(f"\n📄 Relatório salvo em: {caminho_arquivo}")
            return True

        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")
            return False

    @staticmethod
    def gerar_relatorio_texto(
        resultado: ResultadoConfrontoPagamentos
    ) -> str:
        """
        Gera um relatório em formato texto
        
        Args:
            resultado: Resultado do confronto
        
        Returns:
            String contendo o relatório formatado
        """
        linhas = []
        linhas.append("=" * 80)
        linhas.append(f"RELATÓRIO DE CONFRONTO DE PAGAMENTOS")
        linhas.append(f"Data: {resultado.data_processamento}")
        linhas.append("=" * 80)
        linhas.append("")

        # Resumo geral
        linhas.append("RESUMO GERAL:")
        linhas.append(f"  Total de pagamentos: {resultado.total_pagamentos}")
        linhas.append(f"  Integrados: {resultado.total_integrados} ✅")
        linhas.append(f"  Rejeitados: {resultado.total_rejeitados} ❌")
        linhas.append(f"  Taxa de integração: {resultado.percentual_integracao}%")
        linhas.append("")

        # Detalhes dos rejeitados
        if resultado.pedidos_rejeitados:
            linhas.append("PEDIDOS REJEITADOS (NÃO ENCONTRADOS NO WINTHOR):")
            linhas.append("-" * 80)
            linhas.append(f"{'FILIAL':<8} | {'PEDIDO':<15} | {'CLIENTE':<40}")
            linhas.append("-" * 80)

            for pedido in resultado.pedidos_rejeitados:
                cliente = (pedido.cliente or "N/A")[:40]
                linhas.append(
                    f"{pedido.codigo_filial:<8} | "
                    f"{pedido.numero_pedido:<15} | "
                    f"{cliente:<40}"
                )

            linhas.append("-" * 80)

        linhas.append("")
        linhas.append("=" * 80)

        return "\n".join(linhas)

    @staticmethod
    def salvar_relatorio_texto(
        resultado: ResultadoConfrontoPagamentos,
        caminho_arquivo: str
    ) -> bool:
        """
        Salva o relatório em formato texto
        
        Args:
            resultado: Resultado do confronto
            caminho_arquivo: Caminho para salvar o arquivo
        
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            relatorio = NotificationService.gerar_relatorio_texto(resultado)

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(relatorio)

            print(f"\n📄 Relatório salvo em: {caminho_arquivo}")
            return True

        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")
            return False

    @staticmethod
    def enviar_email(
        resultado: ResultadoConfrontoPagamentos,
        destinatarios: List[str],
        remetente: str,
        **kwargs
    ) -> bool:
        """
        Envia notificação por email (placeholder - implementar com SMTP)
        
        Args:
            resultado: Resultado do confronto
            destinatarios: Lista de emails para enviar
            remetente: Email do remetente
            **kwargs: Argumentos adicionais (smtp_host, smtp_port, etc)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Construir email
            assunto = f"Relatório de Confronto de Pagamentos - {resultado.data_processamento}"
            corpo = NotificationService.gerar_relatorio_texto(resultado)

            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

            # Configurações padrão (podem ser sobrescrito por kwargs)
            smtp_host = kwargs.get('smtp_host', 'smtp.gmail.com')
            smtp_port = kwargs.get('smtp_port', 587)
            username = kwargs.get('username')
            password = kwargs.get('password')

            # Enviar email
            if not username or not password:
                print("⚠️ Credenciais SMTP não fornecidas. Email não enviado.")
                return False

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            print(f"\n📧 Email enviado para: {', '.join(destinatarios)}")
            return True

        except Exception as e:
            print(f"\n❌ Erro ao enviar email: {e}")
            return False
