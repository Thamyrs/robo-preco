from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import smtplib
import pandas as pd
import time
import os
import re


def iniciar_driver(headless=True):
    """Inicializa o Microsoft Edge WebDriver.

    É necessário que o arquivo 'msedgedriver.exe' esteja na mesma pasta do projeto 
    ou que o caminho completo seja informado nas opções do EdgeOptions.

    headless=True fará com que que o navegador seja executado em modo silencioso (sem interface gráfica) 
    headless=False o navegador ficará visível durante a execução
    """
    options = webdriver.EdgeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(options=options)
    return driver


def obter_dados_produto(driver, url):
    """Acessa a URL e extrai nome e preço do produto."""

    #TODO: validar erros de execução (como URL inválida e problemas de conectividade)

    driver.get(url)
    time.sleep(6)

    try:
        nome = driver.find_element(By.XPATH, "//h1[@data-pl='product-title']").text
    except:
        nome = "Produto não encontrado"

    """"""
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

if __name__ == "__main__":
    #TODO: remover URL e email hardcoded. 
    url_produto = "https://pt.aliexpress.com/item/1005009310989008.html"
    email_destino="rilap53183@fantastu.com"

    driver = iniciar_driver()
    nome, preco = obter_dados_produto(driver, url_produto)
    driver.quit()

    print(f"Produto: {nome}")
    print(f"Preço atual: {preco}")

    registrar_preco_csv(nome, preco, url_produto)
    enviar_alerta_email(nome, preco, 100.0, url_produto, email_destino)
