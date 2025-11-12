from selenium import webdriver
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from urllib.parse import urlparse
import smtplib
import pandas as pd
import time
import os
import re
import socket
import logging
import json

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler(".\\logs\\robo_preco.log", encoding="utf-8"),  
        logging.StreamHandler() 
    ]
)

def verificar_conexao(host="8.8.8.8", port=53, timeout=3):
    """Verifica se há conexão com a internet tentando se conectar ao DNS do Google (8.8.8.8).
    Retorna True se a conexão for bem-sucedida.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        logging.info("Conexão com a internet verificada com sucesso.")
        return True
    except socket.error as e:
        logging.error(f"Sem conexão com a internet: {e}")
        return False


def valida_url(url):
    """
    Verifica se a URL é válida, pertence ao domínio do AliExpress e representa uma página de produto (incluindo URLs encurtadas).
    Retorna True se a url passar por todos os 3 requisitos.
    """
    try:
        resultado = urlparse(url)
        if not all([resultado.scheme, resultado.netloc]):
            return False
        dominio = resultado.netloc.lower()
        if not dominio.endswith("aliexpress.com"):
            return False
        padrao_item = re.search(r"/item/\d+\.html", resultado.path)
        padrao_encurtado = dominio.startswith("a.aliexpress.com") and resultado.path.startswith("/_")
        return bool(padrao_item or padrao_encurtado)
    except Exception:
        return False


def iniciar_driver(headless=True):
    """Inicializa o Microsoft Edge WebDriver.

    É necessário que o arquivo 'msedgedriver.exe' seja da mesma versão que o navegador da sua máquina e esteja na mesma pasta do projeto ou que o caminho completo seja informado nas opções do EdgeOptions.

    headless=True -> fará com que que o navegador seja executado em modo silencioso (sem interface gráfica) 
    headless=False -> o navegador ficará visível durante a execução
    """
    options = webdriver.EdgeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(options=options)
    return driver


def obter_dados_produto(driver, url):
    """Acessa a URL e extrai nome e preço do produto.
    
    Retorna:
        nome (str): nome do produto.
        preco (float | None): preço convertido para float. Se o preço não for encontrado ou a URL for inválida, será retornado -1.
    """
    if(valida_url(url)):
        try:
            driver.get(url)
            time.sleep(6)
            logging.info(f"Acessando página: {url}")
        except Exception as e:
            logging.error(f"Erro ao acessar {url}: {e}")
            return "Erro de acesso", -1

        try:
            nome = driver.find_element(By.XPATH, "//h1[@data-pl='product-title']").text
        except Exception as e:
            logging.warning(f"Não foi possível capturar o nome do produto: {e}")
            nome = "Produto não encontrado"

        try:
            preco= driver.find_element(By.CLASS_NAME, "price-default--current--F8OlYIo").text
            preco_limpo = re.sub(r"[^\d,]", "", preco)  
            preco = float(preco_limpo.replace(",", "."))  
        except Exception as e:
            logging.warning(f"Erro ao capturar preço: {e}")
            preco = -1
        
    else:
        logging.warning(f"URL inválida ou fora do padrão de produto: {url}")
        nome = "URL inválida"
        preco = -1
    
    return nome, preco


def registrar_preco_csv(nome, preco, url, arquivo_csv=".\\logs\\historico_precos.csv"):
    """Registra o nome, preço e data no arquivo CSV."""
    novo_registro = pd.DataFrame([{
        "Produto": nome,
        "Preço": preco,
        "URL": url,
        "Data": pd.Timestamp.now()
    }])

    if os.path.exists(arquivo_csv):
        df_existente = pd.read_csv(arquivo_csv)
        df = pd.concat([df_existente, novo_registro], ignore_index=True)
    else:
        df = novo_registro

    df.to_csv(arquivo_csv, index=False, encoding="utf-8-sig")
    print(f"Histórico atualizado em '{arquivo_csv}'")


def enviar_alerta_email(nome_produto, preco_atual, preco_alvo, url_produto,
                        email_destino):
    """
    Envia um alerta por e-mail quando o preço atual for igual ou menor que o preço alvo.

    Parâmetros:
        nome_produto (str): Nome do produto monitorado.
        preco_atual (float): Preço atual do produto.
        preco_alvo (float): Preço desejado para o alerta.
        url_produto (str): URL do produto.
        email_destino (str): E-mail do destinatário que receberá o alerta.
    """

    email_origem = os.getenv("EMAIL_ORIGEM")
    senha_email = os.getenv("SENHA_EMAIL")

    if preco_atual >= 0 and preco_atual <= preco_alvo:
        logging.info(f"{nome_produto} está a R$ {preco_atual}, R$ {round(preco_alvo - preco_atual, 2)} a menos que o valor alvo!")
        logging.info(f"Preparando o envio do alerta")
        assunto = f"Alerta de preço - {nome_produto}"
        corpo = f"""
        O preço do produto caiu! 🎉

        🛍️ Produto: {nome_produto}
        🎯 Preço mínimo desejado: R$ {preco_alvo}
        💸 Preço atual: R$ {preco_atual}
        
        🔗 Link: {url_produto}

        Atenciosamente,
        Seu Bot de Monitoramento de Preços 🤖
        """

        msg = MIMEMultipart()
        msg["From"] = email_origem
        msg["To"] = email_destino
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
                servidor.starttls()
                servidor.login(email_origem, senha_email)
                servidor.send_message(msg)
            logging.info(f"E-mail de alerta enviado para {email_destino} ({nome_produto})")
        except Exception as e:
            logging.error(f"Erro ao enviar e-mail: {e}")


def carregar_produtos_env():
    """
    Lê a variável de ambiente PRODUTOS e converte para dicionário.
    Exemplo esperado:
    {"url1": 100.0, "url2": 55.5}
    """

    produtos_env = os.getenv("PRODUTOS")

    if not produtos_env:
        logging.error("Variável PRODUTOS não definida.")
        return {}

    try:
        produtos = json.loads(produtos_env)
        logging.info(f"{len(produtos)} produto(s) carregado(s) do ambiente.")
        return produtos
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao interpretar JSON da variável PRODUTOS: {e}")
        return {}


def main():

    load_dotenv()

    logging.info("Iniciando execução do robô de preços.")

    email_destino = os.getenv("EMAIL_DESTINO")
    if not email_destino:
        logging.error("EMAIL_DESTINO não configurado.")
        return

    produtos_monitorados = carregar_produtos_env()
    if not produtos_monitorados:
        logging.error("Nenhum produto informado.")
        return

    logging.info("Verificando conexão com a internet...")
    if not verificar_conexao():
        logging.error("Abortando execução: sem conexão com a internet.")
        return
    
    driver = iniciar_driver()
    logging.info("Driver iniciado.")

    for url_produto, preco_alvo in produtos_monitorados.items():
        logging.info(f"Consultando produto: {url_produto}")
        nome, preco = obter_dados_produto(driver, url_produto)
        logging.info(f"{nome}: preço atual R${preco}")
        registrar_preco_csv(nome, preco, url_produto)
        enviar_alerta_email(nome, preco, preco_alvo, url_produto, email_destino)
        
    driver.quit() 
    logging.info("Execução finalizada com sucesso.")
    
    
if __name__ == "__main__":
    main()