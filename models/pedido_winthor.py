from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class PedidoWinthor:
    """Modelo representando um pedido importado no Winthor"""
    numero_pedido: str
    filial: Optional[str] = None
    cliente: Optional[str] = None
    data_importacao: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PedidoWinthor":
        """Constrói um PedidoWinthor a partir da resposta da API"""
        # Tries múltiplas chaves possíveis para o número do pedido
        numero = (
            data.get("numpedrca") or 
            data.get("NUMPEDRCA") or 
            data.get("numPedido") or
            data.get("codigoPedidoMaxima") or
            ""
        )
        
        return cls(
            numero_pedido=str(numero).strip(),
            filial=data.get("filial") or data.get("nomeFilial"),
            cliente=data.get("cliente") or data.get("nomeCliente"),
            data_importacao=data.get("dataImportacao") or data.get("dtIncluido"),
            status=data.get("status") or data.get("statusPedido"),
        )

    @classmethod
    def from_list(cls, data_list: List[Dict[str, Any]]) -> List["PedidoWinthor"]:
        """Constrói uma lista de PedidoWinthor a partir de uma lista de dicionários"""
        return [cls.from_dict(item) for item in data_list]

    def to_dict(self) -> Dict[str, Any]:
        """Converte o PedidoWinthor para dicionário"""
        return {
            "numero_pedido": self.numero_pedido,
            "filial": self.filial,
            "cliente": self.cliente,
            "data_importacao": self.data_importacao,
            "status": self.status,
        }
