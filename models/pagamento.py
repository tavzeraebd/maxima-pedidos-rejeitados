from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Pagamento:
    """Modelo representando um pagamento processado na Maxima"""
    codigo_filial: str          # "10" (extraído de "10 - Empresa")
    nome_filial: str            # "10 - Empresa Ltda"
    nome_cliente: str           # "EMPORIO GERIBA LTDA"
    codigo_pedido_maxima: str   # Código do pedido na Maxima
    data_pagamento: Optional[str] = None
    valor: Optional[float] = None
    gateway: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pagamento":
        """Constrói um Pagamento a partir do dicionário da API Maxima"""
        nome_filial = data.get("nomeFilial", "")
        
        # Extrai os 2 primeiros dígitos do nome da filial (ex: "10 - Empresa" -> "10")
        codigo_filial = nome_filial.split("-")[0].strip() if nome_filial else "00"
        
        # Extrai o código do pedido (pode estar em diferentes locais na resposta)
        pedido_data = data.get("pedido", {})
        codigo_pedido = pedido_data.get("codigoPedidoMaxima", data.get("codigoPedidoMaxima", ""))
        
        return cls(
            codigo_filial=codigo_filial,
            nome_filial=nome_filial,
            nome_cliente=data.get("nomeCliente", ""),
            codigo_pedido_maxima=str(codigo_pedido),
            data_pagamento=data.get("dtIncluido"),
            valor=data.get("valor"),
            gateway=data.get("nomeGateway"),
            status=data.get("statusPagamento"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o Pagamento para dicionário"""
        return {
            "codigo_filial": self.codigo_filial,
            "nome_filial": self.nome_filial,
            "nome_cliente": self.nome_cliente,
            "codigo_pedido_maxima": self.codigo_pedido_maxima,
            "data_pagamento": self.data_pagamento,
            "valor": self.valor,
            "gateway": self.gateway,
            "status": self.status,
        }
