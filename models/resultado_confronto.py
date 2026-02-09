from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class ResultadoConfrontoPedido:
    """Resultado do confronto de um pedido individual"""
    codigo_filial: str
    numero_pedido: str
    cliente: str
    status: str  # "INTEGRADO" ou "REJEITADO"
    detalhes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "codigo_filial": self.codigo_filial,
            "numero_pedido": self.numero_pedido,
            "cliente": self.cliente,
            "status": self.status,
            "detalhes": self.detalhes,
        }


@dataclass
class ResultadoConfrontoPagamentos:
    """Resultado completo do confronto de pagamentos"""
    data_processamento: str
    total_pagamentos: int
    total_integrados: int
    total_rejeitados: int
    pedidos: List[ResultadoConfrontoPedido] = field(default_factory=list)

    @property
    def percentual_integracao(self) -> float:
        """Percentual de pedidos integrados"""
        if self.total_pagamentos == 0:
            return 0.0
        return round((self.total_integrados / self.total_pagamentos) * 100, 2)

    @property
    def pedidos_rejeitados(self) -> List[ResultadoConfrontoPedido]:
        """Filtra apenas os pedidos rejeitados"""
        return [p for p in self.pedidos if p.status == "REJEITADO"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_processamento": self.data_processamento,
            "total_pagamentos": self.total_pagamentos,
            "total_integrados": self.total_integrados,
            "total_rejeitados": self.total_rejeitados,
            "percentual_integracao": self.percentual_integracao,
            "pedidos": [p.to_dict() for p in self.pedidos],
        }

    def resumo(self) -> str:
        """Gera um resumo textual dos resultados"""
        return (
            f"Processados: {self.total_pagamentos} | "
            f"Integrados: {self.total_integrados} ✅ | "
            f"Rejeitados: {self.total_rejeitados} ❌ | "
            f"Taxa: {self.percentual_integracao}%"
        )
