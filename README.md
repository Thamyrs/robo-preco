# Robô Monitor de Preços

<p>
   <img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=RED&style=for-the-badge" #vitrinedev/>
</p>


## Descrição do projeto

Projeto para a disciplina de Programabilidade e Automação do curso de redes de computadores.

Trata-se de um robô construído com Python e Selenium para verificar o preço de produtos do Aliexpress, e enviar um email de alerta quando existir uma promoção desajada. 


## Workflow

Ao ser executado, o robô segue os seguintes passos:

1. Verifica se há conexão com a internet e se as variáveis de ambiente foram informadas  
2. Inicia o **web driver do Edge** em modo *headless* (sem abrir a interface gráfica)  
3. Acessa a URL do produto e valida se ela pertence a uma página de produto do Aliexpress  
4. Resgata os valores de **nome** e **preço do produto**  
5. Compara o valor atual com o preço desejado e, se for menor ou igual, **envia um e-mail de alerta**  
6. Registra o histórico de pesquisa em um arquivo `.csv`  
7. Cria um arquivo de **log** com a execução do robô 


## Pré-requisitos 

Você precisará ter:
- ``python3`` instalado em sua máquina  
- Conexão com a internet  
- Uma conta **@gmail.com** com **App Password** configurada  

> **Observação:**  
> O uso de *App Password* não é recomendado pela Google por questões de segurança.  
> Recomendo criar uma conta nova **somente para uso do robô**.


### Como criar uma App Password

1. Habilite a **autenticação em duas etapas** da sua conta  
2. Vá em **Segurança → Senhas de app**  
3. Gere um código e copie-o para uso nas variáveis de ambiente  

<img width="51%" height="auto" alt="MFA" src="https://github.com/user-attachments/assets/b3592ac1-95d7-4f7a-bf6f-05dee22b7fa7" />
<img width="51%" height="auto" alt="app password" src="https://github.com/user-attachments/assets/a0637850-d56f-46ae-befe-9a8464c1197d" />

## Configurações e execução

Voce precisará criar variáveis de ambiente para que o código funcione. 

Se estiver executando localmente, copie o arquivo `.env.example` para `.env` e configure os valores:
- EMAIL_ORIGEM=<email_gmail>
- SENHA_EMAIL=<app_password>
- EMAIL_DESTINO=<email_para_alertas>
- PRODUTOS={"https://url1/produto": 20.0, "https://url2/produto": 100.0}

> O campo `PRODUTOS` deve estar no formato JSON, em que a chave é a URL do produto e o valor é um número float que representa o preço desejado para o alerta.

--- 

A pasta `robo-preco/Scripts` contém scripts para facilitar a execução:
- Cria o ambiente virtual Python  
- Instala as dependências (`requirements.txt`)  
- Executa o código do robô 

### Execução manual
#### Windows (Powershell)
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Scripts\executar_robo.ps1
```

#### Linux (Terminal)
```bash
chmod +x ./Scripts/executar_robo.sh
./Scripts/executar_robo.sh
```

### Execução com Agendamento (Windows)
Você pode usar o task scheduler (agendador de tarefas) para executar o script periodicamente. 

Vá em ``Task Scheduler -> Criar Tarefa... -> Ações -> Novo``

Adicione o script ".\Scripts\executar_robo.bat" e configure a ação como "Iniciar um programa"

<img width="350" height="200" alt="image" src="https://github.com/user-attachments/assets/b1b99b7b-dd30-4fd5-ad18-a3531d25fc22" />

Em ``Disparadores -> Novo``, você poderá configurar a frequência que o script será executado.

Não é necessário privilégios elevados para executar o robô.



### Execução com agendamento no GitHub Workflows

O script [`/.github/workflows/schedule.yml`](./.github/workflows/schedule.yml) dentro desse projeto permite que seja criado um **Workflow** para execução automática do robô.  
Ele está configurado para executar **a cada 6 horas**, mas se você quiser alterar a frequência, modifique a linha abaixo dentro do arquivo:

```yaml
- cron: "0 */6 * * *"
```

#### Como executar

1. **Faça um fork** deste projeto para o seu GitHub.  
2. **Configure os secrets e variáveis de ambiente** no repositório.  
   > **Atenção:** Nunca use o `.env` a não ser que você execute o código localmente na sua máquina, pois as credenciais, tokens e outros secrets que você colocar lá ficarão expostos.

---

#### Configuração de Secrets

Dentro do repositório, vá em:

``
Settings → Secrets and variables → Actions
``

Em **Repository secrets**, crie as seguintes variáveis:

| Nome | Descrição |
|------|------------|
| `EMAIL_ORIGEM` | E-mail usado pelo bot |
| `SENHA_ORIGEM` | Senha do e-mail do bot |

<img width="51%" height="auto" alt="secrets" src="https://github.com/user-attachments/assets/e89148bc-9222-4a9a-b7ba-a9b1c6f5289d" />

---

#### Configuração de Variáveis

Em **Repository variables**, crie:

| Nome | Descrição |
|------|------------|
| `EMAIL_DESTINO` | E-mail que receberá os alertas |
| `PRODUTOS` | JSON com os produtos e preços desejados |

Exemplo de valor para `PRODUTOS`:

```json
{"https://exemplo.com/produto1": 150.00, "https://exemplo.com/produto2": 299.90}
```

<img width="51%" height="auto" alt="variaveis" src="https://github.com/user-attachments/assets/da3dfe2f-70eb-4f75-856d-e362b8cd3723" />

---

#### Executando o Workflow

Depois de configurar tudo, vá em **Actions**.  
Você verá o workflow **“Monitor de Preços”** e o histórico de execuções (se houver).  
Você também pode **executar manualmente** clicando em:

``
Actions → Monitor de Preços → Run workflow
``

<img width="1889" height="734" alt="image" src="https://github.com/user-attachments/assets/6abd8c71-3a7c-492d-9af8-806d727f7223" />











