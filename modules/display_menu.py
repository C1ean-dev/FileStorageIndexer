def display_menu():
    # ANSI escape codes for colors
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    menu_options = f"""
    Opções:
        {GREEN}--- Escaneamento ---
        1. Escanear pasta de rede (Streaming - muito recomendado)
        2. Escanear pasta de rede (Batch - progresso determinado)
        3. Escanear apenas pastas{RESET}
        {BLUE}--- Busca ---
        4. Buscar arquivo
        5. Buscar por extensão
        6. Buscar pasta{RESET}
        {YELLOW}--- Configurações e Status ---
        7. Mostrar estatísticas
        8. Limpar índice
        9. Criar atalho na área de trabalho{RESET}
        {RED}--- Sair ---
        0. Sair{RESET}
    """
    print(menu_options)
