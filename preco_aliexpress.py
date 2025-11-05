from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os


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

    try:
        preco = driver.find_element(By.CLASS_NAME, "price-default--current--F8OlYIo").text
    except:
        preco = "Preço não encontrado"

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


def monitorar_produto(url):
    """Executa o processo completo de monitoramento."""
    driver = iniciar_driver()
    nome, preco = obter_dados_produto(driver, url)
    driver.quit()

    print(f"Produto: {nome}")
    print(f"Preço atual: {preco}")

    registrar_preco_csv(nome, preco, url)

#TODO: criar função para alertar quando o preço cair.

#TODO: criar registro de logs da aplicação

if __name__ == "__main__":
    #TODO: remover URL hardcoded. 
    url_produto = "https://pt.aliexpress.com/item/1005008632475317.html"
    monitorar_produto(url_produto)
