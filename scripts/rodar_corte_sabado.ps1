# ==============================================================================
# scripts/rodar_corte_sabado.ps1
# Runbook de Automacao para o Corte Oficial de Sabado (03/10/2026 as 20h00)
# Desafio de Estatistica e Econometria FGV EPGE (Eleicoes Presidenciais 2026)
# Grupo: Joao Pedro Valuche, Arthur Caron Lyra, Lethicia Manfioletti Possamai
#
# Execucao:
#   powershell -ExecutionPolicy Bypass -File scripts/rodar_corte_sabado.ps1
#
# Regra estrita: Zero travessoes em todo o arquivo.
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " RUNBOOK OFICIAL: CORTE DE SABADO (20H00) - DESAFIO FGV EPGE 2026" -ForegroundColor Cyan
Write-Host " Grupo: Joao Pedro Valuche, Arthur Caron Lyra, Lethicia Manfioletti Possamai" -ForegroundColor Cyan
Write-Host " Tag Base do Modelo: modelo-congelado" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$PYTHON = Join-Path $ROOT_DIR ".venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON)) {
    Write-Host "[ERRO CRITICO] Ambiente virtual Python nao encontrado em $PYTHON" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Python detectado: $PYTHON" -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 1: Verificacao do Teste de Transcricao das Pesquisas
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 1/7] Executando teste de transcricao contra HTMLs salvos no MANIFEST..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON -m pytest tests/test_pipeline.py -k test_transcricao_pesquisas_2026_contra_html_salvo -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 1] Divergencia na transcricao das pesquisas de 2026!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Teste de transcricao aprovado com sucesso." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 2: Execucao da Suite Completa de Testes Unitarios e Integrados
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 2/7] Executando suite completa de testes automatizados (pytest -v)..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON -m pytest -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 2] Testes automatizados falharam!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Suite completa de testes aprovada (100% passando)." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 3: Execucao do Motor de Modelagem Oficial e Geracao da Planilha
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 3/7] Executando motor econometrico oficial e gerando previsao_2026.xlsx..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON scripts/executar_backtest_oficial.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 3] Erro na execucao do motor econometrico!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Planilha outputs/previsao_2026.xlsx gerada pelo Modelo Oficial." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 4: Validacao Estrita da Planilha de Entrega (Edital FGV EPGE)
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 4/7] Validando conformidade estrita de outputs/previsao_2026.xlsx..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON scripts/validar_entrega.py outputs/previsao_2026.xlsx
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 4] Planilha invalida contra as regras do edital!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Planilha oficial validada com zero erros." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 5: Atualizacao dos Dados da Interface Interativa
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 5/7] Atualizando interface/dados.json e interface/dados.js..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON scripts/gerar_dados_interface.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 5] Erro ao atualizar dados da interface!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Interface atualizada com sucesso para navegacao local file://" -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 6: Geracao do Relatorio Oficial Checkpoint 4
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 6/7] Gerando relatorio oficial reports/checkpoint_4.md..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON scripts/gerar_relatorio_checkpoint4.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 6] Erro ao gerar relatorio do Checkpoint 4!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Relatorio reports/checkpoint_4.md gerado e sincronizado." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# ETAPA 7: Geracao dos Numeros em LaTeX, Compilacao do PDF e Auditoria Estrita
# ------------------------------------------------------------------------------
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "[ETAPA 7/7] Gerando docs/numeros_finais.tex, compilando PDF e auditando conteudo..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Yellow

& $PYTHON scripts/gerar_numeros_latex.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA NA ETAPA 7] Erro ao gerar docs/numeros_finais.tex!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] docs/numeros_finais.tex gerado com sucesso." -ForegroundColor Green

if (Get-Command pdflatex -ErrorAction SilentlyContinue) {
    Write-Host "[INFO] pdflatex detectado. Compilando docs/metodologia.tex (passo 1/2)..." -ForegroundColor Cyan
    Push-Location docs
    try {
        & pdflatex -interaction=nonstopmode metodologia.tex
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FALHA NA ETAPA 7] Erro na primeira compilacao de metodologia.tex!" -ForegroundColor Red
            exit 1
        }
        Write-Host "[INFO] Compilando docs/metodologia.tex (passo 2/2)..." -ForegroundColor Cyan
        & pdflatex -interaction=nonstopmode metodologia.tex
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FALHA NA ETAPA 7] Erro na segunda compilacao de metodologia.tex!" -ForegroundColor Red
            exit 1
        }
    }
    finally {
        Pop-Location
    }
} else {
    Write-Host "[INFO] pdflatex nao disponivel no ambiente local. Gerando docs/metodologia.pdf via motor Python..." -ForegroundColor Cyan
    & $PYTHON scripts/gerar_pdf_metodologia.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FALHA CRITICA NA ETAPA 7] Erro ao gerar docs/metodologia.pdf via Python!" -ForegroundColor Red
        exit 1
    }
}

# Auditoria estrita do PDF com pypdf
Write-Host "[INFO] Executando auditoria estrita de docs/metodologia.pdf via pypdf..." -ForegroundColor Cyan
& $PYTHON -c "
import sys
import pypdf
import openpyxl

reader = pypdf.PdfReader('docs/metodologia.pdf')
num_pags = len(reader.pages)
if num_pags != 2:
    print(f'[ERRO FATAL] PDF possui {num_pags} paginas! Exige-se exatamente 2.')
    sys.exit(1)

texto_completo = '\n'.join(p.extract_text() for p in reader.pages)

if 'PRELIMINAR' in texto_completo.upper():
    print('[ERRO FATAL] Palavra PRELIMINAR detectada no PDF final!')
    sys.exit(1)

wb = openpyxl.load_workbook('outputs/previsao_2026.xlsx', data_only=True)
ws1 = wb['Candidatos']
ws2 = wb['Adicionais']

faltantes = []
for row in ws1.iter_rows(min_row=2, values_only=True):
    nome = str(row[0] or '').strip()
    if nome and nome.lower() != 'total':
        val = float(row[2])
        v_str = f'{val:.1f}%'.replace('.', ',')
        if v_str not in texto_completo:
            faltantes.append(f'Aba 1 ({nome}): {v_str}')

for row in ws2.iter_rows(min_row=2, values_only=True):
    lbl = str(row[0] or '').strip()
    if lbl:
        val = float(row[1])
        v_str = f'{val:.1f}%'.replace('.', ',')
        if v_str not in texto_completo:
            faltantes.append(f'Aba 2 ({lbl}): {v_str}')

if faltantes:
    print(f'[ERRO FATAL] Valores do XLSX ausentes no PDF: {faltantes}')
    sys.exit(1)

print('[OK] PDF auditado: 2 paginas, sem PRELIMINAR, 100% dos percentuais conferidos.')
"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA CRITICA NA ETAPA 7] Auditoria de conformidade de docs/metodologia.pdf falhou!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] docs/metodologia.pdf aprovado em todas as checagens estritas." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------------------------
# RESUMO FINAL E ORIENTACOES PARA O OPERADOR
# ------------------------------------------------------------------------------
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " CORTE CONCLUIDO COM SUCESSO EM TODAS AS ETAPAS!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Artefatos oficiais gerados e validados:" -ForegroundColor White
Write-Host "  1. Planilha Oficial:      outputs/previsao_2026.xlsx" -ForegroundColor White
Write-Host "  2. Relatorio de Fechamento: reports/checkpoint_4.md" -ForegroundColor White
Write-Host "  3. Nota Metodologica PDF: docs/metodologia.pdf (2 paginas)" -ForegroundColor White
Write-Host "  4. Dados da Interface:     interface/dados.json e interface/dados.js" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos para fechamento do sabado 20h00:" -ForegroundColor Yellow
Write-Host "  git status" -ForegroundColor Gray
Write-Host "  git add outputs/previsao_2026.xlsx reports/checkpoint_4.md docs/ interface/ data/" -ForegroundColor Gray
Write-Host '  git commit -m "feat(checkpoint-4): previsao oficial final apos corte de sabado 20h"' -ForegroundColor Gray
Write-Host "  git tag checkpoint-4" -ForegroundColor Gray
Write-Host "  git push origin main; git push origin checkpoint-4" -ForegroundColor Gray
Write-Host ""
