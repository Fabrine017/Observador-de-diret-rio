# Sistema de Monitoramento de Diretório

## Sobre o projeto

Este projeto consiste em um sistema de monitoramento de diretório desenvolvido em Python. Seu objetivo é acompanhar as alterações realizadas em um diretório durante a execução do programa, identificando arquivos **adicionados, removidos e renomeados**.

O sistema realiza verificações periódicas do diretório, registra os eventos detectados em um arquivo de log e, ao final da execução, apresenta um relatório com métricas do monitoramento.

O projeto foi desenvolvido como uma aplicação prática para estudo de **Python, manipulação de arquivos e diretórios, concorrência com threads, logging e geração de métricas**.

---

## Funcionalidades

- Monitoramento periódico de um diretório.
- Identificação de arquivos adicionados.
- Identificação de arquivos removidos.
- Identificação de arquivos renomeados.
- Registro dos eventos em arquivo de log.
- Rotação automática dos arquivos de log por tamanho.
- Utilização de timestamps nos registros.
- Execução simultânea do monitoramento e do comando de encerramento.
- Geração de relatório ao final da execução.
- Tratamento de diretório inexistente por meio de exceção personalizada.
- Aceitação do comando de encerramento sem diferenciação entre letras maiúsculas e minúsculas.

---

## Tecnologias e bibliotecas

| Biblioteca | Finalidade |
|---|---|
| `os` | Acesso ao sistema de arquivos, listagem de diretórios e obtenção de informações dos arquivos. |
| `time` | Controle do intervalo entre verificações e cálculo do tempo de monitoramento. |
| `threading` | Execução concorrente do monitoramento e da rotina de encerramento. |
| `logging` | Geração e gerenciamento dos registros de eventos. |
| `RotatingFileHandler` | Rotação dos arquivos de log quando o limite de tamanho é atingido. |
| `pathlib.Path` | Importada para possível manipulação de caminhos, embora não seja utilizada na implementação atual. |

---

## Arquitetura geral

```text
                    INÍCIO
                       │
                       ▼
              Solicita o diretório
                       │
                       ▼
             Verifica se existe
                  │         │
                 NÃO       SIM
                  │         │
                  ▼         ▼
             Exceção     Inicia threads
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        Thread de encerramento       Thread de monitoramento
                │                           │
                │                    Lista arquivos
                │                           │
                │                    Aguarda 5 segundos
                │                           │
                │                    Lista novamente
                │                           │
                │              Compara os dois estados
                │                           │
                │             ┌─────────────┼─────────────┐
                │             ▼             ▼             ▼
                │         Adicionado     Removido     Renomeado
                │             │             │             │
                │             └─────────────┼─────────────┘
                │                           ▼
                │                     Gera log
                │                           │
                └───────────────► Verifica evento de parada
                                            │
                                            ▼
                                  Gera relatório final
```

---

# Monitoramento do diretório

A função `monitorar()` é responsável por acompanhar o estado do diretório.

A cada ciclo, o programa obtém uma lista dos arquivos presentes:

```python
arquivos_iniciais = os.listdir(diretorio)
```

Em seguida, registra o identificador (`st_ino`) de cada arquivo:

```python
id_iniciais[arquivo_inicial] = os.stat(caminho_inicial).st_ino
```

O sistema aguarda cinco segundos e realiza uma nova listagem:

```python
arquivos_atuais = os.listdir(diretorio)
```

As duas listas representam estados diferentes do diretório. A comparação permite identificar alterações ocorridas durante o intervalo.

---

## Identificação de arquivos adicionados

Os arquivos presentes no estado atual, mas ausentes no estado inicial, são identificados utilizando conjuntos:

```python
set(arquivos_atuais) - set(arquivos_iniciais)
```

O resultado é armazenado na lista de arquivos adicionados e registrado no log.

Exemplo:

```text
Arquivo adicionado: relatorio.txt
```

---

## Identificação de arquivos removidos

O processo inverso identifica arquivos que estavam presentes inicialmente, mas não estão mais no diretório:

```python
set(arquivos_iniciais) - set(arquivos_atuais)
```

O evento é armazenado e registrado no arquivo de log.

Exemplo:

```text
Arquivo removido: dados.csv
```

---

## Identificação de arquivos renomeados

A identificação de renomeações utiliza o identificador retornado por:

```python
os.stat(caminho).st_ino
```

Inicialmente, o sistema associa cada nome de arquivo ao seu identificador:

```text
nome do arquivo → ID
```

Posteriormente, verifica os identificadores dos arquivos encontrados no estado atual.

Quando o mesmo identificador aparece associado a um nome diferente, o sistema interpreta a alteração como uma possível renomeação.

Exemplo:

```text
Arquivo renomeado: antigo.txt -> novo.txt
```

Essa abordagem utiliza a identidade do arquivo como referência para diferenciar uma renomeação de uma simples combinação de remoção e adição.

> **Observação:** o significado de `st_ino` é dependente do sistema operacional e do sistema de arquivos. A implementação atual considera o ambiente Windows utilizado no projeto.

---

# Concorrência com `threading`

O sistema utiliza duas threads principais:

```python
exec_encerrar = threading.Thread(target=encerrar)
exec_monitorar = threading.Thread(target=monitorar)
```

### Thread de monitoramento

A função `monitorar()` executa continuamente as verificações do diretório.

### Thread de encerramento

A função `encerrar()` permanece aguardando uma entrada do usuário:

```text
Digite "stop" para encerrar:
```

A entrada é convertida para letras minúsculas por meio de:

```python
.lower()
```

Dessa forma, comandos como `stop`, `STOP` ou `Stop` podem ser reconhecidos da mesma maneira.

Quando o comando informado é `stop`, o evento de encerramento é sinalizado:

```python
encerrar.set()
```

O objeto utilizado para essa comunicação é:

```python
encerrar = threading.Event()
```

A thread de monitoramento verifica esse evento e encerra sua execução quando ele estiver definido.

Essa estrutura permite que o programa continue monitorando o diretório enquanto aguarda, simultaneamente, o comando do usuário para finalizar a execução.

---

# Sistema de logging

O projeto utiliza o módulo `logging` da biblioteca padrão do Python.

A configuração utiliza um `Logger` e um `RotatingFileHandler`:

```python
logger = logging.getLogger()
logger.setLevel(logging.INFO)
```

O handler é configurado para gravar os registros em:

```text
logs
```

com limite de tamanho e quantidade de arquivos de backup:

```python
arquivo_logger = RotatingFileHandler(
    filename='logs',
    maxBytes=5_248_00,
    backupCount=5,
    encoding='utf-8'
)
```

O handler é conectado ao logger:

```python
logger.addHandler(arquivo_logger)
```

---

## Formatação dos logs

Os registros utilizam:

```python
logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%d/%m/%Y | %H:%M:%S'
)
```

Dessa forma, os eventos são registrados contendo:

1. Data e horário;
2. Nível do evento;
3. Mensagem descritiva.

Exemplo:

```text
03/09/2026 | 10:23:15 | INFO | Arquivo adicionado: relatorio.txt
```

---

## Rotação dos arquivos de log

O projeto utiliza `RotatingFileHandler` para evitar que um único arquivo de log cresça indefinidamente.

A configuração estabelece:

- `maxBytes`: tamanho máximo definido para o arquivo antes da rotação;
- `backupCount=5`: quantidade de arquivos de backup mantidos;
- `encoding='utf-8'`: codificação utilizada para os registros.

Quando o limite é atingido durante a geração de um novo registro, o handler realiza a rotação dos arquivos.

A estrutura pode assumir a forma:

```text
logs
logs.1
logs.2
logs.3
...
```

---

# Exceção personalizada

O projeto possui uma exceção personalizada:

```python
class DiretorioInexistente(Exception):
    pass
```

Antes de iniciar o monitoramento, o sistema verifica se o diretório informado existe:

```python
if os.path.exists(diretorio):
```

Caso contrário, a exceção é levantada:

```python
raise DiretorioInexistente
```

e tratada pelo bloco:

```python
except DiretorioInexistente:
    print('Esse diretório não existe.')
```

Essa abordagem permite tratar explicitamente a ausência do diretório informado.

---

# Métricas e relatório

Ao finalizar o monitoramento, o sistema calcula métricas relacionadas aos eventos identificados:

```python
adicionados_num = len(arquivos_adicionados)
removidos_num = len(arquivos_removidos)
renomeados_num = len(arquivos_renomeados)
```

Também calcula o tempo de execução e obtém o nome do diretório monitorado.

Ao final, um relatório é apresentado no terminal contendo:

```text
===================================

RELATÓRIO DE MONITORAMENTO

===================================

| Diretório monitorado: exemplo
| Total de arquivos monitorados: 10
| Arquivos adicionados: 2
| Arquivos removidos: 1
| Arquivos renomeados: 1
| Tempo em monitoramento: 00:05:32
| Último evento: ...
```

O último evento registrado também é recuperado do arquivo de log.

---

# Conceitos praticados

Este projeto reúne diversos conceitos importantes de desenvolvimento em Python:

### Manipulação do sistema de arquivos

- `os.listdir()`
- `os.path.join()`
- `os.path.basename()`
- `os.path.exists()`
- `os.stat()`

### Estruturas de dados

- Listas
- Dicionários
- Conjuntos (`set`)

### Controle de fluxo

- `while`
- `if`
- `for`
- `break`
- `continue`

### Tratamento de exceções

- Exceções personalizadas
- `try/except`
- `raise`

### Concorrência

- `threading.Thread`
- `threading.Event`
- `start()`
- `join()`

### Logging

- `Logger`
- `Handler`
- `Formatter`
- `RotatingFileHandler`
- níveis de log
- rotação de arquivos

### Métricas

- Contagem de eventos
- Medição de tempo de execução
- Geração de relatório

---

# Fluxo de execução

1. Solicita o caminho do diretório ao usuário.
2. Verifica se o diretório existe.
3. Inicializa as estruturas necessárias para armazenar eventos e identificadores.
4. Cria as threads de monitoramento e encerramento.
5. Obtém o estado inicial do diretório.
6. Aguarda cinco segundos.
7. Obtém o estado atual do diretório.
8. Compara os dois estados.
9. Registra arquivos adicionados e removidos.
10. Compara identificadores para detectar renomeações.
11. Registra os eventos utilizando o sistema de logging.
12. Verifica se o usuário solicitou o encerramento.
13. Ao finalizar, calcula as métricas.
14. Apresenta o relatório de monitoramento.

---

# Como executar

## Requisitos

- Python 3.x
- Sistema operacional Windows
- Um diretório existente para ser monitorado

## Execução

No terminal, execute:

```bash
python observador.py
```

Em seguida, informe o caminho do diretório:

```text
C:\Users\Usuario\Documents\teste
```

Para finalizar:

```text
Digite "stop" para encerrar:
```

Digite:

```text
stop
```

Após o encerramento, o relatório será exibido no terminal.

---

# Estrutura do projeto

```text
monitoramento-diretorio/
│
├── observador.py
├── logs
└── README.md
```

O arquivo `observador.py` contém a implementação do monitoramento, enquanto `logs` armazena os eventos registrados durante a execução.

---

# Objetivo de aprendizado

O projeto foi desenvolvido com foco no aprendizado prático de conceitos fundamentais de Python e na aplicação desses conceitos em um problema próximo de cenários reais de observabilidade.

Além da manipulação de arquivos, o projeto permite estudar conceitos como **monitoramento de estado, registro de eventos, concorrência, tratamento de exceções e coleta de métricas**.

A implementação também serviu como exercício para compreender a relação entre `Logger`, `Handler` e `Formatter`, além do funcionamento da rotação de arquivos utilizando `RotatingFileHandler`.

---

# Próximos passos

Possíveis evoluções para o projeto incluem:

- Melhorar a precisão das métricas coletadas.
- Separar configuração, monitoramento e geração do relatório em módulos distintos.
- Aprimorar o tratamento de erros durante alterações no diretório.
- Substituir verificações periódicas por mecanismos de monitoramento de eventos do sistema operacional.
- Adicionar testes automatizados.
- Criar uma interface de dashboard para visualização das métricas.
- Estruturar o projeto para facilitar manutenção e expansão.

---

## Status

**Projeto em desenvolvimento / estudo.**

A implementação atual representa uma versão funcional voltada ao aprendizado de Python, monitoramento de arquivos, logging, concorrência e conceitos introdutórios de observabilidade.
