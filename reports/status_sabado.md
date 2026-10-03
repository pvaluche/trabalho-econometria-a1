# Status das pesquisas do sábado (03/10/2026)

Última verificação: 03/10/2026, 17h30 (horário de Brasília). Corte: 20h00.

| instituto | registro | divulgada (sim/nao) | horario da divulgacao | URL | Lula | Flavio |
|---|---|---|---|---|---|---|
| Datafolha | BR-01708/2026 | nao | pendente (previsto 18h45) | pendente | pendente | pendente |
| Quaest | BR-02197/2026 | nao | pendente (previsto após 18h00) | pendente | pendente | pendente |
| AtlasIntel | BR-00999/2026 | nao | pendente (previsto a partir das 14h00) | pendente | pendente | pendente |
| PoderData/Aya | BR-03519/2026 | sim | manhã de 03/10 (horário exato não informado na matéria) | https://www.poder360.com.br/poderdata/na-vespera-do-1o-turno-lula-tem-45-e-flavio-43-dos-votos-validos/ | 45 (válidos) / 42 (totais) | 43 (válidos) / 41 (totais) |
| Real Time Big Data | BR-01068/2026 | sim | 03/10, 09h00 | https://www.cnnbrasil.com.br/eleicoes/real-time-lula-tem-44-de-votos-validos-no-1o-turno-em-mg-flavio-42/ | 44 (MG) | 42 (MG) |

## Observações

- PoderData/Aya: transcrita em `data/manual/pesquisas_2026.csv` com `base = votos validos`, porque a matéria só traz todos os candidatos em votos válidos (em votos totais publica apenas Lula 42% e Flávio 41%). Candidatos que "não pontuaram" foram registrados como 0,0. HTML salvo em `data/raw/pesquisas_2026/poderdata_2026_10_03.html` e registrado no `data/MANIFEST.csv`.
- Real Time Big Data BR-01068/2026: levantamento **estadual de Minas Gerais** (2.000 eleitores), não nacional. Não foi transcrito, porque o modelo agrega apenas pesquisas nacionais. A última pesquisa nacional do instituto (BR-09503/2026, divulgada em 01/10) já está no CSV.
- Datafolha, Quaest e AtlasIntel: ainda não divulgadas no momento da verificação. Nenhum número foi estimado nem copiado de agregador ou rede social.
