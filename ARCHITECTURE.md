# 🏗️ Arquitetura de Serviços - Reconciliação de Pagamentos

Documento explicando a estrutura de serviços para reconciliação de pagamentos entre MaxPayment e Winthor.

## 📋 Fluxo Geral

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. BUSCAR DADOS                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MaxPayment ──────────────┐                                    │
│  (Pagamentos via cartão)  │                                    │
│                           ├──> [PaymentService]               │
│                           │    - buscar_pagamentos_por_periodo│
│                           │    - buscar_pagamentos_ultimos_dias│
│                           │                                    │
│  Winthor ─────────────────┤                                    │
│  (Pedidos importados)     │    [WinthorService]               │
│                           ├──> - buscar_pedidos_importados    │
│                           │    - buscar_pedidos_por_filial    │
│                           │    - verificar_pedido_existente    │
│                                                                 │
│ Resultado: Lista[Pagamento], Lista[PedidoWinthor]              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. RECONCILIAÇÃO (CONFRONTO)                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Compara números de pedidos:                                   │
│  - Pagamentos que ESTÃO no Winthor ──> INTEGRADO ✅            │
│  - Pagamentos que NÃO ESTÃO no Winthor ──> REJEITADO ❌        │
│                                                                  │
│  [ReconciliationService]                                       │
│  - confrontar_pagamentos()       → ResultadoConfrontoPagamentos│
│  - obter_pendentes_winthor()     → Pagamentos não integrados   │
│  - agrupar_por_filial()          → Dados agrupados por filial  │
│                                                                  │
│ Resultado: ResultadoConfrontoPagamentos                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. NOTIFICAÇÕES E RELATÓRIOS                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [NotificationService]                                         │
│  - notificar_rejeitados_console() → Exibe no console           │
│  - gerar_relatorio_texto()        → Texto formatado            │
│  - salvar_relatorio_json()        → Arquivo JSON               │
│  - salvar_relatorio_texto()       → Arquivo TXT                │
│  - enviar_email()                 → Notificação por email      │
│                                                                  │
│ Resultado: Relatórios e notificações                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Estrutura de Arquivos

```
services/
├── payment_service.py              # Busca pagamentos da MaxPayment
├── winthor_service.py              # Busca pedidos do Winthor
├── reconciliation_service.py       # Confronta pagamentos com pedidos
├── notification_service.py         # Notifica e gera relatórios
└── browser_service.py              # Automação de login (existente)

models/
├── pagamento.py                    # Modelo de Pagamento
├── pedido_winthor.py               # Modelo de PedidoWinthor
└── resultado_confronto.py          # Modelos de resultado

logs/
├── relatorio_confronto_YYYYMMDD_HHMMSS.json
└── relatorio_confronto_YYYYMMDD_HHMMSS.txt
```

## 💡 Detalhes dos Componentes

### 1. **PaymentService** (`services/payment_service.py`)

Recupera pagamentos processados na API MaxPayment.

**Métodos principais:**
```python
# Busca pagamentos em um período específico
pagamentos = payment_service.buscar_pagamentos_por_periodo(
    data_inicio="2026-02-09T00:00:00.000Z",
    data_fim="2026-02-09T23:59:59.999Z",
    gateways="3"  # Cartão de crédito
)

# Atalho: busca dos últimos N dias
pagamentos = payment_service.buscar_pagamentos_ultimos_dias(dias=0)
```

**Retorna:** `List[Pagamento]`

**Modelo Pagamento:**
```python
@dataclass
class Pagamento:
    codigo_filial: str              # "10" (2 dígitos)
    nome_filial: str                # "10 - Empresa Ltda"
    nome_cliente: str               # "EMPORIO GERIBA LTDA"
    codigo_pedido_maxima: str       # "269230489"
    data_pagamento: Optional[str]
    valor: Optional[float]
    gateway: Optional[str]
    status: Optional[str]
```

---

### 2. **WinthorService** (`services/winthor_service.py`)

Consulta pedidos importados no Winthor.

**Métodos principais:**
```python
# Busca todos os pedidos importados
pedidos = winthor_service.buscar_pedidos_importados()

# Busca pedidos de uma filial específica
pedidos = winthor_service.buscar_pedidos_por_filial("10")

# Verifica se um pedido existe
existe = winthor_service.verificar_pedido_existente("269230489")
```

**Retorna:** `List[PedidoWinthor]`

**Modelo PedidoWinthor:**
```python
@dataclass
class PedidoWinthor:
    numero_pedido: str              # "269230489"
    filial: Optional[str]           # "10"
    cliente: Optional[str]          # "EMPORIO GERIBA LTDA"
    data_importacao: Optional[str]
    status: Optional[str]
```

---

### 3. **ReconciliationService** (`services/reconciliation_service.py`)

Confronta pagamentos com pedidos do Winthor.

**Métodos principais:**
```python
# Realiza o confronto completo
resultado = ReconciliationService.confrontar_pagamentos(
    pagamentos=pagamentos,
    pedidos_winthor=pedidos_winthor
)

# Obtém apenas os pendentes
pendentes, all_winthor = ReconciliationService.obter_pendentes_winthor(
    pagamentos,
    pedidos_winthor
)

# Agrupa resultados por filial
agrupado = ReconciliationService.agrupar_por_filial(resultado)
```

**Retorna:** `ResultadoConfrontoPagamentos`

**Modelo de Resultado:**
```python
@dataclass
class ResultadoConfrontoPagamentos:
    data_processamento: str         # ISO datetime
    total_pagamentos: int           # Total processado
    total_integrados: int           # Status INTEGRADO ✅
    total_rejeitados: int           # Status REJEITADO ❌
    pedidos: List[ResultadoConfrontoPedido]
    
    # Propriedades úteis:
    percentual_integracao: float    # Taxa de sucesso (0-100%)
    pedidos_rejeitados: List[...]   # Filtra apenas rejeitados
    resumo(): str                   # String formatada com resumo
```

---

### 4. **NotificationService** (`services/notification_service.py`)

Gera notificações e relatórios.

**Métodos principais:**
```python
# Exibe rejeitados no console
NotificationService.notificar_rejeitados_console(resultado)

# Gera relatório formatado em texto
texto = NotificationService.gerar_relatorio_texto(resultado)

# Salva em JSON
NotificationService.salvar_relatorio_json(resultado, "logs/relatorio.json")

# Salva em TXT
NotificationService.salvar_relatorio_texto(resultado, "logs/relatorio.txt")

# Envia por email
NotificationService.enviar_email(
    resultado,
    destinatarios=["admin@empresa.com"],
    remetente="sistema@empresa.com",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="seu_email@gmail.com",
    password="sua_senha_app"
)
```

---

## 🔄 Fluxo de Uso Completo

```python
from services.payment_service import PaymentService
from services.winthor_service import WinthorService
from services.reconciliation_service import ReconciliationService
from services.notification_service import NotificationService

# 1️⃣ Inicializar serviços
payment = PaymentService(url, token)
winthor = WinthorService(url, token)

# 2️⃣ Buscar dados
pagamentos = payment.buscar_pagamentos_ultimos_dias(dias=0)
pedidos_winthor = winthor.buscar_pedidos_importados()

# 3️⃣ Reconciliar
resultado = ReconciliationService.confrontar_pagamentos(
    pagamentos, pedidos_winthor
)

# 4️⃣ Notificar
NotificationService.notificar_rejeitados_console(resultado)
NotificationService.salvar_relatorio_json(resultado, "relatorio.json")
NotificationService.salvar_relatorio_texto(resultado, "relatorio.txt")
```

---

## 📊 Exemplo de Saída

### Console
```
✅ PEDIDOS INTEGRADOS:
================================
Filial 10: 245 pagamentos integrados ✅
Filial 15: 89 pagamentos integrados ✅
Total: 334 ✅

❌ PEDIDOS REJEITADOS:
================================
FILIAL    | PEDIDO          | CLIENTE
---------|-----------------|------------------------------
10       | 269230489       | EMPORIO GERIBA LTDA
15       | 269230490       | LOJA ONLINE LTDA
10       | 269230491       | DISTRIBUIDORA CENTRAL

Total de rejeitados: 3
```

### JSON
```json
{
  "data_processamento": "2026-02-09T10:30:45.123456",
  "total_pagamentos": 337,
  "total_integrados": 334,
  "total_rejeitados": 3,
  "percentual_integracao": 99.11,
  "pedidos": [
    {
      "codigo_filial": "10",
      "numero_pedido": "269230489",
      "cliente": "EMPORIO GERIBA LTDA",
      "status": "REJEITADO",
      "detalhes": {
        "nome_filial": "10 - Empresa",
        "valor": 1500.00,
        "gateway": "Cartão Crédito",
        "data_pagamento": "2026-02-09T10:15:30Z"
      }
    }
  ]
}
```

---

## 🔐 Configuração de Ambiente

Adicione ao seu `.env`:

```env
# MaxPayment (Pagamentos)
MAXPAYMENT_API_URL=https://maxpayment-api.solucoesmaxima.com.br/relatorio/ConsultarPagamentoPorPeriodo
MAXIMA_AUTH_TOKEN=seu_token_aqui

# Winthor (Pedidos)
WINTHOR_API_URL=https://api.ebdgrupo.com.br/maxima/v1/pedidos
WINTHOR_AUTH_TOKEN=seu_token_aqui
```

---

## 📝 Notas Importantes

1. **Tokens**: Ambos os serviços limpam automaticamente prefixos ("Bearer ", aspas, espaços)
2. **Timeout**: Padrão é 30 segundos para requisições
3. **Tratamento de erros**: Todos retornam listas vazias em caso de erro
4. **Formato de data**: ISO 8601 UTC (ex: "2026-02-09T03:00:00.000Z")
5. **Agrupamento**: Por padrão agrupa por código de filial (2 primeiros dígitos)

---

## 🚀 Próximas Melhorias

- [ ] Webhook para notificação em tempo real
- [ ] Dashboard com gráficos de integrações
- [ ] Retry automático com exponential backoff
- [ ] Cache de resultados
- [ ] Agendamento automático (cron jobs)
- [ ] Integração com Slack/Discord
