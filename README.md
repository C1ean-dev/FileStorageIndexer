# Indexador de Arquivos de Rede

Este é um script Python para indexar arquivos em pastas de rede (ou locais) e permitir buscas rápidas por nome ou extensão. Ele utiliza SQLite para armazenar o índice e `ThreadPoolExecutor` para processamento paralelo, otimizando o desempenho em grandes volumes de arquivos.

## Funcionalidades

- **Escaneamento de Pastas:** Indexa recursivamente arquivos em um caminho de rede ou local.
  - **Modo Streaming:** Ideal para pastas muito grandes, com baixo uso de memória.
  - **Modo Batch:** Exibe uma barra de progresso determinada, melhor para pastas de tamanho médio.
- **Busca Rápida:**
  - Busca arquivos por nome (exata ou parcial).
  - Busca arquivos por extensão (ex: `.pdf`, `.docx`).
- **Estatísticas:** Exibe o total de arquivos indexados, tamanho total e as extensões de arquivo mais comuns.
- **Limpeza de Índice:** Permite limpar todos os registros do banco de dados.
- **Interface Interativa:** Um menu de linha de comando para fácil interação.
- **Exportação de Resultados:** Opção de salvar resultados de busca por extensão em um arquivo de texto (`.txt`).

## Requisitos

- Python 3.x
- Bibliotecas Python: `sqlite3` (geralmente incluída no Python), `tqdm`, `pathlib`, `argparse`.

Você pode instalar as dependências usando `pip`:

```bash
pip install -r requirements.txt
```

## Como Usar

### Execução Interativa

Execute o script sem argumentos para iniciar o menu interativo:

```bash
python file_indexer.py
```

No menu, você poderá escolher entre as seguintes opções:

1.  **Escanear pasta de rede (Streaming):** Digite o caminho da pasta para iniciar o escaneamento. Recomendado para grandes volumes de dados.
2.  **Escanear pasta de rede (Batch):** Digite o caminho da pasta para iniciar o escaneamento. Exibe uma barra de progresso.
3.  **Buscar arquivo:** Digite o nome do arquivo para buscar.
4.  **Buscar por extensão:** Digite a extensão (ex: `pdf`, `docx`). Se houver muitos resultados, você poderá listar mais, baixar a lista completa em TXT ou voltar ao menu.
5.  **Mostrar estatísticas:** Exibe informações sobre o índice.
6.  **Limpar índice:** Remove todos os arquivos indexados do banco de dados.
0.  **Sair:** Encerra o programa.

### Execução por Linha de Comando (Argumentos)

Você também pode usar o script com argumentos de linha de comando para operações específicas:

-   **Escanear uma pasta:**
    ```bash
    python file_indexer.py --scan "\\caminho\da\sua\pasta\de\rede" --streaming
    # ou para modo batch
    python file_indexer.py --scan "\\caminho\da\sua\pasta\de\rede" --batch
    ```
    (Use `--streaming` para baixo uso de memória ou `--batch` para barra de progresso determinada)

-   **Buscar um arquivo por nome:**
    ```bash
    python file_indexer.py --search "meu_documento"
    # Para busca exata:
    python file_indexer.py --search "relatorio_final.pdf" --exact
    ```

-   **Buscar arquivos por extensão:**
    ```bash
    python file_indexer.py --extension "pdf"
    ```

-   **Mostrar estatísticas do índice:**
    ```bash
    python file_indexer.py --stats
    ```

-   **Limpar o índice:**
    ```bash
    python file_indexer.py --clear
    ```

-   **Especificar o caminho do banco de dados:**
    ```bash
    python file_indexer.py --db "meu_indice.db" --scan "C:\minha_pasta"
    ```

-   **Especificar o número de threads (workers):**
    ```bash
    python file_indexer.py --workers 4 --scan "C:\minha_pasta"
    ```

## Estrutura do Projeto

-   `file_indexer.py`: O script principal que contém a lógica do indexador e a interface de usuário.
-   `utils\updateRelease\updater.py`: realiza atualizaçoes baseado nas releases do github.
-   `file_index.db`: O arquivo de banco de dados SQLite onde as informações dos arquivos são armazenadas. (criado pelo indexer)
-   `file_indexer.log`: Arquivo de log para registrar operações e erros. (criado pelo indexer)

## Contribuição

Sinta-se à vontade para contribuir, reportar issues ou sugerir melhorias.
