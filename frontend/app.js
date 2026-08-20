/* ==========================================================================
   SIGES - SISTEMA DE GESTÃO DE ETAPAS DE SERVIÇOS (COSAMPA)
   Aplicação Front-end SPA Unificada (Lean & Clean Architecture)
   ========================================================================== */

// --- 1. CONSTANTES E CONFIGURAÇÕES DO DOMÍNIO ---
const STATUS_DEFS = {
  1: { n: 'Aguardando Conferência', a: 'Fechamento', m: 'med', sla: 3 },
  2: { n: 'Pendências Operacionais', a: 'Operação', m: 'pen', sla: 5 },
  3: { n: 'Aguard. Envio p/ Validação', a: 'Fechamento', m: 'med', sla: 2 },
  4: { n: 'Aguard. Validação do Cliente', a: 'Faturamento', m: 'fat', sla: 7 },
  5: { n: 'Rejeitado na Validação (Fech.)', a: 'Fechamento', m: 'med', sla: 3 },
  6: { n: 'Rejeitado na Validação (Oper.)', a: 'Operação', m: 'pen', sla: 5 },
  7: { n: 'Validado — Aguard. Autorização', a: 'Faturamento', m: 'fat', sla: 3 },
  8: { n: 'Faturado — Aguard. Conciliação', a: 'Faturamento', m: 'con', sla: 10 },
  9: { n: 'Análise de Conciliação', a: 'Faturamento', m: 'con', sla: 5 },
  10: { n: 'Conciliado c/ Divergências', a: 'Fechamento', m: 'med', sla: 4 },
  11: { n: 'Pgto a Menor — Cobrar Cliente', a: 'Fechamento', m: 'med', sla: 7 },
  12: { n: 'Pgto a Menor — Em Disputa', a: 'Fechamento', m: 'med', sla: 15 },
  13: { n: 'Faturado Total', a: 'Geral', m: 'fin', sla: null },
  14: { n: 'Faturado a Maior', a: 'Geral', m: 'fin', sla: null },
  15: { n: 'Faturado a Menor', a: 'Geral', m: 'fin', sla: null }
};

const MACRO_DEFS = {
  med: { lb: 'Medição', bg: 'oklch(0.93 0.035 250)', fg: 'oklch(0.38 0.09 250)' },
  pen: { lb: 'Pendências', bg: 'oklch(0.95 0.05 80)', fg: 'oklch(0.45 0.1 70)' },
  fat: { lb: 'Faturamento', bg: 'oklch(0.94 0.035 300)', fg: 'oklch(0.42 0.09 300)' },
  con: { lb: 'Conciliação', bg: 'oklch(0.94 0.04 210)', fg: 'oklch(0.4 0.08 210)' },
  fin: { lb: 'Finalizado', bg: 'oklch(0.94 0.05 160)', fg: 'oklch(0.38 0.09 160)' }
};

const CONTRATOS = {
  A: 'CT-2024/018 · Dist. Leste',
  B: 'CT-2025/007 · Dist. Sul',
  C: 'CT-2023/031 · Ilum. Pública ZL'
};

const NEXT_MAP = { 1: 3, 3: 4, 5: 3, 10: 3 };

const TELAS_DEF = [
  { id: 'gerencial', label: 'Gerencial', icon: '★' },
  { id: 'medicao', label: '01. Medição', icon: '01' },
  { id: 'pendencias', label: '02. Pendências', icon: '02' },
  { id: 'faturamento', label: '03. Faturamento', icon: '03' },
  { id: 'conciliacoes', label: '04. Conciliações', icon: '04' },
  { id: 'finalizados', label: '05. Finalizados', icon: '05' },
  { id: 'relatorios', label: 'Consultas + Relatórios', icon: 'C·R' },
  { id: 'gestao_acessos', label: 'Gestão de Acessos', icon: '⚙', masterOnly: true }
];

const PERFIS_INICIAIS = {
  'Master': { nome: 'Master', descricao: 'Administrador total do sistema e gestão de acessos', is_master: true, telas: ['gerencial', 'medicao', 'pendencias', 'faturamento', 'conciliacoes', 'finalizados', 'relatorios', 'gestao_acessos'] },
  'Fechamento': { nome: 'Fechamento', descricao: 'Gestão de medições e fechamento', is_master: false, telas: ['gerencial', 'medicao', 'pendencias', 'finalizados', 'relatorios'] },
  'Operação': { nome: 'Operação', descricao: 'Tratativa de pendências operacionais', is_master: false, telas: ['gerencial', 'pendencias', 'finalizados', 'relatorios'] },
  'Faturamento': { nome: 'Faturamento', descricao: 'Acesso às etapas comerciais', is_master: false, telas: ['gerencial', 'medicao', 'pendencias', 'faturamento', 'conciliacoes', 'finalizados', 'relatorios'] }
};

const USUARIOS_INICIAIS = [
  { id: 1, nome: 'Administrador Master', email: 'admin@cosampa.com.br', perfil: 'Master' },
  { id: 2, nome: 'Carlos Fechamento', email: 'carlos@cosampa.com.br', perfil: 'Fechamento' },
  { id: 3, nome: 'Fernanda Operação', email: 'fernanda@cosampa.com.br', perfil: 'Operação' },
  { id: 4, nome: 'Roberto Faturamento', email: 'roberto@cosampa.com.br', perfil: 'Faturamento' }
];

const MOCK_SERVICOS = [
  { id: 'SOB-2026-0341', ct: 'A', ob: 'Vila Prudente', tp: 'Rede', st: 1, v: 12400, d: 11, nota: 'NM-0873' },
  { id: 'SOB-2026-0347', ct: 'A', ob: 'Vila Prudente', tp: 'Medidor', st: 1, v: 980, d: 8, nota: 'NM-0879' },
  { id: 'SOB-2026-0352', ct: 'B', ob: 'Jd. Ângela', tp: 'Transformador', st: 1, v: 38200, d: 12, nota: 'NM-0881' },
  { id: 'SOB-2026-0298', ct: 'A', ob: 'Penha', tp: 'Rede', st: 2, v: 21500, d: 4, pend: [{ t: 'Fotos', tr: false }, { t: 'Materiais', tr: false }] },
  { id: 'SOB-2026-0301', ct: 'B', ob: 'Capela do Socorro', tp: 'Ramal', st: 2, v: 3400, d: 7, pend: [{ t: 'Documentos', tr: false }, { t: 'Retorno', tr: false }] },
  { id: 'SOB-2026-0315', ct: 'C', ob: 'Itaquera', tp: 'Poste', st: 2, v: 7250, d: 10, pend: [{ t: 'Fotos', tr: false }] },
  { id: 'SOB-2026-0289', ct: 'A', ob: 'Penha', tp: 'Rede', st: 3, v: 45900, d: 12, nota: 'NM-0851' },
  { id: 'SOB-2026-0276', ct: 'A', ob: 'Mooca', tp: 'Rede', st: 4, v: 78500, d: 6, nota: 'NM-0812' },
  { id: 'SOB-2026-0269', ct: 'B', ob: 'Parelheiros', tp: 'Rede', st: 5, v: 18700, d: 11, nota: 'NM-0842', ret: 'Baremo divergente na atividade 3.1' },
  { id: 'SOB-2026-0248', ct: 'A', ob: 'Belém', tp: 'Rede', st: 7, v: 52000, d: 11, nota: 'NM-0790' },
  { id: 'SOB-2026-0237', ct: 'B', ob: 'Santo Amaro', tp: 'Rede', st: 8, v: 66800, d: 3, nota: 'NF-4521' },
  { id: 'SOB-2026-0216', ct: 'A', ob: 'Sapopemba', tp: 'Rede', st: 10, v: 33500, d: 6, nota: 'NF-4460', ret: 'Divergência de R$ 1.240 no baremo' },
  { id: 'SOB-2026-0187', ct: 'A', ob: 'Sé', tp: 'Rede', st: 13, v: 15300, d: 8, nota: 'NF-4432' }
];

// --- 2. GERENCIADOR DE AUTENTICAÇÃO E SESSÃO ---
class AuthService {
  constructor() {
    this.perfis = JSON.parse(localStorage.getItem('siges_perfis')) || { ...PERFIS_INICIAIS };
    this.usuarios = JSON.parse(localStorage.getItem('siges_usuarios')) || [ ...USUARIOS_INICIAIS ];
    this.usuarioLogado = JSON.parse(localStorage.getItem('siges_usuario_logado')) || this.usuarios[0]; // Padrão Master
  }

  getPerfilAtivo() {
    return this.perfis[this.usuarioLogado.perfil] || this.perfis['Master'];
  }

  setPerfilAtivo(nomePerfil) {
    if (this.perfis[nomePerfil]) {
      this.usuarioLogado.perfil = nomePerfil;
      this.salvar();
    }
  }

  temAcessoTela(telaId) {
    const p = this.getPerfilAtivo();
    if (!p) return false;
    if (p.is_master) return true;
    return p.telas.includes(telaId);
  }

  atualizarPermissoes(nomePerfil, novasTelas) {
    if (this.perfis[nomePerfil]) {
      this.perfis[nomePerfil].telas = novasTelas;
      this.salvar();
    }
  }

  adicionarUsuario(nome, email, perfil) {
    const u = { id: Date.now(), nome, email, perfil };
    this.usuarios.push(u);
    this.salvar();
    return u;
  }

  salvar() {
    localStorage.setItem('siges_usuario_logado', JSON.stringify(this.usuarioLogado));
    localStorage.setItem('siges_perfis', JSON.stringify(this.perfis));
    localStorage.setItem('siges_usuarios', JSON.stringify(this.usuarios));
  }
}

const authService = new AuthService();

// --- 3. ESTADO REATIVO GLOBAL DA APLICAÇÃO ---
class Store {
  constructor() {
    const svcs = JSON.parse(localStorage.getItem('siges_svcs')) || MOCK_SERVICOS.map(s => ({
      ...s,
      hist: s.hist || [{ st: s.st, d: s.d }],
      bar: s.bar || [
        { cod: '3.1', desc: 'Lançamento de cabo BT', qtd: 1, med: Math.round(s.v * 0.55), pago: s.st === 13 ? Math.round(s.v * 0.55) : null },
        { cod: '3.4', desc: 'Instalação de cruzeta', qtd: 1, med: Math.round(s.v * 0.30), pago: s.st === 13 ? Math.round(s.v * 0.30) : null },
        { cod: '5.2', desc: 'Aterramento de estrutura', qtd: 1, med: Math.round(s.v * 0.15), pago: s.st === 13 ? Math.round(s.v * 0.15) : null }
      ]
    }));

    this.state = {
      telaAtiva: 'gerencial',
      pinSidebar: true,
      filtros: { periodo: 'mes', contrato: 'todos', tipo: 'todos', area: 'todas', status: 'todos', busca: '' },
      presets: [{ nome: 'Dist. Leste · 7 dias', f: { periodo: '7d', contrato: 'A', tipo: 'todos', area: 'todas', status: 'todos', busca: '' } }],
      salvandoPreset: false,
      pNome: '',
      selecionados: [],
      alvoStatus: '',
      grupoPendencias: { Documentos: false, Fotos: false, Materiais: false, Retorno: false, Outros: false },
      servicoFocoId: null,
      drawerServicoId: null,
      premissasAberta: false,
      toast: null,
      minutosAtualizacao: 0,
      servicos: svcs
    };

    this.listeners = [];
  }

  getState() { return this.state; }

  subscribe(fn) {
    this.listeners.push(fn);
    return () => this.listeners = this.listeners.filter(l => l !== fn);
  }

  setState(partial) {
    this.state = { ...this.state, ...partial };
    localStorage.setItem('siges_svcs', JSON.stringify(this.state.servicos));
    this.listeners.forEach(l => l(this.state));
  }

  notifyToast(msg) {
    this.setState({ toast: msg });
    setTimeout(() => {
      if (this.state.toast === msg) this.setState({ toast: null });
    }, 4200);
  }

  setTelaAtiva(telaId) {
    if (!authService.temAcessoTela(telaId)) {
      this.notifyToast(`Acesso restrito para o perfil ${authService.usuarioLogado.perfil}.`);
      return;
    }
    this.setState({ telaAtiva: telaId, selecionados: [], drawerServicoId: null, servicoFocoId: null });
  }

  setPerfilAtivo(nomePerfil) {
    authService.setPerfilAtivo(nomePerfil);
    const ok = authService.temAcessoTela(this.state.telaAtiva);
    this.setState({ telaAtiva: ok ? this.state.telaAtiva : 'gerencial', selecionados: [] });
    if (!ok) this.notifyToast(`Perfil ${nomePerfil} ativado — redirecionado para Gerencial.`);
  }

  getServicosFiltrados() {
    const f = this.state.filtros;
    return this.state.servicos.filter(s => {
      if (f.contrato !== 'todos' && s.ct !== f.contrato) return false;
      if (f.tipo !== 'todos' && s.tp !== f.tipo) return false;
      if (f.area !== 'todas' && STATUS_DEFS[s.st]?.a !== f.area) return false;
      if (f.status !== 'todos' && s.st !== Number(f.status)) return false;
      if (f.periodo === '7d' && s.d < 7) return false;
      if (f.periodo === '3d' && s.d < 11) return false;
      if (f.busca) {
        const q = f.busca.toLowerCase();
        if (!`${s.id} ${s.ob} ${s.tp}`.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }

  tramitarSelecionados() {
    const sel = this.state.selecionados;
    if (!sel.length) return this.notifyToast('Selecione ao menos um serviço na tabela.');
    let count = 0;
    const novos = this.state.servicos.map(s => {
      if (sel.includes(s.id) && NEXT_MAP[s.st]) {
        count++;
        const next = NEXT_MAP[s.st];
        return { ...s, st: next, d: 13, hist: [ ...(s.hist || []), { st: next, d: 13 } ] };
      }
      return s;
    });
    this.setState({ servicos: novos, selecionados: [] });
    this.notifyToast(`${count} serviço(s) tramitado(s) com sucesso.`);
  }

  aplicarStatusEmMassa(stIdStr) {
    const sel = this.state.selecionados;
    if (!sel.length) return this.notifyToast('Selecione ao menos um serviço.');
    const stId = Number(stIdStr);
    if (!stId) return this.notifyToast('Escolha o novo status.');
    const novos = this.state.servicos.map(s => {
      if (sel.includes(s.id)) {
        let pends = s.pend || [];
        if (stId === 2 && !pends.some(p => !p.tr)) pends = [{ t: 'Outros', tr: false, det: '' }];
        return { ...s, st: stId, d: 13, pend: pends, hist: [ ...(s.hist || []), { st: stId, d: 13 } ] };
      }
      return s;
    });
    this.setState({ servicos: novos, selecionados: [], alvoStatus: '' });
    this.notifyToast(`${sel.length} serviço(s) movido(s) para status ${padNum(stId)}.`);
  }

  enviarParaPendencias(tipos) {
    const sel = this.state.selecionados;
    if (!sel.length) return this.notifyToast('Selecione ao menos um serviço.');
    if (!tipos.length) return this.notifyToast('Marque ao menos um tipo de pendência.');
    const novos = this.state.servicos.map(s => {
      if (sel.includes(s.id)) {
        return { ...s, st: 2, d: 13, pend: tipos.map(t => ({ t, tr: false, det: '' })), hist: [ ...(s.hist || []), { st: 2, d: 13 } ] };
      }
      return s;
    });
    this.setState({ servicos: novos, selecionados: [] });
    this.notifyToast(`${sel.length} serviço(s) enviado(s) para 02. Pendências.`);
  }

  tratarPendenciaItem(servicoId, indexItem) {
    let ret = false;
    const novos = this.state.servicos.map(s => {
      if (s.id === servicoId && s.pend) {
        const pList = s.pend.map((p, idx) => idx === indexItem ? { ...p, tr: !p.tr } : p);
        let novoSt = s.st;
        if (pList.every(p => p.tr) && (s.st === 2 || s.st === 6)) {
          novoSt = 1; // RN-04: Retorno automático para 01
          ret = true;
        }
        return { ...s, pend: pList, st: novoSt };
      }
      return s;
    });
    this.setState({ servicos: novos });
    if (ret) this.notifyToast(`${servicoId} — Pendências resolvidas! Retornou para 01. Aguardando Conferência (RN-04).`);
  }
}

const store = new Store();

// --- 4. FUNÇÕES AUXILIARES DE FORMATAÇÃO ---
function formatMoney(v) { return v == null ? 'R$ 0' : 'R$ ' + v.toLocaleString('pt-BR'); }
function padNum(n) { return String(n).padStart(2, '0'); }

// --- 5. COMPONENTES E RENDERIZADORES DA INTERFACE ---
function renderApp(state) {
  const root = document.getElementById('app-root');
  if (!root) return;

  const perfilAtivo = authService.getPerfilAtivo();
  const servicosFiltrados = store.getServicosFiltrados();

  root.innerHTML = `
    <!-- Sidebar Retrátil -->
    <aside class="sidebar" style="width:${state.pinSidebar ? 236 : 62}px">
      <div style="display:flex;align-items:center;gap:10px;padding:13px 14px;border-bottom:1px solid rgba(255,255,255,0.07)">
        <div style="width:32px;height:32px;border-radius:8px;background:var(--ac-primary);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700">C</div>
        ${state.pinSidebar ? `
          <div style="flex:1">
            <div style="font-size:13px;font-weight:700;color:#eef3f1">Cosampa</div>
            <div style="font-size:10.5px;color:#7d8c86">Esteira de Faturamento</div>
          </div>
          <button id="btn-pin" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);color:#c6d2cc;border-radius:7px;width:26px;height:26px;cursor:pointer">${state.pinSidebar ? '«' : '»'}</button>
        ` : ''}
      </div>
      <div style="padding:10px 0;flex:1;overflow-y:auto">
        ${TELAS_DEF.map(t => {
          const ok = authService.temAcessoTela(t.id);
          const at = state.telaAtiva === t.id;
          return `
            <div class="menu-item" data-tela="${t.id}" style="display:flex;align-items:center;gap:11px;margin:2px 9px;padding:8px 9px;border-radius:8px;font-size:13px;background:${at ? 'var(--ac-primary)' : 'transparent'};color:${at ? '#fff' : ok ? '#c6d2cc' : '#5c6a64'};opacity:${ok ? 1 : 0.55};cursor:${ok ? 'pointer' : 'not-allowed'}">
              <span style="font-family:var(--font-mono);font-size:11px;font-weight:600;min-width:26px;text-align:center">${t.icon}</span>
              ${state.pinSidebar ? `<span>${t.label}</span>` : ''}
            </div>
          `;
        }).join('')}
      </div>
      ${state.pinSidebar ? `<div style="padding:12px 16px;border-top:1px solid rgba(255,255,255,0.07);font-size:10.5px;color:#67766f">Perfil: <b>${perfilAtivo.nome}</b></div>` : ''}
    </aside>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Header -->
      <header class="top-header">
        <div style="font-size:16.5px;font-weight:700">${(TELAS_DEF.find(t=>t.id===state.telaAtiva)||{}).label}</div>
        <span style="font-size:10px;font-weight:600;color:#5b6b65;border:1px solid #d7dedb;border-radius:6px;padding:3px 7px">Satélite GPM</span>
        <div style="flex:1"></div>
        <div style="display:flex;align-items:center;gap:7px;font-size:11.5px;color:#5b6b65;background:#f2f5f4;border:1px solid #e2e8e5;border-radius:8px;padding:5px 10px">
          <span>GPM · atualizado agora</span>
          <button id="btn-sync" style="border:none;background:transparent;color:var(--ac-primary);cursor:pointer">⟳</button>
        </div>
        <div style="display:flex;align-items:center;gap:7px">
          <span style="font-size:11px;color:#71807a">Perfil</span>
          <select id="select-perfil" class="select-input" style="font-weight:600">
            ${Object.keys(authService.perfis).map(p => `<option value="${p}" ${p === perfilAtivo.nome ? 'selected' : ''}>${p}</option>`).join('')}
          </select>
        </div>
      </header>

      <!-- Filter Bar -->
      ${state.telaAtiva !== 'gestao_acessos' ? `
        <div class="filter-bar">
          <select id="f-contrato" class="select-input">
            <option value="todos" ${state.filtros.contrato==='todos'?'selected':''}>Todos os contratos</option>
            <option value="A" ${state.filtros.contrato==='A'?'selected':''}>CT-2024/018 · Dist. Leste</option>
            <option value="B" ${state.filtros.contrato==='B'?'selected':''}>CT-2025/007 · Dist. Sul</option>
            <option value="C" ${state.filtros.contrato==='C'?'selected':''}>CT-2023/031 · Ilum. Pública ZL</option>
          </select>
          <select id="f-tipo" class="select-input">
            <option value="todos" ${state.filtros.tipo==='todos'?'selected':''}>Todos os tipos</option>
            <option value="Rede">Rede</option><option value="Transformador">Transformador</option><option value="Medidor">Medidor</option>
          </select>
          <input id="f-busca" class="text-input" value="${state.filtros.busca}" placeholder="Buscar SOB, obra..." style="width:180px">
        </div>
      ` : ''}

      <!-- Main View Content -->
      <main class="view-container">
        ${renderMainViewContent(state, servicosFiltrados)}
      </main>
    </div>

    <!-- Modais e Drawers -->
    ${renderDrawer(state)}
    ${state.toast ? `<div class="toast-container">${state.toast}</div>` : ''}
  `;

  // Attach Event Listeners
  root.querySelector('#btn-pin')?.addEventListener('click', () => store.setState({ pinSidebar: !state.pinSidebar }));
  root.querySelector('#select-perfil')?.addEventListener('change', (e) => store.setPerfilAtivo(e.target.value));
  root.querySelector('#f-contrato')?.addEventListener('change', (e) => store.setState({ filtros: { ...state.filtros, contrato: e.target.value } }));
  root.querySelector('#f-busca')?.addEventListener('input', (e) => store.setState({ filtros: { ...state.filtros, busca: e.target.value } }));

  root.querySelectorAll('.menu-item').forEach(el => {
    el.addEventListener('click', () => store.setTelaAtiva(el.getAttribute('data-tela')));
  });

  attachViewListeners(root, state, servicosFiltrados);
}

function renderMainViewContent(state, servicosFiltrados) {
  if (state.telaAtiva === 'gestao_acessos') {
    return renderGestaoAcessosView();
  }

  if (state.telaAtiva === 'pendencias') {
    const pendSvcs = servicosFiltrados.filter(s => [2, 6].includes(s.st));
    return renderPendenciasPanel(pendSvcs, state);
  }

  // Tabela Principal (Gerencial e demais)
  return `
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:14px">
      <div class="kpi-card"><div style="font-size:11px;color:#71807a">SERVIÇOS NA ESTEIRA</div><div class="kpi-val">${servicosFiltrados.length}</div></div>
      <div class="kpi-card"><div style="font-size:11px;color:#71807a">VALOR TOTAL</div><div class="kpi-val">${formatMoney(servicosFiltrados.reduce((a,s)=>a+s.v,0))}</div></div>
      <div class="kpi-card"><div style="font-size:11px;color:#71807a">SLA ESTOURADO</div><div class="kpi-val" style="color:#b03a28">${servicosFiltrados.filter(s=>s.d>5).length}</div></div>
    </div>
    ${renderServicosTable(servicosFiltrados, state)}
  `;
}

function renderGestaoAcessosView() {
  const pMaster = authService.getPerfilAtivo();
  if (!pMaster.is_master) {
    return `<div style="background:#f8e7e3;color:#b03a28;padding:16px;border-radius:8px">Acesso Negado: Exclusivo Usuário Master.</div>`;
  }
  const perfis = authService.perfis;
  const usuarios = authService.usuarios;

  return `
    <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:20px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h3 style="margin:0">⚙ Gestão de Usuários e Permissões (Usuário Master)</h3>
        <button id="btn-add-user" class="btn-primary">+ Cadastrar Usuário</button>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="background:#f7f9f8;border-bottom:2px solid var(--border-subtle);text-align:left">
            <th style="padding:8px">Perfil</th>
            ${TELAS_DEF.map(t => `<th style="padding:8px;text-align:center">${t.label}</th>`).join('')}
            <th style="padding:8px;text-align:right">Ações</th>
          </tr>
        </thead>
        <tbody>
          ${Object.keys(perfis).map(pKey => {
            const p = perfis[pKey];
            return `
              <tr style="border-bottom:1px solid var(--border-subtle)">
                <td style="padding:8px;font-weight:700">${p.nome} ${p.is_master ? '(MASTER)' : ''}</td>
                ${TELAS_DEF.map(t => `
                  <td style="padding:8px;text-align:center">
                    <input type="checkbox" class="check-perm" data-perfil="${pKey}" data-tela="${t.id}" ${p.is_master || p.telas.includes(t.id) ? 'checked' : ''} ${p.is_master ? 'disabled' : ''}>
                  </td>
                `).join('')}
                <td style="padding:8px;text-align:right">
                  ${!p.is_master ? `<button class="btn-save-perm btn-secondary" data-perfil="${pKey}">Salvar</button>` : ''}
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>

      <h4 style="margin:20px 0 10px">Usuários Cadastrados</h4>
      <ul style="font-size:12px;padding-left:20px">
        ${usuarios.map(u => `<li><b>${u.nome}</b> (${u.email}) — Perfil: <i>${u.perfil}</i></li>`).join('')}
      </ul>
    </div>
  `;
}

function renderServicosTable(servicos, state) {
  return `
    <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left">
            <th style="padding:8px;width:30px"><input type="checkbox" id="check-all"></th>
            <th style="padding:8px">Status</th>
            <th style="padding:8px">SOB / Serviço</th>
            <th style="padding:8px">Nota</th>
            <th style="padding:8px;text-align:right">Valor</th>
          </tr>
        </thead>
        <tbody>
          ${servicos.map(s => `
            <tr class="row-svc" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;cursor:pointer">
              <td style="padding:8px" onclick="event.stopPropagation()">
                <input type="checkbox" class="check-svc" data-id="${s.id}" ${state.selecionados.includes(s.id)?'checked':''}>
              </td>
              <td style="padding:8px">
                <span style="font-weight:600;padding:2px 6px;border-radius:4px;background:#eaf2ee;color:#14483a">${padNum(s.st)}. ${STATUS_DEFS[s.st]?.n}</span>
              </td>
              <td style="padding:8px"><b>${s.id}</b> — ${s.ob} (${s.tp})</td>
              <td style="padding:8px">${s.nota || '—'}</td>
              <td style="padding:8px;text-align:right;font-weight:600">${formatMoney(s.v)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderPendenciasPanel(pendSvcs, state) {
  const foco = pendSvcs.find(s => s.id === state.servicoFocoId);
  return `
    <div style="display:flex;gap:14px">
      <div style="flex:1">${renderServicosTable(pendSvcs, state)}</div>
      <div style="width:300px;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:14px">
        ${foco ? `
          <h4 style="margin:0 0 10px">${foco.id} — Checklist</h4>
          ${(foco.pend || []).map((p, idx) => `
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12px">
              <button class="btn-toggle-pend" data-idx="${idx}" style="cursor:pointer">${p.tr ? '✓' : '✕'}</button>
              <span>${p.t}</span>
            </div>
          `).join('')}
        ` : `<div style="font-size:12px;color:#8a9791">Clique em uma linha para tratar pendências.</div>`}
      </div>
    </div>
  `;
}

function renderDrawer(state) {
  if (!state.drawerServicoId) return '';
  const s = state.servicos.find(x => x.id === state.drawerServicoId);
  if (!s) return '';
  return `
    <div class="drawer-panel">
      <div style="padding:16px;border-bottom:1px solid var(--border-subtle);display:flex;justify-content:space-between">
        <h3 style="margin:0">${s.id} — ${formatMoney(s.v)}</h3>
        <button id="btn-close-drawer" style="cursor:pointer">×</button>
      </div>
      <div style="padding:16px;flex:1;overflow-y:auto;font-size:12px">
        <p><b>Obra:</b> ${s.ob} | <b>Tipo:</b> ${s.tp}</p>
        <p><b>Contrato:</b> ${CONTRATOS[s.ct] || s.ct}</p>
        <hr>
        <h4>Atividades Baremo</h4>
        <ul>
          ${(s.bar || []).map(b => `<li>${b.cod} ${b.desc}: ${formatMoney(b.med)}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;
}

function attachViewListeners(root, state, servicosFiltrados) {
  root.querySelectorAll('.btn-save-perm').forEach(btn => {
    btn.addEventListener('click', () => {
      const pKey = btn.getAttribute('data-perfil');
      const cbs = root.querySelectorAll(`.check-perm[data-perfil="${pKey}"]`);
      const telas = [];
      cbs.forEach(cb => { if (cb.checked) telas.push(cb.getAttribute('data-tela')); });
      authService.atualizarPermissoes(pKey, telas);
      store.notifyToast(`Permissões salvas para ${pKey}`);
    });
  });

  root.querySelector('#btn-add-user')?.addEventListener('click', () => {
    const nome = prompt('Nome:'); if (!nome) return;
    const email = prompt('E-mail:'); if (!email) return;
    const perfil = prompt('Perfil (Master, Fechamento, Operação, Faturamento):', 'Operação');
    authService.adicionarUsuario(nome, email, perfil);
    store.notifyToast(`Usuário ${nome} adicionado!`);
    renderApp(store.getState());
  });

  root.querySelectorAll('.row-svc').forEach(row => {
    row.addEventListener('click', () => {
      const sId = row.getAttribute('data-id');
      if (state.telaAtiva === 'pendencias') store.setState({ servicoFocoId: sId });
      else store.setState({ drawerServicoId: sId });
    });
  });

  root.querySelectorAll('.btn-toggle-pend').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = Number(btn.getAttribute('data-idx'));
      if (state.servicoFocoId) store.tratarPendenciaItem(state.servicoFocoId, idx);
    });
  });

  root.querySelector('#btn-close-drawer')?.addEventListener('click', () => store.setState({ drawerServicoId: null }));
}

// Inicialização ao carregar o DOM
document.addEventListener('DOMContentLoaded', () => {
  store.subscribe(state => renderApp(state));
  renderApp(store.getState());
});
