# Triagem Semântica Local — Instagram, Marketing Digital e Assuntos Estudantis

Ferramenta em Python para apoiar a triagem de referências científicas sobre **Instagram como ferramenta de marketing digital em centros de assuntos estudantis (CAEST)**. Utiliza Sentence Transformers e o modelo multilíngue MiniLM para comparar títulos e resumos com protótipos temáticos, aplicar regras de elegibilidade e gerar uma planilha Excel auditável.

**Versão documentada: V4.3**, identificada no código fornecido. O arquivo de origem e o nome do script ainda mencionam V3; este README descreve a implementação presente no bloco “Versão Melhorada”.

> A classificação é um apoio à revisão humana. Similaridade semântica não é probabilidade de inclusão, avaliação de qualidade metodológica nem confirmação de que um artigo atende ao protocolo da pesquisa.

## Sumário

- [Objetivo e escopo](#objetivo-e-escopo)
- [Recursos implementados](#recursos-implementados)
- [Organização dos arquivos](#organização-dos-arquivos)
- [Requisitos e instalação](#requisitos-e-instalação)
- [Preparação dos dados](#preparação-dos-dados)
- [Execução](#execução)
- [Método de classificação](#método-de-classificação)
- [Planilha de resultados](#planilha-de-resultados)
- [Configuração e adaptação](#configuração-e-adaptação)
- [Uso na revisão bibliográfica](#uso-na-revisão-bibliográfica)
- [Limitações e divergências dos anexos](#limitações-e-divergências-dos-anexos)
- [Solução de problemas](#solução-de-problemas)
- [Reprodutibilidade e contribuição](#reprodutibilidade-e-contribuição)
- [Autoria, licença e fontes](#autoria-licença-e-fontes)

## Objetivo e escopo

O projeto organiza referências recuperadas previamente em buscas bibliográficas, inclusive arquivos preparados a partir do Findpapers. A entrada efetiva é um CSV local: não há integração de busca implementada neste script.

A análise combina cinco eixos: Instagram, assuntos estudantis, marketing, redes sociais e promoção. Seu objetivo é distinguir proximidade temática, categoria semântica, elegibilidade sugerida e utilidade teórica.

Não há quantidade fixa de artigos no código. Todas as linhas lidas são mantidas na aba principal, inclusive registros fora do escopo e duplicatas. As demais abas são recortes dessa mesma base.

## Recursos implementados

- Leitura de CSV com identificação automática das colunas de título e resumo.
- Preservação das colunas originais, salvo colisões com os nomes das colunas geradas.
- Embeddings normalizados de artigos, frases e protótipos em português, inglês e espanhol.
- Categorias A1, A2, B, C e D, com possibilidade de `FORA_DO_ESCOPO`.
- Classificação interna do papel dos cinco eixos.
- Dimensão composta de marketing e promoção.
- Relevância temática numérica e qualitativa.
- Verificação de consistência entre categoria e eixos.
- Sinalização de possíveis falsos positivos e falsos negativos.
- Extração de trechos próximos aos eixos Instagram, assuntos estudantis e marketing/promoção.
- Exportação de nove abas em Excel.

O script não usa API de IA generativa nem exige chave de API. O carregamento inicial do modelo pode exigir internet; a inferência dos textos ocorre localmente. Para execução sem rede, os arquivos do modelo precisam estar disponíveis no cache ou em uma pasta local previamente preparada.

## Organização dos arquivos

Organização sugerida, seguindo os caminhos dos anexos:

| Caminho | Finalidade |
|---|---|
| `README.md` | Documentação do projeto |
| `.venv-triagem/` | Ambiente virtual local; não versionar |
| `resultados/triagem_semantica_local_v3_assuntos_estudantis.py` | Script com o código V4.3 |
| `resultados/artigos.csv` | Base de entrada |
| `resultados/triagem_semantica_local_final.xlsx` | Resultado gerado |

**Preparação inicial:** copie o bloco Python completo da seção “Versão Melhorada” do documento de origem para o arquivo `.py` indicado. Os anexos são documentos Markdown; este README não pressupõe que o script já tenha sido extraído ou publicado.

O nome legado do script foi mantido nos comandos para corresponder ao material fornecido. Ele pode ser renomeado, desde que os comandos de execução sejam ajustados.

## Requisitos e instalação

### Ambiente registrado nos anexos

| Componente | Versão registrada | Uso |
|---|---|---|
| Python | 3.11.16 | Interpretador; comandos usam Python 3.11 |
| NumPy | 1.26.4 | Operações vetoriais |
| PyTorch | 2.2.2 | Execução do modelo |
| Transformers | 4.40.2 | Infraestrutura de modelos |
| Sentence Transformers | 2.7.0 | Embeddings e carregamento do MiniLM |
| pandas | Não fixada | Leitura e transformação dos dados |
| openpyxl | Não fixada | Escrita do Excel |

Essas versões reproduzem a configuração descrita nos documentos; não representam uma matriz de compatibilidade testada em todos os sistemas. A instalação não foi executada como parte da elaboração deste README. A disponibilidade de pacotes depende do sistema operacional e da arquitetura.

### 1. Criar o ambiente virtual

Com Python 3.11 já instalado, execute no terminal macOS/Linux:

```bash
mkdir -p ~/findpapers/resultados
cd ~/findpapers
python3.11 -m venv .venv-triagem
source .venv-triagem/bin/activate
```

### 2. Instalar as dependências

Use o interpretador do ambiente explicitamente para evitar interferência de aliases ou de outro Python:

```bash
./.venv-triagem/bin/python -m pip install --upgrade pip setuptools wheel
./.venv-triagem/bin/python -m pip install \
  "numpy==1.26.4" \
  "torch==2.2.2" \
  "transformers==4.40.2" \
  "sentence-transformers==2.7.0" \
  pandas openpyxl
./.venv-triagem/bin/python -m pip check
```

A instalação explícita de `sentence-transformers` foi incluída aqui porque o anexo verifica sua importação, mas não apresenta o comando de instalação correspondente.

### 3. Verificar o ambiente

```bash
./.venv-triagem/bin/python - <<'PY'
import sys
import numpy
import torch
import transformers
import sentence_transformers
import pandas
import openpyxl

print("Executável:", sys.executable)
print("Python:", sys.version)
for module in (numpy, torch, transformers, sentence_transformers, pandas, openpyxl):
    print(f"{module.__name__}: {module.__version__}")
print("MPS disponível:", torch.backends.mps.is_available())
PY
```

Os atributos corretos para consultar as versões são `__version__`. A disponibilidade de MPS depende do equipamento e do ambiente; `False` não impede a execução em CPU. O script original não fixa o dispositivo de processamento.

### 4. Carregar o modelo

```bash
./.venv-triagem/bin/python - <<'PY'
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("MODELO OK")
print("Limite configurado de tokens:", model.max_seq_length)
PY
```

O primeiro carregamento pode levar mais tempo por envolver download. Esse teste verifica o carregamento, não a validade científica dos critérios de classificação.

## Preparação dos dados

Salve o arquivo como `artigos.csv`, na mesma pasta do script, usando codificação UTF-8 e separador vírgula. A leitura usa `encoding="utf-8-sig"`, que também aceita o marcador BOM de arquivos UTF-8.

| Conteúdo | Cabeçalhos reconhecidos | Obrigatoriedade |
|---|---|---|
| Título | `title`, `titulo`, `título`, `article title` | Coluna obrigatória |
| Resumo | `abstract`, `resumo`, `summary` | Coluna opcional |
| Outros metadados | Nomes livres, como `doi`, `year`, `authors` | Opcionais; preservados |

A função procura primeiro correspondências exatas, ignorando maiúsculas/minúsculas e espaços nas extremidades; depois, tenta correspondências parciais. Cabeçalhos ambíguos devem ser revisados antes da execução.

Exemplo **fictício**, apenas para ilustrar o formato:

```csv
title,abstract,year
"Instagram e serviços estudantis","Estudo sobre divulgação de serviços de apoio ao estudante pelo Instagram.",2026
"Redes sociais no ensino","Uso de plataformas sociais em atividades pedagógicas.",2025
```

Coloque entre aspas campos que contenham vírgulas. Não utilize esse exemplo como evidência científica nem como validação da classificação.

Se não houver coluna de resumo, o programa continua, mas o código atual utiliza a coluna de título também como resumo e acaba duplicando o título no texto analisado. Essa particularidade está registrada nas limitações.

## Execução

Com o CSV e o script preparados:

```bash
cd ~/findpapers/resultados
~/findpapers/.venv-triagem/bin/python \
  ~/findpapers/resultados/triagem_semantica_local_v3_assuntos_estudantis.py
```

Saída efetivamente definida no código:

```text
~/findpapers/resultados/triagem_semantica_local_final.xlsx
```

Os caminhos de entrada e saída são calculados a partir da localização do script (`Path(__file__).resolve().parent`), não do diretório atual do terminal. Não há argumentos de linha de comando implementados.

Uma nova execução sobrescreve a planilha de mesmo nome. Preserve uma cópia antes de executar novamente se houver decisões humanas adicionadas ao arquivo.

## Método de classificação

### 1. Preparação e embeddings

O programa normaliza espaços, combina título e resumo e divide o texto em frases com uma expressão regular baseada em `.`, `!` e `?`. Frases com até 15 caracteres são descartadas nessa etapa; se nenhuma restar, o texto completo é usado como alternativa.

Artigos, frases e protótipos são convertidos em vetores normalizados. O produto escalar desses vetores equivale à similaridade de cosseno. Para cada eixo, categoria e contexto negativo, o score do artigo é a **média das três maiores similaridades com seus protótipos**; se houver menos de três, usa-se a média dos disponíveis.

### 2. Eixos e papéis

| Eixo interno | Conteúdo representado |
|---|---|
| `INSTAGRAM` | Uso do Instagram como ferramenta ou objeto de estudo |
| `ASSUNTOS_ESTUDANTIS` | Assistência, serviços e apoio ao estudante |
| `MARKETING` | Marketing digital, estratégias e marketing de serviços |
| `REDES_SOCIAIS` | Plataformas sociais e estratégias de mídias sociais |
| `PROMOÇÃO` | Divulgação, comunicação institucional, outreach e engajamento |

As regras são aplicadas nesta ordem:

| Papel | Condição |
|---|---|
| `CENTRAL` | Score ≥ 0,52 **e** score ≥ média dos cinco eixos + 0,035 |
| `SECUNDÁRIO` | Não classificado como central e score ≥ 0,43 |
| `INCIDENTAL` | Score ≥ 0,36 e abaixo de 0,43 |
| `AUSENTE` | Score < 0,36 |

Mesmo com score acima de 0,52, um eixo pode ser secundário caso não cumpra a margem relativa. Os cinco papéis são calculados internamente, mas apenas Instagram e assuntos estudantis têm o papel exportado explicitamente.

### 3. Marketing/promoção e relevância temática

Definindo `I` como Instagram, `AE` como assuntos estudantis e `R` como redes sociais:

```text
MP = máximo(score MARKETING, score PROMOÇÃO)
Relevância temática = (I + AE + MP) / 3
```

| Grau | Intervalo do score temático |
|---|---|
| `MUITO ALTA` | ≥ 0,50 |
| `ALTA` | ≥ 0,43 e < 0,50 |
| `MÉDIA` | ≥ 0,36 e < 0,43 |
| `BAIXA` | < 0,36 |

O máximo permite que promoção contribua mesmo sem forte proximidade com o termo marketing. Os scores não são porcentagens nem probabilidades calibradas. O grau de relevância, isoladamente, não determina a elegibilidade.

### 4. Categorias e regras de ajuste

| Categoria | Significado temático dos protótipos |
|---|---|
| `A1` | Instagram como objeto principal em assuntos estudantis para marketing/promoção |
| `A2` | Instagram como canal de uma estratégia mais ampla de redes sociais em assuntos estudantis |
| `B` | Redes sociais e marketing/promoção em assuntos estudantis |
| `C` | Instagram e assuntos estudantis sem foco específico em marketing |
| `D` | Marketing/promoção em assuntos estudantis sem Instagram |
| `FORA_DO_ESCOPO` | Score global de assuntos estudantis abaixo do limiar mínimo |

A categoria bruta é aquela com maior score de similaridade aos protótipos. Em seguida, aplicam-se os ajustes:

1. Se `AE < 0,36`, a categoria final passa a `FORA_DO_ESCOPO`.
2. Caso contrário, se a categoria bruta for A1, redes sociais tiver papel central ou secundário e Instagram não for central, a categoria final passa a A2.
3. Caso contrário, se a categoria bruta for D e `I ≥ 0,36`, a categoria final passa a C.
4. Nos demais casos, mantém-se a categoria bruta.

A regra A1 → A2 usa os **papéis dos eixos**; não compara diretamente se o score de redes sociais é maior que o de Instagram. As descrições das categorias expressam a intenção dos protótipos, não garantias de atendimento a todos os critérios.

### 5. Consistência

Cada requisito abaixo corresponde a score ≥ 0,36:

| Categoria | Requisitos avaliados |
|---|---|
| A1 | I, AE, MP |
| A2 | I, AE, R, MP |
| B | AE, R, MP |
| C | I, AE |
| D | AE, MP |

Todos atendidos: `CONSISTENTE`. Pelo menos metade, mas não todos: `PARCIAL`. Menos da metade: `INCONSISTENTE`. Registros fora do escopo recebem `INCONSISTENTE`.

Essa verificação não exige Instagram central em A1, não testa ausência de marketing em C e não testa ausência de Instagram em D. Portanto, consistência tem o significado restrito dessas regras.

### 6. Possíveis falsos positivos e negativos

São comparados três contextos negativos: `ENSINO`, `MARKETING_INSTITUCIONAL` e `COMPORTAMENTO_ESTUDANTIL`.

```text
Falso positivo provável = SIM quando:
maior score de contexto negativo > AE + 0,05
E AE < 0,43

Falso negativo provável = SIM quando:
AE < 0,36
E melhor similaridade de um trecho com um protótipo de AE ≥ 0,43
```

O score do melhor trecho é um **máximo**, enquanto o score global de AE usa a média das três melhores correspondências. São medidas diferentes. Esses indicadores sinalizam casos para leitura; não demonstram erros confirmados.

### 7. Trechos de apoio

Para Instagram, assuntos estudantis e marketing/promoção, seleciona-se a frase com a maior similaridade a qualquer protótipo do grupo. Ela é exportada quando atinge 0,36; caso contrário, o campo fica vazio.

Os trechos são extraídos do título e do resumo fornecidos. Não são justificativas geradas por um modelo de linguagem e não comprovam, sozinhos, o atendimento ao protocolo de inclusão.

### 8. Elegibilidade e utilidade

| Categoria/condição | Elegibilidade inicial | Utilidade teórica |
|---|---|---|
| A1 ou A2 consistente | `ELEGÍVEL` | `NÚCLEO PRINCIPAL` |
| A1 ou A2 parcial/inconsistente | `POTENCIALMENTE_ELEGÍVEL` | `NÚCLEO PRINCIPAL` |
| B | `POTENCIALMENTE_ELEGÍVEL` | `RELACIONADO` |
| C | `REVISÃO_HUMANA` | `RELACIONADO` |
| D | `NÃO_ELEGÍVEL` | `CONTEXTUAL (FUNDAMENTAÇÃO)` |
| Fora do escopo | `NÃO_ELEGÍVEL` | `DESCARTAR` |

Depois dessa atribuição:

- Falso positivo provável muda `ELEGÍVEL` ou `POTENCIALMENTE_ELEGÍVEL` para `REVISÃO_HUMANA`.
- Falso negativo provável força `REVISÃO_HUMANA`; quando fora do escopo, sua utilidade passa a `REVISÃO DE POSSÍVEL FALSO NEGATIVO`.

Esses ajustes não alteram novamente a categoria final. Um registro pode estar simultaneamente em `FORA_DO_ESCOPO` e `REVISÃO_HUMANA`.

## Planilha de resultados

### Abas geradas

| Aba | Conteúdo |
|---|---|
| `Triagem Completa` | Todas as linhas e todas as colunas geradas, na ordem da entrada |
| `Matriz de Decisão` | Colunas selecionadas, ordenadas por relevância temática decrescente |
| `Elegíveis` | Elegibilidade `ELEGÍVEL` |
| `Potenciais` | Elegibilidade `POTENCIALMENTE_ELEGÍVEL` |
| `Revisão Humana` | Elegibilidade `REVISÃO_HUMANA` |
| `Falsos Positivos` | Indicador de falso positivo provável igual a `SIM` |
| `Falsos Negativos` | Indicador de falso negativo provável igual a `SIM` |
| `Contextuais` | Categoria final D |
| `Fora do Escopo` | Categoria final `FORA_DO_ESCOPO` |

As abas se sobrepõem: não some suas contagens para obter o número de artigos. Use `Triagem Completa` como base consolidada. Não há abas separadas de núcleo principal ou relacionados nesta implementação.

### Dicionário das colunas adicionadas

| Coluna | Interpretação |
|---|---|
| `Relevância temática (Score)` | Média de I, AE e MP, arredondada a quatro casas |
| `Relevância temática (Grau)` | Faixa qualitativa calculada antes do arredondamento |
| `Categoria Semântica Bruta` | Categoria mais próxima antes das regras |
| `Categoria Final` | Categoria após os ajustes estruturais |
| `Motivo da decisão` | Registro textual da manutenção ou reclassificação; pode incluir alerta de falso negativo |
| `Elegibilidade` | Encaminhamento automático após os ajustes |
| `Utilidade teórica` | Papel sugerido na revisão |
| `Falso Positivo Provável` | Sinalizador `SIM`/`NÃO` |
| `Falso Negativo Provável` | Sinalizador `SIM`/`NÃO` |
| `Contexto negativo dominante` | Contexto negativo com maior score, mesmo quando o alerta é `NÃO` |
| `Score contexto negativo` | Score do contexto negativo dominante |
| `Consistência` | Atendimento aos requisitos mínimos da categoria |
| `INSTAGRAM (Papel/Score)` | Papel e score de Instagram em um campo textual |
| `ASSUNTOS_EST. (Papel/Score)` | Papel e score de assuntos estudantis em um campo textual |
| `Score melhor trecho Assuntos Est.` | Maior correspondência local aos protótipos de AE |
| `MARKETING/PROMO (Score Max)` | Máximo entre os scores de marketing e promoção |
| `REDES_SOCIAIS (Score)` | Score do eixo redes sociais |
| `Trecho mais próximo: Assuntos Est.` | Frase selecionada para AE |
| `Trecho mais próximo: Instagram` | Frase selecionada para Instagram |
| `Trecho mais próximo: Mkt/Promo` | Frase selecionada para marketing/promoção |

`Consistência` está na aba completa, mas não na seleção da `Matriz de Decisão`. O motivo textual não descreve necessariamente todos os ajustes de elegibilidade, especialmente o alerta de falso positivo; consulte também as colunas de sinalização.

## Configuração e adaptação

Os principais parâmetros ficam no início do script:

```python
INPUT_FILE = BASE_DIR / "artigos.csv"
OUTPUT_FILE = BASE_DIR / "triagem_semantica_local_final.xlsx"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

AXIS_PRESENT = 0.36
AXIS_SECONDARY = 0.43
AXIS_CENTRAL = 0.52
CENTRAL_MARGIN = 0.035
```

Para adaptar o tema, revise em conjunto `AXES`, `CATEGORIES`, `NEGATIVE_CONTEXTS`, as regras de consistência e as regras de elegibilidade. Alterar somente os nomes dos eixos não adapta a lógica.

Para arquivos com separador ponto e vírgula, ajuste a leitura:

```python
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig", sep=";")
```

Os tamanhos de lote definidos são 16 artigos e 32 frases. Em caso de memória insuficiente, reduza os valores `batch_size` nas chamadas de `model.encode`.

Os limites de relevância temática (`0.50`, `0.43`, `0.36`) e a margem de contexto negativo (`0.05`) aparecem diretamente na lógica. Alterar as constantes dos eixos não atualiza automaticamente todos esses valores.

## Uso na revisão bibliográfica

1. Defina os critérios de inclusão e exclusão antes de interpretar os resultados.
2. Revise a qualidade dos títulos e resumos; resolva duplicatas conforme o protocolo.
3. Execute a triagem e registre a configuração utilizada.
4. Priorize `Revisão Humana`, incluindo possíveis falsos negativos fora do escopo.
5. Confira os candidatos elegíveis com leitura humana e, quando necessário, texto completo.
6. Avalie uma amostra dos não elegíveis para investigar exclusões indevidas.
7. Registre decisões humanas separadamente dos resultados automáticos.

Sugestão de campos manuais, **não criados pelo script**: `Incluir?`, `Motivo da exclusão`, `Revisor`, `Data da revisão`, `Tipo de estudo`, `Objetivo`, `Método`, `Resultados` e `Limitações`.

Para avaliar o método, compare a saída com uma amostra rotulada por revisores e examine erros por categoria. Os anexos não apresentam métricas de precisão, revocação ou validação dos limiares.

## Limitações e divergências dos anexos

### Divergências de documentação resolvidas neste README

| Descrição encontrada | Comportamento do código fornecido |
|---|---|
| Documento e script identificados como V3 | Cabeçalho e mensagem final identificam V4.3 |
| Saída `triagem_semantica_local_v3_assuntos_estudantis.xlsx` | Saída real: `triagem_semantica_local_final.xlsx` |
| Eixo chamado CAEST | Chave interna: `ASSUNTOS_ESTUDANTIS` |
| `INCLUIR`, `DÚVIDA`, `EXCLUIR` | Usa os quatro estados de elegibilidade descritos acima |
| Relação direta/indireta, confiança e prioridade de leitura | Não exportadas pelo código |
| Papéis explícitos para todos os eixos | Apenas I e AE exportam papel; demais dados são parciais/compostos |
| Abas de núcleo principal e relacionados | Classificações na coluna de utilidade, sem abas próprias |

### Limitações técnicas e metodológicas

- **Ausência de resumo:** o título é duplicado quando não existe coluna de resumo. Corrigir essa alternativa é uma melhoria de código ainda não aplicada aqui.
- **Textos longos:** sujeitos ao limite de tokens do modelo; o script não agrega janelas do artigo para produzir o score global.
- **Dados vazios:** não há validação robusta de CSV sem registros nem de linhas sem título e resumo úteis.
- **Segmentação simples:** abreviações e pontuação podem dividir frases de forma inadequada.
- **Regras heurísticas:** os limiares e protótipos precisam de validação para o corpus; não foram aprendidos com rótulos humanos neste script.
- **Auditoria parcial:** os scores individuais de todas as categorias, contextos e eixos não são integralmente exportados.
- **Duplicatas:** não há deduplicação, e protótipos repetidos podem influenciar a média das três melhores correspondências.
- **Escopo textual:** apenas título e resumo; não há leitura de PDF, coleta de texto completo ou tradução automática.
- **Histórico:** não há comparação automática entre V3 e V4 nem relatório de mudanças entre execuções.
- **Preservação:** colunas originais com os mesmos nomes das colunas geradas terão seus valores substituídos na saída.
- **Apresentação:** o Excel é exportado sem um projeto de formatação, gráficos ou dashboard.

O termo “definitiva” aparece no código de origem, mas não constitui evidência de validação científica ou garantia de ausência de erros.

## Solução de problemas

| Sintoma | Verificação e ação |
|---|---|
| `artigos.csv` não encontrado | Coloque-o ao lado do script ou ajuste `INPUT_FILE` |
| Coluna de título não encontrada | Use um cabeçalho reconhecido; confira também o separador |
| Toda a entrada aparece em uma única coluna | O CSV pode usar `;`; ajuste `sep` |
| `ModuleNotFoundError` | Instale o pacote com o mesmo interpretador usado para executar o script |
| `No matching distribution found` | Confira versão do Python, sistema e arquitetura; o ambiente documentado utiliza Python 3.11 |
| Erro de compatibilidade binária NumPy/PyTorch | Confira se o ambiente corresponde às versões registradas; evite misturar instalações |
| Alias direciona para outro Python | Use `~/findpapers/.venv-triagem/bin/python` explicitamente |
| Erro ao baixar ou carregar o modelo | Confira rede, cache e disponibilidade local dos arquivos do modelo |
| Aviso sobre `resume_download` | O anexo registra esse aviso seguido de `MODELO OK`; diferencie aviso de exceção que interrompe a execução |
| `MPS disponível: False` | Não representa, isoladamente, falha; verifique a execução em CPU |
| Memória insuficiente | Reduza os lotes de artigos e frases |
| Erro ao salvar Excel | Confira permissão de escrita e se outro aplicativo está bloqueando o arquivo |
| Falha com base vazia | Forneça um CSV com registros válidos; o código não trata esse caso de forma robusta |

## Reprodutibilidade e contribuição

Para cada execução relevante, preserve o CSV original, uma cópia do script, a planilha, a data e as versões das dependências. Registre também qualquer alteração nos protótipos e limiares. O modelo é carregado pelo nome, sem revisão fixada no código.

Depois de validar o ambiente, registre as dependências resolvidas:

```bash
cd ~/findpapers
./.venv-triagem/bin/python -m pip freeze > requirements-lock.txt
```

Sugestão de `.gitignore` a criar no repositório:

```gitignore
.venv-triagem/
__pycache__/
*.pyc
.DS_Store
```

Decida separadamente se os CSVs e resultados podem ser publicados, conforme as permissões das fontes. Para contribuições, descreva a regra alterada, apresente exemplos de seu impacto e verifique se o total de linhas da aba completa continua igual ao da entrada.

Melhorias possíveis: corrigir a duplicação de títulos, validar entradas vazias, exportar todos os scores, adicionar identificador estável, implementar comparação entre execuções e avaliar o classificador contra decisões humanas. Esses itens são propostas, não funcionalidades existentes.

## Autoria, licença e fontes

**Autoria e licença:** não foram identificadas declarações formais nos anexos. O responsável pelo repositório deve definir a autoria e adicionar um arquivo `LICENSE` antes de declarar uma licença de distribuição.

Documentação elaborada a partir de:

1. **06 Semantica Local CAEST Com Transformer e MiniLM - V3 Prompt.md** — código da seção “Versão Melhorada”, identificado internamente como V4.3.
2. **Instalação e configuração modelo MiniLM local.md** — comandos de preparação do ambiente e versões registradas.

Esta documentação resulta da leitura dos arquivos e da análise estática do código. Não afirma que o modelo foi executado, que um corpus foi processado ou que os resultados foram validados empiricamente durante sua elaboração.
