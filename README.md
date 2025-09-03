## 🎯 **Visão Geral**

O File Indexer é uma aplicação Python que permite indexar arquivos em pastas de rede, oferecendo funcionalidades de busca rápida e estatísticas detalhadas. A versão atual está sendo completamente reestruturada.

## 🏗️ **Arquitetura**

Este projeto implementa **Clean Architecture** com 4 camadas bem definidas:

```
src/
├── domain/           # 🏛️ Regras de negócio puras
│   ├── entities/     # FileItem, FolderItem, IndexStats
│   ├── value_objects/# FilePath, FileSize, SearchCriteria
│   ├── services/     # FileProcessor, SearchEngine, StatisticsCalculator
│   ├── enums/        # ScanMode, SearchType
│   └── exceptions/   # Domain-specific exceptions
├── application/      # 🎯 Casos de uso e orquestração
│   ├── use_cases/    # ScanFilesStreaming, SearchFiles, GetStatistics
│   ├── interfaces/   # Ports (FileRepository, Logger, etc.)
│   └── dtos/         # ScanRequest, SearchRequest, SearchResult
├── infrastructure/  # 🏗️ Detalhes técnicos
│   ├── database/     # SQLite implementation
│   ├── file_system/  # OS file system access
│   ├── logging/      # Console/File logging
│   └── progress/     # TQDM progress reporting
└── presentation/    # 🖥️ Interface CLI
    ├── cli/          # Controllers, Views, Formatters
    └── config/       # Dependency Injection
```

## 🚀 **Funcionalidades**

### ✅ **Core Features**
- **🚀 Escaneamento Streaming** - Baixo uso de memória para grandes volumes
- **🔍 Busca por Nome** - Com suporte a busca exata e parcial
- **📁 Busca por Extensão** - Filtros por tipo de arquivo
- **📈 Estatísticas** - Métricas completas do índice
- **🗑️ Limpeza de Índice** - Remoção segura de dados
- **📊 Progress Reporting** - Barras de progresso em tempo real

### ✅ **Arquiteturais**
- **🏛️ Clean Architecture** - 4 camadas bem definidas
- **🎯 Use Cases** - Casos de uso bem definidos
- **🔒 Value Objects** - Validação e encapsulamento
- **📝 Structured Logging** - Sistema de logs

## 📋 **Pré-requisitos**

- **Python 3.8+**
- **SQLite3** (incluído no Python)
- **TQDM** (para barras de progresso)

## 🛠️ **Instalação**

### 1. **Clone o repositório**
```bash
git clone <repository-url>
cd file-indexer
```

### 2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

### 3. **Execute a aplicação**
```bash
python main.py
```

## 📖 **Como Usar**

### **Interface CLI**
Após executar `python main.py`, você verá o menu principal:

```
==================================================
File Indexer - Clean Architecture v2.0.0
==================================================
1. 🚀 Escanear pasta (Streaming)
2. 🔍 Buscar arquivo por nome
3. 📁 Buscar por extensão
4. 📈 Mostrar estatísticas
5. 🗑️ Limpar índice
6. ❌ Sair
==================================================
Escolha uma opção (1-6):
```

### **Exemplos de Uso**

#### **1. Escanear uma pasta**
```
Escolha uma opção (1-6): 1
Digite o caminho da pasta para escanear: /caminho/para/pasta
```

#### **2. Buscar arquivos**
```
Escolha uma opção (1-6): 2
Digite o nome do arquivo (ou parte dele): documento
```

#### **3. Buscar por extensão**
```
Escolha uma opção (1-6): 3
Digite a extensão (ex: .pdf, .txt): .pdf
```

## 🔄 **Fluxo de Execução Completo**

### **🎯 Exemplo: Verificação de Atualizações**

Este exemplo mostra como uma única ação do usuário percorre **todas as camadas** da Clean Architecture:

#### **1. Camada de Apresentação (Presentation)**
```python
# src/presentation/cli/handlers/check_updates_handler.py
class CheckUpdatesHandler(BaseHandler):
    def handle(self):
        print("Verificando atualizações...")

        # 🏗️ Chama o container DI
        use_case = self.container.get_check_updates_use_case()
        result = use_case.execute()

        # 📊 Exibe resultado para usuário
        self._display_update_results(result)
```

#### **2. Camada de Aplicação (Application)**
```python
# src/application/use_cases/updates/check_updates.py
class CheckUpdatesUseCase:
    def __init__(self, updater: Updater, logger: Logger):
        self.updater = updater  # ← Interface injetada
        self.logger = logger

    def execute(self):
        # 🎯 ORQUESTRAÇÃO: Coordena serviços
        update_info = self.updater.check_for_updates()

        if update_info['update_available']:
            return {
                'status': 'update_available',
                'current_version': update_info['current_version'],
                'latest_version': update_info['latest_version']
            }
```

#### **3. Camada de Domínio (Domain)**
```python
# src/application/interfaces/services/updater.py
class Updater(ABC):
    @abstractmethod
    def check_for_updates(self) -> Dict[str, any]:
        """Contrato: deve verificar atualizações"""
        pass  # ← Interface abstrata
```

#### **4. Camada de Infraestrutura (Infrastructure)**
```python
# src/infrastructure/updates/github_updater.py
class GitHubUpdater(Updater):  # ← Implementa interface
    def check_for_updates(self):
        # 🏗️ IMPLEMENTAÇÃO REAL
        response = requests.get(
            f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        )

        if response.status_code == 200:
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')

            return {
                'update_available': self._is_newer_version(latest_version, self.current_version),
                'current_version': self.current_version,
                'latest_version': latest_version,
                'release_notes': release_data.get('body', ''),
                'download_url': release_data.get('html_url', '')
            }
```

#### **5. Injeção de Dependências (Dependency Injection)**
```python
# src/presentation/config/dependency_injection.py
def _configure_infrastructure(self):
    # 🏗️ Cria implementação concreta
    self._services['updater'] = GitHubUpdater(
        repo_owner="C1ean-dev",
        repo_name="FileStorageIndexer",
        current_version="2.0.0"
    )

def _configure_application_layer(self):
    # 🎯 Injeta dependências nos use cases
    self._services['check_updates_use_case'] = CheckUpdatesUseCase(
        updater=self._services['updater'],  # ← Interface
        logger=self._services['logger']
    )
```

### **📊 Sequência Completa de Execução**

```
1. 👤 USUÁRIO clica "9. Verificar atualizações"
   ↓
2. 🖥️ CLI Handler recebe input
   ↓
3. 🏗️ Container DI resolve dependências
   ↓
4. 🎯 Use Case orquestra operação
   ↓
5. 🏛️ Domain Service define regras
   ↓
6. 🏗️ Infrastructure executa operação real
   ↓
7. 🌐 GitHub API retorna dados
   ↓
8. 🏗️ Infrastructure processa resposta
   ↓
9. 🏛️ Domain Service valida dados
   ↓
10. 🎯 Use Case formata resultado
    ↓
11. 🖥️ CLI Handler exibe resultado
    ↓
12. 👤 USUÁRIO vê resultado final
```

### **🎨 Exemplo Visual do Fluxo**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PRESENTATION  │ -> │  APPLICATION    │ -> │    DOMAIN       │
│   (Handlers)    │    │   (Use Cases)   │    │   (Services)    │
│                 │    │                 │    │                 │
│ check_updates_  │    │ CheckUpdates    │    │ Updater         │
│ handler.py      │    │ UseCase         │    │ (Interface)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ↑                       ↑                       ↑
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ INFRASTRUCTURE  │
                    │   (Implement)   │
                    │                 │
                    │ GitHubUpdater   │
                    │ (Concrete Impl) │
                    └─────────────────┘
```

## 🧪 **Testes**

### **Executar Testes**
```bash
# Testes unitários
python -m pytest tests/unit/

# Testes de integração
python -m pytest tests/integration/

# Todos os testes
python -m pytest
```

### **Cobertura de Testes**
```bash
# Com relatório de cobertura
python -m pytest --cov=src --cov-report=html
```

### **Verificação das Camadas**
```python
# Teste rápido das dependências
from src.presentation.config.dependency_injection import get_container

container = get_container()
print("✅ Container inicializado")

# Teste dos serviços principais
updater = container.get('updater')
print(f"✅ Updater: {updater.__class__.__name__}")

use_case = container.get_check_updates_use_case()
print(f"✅ Use Case: {use_case.__class__.__name__}")

print("🎉 Todas as camadas estão funcionando!")
```

## 🔧 **Configuração**

### **Variáveis de Ambiente**
```bash
# Database
DATABASE_PATH=./data/file_indexer.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/file_indexer.log

# Performance
BATCH_SIZE=1000
MAX_WORKERS=4
```

## 🤝 **Contribuição**
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📊 **Status do Projeto**

| Componente | Status | Versão |
|------------|--------|---------|
| **Domain Layer** | ✅ Completo | 2.0.0 |
| **Application Layer** | ✅ Completo | 2.0.0 |
| **Infrastructure Layer** | ✅ Completo | 2.0.0 |
| **Presentation Layer** | ✅ Completo | 2.0.0 |
| **Testes** | 🚧 Em desenvolvimento | - |
| **Documentação** | ✅ Completa | 2.0.0 |
 
**Versão:** 2.0.0 
**Status:** ✅ **PRODUÇÃO PRONTO**
