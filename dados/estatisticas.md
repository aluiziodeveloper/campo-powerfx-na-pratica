# Massa do Teste de Realidade #1 — números gerados

*Gerado por `ferramentas/gerar_material.py`, semente 2026, data final 30/09/2026.*

## As duas sentinelas

| Sentinela | NumeroOS | ID esperado na lista | Título | Status | Local |
|---|---|---|---|---|---|
| Primeira | OS-000472 | 472 | Vibração no motor do exaustor E-14 | Aberta | Subestação Leste |
| Segunda | OS-012152 | 12152 | Vibração excessiva na bomba B-07 | Aberta | Estação Elevatória Leste |

O ID esperado supõe que a lista `Ocorrencias` recebeu os 351 registros da planilha (IDs 1 a 351) e nada mais
antes da carga. Se a sua lista já tiver outros itens, ou itens apagados, os IDs se deslocam; o que o teste exige é
que a primeira sentinela fique com ID até 500 e a segunda acima de 2.000. Confira depois da carga.

## Totais na lista depois da carga (planilha + massa)

- Registros: **12.351**
- Abertas (normalizando as grafias da planilha): **2.400**
- Em andamento: **619**
- Fechadas: **9.332**
- Abertas por unidade: média **60**, maior **179** (Estação Elevatória Leste), menor **27**

O Capítulo 11 trabalha com estes números arredondados: cerca de 12.350 registros, perto de 2.400 abertas,
sessenta por unidade no caso típico e cerca de cento e oitenta na maior.
