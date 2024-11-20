import time
import pyperclip  # Para manipular a área de transferência
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Caminho do arquivo .txt a ser monitorado
CAMINHO_ARQUIVO = "C:\\Users\\Jhonatan\\chatbot\\notificacao.txt"  # Caminho do seu arquivo .txt

# Classe do bot para interagir com o WhatsApp
class WhatsAppGrupoBot:
    def __init__(self, caminho_edgedriver, nome_grupo):
        # Configurações do navegador
        edge_options = Options()
        service = Service(caminho_edgedriver)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.nome_grupo = nome_grupo

        # Abrir WhatsApp Web
        self.driver.get('https://web.whatsapp.com')
        print("Escaneie o QR Code para fazer login")
        input("Pressione Enter após escanear o QR Code...")

    def garantir_que_esta_no_grupo(self):
        try:
            # Tentar encontrar o grupo com o nome fornecido
            grupo = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[@title="{self.nome_grupo}"]'))
            )
            grupo.click()  # Clica no grupo para abrir a conversa
            print(f"Grupo '{self.nome_grupo}' encontrado e aberto.")
            return True
        except Exception as e:
            print(f"Erro ao garantir que está no grupo: {e}")
            return False

    def enviar_resposta(self, mensagem):
        try:
            # Garante que o bot está no grupo antes de enviar a mensagem
            if not self.garantir_que_esta_no_grupo():
                print("Erro: não foi possível encontrar o grupo.")
                return

            # Apaga o conteúdo da caixa de mensagem
            campo_texto = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p'))
            )
            campo_texto.click()  # Clica para ativar o campo de mensagem
            campo_texto.send_keys(Keys.CONTROL + "a")  # Ctrl + A para selecionar tudo
            campo_texto.send_keys(Keys.DELETE)  # Apaga o conteúdo selecionado

            # Coloca o conteúdo do arquivo na área de transferência e cola no campo de mensagem
            pyperclip.copy(mensagem)  # Copia o conteúdo para a área de transferência
            campo_texto.send_keys(Keys.CONTROL + "v")  # Cola o conteúdo

            # Envia a mensagem pressionando Enter
            campo_texto.send_keys(Keys.RETURN)  # Envia a mensagem
            print(f"Mensagem enviada: {mensagem}")

            # Limpa a área de transferência após o envio
            pyperclip.copy("")  # Limpa a área de transferência
        except Exception as e:
            print(f"Erro ao enviar a mensagem: {e}")

    def fechar(self):
        self.driver.quit()


# Classe para monitorar alterações no arquivo .txt
class FileMonitor(FileSystemEventHandler):
    def __init__(self, bot):
        self.bot = bot

    def on_modified(self, event):
        # Verifica se o arquivo modificado é o arquivo que estamos monitorando
        if event.src_path == CAMINHO_ARQUIVO:
            print(f"Arquivo {CAMINHO_ARQUIVO} alterado. Enviando mensagem no WhatsApp...")
            # Lê o conteúdo do arquivo .txt
            with open(CAMINHO_ARQUIVO, 'r') as file:
                conteudo = file.read()

            # Remove quebras de linha extras (caso o conteúdo tenha múltiplas linhas)
            #conteudo = " ".join(conteudo.splitlines())

            # Envia o conteúdo do arquivo no WhatsApp
            self.bot.enviar_resposta(conteudo)


# Configuração do bot e monitoramento de arquivos
if __name__ == "__main__":
    # Caminho do WebDriver (Edge)
    caminho_edgedriver = 'C:\\WebDriver\\msedgedriver.exe'  # Substitua com o caminho correto para o seu WebDriver
    nome_grupo = 'TESTE_CHATBOT'  # Substitua com o nome do seu grupo

    # Iniciar o bot para WhatsApp
    bot = WhatsAppGrupoBot(caminho_edgedriver, nome_grupo)

    # Configurar o monitoramento de arquivos
    event_handler = FileMonitor(bot)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(CAMINHO_ARQUIVO), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
