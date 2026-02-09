# 🚀 Guia de Uso Rápido - Reconciliação de Pagamentos

Aprenda a usar os serviços de reconciliação em 5 minutos.

## ⚡ Uso Mínimo (5 linhas)

```python
from services.payment_service import PaymentService
from services.winthor_service import WinthorService
from services.reconciliation_service import ReconciliationService

payment = PaymentService(os.getenv("MAXPAYMENT_API_URL"), os.getenv("MAXIMA_AUTH_TOKEN"))
winthor = WinthorService(os.getenv("WINTHOR_API_URL"), os.getenv("WINTHOR_AUTH_TOKEN"))

pagamentos = payment.buscar_pagamentos_ultimos_dias(dias=0)
pedidos = winthor.buscar_pedidos_importados()

resultado = ReconciliationService.confrontar_pagamentos(pagamentos, pedidos)
print(f"✅ {resultado.total_integrados} | ❌ {resultado.total_rejeitados}")
```

---

## 📚 Exemplos Práticos

### 1️⃣ Buscar Pagamentos de Hoje

```python
from services.payment_service import PaymentService
from models.pagamento import Pagamento

service = PaymentService(url, token)

# Opção A: Buscar pagamentos de hoje
pagamentos = service.buscar_pagamentos_ultimos_dias(dias=0)

# Opção B: Buscar pagamentos de ontem
pagamentos = service.buscar_pagamentos_ultimos_dias(dias=1)

# Opção C: Buscar em período específico
pagamentos = service.buscar_pagamentos_por_periodo(
    data_inicio="2026-02-01T00:00:00.000Z",
    data_fim="2026-02-09T23:59:59.999Z",
    itens_por_pagina=100
)

# Acessar dados
for p in pagamentos:
    print(f"Filial: {p.codigo_filial} | Pedido: {p.codigo_pedido_maxima} | Cliente: {p.nome_cliente}")
```

### 2️⃣ Buscar Pedidos do Winthor

```python
from services.winthor_service import WinthorService

service = WinthorService(url, token)

# Buscar todos os pedidos importados
pedidos = service.buscar_pedidos_importados()

# Buscar pedidos de uma filial específica
pedidos_filial_10 = service.buscar_pedidos_por_filial("10")

# Verificar se um pedido existe
existe = service.verificar_pedido_existente("269230489")
if existe:
    print("✅ Pedido encontrado no Winthor")
else:
    print("❌ Pedido NÃO encontrado no Winthor")

# Acessar dados
for p in pedidos:
    print(f"Pedido: {p.numero_pedido} | Cliente: {p.cliente}")
```

### 3️⃣ Fazer o Confronto (Reconciliação)

```python
from services.reconciliation_service import ReconciliationService

# Dados da etapa anterior
pagamentos = [...]  # Lista de Pagamento
pedidos_winthor = [...]  # Lista de PedidoWinthor

# Realizar confronto
resultado = ReconciliationService.confrontar_pagamentos(pagamentos, pedidos_winthor)

# Ver resumo geral
print(resultado.resumo())
# Processados: 337 | Integrados: 334 ✅ | Rejeitados: 3 ❌ | Taxa: 99.11%

# Acessar detalhes
print(f"Total de pagamentos: {resultado.total_pagamentos}")
print(f"Taxa de integração: {resultado.percentual_integracao}%")

# Ver pedidos rejeitados
for p in resultado.pedidos_rejeitados:
    print(f"❌ {p.numero_pedido}: {p.cliente}")

# Agrupar por filial
agrupado = ReconciliationService.agrupar_por_filial(resultado)
for filial, dados in agrupado.items():
    print(f"Filial {filial}: {dados['integrados']} ✅ | {dados['rejeitados']} ❌")
```

### 4️⃣ Gerar Notificações

```python
from services.notification_service import NotificationService
from datetime import datetime

# Exibir rejeições no console
NotificationService.notificar_rejeitados_console(resultado)

# Salva em JSON
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
NotificationService.salvar_relatorio_json(resultado, f"logs/relatorio_{timestamp}.json")

# Salva em TXT
NotificationService.salvar_relatorio_texto(resultado, f"logs/relatorio_{timestamp}.txt")

# Gerar relatório como texto (sem salvar)
relatorio = NotificationService.gerar_relatorio_texto(resultado)
print(relatorio)

# Enviar por email (opcional)
NotificationService.enviar_email(
    resultado,
    destinatarios=["admin@empresa.com", "gerente@empresa.com"],
    remetente="sistema@empresa.com",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="sua_conta@gmail.com",
    password="sua_senha_app"
)
```

---

## 🎯 Casos de Uso Comuns

### Caso 1: Verificar se um pagamento foi integrado

```python
numero_pedido = "269230489"

# Buscar pagamento
pagamentos = payment_service.buscar_pagamentos_ultimos_dias(dias=0)
pagamento_existe = any(p.codigo_pedido_maxima == numero_pedido for p in pagamentos)

if pagamento_existe:
    print("✅ Pagamento encontrado na MaxPayment")
    
    # Verificar se está no Winthor
    existe_winthor = winthor_service.verificar_pedido_existente(numero_pedido)
    
    if existe_winthor:
        print("✅ Pedido integrado no Winthor")
    else:
        print("❌ Pedido NÃO integrado no Winthor")
else:
    print("❌ Pagamento não encontrado")
```

### Caso 2: Listar todos os pedidos rejeitados de uma filial

```python
filial_alvo = "10"

# Buscar e reconciliar
pagamentos = payment_service.buscar_pagamentos_ultimos_dias(dias=0)
pedidos = winthor_service.buscar_pedidos_importados()
resultado = ReconciliationService.confrontar_pagamentos(pagamentos, pedidos)

# Filtrar por filial
rejeitados_filial = [
    p for p in resultado.pedidos_rejeitados 
    if p.codigo_filial == filial_alvo
]

print(f"Pedidos rejeitados da Filial {filial_alvo}:")
for p in rejeitados_filial:
    print(f"  - {p.numero_pedido}: {p.cliente}")
```

### Caso 3: Relatório por filial

```python
resultado = ReconciliationService.confrontar_pagamentos(pagamentos, pedidos)
agrupado = ReconciliationService.agrupar_por_filial(resultado)

print("\n📊 RELATÓRIO POR FILIAL\n")

for filial in sorted(agrupado.keys()):
    dados = agrupado[filial]
    taxa = (dados["integrados"] / dados["total"] * 100) if dados["total"] > 0 else 0
    
    print(f"Filial {filial}:")
    print(f"  Total: {dados['total']} pagamentos")
    print(f"  Integrados: {dados['integrados']} ✅")
    print(f"  Rejeitados: {dados['rejeitados']} ❌")
    print(f"  Taxa: {taxa:.1f}%")
    
    if dados["pedidos_rejeitados"]:
        print("  Detalhes dos rejeitados:")
        for p in dados["pedidos_rejeitados"]:
            print(f"    • {p['numero']}: {p['cliente'][:50]}")
    print()
```

### Caso 4: Exportar dados em JSON

```python
import json

resultado = ReconciliationService.confrontar_pagamentos(pagamentos, pedidos)

# Salvar resultado em JSON
with open("resultado_reconciliacao.json", "w", encoding="utf-8") as f:
    json.dump(resultado.to_dict(), f, indent=2, ensure_ascii=False)

# Salvar apenas os rejeitados
rejeitados_dict = [p.to_dict() for p in resultado.pedidos_rejeitados]
with open("rejeitados.json", "w", encoding="utf-8") as f:
    json.dump(rejeitados_dict, f, indent=2, ensure_ascii=False)

print(f"✅ Dados exportados! {len(rejeitados_dict)} pedidos rejeitados salvos")
```

---

## 🔍 Propriedades e Métodos Úteis

### Pagamento
```python
p = pagamentos[0]
p.codigo_filial              # "10"
p.nome_filial                # "10 - Empresa Ltda"
p.nome_cliente               # "EMPORIO GERIBA LTDA"
p.codigo_pedido_maxima       # "269230489"
p.valor                      # 1500.50
p.data_pagamento             # "2026-02-09T10:15:30Z"
p.to_dict()                  # Converte para dicionário
```

### PedidoWinthor
```python
p = pedidos_winthor[0]
p.numero_pedido              # "269230489"
p.filial                     # "10"
p.cliente                    # "EMPORIO GERIBA LTDA"
p.data_importacao            # "2026-02-09T10:20:00Z"
p.status                     # "INTEGRADO"
p.to_dict()                  # Converte para dicionário
```

### ResultadoConfrontoPagamentos
```python
r = resultado
r.data_processamento         # Timestamp do processamento
r.total_pagamentos           # Total de pagamentos processados
r.total_integrados           # Total integrado com sucesso
r.total_rejeitados           # Total que falhou
r.percentual_integracao      # Taxa (0-100%)
r.pedidos_rejeitados         # Filtra apenas rejeitados
r.resumo()                   # String com resumo
r.to_dict()                  # Converte para dicionário
```

---

## ⚙️ Configuração Necessária

Adicione ao seu `.env`:

```env
# MaxPayment API
MAXPAYMENT_API_URL=https://maxpayment-api.solucoesmaxima.com.br/relatorio/ConsultarPagamentoPorPeriodo
MAXIMA_AUTH_TOKEN=seu_token_jwt_aqui

# Winthor API
WINTHOR_API_URL=https://api.ebdgrupo.com.br/maxima/v1/pedidos
WINTHOR_AUTH_TOKEN=seu_token_aqui

# (Opcional) Para enviar emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
```

---

## 🛠️ Troubleshooting

### Erro: "Token não configurado"
```python
# Verifique se as variáveis estão no .env
import os
print(os.getenv("MAXIMA_AUTH_TOKEN"))  # Deve imprimir o token
```

### Erro: "Sem resultados"
```python
# Pode ser que não haja pagamentos naquele período
# Teste com datas diferentes
pagamentos = payment_service.buscar_pagamentos_ultimos_dias(dias=7)  # Últimos 7 dias
```

### Erro: "Autenticação falhou no Winthor"
```python
# Tente mudar o tipo de autenticação
service = WinthorService(url, token, auth_type="Basic")  # Era "Bearer"
```

---

## 📖 Exemplo Completo (Production-Ready)

Veja `exemplo_reconciliacao.py` para um exemplo completo com tratamento de erros.

```bash
python exemplo_reconciliacao.py
```

---

## 💡 Dicas

1. **Sempre validar tokens**: Eles podem expirar
2. **Usar try-except**: Os serviços podem falhar por rede
3. **Log tudo**: Use os arquivos de log para auditoria
4. **Agendar tarefas**: Use cron ou APScheduler para execução automática
5. **Monitorar**: Crie alertas para taxa de integração < 95%

