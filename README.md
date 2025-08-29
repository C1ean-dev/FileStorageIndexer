# 📁 File Indexer - Clean Architecture

Um indexador de arquivos profissional desenvolvido seguindo os princípios da **Clean Architecture**, oferecendo alta performance, testabilidade e manutenibilidade.

## 🎯 **Visão Geral**

O File Indexer é uma aplicação Python que permite indexar arquivos em pastas de rede, oferecendo funcionalidades de busca rápida e estatísticas detalhadas. A versão atual foi completamente reestruturada seguindo a Clean Architecture para garantir qualidade de código profissional.

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
- **🔌 Dependency Injection** - Container IoC completo
- **📚 Repository Pattern** - Abstração de persistência
- **🎯 Use Cases** - Casos de uso bem definidos
- **🔒 Value Objects** - Validação e encapsulamento
- **📝 Structured Logging** - Sistema de logs profissional

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

## 📚 **Documentação**

### **Arquitetura Detalhada**
- [📖 Documentação da Migração](docs/clean_architecture_migration.md)
- [🏗️ Diagramas de Arquitetura](docs/architecture/)
- [🎯 Casos de Uso](docs/use_cases/)

### **Guias de Desenvolvimento**
- [🚀 Guia de Contribuição](CONTRIBUTING.md)
- [📝 Padrões de Código](docs/coding_standards.md)
- [🔧 Configuração do Ambiente](docs/setup.md)

## 🏛️ **Princípios Aplicados**

### **Clean Architecture**
- ✅ **Dependency Rule** - Dependências apontam para dentro
- ✅ **Separation of Concerns** - Responsabilidades bem definidas
- ✅ **Testability** - Código altamente testável
- ✅ **Flexibility** - Fácil manutenção e extensão

### **SOLID Principles**
- ✅ **Single Responsibility** - Uma responsabilidade por classe
- ✅ **Open/Closed** - Aberto para extensão, fechado para modificação
- ✅ **Liskov Substitution** - Subtipos substituem supertipos
- ✅ **Interface Segregation** - Interfaces específicas
- ✅ **Dependency Inversion** - Dependências de abstrações

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

### **Configuração Personalizada**
Edite `src/presentation/config/dependency_injection.py` para personalizar injeção de dependências.

## 🚀 **Próximos Passos**

### **Curto Prazo**
- [ ] Interface web com FastAPI (como o gerenciamento de documentos)
- [ ] Suporte a PostgreSQL (utilizar patterns para que seja possivel flexibilizar o banco talvez utilizando ORM ainda estou analisando)
- [ ] Cache de estatísticas (adição para o FastAPI, para nao realizar tantas verificaçoes diretamente no banco)
- [ ] Testes unitários

### **Médio Prazo**
- [ ] Interface gráfica (tkinker me da mt dor de cabeça mesmo ja utilizando anteriormente)
- [ ] Busca full-text (já implementado na v1 porem não de maneira eficiente)

### **Longo Prazo**
- [ ] Machine Learning para sugestões
- [ ] Integração com cloud storage (armazenamento do banco, talvez o cache tbm)

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
