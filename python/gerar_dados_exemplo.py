"""Gera um CSV FICTÍCIO de notas (semente fixa) para demonstrar o pipeline."""
import csv
import random
from pathlib import Path

random.seed(7)
DESTINO = Path(__file__).resolve().parent.parent / "data" / "entrada" / "notas_exemplo.csv"
NOMES = ["Ana Lima", "Bruno Souza", "Carla Dias", "Diego Rocha", "Elisa Prado", "Fábio Nunes",
         "Gabriela Melo", "Hugo Alves", "Isabela Cruz", "João Pires", "Karen Teles", "Lucas Faria",
         "Marina Costa", "Nicolas Reis", "Olívia Braga", "Paulo Vieira", "Queila Matos",
         "Rafael Lopes", "Sara Duarte", "Tiago Moraes"]
DISCIPLINAS = [("ALG101", "Algoritmos"), ("BD201", "Banco de Dados"), ("WEB301", "Desenvolvimento Web")]
AVALIACOES = [("P1", 1), ("P2", 1), ("Trabalho", 2)]


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with open(DESTINO, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["matricula", "aluno", "codigo", "disciplina", "avaliacao", "nota", "peso"])
        for i, nome in enumerate(NOMES, 1):
            perfil = random.gauss(6.8, 1.6)  # "habilidade" do aluno
            for codigo, disc in DISCIPLINAS:
                for aval, peso in AVALIACOES:
                    nota = min(10, max(0, round(random.gauss(perfil, 1.2), 1)))
                    w.writerow([f"2024{i:04d}", nome, codigo, disc, aval, nota, peso])
    print(f"Gerado: {DESTINO}")


if __name__ == "__main__":
    main()
