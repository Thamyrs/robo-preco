from selenium import webdriver
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium.common.exceptions import WebDriverException
from dotenv import load_dotenv
from urllib.parse import urlparse
import smtplib
import pandas as pd
import time
import os
import re
import socket


def verificar_conexao(host="8.8.8.8", port=53, timeout=3):
    """Verifica se há conexão com a internet tentando se conectar ao DNS do Google (8.8.8.8).
    Retorna True se a conexão for bem-sucedida.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def valida_url(url):
    """
    Verifica se a URL é válida, pertence ao domínio do AliExpress e
    representa uma página de produto (incluindo URLs encurtadas).
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


def iniciar_driver(headless=False):
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
        preco (float | None): preço convertido para float, ou None se não encontrado.
    """
    try:
        driver.get(url)
        time.sleep(6)
    except WebDriverException as e:
        if "ERR_INTERNET_DISCONNECTED" in str(e):
            raise ConnectionError("Sem conexão com a internet. Verifique sua rede e tente novamente.")
        else:
            raise

    try:
        nome = driver.find_element(By.XPATH, "//h1[@data-pl='product-title']").text
    except:
        nome = "Produto não encontrado"

    try:
        preco= driver.find_element(By.CLASS_NAME, "price-default--current--F8OlYIo").text
        preco_limpo = re.sub(r"[^\d,]", "", preco)  
        preco = float(preco_limpo.replace(",", "."))  
    except:
        preco = None

    return nome, preco


def registrar_preco_csv(nome, preco, url, arquivo_csv="historico_precos_aliexpress.csv"):
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
    load_dotenv()

    #TODO: Configurar GitHub secrets e workflow do GitHub Actions.

    email_origem = os.getenv("EMAIL_ORIGEM")
    senha_email = os.getenv("SENHA_EMAIL")

    if preco_atual <= preco_alvo:
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

            print(f"Alerta enviado com sucesso para {email_destino}!")
        except Exception as e:
            print(f"⚠️ Erro ao enviar e-mail: {e}")

#TODO: criar registro de logs da aplicação

def main():
#TODO: remover URL e email hardcoded. 
    url_produto = "https://pt.aliexpress.com/item/1005008632475317.html"
    email_destino="rilap53183@fantastu.com"

    print("Verificando conexão com a internet...")
    if not verificar_conexao():
        print("❌ Sem conexão com a internet. Abortando execução.")
        return

    print("Validando formato da URL...")
    if not valida_url(url_produto):
        print("❌ URL com formato inválido. Pulando execução.")
        return
    
    driver = iniciar_driver()
    nome, preco = obter_dados_produto(driver, url_produto)
    driver.quit()

    print(f"Produto: {nome}")
    print(f"Preço atual: {preco}")

    registrar_preco_csv(nome, preco, url_produto)
    enviar_alerta_email(nome, preco, 100.0, url_produto, email_destino)

if __name__ == "__main__":
    main()