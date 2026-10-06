"""Automação: organiza os arquivos de uma pasta em subpastas por tipo.
Seguro por padrão: use --executar para mover de fato (sem ele, apenas simula)."""
import argparse
import shutil
from pathlib import Path

CATEGORIAS = {
    "Documentos": {".pdf", ".doc", ".docx", ".txt", ".odt", ".md"},
    "Planilhas": {".xls", ".xlsx", ".csv", ".ods"},
    "Apresentacoes": {".ppt", ".pptx", ".odp"},
    "Imagens": {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"},
    "Codigo": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".sql", ".ipynb", ".json"},
    "Compactados": {".zip", ".rar", ".7z", ".tar", ".gz"},
}


def categoria(ext: str) -> str:
    ext = ext.lower()
    return next((c for c, exts in CATEGORIAS.items() if ext in exts), "Outros")


def destino_livre(destino: Path) -> Path:
    """Evita sobrescrever: arquivo.txt -> arquivo (1).txt -> arquivo (2).txt ..."""
    if not destino.exists():
        return destino
    n = 1
    while (cand := destino.with_name(f"{destino.stem} ({n}){destino.suffix}")).exists():
        n += 1
    return cand


def organizar(pasta: Path, executar: bool = False) -> list[tuple[Path, Path]]:
    movimentos = []
    for arq in sorted(pasta.iterdir()):
        if not arq.is_file() or arq.name.startswith("."):
            continue
        dest = destino_livre(pasta / categoria(arq.suffix) / arq.name)
        movimentos.append((arq, dest))
        if executar:
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(arq), str(dest))
    return movimentos


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pasta", type=Path)
    p.add_argument("--executar", action="store_true", help="move os arquivos (padrão: apenas simula)")
    a = p.parse_args()
    if not a.pasta.is_dir():
        raise SystemExit(f"Pasta não encontrada: {a.pasta}")
    movs = organizar(a.pasta, a.executar)
    modo = "Movido" if a.executar else "[simulação]"
    for origem, dest in movs:
        print(f"{modo} {origem.name} -> {dest.relative_to(a.pasta)}")
    print(f"{len(movs)} arquivo(s) {'organizados' if a.executar else 'seriam organizados'}.")


if __name__ == "__main__":
    main()
