import os
import requests
from datetime import datetime, timedelta
from typing import List, Optional
from models.pagamento import Pagamento


class PaymentService:
    """Serviço para consultar pagamentos processados na MaxPayment API"""

    def __init__(self, base_url: str, auth_token: str):
        """
        Inicializa o serviço de pagamentos
        
        Args:
            base_url: URL base da API MaxPayment
            auth_token: Token de autenticação Bearer
        """
        self.base_url = base_url
        self.auth_token = self._limpar_token(auth_token)
        self.headers = self._preparar_headers()

    @staticmethod
    def _limpar_token(token: str) -> str:
        """Remove prefixos e símbolos desnecessários do token"""
        if not token:
            return ""
        return token.strip().replace("'", "").replace('"', '').replace("Bearer ", "")

    def _preparar_headers(self) -> dict:
        """Prepara headers padrão para requisições"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

    def buscar_pagamentos_por_periodo(
        self,
        data_inicio: str,
        data_fim: str,
        pagina: int = 1,
        itens_por_pagina: int = 10,
        filiais: str = "",
        gateways: str = "3",
        status_pagamentos: str = "5",
    ) -> List[Pagamento]:
        """
        Busca pagamentos processados em um período específico
        
        Args:
            data_inicio: Data inicial no formato ISO (2026-02-09T03:00:00.000Z)
            data_fim: Data final no formato ISO (2026-02-09T03:00:00.000Z)
            pagina: Número da página (padrão: 1)
            itens_por_pagina: Itens por página (padrão: 10)
            filiais: IDs das filiais a filtrar (vazio = todas)
            gateways: ID do gateway (padrão: 3 para cartão de crédito)
            status_pagamentos: Status dos pagamentos (padrão: 5)
        
        Returns:
            Lista de objetos Pagamento
        """
        params = {
            "Pagina": str(pagina),
            "ItensPorPagina": str(itens_por_pagina),
            "CampoOrdem": "dtIncluido",
            "TipoOrdemAsc": "false",
            "dataInicio": data_inicio,
            "dataFim": data_fim,
            "filialId": "0",
            "statusPagamento": "0",
            "ambiente": "1",
            "nomeCliente": "",
            "tokenId": "0",
            "adquirente": "0",
            "paginar": "true",
            "filiais": filiais,
            "gateways": gateways,
            "statusPagamentos": status_pagamentos,
            "filtroAvancado": ""
        }

        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json().get("data", [])
            return [Pagamento.from_dict(item) for item in data]

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar pagamentos: {e}")
            return []

    def buscar_pagamentos_ultimos_dias(
        self,
        dias: int = 0,
        **kwargs
    ) -> List[Pagamento]:
        """
        Busca pagamentos dos últimos N dias
        
        Args:
            dias: Número de dias para trás (0 = hoje, 1 = ontem, etc)
            **kwargs: Argumentos adicionais para buscar_pagamentos_por_periodo
        
        Returns:
            Lista de pagamentos
        """
        agora = datetime.utcnow()
        data_alvo = agora - timedelta(days=dias)
        
        # Formata para ISO 8601 com UTC (Z = Zulu = UTC)
        data_inicio = data_alvo.strftime("%Y-%m-%dT00:00:00.000Z")
        data_fim = data_alvo.strftime("%Y-%m-%dT23:59:59.999Z")

        return self.buscar_pagamentos_por_periodo(
            data_inicio=data_inicio,
            data_fim=data_fim,
            **kwargs
        )
