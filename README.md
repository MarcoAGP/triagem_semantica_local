# Triagem Semântica Local — Instagram e Assuntos Estudantis

Triagem assistida de referências bibliográficas sobre **Instagram, marketing digital e assuntos estudantis**, com processamento local em Python e embeddings do modelo **paraphrase-multilingual-MiniLM-L12-v2**.

O programa lê títulos e resumos de um CSV, calcula proximidades semânticas, aplica regras de classificação e gera uma planilha Excel para auditoria e revisão humana. O escopo inclui serviços de apoio e assistência ao estudante, com aplicação em pesquisas sobre Centros de Assuntos Estudantis (CAEST).

> A classificação é uma sugestão heurística. Similaridade semântica não é probabilidade de elegibilidade nem comprovação de que um estudo atende aos critérios de uma revisão. A decisão científica final depende da leitura e avaliação do pesquisador.

## Sumário

- [Arquivos do repositório](#arquivos-do-repositório)
- [Funcionalidades](#funcionalidades)
- [Base de dados](#base-de-dados)
- [Instalação](#instalação)
- [Execução](#execução)
- [Como a classificação funciona](#como-a-classificação-funciona)
- [Planilha de saída](#planilha-de-saída)
- [Configuração](#configuração)
- [Revisão humana e reprodutibilidade](#revisão-humana-e-reprodutibilidade)
- [Limitações conhecidas](#limitações-conhecidas)
- [Solução de problemas](#solução-de-problemas)
- [Contribuições e licença](#contribuições-e-licença)

## Arquivos do repositório

| Arquivo                                                                                                  | Finalidade                                                |
| -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `README.md`                                                                                              | Documentação do projeto                                   |
| [`artigos.csv`](artigos.csv)                                                                             | Referências bibliográficas usadas como entrada            |
| [`triagem_semantica_local_v3_assuntos_estudantis.py`](triagem_semantica_local_v3_assuntos_estudantis.py) | Script de processamento e exportação                      |
| `triagem_semantica_local_final.xlsx`                                                                     | Saída gerada pela execução; não é necessária para iniciar |

Mantenha o CSV e o script **na mesma pasta**. Os caminhos de entrada e saída são resolvidos a partir da localização do próprio script, e não da pasta atual do terminal.

Esta documentação descreve o arquivo Python fornecido, identificado como **V3**. Exemplos conceituais dos materiais de apoio não representam necessariamente colunas ou recursos implementados.

## Funcionalidades

- Análise conjunta de título e resumo, preservando os metadados de entrada na aba principal.
- Comparação com protótipos textuais em português, inglês e espanhol.
- Avaliação de cinco eixos: Instagram, assuntos estudantis, marketing, redes sociais e promoção.
- Classificação semântica bruta A1/A2/B/C/D, com ajustes estruturais e categoria `FORA_DO_ESCOPO`.
- Separação entre relevância temática, elegibilidade e utilidade teórica.
- Verificação de consistência entre categoria e presença dos eixos.
- Sinalização de possíveis falsos positivos e falsos negativos.
- Extração de trechos próximos aos conceitos de Instagram, assuntos estudantis e marketing/promoção.
- Exportação de nove abas em Excel.

O programa não faz busca bibliográfica, download de PDFs, tradução ou treinamento de um modelo. Ele analisa os metadados já reunidos no CSV. Não utiliza a API do Gemini nem exige chave de API para essa análise.

## Base de dados

### Retrato do arquivo fornecido

A inspeção do CSV anexado para esta documentação identificou:

| Indicador            | Quantidade |
| -------------------- | ---------: |
| Registros            |        822 |
| Colunas              |         17 |
| Títulos vazios       |          0 |
| Resumos vazios       |        207 |
| DOI vazio            |        109 |
| Idioma não informado |        587 |

Esses números descrevem a entrada, **não resultados da classificação**. Não representam necessariamente 822 estudos únicos: o script não remove duplicatas. Ao substituir o CSV, os totais podem mudar.

### Dicionário de dados

| Coluna             | Conteúdo                                  | Utilização pelo script                             |
| ------------------ | ----------------------------------------- | -------------------------------------------------- |
| `title`            | Título                                    | Texto analisado; coluna obrigatória ou equivalente |
| `authors`          | Autores                                   | Preservado                                         |
| `publication_date` | Data de publicação                        | Preservado                                         |
| `doi`              | Identificador DOI                         | Preservado                                         |
| `url`              | Página do artigo                          | Preservado                                         |
| `pdf_url`          | Endereço do PDF                           | Preservado; não é acessado                         |
| `language`         | Idioma informado                          | Preservado; não seleciona o modelo                 |
| `paper_type`       | Tipo de publicação                        | Preservado                                         |
| `keywords`         | Palavras-chave                            | Preservado; não entra no texto analisado           |
| `found_in`         | Fontes de recuperação                     | Preservado                                         |
| `database_count`   | Quantidade de bases registrada na entrada | Preservado                                         |
| `citations`        | Contagem de citações fornecida            | Preservado                                         |
| `is_open_access`   | Indicador de acesso aberto                | Preservado                                         |
| `is_retracted`     | Indicador de retratação                   | Preservado; não gera exclusão automática           |
| `reference_count`  | Contagem de referências fornecida         | Preservado                                         |
| `cited_by_count`   | Contagem de citações recebidas fornecida  | Preservado                                         |
| `abstract`         | Resumo                                    | Texto analisado, quando disponível                 |

As contagens bibliográficas são aceitas como fornecidas; o programa não valida sua atualização, origem ou equivalência entre bases.

### Formato aceito

A leitura utiliza `pd.read_csv(INPUT_FILE, encoding="utf-8-sig")`: separador padrão **vírgula**, cabeçalho e codificação UTF-8, com ou sem BOM. Campos que contêm vírgulas ou quebras de linha precisam estar corretamente delimitados por aspas.

O reconhecimento de colunas primeiro tenta correspondência exata, ignorando maiúsculas/minúsculas e espaços externos; depois procura nomes que contenham os termos candidatos.

| Campo  | Nomes reconhecidos                           |
| ------ | -------------------------------------------- |
| Título | `title`, `titulo`, `título`, `article title` |
| Resumo | `abstract`, `resumo`, `summary`              |

A ausência da coluna de título interrompe a execução. Um resumo vazio é tratado como texto vazio. Se a coluna inteira de resumo estiver ausente, há um comportamento específico descrito em [Limitações conhecidas](#limitações-conhecidas).

## Instalação

### Ambiente de referência

O material de instalação fornecido registra a seguinte combinação. Ela é apresentada como referência histórica do projeto, não como garantia de compatibilidade com todos os sistemas:

| Componente            | Versão registrada                      |
| --------------------- | -------------------------------------- |
| Python                | 3.11, com 3.11.16 relatado no material |
| NumPy                 | 1.26.4                                 |
| PyTorch               | 2.2.2                                  |
| Transformers          | 4.40.2                                 |
| Sentence Transformers | 2.7.0                                  |
| pandas                | Não fixada no material                 |
| openpyxl              | Não fixada no material                 |

É necessário ter Python instalado e espaço para o ambiente e os arquivos do modelo. A disponibilidade dos pacotes depende do sistema operacional, da arquitetura e do interpretador. GPU não é um requisito do script; a seleção de dispositivo é delegada ao Sentence Transformers.

### 1. Obter os arquivos

Baixe ou clone este repositório e abra um terminal na pasta que contém o script e `artigos.csv`. Os comandos abaixo partem dessa pasta. Não é necessário instalar o Findpapers para executar esta etapa de triagem.

### 2. Criar um ambiente isolado

**macOS ou Linux:**

```bash
python3.11 -m venv .venv-triagem
source .venv-triagem/bin/activate
```

**Windows — PowerShell:**

```powershell
py -3.11 -m venv .venv-triagem
.\.venv-triagem\Scripts\Activate.ps1
```

Se a ativação não estiver disponível, use diretamente o executável do ambiente nos comandos posteriores: `.venv-triagem/bin/python` no macOS/Linux ou `.\.venv-triagem\Scripts\python.exe` no Windows.

### 3. Instalar as dependências

Com o ambiente ativo:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install "numpy==1.26.4" "torch==2.2.2" "transformers==4.40.2" "sentence-transformers==2.7.0" pandas openpyxl
python -m pip check
```

`sentence-transformers` é o nome do pacote de instalação; `sentence_transformers` é o nome usado na importação. O `openpyxl` é necessário para escrever o Excel, embora não seja importado diretamente no início do script.

### 4. Conferir o ambiente

```bash
python -c "import sys, torch, numpy, pandas, openpyxl, transformers, sentence_transformers; print('Python:', sys.version); print('Executável:', sys.executable); print('NumPy:', numpy.__version__); print('Torch:', torch.__version__); print('Transformers:', transformers.__version__); print('Sentence Transformers:', sentence_transformers.__version__); print('pandas:', pandas.__version__); print('openpyxl:', openpyxl.__version__)"
```

Use `__version__` para consultar as versões. O atributo `.version` que aparece em exemplos do material de apoio não é a forma equivalente de obter essas strings.

### 5. Preparar o modelo

```bash
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print('MODELO OK'); print('Limite de tokens:', m.max_seq_length)"
```

A primeira carga pode precisar de internet para baixar o modelo. Depois de os arquivos necessários estarem em cache, a inferência é local. O script não inclui chamadas para enviar títulos ou resumos a uma API externa; o carregamento do modelo pode realizar acessos de rede para resolver seus arquivos.

## Execução

Com o ambiente ativo e os dois arquivos na mesma pasta:

```bash
python triagem_semantica_local_v3_assuntos_estudantis.py
```

Alternativa explícita no macOS/Linux:

```bash
.venv-triagem/bin/python triagem_semantica_local_v3_assuntos_estudantis.py
```

Alternativa explícita no Windows:

```powershell
.\.venv-triagem\Scripts\python.exe triagem_semantica_local_v3_assuntos_estudantis.py
```

O terminal informa o carregamento do modelo, mostra barras de progresso da codificação e anuncia o caminho do Excel ao final. O tempo depende do equipamento, do cache do modelo e da quantidade e extensão dos textos.

**Saída:** `triagem_semantica_local_final.xlsx`, na mesma pasta do script. Uma nova execução usa o mesmo nome e pode sobrescrever o resultado anterior. Guarde uma cópia antes de refazer a triagem ou altere `OUTPUT_FILE`.

O programa não aceita argumentos de linha de comando e não solicita seleção interativa de arquivos.

## Como a classificação funciona

### 1. Preparação dos textos

Valores ausentes são convertidos em texto vazio e espaços consecutivos são normalizados. O documento analisado é `título + ". " + resumo`, quando ambos estão preenchidos.

Os trechos são separados pela expressão `(?<=[.!?])\s+`. Apenas trechos com mais de 15 caracteres são mantidos; se nenhum permanecer, o texto completo é usado. Essa separação simples não equivale a um segmentador linguístico completo.

### 2. Embeddings e pontuações

O mesmo modelo codifica documentos, trechos e protótipos. Todos os embeddings são normalizados. O produto escalar entre esses vetores corresponde à similaridade de cosseno.

Para cada eixo, categoria ou contexto negativo, o score global é a **média das três maiores similaridades com seus protótipos**; quando há menos de três, usa-se a média dos disponíveis.

Os trechos locais usam outra regra: a maior similaridade com qualquer protótipo do grupo. Portanto, o score do melhor trecho e o score global não são calculados da mesma maneira.

### 3. Eixos e papéis

| Eixo                  | Conceito representado                                       |
| --------------------- | ----------------------------------------------------------- |
| `INSTAGRAM`           | Uso do Instagram em comunicação e marketing                 |
| `ASSUNTOS_ESTUDANTIS` | Assistência, apoio, serviços e assuntos estudantis          |
| `MARKETING`           | Marketing digital e estratégias de marketing                |
| `REDES_SOCIAIS`       | Plataformas e estratégias de mídias sociais                 |
| `PROMOÇÃO`            | Divulgação, promoção de serviços, comunicação e engajamento |

As regras são avaliadas nesta ordem:

| Papel        | Condição                                                 |
| ------------ | -------------------------------------------------------- |
| `CENTRAL`    | Score ≥ 0,52 **e** score ≥ média dos cinco eixos + 0,035 |
| `SECUNDÁRIO` | Não passou na regra anterior e score ≥ 0,43              |
| `INCIDENTAL` | Não passou nas anteriores e score ≥ 0,36                 |
| `AUSENTE`    | Score < 0,36                                             |

Um eixo com score acima de 0,52 pode continuar `SECUNDÁRIO` se não superar a média pela margem exigida. Os cinco papéis são calculados, mas a saída exporta papel/score explicitamente apenas para Instagram e assuntos estudantis.

### 4. Marketing/promoção e relevância

A dimensão composta é definida por:

```text
MP = máximo(score de MARKETING, score de PROMOÇÃO)
Relevância temática = (score de INSTAGRAM + score de ASSUNTOS_ESTUDANTIS + MP) / 3
```

| Grau         | Intervalo do score temático |
| ------------ | --------------------------- |
| `MUITO ALTA` | ≥ 0,50                      |
| `ALTA`       | ≥ 0,43 e < 0,50             |
| `MÉDIA`      | ≥ 0,36 e < 0,43             |
| `BAIXA`      | < 0,36                      |

Esse score organiza proximidade temática; não determina sozinho a elegibilidade.

### 5. Categorias e ajustes

A categoria bruta é a categoria de maior score entre os protótipos A1–D.

| Categoria | Intenção temática dos protótipos                                                          |
| --------- | ----------------------------------------------------------------------------------------- |
| A1        | Instagram como objeto principal em assuntos estudantis, marketing e promoção              |
| A2        | Instagram como canal de uma estratégia mais ampla de redes sociais em assuntos estudantis |
| B         | Redes sociais, marketing e promoção em serviços estudantis                                |
| C         | Instagram e assuntos estudantis, sem foco específico em marketing                         |
| D         | Marketing e promoção de serviços estudantis sem Instagram                                 |

Em seguida, aplicam-se as regras, nesta ordem:

1. Se assuntos estudantis < 0,36, a categoria final é `FORA_DO_ESCOPO`.
2. Caso contrário, uma categoria bruta A1 vira A2 quando redes sociais é `CENTRAL` ou `SECUNDÁRIO` e Instagram não é `CENTRAL`.
3. Caso contrário, uma categoria bruta D vira C quando Instagram ≥ 0,36.
4. Nos demais casos, mantém-se a categoria bruta.

A regra A1 → A2 não compara diretamente se o score de redes sociais é maior que o de Instagram e não exige explicitamente Instagram ≥ 0,36. A descrição temática das categorias é uma referência conceitual; a verificação de consistência é uma etapa separada.

### 6. Consistência

Cada requisito abaixo é considerado atendido quando seu score é ≥ 0,36:

| Categoria final | Requisitos                                         |
| --------------- | -------------------------------------------------- |
| A1              | Instagram, assuntos estudantis e MP                |
| A2              | Instagram, assuntos estudantis, redes sociais e MP |
| B               | Assuntos estudantis, redes sociais e MP            |
| C               | Instagram e assuntos estudantis                    |
| D               | Assuntos estudantis e MP                           |

Todos atendidos: `CONSISTENTE`. Pelo menos metade: `PARCIAL`. Menos da metade: `INCONSISTENTE`. `FORA_DO_ESCOPO` recebe `INCONSISTENTE` diretamente.

### 7. Alertas e trechos

Os contextos negativos são `ENSINO`, `MARKETING_INSTITUCIONAL` e `COMPORTAMENTO_ESTUDANTIL`. Eles ajudam a identificar artigos próximos ao vocabulário do tema, mas potencialmente distantes do recorte de serviços estudantis.

- **Falso Positivo Provável = SIM:** maior score negativo > score de assuntos estudantis + 0,05, e assuntos estudantis < 0,43.
- **Falso Negativo Provável = SIM:** score global de assuntos estudantis < 0,36, mas o melhor trecho local desse eixo ≥ 0,43.

Para Instagram, assuntos estudantis e MP, o programa exporta o trecho de maior similaridade se ela for ≥ 0,36. Caso contrário, o campo fica vazio. Esses trechos são evidências recuperadas por proximidade, não justificativas causais do modelo nem confirmação do conteúdo do artigo completo.

### 8. Elegibilidade e utilidade

| Categoria/condição             | Elegibilidade inicial     | Utilidade teórica            |
| ------------------------------ | ------------------------- | ---------------------------- |
| A1 ou A2 consistente           | `ELEGÍVEL`                | `NÚCLEO PRINCIPAL`           |
| A1 ou A2 parcial/inconsistente | `POTENCIALMENTE_ELEGÍVEL` | `NÚCLEO PRINCIPAL`           |
| B                              | `POTENCIALMENTE_ELEGÍVEL` | `RELACIONADO`                |
| C                              | `REVISÃO_HUMANA`          | `RELACIONADO`                |
| D                              | `NÃO_ELEGÍVEL`            | `CONTEXTUAL (FUNDAMENTAÇÃO)` |
| Fora do escopo                 | `NÃO_ELEGÍVEL`            | `DESCARTAR`                  |

Depois dessa atribuição:

- Um falso positivo provável muda `ELEGÍVEL` ou `POTENCIALMENTE_ELEGÍVEL` para `REVISÃO_HUMANA`, sem alterar a utilidade.
- Um falso negativo provável recebe `REVISÃO_HUMANA`. Se estiver fora do escopo, sua utilidade passa a `REVISÃO DE POSSÍVEL FALSO NEGATIVO`, mantendo a categoria `FORA_DO_ESCOPO`.

Logo, um artigo pode aparecer simultaneamente em “Fora do Escopo”, “Falsos Negativos” e “Revisão Humana”.

## Planilha de saída

| Aba                 | Conteúdo                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| `Triagem Completa`  | Todos os registros, metadados originais e campos calculados                                          |
| `Matriz de Decisão` | Título, resumo quando disponível e seleção dos campos calculados, em ordem decrescente de relevância |
| `Elegíveis`         | Elegibilidade final `ELEGÍVEL`                                                                       |
| `Potenciais`        | Elegibilidade final `POTENCIALMENTE_ELEGÍVEL`                                                        |
| `Revisão Humana`    | Elegibilidade final `REVISÃO_HUMANA`                                                                 |
| `Falsos Positivos`  | Alerta de falso positivo igual a `SIM`                                                               |
| `Falsos Negativos`  | Alerta de falso negativo igual a `SIM`                                                               |
| `Contextuais`       | Categoria final D                                                                                    |
| `Fora do Escopo`    | Categoria final `FORA_DO_ESCOPO`                                                                     |

As abas são recortes sobrepostos; não some suas contagens para calcular o total de estudos. A aba principal mantém a ordem da entrada; apenas a matriz é explicitamente ordenada por relevância. Abas sem correspondências ainda são gravadas com cabeçalhos.

### Campos acrescentados

| Grupo          | Colunas                                                                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Relevância     | `Relevância temática (Score)`, `Relevância temática (Grau)`                                                                                           |
| Classificação  | `Categoria Semântica Bruta`, `Categoria Final`, `Motivo da decisão`, `Consistência`                                                                   |
| Encaminhamento | `Elegibilidade`, `Utilidade teórica`                                                                                                                  |
| Alertas        | `Falso Positivo Provável`, `Falso Negativo Provável`, `Contexto negativo dominante`, `Score contexto negativo`                                        |
| Eixos          | `INSTAGRAM (Papel/Score)`, `ASSUNTOS_EST. (Papel/Score)`, `Score melhor trecho Assuntos Est.`, `MARKETING/PROMO (Score Max)`, `REDES_SOCIAIS (Score)` |
| Trechos        | `Trecho mais próximo: Assuntos Est.`, `Trecho mais próximo: Instagram`, `Trecho mais próximo: Mkt/Promo`                                              |

São 20 campos calculados adicionais. Com as 17 colunas desta entrada, a aba principal terá 37 colunas se a execução concluir normalmente. A matriz não inclui `Consistência`, embora esse campo esteja na aba principal.

## Configuração

Edite as constantes no início do script:

```python
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "artigos.csv"
OUTPUT_FILE = BASE_DIR / "triagem_semantica_local_final.xlsx"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

AXIS_PRESENT = 0.36
AXIS_SECONDARY = 0.43
AXIS_CENTRAL = 0.52
CENTRAL_MARGIN = 0.035
```

Os dicionários `AXES`, `NEGATIVE_CONTEXTS` e `CATEGORIES` definem os protótipos. Alterar frases, repetições ou categorias muda a pontuação: como a agregação considera os três melhores valores, protótipos repetidos também podem influenciar o resultado.

Os lotes são definidos nas chamadas `model.encode`: 16 documentos e 32 trechos. Reduzi-los pode diminuir o uso de memória durante a codificação, mas o programa ainda mantém embeddings e matrizes em memória.

Os limites do grau de relevância (0,50/0,43/0,36) e a margem de contexto negativo (0,05) estão escritos diretamente na lógica. Alterar apenas as constantes dos eixos não atualiza automaticamente todos esses números.

## Revisão humana e reprodutibilidade

1. Preserve uma cópia do CSV original e registre o commit do script utilizado.
2. Revise registros sem resumo e eventuais duplicatas antes de interpretar os resultados.
3. Inspecione os alertas e compare os trechos com o resumo e, quando necessário, com o texto completo.
4. Confira os candidatos elegíveis segundo critérios explícitos da pesquisa.
5. Registre a decisão humana em uma cópia da planilha, com motivo, responsável e data.
6. Avalie os limiares em uma amostra rotulada por pessoas antes de adotá-los como parte do protocolo.

Para registrar as dependências resolvidas:

```bash
python -m pip freeze > requirements-lock.txt
```

Esse comando cria um arquivo adicional opcional; ele não acompanha necessariamente o repositório. Registre também sistema operacional, arquitetura, versão do Python, dispositivo e revisão do modelo utilizada. O script fixa o nome do modelo, mas não uma revisão específica de seus arquivos.

Uma formulação metodológica possível é: “Foi realizada triagem assistida por similaridade semântica entre títulos/resumos e protótipos temáticos, com regras heurísticas de categorização e encaminhamento para revisão humana.” Não trate os scores como precisão, sensibilidade ou confiança estatisticamente validada sem uma avaliação independente.

## Limitações conhecidas

- **Apenas metadados textuais:** palavras-chave e texto integral não entram na análise. Datas, idioma, tipo de estudo e retratação não são critérios automáticos de exclusão.
- **Ausência da coluna de resumo:** o código atribui `abstract_col = title_col`. Assim, apesar do aviso de análise apenas por títulos, `build_text` concatena o título consigo mesmo. Para analisar uma base sem resumos sem essa duplicação, inclua uma coluna `abstract` vazia no CSV.
- **Textos longos:** estão sujeitos ao limite de tokens do modelo. O script não faz divisão em janelas para o embedding global; consultar `max_seq_length` ajuda a conhecer esse limite. A análise local por trechos não elimina todas as consequências do truncamento.
- **Heurísticas não calibradas:** limiares e protótipos precisam de validação para cada corpus. O contexto negativo dominante é sempre o maior dos três, mesmo quando todos têm baixa similaridade.
- **Dados de entrada:** não há deduplicação, validação de DOI nem tratamento específico para CSV vazio ou registros sem conteúdo útil.
- **Escalabilidade:** todos os textos, embeddings e matrizes são mantidos em memória; a associação dos trechos a cada artigo percorre novamente o mapa de trechos.
- **Auditoria parcial:** os scores de todas as categorias e os scores separados de marketing e promoção não são exportados. O melhor score local de assuntos estudantis é exportado, mas não os scores locais dos outros dois grupos.
- **Escopo da implementação:** não há comparação entre versões V3/V4, tradução, interface gráfica, classificação `INCLUIR/DÚVIDA/EXCLUIR`, coluna de confiança, relação direta/indireta ou prioridade numérica de leitura. Também não há abas próprias chamadas “Núcleo Principal” ou “Relacionados”; essas informações aparecem em `Utilidade teórica`.

A preparação deste README incluiu inspeção estática do script, validação de sua sintaxe e leitura estrutural do CSV. Não incluiu execução da inferência nem validação do desempenho científico do classificador. As versões do ambiente foram extraídas do material de apoio, sem teste de instalação nesta análise.

## Solução de problemas

| Sintoma                                     | Verificação ou ação                                                                                                          |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `artigos.csv não encontrado`                | Coloque o CSV junto ao script ou ajuste `INPUT_FILE`                                                                         |
| Coluna de título não encontrada             | Confira cabeçalho e separador; um CSV com ponto e vírgula exige ajuste de `sep` na leitura                                   |
| `ModuleNotFoundError`                       | Instale os pacotes usando o Python do ambiente virtual                                                                       |
| Instalação feita, mas importação falha      | Confira `sys.executable` e use o caminho explícito do ambiente; aliases do terminal podem apontar para outro Python          |
| `No matching distribution found`            | Verifique versão do Python, arquitetura e disponibilidade de pacote para o sistema; o ambiente de referência usa Python 3.11 |
| Erro de incompatibilidade NumPy/PyTorch     | Recrie o ambiente isolado com a combinação de referência e execute `python -m pip check`                                     |
| Falha ao carregar o modelo                  | Execute primeiro o comando “Preparar o modelo” e confira conexão, cache e permissões                                         |
| Sem aceleração MPS/CUDA                     | O script não exige acelerador; a disponibilidade depende do hardware e da instalação                                         |
| `PermissionError` ao exportar               | Feche o Excel aberto e confira permissão de escrita na pasta                                                                 |
| Processamento lento ou memória insuficiente | Reduza os lotes; avalie uma amostra separada e considere a quantidade de trechos                                             |
| Categorias aparentemente incorretas         | Revise os textos, os limiares, os protótipos e os alertas; não interprete os rótulos como decisões definitivas               |

## Contribuições e licença

Melhorias úteis incluem corrigir o fallback sem resumo, tratar entradas vazias, adicionar parâmetros de linha de comando, exportar todos os scores e avaliar a classificação contra uma amostra humana de referência. Ao propor uma mudança, descreva seu efeito metodológico e compare resultados sobre a mesma entrada.

Nenhum arquivo de licença foi fornecido com os materiais analisados. Defina uma licença em `LICENSE` antes de declarar condições de reutilização do código. A disponibilização dos metadados e resumos deve observar as condições de suas fontes; a licença do código não determina automaticamente os direitos sobre esses textos.
