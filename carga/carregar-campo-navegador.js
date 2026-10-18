/*
 * Carga do CAMPO pelo navegador — material de apoio de "Power Fx na Prática" (Capítulos 5, 9 e 12).
 *
 * Faz o mesmo que Carregar-CAMPO.ps1, sem instalar nada e sem registrar aplicativo no
 * Microsoft Entra ID: roda na página do próprio site do SharePoint, com a sessão de quem
 * está entrando, e só conversa com esse site (API REST do SharePoint, requisições $batch).
 *
 * Como usar (o README desta pasta tem o passo a passo):
 *   1. Entre no site do SharePoint onde a lista vai morar.
 *   2. Abra as ferramentas do desenvolvedor (F12), aba Console.
 *   3. Leia este arquivo antes de colar. Depois cole e tecle Enter.
 *   4. No painel que aparece, escolha os arquivos da pasta dados/ e as etapas.
 *
 * Etapas: Listas (cria Ocorrencias e Unidades com as colunas e os seis índices do
 * Capítulo 5), Planilha (351 registros e 40 unidades), Massa (12.000 OS em lotes de 100,
 * em sequência; se for interrompida, a nova execução grava só o que falta) e Conferir
 * (totais por status e ID das duas sentinelas contra esperado.json).
 */
(function (raiz) {
  "use strict";

  const LISTA = "Ocorrencias";
  const LISTA_UNIDADES = "Unidades";
  const TAMANHO_LOTE = 100;
  const FUSO_DOS_DADOS = "-03:00"; // horários do CSV são de Brasília; grava-se em UTC (Capítulo 10)

  const COLUNAS = [
    { nome: "NumeroOS", tipo: "Text", indice: true },
    { nome: "Descricao", tipo: "Note", indice: false },
    { nome: "Status", tipo: "Text", indice: true },
    { nome: "Prioridade", tipo: "Text", indice: true },
    { nome: "Local", tipo: "Text", indice: true },
    { nome: "DataAbertura", tipo: "DateTime", indice: true },
    { nome: "Responsavel", tipo: "Text", indice: false },
  ];

  // ------------------------------------------------------------ funções puras

  /** CSV com separador ";", aspas duplas como no Excel, BOM e CRLF tolerados. */
  function lerCsv(texto) {
    texto = texto.replace(/^﻿/, "");
    const linhas = [];
    let campo = "", linha = [], aspas = false;
    for (let i = 0; i < texto.length; i++) {
      const c = texto[i];
      if (aspas) {
        if (c === '"' && texto[i + 1] === '"') { campo += '"'; i++; }
        else if (c === '"') aspas = false;
        else campo += c;
      } else if (c === '"') aspas = true;
      else if (c === ";") { linha.push(campo); campo = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && texto[i + 1] === "\n") i++;
        linha.push(campo); campo = "";
        if (linha.length > 1 || linha[0] !== "") linhas.push(linha);
        linha = [];
      } else campo += c;
    }
    if (campo !== "" || linha.length) { linha.push(campo); linhas.push(linha); }
    const [cabecalho, ...dados] = linhas;
    return dados.map((l) => Object.fromEntries(cabecalho.map((c, i) => [c, l[i] ?? ""])));
  }

  function paraUtc(texto) {
    if (!texto) return null;
    return new Date(texto + FUSO_DOS_DADOS).toISOString().replace(".000Z", "Z");
  }

  function valores(linha) {
    const v = {
      Title: linha.Titulo, NumeroOS: linha.NumeroOS, Descricao: linha.Descricao,
      Status: linha.Status, Prioridade: linha.Prioridade, Local: linha.Local,
    };
    const data = paraUtc(linha.DataAbertura);
    if (data) v.DataAbertura = data;
    if (linha.Responsavel) v.Responsavel = linha.Responsavel;
    return v;
  }

  /** Corpo multipart de um POST {web}/_api/$batch com um changeset de criações. */
  function montarLote(web, lista, tipoEntidade, itens, n) {
    const lote = `batch_campo_${n}`, cs = `changeset_campo_${n}`;
    const p = [`--${lote}`, `Content-Type: multipart/mixed; boundary="${cs}"`, "Content-Transfer-Encoding: binary", ""];
    for (const valoresItem of itens) {
      const corpo = Object.assign({ __metadata: { type: tipoEntidade } }, valoresItem);
      p.push(`--${cs}`, "Content-Type: application/http", "Content-Transfer-Encoding: binary", "",
        `POST ${web}/_api/web/lists/getbytitle('${lista}')/items HTTP/1.1`,
        "Content-Type: application/json;odata=verbose", "Accept: application/json;odata=nometadata", "",
        JSON.stringify(corpo), "");
    }
    p.push(`--${cs}--`, `--${lote}--`, "");
    return { limite: lote, corpo: p.join("\r\n") };
  }

  /** O $batch responde 200 mesmo quando itens falham: o status de cada um vem no corpo. */
  function lerRespostaLote(texto) {
    const status = [...texto.matchAll(/^HTTP\/1\.1 (\d{3})[^\r\n]*/gm)].map((m) => Number(m[1]));
    const falhas = [];
    status.forEach((s, i) => { if (s >= 400) falhas.push({ posicao: i, status: s }); });
    const msg = texto.match(/"message"\s*:\s*(?:\{[^}]*"value"\s*:\s*)?"([^"]+)"/);
    return { gravados: status.filter((s) => s === 201).length, falhas, mensagem: msg ? msg[1] : "" };
  }

  /** O que falta gravar da massa, e se a posição das sentinelas ainda serve ao teste. */
  function planejarMassa(massa, presentes, ultimo, esperado) {
    const indice = new Map(massa.map((m, i) => [m.NumeroOS, i]));
    if (ultimo && indice.has(ultimo.NumeroOS)) {
      const fim = indice.get(ultimo.NumeroOS);
      const pendentes = massa.filter((m) => !presentes.has(m.NumeroOS));
      const buracos = pendentes.filter((m) => indice.get(m.NumeroOS) < fim).length;
      return { retomada: true, pendentes, buracos };
    }
    const proximo = ultimo ? ultimo.ID + 1 : 1;
    const estimativas = esperado.sentinelas.map((s) => ({ NumeroOS: s.NumeroOS, id: proximo + s.indice_na_massa }));
    return { retomada: false, pendentes: massa, proximo, estimativas, posicaoServe: estimativas[0].id <= 500 };
  }

  function contarStatus(itens) {
    const normal = { "aberta": "Aberta", "aberto": "Aberta", "em andamento": "Em andamento", "fechada": "Fechada" };
    const grafias = {}, porStatus = {};
    for (const it of itens) {
      const st = it.Status ?? "";
      grafias[st] = (grafias[st] || 0) + 1;
      const k = normal[st.trim().toLowerCase()] || st;
      porStatus[k] = (porStatus[k] || 0) + 1;
    }
    return { total: itens.length, grafias, porStatus };
  }

  const puras = { lerCsv, paraUtc, valores, montarLote, lerRespostaLote, planejarMassa, contarStatus };

  // ------------------------------------------------------------ SharePoint

  const espera = (ms) => new Promise((r) => setTimeout(r, ms));

  function urlDoSite() {
    const m = location.pathname.match(/^\/(sites|teams)\/[^/]+/i);
    return location.origin + (m ? m[0] : "");
  }

  class Site {
    constructor(web, registrar) { this.web = web; this.registrar = registrar; this.digest = null; this.validade = 0; }

    async chave() {
      if (this.digest && Date.now() < this.validade) return this.digest;
      const r = await fetch(`${this.web}/_api/contextinfo`, { method: "POST", headers: { Accept: "application/json;odata=nometadata" }, credentials: "include" });
      if (!r.ok) throw new Error(`Não consegui a chave de formulário do site (${r.status}). Você está no site certo, com permissão de edição?`);
      const j = await r.json();
      this.digest = j.FormDigestValue;
      this.validade = Date.now() + (j.FormDigestTimeoutSeconds - 120) * 1000;
      return this.digest;
    }

    /** Requisição com nova tentativa quando o serviço pede para esperar (429 e 503). */
    async pedir(caminho, opcoes = {}, tentativas = 8) {
      for (let t = 1; ; t++) {
        const headers = Object.assign({ Accept: "application/json;odata=nometadata" }, opcoes.headers || {});
        if (opcoes.method && opcoes.method !== "GET") headers["X-RequestDigest"] = await this.chave();
        const r = await fetch(caminho.startsWith("http") ? caminho : `${this.web}${caminho}`, Object.assign({}, opcoes, { headers, credentials: "include" }));
        if ((r.status === 429 || r.status === 503) && t < tentativas) {
          const s = Number(r.headers.get("Retry-After")) || Math.min(2 ** t, 120);
          this.registrar(`  o serviço pediu para esperar ${s} s (código ${r.status}); tentativa ${t + 1}`);
          await espera(s * 1000);
          continue;
        }
        return r;
      }
    }

    async json(caminho, opcoes) {
      const r = await this.pedir(caminho, opcoes);
      if (!r.ok) throw new Error(`${opcoes && opcoes.method || "GET"} ${caminho}: ${r.status} ${await r.text()}`);
      return r.status === 204 ? null : r.json();
    }

    async lista(nome) {
      const r = await this.pedir(`/_api/web/lists/getbytitle('${nome}')?$select=Id,ItemCount,ListItemEntityTypeFullName`);
      if (r.status === 404) return null;
      if (!r.ok) throw new Error(`Lendo a lista ${nome}: ${r.status}`);
      return r.json();
    }

    async criarLista(nome, tituloDaColunaTitle) {
      await this.json("/_api/web/lists", {
        method: "POST", headers: { "Content-Type": "application/json;odata=verbose" },
        body: JSON.stringify({ __metadata: { type: "SP.List" }, BaseTemplate: 100, Title: nome, OnQuickLaunch: true }),
      });
      await this.alterarCampo(nome, "Title", { Title: tituloDaColunaTitle });
    }

    async campoExiste(lista, nome) {
      const r = await this.pedir(`/_api/web/lists/getbytitle('${lista}')/fields/getbyinternalnameortitle('${nome}')?$select=InternalName`);
      return r.ok;
    }

    async criarCampo(lista, c) {
      const extra = c.tipo === "Note" ? " NumLines='6' RichText='FALSE'" : c.tipo === "DateTime" ? " Format='DateTime'" : "";
      const xml = `<Field Type='${c.tipo}' DisplayName='${c.nome}' Name='${c.nome}' StaticName='${c.nome}'${extra} />`;
      await this.json(`/_api/web/lists/getbytitle('${lista}')/fields/createfieldasxml`, {
        method: "POST", headers: { "Content-Type": "application/json;odata=verbose", Accept: "application/json;odata=verbose" },
        // 8 = usar o nome interno informado; 16 = acrescentar à exibição padrão
        body: JSON.stringify({ parameters: { __metadata: { type: "SP.XmlSchemaFieldCreationInformation" }, SchemaXml: xml, Options: 24 } }),
      });
    }

    async alterarCampo(lista, nome, valores) {
      await this.json(`/_api/web/lists/getbytitle('${lista}')/fields/getbyinternalnameortitle('${nome}')`, {
        method: "POST",
        headers: { "Content-Type": "application/json;odata=verbose", "X-HTTP-Method": "MERGE", "IF-MATCH": "*" },
        body: JSON.stringify(Object.assign({ __metadata: { type: "SP.Field" } }, valores)),
      });
    }

    async ultimoItem(lista) {
      const j = await this.json(`/_api/web/lists/getbytitle('${lista}')/items?$select=ID,NumeroOS&$orderby=ID desc&$top=1`);
      return j.value[0] || null;
    }

    async todosOsItens(lista, campos) {
      const itens = [];
      let url = `/_api/web/lists/getbytitle('${lista}')/items?$select=ID,${campos}&$top=5000`;
      while (url) {
        const j = await this.json(url);
        itens.push(...j.value);
        url = j["odata.nextLink"] || null;
      }
      return itens;
    }

    async itemPorNumero(lista, numero) {
      const j = await this.json(`/_api/web/lists/getbytitle('${lista}')/items?$select=ID&$filter=NumeroOS eq '${numero}'`);
      return j.value[0] || null;
    }

    async gravarEmLotes(lista, valoresDosItens, rotulo) {
      const info = await this.lista(lista);
      for (let i = 0, n = 1; i < valoresDosItens.length; i += TAMANHO_LOTE, n++) {
        const parte = valoresDosItens.slice(i, i + TAMANHO_LOTE);
        const { limite, corpo } = montarLote(this.web, lista, info.ListItemEntityTypeFullName, parte, n);
        const r = await this.pedir("/_api/$batch", { method: "POST", headers: { "Content-Type": `multipart/mixed; boundary=${limite}` }, body: corpo });
        const texto = await r.text();
        if (!r.ok) throw new Error(`${rotulo}: o lote que começa na linha ${i + 1} foi recusado inteiro (${r.status}). ${texto.slice(0, 300)}`);
        const res = lerRespostaLote(texto);
        if (res.falhas.length || res.gravados !== parte.length) {
          throw new Error(`${rotulo}: ${parte.length - res.gravados} item(ns) recusado(s) no lote que começa na linha ${i + 1}` +
            ` (código ${res.falhas.map((f) => f.status).join(", ") || "?"}). ${res.mensagem} — corrija a causa e execute de novo: a etapa grava só o que falta.`);
        }
        this.registrar(`${rotulo}: ${Math.min(i + TAMANHO_LOTE, valoresDosItens.length)} de ${valoresDosItens.length}`);
      }
    }
  }

  // ------------------------------------------------------------ etapas

  async function etapaListas(sp, log) {
    if (!(await sp.lista(LISTA))) { await sp.criarLista(LISTA, "Titulo"); log(`Lista ${LISTA} criada.`); }
    else log(`Lista ${LISTA} já existe; conferindo as colunas.`);
    for (const c of COLUNAS) {
      if (!(await sp.campoExiste(LISTA, c.nome))) { await sp.criarCampo(LISTA, c); log(`  coluna ${c.nome} (${c.tipo}) criada`); }
    }
    // Índices com a lista ainda pequena: depois de crescer, a operação pode ser recusada (Capítulo 5).
    for (const nome of ["Title", ...COLUNAS.filter((c) => c.indice).map((c) => c.nome)]) await sp.alterarCampo(LISTA, nome, { Indexed: true });
    log("  seis índices conferidos: Titulo, NumeroOS, Status, Prioridade, Local, DataAbertura");
    if (!(await sp.lista(LISTA_UNIDADES))) {
      await sp.criarLista(LISTA_UNIDADES, "Nome");
      await sp.criarCampo(LISTA_UNIDADES, { nome: "Supervisor", tipo: "Text" });
      log(`Lista ${LISTA_UNIDADES} criada.`);
    }
  }

  async function exigirColunas(sp) {
    const faltando = [];
    for (const c of COLUNAS) if (!(await sp.campoExiste(LISTA, c.nome))) faltando.push(c.nome);
    if (faltando.length) throw new Error(`A lista ${LISTA} não tem as colunas: ${faltando.join(", ")}. Marque a etapa Listas, ou confira o nome interno de cada coluna.`);
  }

  async function etapaPlanilha(sp, arquivos, log) {
    const info = await sp.lista(LISTA);
    if (info.ItemCount > 0) log(`Planilha: a lista já tem ${info.ItemCount} itens; etapa pulada (nada é gravado em duplicidade).`);
    else await sp.gravarEmLotes(LISTA, arquivos.planilha.map(valores), "Planilha");
    const un = await sp.lista(LISTA_UNIDADES);
    if (un && un.ItemCount === 0) await sp.gravarEmLotes(LISTA_UNIDADES, arquivos.unidades.map((u) => ({ Title: u.Nome, Supervisor: u.Supervisor })), "Unidades");
  }

  async function etapaMassa(sp, arquivos, ignorarPosicao, log) {
    const ultimo = await sp.ultimoItem(LISTA);
    let presentes = new Set();
    if (ultimo && arquivos.massa.some((m) => m.NumeroOS === ultimo.NumeroOS)) {
      presentes = new Set((await sp.todosOsItens(LISTA, "NumeroOS")).map((i) => i.NumeroOS));
    }
    const plano = planejarMassa(arquivos.massa, presentes, ultimo, arquivos.esperado);
    if (plano.retomada) {
      log(`Massa: retomando. Último item gravado: ${ultimo.NumeroOS} (ID ${ultimo.ID}); faltam ${plano.pendentes.length}.`);
      if (plano.buracos) log(`  ${plano.buracos} item(ns) recusado(s) no meio da carga entram agora, com ID fora da ordem do arquivo.`);
    } else {
      log(`Massa: o próximo ID é pelo menos ${plano.proximo}. Estimativa: ` + plano.estimativas.map((e) => `${e.NumeroOS} com ID ${e.id}`).join(", ") + ".");
      log("  (itens apagados também consomem ID; se houve exclusões, os números reais serão maiores)");
      if (!plano.posicaoServe && !ignorarPosicao) {
        throw new Error(`A primeira sentinela ficaria com ID ${plano.estimativas[0].id}, acima de 500, e o Teste de Realidade #1 deixaria de mostrar o que mostra. ` +
          "Apagar itens não resolve, porque o SharePoint não reaproveita ID. Use um site novo, com todas as etapas, ou marque \"ignorar posição\".");
      }
    }
    if (!plano.pendentes.length) { log("Massa: já estava completa."); return; }
    const t0 = performance.now();
    await sp.gravarEmLotes(LISTA, plano.pendentes.map(valores), "Massa");
    const s = Math.round((performance.now() - t0) / 1000);
    log(`Massa gravada em ${Math.floor(s / 60)} min ${s % 60} s. Anote a duração: ela é do seu locatário, não da plataforma.`);
  }

  async function etapaConferir(sp, arquivos, log) {
    const esperado = arquivos.esperado;
    const c = contarStatus(await sp.todosOsItens(LISTA, "Status"));
    const linhas = [["Registros", esperado.total, c.total]];
    for (const st of ["Aberta", "Em andamento", "Fechada"]) linhas.push([st, esperado.por_status[st], c.porStatus[st] || 0]);
    for (const s of esperado.sentinelas) {
      const it = await sp.itemPorNumero(LISTA, s.NumeroOS);
      linhas.push([`${s.NumeroOS} (${s.regra})`, s.ID_esperado, it ? it.ID : "não encontrada"]);
    }
    log("Conferência (item · esperado · na lista):");
    for (const [item, esp, real] of linhas) log(`  ${item.padEnd(24)} ${String(esp).padStart(6)} ${String(real).padStart(14)}  ${esp === real ? "ok" : "DIFERENTE"}`);
    log("Grafias de Status na lista: " + Object.entries(c.grafias).map(([k, v]) => `${k} = ${v}`).join("; "));
    log("As contagens normalizam as grafias da planilha, como o Capítulo 8 faz. O que o Teste de Realidade #1 exige são as duas regras de ID.");
  }

  // ------------------------------------------------------------ painel

  function painel() {
    document.getElementById("campo-carga")?.remove();
    const d = document.createElement("div");
    d.id = "campo-carga";
    d.style.cssText = "position:fixed;top:16px;right:16px;width:min(560px,calc(100vw - 32px));max-height:calc(100vh - 32px);overflow:auto;z-index:2147483647;" +
      "background:#fff;color:#111;border:1px solid #888;border-left:4px solid #0b6;box-shadow:0 4px 24px rgba(0,0,0,.25);font:13px/1.45 system-ui,sans-serif;padding:14px";
    d.innerHTML = `
      <strong>Carga do CAMPO</strong> · Power Fx na Prática
      <p style="margin:8px 0">Site: <input id="cc-site" style="width:100%" value="${urlDoSite()}"></p>
      <p style="margin:8px 0">Arquivos da pasta <code>dados/</code> (planilha_ocorrencias_351.csv, unidades_40.csv, ocorrencias_12000.csv, esperado.json):<br>
        <input id="cc-arquivos" type="file" multiple accept=".csv,.json"></p>
      <p style="margin:8px 0">
        <label><input type="checkbox" id="cc-listas"> Listas</label>&nbsp;
        <label><input type="checkbox" id="cc-planilha"> Planilha</label>&nbsp;
        <label><input type="checkbox" id="cc-massa" checked> Massa</label>&nbsp;
        <label><input type="checkbox" id="cc-conferir" checked> Conferir</label>&nbsp;
        <label title="Carregar mesmo que a primeira sentinela passe do ID 500"><input type="checkbox" id="cc-ignorar"> ignorar posição</label></p>
      <button id="cc-executar">Executar</button> <button id="cc-fechar">Fechar</button>
      <pre id="cc-log" style="white-space:pre-wrap;background:#f4f4f4;padding:8px;margin-top:10px;min-height:60px;font:12px/1.4 ui-monospace,monospace"></pre>`;
    document.body.appendChild(d);
    const logEl = d.querySelector("#cc-log");
    const log = (t) => { logEl.textContent += `${new Date().toLocaleTimeString()}  ${t}\n`; logEl.scrollTop = logEl.scrollHeight; console.log(t); };
    d.querySelector("#cc-fechar").onclick = () => d.remove();
    d.querySelector("#cc-executar").onclick = async () => {
      const botao = d.querySelector("#cc-executar");
      botao.disabled = true;
      try {
        const etapas = ["listas", "planilha", "massa", "conferir"].filter((e) => d.querySelector(`#cc-${e}`).checked);
        const arquivos = await lerArquivos(d.querySelector("#cc-arquivos").files, etapas);
        const sp = new Site(d.querySelector("#cc-site").value.replace(/\/$/, ""), log);
        const t0 = performance.now();
        log(`Etapas: ${etapas.join(", ")}`);
        if (etapas.includes("listas")) await etapaListas(sp, log);
        if (etapas.includes("planilha") || etapas.includes("massa")) await exigirColunas(sp);
        if (etapas.includes("planilha")) await etapaPlanilha(sp, arquivos, log);
        if (etapas.includes("massa")) await etapaMassa(sp, arquivos, d.querySelector("#cc-ignorar").checked, log);
        if (etapas.includes("conferir")) await etapaConferir(sp, arquivos, log);
        log(`Fim, em ${Math.round((performance.now() - t0) / 1000)} s.`);
      } catch (e) {
        log(`PAROU: ${e.message}`);
      } finally {
        botao.disabled = false;
      }
    };
  }

  async function lerArquivos(lista, etapas) {
    const porNome = {};
    for (const f of lista) porNome[f.name] = f;
    const precisa = { esperado: "esperado.json" };
    if (etapas.includes("planilha")) Object.assign(precisa, { planilha: "planilha_ocorrencias_351.csv", unidades: "unidades_40.csv" });
    if (etapas.includes("massa")) precisa.massa = "ocorrencias_12000.csv";
    const faltam = Object.values(precisa).filter((n) => !porNome[n]);
    if (faltam.length) throw new Error(`Escolha também: ${faltam.join(", ")}`);
    const r = {};
    for (const [chave, nome] of Object.entries(precisa)) {
      const texto = await porNome[nome].text();
      r[chave] = nome.endsWith(".json") ? JSON.parse(texto) : lerCsv(texto);
    }
    return r;
  }

  // No Node, para os testes de testes/testar-navegador.js; no navegador, o painel.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = Object.assign({ Site, etapaListas, exigirColunas, etapaPlanilha, etapaMassa, etapaConferir, TAMANHO_LOTE }, puras);
  } else {
    raiz.CargaCAMPO = puras;
    painel();
  }
})(typeof window !== "undefined" ? window : globalThis);
