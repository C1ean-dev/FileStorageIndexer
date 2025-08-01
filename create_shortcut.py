import os
import win32com.client

def create_shortcut():
    """
    Cria um atalho na área de trabalho para o executável 'pesquisa.exe'.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(script_dir, "dist", "pesquisa.exe")
    icon_path = os.path.join(script_dir, "icons", "Neco-Arc_Remake.ico")
    shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Pesquisa.lnk")
    working_directory = os.path.join(script_dir, "dist")

    if not os.path.exists(target_path):
        print(f"Erro: O arquivo executável não foi encontrado em '{target_path}'.")
        print("Certifique-se de que o build do PyInstaller foi executado com sucesso.")
        return

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.IconLocation = icon_path
    shortcut.WorkingDirectory = working_directory
    shortcut.save()

    print(f"Atalho 'Pesquisa.lnk' criado em '{shortcut_path}'.")
    print("Agora você pode clicar com o botão direito no atalho e selecionar 'Fixar na Barra de Tarefas'.")

if __name__ == "__main__":
    create_shortcut()
