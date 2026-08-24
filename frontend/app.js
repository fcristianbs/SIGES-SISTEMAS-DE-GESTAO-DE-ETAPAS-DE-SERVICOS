/* ==========================================================================
   SIGES - SISTEMA DE GESTÃO DE ETAPAS DE SERVIÇOS (COSAMPA)
   Front-end SPA com Paginação de 10 itens por página e Conexão Real MySQL
   ========================================================================== */

const STATUS_DEFS = {
  1: { n: 'Aguardando Conferência', a: 'Fechamento', m: 'med', sla: 3, color: '#1c5f4b', bg: '#eaf2ee', fg: '#14483a' },
  2: { n: 'Pendências Operacionais', a: 'Operação', m: 'pen', sla: 5, color: '#b03a28', bg: '#fdf2f0', fg: '#b03a28' },
  3: { n: 'Aguard. Envio p/ Validação', a: 'Fechamento', m: 'med', sla: 2, color: '#2b6e58', bg: '#eef6f3', fg: '#1c5f4b' },
  4: { n: 'Aguard. Validação do Cliente', a: 'Faturamento', m: 'fat', sla: 7, color: '#d97706', bg: '#fef3c7', fg: '#92400e' },
  5: { n: 'Rejeitado na Validação (Fech.)', a: 'Fechamento', m: 'med', sla: 3, color: '#dc2626', bg: '#fee2e2', fg: '#991b1b' },
  6: { n: 'Rejeitado na Validação (Oper.)', a: 'Operação', m: 'pen', sla: 5, color: '#dc2626', bg: '#fee2e2', fg: '#991b1b' },
  7: { n: 'Validado — Aguard. Autorização', a: 'Faturamento', m: 'fat', sla: 3, color: '#059669', bg: '#d1fae5', fg: '#065f46' },
  8: { n: 'Faturado — Aguard. Conciliação', a: 'Faturamento', m: 'con', sla: 10, color: '#2563eb', bg: '#dbeafe', fg: '#1e40af' },
  9: { n: 'Análise de Conciliação', a: 'Faturamento', m: 'con', sla: 5, color: '#4f46e5', bg: '#e0e7ff', fg: '#3730a3' },
  10: { n: 'Conciliado c/ Divergências', a: 'Fechamento', m: 'med', sla: 4, color: '#ea580c', bg: '#ffedd5', fg: '#9a3412' },
  11: { n: 'Pgto a Menor — Cobrar Cliente', a: 'Fechamento', m: 'med', sla: 7, color: '#c026d3', bg: '#fae8ff', fg: '#86198f' },
  12: { n: 'Pgto a Menor — Em Disputa', a: 'Fechamento', m: 'med', sla: 15, color: '#9333ea', bg: '#f3e8ff', fg: '#6b21a8' },
  13: { n: 'Faturado Total', a: 'Geral', m: 'fin', sla: null, color: '#16a34a', bg: '#dcfce7', fg: '#15803d' },
  14: { n: 'Faturado a Maior', a: 'Geral', m: 'fin', sla: null, color: '#0891b2', bg: '#cffafe', fg: '#155e75' },
  15: { n: 'Faturado a Menor', a: 'Geral', m: 'fin', sla: null, color: '#475569', bg: '#f1f5f9', fg: '#334155' }
};

const TELAS_DEF = [
  { id: 'gerencial', label: 'Gerencial', icon: '★', url: 'index.html' },
  { id: 'medicao', label: '01. Medição', icon: '01', url: 'medicao.html' },
  { id: 'pendencias', label: '02. Pendências', icon: '02', url: 'pendencias.html' },
  { id: 'faturamento', label: '03. Faturamento', icon: '03', url: 'faturamento.html' },
  { id: 'conciliacoes', label: '04. Conciliações', icon: '04', url: 'conciliacoes.html' },
  { id: 'finalizados', label: '05. Finalizados', icon: '05', url: 'finalizados.html' },
  { id: 'relatorios', label: 'Consultas + Relatórios', icon: 'C·R', url: 'relatorios.html' },
  { id: 'gestao_acessos', label: 'Gestão de Acessos', icon: '⚙', url: 'gestao_acessos.html', masterOnly: true }
];

const PERFIS_INICIAIS = {
  'Master': { nome: 'Master', is_master: true, telas: ['gerencial', 'medicao', 'pendencias', 'faturamento', 'conciliacoes', 'finalizados', 'relatorios', 'gestao_acessos'] },
  'Fechamento': { nome: 'Fechamento', is_master: false, telas: ['gerencial', 'medicao', 'pendencias', 'finalizados', 'relatorios'] },
  'Operação': { nome: 'Operação', is_master: false, telas: ['gerencial', 'pendencias', 'finalizados', 'relatorios'] },
  'Faturamento': { nome: 'Faturamento', is_master: false, telas: ['gerencial', 'medicao', 'pendencias', 'faturamento', 'conciliacoes', 'finalizados', 'relatorios'] }
};

const USUARIOS_INICIAIS = [
  { id: 1, nome: 'Administrador Master', email: 'admin@cosampa.com.br', perfil: 'Master', telas_custom: null },
  { id: 2, nome: 'Carlos Fechamento', email: 'carlos@cosampa.com.br', perfil: 'Fechamento', telas_custom: null },
  { id: 3, nome: 'Fernanda Operação', email: 'fernanda@cosampa.com.br', perfil: 'Operação', telas_custom: null },
  { id: 4, nome: 'Roberto Faturamento', email: 'roberto@cosampa.com.br', perfil: 'Faturamento', telas_custom: null }
];

class AuthService {
  constructor() {
    this.perfis = JSON.parse(localStorage.getItem('siges_perfis')) || { ...PERFIS_INICIAIS };
    this.usuarios = JSON.parse(localStorage.getItem('siges_usuarios')) || [ ...USUARIOS_INICIAIS ];
    this.usuarioLogado = JSON.parse(localStorage.getItem('siges_usuario_logado')) || null;
  }

  isAutenticado() { return !!this.usuarioLogado; }

  login(email) {
    const user = this.usuarios.find(u => u.email.toLowerCase() === email.toLowerCase()) || {
      id: Date.now(), nome: email.split('@')[0], email: email, perfil: 'Master', telas_custom: null
    };
    this.usuarioLogado = user;
    this.salvar();
    return user;
  }

  logout() {
    this.usuarioLogado = null;
    localStorage.removeItem('siges_usuario_logado');
    window.location.href = 'login.html';
  }

  getPerfilAtivo() {
    if (!this.usuarioLogado) return null;
    return this.perfis[this.usuarioLogado.perfil] || this.perfis['Master'];
  }

  temAcessoTela(telaId) {
    if (!this.usuarioLogado) return false;
    if (this.usuarioLogado.telas_custom && Array.isArray(this.usuarioLogado.telas_custom)) {
      return this.usuarioLogado.telas_custom.includes(telaId);
    }
    const p = this.getPerfilAtivo();
    if (!p) return false;
    if (p.is_master) return true;
    return p.telas.includes(telaId);
  }

  atualizarPermissoesPerfil(nomePerfil, novasTelas) {
    if (this.perfis[nomePerfil]) {
      this.perfis[nomePerfil].telas = novasTelas;
      this.salvar();
    }
  }

  atualizarPermissoesUsuario(usuarioId, novasTelas) {
    const u = this.usuarios.find(x => x.id === usuarioId);
    if (u) {
      u.telas_custom = novasTelas;
      if (this.usuarioLogado && this.usuarioLogado.id === usuarioId) {
        this.usuarioLogado.telas_custom = novasTelas;
      }
      this.salvar();
    }
  }

  adicionarUsuario(nome, email, perfil) {
    const u = { id: Date.now(), nome, email, perfil, telas_custom: null };
    this.usuarios.push(u);
    this.salvar();
    return u;
  }

  salvar() {
    if (this.usuarioLogado) {
      localStorage.setItem('siges_usuario_logado', JSON.stringify(this.usuarioLogado));
    }
    localStorage.setItem('siges_perfis', JSON.stringify(this.perfis));
    localStorage.setItem('siges_usuarios', JSON.stringify(this.usuarios));
  }
}

const authService = new AuthService();

class Store {
  constructor() {
    this.state = {
      telaAtualId: document.body.getAttribute('data-page-id') || 'gerencial',
      pinSidebar: true,
      filtros: { periodo: 'mes', contrato: 'todos', tipo: 'todos', area: 'todas', status: 'todos', busca: '' },
      presets: JSON.parse(localStorage.getItem('siges_presets')) || [{ id: 'p1', nome: 'Todos os Contratos', filtros: { periodo: 'mes', contrato: 'todos', tipo: 'todos', area: 'todas', status: 'todos', busca: '' } }],
      modeGestao: 'perfil',
      usuarioGestaoId: 3,
      selecionados: [],
      servicoFocoId: null,
      drawerServicoId: null,
      toast: null,
      carregando: false,
      paginaAtual: 1,
      itensPorPagina: 10,
      servicos: []
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
    localStorage.setItem('siges_presets', JSON.stringify(this.state.presets));
    this.listeners.forEach(l => l(this.state));
  }

  async carregarServicosAPI() {
    this.setState({ carregando: true });
    try {
      const f = this.state.filtros;
      const params = new URLSearchParams();
      if (f.contrato !== 'todos') params.append('contrato', f.contrato);
      if (f.tipo !== 'todos') params.append('tipo', f.tipo);
      if (f.status !== 'todos') params.append('status_id', f.status);
      if (f.busca) params.append('busca', f.busca);

      const res = await fetch(`/api/servicos?${params.toString()}`);
      if (res.ok) {
        const dados = await res.json();
        const focoId = dados.length > 0 ? dados[0].id : null;
        this.setState({ servicos: dados, servicoFocoId: focoId, carregando: false, paginaAtual: 1 });
      } else {
        this.setState({ carregando: false });
      }
    } catch (e) {
      console.warn('Erro ao buscar API /api/servicos:', e);
      this.setState({ carregando: false });
    }
  }

  notifyToast(msg) {
    this.setState({ toast: msg });
    setTimeout(() => {
      if (this.state.toast === msg) this.setState({ toast: null });
    }, 4200);
  }

  getServicosFiltrados() {
    const f = this.state.filtros;
    return this.state.servicos.filter(s => {
      if (f.contrato !== 'todos' && s.ct !== f.contrato) return false;
      if (f.tipo !== 'todos' && s.tp !== f.tipo) return false;
      if (f.status && f.status !== 'todos' && s.st !== Number(f.status)) return false;
      if (f.busca) {
        const q = f.busca.toLowerCase();
        if (!`${s.id} ${s.ob} ${s.tp} ${s.ct}`.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }

  tratarPendenciaItem(servicoId, indexItem, novoDet = null, anexoNome = null) {
    let ret = false;
    const novos = this.state.servicos.map(s => {
      if (s.id === servicoId && s.pend) {
        const pList = s.pend.map((p, idx) => {
          if (idx === indexItem) {
            return {
              ...p,
              tr: (novoDet === null && anexoNome === null) ? !p.tr : p.tr,
              det: novoDet !== null ? novoDet : p.det,
              anx: anexoNome !== null ? anexoNome : p.anx
            };
          }
          return p;
        });
        let novoSt = s.st;
        if (pList.every(p => p.tr) && (s.st === 2 || s.st === 6)) {
          novoSt = 1;
          ret = true;
        }
        return { ...s, pend: pList, st: novoSt };
      }
      return s;
    });
    this.setState({ servicos: novos });
    if (ret) this.notifyToast(`${servicoId} — Todas as pendências foram tratadas! Retornou para 01. Aguardando Conferência.`);
  }
}

const store = new Store();

function initPage() {
  const pageId = document.body.getAttribute('data-page-id') || 'gerencial';

  if (pageId === 'login') {
    bindLoginPage();
    return;
  }

  if (!authService.isAutenticado()) {
    window.location.href = 'login.html';
    return;
  }

  if (!authService.temAcessoTela(pageId)) {
    alert(`Acesso negado ao usuário "${authService.usuarioLogado.nome}". Redirecionando para a página principal.`);
    window.location.href = 'index.html';
    return;
  }

  localStorage.removeItem('siges_svcs');
  store.subscribe(state => renderPageUI(pageId, state));
  store.carregarServicosAPI();
}

function bindLoginPage() {
  const form = document.getElementById('form-login');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      authService.login(email);
      window.location.href = 'index.html';
    });
  }

  document.querySelectorAll('.btn-quick-login').forEach(btn => {
    btn.addEventListener('click', () => {
      const email = btn.getAttribute('data-email');
      authService.login(email);
      window.location.href = 'index.html';
    });
  });
}

function renderPaginador(totalItens, paginaAtual, itensPorPagina = 10) {
  const totalPaginas = Math.ceil(totalItens / itensPorPagina) || 1;
  const inicio = totalItens === 0 ? 0 : (paginaAtual - 1) * itensPorPagina + 1;
  const fim = Math.min(paginaAtual * itensPorPagina, totalItens);

  let paginasBtns = [];
  const maxBtns = 5;
  let startP = Math.max(1, paginaAtual - 2);
  let endP = Math.min(totalPaginas, startP + maxBtns - 1);
  if (endP - startP < maxBtns - 1) {
    startP = Math.max(1, endP - maxBtns + 1);
  }

  for (let i = startP; i <= endP; i++) {
    paginasBtns.push(`
      <button class="btn-pag-num ${i === paginaAtual ? 'active' : ''}" data-page="${i}" style="padding:4px 9px;border:1px solid ${i === paginaAtual ? 'var(--ac-primary)' : '#d7dedb'};background:${i === paginaAtual ? 'var(--ac-primary)' : '#fff'};color:${i === paginaAtual ? '#fff' : '#334155'};border-radius:5px;font-weight:600;font-size:11.5px;cursor:pointer">
        ${i}
      </button>
    `);
  }

  return `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#f7f9f8;border-top:1px solid var(--border-subtle);font-size:11.5px;color:#5b6b65">
      <div>Exibindo <b>${inicio}–${fim}</b> de <b>${totalItens}</b> serviços</div>
      <div style="display:flex;align-items:center;gap:4px">
        <button id="btn-pag-ant" ${paginaAtual <= 1 ? 'disabled' : ''} style="padding:4px 9px;border:1px solid #d7dedb;background:#fff;border-radius:5px;font-size:11.5px;cursor:${paginaAtual <= 1 ? 'not-allowed' : 'pointer'};opacity:${paginaAtual <= 1 ? 0.5 : 1}">
          « Anterior
        </button>
        ${paginasBtns.join('')}
        <button id="btn-pag-prox" ${paginaAtual >= totalPaginas ? 'disabled' : ''} style="padding:4px 9px;border:1px solid #d7dedb;background:#fff;border-radius:5px;font-size:11.5px;cursor:${paginaAtual >= totalPaginas ? 'not-allowed' : 'pointer'};opacity:${paginaAtual >= totalPaginas ? 0.5 : 1}">
          Próxima »
        </button>
      </div>
    </div>
  `;
}

function bindPaginadorEvents(container, totalItens) {
  const itensPorPagina = 10;
  const totalPaginas = Math.ceil(totalItens / itensPorPagina) || 1;
  const state = store.getState();

  container.querySelector('#btn-pag-ant')?.addEventListener('click', () => {
    if (state.paginaAtual > 1) {
      store.setState({ paginaAtual: state.paginaAtual - 1 });
    }
  });

  container.querySelector('#btn-pag-prox')?.addEventListener('click', () => {
    if (state.paginaAtual < totalPaginas) {
      store.setState({ paginaAtual: state.paginaAtual + 1 });
    }
  });

  container.querySelectorAll('.btn-pag-num').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = Number(btn.getAttribute('data-page'));
      store.setState({ paginaAtual: p });
    });
  });
}

function renderPageUI(pageId, state) {
  const user = authService.usuarioLogado;
  const perfilAtivo = authService.getPerfilAtivo();
  const servicosFiltrados = store.getServicosFiltrados();

  // Sidebar
  const sidebar = document.getElementById('sidebar-container');
  if (sidebar) {
    sidebar.style.width = state.pinSidebar ? '236px' : '62px';
    sidebar.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;padding:13px 14px;border-bottom:1px solid var(--border-dark)">
        <div style="width:32px;height:32px;border-radius:8px;background:var(--ac-primary);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex-shrink:0">C</div>
        ${state.pinSidebar ? `
          <div style="flex:1">
            <div style="font-size:13px;font-weight:700;color:#eef3f1">Cosampa</div>
            <div style="font-size:10.5px;color:#7d8c86">Esteira de Faturamento</div>
          </div>
          <button id="btn-pin" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);color:#c6d2cc;border-radius:7px;width:26px;height:26px;font-size:12px;padding:0">${state.pinSidebar ? '«' : '»'}</button>
        ` : ''}
      </div>
      <div style="padding:10px 0;flex:1;overflow-y:auto">
        ${TELAS_DEF.map(t => {
          const ok = authService.temAcessoTela(t.id);
          const at = pageId === t.id;
          return `
            <a href="${ok ? t.url : '#'}" style="text-decoration:none">
              <div style="display:flex;align-items:center;gap:11px;margin:2px 9px;padding:8px 9px;border-radius:8px;font-size:13px;background:${at ? 'var(--ac-primary)' : 'transparent'};color:${at ? '#fff' : ok ? '#c6d2cc' : '#5c6a64'};opacity:${ok ? 1 : 0.45};cursor:${ok ? 'pointer' : 'not-allowed'}">
                <span style="font-family:var(--font-mono);font-size:11px;font-weight:600;min-width:26px;text-align:center">${t.icon}</span>
                ${state.pinSidebar ? `<span>${t.label}</span>` : ''}
              </div>
            </a>
          `;
        }).join('')}
      </div>
      ${state.pinSidebar ? `<div style="padding:12px 16px;border-top:1px solid var(--border-dark);font-size:10.5px;color:#67766f">Operador: <b>${user.nome}</b></div>` : ''}
    `;
    sidebar.querySelector('#btn-pin')?.addEventListener('click', () => store.setState({ pinSidebar: !state.pinSidebar }));
  }

  // Header
  const header = document.getElementById('header-container');
  if (header) {
    const info = TELAS_DEF.find(t => t.id === pageId) || { label: 'Gerencial' };
    header.innerHTML = `
      <div class="top-header">
        <div style="font-size:16.5px;font-weight:700">${info.label}</div>
        <span style="font-size:10px;font-weight:600;color:#5b6b65;border:1px solid #d7dedb;border-radius:6px;padding:3px 7px;text-transform:uppercase">Satélite GPM</span>
        <div style="flex:1"></div>
        <div style="display:flex;align-items:center;gap:12px">
          <div style="text-align:right">
            <div style="font-size:12px;font-weight:700">${user.nome}</div>
            <div style="font-size:10.5px;color:#71807a">Perfil: <b>${perfilAtivo.nome}</b></div>
          </div>
          <button id="btn-logout" class="btn-secondary" style="font-size:11px;padding:5px 10px">Sair</button>
        </div>
      </div>
    `;
    header.querySelector('#btn-logout')?.addEventListener('click', () => authService.logout());
  }

  // FilterBar Dinâmica
  const filterBar = document.getElementById('filterbar-container');
  if (filterBar && pageId !== 'gestao_acessos') {
    const contratosUnicos = Array.from(new Set(state.servicos.map(s => s.ct))).filter(Boolean);
    const tiposUnicos = Array.from(new Set(state.servicos.map(s => s.tp))).filter(Boolean);

    filterBar.innerHTML = `
      <div class="filter-bar">
        <select id="f-periodo" class="select-input">
          <option value="mes" ${state.filtros.periodo==='mes'?'selected':''}>Período Total (GPM)</option>
          <option value="7d" ${state.filtros.periodo==='7d'?'selected':''}>Últimos 7 dias</option>
        </select>
        <select id="f-contrato" class="select-input">
          <option value="todos" ${state.filtros.contrato==='todos'?'selected':''}>Todos os contratos (${contratosUnicos.length})</option>
          ${contratosUnicos.map(c => `<option value="${c}" ${state.filtros.contrato===c?'selected':''}>${c}</option>`).join('')}
        </select>
        <select id="f-tipo" class="select-input">
          <option value="todos" ${state.filtros.tipo==='todos'?'selected':''}>Todos os tipos (${tiposUnicos.length})</option>
          ${tiposUnicos.map(tp => `<option value="${tp}" ${state.filtros.tipo===tp?'selected':''}>${tp}</option>`).join('')}
        </select>
        <select id="f-status" class="select-input">
          <option value="todos" ${state.filtros.status==='todos'?'selected':''}>Todos os status (15)</option>
          ${Object.keys(STATUS_DEFS).map(k => `<option value="${k}" ${state.filtros.status===k?'selected':''}>0${k}. ${STATUS_DEFS[k].n}</option>`).join('')}
        </select>
        <input id="f-busca" class="text-input" value="${state.filtros.busca}" placeholder="Buscar SOB, obra, contrato..." style="width:220px">
      </div>
    `;
    filterBar.querySelector('#f-contrato')?.addEventListener('change', (e) => {
      store.setState({ filtros: { ...store.getState().filtros, contrato: e.target.value }, paginaAtual: 1 });
    });
    filterBar.querySelector('#f-tipo')?.addEventListener('change', (e) => {
      store.setState({ filtros: { ...store.getState().filtros, tipo: e.target.value }, paginaAtual: 1 });
    });
    filterBar.querySelector('#f-status')?.addEventListener('change', (e) => {
      store.setState({ filtros: { ...store.getState().filtros, status: e.target.value }, paginaAtual: 1 });
    });
    filterBar.querySelector('#f-busca')?.addEventListener('input', (e) => {
      store.setState({ filtros: { ...store.getState().filtros, busca: e.target.value }, paginaAtual: 1 });
    });
  }

  // Renderização da Tela
  if (pageId === 'gerencial') renderGerencial(servicosFiltrados, state);
  else if (pageId === 'medicao') renderMedicao(servicosFiltrados, state);
  else if (pageId === 'pendencias') renderPendencias(servicosFiltrados.filter(s => s.st === 2 || s.st === 6), state);
  else if (pageId === 'gestao_acessos') renderGestaoAcessos();
  else renderGenericScreen(pageId, servicosFiltrados);

  renderDrawer(state);
  renderToast(state.toast);
}

// --- DASHBOARD GERENCIAL COM PAGINAÇÃO NO RADAR ---
function renderGerencial(svcs, state) {
  const container = document.querySelector('.view-container');
  if (!container) return;

  const totalValor = svcs.reduce((a, s) => a + s.v, 0);
  const estourados = svcs.filter(s => s.d > 5);

  const pag = state.paginaAtual || 1;
  const pagItens = svcs.slice((pag - 1) * 10, pag * 10);

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:14px;max-width:1420px">
      <!-- 4 KPI Cards com Dados do MySQL -->
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Serviços na Esteira</div>
          <div class="kpi-val">${svcs.length}</div>
          <div style="font-size:11.5px;color:#71807a;margin-top:4px">Base Real MySQL (siges.servicos)</div>
        </div>
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Valor na Esteira</div>
          <div class="kpi-val">R$ ${(totalValor/1000).toFixed(1)} mil</div>
          <div style="font-size:11.5px;color:#71807a;margin-top:4px">soma da amostragem ativa</div>
        </div>
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Por Macroetapa</div>
          <div style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin-top:12px;background:#f0f3f2">
            <div style="width:50%;background:#1c5f4b" title="Medição"></div>
            <div style="width:20%;background:#b03a28" title="Pendências"></div>
            <div style="width:15%;background:#d97706" title="Faturamento"></div>
            <div style="width:15%;background:#2563eb" title="Conciliação"></div>
          </div>
          <div style="font-size:10.5px;color:#71807a;margin-top:8px">Medição · Pendências · Faturamento</div>
        </div>
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Tempo Médio na Etapa</div>
          <div class="kpi-val">3,0 d</div>
          <div style="font-size:11.5px;color:var(--color-alert);margin-top:4px;font-weight:600">${estourados.length} com SLA estourado</div>
        </div>
      </div>

      <!-- Gráfico de Status por Colunas -->
      <div style="display:grid;grid-template-columns:1.55fr 1fr;gap:14px">
        <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px">
          <div style="display:flex;justify-content:space-between;align-items:baseline">
            <span style="font-size:13px;font-weight:700">Serviços por status (Base Real)</span>
            <span style="font-size:11px;color:#8a9791">${svcs.length} serviços carregados</span>
          </div>
          <div style="display:flex;align-items:flex-end;gap:5px;height:158px;margin-top:14px">
            ${(() => {
              const statusCounts = Object.keys(STATUS_DEFS).map(stId => svcs.filter(s => s.st === Number(stId)).length);
              const maxC = Math.max(...statusCounts, 1);
              return Object.keys(STATUS_DEFS).map(stId => {
                const def = STATUS_DEFS[stId];
                const c = svcs.filter(s => s.st === Number(stId)).length;
                const h = c > 0 ? Math.max(6, Math.round((c / maxC) * 125)) : 4;
                return `
                  <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%">
                    <span style="font-family:var(--font-mono);font-size:10px;color:#5b6b65">${c}</span>
                    <div style="width:100%;max-width:24px;height:${h}px;background:${def.color};border-radius:4px 4px 0 0" title="0${stId}. ${def.n}"></div>
                    <span style="font-family:var(--font-mono);font-size:9.5px;color:#8a9791;margin-top:4px">0${stId}</span>
                  </div>
                `;
              }).join('');
            })()}
          </div>
        </div>

        <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px">
          <span style="font-size:13px;font-weight:700">Valor parado por macroetapa</span>
          <div style="margin-top:14px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:11px">
              <span style="width:86px;font-size:11.5px">Medição</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:75%;height:100%;background:#1c5f4b"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ ${(totalValor*0.6/1000).toFixed(1)}k</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:11px">
              <span style="width:86px;font-size:11.5px">Pendências</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:25%;height:100%;background:#b03a28"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ ${(totalValor*0.2/1000).toFixed(1)}k</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
              <span style="width:86px;font-size:11.5px">Finalizados</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:40%;height:100%;background:#16a34a"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ ${(totalValor*0.2/1000).toFixed(1)}k</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Radar de Serviços Reais com Paginação de 10 Itens por Página -->
      <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
        <div style="padding:14px 18px;border-bottom:1px solid var(--border-subtle);font-size:13px;font-weight:700">Radar da Operação — Registros Recentes (Paginação de 10 por página)</div>
        ${pagItens.map(s => {
          const stDef = STATUS_DEFS[s.st] || STATUS_DEFS[1];
          return `
            <div class="row-svc" data-id="${s.id}" style="display:grid;grid-template-columns:180px 140px 1fr 140px 120px 80px;gap:10px;align-items:center;padding:10px 18px;border-bottom:1px solid #eef1f0;cursor:pointer">
              <span class="badge-status" style="background:${stDef.bg};color:${stDef.fg}">
                <span class="badge-status-num">0${s.st}</span> ${stDef.n}
              </span>
              <span style="font-family:var(--font-mono);font-weight:600">${s.id}</span>
              <span><b>${s.ob}</b> <small style="color:#71807a">(${s.tp})</small></span>
              <span style="font-size:11px;color:#5b6b65;font-weight:600">${s.ct}</span>
              <span style="font-weight:600;font-family:var(--font-mono);text-align:right">R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
              <span style="color:var(--ac-primary);font-weight:600;text-align:right">Abrir →</span>
            </div>
          `;
        }).join('')}
        ${renderPaginador(svcs.length, pag, 10)}
      </div>
    </div>
  `;

  bindPaginadorEvents(container, svcs.length);

  container.querySelectorAll('.row-svc').forEach(row => {
    row.addEventListener('click', () => {
      const id = row.getAttribute('data-id');
      store.setState({ drawerServicoId: id });
    });
  });
}

function renderMedicao(svcs, state) {
  const container = document.querySelector('.view-container');
  if (!container) return;

  const pag = state.paginaAtual || 1;
  const pagItens = svcs.slice((pag - 1) * 10, pag * 10);

  container.innerHTML = `
    <div style="display:flex;gap:14px;align-items:flex-start">
      <div style="flex:1;min-width:0;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left;font-size:10.5px;color:#71807a;font-weight:700">
              <th style="padding:10px 12px;width:28px"><input type="checkbox" id="check-all-med"></th>
              <th style="padding:10px">STATUS</th>
              <th style="padding:10px">SERVIÇO</th>
              <th style="padding:10px">CONTRATO</th>
              <th style="padding:10px">DATA</th>
              <th style="padding:10px">BASE</th>
              <th style="padding:10px;text-align:right">VALOR</th>
              <th style="padding:10px">RETORNO</th>
            </tr>
          </thead>
          <tbody>
            ${pagItens.map(s => {
              const def = STATUS_DEFS[s.st] || STATUS_DEFS[1];
              const isSel = state.selecionados.includes(s.id);
              return `
                <tr class="row-svc" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;background:${isSel ? '#eaf2ee' : '#fff'};cursor:pointer">
                  <td style="padding:10px 12px" onclick="event.stopPropagation()">
                    <input type="checkbox" class="check-svc" data-id="${s.id}" ${isSel ? 'checked' : ''}>
                  </td>
                  <td style="padding:10px">
                    <span class="badge-status" style="background:${def.bg};color:${def.fg}">
                      <span class="badge-status-num">0${s.st}</span> ${def.n}
                    </span>
                  </td>
                  <td style="padding:10px">
                    <b>${s.id}</b><br><small style="color:#71807a">${s.ob} · ${s.tp}</small>
                  </td>
                  <td style="padding:10px;font-weight:600;font-size:11px">${s.ct}</td>
                  <td style="padding:10px;font-family:var(--font-mono)">${s.data || '—'}</td>
                  <td style="padding:10px">${s.dep || '—'}</td>
                  <td style="padding:10px;text-align:right;font-weight:600;font-family:var(--font-mono)">R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                  <td style="padding:10px;font-size:11px;color:#71807a">${s.ret || '—'}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
        
        ${renderPaginador(svcs.length, pag, 10)}
      </div>

      <div style="width:280px;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
          <h4 style="margin:0;font-size:13px;font-weight:700">TRATATIVAS</h4>
          <span style="background:#3c4a45;color:#fff;font-size:10px;font-weight:700;border-radius:12px;padding:2px 8px;font-family:var(--font-mono)">${state.selecionados.length} sel.</span>
        </div>

        <div style="margin-bottom:18px">
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Alterar status</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:8px">Individual ou em massa.</div>
          <select id="select-bulk-status" class="select-input" style="width:100%;margin-bottom:8px">
            <option value="">Novo status...</option>
            ${Object.keys(STATUS_DEFS).map(k => `<option value="${k}">0${k}. ${STATUS_DEFS[k].n}</option>`).join('')}
          </select>
          <button id="btn-apply-bulk" class="btn-primary" style="width:100%">Aplicar aos selecionados</button>
        </div>

        <div style="border-top:1px solid var(--border-subtle);padding-top:14px">
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Grupo de pendências</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:10px">Envia os selecionados para 02. Pendências.</div>
          
          <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:12px">
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Documentos"> Documentos</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Fotos"> Fotos</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Materiais"> Materiais</label>
          </div>

          <button id="btn-enviar-pend" style="width:100%;background:#fdf3e3;color:#8a5a0d;border:1px solid #ecd9b7;border-radius:8px;padding:8px;font-size:12px;font-weight:600">Enviar para 02. Pendências</button>
        </div>
      </div>
    </div>
  `;

  bindPaginadorEvents(container, svcs.length);

  container.querySelector('#check-all-med')?.addEventListener('change', (e) => {
    const checked = e.target.checked;
    store.setState({ selecionados: checked ? svcs.map(s => s.id) : [] });
  });

  container.querySelectorAll('.check-svc').forEach(cb => {
    cb.addEventListener('change', (e) => {
      const id = cb.getAttribute('data-id');
      const sels = e.target.checked ? [...state.selecionados, id] : state.selecionados.filter(x => x !== id);
      store.setState({ selecionados: sels });
    });
  });

  container.querySelectorAll('.row-svc').forEach(row => {
    row.addEventListener('click', () => {
      const id = row.getAttribute('data-id');
      store.setState({ drawerServicoId: id });
    });
  });

  container.querySelector('#btn-apply-bulk')?.addEventListener('click', () => {
    const st = container.querySelector('#select-bulk-status').value;
    if (!st || state.selecionados.length === 0) return alert('Selecione serviços e um novo status.');
    const novos = state.servicos.map(s => state.selecionados.includes(s.id) ? { ...s, st: Number(st) } : s);
    store.setState({ servicos: novos, selecionados: [] });
    store.notifyToast(`Status alterado para ${state.selecionados.length} serviço(s)!`);
  });

  container.querySelector('#btn-enviar-pend')?.addEventListener('click', () => {
    if (state.selecionados.length === 0) return alert('Selecione serviços para enviar para pendências.');
    const gps = Array.from(container.querySelectorAll('.gp-check:checked')).map(c => c.value);
    const pItems = (gps.length ? gps : ['Geral']).map(t => ({ t, tr: false, det: '', anx: null }));

    const novos = state.servicos.map(s => {
      if (state.selecionados.includes(s.id)) {
        return { ...s, st: 2, pend: pItems };
      }
      return s;
    });

    store.setState({ servicos: novos, selecionados: [] });
    store.notifyToast(`${state.selecionados.length} serviço(s) enviado(s) para 02. Pendências Operacionais!`);
  });
}

function renderPendencias(svcs, state) {
  const container = document.querySelector('.view-container');
  if (!container) return;

  const pag = state.paginaAtual || 1;
  const pagItens = svcs.slice((pag - 1) * 10, pag * 10);
  const foco = pagItens.find(s => s.id === state.servicoFocoId) || pagItens[0] || svcs[0];

  container.innerHTML = `
    <div style="display:flex;gap:14px;align-items:flex-start">
      <div style="flex:1;min-width:0;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left;font-size:10.5px;color:#71807a;font-weight:700">
              <th style="padding:10px">STATUS</th>
              <th style="padding:10px">SERVIÇO</th>
              <th style="padding:10px">RETORNO / PENDÊNCIAS</th>
              <th style="padding:10px">DATA</th>
              <th style="padding:10px;text-align:right">VALOR</th>
            </tr>
          </thead>
          <tbody>
            ${pagItens.map(s => {
              const def = STATUS_DEFS[s.st] || STATUS_DEFS[2];
              const isFoco = foco && foco.id === s.id;
              return `
                <tr class="row-foco" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;background:${isFoco ? '#eaf2ee' : '#fff'};cursor:pointer">
                  <td style="padding:10px">
                    <span class="badge-status" style="background:${def.bg};color:${def.fg}">
                      <span class="badge-status-num">0${s.st}</span> ${def.n}
                    </span>
                  </td>
                  <td style="padding:10px">
                    <b>${s.id}</b><br><small style="color:#71807a">${s.ob} · ${s.tp}</small>
                  </td>
                  <td style="padding:10px;font-size:11.5px">
                    <span style="padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;background:#fee2e2;color:#991b1b">
                      ✕ ${s.ret || 'Retorno de Campo'}
                    </span>
                  </td>
                  <td style="padding:10px;font-family:var(--font-mono)">${s.data || '—'}</td>
                  <td style="padding:10px;text-align:right;font-weight:600;font-family:var(--font-mono)">R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>

        ${renderPaginador(svcs.length, pag, 10)}
      </div>

      <div style="width:320px;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px">
        ${foco ? `
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
            <h3 style="margin:0;font-size:15px;font-family:var(--font-mono)">${foco.id}</h3>
            <span id="btn-open-drawer-foco" style="font-size:11.5px;font-weight:600;color:var(--ac-primary);cursor:pointer">Detalhamento ↗</span>
          </div>

          <span class="badge-status" style="background:#ffedd5;color:#9a3412;margin-bottom:12px">
            <span class="badge-status-num">02</span> Pendências Operacionais
          </span>

          <div style="margin-top:10px">
            <div class="card-pendencia">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div style="display:flex;align-items:center;gap:8px">
                  <span style="font-size:13px;font-weight:700">${foco.ret || 'Pendência de Campo'}</span>
                </div>
                <span class="badge-pend-status badge-pend-pendente">PENDENTE</span>
              </div>

              <input class="text-input input-det-pend" value="" placeholder="Detalhamento da tratativa..." style="width:100%;font-size:11.5px">

              <div style="display:flex;align-items:center;gap:8px">
                <button class="btn-anexo btn-trigger-anexo">+ Anexo</button>
                <input type="file" class="file-input-hidden" style="display:none">
              </div>
            </div>
          </div>
        ` : `<div style="color:#71807a">Nenhum serviço em pendência operacional nesta amostragem.</div>`}
      </div>
    </div>
  `;

  bindPaginadorEvents(container, svcs.length);

  container.querySelectorAll('.row-foco').forEach(row => {
    row.addEventListener('click', () => {
      const id = row.getAttribute('data-id');
      store.setState({ servicoFocoId: id });
    });
  });

  container.querySelector('#btn-open-drawer-foco')?.addEventListener('click', () => {
    if (foco) store.setState({ drawerServicoId: foco.id });
  });
}

function renderGenericScreen(pageId, svcs) {
  const container = document.querySelector('.view-container');
  if (!container) return;
  const info = TELAS_DEF.find(t => t.id === pageId) || { label: pageId };

  const state = store.getState();
  const pag = state.paginaAtual || 1;
  const pagItens = svcs.slice((pag - 1) * 10, pag * 10);

  container.innerHTML = `
    <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
      <div style="padding:16px 20px;border-bottom:1px solid var(--border-subtle)">
        <h3 style="margin:0">${info.label}</h3>
        <p style="margin:4px 0 0;color:#71807a;font-size:12px">Exibindo registros reais carregados do banco MySQL <b>siges</b>:</p>
      </div>

      <table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left">
            <th style="padding:10px">Status</th>
            <th style="padding:10px">Serviço</th>
            <th style="padding:10px">Contrato</th>
            <th style="padding:10px">Tipo</th>
            <th style="padding:10px;text-align:right">Valor</th>
          </tr>
        </thead>
        <tbody>
          ${pagItens.map(s => {
            const def = STATUS_DEFS[s.st] || STATUS_DEFS[1];
            return `
              <tr class="row-svc" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;cursor:pointer">
                <td style="padding:10px">
                  <span class="badge-status" style="background:${def.bg};color:${def.fg}">
                    <span class="badge-status-num">0${s.st}</span> ${def.n}
                  </span>
                </td>
                <td style="padding:10px"><b>${s.id}</b> — ${s.ob}</td>
                <td style="padding:10px;font-weight:600">${s.ct}</td>
                <td style="padding:10px">${s.tp}</td>
                <td style="padding:10px;text-align:right;font-weight:600">R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>

      ${renderPaginador(svcs.length, pag, 10)}
    </div>
  `;

  bindPaginadorEvents(container, svcs.length);

  container.querySelectorAll('.row-svc').forEach(row => {
    row.addEventListener('click', () => {
      const id = row.getAttribute('data-id');
      store.setState({ drawerServicoId: id });
    });
  });
}

function renderGestaoAcessos() {
  const container = document.getElementById('gestao-acessos-container') || document.querySelector('.view-container');
  if (!container) return;

  const mode = store.getState().modeGestao || 'perfil';
  const perfis = authService.perfis;
  const usuarios = authService.usuarios;
  const usuarioFocoId = store.getState().usuarioGestaoId || usuarios[0].id;
  const usuarioFoco = usuarios.find(u => u.id === usuarioFocoId) || usuarios[0];

  container.innerHTML = `
    <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:20px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <div>
          <h3 style="margin:0">⚙ Gestão de Acessos a Telas (Usuário Master)</h3>
          <p style="margin:4px 0 0;font-size:11.5px;color:#71807a">Defina as permissões por Perfil Corporativo ou personalize individualmente por Usuário.</p>
        </div>
        <button id="btn-add-user" class="btn-primary">+ Cadastrar Usuário</button>
      </div>

      <div style="display:flex;gap:10px;margin-bottom:16px;background:#f7f9f8;padding:8px;border-radius:8px;border:1px solid var(--border-subtle)">
        <button id="btn-mode-perfil" class="${mode==='perfil'?'btn-primary':'btn-secondary'}" style="font-size:12px">Gerenciar por PERFIL</button>
        <button id="btn-mode-usuario" class="${mode==='usuario'?'btn-primary':'btn-secondary'}" style="font-size:12px">Gerenciar por USUÁRIO INDIVIDUAL</button>
      </div>

      ${mode === 'perfil' ? `
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:2px solid var(--border-subtle);text-align:left">
              <th style="padding:10px">Perfil</th>
              ${TELAS_DEF.map(t => `<th style="padding:10px;text-align:center">${t.label}</th>`).join('')}
              <th style="padding:10px;text-align:right">Ações</th>
            </tr>
          </thead>
          <tbody>
            ${Object.keys(perfis).map(pKey => {
              const p = perfis[pKey];
              return `
                <tr style="border-bottom:1px solid var(--border-subtle)">
                  <td style="padding:10px;font-weight:700">${p.nome} ${p.is_master ? '(MASTER)' : ''}</td>
                  ${TELAS_DEF.map(t => `
                    <td style="padding:10px;text-align:center">
                      <input type="checkbox" class="check-perm-perfil" data-perfil="${pKey}" data-tela="${t.id}" ${p.is_master || p.telas.includes(t.id) ? 'checked' : ''} ${p.is_master ? 'disabled' : ''}>
                    </td>
                  `).join('')}
                  <td style="padding:10px;text-align:right">
                    ${!p.is_master ? `<button class="btn-save-perm-perfil btn-secondary" data-perfil="${pKey}">Salvar Perfil</button>` : ''}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      ` : `
        <div style="display:flex;gap:14px">
          <div style="width:240px;border-right:1px solid var(--border-subtle);padding-right:14px">
            <h4 style="margin:0 0 10px">Selecione o Usuário:</h4>
            ${usuarios.map(u => `
              <div class="item-user-select" data-id="${u.id}" style="padding:8px 10px;border-radius:6px;cursor:pointer;margin-bottom:4px;background:${u.id===usuarioFoco.id?'#eaf2ee':'transparent'};font-weight:${u.id===usuarioFoco.id?'700':'400'}">
                ${u.nome} <br><small style="color:#71807a">${u.email} (${u.perfil})</small>
              </div>
            `).join('')}
          </div>

          <div style="flex:1">
            <h4 style="margin:0 0 6px">Permissões de: <b>${usuarioFoco.nome}</b> (${usuarioFoco.email})</h4>
            <p style="font-size:11.5px;color:#71807a;margin:0 0 14px">Perfil Base: ${usuarioFoco.perfil}. Desmarque as abas para remover o acesso deste usuário específico.</p>
            
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px">
              ${TELAS_DEF.map(t => {
                const temAcc = usuarioFoco.perfil === 'Master' || (usuarioFoco.telas_custom ? usuarioFoco.telas_custom.includes(t.id) : perfis[usuarioFoco.perfil]?.telas.includes(t.id));
                return `
                  <label style="display:flex;align-items:center;gap:8px;font-size:12px;padding:8px;border:1px solid var(--border-subtle);border-radius:6px;cursor:pointer">
                    <input type="checkbox" class="check-perm-user" data-tela="${t.id}" ${temAcc ? 'checked' : ''} ${usuarioFoco.perfil==='Master'?'disabled':''}>
                    <span><b>${t.label}</b> (${t.id})</span>
                  </label>
                `;
              }).join('')}
            </div>

            ${usuarioFoco.perfil !== 'Master' ? `<button id="btn-save-user-perms" class="btn-primary">Salvar Permissões do Usuário</button>` : ''}
          </div>
        </div>
      `}
    </div>
  `;

  container.querySelector('#btn-mode-perfil')?.addEventListener('click', () => store.setState({ modeGestao: 'perfil' }));
  container.querySelector('#btn-mode-usuario')?.addEventListener('click', () => store.setState({ modeGestao: 'usuario' }));

  container.querySelectorAll('.item-user-select').forEach(item => {
    item.addEventListener('click', () => {
      const id = Number(item.getAttribute('data-id'));
      store.setState({ usuarioGestaoId: id });
    });
  });

  container.querySelectorAll('.btn-save-perm-perfil').forEach(btn => {
    btn.addEventListener('click', () => {
      const pKey = btn.getAttribute('data-perfil');
      const cbs = container.querySelectorAll(`.check-perm-perfil[data-perfil="${pKey}"]`);
      const telas = [];
      cbs.forEach(cb => { if (cb.checked) telas.push(cb.getAttribute('data-tela')); });
      authService.atualizarPermissoesPerfil(pKey, telas);
      store.notifyToast(`Permissões do Perfil "${pKey}" salvas com sucesso!`);
    });
  });

  container.querySelector('#btn-save-user-perms')?.addEventListener('click', () => {
    const cbs = container.querySelectorAll('.check-perm-user');
    const telas = [];
    cbs.forEach(cb => { if (cb.checked) telas.push(cb.getAttribute('data-tela')); });
    authService.atualizarPermissoesUsuario(usuarioFoco.id, telas);
    store.notifyToast(`Permissões salvas para o usuário ${usuarioFoco.nome}!`);
  });

  container.querySelector('#btn-add-user')?.addEventListener('click', () => {
    const nome = prompt('Nome do Operador:'); if (!nome) return;
    const email = prompt('E-mail Corporativo:'); if (!email) return;
    const perfil = prompt('Perfil (Master, Fechamento, Operação, Faturamento):', 'Operação');
    authService.adicionarUsuario(nome, email, perfil);
    store.notifyToast(`Usuário ${nome} cadastrado!`);
    window.location.reload();
  });
}

function renderDrawer(state) {
  const container = document.getElementById('drawer-container');
  if (!container) return;
  if (!state.drawerServicoId) { container.innerHTML = ''; return; }
  const s = state.servicos.find(x => x.id === state.drawerServicoId);
  if (!s) return;

  container.innerHTML = `
    <div class="drawer-panel">
      <div style="padding:16px 20px;border-bottom:1px solid var(--border-subtle);display:flex;justify-content:space-between;align-items:center">
        <div>
          <h3 style="margin:0">${s.id} — R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</h3>
          <span style="font-size:11.5px;color:#71807a">${s.ob} (${s.tp})</span>
        </div>
        <button id="btn-close-drawer" style="background:none;border:none;font-size:22px;cursor:pointer">×</button>
      </div>
      <div style="padding:20px;flex:1;overflow-y:auto;font-size:12px">
        <p><b>Contrato:</b> ${s.ct}</p>
        <p><b>Status Atual:</b> 0${s.st}. ${STATUS_DEFS[s.st]?.n || 'Status'}</p>
        <p><b>Centro de Serviço:</b> ${s.dep || '—'}</p>
        <p><b>Data Execução / Geração:</b> ${s.data || '—'}</p>
        <p><b>Retorno de Campo:</b> ${s.ret || '—'}</p>
      </div>
    </div>
  `;

  container.querySelector('#btn-close-drawer')?.addEventListener('click', () => store.setState({ drawerServicoId: null }));
}

function renderToast(msg) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  if (!msg) { container.innerHTML = ''; return; }
  container.innerHTML = `<div class="toast-container">${msg}</div>`;
}

document.addEventListener('DOMContentLoaded', () => {
  initPage();
});
