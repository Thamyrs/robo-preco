from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from urllib.parse import urlparse
import smtplib
import pandas as pd
import os
import re
import socket
import logging
import json


LOG_DIR = os.path.join(".", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def verificar_conexao(host: str ="8.8.8.8", port: int =53, timeout: int =3) -> bool:
    """
    Verifica se há conexão com a internet tentando se conectar ao DNS do Google (8.8.8.8).
    
    Args:
        host (str): Endereço IP a ser testado (padrão: 8.8.8.8).
        port (int): Porta usada para teste (padrão: 53).
        timeout (int): Tempo máximo de espera em segundos (padrão: 3).
    
    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
        logging.info("Conexão com a internet verificada com sucesso.")
        return True
    except (socket.timeout, socket.error) as e:
        logging.error(f"Sem conexão com a internet: {e}")
        return False


def iniciar_driver() -> webdriver.Edge:
    """
    Inicializa o Microsoft Edge WebDriver em modo headless.

    Returns:
        webdriver.Edge: Instância configurada do Edge WebDriver.
    """
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.page_load_strategy = "eager"

    try:
        driver = webdriver.Edge(options=options)
        logging.info("Driver Edge inicializado com sucesso.")
        return driver
    except Exception as e:
        logging.error(f"Erro ao inicializar o Edge WebDriver: {e}")
        raise


def carregar_produtos_env() -> dict[str, float]:
    """
    Lê a variável de ambiente PRODUTOS e converte seu conteúdo JSON em um dicionário.
    
    Returns:
        dict[str, float]: Dicionário contendo URLs e seus preços-alvo.
    """
    produtos_env = os.getenv("PRODUTOS")

    if not produtos_env:
        logging.error("Variável de ambiente 'PRODUTOS' não definida.")
        return {}

    try:
        produtos = json.loads(produtos_env)
        if not isinstance(produtos, dict) or not all(isinstance(v, (int, float)) for v in produtos.values()):
            logging.error("Formato inválido na variável 'PRODUTOS'. Esperado: {'url': float}")
            return {}
        logging.info(f"{len(produtos)} produto(s) carregado(s) do ambiente.")
        return produtos
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao interpretar JSON da variável 'PRODUTOS': {e}")
        return {}
    

def valida_url(url_produto: str) -> bool:
    """
    Verifica se a URL é válida, pertence ao domínio do AliExpress e representa uma página de produto (incluindo URLs encurtadas).
    
    Args:
        url_produto (str): URL a ser verificada.
    
    Returns:
        bool: True se a URL for válida e corresponder a uma página de produto do AliExpress.
    """
    try:
        resultado = urlparse(url_produto)
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


def obter_dados_produto(driver: webdriver.Edge, url_produto: str) -> tuple[str, float]:
    """Acessa a URL e extrai nome e preço do produto.

    Args:
        driver (webDriver.Edge): Instância do Edge WebDriver.
        url_produto (str): URL a ser acessada.
    
    Returns:
        tuple[str, float]: Nome do produto (str) e preço (float). 
        Caso o preço não seja encontrado ou a URL seja inválida, retorna ("<mensagem>", -1.0)
    """
    if not valida_url(url_produto):
        logging.warning(f"URL inválida ou fora do padrão de produto: {url_produto}")
        return "URL inválida", -1.0

    try:
        driver.get(url_produto)
        logging.info(f"Acessando página: {url_produto}")
    except Exception as e:
        logging.error(f"Erro ao acessar {url_produto}: {e}")
        return "Erro de acesso", -1.0

    wait = WebDriverWait(driver, 10) 

    try:
        nome_elemento = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[@data-pl='product-title']"))
        )
        nome = nome_elemento.text.strip()
    except TimeoutException:
        logging.warning("Tempo limite excedido ao tentar localizar o nome do produto.")
        nome = "Produto não encontrado"
    except NoSuchElementException as e:
        logging.warning(f"Elemento de nome não encontrado: {e}")
        nome = "Produto não encontrado"

    try:
        preco_elemento = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "price-default--current--F8OlYIo"))
        )
        preco_raw = preco_elemento.text
        preco_limpo = re.sub(r"[^\d,]", "", preco_raw)
        preco = float(preco_limpo.replace(",", "."))
    except TimeoutException:
        logging.warning("Tempo limite excedido ao tentar localizar o preço do produto.")
        preco = -1.0
    except (NoSuchElementException, ValueError) as e:
        logging.warning(f"Erro ao capturar ou converter preço: {e}")
        preco = -1.0

    return nome, preco


def registrar_preco_csv(nome_produto: str, preco_produto: float, url_produto: str, nome_arquivo_csv: str ="historico_precos.csv", dir_csv: str =LOG_DIR) -> None:
    """
    Registra o nome, preço e data do produto em um arquivo CSV.

    Args:
        nome_produto (str): nome do produto
        preco_produto (float): preço atual do produto
        url_produto (str): URL do produto
        nome_arquivo_csv (str): nome do arquivo onde será feito os registros (padrão: historico_precos.csv)
        dir_csv: path onde o arquivo .csv será armazenado (padrão: LOG_DIR -> .\\logs)
    """

    path_arquivo_csv=os.path.join(dir_csv, nome_arquivo_csv)

    novo_registro = pd.DataFrame([{
        "Produto": nome_produto,
        "Preço": preco_produto,
        "URL": url_produto,
        "Data": pd.Timestamp.now()
    }])

    if os.path.exists(path_arquivo_csv):
        df_existente = pd.read_csv(path_arquivo_csv)
        df = pd.concat([df_existente, novo_registro], ignore_index=True)
    else:
        df = novo_registro

    df.to_csv(path_arquivo_csv, index=False, encoding="utf-8-sig")
    print(f"Histórico atualizado em '{path_arquivo_csv}'")


def enviar_alerta_email(nome_produto: str, preco_atual: float, preco_alvo: float, url_produto: str, email_destino: str) -> None:
    """
    Envia um alerta por e-mail quando o preço atual for igual ou menor que o preço alvo.

    Args:
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


def main():

    load_dotenv()

    logging.info("Iniciando execução do robô de preços.")

    logging.info("Verificando conexão com a internet...")
    if not verificar_conexao():
        logging.error("Abortando execução: sem conexão com a internet.")
        return

    driver = iniciar_driver()
    logging.info("Driver iniciado.")

    email_destino = os.getenv("EMAIL_DESTINO")
    if not email_destino:
        logging.error("EMAIL_DESTINO não configurado.")
        return

    produtos_monitorados = carregar_produtos_env()
    if not produtos_monitorados:
        logging.error("Nenhum produto informado.")
        return

    for url_produto, preco_alvo in produtos_monitorados.items():
        logging.info(f"Consultando produto: {url_produto}")
        nome, preco = obter_dados_produto(driver, url_produto)
        logging.info(f"{nome}: preço atual R${preco}")
        registrar_preco_csv(nome, preco, url_produto)
        enviar_alerta_email(nome, preco, preco_alvo, url_produto, email_destino)

    driver.quit() 
    logging.info("Execução finalizada com sucesso.")

    
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, "robo_preco.log"), encoding="utf-8"),  
            logging.StreamHandler() 
        ]
    )
    try:
        main()
    except Exception as e:
        logging.error(f"Erro fatal na execução: {e}")