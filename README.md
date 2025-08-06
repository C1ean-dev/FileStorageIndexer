# Indexador de Arquivos de Rede

Este é um script Python para indexar arquivos em pastas de rede (ou locais) e permitir buscas rápidas por nome ou extensão. Ele utiliza SQLite para armazenar o índice e `ThreadPoolExecutor` para processamento paralelo, otimizando o desempenho em grandes volumes de arquivos.

## Funcionalidades

- **Escaneamento de Arquivos:** Indexa recursivamente arquivos em um caminho de rede ou local.
  - **Modo Streaming:** Ideal para pastas muito grandes, com baixo uso de memória.
  - **Modo Batch:** Exibe uma barra de progresso determinada, melhor para pastas de tamanho médio.
- **Escaneamento de Pastas:** Indexa recursivamente Pastas.
- **Busca Rápida via index:**
  - Busca arquivos por nome (exata ou parcial fazendo primeiro uma query sem like depois com like).
  - Busca arquivos por extensão (ex: `.pdf`, `.docx`).
- **Estatísticas:** Exibe o total de arquivos indexados, tamanho total e as extensões de arquivo mais comuns.
- **Limpeza de Índice:** Permite limpar todos os registros do banco de dados.
- **Interface Interativa:** Um menu de linha de comando para fácil interação.

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
3.  **Escanear apenas pastas:** Digite o caminho da pasta para iniciar o escaneamento.
4.  **Buscar arquivo:** Digite o nome do arquivo para buscar.
5.  **Buscar por extensão:** Digite a extensão (ex: `pdf`, `docx`). Se houver muitos resultados, você poderá listar mais, baixar a lista completa em TXT ou voltar ao menu.
6.  **Escanear apenas pastas:** Digite o nome da pasta para buscar.
7.  **Mostrar estatísticas:** Exibe informações sobre o índice.
8.  **Limpar índice:** Remove todos os arquivos indexados do banco de dados.
0.  **Sair:** Encerra o programa.
### Processo de atualização em background
Agora o software atualiza o banco de dados sem a necessidade do usuario realizar um novo scaneamento por ser um processo demorado ele roda em background enquanto a aplicação está em execução abaixo os processos que ele realiza.
- **Obter Estado Atual do Sistema de Arquivos:**
    ele ira percorrer o sistema real capturando suas informaçoes e criando um snapshot
- **Obter Estado Atual do Banco de Dados** 
    consulta o banco e cria um snapshot do banco 
- **Comparar e Sincronizar**
    se um novo objeto é encontrado no snap do sistema de arquivos e não está no snap do banco ele é um NOVO OBJETO chamando indexer.insert_record()
    Caso ele exista em ambos snap e for um FILE sua data é comparada para verificar se ouve alteração e ele é considerado um objeto atualizado
    Caso um objeto exista no banco mas nao exista no sistema de arquivos ele vai ser considerado deletado e será removido do banco 
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
