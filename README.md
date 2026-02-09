# 🤖 Pedido Rejeitado v5 - Sistema de Reconciliação de Pagamentos

Sistema completo de automação que recupera pagamentos processados via cartão de crédito, busca pedidos importados no Winthor e identifica quais pagamentos **não foram integrados** (rejeitados).

## ✨ Características Principais

✅ **Busca automática de pagamentos** - Extrai dados da API MaxPayment  
✅ **Consulta de pedidos Winthor** - Verifica quais pedidos foram importados  
✅ **Reconciliação inteligente** - Confronta e identifica discrepâncias  
✅ **Notificações detalhadas** - Relatórios em console, JSON e TXT  
✅ **Renovação de token automática** - Integra login via Selenium Chrome headless  
✅ **Agrupamento por filial** - Análise de performance por unidade  

## 📊 Fluxo de Execução

```
┌─────────────────────────────┐
│  python main.py             │  ← Executa reconciliação completa
│  python main.py --token     │  ← Apenas renova token
└─────────────────────────────┘
                ↓
        ┌───────────────────┐
        │  1. Renovar Token │
        │   (se necessário) │
        └─────────┬─────────┘
                  ↓
    ┌─────────────────────────────┐
    │ 2. Buscar Pagamentos MaxPay │
    │    (Cartão de Crédito)      │
    └──────────────┬──────────────┘
                   ↓
    ┌──────────────────────────────┐
    │ 3. Buscar Pedidos Winthor    │
    │    (Importados do dia)       │
    └──────────────┬───────────────┘
                   ↓
    ┌──────────────────────────────┐
    │ 4. Reconciliação             │
    │    (Confronto de pedidos)    │
    └──────────────┬───────────────┘
                   ↓
    ┌──────────────────────────────┐
    │ 5. Gerar Relatórios          │
    │    (JSON, TXT, Console)      │
    └──────────────────────────────┘
```

## 🚀 Início Rápido

### 1. Pré-requisitos

- Python 3.8+
- Google Chrome instalado
- Conexão com internet

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/pedido-rejeitado-v5.git
cd pedido-rejeitado-v5

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 3. Configuração

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```env
# MaxPayment API
MAXPAYMENT_API_URL=https://maxpayment-api.solucoesmaxima.com.br/relatorio/ConsultarPagamentoPorPeriodo
MAXIMA_AUTH_TOKEN=seu_token_jwt_aqui

# Winthor API
WINTHOR_API_URL=https://api.ebdgrupo.com.br/maxima/v1/pedidos
WINTHOR_AUTH_TOKEN=seu_token_aqui

# Credenciais Maxima (para renovação automática de token)
MAXIMA_URL=https://app.solucoesmaxima.com.br/
USUARIO_LOGIN=seu_usuario
SENHA_LOGIN=sua_senha

# XPath (não alterar se a interface não mudar)
XPATH_USER=//*[@id="mat-input-0"]
XPATH_PASS=//*[@id="mat-input-1"]
```

### 4. Execução

**Reconciliação completa:**
```bash
python main.py
```

**Apenas renovar token:**
```bash
python main.py --token
```

**Ver ajuda:**
```bash
python main.py --help
```

## 📁 Estrutura do Projeto

```
pedido-rejeitado-v5/
├── main.py                          # 🎯 Entry point principal
├── config.py                        # Configurações (token automation)
├── requirements.txt                 # Dependências do projeto
├── .env.example                     # Template de configuração
│
├── models/                          # 📦 Modelos de dados
│   ├── pagamento.py                # Pagamento (MaxPayment)
│   ├── pedido_winthor.py           # PedidoWinthor
│   ├── resultado_confronto.py      # ResultadoConfrontoPagamentos
│   └── token_model.py              # TokenModel
│
├── services/                        # 🔧 Serviços de negócio
│   ├── payment_service.py          # Busca pagamentos
│   ├── winthor_service.py          # Busca pedidos Winthor
│   ├── reconciliation_service.py   # Confronta (reconcilia)
│   ├── notification_service.py     # Gera relatórios
│   └── browser_service.py          # Automação de login
│
├── utils/                           # 🛠️ Utilitários
│   └── logger.py                   # Sistema de logs
│
├── logs/                            # 📋 Saída de relatórios
│   └── relatorio_confronto_*.json/txt
│
├── docs/                            # 📚 Documentação
│   ├── README.md                   # Este arquivo
│   ├── ARCHITECTURE.md             # Detalhes da arquitetura
│   └── QUICK_START.md              # Exemplos de uso
│
└── LICENSE                          # MIT License
```

## 🎯 Arquitetura

### 1. **PaymentService** - Busca Pagamentos
Consulta a API MaxPayment para recuperar pagamentos via cartão de crédito.

```python
from services.payment_service import PaymentService

service = PaymentService(url, token)
pagamentos = service.buscar_pagamentos_ultimos_dias(dias=0)
```

### 2. **WinthorService** - Busca Pedidos
Consulta a API Winthor para recuperar pedidos importados.

```python
from services.winthor_service import WinthorService

service = WinthorService(url, token)
pedidos = service.buscar_pedidos_importados()
```

### 3. **ReconciliationService** - Confronta
Compara pagamentos com pedidos e identifica rejeitados.

```python
from services.reconciliation_service import ReconciliationService

resultado = ReconciliationService.confrontar_pagamentos(
    pagamentos=pagamentos,
    pedidos_winthor=pedidos
)

print(resultado.resumo())
# Processados: 337 | Integrados: 334 ✅ | Rejeitados: 3 ❌ | Taxa: 99.11%
```

### 4. **NotificationService** - Relatórios
Gera notificações e salva relatórios em múltiplos formatos.

```python
from services.notification_service import NotificationService

# Console
NotificationService.notificar_rejeitados_console(resultado)

# JSON
NotificationService.salvar_relatorio_json(resultado, "relatorio.json")

# Texto
NotificationService.salvar_relatorio_texto(resultado, "relatorio.txt")
```

## 📊 Output Esperado

### Console
```
================================================================================
🤖 PEDIDO REJEITADO v5 - Sistema de Reconciliação de Pagamentos
   Iniciado em: 09/02/2026 10:30:45
================================================================================

📥 Etapa 1: Buscando pagamentos na MaxPayment...
   ✓ 337 pagamentos encontrados

📥 Etapa 2: Buscando pedidos importados no Winthor...
   ✓ 334 pedidos encontrados no Winthor

🔄 Etapa 3: Reconciliando pagamentos...
   ✓ Reconciliação concluída

================================================================================
📊 RESULTADO: Processados: 337 | Integrados: 334 ✅ | Rejeitados: 3 ❌ | Taxa: 99.11%
================================================================================

❌ PEDIDOS REJEITADOS - 2026-02-09T10:30:45.123456
================================================================================
FILIAL    | PEDIDO          | CLIENTE
----------|-----------------|------------------------------
10        | 269230489       | EMPORIO GERIBA LTDA
15        | 269230490       | LOJA ONLINE LTDA
10        | 269230491       | DISTRIBUIDORA CENTRAL
----------|-----------------|------------------------------
Total de rejeitados: 3

💾 Gerando relatórios...

✅ Processo concluído com sucesso!
================================================================================
```

### JSON (`logs/relatorio_confronto_*.json`)
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
      "status": "REJEITADO"
    }
  ]
}
```

## 🔐 Segurança

⚠️ **Importante:**

1. **Nunca commitar `.env`** com credenciais reais
2. **Use `.env.example`** como template
3. **Configurados em `.gitignore`**:
   - `.env` (credenciais)
   - `logs/` (relatórios com dados sensíveis)
   - `__pycache__/` (Python cache)

## 📝 Documentação Completa

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detalhes técnicos da arquitetura
- **[QUICK_START.md](QUICK_START.md)** - Exemplos práticos de uso

## 🛠️ Troubleshooting

### "Token não configurado"
```bash
# Renove o token automaticamente
python main.py --token
```

### "Sem resultados"
- Verifique se há pagamentos naquele período
- Teste com `dias=7` para última semana

### "Erro de autenticação"
- Valide tokens no `.env`
- Teste manualmente as APIs

## 📦 Dependências

```
selenium>=4.0.0
python-dotenv>=0.21.0
webdriver-manager>=3.8.0
requests>=2.28.0
```

## 📧 Contato & Suporte

Para dúvidas, crie uma issue no GitHub.

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

**Versão:** 5.0.0  
**Última atualização:** Fevereiro de 2026  
**Status:** ✅ Production Ready

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.8+
- Google Chrome instalado
- ChromeDriver (baixado automaticamente via webdriver-manager)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/pedido-rejeitado-v5.git
cd pedido-rejeitado-v5
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env` com suas credenciais:
```bash
cp .env.example .env
```

5. Edite o `.env` com suas informações:
```env
MAXIMA_URL=https://app.solucoesmaxima.com.br/
MAXIMA_USER=seu_usuario
MAXIMA_PASS=sua_senha
XPATH_USER=//*[@id="mat-input-0"]
XPATH_PASS=//*[@id="mat-input-1"]
MAXIMA_TOKEN=
```

### Uso

Execute a automação:
```bash
python main.py
```

**Output esperado:**
```
Iniciando processo de renovação de Token...
Abrindo navegador em modo silencioso (Headless)...
✅ Sucesso! Token atualizado no .env em 9.24s
```

O token será salvo automaticamente em `.env` na variável `MAXIMA_TOKEN`.

## 📁 Estrutura do Projeto

```
pedido-rejeitado-v5/
├── main.py                      # Entry point da aplicação
├── config.py                    # Configurações do projeto
├── .env                         # Variáveis de ambiente
├── .env.example                 # Template do .env
├── requirements.txt             # Dependências Python
├── models/
│   ├── __init__.py
│   └── token_model.py          # Modelo de Token (persistência)
├── services/
│   ├── __init__.py
│   └── browser_service.py      # Serviço de navegador (Selenium)
├── utils/
│   ├── __init__.py
│   └── logger.py               # Utilitários de logging
├── logs/                        # Logs da aplicação
└── README.md                    # Este arquivo
```

## 🔧 Componentes Principais

### `main.py`
Entry point da aplicação. Orquestra o workflow de automação.

### `services/browser_service.py`
Gerencia o navegador Chrome:
- Configuração de opções (headless, gpu, sandbox)
- Login automático via XPath
- Polling de localStorage para extração do token
- Cleanup de recursos

```python
class BrowserService:
    def perform_login(self) -> str
        """Realiza login e extrai token JWT do localStorage"""
```

### `models/token_model.py`
Modela e persiste o token:
- Limpeza de prefixos ("Bearer ")
- Salva no `.env` via `dotenv.set_key()`

```python
class TokenModel:
    @staticmethod
    def save_token(raw_token: str) -> str
        """Limpa e salva token no .env"""
```

### `utils/logger.py`
Logger centralizado para toda a aplicação.

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `MAXIMA_URL` | URL do sistema Maxima | `https://app.solucoesmaxima.com.br/` |
| `MAXIMA_USER` | Usuário para login | `seu_usuario` |
| `MAXIMA_PASS` | Senha para login | `sua_senha` |
| `XPATH_USER` | XPath do campo de usuário | `//*[@id="mat-input-0"]` |
| `XPATH_PASS` | XPath do campo de senha | `//*[@id="mat-input-1"]` |
| `MAXIMA_TOKEN` | Token JWT (gerado automaticamente) | `eyJhbGciOi...` |

### Polling Otimizado

O projeto utiliza polling otimizado com estratégia eficiente:
- **Intervalo**: 0.5 segundos
- **Máximo de tentativas**: 20 (total ~10 segundos)
- **Execução**: JavaScript via `execute_script()` (não bloqueia o navegador)

```python
for _ in range(20):
    token = self.driver.execute_script("""
        return Object.keys(localStorage)
            .filter(k => k.toLowerCase().includes('token'))
            .map(k => localStorage.getItem(k))[0];
    """)
    if token: return token
    time.sleep(0.5)
```

### Otimizações de Performance

1. **Chrome headless**: Executa sem interface gráfica
2. **Page load strategy eager**: Não espera recursos externos
3. **Bloqueio de imagens**: Desabilita carregamento de imagens (reduz I/O)
4. **No sandbox**: Para ambientes containerizados

## 📊 Logs e Output

Os logs são salvos em `logs/` com formato estruturado.

**Níveis de log:**
- `INFO`: Operações normais (login, extração)
- `ERROR`: Falhas críticas (token não encontrado)

**Exemplo de log:**
```
2026-02-09 10:30:45 [INFO] Iniciando processo de renovação de Token...
2026-02-09 10:30:45 [INFO] Abrindo navegador em modo silencioso (Headless)...
2026-02-09 10:30:54 [INFO] ✅ Sucesso! Token atualizado no .env em 9.24s
```

## 🐛 Troubleshooting

### "Token não foi interceptado no navegador"
- Verifique se os XPath estão corretos: inspecione o HTML da página
- Confirme que o usuário/senha estão corretos
- Teste se a página está carregando normalmente

### "ChromeDriver version mismatch"
```bash
pip install --upgrade chromedriver-binary
```

### "Elemento não encontrado (XPath)"
- Abra a página do Maxima no navegador
- Clique com botão direito → Inspecionar no campo de login
- Copie o XPath atualizado

### Timeout em login
- Verifique sua conexão de internet
- Aumente o timeout em `browser_service.py`:
```python
wait = WebDriverWait(self.driver, 20)  # aumentar de 10 para 20 segundos
```

## 📦 Dependências

```
selenium>=4.0.0
python-dotenv>=0.21.0
webdriver-manager>=3.8.0
```

Instale com:
```bash
pip install -r requirements.txt
```

## 🔐 Segurança

⚠️ **Importantes:**
- Nunca commitar o arquivo `.env` com credenciais reais no repositório
- Use um `.gitignore` para proteger arquivos sensíveis:
```
.env
.env.local
*.log
```
- Considere usar secrets manager em ambiente de produção

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo `LICENSE` para detalhes.

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no GitHub.

---

**Versão:** 5.0.0  
**Última atualização:** Fevereiro de 2026  
**Autor:** Hudson
