from core.indexer import FileIndexer, format_file_size
import os

def search_extension_menu(indexer: FileIndexer):
    """Handles the 'Search by Extension' menu option."""
    ext = input("Digite a extensão (ex: pdf, docx): ").strip()
    if ext:
        results = indexer.search_by_extension(ext)
        if results:
            print(f"\nEncontrados {len(results)} arquivo(s) com extensão .{ext}")
            current_display_index = 0
            while True:
                for filename, full_path, file_size, modified_date in results[current_display_index:current_display_index + 10]:
                    print(f"  {filename} - {full_path}")
                
                current_display_index += 10
                
                if current_display_index >= len(results):
                    print("\nTodos os arquivos foram listados.")
                    break
                
                remaining_files = len(results) - current_display_index
                print(f"  ... e mais {remaining_files} arquivos")
                
                while True:
                    action = input("\nOpções:\n1. Listar mais 10 arquivos\n2. Baixar lista completa (TXT)\n3. Voltar ao menu\nEscolha uma opção: ").strip()
                    if action == "1":
                        break  # Continue o loop externo para listar mais
                    elif action == "2":
                        output_filename = input("Digite o nome do arquivo TXT para salvar (ex: resultados.txt): ").strip()
                        if not output_filename:
                            output_filename = "resultados_busca.txt"
                        
                        try:
                            with open(output_filename, "w", encoding="utf-8") as f:
                                for filename, full_path, file_size, modified_date in results:
                                    f.write(f"Arquivo: {filename}\n")
                                    f.write(f"Caminho: {full_path}\n")
                                    f.write(f"Tamanho: {format_file_size(file_size)}\n")
                                    f.write(f"Modificado: {modified_date}\n")
                                    f.write("-" * 80 + "\n")
                            print(f"Lista salva em '{output_filename}' com sucesso.")
                        except IOError as e:
                            print(f"Erro ao salvar arquivo: {e}")
                        break # Voltar ao menu principal após salvar
                    elif action == "3":
                        break # Voltar ao menu principal
                    else:
                        print("Opção inválida. Tente novamente.")
                if action == "2" or action == "3":
                    break # Sair do loop principal se o usuário escolheu salvar ou voltar
        else:
            print("Nenhum arquivo encontrado.")
