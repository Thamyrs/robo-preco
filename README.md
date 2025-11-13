# Robô Monitor de Preços

<p>
   <img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=RED&style=for-the-badge" #vitrinedev/>
</p>

## Descrição do projeto

Projeto para a disciplina de Programabilidade e Automação do curso de redes de computadores.

Trata-se de um robô construído com Python e Selenium para verificar o preço de produtos do Aliexpress, e enviar um email de alerta quando existir uma promoção desajada. 

## Workflow

Ao ser executado, o robô passará pelos seguintes passos:

1. Verifica se há conexão com a internet e se as variáveis de ambiente necessárias foram informadas
2. Inicia o web driver do Edge em modo headless (ou seja, a GUI do navegador não será diretamente aberta)
3. Acessa a URL do produto e valida se ela pertence a um produto do Aliexpress
4. Resgata os valores de nome e preço do produto
5. Compara o valor atual do produto com o valor de promoção desejado informado, e caso seja menor ou igual, dispara um email de alerta
6. Registra o histórico de pesquisa em um arquivo csv
7. Cria um arquivo de log com a execução do robô

## Pré-requisitos 
Você precisará ter:
- python3 instalado em sua máquina
- conexão com a internet
- um usuário com domínio gmail.com e com app password configurada

O uso de app password não é recomendado pela Google por não ser muito seguro, e estamos usando nesse projeto como um workaround. 
Portanto, eu recomendo criar uma conta nova no gmail apenas coma finalidade de executar o robô.

Para criar a senha de app, será necessário habilitar a autenticação em duas etapas da sua conta. 
Em seguida, buscar por "segurança > senhas de app" nas configurações da conta,
e criar um código.

<img width="51%" height="auto" alt="MFA" src="https://github.com/user-attachments/assets/b3592ac1-95d7-4f7a-bf6f-05dee22b7fa7" />
<img width="51%" height="auto" alt="app password" src="https://github.com/user-attachments/assets/a0637850-d56f-46ae-befe-9a8464c1197d" />

## Configurações e execução

Voce precisará criar variáveis de ambiente para que o código funcione. 
Caso você esteja executando localmente, crie uma cópia do arquivo .env.example para .env, e certifique-se que as seguintes variáveis estejam configuradas:
- EMAIL_ORIGEM: email do usuário gmail que fará o envio dos alertas
- SENHA_EMAIL: app password do usuário gmail
- EMAIL_DESTINO: email para quem serão enviados os alertas de preço
- PRODUTOS: lista das URLs de produto com o valor minimo aceitavel pelo usuario para o disparo de emails. Deve estar no seguinte formato JSON -> {"https://url1/produto": 20.0, "https://url2/produto": 100.0}

A pasta robo-preco/Scripts contém scripts para executar o código junto com a configuração do ambiente. Eles vão:
- Criar um ambiente virtual python
- Instalar as dependências (requirements.txt) dentro do venv
- Executar o código do robô 

### Execução manual
Caso você esteja em um ambiente Windows, abra a pasta do projeto no PowerShell e execute o seguinte:
```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Scripts\executar_robo.ps1
```

Caso você esteja em um ambiente Linux, abra a pasta do projeto no terminal e execute o seguinte:
```
chmod +x ./Scripts/executar_robo.sh
./Scripts/executar_robo.sh
```

### Execução com agendamento em ambiente Windows
Você pode usar o task scheduler (agendador de tarefas) para executar o script periodicamente. 

Vá em ``Task Scheduler -> Criar Tarefa... -> Ações -> Novo``

Adicione o script ".\Scripts\executar_robo.bat" e configure a ação como "Iniciar um programa"

<img width="350" height="200" alt="image" src="https://github.com/user-attachments/assets/b1b99b7b-dd30-4fd5-ad18-a3531d25fc22" />

Em ``Disparadores -> Novo``, você poderá configurar a frequência que o script será executado.

Não é necessário privilégios elevados para executar o robô.



### Execução com agendament no Github Worflows

O script /.github/workflows/schedule.yaml dentro desse projeto permite que seja criado um Workflow para execução automática do robô.
Ele está configurado para executar a cada 6 horas, mas se você quiser alterar a frequência, altere a linha ``- cron: "0 */6 * * *"`` do arquivo.

Para executar, faça um fork desse projeto para dentro do seu GitHub. 

Para funcionar, você obrigatoriamente precisará configurar secrets e variáveis de ambiente no repositório. 
Nunca use o .env a não ser que você execute o código localmente na sua máquina, pois as credenciais, tokens e outros secrets que você colocar lá ficarão expostos.

Dentro do repositório git do projeto, vá em ``Settings -> Secrets and variables -> Actions``

Em Repository secrets, crie as variáveis EMAIL_ORIGEM, e SENHA_ORIGEM, que armazenarão as credenciais do bot 

<img width="500" height="150" alt="image" src="https://github.com/user-attachments/assets/e89148bc-9222-4a9a-b7ba-a9b1c6f5289d" />

Em repository variables, crie as variáveis EMAIL_DESTINO, que será o email que receberá os alertas, e PRODUTOS, que receberá um JSON informando ``{"url_do_produto": preco_desejado}``

<img width="500" height="150" alt="image" src="https://github.com/user-attachments/assets/da3dfe2f-70eb-4f75-856d-e362b8cd3723" />

Em seguida vá em Actions, você poderá visualizar o workflow "Monitor de Preços" e o histórico de execuções (se houver). 
Você também pode executar a rotina manualmente clicando no nome do workflow -> run workflow

<img width="1889" height="734" alt="image" src="https://github.com/user-attachments/assets/6abd8c71-3a7c-492d-9af8-806d727f7223" />











