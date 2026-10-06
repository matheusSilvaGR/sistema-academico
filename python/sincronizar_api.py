"""Integração: envia alunos, disciplinas e notas de um CSV para a API Node.js.
Idempotente: alunos e disciplinas existentes são reaproveitados e notas repetidas
(mesmo aluno, disciplina e avaliação) são ignoradas pela API (409)."""
import argparse
import csv
import json
import urllib.error
import urllib.request
from pathlib import Path


class ApiError(RuntimeError):
    pass


def chamar(base: str, metodo: str, caminho: str, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(base + caminho, data=dados, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            texto = r.read().decode()
            return r.status, json.loads(texto) if texto else None
    except urllib.error.HTTPError as e:
        texto = e.read().decode()
        return e.code, json.loads(texto) if texto else None
    except urllib.error.URLError as e:
        raise ApiError(f"API indisponível em {base}: {e.reason}") from e


def sincronizar(csv_path: Path, base: str) -> dict:
    alunos = {a["matricula"]: a["id"] for a in chamar(base, "GET", "/alunos")[1]}
    discs = {d["codigo"]: d["id"] for d in chamar(base, "GET", "/disciplinas")[1]}
    resumo = {"alunos_novos": 0, "disciplinas_novas": 0, "notas_enviadas": 0,
              "notas_ja_existentes": 0, "erros": []}

    with open(csv_path, newline="", encoding="utf-8") as f:
        for n, linha in enumerate(csv.DictReader(f), start=2):
            mat, cod = linha["matricula"], linha["codigo"].upper()
            if mat not in alunos:
                st, r = chamar(base, "POST", "/alunos", {"nome": linha["aluno"], "matricula": mat})
                if st != 201:
                    resumo["erros"].append(f"linha {n}: aluno {mat}: {r}"); continue
                alunos[mat] = r["id"]; resumo["alunos_novos"] += 1
            if cod not in discs:
                st, r = chamar(base, "POST", "/disciplinas", {"nome": linha["disciplina"], "codigo": cod})
                if st != 201:
                    resumo["erros"].append(f"linha {n}: disciplina {cod}: {r}"); continue
                discs[cod] = r["id"]; resumo["disciplinas_novas"] += 1
            st, r = chamar(base, "POST", "/notas", {
                "alunoId": alunos[mat], "disciplinaId": discs[cod], "valor": float(linha["nota"]),
                "peso": float(linha["peso"]), "avaliacao": linha["avaliacao"]})
            if st == 201:
                resumo["notas_enviadas"] += 1
            elif st == 409:
                resumo["notas_ja_existentes"] += 1
            else:
                resumo["erros"].append(f"linha {n}: nota: {r}")
    return resumo


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path)
    p.add_argument("--api", default="http://localhost:3000")
    a = p.parse_args()
    try:
        print(json.dumps(sincronizar(a.csv, a.api), indent=2, ensure_ascii=False))
    except ApiError as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
