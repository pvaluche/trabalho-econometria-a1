"""
download.py
Utilitarios para download de arquivos com verificacao de integridade e
registro automatico no MANIFEST.csv.
"""

import csv
import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import MANIFEST_PATH, RAW_DIR

logger = logging.getLogger(__name__)


def sha256_arquivo(caminho: Path) -> str:
    """Calcula o hash SHA-256 de um arquivo em blocos (eficiente em memoria)."""
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar_arquivo(
    url: str,
    destino: Path | None = None,
    nome: str | None = None,
    forcar: bool = False,
) -> Path:
    """
    Baixa um arquivo de uma URL e salva em RAW_DIR (ou em `destino`).

    Parameters
    ----------
    url : str
        URL de origem.
    destino : Path, optional
        Caminho completo de destino. Se None, usa RAW_DIR / nome.
    nome : str, optional
        Nome do arquivo. Ignorado se `destino` for fornecido.
        Se ambos forem None, usa o ultimo segmento da URL.
    forcar : bool
        Se True, baixa mesmo que o arquivo ja exista.

    Returns
    -------
    Path
        Caminho do arquivo baixado.
    """
    if destino is None:
        if nome is None:
            nome = url.split("/")[-1]
        destino = RAW_DIR / nome

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists() and not forcar:
        logger.info("Arquivo ja existe, pulando download: %s", destino.name)
        return destino

    logger.info("Baixando %s -> %s", url, destino)
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(destino, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)

    tamanho = destino.stat().st_size
    hash_sha256 = sha256_arquivo(destino)
    _registrar_manifest(
        arquivo=destino.name,
        url=url,
        tamanho=tamanho,
        sha256=hash_sha256,
    )

    logger.info(
        "Download concluido: %s (%d bytes, sha256=%s...)",
        destino.name,
        tamanho,
        hash_sha256[:8],
    )
    return destino


def _registrar_manifest(
    arquivo: str,
    url: str,
    tamanho: int,
    sha256: str,
) -> None:
    """Acrescenta (ou atualiza) uma linha no MANIFEST.csv."""
    campos = ["arquivo", "url", "data_download", "tamanho_bytes", "sha256"]
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    linhas: list[dict] = []
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            linhas = [r for r in reader if r["arquivo"] != arquivo]

    nova_linha = {
        "arquivo": arquivo,
        "url": url,
        "data_download": datetime.now(tz=timezone.utc).isoformat(),
        "tamanho_bytes": str(tamanho),
        "sha256": sha256,
    }
    linhas.append(nova_linha)

    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)
