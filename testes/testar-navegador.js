/*
 * Testa carga/carregar-campo-navegador.js contra uma API REST do SharePoint simulada.
 * Não conecta a nada: fetch é substituído por um servidor em memória que responde às
 * mesmas rotas que o script usa ($batch inclusive, com o corpo multipart de verdade).
 *
 * Uso: node testes/testar-navegador.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const RAIZ = path.join(__dirname, "..");
const carga = require(path.join(RAIZ, "carga", "carregar-campo-navegador.js"));
const dados = (n) => fs.readFileSync(path.join(RAIZ, "dados", n), "utf8");

const arquivos = {
  planilha: carga.lerCsv(dados("planilha_ocorrencias_351.csv")),
  unidades: carga.lerCsv(dados("unidades_40.csv")),
  massa: carga.lerCsv(dados("ocorrencias_12000.csv")),
  esperado: JSON.parse(dados("esperado.json")),
};

let passou = 0;
function confere(cond, descricao) {
  assert.ok(cond, "FALHOU: " + descricao);
  passou++;
  console.log("ok  " + descricao);
}

// ------------------------------------------------------------ funções puras

confere(arquivos.planilha.length === 351 && arquivos.massa.length === 12000 && arquivos.unidades.length === 40, "CSV lidos: 351, 12.000 e 40 linhas");
confere(arquivos.massa[120].NumeroOS === "OS-000472" && arquivos.massa[11800].NumeroOS === "OS-012152", "sentinelas nas posições 120 e 11800 da massa");
confere(carga.lerCsv('a;b\r\n"x;1";"di""z"\r\n')[0].a === "x;1" && carga.lerCsv('a;b\n"x;1";"di""z"\n')[0].b === 'di"z', "CSV com aspas, ponto e vírgula dentro do campo e CRLF");
confere(carga.paraUtc("2023-03-06T16:40:00") === "2023-03-06T19:40:00Z" && carga.paraUtc("") === null, "data de Brasília vira UTC; data em branco continua em branco");
const v = carga.valores(arquivos.massa[0]);
confere(!("Responsavel" in v) && v.Title === arquivos.massa[0].Titulo, "responsável em branco não vai no corpo; Titulo vai para Title");
const resp = "--b\r\nContent-Type: application/http\r\n\r\nHTTP/1.1 201 Created\r\n\r\n{}\r\n--b\r\nHTTP/1.1 400 Bad Request\r\n\r\n" +
  '{"odata.error":{"code":"-1","message":{"lang":"pt-BR","value":"Coluna inexistente"}}}\r\n--b--';
const lida = carga.lerRespostaLote(resp);
confere(lida.gravados === 1 && lida.falhas.length === 1 && lida.mensagem === "Coluna inexistente", "resposta do $batch: 201 e 400 separados, mensagem extraída");

// ------------------------------------------------------------ SharePoint simulado

function servidor({ proximoInicial = 1, recusarNumero = null } = {}) {
  const sp = { listas: {}, recusarNumero, lotes: 0 };
  const nova = (nome) => ({ nome, itens: [], campos: new Set(["Title"]), proximo: proximoInicial, indices: new Set(), tipo: `SP.Data.${nome}ListItem` });
  const resposta = (status, corpo, tipo = "application/json") => ({
    ok: status >= 200 && status < 300, status, headers: { get: () => null },
    json: async () => (typeof corpo === "string" ? JSON.parse(corpo) : corpo),
    text: async () => (typeof corpo === "string" ? corpo : JSON.stringify(corpo)),
  });
  const gravar = (lista, corpo) => {
    const l = sp.listas[lista];
    if (sp.recusarNumero && corpo.NumeroOS === sp.recusarNumero) { sp.recusarNumero = null; return 429; }
    for (const k of Object.keys(corpo)) if (k !== "__metadata" && !l.campos.has(k)) return 400;
    assert.strictEqual(corpo.__metadata.type, l.tipo, "tipo da entidade no corpo");
    l.itens.push(Object.assign({ ID: l.proximo++ }, corpo));
    return 201;
  };
  sp.fetch = async (url, op = {}) => {
    const u = new URL(url);
    const p = decodeURIComponent(u.pathname).replace(/^\/sites\/campo/, "");
    const q = Object.fromEntries(u.searchParams);
    const metodo = op.method || "GET";
    if (metodo !== "GET" && p !== "/_api/contextinfo") assert.ok(op.headers["X-RequestDigest"], "chave de formulário em toda escrita");
    let m;
    if (p === "/_api/contextinfo") return resposta(200, { FormDigestValue: "chave", FormDigestTimeoutSeconds: 1800 });
    if (p === "/_api/web/lists" && metodo === "POST") { const b = JSON.parse(op.body); sp.listas[b.Title] = nova(b.Title); return resposta(201, {}); }
    if ((m = p.match(/^\/_api\/web\/lists\/getbytitle\('([^']+)'\)$/))) {
      const l = sp.listas[m[1]];
      return l ? resposta(200, { Id: "x", ItemCount: l.itens.length, ListItemEntityTypeFullName: l.tipo }) : resposta(404, {});
    }
    if ((m = p.match(/^\/_api\/web\/lists\/getbytitle\('([^']+)'\)\/fields\/createfieldasxml$/))) {
      const xml = JSON.parse(op.body).parameters.SchemaXml;
      sp.listas[m[1]].campos.add(xml.match(/Name='([^']+)'/)[1]);
      return resposta(201, {});
    }
    if ((m = p.match(/^\/_api\/web\/lists\/getbytitle\('([^']+)'\)\/fields\/getbyinternalnameortitle\('([^']+)'\)$/))) {
      const l = sp.listas[m[1]];
      if (metodo === "GET") return l.campos.has(m[2]) ? resposta(200, { InternalName: m[2] }) : resposta(404, {});
      if (JSON.parse(op.body).Indexed) l.indices.add(m[2]);
      return resposta(204, "");
    }
    if ((m = p.match(/^\/_api\/web\/lists\/getbytitle\('([^']+)'\)\/items$/))) {
      const l = sp.listas[m[1]];
      if (q.$filter) { const n = q.$filter.match(/'([^']+)'/)[1]; return resposta(200, { value: l.itens.filter((i) => i.NumeroOS === n) }); }
      if (q.$orderby === "ID desc") return resposta(200, { value: l.itens.slice().sort((a, b) => b.ID - a.ID).slice(0, 1) });
      const inicio = Number(q.$skiptoken || 0), top = Number(q.$top);
      const pagina = l.itens.slice(inicio, inicio + top);
      const prox = inicio + top < l.itens.length ? `${u.origin}${u.pathname}?$top=${top}&$skiptoken=${inicio + top}` : undefined;
      return resposta(200, Object.assign({ value: pagina }, prox ? { "odata.nextLink": prox } : {}));
    }
    if (p === "/_api/$batch") {
      sp.lotes++;
      const partes = op.body.split(/\r\n--changeset_campo_\d+\r\n/).slice(1);
      const status = partes.map((parte) => {
        const lista = parte.match(/getbytitle\('([^']+)'\)\/items HTTP/)[1];
        const corpo = JSON.parse(parte.split("\r\n").find((l) => l.startsWith("{")));
        return gravar(lista, corpo);
      });
      assert.ok(status.length <= carga.TAMANHO_LOTE, "no máximo 100 operações por lote");
      return resposta(200, status.map((s) => `--batchresponse\r\nContent-Type: application/http\r\n\r\nHTTP/1.1 ${s} X\r\n\r\n{}`).join("\r\n") + "\r\n--batchresponse--", "multipart/mixed");
    }
    throw new Error(`rota não simulada: ${metodo} ${p}`);
  };
  return sp;
}

async function executar(sp, etapas, { ignorar = false } = {}) {
  global.fetch = sp.fetch;
  const log = [];
  const site = new carga.Site("https://exemplo.sharepoint.com/sites/campo", (t) => log.push(t));
  const registrar = (t) => log.push(t);
  if (etapas.includes("listas")) await carga.etapaListas(site, registrar);
  if (etapas.includes("planilha") || etapas.includes("massa")) await carga.exigirColunas(site);
  if (etapas.includes("planilha")) await carga.etapaPlanilha(site, arquivos, registrar);
  if (etapas.includes("massa")) await carga.etapaMassa(site, arquivos, ignorar, registrar);
  if (etapas.includes("conferir")) await carga.etapaConferir(site, arquivos, registrar);
  return log;
}

const idDe = (sp, n) => sp.listas.Ocorrencias.itens.find((i) => i.NumeroOS === n)?.ID;

(async () => {
  global.performance = global.performance || { now: () => Date.now() };

  // 1. ambiente novo
  let sp = servidor();
  let log = await executar(sp, ["listas", "planilha", "massa", "conferir"]);
  confere(sp.listas.Ocorrencias.itens.length === 12351 && sp.listas.Unidades.itens.length === 40, "ambiente novo: 12.351 ocorrências e 40 unidades");
  confere(sp.listas.Ocorrencias.indices.size === 6, "ambiente novo: seis índices");
  confere(idDe(sp, "OS-000472") === 472 && idDe(sp, "OS-012152") === 12152, "sentinelas com ID 472 e 12152");
  confere(sp.lotes === 4 + 1 + 120, "lotes de 100: 4 da planilha, 1 das unidades, 120 da massa");
  confere(log.filter((l) => /DIFERENTE/.test(l)).length === 0, "conferência sem nenhuma linha DIFERENTE");
  confere(log.some((l) => /aberta = 7; .*Aberto = 9/.test(l)), "conferência mostra as grafias da planilha");

  // 2 e 3. item recusado no meio da massa, e retomada
  sp = servidor({ recusarNumero: "OS-005401" });
  let erro = null;
  try { await executar(sp, ["listas", "planilha", "massa"]); } catch (e) { erro = e; }
  confere(erro && /grava só o que falta/.test(erro.message), "item recusado: a carga para e diz como retomar");
  confere(sp.listas.Ocorrencias.itens.length === 351 + 5099, "item recusado: o resto do lote entrou (lote não transacional)");
  log = await executar(sp, ["massa", "conferir"]);
  const numeros = sp.listas.Ocorrencias.itens.map((i) => i.NumeroOS);
  confere(numeros.length === 12351 && new Set(numeros).size === 12351, "retomada: 12.351 itens, nenhum repetido");
  confere(idDe(sp, "OS-005401") === 5451 && idDe(sp, "OS-012152") === 12152, "retomada: recusado entra primeiro; segunda sentinela mantém o ID");

  // 4. lista que já consumiu ID demais
  sp = servidor({ proximoInicial: 600 });
  erro = null;
  try { await executar(sp, ["listas", "planilha", "massa"]); } catch (e) { erro = e; }
  confere(erro && /acima de 500/.test(erro.message) && sp.listas.Ocorrencias.itens.length === 351, "ID consumidos: a massa se recusa a começar, e nada é gravado");

  console.log(`\nTodos os ${passou} testes passaram.`);
})().catch((e) => { console.error(e); process.exit(1); });
