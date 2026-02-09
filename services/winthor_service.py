import requests
from typing import List, Dict, Any
from models.pedido_winthor import PedidoWinthor


class WinthorService:
    """Serviço para consultar pedidos importados no Winthor"""

    def __init__(self, base_url: str, auth_token: str, auth_type: str = "Bearer"):
        """
        Inicializa o serviço do Winthor
        
        Args:
            base_url: URL base da API do Winthor
            auth_token: Token de autenticação
            auth_type: Tipo de autenticação ("Bearer" ou "Basic")
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = self._limpar_token(auth_token)
        self.auth_type = auth_type
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
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.auth_type} {self.auth_token}",
        }

    def buscar_pedidos_importados(self) -> List[PedidoWinthor]:
        """
        Busca todos os pedidos do dia que foram importados no Winthor
        
        Returns:
            Lista de PedidoWinthor encontrados
        """
        endpoint = f"{self.base_url}/imported"

        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            
            # Tenta com Bearer primeiro, se falhar com 401, tenta Basic
            if response.status_code == 401 and self.auth_type == "Bearer":
                self.auth_type = "Basic"
                self.headers = self._preparar_headers()
                response = requests.get(endpoint, headers=self.headers, timeout=30)

            response.raise_for_status()
            data_json = response.json()

            # Trata diferentes formatos de resposta
            if isinstance(data_json, list):
                data = data_json
            else:
                data = data_json.get("data", data_json.get("orders", data_json.get("items", [])))

            if not data:
                return []

            return PedidoWinthor.from_list(data)

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar pedidos do Winthor: {e}")
            return []

    def buscar_pedidos_por_filial(self, filial: str) -> List[PedidoWinthor]:
        """
        Busca pedidos importados de uma filial específica
        
        Args:
            filial: Código ou ID da filial
        
        Returns:
            Lista de PedidoWinthor da filial
        """
        endpoint = f"{self.base_url}/imported/filial/{filial}"

        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            data_json = response.json()

            if isinstance(data_json, list):
                data = data_json
            else:
                data = data_json.get("data", [])

            return PedidoWinthor.from_list(data) if data else []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar pedidos da filial {filial}: {e}")
            return []

    def verificar_pedido_existente(self, numero_pedido: str) -> bool:
        """
        Verifica se um pedido específico existe no Winthor
        
        Args:
            numero_pedido: Número do pedido a verificar
        
        Returns:
            True se o pedido existe, False caso contrário
        """
        endpoint = f"{self.base_url}/items/{numero_pedido}"

        try:
            response = requests.head(endpoint, headers=self.headers, timeout=10)
            return response.status_code == 200

        except requests.exceptions.RequestException:
            return False
