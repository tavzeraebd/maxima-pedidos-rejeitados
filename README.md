# 🤖 Pedido Rejeitado v5 - Automação de Token Maxima

Automação de login e extração de token JWT do sistema **Maxima** com Selenium Chrome em modo headless e polling otimizado.

## 📋 Descrição

Este projeto automatiza o processo de renovação de token de autenticação no sistema Maxima, extraindo o JWT armazenado no `localStorage` do navegador durante o login. O token é salvo no arquivo `.env` para uso em integrações API.

**Características:**
- ✅ Login automático no sistema Maxima
- ✅ Extração de token JWT via JavaScript executor
- ✅ Polling otimizado (9-10 segundos de execução)
- ✅ Modo headless (sem interface gráfica)
- ✅ Salvamento automático do token no `.env`
- ✅ Limpeza de token (remove prefixo "Bearer")

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
