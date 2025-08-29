import os
import sys
import win32com.client

def create_shortcut():
    """
    Cria um atalho na área de trabalho para o executável que está rodando.
    """
    # sys.executable é o caminho para o executável (ex: pesquisa.exe)
    target_path = sys.executable
    working_directory = os.path.dirname(target_path)
    shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Pesquisa.lnk")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    # Usa o próprio executável como fonte do ícone
    shortcut.IconLocation = target_path
    shortcut.WorkingDirectory = working_directory
    shortcut.save()

    print(f"Atalho 'Pesquisa.lnk' criado em '{shortcut_path}'.")
    print("Agora você pode clicar com o botão direito no atalho e selecionar 'Fixar na Barra de Tarefas'.")

if __name__ == "__main__":
    create_shortcut()
