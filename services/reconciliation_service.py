from datetime import datetime
from typing import List, Tuple
from models.pagamento import Pagamento
from models.pedido_winthor import PedidoWinthor
from models.resultado_confronto import ResultadoConfrontoPagamentos, ResultadoConfrontoPedido


class ReconciliationService:
    """Serviço para reconciliar (confrontar) pagamentos com pedidos do Winthor"""

    @staticmethod
    def confrontar_pagamentos(
        pagamentos: List[Pagamento],
        pedidos_winthor: List[PedidoWinthor]
    ) -> ResultadoConfrontoPagamentos:
        """
        Realiza o confronto entre pagamentos processados e pedidos importados no Winthor.
        Identifica quais pagamentos não foram encontrados no Winthor.
        
        Args:
            pagamentos: Lista de pagamentos processados
            pedidos_winthor: Lista de pedidos importados no Winthor
        
        Returns:
            ResultadoConfrontoPagamentos com os resultados
        """
        # Mapeia números de pedidos do Winthor para acesso rápido
        numeros_winthor = {p.numero_pedido.strip() for p in pedidos_winthor}

        resultado = ResultadoConfrontoPagamentos(
            data_processamento=datetime.now().isoformat(),
            total_pagamentos=len(pagamentos),
            total_integrados=0,
            total_rejeitados=0,
        )

        # Processa cada pagamento
        for pagamento in pagamentos:
            numero_pedido = str(pagamento.codigo_pedido_maxima).strip()

            # Verifica se o pedido foi encontrado no Winthor
            if numero_pedido in numeros_winthor:
                status = "INTEGRADO"
                resultado.total_integrados += 1
            else:
                status = "REJEITADO"
                resultado.total_rejeitados += 1

            # Cria resultado individual
            confronto_item = ResultadoConfrontoPedido(
                codigo_filial=pagamento.codigo_filial,
                numero_pedido=numero_pedido,
                cliente=pagamento.nome_cliente,
                status=status,
                detalhes={
                    "nome_filial": pagamento.nome_filial,
                    "valor": pagamento.valor,
                    "gateway": pagamento.gateway,
                    "data_pagamento": pagamento.data_pagamento,
                }
            )

            resultado.pedidos.append(confronto_item)

        return resultado

    @staticmethod
    def obter_pendentes_winthor(
        pagamentos: List[Pagamento],
        pedidos_winthor: List[PedidoWinthor]
    ) -> Tuple[List[Pagamento], List[PedidoWinthor]]:
        """
        Identifica quais pagamentos não foram integrados (não estão no Winthor).
        
        Args:
            pagamentos: Lista de pagamentos
            pedidos_winthor: Lista de pedidos no Winthor
        
        Returns:
            Tupla com (pagamentos_pendentes, todos_os_pedidos_winthor)
        """
        numeros_winthor = {p.numero_pedido.strip() for p in pedidos_winthor}
        pendentes = [
            p for p in pagamentos
            if str(p.codigo_pedido_maxima).strip() not in numeros_winthor
        ]

        return pendentes, pedidos_winthor

    @staticmethod
    def agrupar_por_filial(
        resultado: ResultadoConfrontoPagamentos
    ) -> dict:
        """
        Agrupa os resultados do confronto por filial
        
        Args:
            resultado: Resultado do confronto
        
        Returns:
            Dicionário com resultados agrupados por filial
        """
        agrupado = {}

        for pedido in resultado.pedidos:
            filial = pedido.codigo_filial

            if filial not in agrupado:
                agrupado[filial] = {
                    "total": 0,
                    "integrados": 0,
                    "rejeitados": 0,
                    "pedidos_rejeitados": []
                }

            agrupado[filial]["total"] += 1

            if pedido.status == "INTEGRADO":
                agrupado[filial]["integrados"] += 1
            else:
                agrupado[filial]["rejeitados"] += 1
                agrupado[filial]["pedidos_rejeitados"].append({
                    "numero": pedido.numero_pedido,
                    "cliente": pedido.cliente,
                })

        return agrupado
