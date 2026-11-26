#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
TRIAGEM SEMÂNTICA LOCAL — V3 (DEFINITIVA)
============================================================
Tema da revisão:
    Instagram + Marketing Digital + Centro de Assuntos Estudantis
============================================================
"""

from pathlib import Path
import re
import sys
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# ============================================================
# CONFIGURAÇÃO
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "artigos.csv"
OUTPUT_FILE = BASE_DIR / "triagem_semantica_local_final.xlsx"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

AXIS_PRESENT = 0.36
AXIS_SECONDARY = 0.43
AXIS_CENTRAL = 0.52
CENTRAL_MARGIN = 0.035

# ============================================================
# PROTÓTIPOS
# ============================================================
AXES = {
    "INSTAGRAM": [
        "Instagram",
        "uso do Instagram",
        "Instagram em centros de assuntos estudantis",
        "Instagram como ferramenta de comunicação",
        "Instagram como ferramenta de marketing",
        "Instagram",
        "uso de Instagram",
        "Instagram en centros de asuntos estudiantiles",
        "Instagram as a communication tool",
        "Instagram as a marketing tool",
    ],
    "ASSUNTOS_ESTUDANTIS": [
        "centro de assuntos estudantis",
        "assuntos estudantis",
        "pro-reitoria de assuntos estudantis",
        "assistencia estudantil",
        "servicos estudantis",
        "atendimento ao estudante",
        "apoio ao estudante",
        "student affairs center",
        "student affairs",
        "student services",
        "office of student affairs",
        "student support services",
        "student affairs department",
        "centro de asuntos estudiantiles",
        "asuntos estudiantiles",
        "servicios estudiantiles",
    ],
    "MARKETING": [
        "marketing",
        "marketing digital",
        "social media marketing",
        "marketing de midias sociais",
        "estratégia de marketing",
        "marketing para assuntos estudantis",
        "estrategia de marketing digital",
        "marketing de servicios",
        "digital marketing",
        "marketing strategy",
        "service marketing",
    ],
    "REDES_SOCIAIS": [
        "redes sociais",
        "mídias sociais",
        "social media",
        "estratégia de redes sociais",
        "redes sociales",
        "medios sociales",
        "plataformas de redes sociales",
        "social networks",
        "social media platforms",
        "social media strategy",
    ],
    "PROMOÇÃO": [
        "promoção",
        "promoção de serviços",
        "divulgação",
        "divulgação de serviços",
        "comunicação institucional",
        "extensão e divulgação",
        "engajamento de usuários",
        "promoción",
        "difusión",
        "difusión de servicios",
        "comunicación institucional",
        "promotion",
        "outreach",
        "service promotion",
        "institutional communication",
        "engagement",
    ],
}

NEGATIVE_CONTEXTS = {
    "ENSINO": [
        "Instagram used for teaching",
        "Instagram as educational tool",
        "social media in classroom",
        "student learning through Instagram",
        "Instagram in medical education",
        "Instagram for anatomy education",
        "uso do instagram no ensino",
        "instagram como ferramenta pedagógica",
    ],
    "MARKETING_INSTITUCIONAL": [
        "university marketing",
        "university branding",
        "student recruitment",
        "higher education marketing",
        "marketing universitário",
        "captação de alunos",
    ],
    "COMPORTAMENTO_ESTUDANTIL": [
        "student social media use",
        "social media addiction among students",
        "student engagement with social media",
        "Instagram use among college students",
        "comportamento dos estudantes nas redes sociais",
        "vício em redes sociais",
    ],
}

CATEGORIES = {
    "A1": [
        "Instagram como objeto principal de estudo em assuntos estudantis para marketing digital e promoção",
        "uso do Instagram por centros de assuntos estudantis como principal ferramenta de marketing e divulgação",
        "Instagram central para promoção de serviços de apoio ao estudante",
        "Instagram as the main object of study in student affairs for digital marketing and promotion",
    ],
    "A2": [
        "Instagram utilizado por assuntos estudantis como parte de uma estratégia mais ampla de redes sociais",
        "Instagram como um canal dentro da estratégia de marketing digital de assistência estudantil",
        "Instagram used by student affairs as part of a broader social media strategy",
    ],
    "B": [
        "redes sociais utilizadas por assuntos estudantis para marketing e promoção",
        "mídias sociais e marketing digital em serviços estudantis",
        "social media used by student affairs for marketing and promotion",
    ],
    "C": [
        "Instagram e assuntos estudantis",
        "uso do Instagram por centros de assuntos estudantis sem foco específico em marketing",
        "Instagram and student affairs",
    ],
    "D": [
        "marketing digital aplicado a assuntos estudantis sem Instagram",
        "promoção de serviços de apoio ao estudante",
        "digital marketing applied to student affairs without Instagram",
    ],
}


# ============================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================
def normalize_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def find_column(df, candidates):
    normalized = {str(col).strip().lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    for col in df.columns:
        if any(c.lower() in str(col).lower() for c in candidates):
            return col
    return None


def build_text(row, title_col, abstract_col):
    title = normalize_text(row.get(title_col, ""))
    abstract = normalize_text(row.get(abstract_col, ""))
    if title and abstract:
        return f"{title}. {abstract}"
    return title or abstract


def encode_prototypes(model, dictionary):
    texts, labels = [], []
    for label, phrases in dictionary.items():
        texts.extend(phrases)
        labels.extend([label] * len(phrases))
    return model.encode(
        texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    ), labels


def aggregate_scores(similarity_row, labels, names):
    scores = {}
    for name in names:
        values = sorted(
            [similarity_row[i] for i, l in enumerate(labels) if l == name], reverse=True
        )
        scores[name] = float(
            np.mean(values[:3]) if len(values) >= 3 else np.mean(values)
        )
    return scores


def classify_axis(score, all_scores):
    mean_score = np.mean(list(all_scores.values()))
    if score >= AXIS_CENTRAL and score >= (mean_score + CENTRAL_MARGIN):
        return "CENTRAL"
    if score >= AXIS_SECONDARY:
        return "SECUNDÁRIO"
    if score >= AXIS_PRESENT:
        return "INCIDENTAL"
    return "AUSENTE"


def determine_consistency(category, axis_scores):
    I, AE = axis_scores["INSTAGRAM"], axis_scores["ASSUNTOS_ESTUDANTIS"]
    MP = max(axis_scores["MARKETING"], axis_scores["PROMOÇÃO"])
    R = axis_scores["REDES_SOCIAIS"]

    if category == "A1":
        reqs = [I >= AXIS_PRESENT, AE >= AXIS_PRESENT, MP >= AXIS_PRESENT]
    elif category == "A2":
        reqs = [
            I >= AXIS_PRESENT,
            AE >= AXIS_PRESENT,
            R >= AXIS_PRESENT,
            MP >= AXIS_PRESENT,
        ]
    elif category == "B":
        reqs = [AE >= AXIS_PRESENT, R >= AXIS_PRESENT, MP >= AXIS_PRESENT]
    elif category == "C":
        reqs = [I >= AXIS_PRESENT, AE >= AXIS_PRESENT]
    elif category == "D":
        reqs = [AE >= AXIS_PRESENT, MP >= AXIS_PRESENT]
    else:
        reqs = [False]

    ratio = sum(reqs) / len(reqs)
    if ratio == 1.0:
        return "CONSISTENTE"
    if ratio >= 0.5:
        return "PARCIAL"
    return "INCONSISTENTE"


# ============================================================
# EXECUÇÃO
# ============================================================
print("=" * 70)
print("TRIAGEM SEMÂNTICA LOCAL — DEFINITIVA")
print("=" * 70)

if not INPUT_FILE.exists():
    print(f"ERRO: {INPUT_FILE} não encontrado.")
    sys.exit(1)

df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# Validação segura das colunas
title_col = find_column(df, ["title", "titulo", "título", "article title"])
if title_col is None:
    print("ERRO: coluna de título não encontrada.")
    print("Colunas disponíveis:")
    print(list(df.columns))
    sys.exit(1)

abstract_col = find_column(df, ["abstract", "resumo", "summary"])
if abstract_col is None:
    print("AVISO: coluna de resumo não encontrada.")
    print("A análise será realizada apenas com os títulos.")
    abstract_col = title_col

print("\nCarregando modelo semântico...")
model = SentenceTransformer(MODEL_NAME)

axis_emb, axis_lbl = encode_prototypes(model, AXES)
cat_emb, cat_lbl = encode_prototypes(model, CATEGORIES)
neg_emb, neg_lbl = encode_prototypes(model, NEGATIVE_CONTEXTS)

texts, sentences_flat, sentence_map = [], [], []

for idx, row in df.iterrows():
    text = build_text(row, title_col, abstract_col)
    texts.append(text)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
    if not sents:
        sents = [text]
    for s in sents:
        sentences_flat.append(s)
        sentence_map.append(idx)

article_embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True,
    batch_size=16,
)
sentence_embeddings = model.encode(
    sentences_flat,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True,
    batch_size=32,
)

axis_sim = article_embeddings @ axis_emb.T
cat_sim = article_embeddings @ cat_emb.T
neg_sim = article_embeddings @ neg_emb.T
sent_axis_sim = sentence_embeddings @ axis_emb.T

results = []
axis_names = list(AXES.keys())
cat_names = list(CATEGORIES.keys())
neg_names = list(NEGATIVE_CONTEXTS.keys())

for index in range(len(df)):
    # 1. Agregação de Scores e Eixos
    axis_scores = aggregate_scores(axis_sim[index], axis_lbl, axis_names)
    axis_labels = {
        axis: classify_axis(axis_scores[axis], axis_scores) for axis in axis_names
    }
    neg_scores = aggregate_scores(neg_sim[index], neg_lbl, neg_names)

    MP = max(axis_scores["MARKETING"], axis_scores["PROMOÇÃO"])
    I, AE, R = (
        axis_scores["INSTAGRAM"],
        axis_scores["ASSUNTOS_ESTUDANTIS"],
        axis_scores["REDES_SOCIAIS"],
    )
    theme_score = float(np.mean([I, AE, MP]))

    # 2. Contexto Negativo (Falso Positivo)
    negative_context = max(neg_scores, key=neg_scores.get)
    max_neg_score = neg_scores[negative_context]
    is_false_positive = (
        "SIM" if (max_neg_score > AE + 0.05 and AE < AXIS_SECONDARY) else "NÃO"
    )

    # 3. Classificação Bruta
    cat_scores = aggregate_scores(cat_sim[index], cat_lbl, cat_names)
    raw_category = max(cat_scores, key=cat_scores.get)

    # 4. Categoria Final & Gates Estruturais
    final_category = raw_category
    decision_reason = ""

    if AE < AXIS_PRESENT:
        final_category = "FORA_DO_ESCOPO"
        decision_reason = f"Eixo Assuntos Estudantis abaixo do limiar ({AE:.3f} < {AXIS_PRESENT:.2f})."
    elif raw_category == "A1":
        if (
            axis_labels["REDES_SOCIAIS"] in ["CENTRAL", "SECUNDÁRIO"]
            and axis_labels["INSTAGRAM"] != "CENTRAL"
        ):
            final_category = "A2"
            decision_reason = "Instagram presente, mas Redes Sociais possui papel estrutural mais forte; reclassificado de A1 para A2."
        else:
            decision_reason = "Classificação semântica A1 mantida."
    elif raw_category == "D" and I >= AXIS_PRESENT:
        final_category = "C"
        decision_reason = "Instagram detectado; reclassificado de D para C."
    else:
        decision_reason = f"Classificação semântica {raw_category} mantida."

    consistency = (
        determine_consistency(final_category, axis_scores)
        if final_category != "FORA_DO_ESCOPO"
        else "INCONSISTENTE"
    )

    # 5. Extração Textual e Falso Negativo
    s_indices = [i for i, mapped_idx in enumerate(sentence_map) if mapped_idx == index]
    evidences = {"INSTAGRAM": "", "ASSUNTOS_ESTUDANTIS": "", "MP": ""}
    best_ae_sentence_score = 0.0

    if s_indices:
        ae_cols = [i for i, l in enumerate(axis_lbl) if l == "ASSUNTOS_ESTUDANTIS"]
        best_ae_sentence_score = max(
            np.max(sent_axis_sim[i, ae_cols]) for i in s_indices
        )

        for target, target_lbls in [
            ("INSTAGRAM", ["INSTAGRAM"]),
            ("ASSUNTOS_ESTUDANTIS", ["ASSUNTOS_ESTUDANTIS"]),
            ("MP", ["MARKETING", "PROMOÇÃO"]),
        ]:
            target_cols = [i for i, l in enumerate(axis_lbl) if l in target_lbls]
            best_sent_idx = max(
                s_indices, key=lambda i: np.max(sent_axis_sim[i, target_cols])
            )
            if np.max(sent_axis_sim[best_sent_idx, target_cols]) >= AXIS_PRESENT:
                evidences[target] = sentences_flat[best_sent_idx]

    possible_false_negative = (
        "SIM"
        if (AE < AXIS_PRESENT and best_ae_sentence_score >= AXIS_SECONDARY)
        else "NÃO"
    )

    # 6. Elegibilidade (com overrides lógicos de Falsos Positivos/Negativos)
    if final_category in ["A1", "A2"]:
        if consistency == "CONSISTENTE":
            elegibilidade = "ELEGÍVEL"
        else:
            elegibilidade = "POTENCIALMENTE_ELEGÍVEL"
        utilidade = "NÚCLEO PRINCIPAL"
    elif final_category == "B":
        elegibilidade = "POTENCIALMENTE_ELEGÍVEL"
        utilidade = "RELACIONADO"
    elif final_category == "C":
        elegibilidade = "REVISÃO_HUMANA"
        utilidade = "RELACIONADO"
    elif final_category == "D":
        elegibilidade = "NÃO_ELEGÍVEL"
        utilidade = "CONTEXTUAL (FUNDAMENTAÇÃO)"
    else:
        elegibilidade = "NÃO_ELEGÍVEL"
        utilidade = "DESCARTAR"

    # Override: Falsos Positivos
    if is_false_positive == "SIM" and elegibilidade in [
        "ELEGÍVEL",
        "POTENCIALMENTE_ELEGÍVEL",
    ]:
        elegibilidade = "REVISÃO_HUMANA"

    # Override: Falsos Negativos
    if possible_false_negative == "SIM":
        elegibilidade = "REVISÃO_HUMANA"
        if final_category == "FORA_DO_ESCOPO":
            utilidade = "REVISÃO DE POSSÍVEL FALSO NEGATIVO"
        decision_reason += (
            f" Possível falso negativo detectado: score global de Assuntos Estudantis={AE:.3f}, "
            f"mas melhor trecho local={best_ae_sentence_score:.3f}."
        )

    # 7. Grau de Relevância
    if theme_score >= 0.50:
        rel_tematica = "MUITO ALTA"
    elif theme_score >= 0.43:
        rel_tematica = "ALTA"
    elif theme_score >= 0.36:
        rel_tematica = "MÉDIA"
    else:
        rel_tematica = "BAIXA"

    # 8. Composição do Registro Final
    record = dict(df.iloc[index].to_dict())
    record.update(
        {
            "Relevância temática (Score)": round(theme_score, 4),
            "Relevância temática (Grau)": rel_tematica,
            "Categoria Semântica Bruta": raw_category,
            "Categoria Final": final_category,
            "Motivo da decisão": decision_reason,
            "Elegibilidade": elegibilidade,
            "Utilidade teórica": utilidade,
            "Falso Positivo Provável": is_false_positive,
            "Falso Negativo Provável": possible_false_negative,
            "Contexto negativo dominante": negative_context,
            "Score contexto negativo": round(max_neg_score, 4),
            "Consistência": consistency,
            "INSTAGRAM (Papel/Score)": f"{axis_labels['INSTAGRAM']} ({round(I, 3)})",
            "ASSUNTOS_EST. (Papel/Score)": f"{axis_labels['ASSUNTOS_ESTUDANTIS']} ({round(AE, 3)})",
            "Score melhor trecho Assuntos Est.": round(best_ae_sentence_score, 4),
            "MARKETING/PROMO (Score Max)": round(MP, 3),
            "REDES_SOCIAIS (Score)": round(R, 3),
            "Trecho mais próximo: Assuntos Est.": evidences["ASSUNTOS_ESTUDANTIS"],
            "Trecho mais próximo: Instagram": evidences["INSTAGRAM"],
            "Trecho mais próximo: Mkt/Promo": evidences["MP"],
        }
    )
    results.append(record)

result_df = pd.DataFrame(results)

# ============================================================
# EXPORTAÇÃO
# ============================================================
texto_cols = [title_col]
if abstract_col != title_col:
    texto_cols.append(abstract_col)

matriz_cols = texto_cols + [
    "Relevância temática (Score)",
    "Relevância temática (Grau)",
    "Categoria Semântica Bruta",
    "Categoria Final",
    "Motivo da decisão",
    "Elegibilidade",
    "Utilidade teórica",
    "Falso Positivo Provável",
    "Falso Negativo Provável",
    "Contexto negativo dominante",
    "Score contexto negativo",
    "INSTAGRAM (Papel/Score)",
    "ASSUNTOS_EST. (Papel/Score)",
    "Score melhor trecho Assuntos Est.",
    "MARKETING/PROMO (Score Max)",
    "REDES_SOCIAIS (Score)",
    "Trecho mais próximo: Assuntos Est.",
    "Trecho mais próximo: Instagram",
    "Trecho mais próximo: Mkt/Promo",
]

axis_matrix = result_df[matriz_cols].copy()
axis_matrix = axis_matrix.sort_values(by="Relevância temática (Score)", ascending=False)

print("\nGerando arquivo Excel auditável...")
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    result_df.to_excel(writer, sheet_name="Triagem Completa", index=False)
    axis_matrix.to_excel(writer, sheet_name="Matriz de Decisão", index=False)
    result_df[result_df["Elegibilidade"] == "ELEGÍVEL"].to_excel(
        writer, sheet_name="Elegíveis", index=False
    )
    result_df[result_df["Elegibilidade"] == "POTENCIALMENTE_ELEGÍVEL"].to_excel(
        writer, sheet_name="Potenciais", index=False
    )
    result_df[result_df["Elegibilidade"] == "REVISÃO_HUMANA"].to_excel(
        writer, sheet_name="Revisão Humana", index=False
    )
    result_df[result_df["Falso Positivo Provável"] == "SIM"].to_excel(
        writer, sheet_name="Falsos Positivos", index=False
    )
    result_df[result_df["Falso Negativo Provável"] == "SIM"].to_excel(
        writer, sheet_name="Falsos Negativos", index=False
    )
    result_df[result_df["Categoria Final"] == "D"].to_excel(
        writer, sheet_name="Contextuais", index=False
    )
    result_df[result_df["Categoria Final"] == "FORA_DO_ESCOPO"].to_excel(
        writer, sheet_name="Fora do Escopo", index=False
    )

print("\n" + "=" * 70)
print("CONCLUÍDO — TRIAGEM SEMÂNTICA LOCAL V3 (FINAL)")
print("=" * 70)
print(f"Arquivo gerado: {OUTPUT_FILE}")
