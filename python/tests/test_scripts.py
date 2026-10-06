import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from organizar_arquivos import categoria, destino_livre, organizar
from processar_notas import carregar, estatisticas_disciplinas, medias_por_aluno_disciplina, situacao


@pytest.fixture
def csv_notas(tmp_path):
    f = tmp_path / "n.csv"
    f.write_text(
        "matricula,aluno,codigo,disciplina,avaliacao,nota,peso\n"
        "1001,Ana,ALG,Algoritmos,P1,8,1\n"
        "1001,Ana,ALG,Algoritmos,P2,6,3\n"      # média ponderada = 6.5
        "1002,Bia,ALG,Algoritmos,P1,9,1\n"
        "1002,Bia,ALG,Algoritmos,P1,9,1\n"      # duplicada
        "1003,Caio,ALG,Algoritmos,P1,15,1\n"    # nota inválida
        "1004,Duda,ALG,Algoritmos,P1,3,1\n")
    return f


def test_situacao():
    assert [situacao(x) for x in (7, 6.99, 5, 4.9)] == ["Aprovado", "Recuperação", "Recuperação", "Reprovado"]


def test_carregar_valida_e_deduplica(csv_notas):
    df = carregar(csv_notas)
    assert len(df) == 4 and df.attrs["descartadas"] == 1


def test_medias_e_estatisticas(csv_notas):
    m = medias_por_aluno_disciplina(carregar(csv_notas)).set_index("aluno")
    assert m.loc["Ana", "media"] == 6.5 and m.loc["Ana", "situacao"] == "Recuperação"
    assert m.loc["Bia", "situacao"] == "Aprovado" and m.loc["Duda", "situacao"] == "Reprovado"
    s = estatisticas_disciplinas(m.reset_index()).iloc[0]
    assert s["alunos"] == 3 and s["taxa_aprovacao_pct"] == pytest.approx(33.3)


def test_colunas_ausentes(tmp_path):
    f = tmp_path / "x.csv"; f.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError):
        carregar(f)


def test_organizar_simula_e_executa(tmp_path):
    for nome in ["a.pdf", "b.csv", "c.png", "d.xyz", "e.pdf"]:
        (tmp_path / nome).write_text("x")
    assert len(organizar(tmp_path, executar=False)) == 5
    assert (tmp_path / "a.pdf").exists()                      # simulação não move
    organizar(tmp_path, executar=True)
    assert (tmp_path / "Documentos" / "a.pdf").exists() and (tmp_path / "Outros" / "d.xyz").exists()
    assert categoria(".PNG") == "Imagens"


def test_nao_sobrescreve(tmp_path):
    (tmp_path / "a.txt").write_text("1")
    assert destino_livre(tmp_path / "a.txt").name == "a (1).txt"
