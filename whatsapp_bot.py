from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

    def encontrar_grupo(self):
        try:
            # Tentar encontrar o grupo com diferentes estratégias
            try:
                # Primeira tentativa: busca por título exato
                grupo = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//span[@title="{self.nome_grupo}"]'))
                )
                grupo.click()
                return True
            except:
                # Segunda tentativa: busca mais flexível
                grupos = self.driver.find_elements(By.XPATH, f'//div[contains(text(), "{self.nome_grupo}")]')
                if grupos:
                    grupos[0].click()
                    return True
                
                print(f"Grupo '{self.nome_grupo}' não encontrado!")
                return False
        except Exception as e:
            print(f"Erro ao encontrar grupo: {e}")
            return False

    def enviar_resposta(self, mensagem):
        try:
            # Usar o XPath fornecido para encontrar a caixa de entrada de mensagens
            caixa_mensagem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p'))
            )
            caixa_mensagem.click()
            caixa_mensagem.send_keys(mensagem + Keys.ENTER)
            print(f"Resposta enviada: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def monitorar_grupo(self):
        # Encontrar grupo primeiro
        if not self.encontrar_grupo():
            print("Não foi possível encontrar o grupo. Verifique o nome.")
            return

        print("Monitorando mensagens no grupo...")
        while True:
            try:
                # Imprimir todas as mensagens para debug
                mensagens = self.driver.find_elements(By.XPATH, '//div[contains(@class, "message")]')
                if mensagens:
                    ultima_mensagem = mensagens[-1]
                    print(f"Última mensagem: {ultima_mensagem.text}")
                    
                    # Verificar se a última mensagem contém 'Oi'
                    if 'Oi' in ultima_mensagem.text:
                        self.enviar_resposta('Olá! Como posso ajudar?')
                
                time.sleep(5)
            except Exception as e:
                print(f"Erro ao monitorar mensagens: {e}")
                break

    def fechar(self):
        self.driver.quit()


# Exemplo de uso
if __name__ == "__main__":
    bot = WhatsAppGrupoBot(
        caminho_edgedriver='C:\\WebDriver\\msedgedriver.exe',
        nome_grupo='TESTE_CHATBOT'
    )
    bot.monitorar_grupo()
