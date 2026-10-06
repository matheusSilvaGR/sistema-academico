"""Processa um CSV de notas: média ponderada, situação, estatísticas por disciplina,
relatório (CSV/JSON) e gráficos. Uso: python processar_notas.py ../data/entrada/notas_exemplo.csv"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

MEDIA_APROVACAO = 7.0
MEDIA_RECUPERACAO = 5.0
COLUNAS = {"matricula", "aluno", "codigo", "disciplina", "avaliacao", "nota", "peso"}


def carregar(csv_path: Path) -> pd.DataFrame:
    """Lê e valida o CSV; descarta linhas inválidas e informa quantas foram removidas."""
    df = pd.read_csv(csv_path, dtype={"matricula": str})
    faltando = COLUNAS - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes no CSV: {sorted(faltando)}")
    df["nota"] = pd.to_numeric(df["nota"], errors="coerce")
    df["peso"] = pd.to_numeric(df["peso"], errors="coerce")
    validas = df["nota"].between(0, 10) & (df["peso"] > 0)
    df.attrs["descartadas"] = int((~validas).sum())
    return df[validas].drop_duplicates(["matricula", "codigo", "avaliacao"]).reset_index(drop=True)


def situacao(media: float) -> str:
    if media >= MEDIA_APROVACAO:
        return "Aprovado"
    if media >= MEDIA_RECUPERACAO:
        return "Recuperação"
    return "Reprovado"


def medias_por_aluno_disciplina(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(ponderada=df["nota"] * df["peso"])
    g = df.groupby(["matricula", "aluno", "codigo", "disciplina"], as_index=False).agg(
        soma=("ponderada", "sum"), pesos=("peso", "sum"))
    g["media"] = (g["soma"] / g["pesos"]).round(2)
    g["situacao"] = g["media"].map(situacao)
    return g.drop(columns=["soma", "pesos"])


def estatisticas_disciplinas(medias: pd.DataFrame) -> pd.DataFrame:
    g = medias.groupby(["codigo", "disciplina"])
    out = g["media"].agg(alunos="count", media="mean", mediana="median", desvio="std",
                         minimo="min", maximo="max").round(2)
    out["taxa_aprovacao_pct"] = (g["situacao"].apply(lambda s: (s == "Aprovado").mean()) * 100).round(1)
    return out.reset_index()


def gerar_graficos(medias: pd.DataFrame, stats: pd.DataFrame, destino: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(stats["disciplina"], stats["media"], color="#2e6da4")
    ax.axhline(MEDIA_APROVACAO, color="#c0392b", ls="--", label=f"Média de aprovação ({MEDIA_APROVACAO:g})")
    ax.set_ylim(0, 10); ax.set_ylabel("Média da turma"); ax.legend()
    ax.set_title("Média por disciplina")
    fig.tight_layout(); fig.savefig(destino / "media_por_disciplina.png", dpi=150); plt.close(fig)

    contagem = medias.groupby(["disciplina", "situacao"]).size().unstack(fill_value=0)
    contagem = contagem.reindex(columns=["Aprovado", "Recuperação", "Reprovado"], fill_value=0)
    ax = contagem.plot(kind="bar", stacked=True, figsize=(8, 4.5),
                       color=["#2e7d32", "#f9a825", "#c62828"])
    ax.set_ylabel("Alunos"); ax.set_xlabel(""); ax.set_title("Situação por disciplina")
    plt.xticks(rotation=0); plt.tight_layout()
    plt.savefig(destino / "situacao_por_disciplina.png", dpi=150); plt.close()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path)
    p.add_argument("--saida", type=Path, default=Path("saida"))
    a = p.parse_args()

    df = carregar(a.csv)
    medias = medias_por_aluno_disciplina(df)
    stats = estatisticas_disciplinas(medias)

    a.saida.mkdir(parents=True, exist_ok=True)
    medias.to_csv(a.saida / "medias_por_aluno.csv", index=False)
    stats.to_csv(a.saida / "estatisticas_disciplinas.csv", index=False)
    gerar_graficos(medias, stats, a.saida)
    resumo = {"registros_validos": len(df), "linhas_descartadas": df.attrs["descartadas"],
              "alunos": int(medias["matricula"].nunique()),
              "taxa_aprovacao_geral_pct": round(float((medias["situacao"] == "Aprovado").mean() * 100), 1),
              "disciplinas": stats.to_dict("records")}
    (a.saida / "resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False))
    print(json.dumps(resumo, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
