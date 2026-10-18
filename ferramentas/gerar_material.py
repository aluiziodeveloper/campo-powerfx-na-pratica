"""Gera o material de apoio de dados do livro "Power Fx na Prática".

Produz, de forma reprodutível (semente fixa):

  1. material/CAMPO_v0.0.xlsx — a planilha do Capítulo 0, com as sete abas, as
     doze fórmulas (F1 a F12) e a sujeira que o livro manda inventariar.
  2. dados/planilha_ocorrencias_351.csv e dados/unidades_40.csv — as duas abas
     que o Capítulo 4 transforma em listas, para quem prepara o ambiente pelo
     automatizador de carga em vez de importar a planilha.
  3. dados/ocorrencias_12000.csv — as 12.000 ordens de serviço do Teste de
     Realidade #1 (Capítulo 8), com as duas sentinelas.
  4. dados/lotes/lote_NNN.txt — os corpos das requisições $batch da API REST do
     SharePoint, que o fluxo de carga envia em sequência.
  5. dados/estatisticas.md e dados/esperado.json — os números da massa gerada,
     para conferência humana e para a conferência do automatizador.

Uso:
    python ferramentas/gerar_material.py [--fim AAAA-MM-DD] [--tamanho-lote 100]

--fim é a data da última ordem de serviço da massa (padrão: 2026-09-30).
Gere com a data em que você vai carregar a lista, para que "abertas há
mais de N dias" e as vencidas façam sentido no seu calendário.

Requer openpyxl (pip install openpyxl) apenas para a planilha.
"""
import argparse
import csv
import datetime as dt
import json
import os
import random

SEMENTE = 2026
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")

# ---------------------------------------------------------------- cadastros

UNIDADES = [
    "Subestação Norte", "Subestação Sul", "Subestação Leste", "Subestação Oeste",
    "Subestação Centro", "ETA Central", "ETA Serra Azul", "ETA Ribeirão Fundo",
    "ETE Vale do Sol", "ETE Rio Claro", "ETE Jardim Bela Vista", "Estação Elevatória Leste",
    "Estação Elevatória Oeste", "Estação Elevatória Porto", "Reservatório Alto da Colina",
    "Reservatório Santa Luzia", "Reservatório Industrial", "Captação Rio Verde",
    "Captação Lagoa Seca", "Adutora Tronco Norte", "Adutora Tronco Sul",
    "Oficina Mecânica Central", "Oficina Elétrica Central", "Almoxarifado Central",
    "Laboratório de Controle", "Sede Administrativa", "Centro de Operações",
    "Usina Fotovoltaica Cerrado", "Usina Fotovoltaica Planalto", "Pátio de Veículos",
    "Base Operacional Norte", "Base Operacional Sul", "Base Operacional Litoral",
    "Base Operacional Serra", "Galpão de Materiais", "Estação de Bombeamento Vila Nova",
    "Estação de Bombeamento Três Pontes", "Booster Morada do Sol", "Booster Parque das Águas",
    "Torre de Telecomunicação Morro Alto",
]
assert len(UNIDADES) == 40

SUPERVISORES = [
    "Adriana Campos", "Bruno Teixeira", "Carla Menezes", "Diego Fontana", "Elaine Prado",
    "Fábio Rezende", "Gisele Arantes", "Henrique Vasconcelos", "Isabela Moura", "João Batista Lemos",
    "Karina Duarte", "Leandro Siqueira", "Márcia Toledo", "Nelson Brandão", "Olívia Castro",
    "Paulo Henrique Dias", "Queila Ramos", "Renato Ventura", "Sabrina Lopes", "Tiago Moreira",
]
# Cada supervisor responde por duas unidades.
SUPERVISOR_DA_UNIDADE = {u: SUPERVISORES[i // 2] for i, u in enumerate(UNIDADES)}

TECNICOS = [
    ("Alex Nogueira", "Mecânica"), ("Beatriz Farias", "Elétrica"), ("Caio Rangel", "Hidráulica"),
    ("Daniela Pires", "Instrumentação"), ("Eduardo Salles", "Mecânica"), ("Fernanda Quintela", "Civil"),
    ("Gabriel Matos", "Elétrica"), ("Heloísa Barreto", "Hidráulica"), ("Igor Fonseca", "Mecânica"),
    ("Juliana Aguiar", "Instrumentação"), ("Kleber Antunes", "Elétrica"), ("Larissa Bezerra", "Civil"),
    ("Marcos Vinícius Rocha", "Mecânica"), ("Natália Cordeiro", "Hidráulica"), ("Otávio Lacerda", "Elétrica"),
    ("Priscila Guedes", "Instrumentação"), ("Rafael Torres", "Mecânica"), ("Simone Carvalho", "Civil"),
    ("Thiago Bastos", "Elétrica"), ("Úrsula Maia", "Hidráulica"), ("Vagner Pacheco", "Mecânica"),
    ("Wesley Cardoso", "Elétrica"), ("Yara Medeiros", "Instrumentação"), ("Zeca Moraes", "Mecânica"),
    ("Aline Rocha", "Hidráulica"), ("Bernardo Leal", "Elétrica"), ("Cíntia Freitas", "Civil"),
    ("Danilo Peixoto", "Mecânica"), ("Érica Andrade", "Hidráulica"), ("Flávio Gusmão", "Elétrica"),
    ("Glória Sampaio", "Instrumentação"), ("Hugo Albuquerque", "Mecânica"), ("Ingrid Queiroz", "Elétrica"),
    ("Jonas Teles", "Hidráulica"), ("Lívia Montenegro", "Civil"), ("Murilo Paiva", "Mecânica"),
]

# Problemas por área: (modelo de título, modelo de descrição). Nenhum contém
# "vibra" nem "B-07": essas palavras pertencem só às sentinelas.
PROBLEMAS = [
    ("Vazamento na bomba {eq}", "Vazamento pelo selo mecânico da bomba {eq}. Piso molhado ao redor da base."),
    ("Ruído anormal no motor {eq}", "Ruído intermitente no motor {eq} durante a partida. Temperatura normal ao toque."),
    ("Aquecimento no mancal do motor {eq}", "Mancal do motor {eq} acima da temperatura usual na medição com termômetro infravermelho."),
    ("Disjuntor desarmando no painel {eq}", "Disjuntor do painel {eq} desarmou três vezes no turno. Carga dentro do nominal."),
    ("Lâmpada queimada na área {eq}", "Iluminação da área {eq} sem funcionar. Reposição de lâmpada e conferência do reator."),
    ("Sensor de nível sem leitura no tanque {eq}", "Supervisório mostra leitura congelada do sensor de nível do tanque {eq}."),
    ("Válvula {eq} não fecha por completo", "Válvula {eq} com passagem residual mesmo totalmente fechada. Possível desgaste da sede."),
    ("Infiltração na parede da casa de bombas {eq}", "Mancha de umidade crescente na parede da casa de bombas {eq}."),
    ("Portão da área {eq} emperrado", "Portão de acesso da área {eq} exige força excessiva para abrir."),
    ("Medidor de vazão {eq} com leitura instável", "Medidor de vazão {eq} oscila sem variação de processo."),
    ("Troca de filtro do compressor {eq}", "Filtro de ar do compressor {eq} saturado. Substituição preventiva."),
    ("Falha de comunicação no CLP {eq}", "CLP {eq} perde comunicação com o supervisório em intervalos irregulares."),
    ("Correia do ventilador {eq} desgastada", "Correia do ventilador {eq} com trincas visíveis e folga excessiva."),
    ("Vazamento de óleo no redutor {eq}", "Gotejamento de óleo no redutor {eq}. Nível ainda dentro da faixa."),
    ("Bomba dosadora {eq} sem recalque", "Bomba dosadora {eq} liga mas não dosa. Mangueira sem obstrução aparente."),
    ("Calha entupida no prédio {eq}", "Calha do prédio {eq} transbordando em dia de chuva."),
    ("Tomada sem energia na sala {eq}", "Tomada de serviço da sala {eq} sem tensão."),
    ("Pintura descascada na estrutura {eq}", "Estrutura metálica {eq} com pontos de corrosão sob a pintura."),
    ("Exaustor {eq} parado", "Exaustor {eq} não parte. Fusível íntegro."),
    ("Ar-condicionado da sala {eq} sem refrigerar", "Ar-condicionado da sala de painéis {eq} ligado sem refrigerar."),
]

PRIORIDADES = [("Crítica", 0.07), ("Alta", 0.20), ("Média", 0.43), ("Baixa", 0.30)]


def escolher_ponderado(rng, pares):
    x = rng.random()
    acum = 0.0
    for valor, peso in pares:
        acum += peso
        if x <= acum:
            return valor
    return pares[-1][0]


def equipamento(rng):
    letra = rng.choice("ACDEFGHMPRTV")
    return f"{letra}-{rng.randint(1, 40):02d}"


def problema(rng):
    t, d = rng.choice(PROBLEMAS)
    eq = equipamento(rng)
    return t.format(eq=eq), d.format(eq=eq)


# Pesos das unidades: uma unidade grande (o triplo da média), três médias-altas,
# o resto entre metade e uma vez e meia da média. Ver Capítulo 11, "A conta que
# você precisa fazer".
def pesos_unidades(rng):
    pesos = {}
    for i, u in enumerate(UNIDADES):
        if u == "Estação Elevatória Leste":
            pesos[u] = 3.0
        elif i in (0, 5, 9):
            pesos[u] = 1.8
        else:
            pesos[u] = rng.uniform(0.5, 1.3)
    total = sum(pesos.values())
    media = total / len(pesos)
    # normaliza para que a média seja 1
    return {u: p / media for u, p in pesos.items()}


# ---------------------------------------------------------------- planilha v0.0

def gerar_ocorrencias_planilha(rng):
    """351 linhas, em ordem cronológica de registro (linhas 2 a 352)."""
    linhas = []
    pesos = pesos_unidades(rng)
    unidades_pond = list(pesos.items())
    soma = sum(p for _, p in unidades_pond)
    unidades_pond = [(u, p / soma) for u, p in unidades_pond]

    # Variantes de Status digitadas antes da validação de dados (segundo ano
    # da planilha). Só sobreviveram as que nunca foram fechadas, porque o
    # arquivamento anual leva apenas as fechadas.
    variantes = ["Aberto"] * 9 + ["aberta"] * 7 + ["Em Andamento"] * 6
    rng.shuffle(variantes)

    numero = 0
    # 1) 22 pendências antigas (2023 e início de 2024), nunca fechadas
    base = dt.datetime(2023, 3, 6, 8, 0)
    for k, st in enumerate(variantes):
        numero = 140 + k * 37
        data = base + dt.timedelta(days=k * 21, hours=rng.randint(0, 9), minutes=rng.choice([0, 10, 20, 30, 40, 50]))
        linhas.append({"NumeroOS": f"OS-{numero:04d}", "Status": st, "DataAbertura": data})
    # 2) 14 pendências de 2025 ainda abertas ou em andamento
    for k in range(14):
        numero = 1520 + k * 81
        data = dt.datetime(2025, 1, 10, 8, 0) + dt.timedelta(days=k * 25, hours=rng.randint(0, 9))
        linhas.append({"NumeroOS": f"OS-{numero:04d}", "Status": rng.choice(["Aberta", "Em andamento"]), "DataAbertura": data})
    # 3) 315 do ano corrente, de 05/01/2026 a 11/09/2026 (sexta-feira)
    inicio = dt.datetime(2026, 1, 5, 7, 30)
    fim = dt.datetime(2026, 9, 11, 17, 30)
    n = 351 - len(linhas)
    passo = (fim - inicio) / (n - 1)
    numero = 2700
    for k in range(n):
        data = inicio + passo * k + dt.timedelta(minutes=rng.randint(-40, 40))
        idade = (fim - data).days
        if idade < 10:
            st = escolher_ponderado(rng, [("Aberta", 0.65), ("Em andamento", 0.25), ("Fechada", 0.10)])
        elif idade < 45:
            st = escolher_ponderado(rng, [("Aberta", 0.30), ("Em andamento", 0.25), ("Fechada", 0.45)])
        else:
            st = escolher_ponderado(rng, [("Aberta", 0.05), ("Em andamento", 0.05), ("Fechada", 0.90)])
        numero += 1
        linhas.append({"NumeroOS": f"OS-{numero:04d}", "Status": st, "DataAbertura": data})

    for ln in linhas:
        ln["Titulo"], ln["Descricao"] = problema(rng)
        ln["Prioridade"] = escolher_ponderado(rng, PRIORIDADES)
        ln["Local"] = escolher_ponderado(rng, unidades_pond)
        ln["Responsavel"] = rng.choice(TECNICOS)[0]

    # Museu #0: críticas abertas entre as linhas 301 e 352 (índices 299 a 350),
    # que o CONT.SES(G2:G300; ...) deixa de contar.
    for idx in (305, 318, 331, 344, 349):
        linhas[idx - 2]["Prioridade"] = "Crítica"
        linhas[idx - 2]["Status"] = "Aberta"

    # Locais digitados de um jeito que a aba Unidades não reconhece (o SEERRO da F4 os esconde)
    locais_sujos = ["Subestacao Norte", "ETA Central ", "Est. Elevatória Oeste", "Almoxarifado", "ETE Rio claro", "Base Op. Sul", "Laboratorio de Controle"]
    for idx, loc in zip((31, 77, 120, 158, 203, 247, 290), locais_sujos):
        linhas[idx - 2]["Local"] = loc

    # 47 sem responsável: as abertas mais recentes ainda sem atribuição, e algumas antigas
    abertas_recentes = [i for i in range(len(linhas) - 1, -1, -1) if linhas[i]["Status"] == "Aberta"]
    sem_resp = set(abertas_recentes[:30])
    restantes = [i for i in range(len(linhas)) if i not in sem_resp]
    rng.shuffle(restantes)
    sem_resp |= set(restantes[:47 - len(sem_resp)])
    for i in sem_resp:
        linhas[i]["Responsavel"] = None
    # 12 sem data de abertura
    candidatos = [i for i in range(40, len(linhas)) if i + 2 not in (305, 318, 331, 344, 349)]
    for i in rng.sample(candidatos, 12):
        linhas[i]["DataAbertura"] = None

    # nenhum título de vibração na planilha (a busca do Capítulo 8 depende disso)
    for ln in linhas:
        assert "vibra" not in (ln["Titulo"] + ln["Descricao"]).lower()
    return linhas


def gerar_arquivo_2025(rng):
    linhas = []
    inicio = dt.datetime(2025, 1, 2, 7, 30)
    for k in range(1180):
        data = inicio + dt.timedelta(minutes=int(k * (360 * 24 * 60) / 1180) + rng.randint(-30, 30))
        t, d = problema(rng)
        linhas.append({
            "NumeroOS": f"OS-{1500 + k:04d}", "Titulo": t, "Descricao": d, "Local": rng.choice(UNIDADES),
            "Prioridade": escolher_ponderado(rng, PRIORIDADES), "Responsavel": rng.choice(TECNICOS)[0],
            "Status": "Fechada", "DataAbertura": data,
        })
    return linhas


def escrever_planilha(linhas, arquivo2025, caminho):
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.workbook.defined_name import DefinedName
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.worksheet.table import Table, TableStyleInfo

    wb = Workbook()
    leia = wb.active
    leia.title = "LEIA-ME"
    leia["A1"] = "CONTROLE DE OCORRÊNCIAS — LEIA ANTES DE MEXER"
    leia["A1"].font = Font(bold=True, size=14)
    avisos = [
        "1. NÃO ORDENE A TABELA SEM SELECIONAR TUDO.",
        "2. NÃO MEXA NA COLUNA L.",
        "3. NO FIM DO MÊS, ARQUIVE AS OCORRÊNCIAS FECHADAS NA ABA DE ARQUIVO.",
    ]
    for i, a in enumerate(avisos, start=3):
        leia.cell(row=i, column=1, value=a).font = Font(bold=True, color="C00000")
    leia["A8"] = "Arquivo de exemplo do livro Power Fx na Prática (Capítulo 0). Dados fictícios: pessoas e unidades inventadas."
    leia["A8"].font = Font(italic=True, color="808080")
    leia.column_dimensions["A"].width = 90

    # ---- Ocorrencias
    ws = wb.create_sheet("Ocorrencias")
    cab = ["NumeroOS", "Titulo", "Descricao", "Local", "Prioridade", "Responsavel", "Status",
           "DataAbertura", "Prazo", "Atrasada", "Supervisor", "NÃO MEXER"]
    ws.append(cab)
    T = "Ocorrencias[[#This Row],[{}]]"
    for ln in linhas:
        ws.append([
            ln["NumeroOS"], ln["Titulo"], ln["Descricao"], ln["Local"], ln["Prioridade"],
            ln["Responsavel"], ln["Status"], ln["DataAbertura"],
            # F2 — prazo por prioridade (SE aninhado)
            f'=IF({T.format("Prioridade")}="Crítica",{T.format("DataAbertura")}+1,'
            f'IF({T.format("Prioridade")}="Alta",{T.format("DataAbertura")}+3,{T.format("DataAbertura")}+10))',
            # F3 — atraso
            f'=IF(AND({T.format("Status")}<>"Fechada",TODAY()>{T.format("Prazo")}),"SIM","")',
            # F4 — supervisor
            f'=IFERROR(VLOOKUP({T.format("Local")},Unidades!A:B,2,FALSE),"")',
            # F1 — dias em aberto (a coluna "NÃO MEXER")
            f'=IF({T.format("Status")}="Fechada","",TODAY()-{T.format("DataAbertura")})',
        ])
    ult = len(linhas) + 1
    tab = Table(displayName="Ocorrencias", ref=f"A1:L{ult}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(tab)
    for r in range(2, ult + 1):
        ws.cell(row=r, column=8).number_format = "dd/mm/yyyy hh:mm"
        ws.cell(row=r, column=9).number_format = "dd/mm/yyyy"
        ws.cell(row=r, column=12).number_format = "0"
    ws["L1"].fill = PatternFill("solid", fgColor="FF0000")
    ws["L1"].font = Font(bold=True, color="FFFFFF")
    ws["L1"].comment = Comment("Coluna DiasEmAberto. Alguém colou valores por cima da fórmula uma vez. NÃO MEXER.", "Supervisão")
    larguras = [11, 42, 60, 30, 11, 24, 15, 17, 12, 10, 22, 12]
    for i, w in enumerate(larguras):
        ws.column_dimensions[chr(65 + i)].width = w

    # validação de dados (criada no segundo ano: vale só para o que se digita depois dela)
    dv_st = DataValidation(type="list", formula1="=Listas!$A$2:$A$4", allow_blank=True)
    dv_pr = DataValidation(type="list", formula1="=Listas!$B$2:$B$5", allow_blank=True)
    ws.add_data_validation(dv_st)
    ws.add_data_validation(dv_pr)
    dv_st.add(f"G2:G{ult + 500}")
    dv_pr.add(f"E2:E{ult + 500}")

    # ---- Painel
    p = wb.create_sheet("Painel")
    p["A1"] = "PAINEL DE OCORRÊNCIAS"
    p["A1"].font = Font(bold=True, size=13)
    # F12 — carimbo de atualização: sabe só que dia é hoje
    p["B1"] = '="Atualizado em "&TEXT(DAY(TODAY()),"00")&"/"&TEXT(MONTH(TODAY()),"00")&"/"&YEAR(TODAY())'
    rotulos = {
        3: ("Abertas", '=COUNTIF(Ocorrencias[Status],"Aberta")'),                      # F5
        4: ("Em andamento", '=COUNTIF(Ocorrencias[Status],"Em andamento")'),           # F6
        5: ("Fechadas", '=COUNTIF(Ocorrencias[Status],"Fechada")'),                    # F7
        7: ("Críticas em aberto", '=COUNTIFS(Ocorrencias!G2:G300,"Aberta",Ocorrencias!E2:E300,"Crítica")'),  # F8
        8: ("Atrasadas", '=COUNTIF(Ocorrencias[Atrasada],"SIM")'),                    # F9
        9: ("Percentual de atraso", '=IFERROR(B8/(B3+B4),0)'),                        # F11
    }
    for r, (rot, f) in rotulos.items():
        p.cell(row=r, column=1, value=rot).font = Font(bold=True)
        p.cell(row=r, column=2, value=f)
    p["B9"].number_format = "0.0%"
    p["A11"] = "Abertas por unidade"
    p["A11"].font = Font(bold=True)
    for i, u in enumerate(UNIDADES):
        r = 12 + i
        p.cell(row=r, column=1, value=u)
        # F10 — a mesma fórmula, quarenta vezes
        p.cell(row=r, column=2, value=f'=COUNTIFS(Ocorrencias[Local],A{r},Ocorrencias[Status],"Aberta")')
    p.column_dimensions["A"].width = 38
    p.column_dimensions["B"].width = 24
    for nome, ref in [("Abertas", "$B$3"), ("EmAndamento", "$B$4"), ("Fechadas", "$B$5"),
                      ("Criticas", "$B$7"), ("Atrasadas", "$B$8"), ("PercentualAtraso", "$B$9"),
                      ("PorUnidade", "$B$12:$B$51")]:
        wb.defined_names[nome] = DefinedName(nome, attr_text=f"Painel!{ref}")

    # ---- Unidades
    u = wb.create_sheet("Unidades")
    u.append(["Nome", "Supervisor"])
    for nome in UNIDADES:
        u.append([nome, SUPERVISOR_DA_UNIDADE[nome]])
    u.column_dimensions["A"].width = 38
    u.column_dimensions["B"].width = 26

    # ---- Equipe
    e = wb.create_sheet("Equipe")
    e.append(["Nome", "Funcao", "Area"])
    for s in SUPERVISORES:
        e.append([s, "Supervisor", "Operação"])
    for nome, area in TECNICOS:
        e.append([nome, "Técnico", area])
    e.column_dimensions["A"].width = 26

    # ---- Listas
    li = wb.create_sheet("Listas")
    li.append(["Status", "Prioridade"])
    for st, pr in zip(["Aberta", "Em andamento", "Fechada", None], ["Crítica", "Alta", "Média", "Baixa"]):
        li.append([st, pr])

    # ---- Arquivo_2025 (colado à mão: valores, sem fórmula)
    a = wb.create_sheet("Arquivo_2025")
    a.append(cab[:8])
    for ln in arquivo2025:
        a.append([ln[c] for c in cab[:8]])
    for r in range(2, len(arquivo2025) + 2):
        a.cell(row=r, column=8).number_format = "dd/mm/yyyy hh:mm"

    for w in wb.worksheets:
        w.sheet_view.zoomScale = 100
    wb.calculation.fullCalcOnLoad = True
    wb.save(caminho)


# ---------------------------------------------------------------- massa de 12.000

def gerar_massa(rng, fim, planilha_registros=351):
    pesos = pesos_unidades(rng)
    soma = sum(pesos.values())
    unidades_pond = [(u, p / soma) for u, p in pesos.items()]
    inicio = fim - dt.timedelta(days=548)
    n = 12000
    massa = []
    for k in range(n):
        data = inicio + dt.timedelta(seconds=int(k * (548 * 86400) / n)) + dt.timedelta(minutes=rng.randint(-20, 20))
        data = data.replace(second=0, microsecond=0)
        idade = (fim - data).days
        if idade < 7:
            st = escolher_ponderado(rng, [("Aberta", 0.75), ("Em andamento", 0.18), ("Fechada", 0.07)])
        elif idade < 30:
            st = escolher_ponderado(rng, [("Aberta", 0.45), ("Em andamento", 0.20), ("Fechada", 0.35)])
        elif idade < 90:
            st = escolher_ponderado(rng, [("Aberta", 0.25), ("Em andamento", 0.10), ("Fechada", 0.65)])
        else:
            st = escolher_ponderado(rng, [("Aberta", 0.165), ("Em andamento", 0.03), ("Fechada", 0.805)])
        t, d = problema(rng)
        resp = None if (st == "Aberta" and rng.random() < 0.12) else rng.choice(TECNICOS)[0]
        massa.append({
            "Titulo": t, "Descricao": d, "Status": st, "Prioridade": escolher_ponderado(rng, PRIORIDADES),
            "Local": escolher_ponderado(rng, unidades_pond), "DataAbertura": data, "Responsavel": resp,
        })
    # sentinelas
    s1, s2 = 120, 11800
    massa[s1].update({
        "Titulo": "Vibração no motor do exaustor E-14",
        "Descricao": "Vibração perceptível no motor do exaustor E-14 em carga plena. Fixação da base conferida.",
        "Status": "Aberta", "Prioridade": "Alta", "Local": "Subestação Leste", "Responsavel": "Igor Fonseca",
    })
    massa[s2].update({
        "Titulo": "Vibração excessiva na bomba B-07",
        "Descricao": "Vibração excessiva no mancal da bomba B-07, ruído crescente desde a semana passada.",
        "Status": "Aberta", "Prioridade": "Crítica", "Local": "Estação Elevatória Leste", "Responsavel": None,
    })
    for i, m in enumerate(massa):
        texto = (m["Titulo"] + " " + m["Descricao"]).lower()
        if i not in (s1, s2):
            assert "vibra" not in texto and "b-07" not in texto
        # ID que o SharePoint atribuirá, se a lista tiver os 351 registros da planilha
        m["ID_esperado"] = planilha_registros + i + 1
        m["NumeroOS"] = f"OS-{m['ID_esperado']:06d}"
    return massa, (s1, s2)


COLUNAS = ["NumeroOS", "Titulo", "Descricao", "Status", "Prioridade", "Local", "DataAbertura", "Responsavel"]


def escrever_csv(massa, caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ID_esperado"] + COLUNAS)
        for m in massa:
            w.writerow([m["ID_esperado"]] + [
                m["DataAbertura"].strftime("%Y-%m-%dT%H:%M:%S") if c == "DataAbertura" else (m[c] or "")
                for c in COLUNAS])


# Os horários do CSV são de Brasília (UTC-3, sem horário de verão desde 2019). Os
# lotes e os roteiros de carga gravam em UTC, para que o instante salvo não dependa
# do fuso do computador de quem carrega nem do fuso regional do site (Capítulo 9).
FUSO_DOS_DADOS_HORAS = -3


def utc(data):
    return (data - dt.timedelta(hours=FUSO_DOS_DADOS_HORAS)).strftime("%Y-%m-%dT%H:%M:%SZ")


def escrever_planilha_csv(planilha, caminho):
    """As 351 linhas da aba Ocorrencias, só as oito colunas de dado, do jeito que
    estão na planilha (com as seis grafias de Status, os brancos e os locais sujos):
    é o que a importação do Capítulo 4 leva para a lista."""
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ID_esperado"] + COLUNAS)
        for i, l in enumerate(planilha, start=1):
            w.writerow([i] + [
                (l["DataAbertura"].strftime("%Y-%m-%dT%H:%M:%S") if l["DataAbertura"] else "") if c == "DataAbertura"
                else (l[c] or "") for c in COLUNAS])


def escrever_unidades_csv(caminho):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Nome", "Supervisor"])
        for u in UNIDADES:
            w.writerow([u, SUPERVISOR_DA_UNIDADE[u]])


def escrever_lotes(massa, pasta, tamanho):
    """Corpos multipart para POST {site}/_api/$batch, um arquivo por lote.

    O marcador {{SITE}} é trocado pela URL do site no fluxo. Os itens de um
    lote estão num único changeset, executado em ordem; os lotes rodam em
    sequência, e por isso o ID de cada item segue a ordem do arquivo.
    """
    os.makedirs(pasta, exist_ok=True)
    for f in os.listdir(pasta):
        if f.startswith("lote_"):
            os.remove(os.path.join(pasta, f))
    CRLF = "\r\n"
    for n, ini in enumerate(range(0, len(massa), tamanho), start=1):
        cs = f"changeset_campo_{n:03d}"
        partes = [f"--batch_campo", f'Content-Type: multipart/mixed; boundary="{cs}"',
                  "Content-Transfer-Encoding: binary", ""]
        for m in massa[ini:ini + tamanho]:
            corpo = {
                "Title": m["Titulo"], "NumeroOS": m["NumeroOS"], "Descricao": m["Descricao"],
                "Status": m["Status"], "Prioridade": m["Prioridade"], "Local": m["Local"],
                "DataAbertura": utc(m["DataAbertura"]),
                "Responsavel": m["Responsavel"],
            }
            partes += [f"--{cs}", "Content-Type: application/http", "Content-Transfer-Encoding: binary", "",
                       "POST {{SITE}}/_api/web/lists/getbytitle('Ocorrencias')/items HTTP/1.1",
                       "Content-Type: application/json;odata=nometadata",
                       "Accept: application/json;odata=nometadata", "",
                       json.dumps(corpo, ensure_ascii=False), ""]
        partes += [f"--{cs}--", "--batch_campo--", ""]
        with open(os.path.join(pasta, f"lote_{n:03d}.txt"), "w", encoding="utf-8", newline="") as f:
            f.write(CRLF.join(partes))
    return n


def estatisticas(planilha, massa, sentinelas, fim, caminho):
    from collections import Counter
    tudo = [{"Status": l["Status"], "Local": l["Local"]} for l in planilha] + massa
    def norm(s):
        return {"aberto": "Aberta", "aberta": "Aberta", "em andamento": "Em andamento"}.get(s.lower(), s)
    st = Counter(norm(x["Status"]) for x in tudo)
    abertas_un = Counter(x["Local"] for x in tudo if norm(x["Status"]) == "Aberta")
    s1, s2 = sentinelas
    linhas = [
        "# Massa do Teste de Realidade #1 — números gerados",
        "",
        f"*Gerado por `ferramentas/gerar_material.py`, semente {SEMENTE}, data final {fim:%d/%m/%Y}.*",
        "",
        "## As duas sentinelas",
        "",
        "| Sentinela | NumeroOS | ID esperado na lista | Título | Status | Local |",
        "|---|---|---|---|---|---|",
    ]
    for nome, i in (("Primeira", s1), ("Segunda", s2)):
        m = massa[i]
        linhas.append(f"| {nome} | {m['NumeroOS']} | {m['ID_esperado']} | {m['Titulo']} | {m['Status']} | {m['Local']} |")
    linhas += [
        "",
        "O ID esperado supõe que a lista `Ocorrencias` recebeu os 351 registros da planilha (IDs 1 a 351) e nada mais",
        "antes da carga. Se a sua lista já tiver outros itens, ou itens apagados, os IDs se deslocam; o que o teste exige é",
        "que a primeira sentinela fique com ID até 500 e a segunda acima de 10.000, o teto do limite de linhas. Confira depois da carga.",
        "",
        "## Totais na lista depois da carga (planilha + massa)",
        "",
        f"- Registros: **{len(tudo):,}**".replace(",", "."),
        f"- Abertas (normalizando as grafias da planilha): **{st['Aberta']:,}**".replace(",", "."),
        f"- Em andamento: **{st['Em andamento']:,}**".replace(",", "."),
        f"- Fechadas: **{st['Fechada']:,}**".replace(",", "."),
        f"- Abertas por unidade: média **{st['Aberta'] / 40:.0f}**, maior **{max(abertas_un.values())}** "
        f"({abertas_un.most_common(1)[0][0]}), menor **{min(abertas_un[u] for u in UNIDADES)}**",
        "",
        "O Capítulo 11 trabalha com estes números arredondados: cerca de 12.350 registros, perto de 2.400 abertas,",
        "sessenta por unidade no caso típico e cerca de cento e oitenta na maior.",
        "",
    ]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    esperado = {
        "gerado_com": {"semente": SEMENTE, "fim": fim.strftime("%Y-%m-%d")},
        "lista": "Ocorrencias",
        "registros_planilha": len(planilha),
        "registros_massa": len(massa),
        "total": len(tudo),
        "por_status": {k: st[k] for k in ("Aberta", "Em andamento", "Fechada")},
        "status_normalizado": "as grafias Aberto/aberta/Em Andamento da planilha contam como Aberta/Em andamento",
        "sentinelas": [
            {"nome": nome, "NumeroOS": massa[i]["NumeroOS"], "indice_na_massa": i,
             "ID_esperado": massa[i]["ID_esperado"], "Titulo": massa[i]["Titulo"], "regra": regra}
            for nome, i, regra in (("primeira", s1, "ID <= 500"), ("segunda", s2, "ID > 10000"))
        ],
    }
    with open(os.path.join(os.path.dirname(caminho), "esperado.json"), "w", encoding="utf-8") as f:
        json.dump(esperado, f, ensure_ascii=False, indent=2)
    return st, abertas_un


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fim", default="2026-09-30")
    # A documentação do $batch não publica um teto de operações por requisição; 100 é o
    # tamanho que o PnP usa internamente e o que os roteiros de carga deste repositório usam.
    ap.add_argument("--tamanho-lote", type=int, default=100)
    ap.add_argument("--sem-planilha", action="store_true")
    a = ap.parse_args()
    fim = dt.datetime.strptime(a.fim, "%Y-%m-%d").replace(hour=17, minute=0)

    rng = random.Random(SEMENTE)
    planilha = gerar_ocorrencias_planilha(rng)
    arquivo2025 = gerar_arquivo_2025(rng)
    if not a.sem_planilha:
        escrever_planilha(planilha, arquivo2025, os.path.join(RAIZ, "material", "CAMPO_v0.0.xlsx"))

    rng_m = random.Random(SEMENTE + 1)
    massa, sent = gerar_massa(rng_m, fim)
    pasta = DADOS
    os.makedirs(pasta, exist_ok=True)
    escrever_planilha_csv(planilha, os.path.join(pasta, "planilha_ocorrencias_351.csv"))
    escrever_unidades_csv(os.path.join(pasta, "unidades_40.csv"))
    escrever_csv(massa, os.path.join(pasta, "ocorrencias_12000.csv"))
    n = escrever_lotes(massa, os.path.join(pasta, "lotes"), a.tamanho_lote)
    st, un = estatisticas(planilha, massa, sent, fim, os.path.join(pasta, "estatisticas.md"))

    # conferência dos números que o livro afirma sobre a planilha
    grafias = sorted({l["Status"] for l in planilha})
    print("grafias de Status:", grafias)
    print("sem responsável:", sum(1 for l in planilha if not l["Responsavel"]))
    print("sem data:", sum(1 for l in planilha if not l["DataAbertura"]))
    print("registros:", len(planilha), "arquivo_2025:", len(arquivo2025))
    crit_fora = sum(1 for i, l in enumerate(planilha) if i + 2 > 300 and l["Status"] == "Aberta" and l["Prioridade"] == "Crítica")
    print("críticas abertas fora de G2:G300:", crit_fora)
    print("lotes:", n, "status:", dict(st), "maior unidade:", un.most_common(1))


if __name__ == "__main__":
    main()
