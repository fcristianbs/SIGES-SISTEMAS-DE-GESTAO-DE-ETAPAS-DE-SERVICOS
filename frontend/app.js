/* ==========================================================================
   SIGES - SISTEMA DE GESTÃO DE ETAPAS DE SERVIÇOS (COSAMPA)
   Front-end SPA com 100% de Paridade Visual e Todos os Gráficos do Gerencial
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

const CONTRATOS = {
  A: 'CT-2024/018 · Dist. Leste',
  B: 'CT-2025/007 · Dist. Sul',
  C: 'CT-2023/031 · Ilum. Pública ZL'
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

const MOCK_SERVICOS = [
  { id: 'SOB-2026-0341', ct: 'A', ob: 'Vila Prudente', tp: 'Rede', st: 1, v: 12400, d: 2, nota: 'NM-0873', data: '11/08', dep: '—', ret: '' },
  { id: 'SOB-2026-0347', ct: 'A', ob: 'Vila Prudente', tp: 'Medidor', st: 1, v: 980, d: 5, nota: 'NM-0879', data: '08/08', dep: '—', ret: '' },
  { id: 'SOB-2026-0352', ct: 'B', ob: 'Jd. Ângela', tp: 'Transformador', st: 1, v: 38200, d: 1, nota: 'NM-0881', data: '12/08', dep: '—', ret: '' },
  { id: 'SOB-2026-0289', ct: 'A', ob: 'Penha', tp: 'Rede', st: 3, v: 45900, d: 1, nota: 'NM-0851', data: '12/08', dep: '—', ret: '' },
  { id: 'SOB-2026-0293', ct: 'B', ob: 'Grajaú', tp: 'Transformador', st: 3, v: 61300, d: 3, nota: 'NM-0854', data: '10/08', dep: '—', ret: '' },
  { id: 'SOB-2026-0269', ct: 'B', ob: 'Parelheiros', tp: 'Rede', st: 5, v: 18700, d: 2, nota: 'NM-0842', data: '11/08', dep: '—', ret: 'Baremo divergente na ati...' },
  { id: 'SOB-2026-0216', ct: 'A', ob: 'Sapopemba', tp: 'Rede', st: 10, v: 33500, d: 7, nota: 'NF-4460', data: '06/08', dep: 'Conciliação', ret: 'Divergência de R$ 1.240 ...' },
  { id: 'SOB-2026-0209', ct: 'B', ob: 'Pirituba', tp: 'Transformador', st: 11, v: 41200, d: 9, nota: 'NF-4447', data: '04/08', dep: 'Conciliação', ret: 'Pago a menor: R$ 38.900' },
  { id: 'SOB-2026-0198', ct: 'A', ob: 'Lapa', tp: 'Rede', st: 12, v: 27600, d: 12, nota: 'NF-4431', data: '01/08', dep: 'Conciliação', ret: 'Em disputa desde 01/08' },
  
  {
    id: 'SOB-2026-0298', ct: 'A', ob: 'Penha', tp: 'Rede', st: 2, v: 21500, d: 9, nota: 'NM-0830', data: '04/08', dep: 'Operação',
    pend: [
      { t: 'Fotos', tr: false, det: '', anx: null },
      { t: 'Materiais', tr: false, det: '', anx: null }
    ]
  },
  {
    id: 'SOB-2026-0301', ct: 'B', ob: 'Capela do Socorro', tp: 'Ramal', st: 2, v: 3400, d: 6, nota: 'NM-0835', data: '07/08', dep: 'Operação',
    pend: [
      { t: 'Documentos', tr: false, det: '', anx: null },
      { t: 'Retorno', tr: false, det: '', anx: null }
    ]
  },
  {
    id: 'SOB-2026-0315', ct: 'C', ob: 'Itaquera', tp: 'Poste', st: 2, v: 7250, d: 3, nota: 'NM-0840', data: '10/08', dep: 'Operação',
    pend: [
      { t: 'Fotos', tr: false, det: '', anx: null }
    ]
  },
  {
    id: 'SOB-2026-0322', ct: 'A', ob: 'Tatuapé', tp: 'Rede', st: 2, v: 5600, d: 4, nota: 'NM-0844', data: '09/08', dep: 'Operação',
    pend: [
      { t: 'Materiais', tr: false, det: '', anx: null },
      { t: 'Outros', tr: true, det: 'Vistoria aprovada', anx: 'Relatorio.pdf' }
    ]
  },
  {
    id: 'SOB-2026-0328', ct: 'B', ob: 'Mooca', tp: 'Ramal', st: 2, v: 4800, d: 8, nota: 'NM-0846', data: '05/08', dep: 'Operação',
    pend: [
      { t: 'Fotos', tr: false, det: '', anx: null },
      { t: 'Documentos', tr: true, det: 'ART quitada', anx: 'ART.pdf' }
    ]
  }
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
    const svcs = JSON.parse(localStorage.getItem('siges_svcs')) || MOCK_SERVICOS.map(s => ({
      ...s,
      bar: s.bar || [
        { cod: '3.1', desc: 'Lançamento de cabo BT', qtd: 1, med: Math.round(s.v * 0.60), pago: null },
        { cod: '3.4', desc: 'Instalação de cruzeta', qtd: 1, med: Math.round(s.v * 0.40), pago: null }
      ]
    }));

    this.state = {
      telaAtualId: document.body.getAttribute('data-page-id') || 'gerencial',
      pinSidebar: true,
      filtros: { periodo: 'mes', contrato: 'todos', tipo: 'todos', area: 'todas', status: 'todos', busca: '' },
      presets: JSON.parse(localStorage.getItem('siges_presets')) || [{ id: 'p1', nome: 'Dist. Leste · 7 dias', filtros: { periodo: '7d', contrato: 'A', tipo: 'todos', area: 'todas', status: 'todos', busca: '' } }],
      modeGestao: 'perfil',
      usuarioGestaoId: 3,
      selecionados: [],
      servicoFocoId: 'SOB-2026-0298',
      drawerServicoId: null,
      toast: null,
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
    localStorage.setItem('siges_presets', JSON.stringify(this.state.presets));
    this.listeners.forEach(l => l(this.state));
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
      if (f.busca) {
        const q = f.busca.toLowerCase();
        if (!`${s.id} ${s.ob} ${s.tp}`.toLowerCase().includes(q)) return false;
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

  store.subscribe(state => renderPageUI(pageId, state));
  renderPageUI(pageId, store.getState());
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

  // FilterBar
  const filterBar = document.getElementById('filterbar-container');
  if (filterBar && pageId !== 'gestao_acessos') {
    filterBar.innerHTML = `
      <div class="filter-bar">
        <select id="f-periodo" class="select-input">
          <option value="mes" ${state.filtros.periodo==='mes'?'selected':''}>Agosto/2026 (mês todo)</option>
          <option value="7d" ${state.filtros.periodo==='7d'?'selected':''}>Últimos 7 dias</option>
        </select>
        <select id="f-contrato" class="select-input">
          <option value="todos" ${state.filtros.contrato==='todos'?'selected':''}>Todos os contratos</option>
          <option value="A" ${state.filtros.contrato==='A'?'selected':''}>CT-2024/018 · Dist. Leste</option>
          <option value="B" ${state.filtros.contrato==='B'?'selected':''}>CT-2025/007 · Dist. Sul</option>
        </select>
        <input id="f-busca" class="text-input" value="${state.filtros.busca}" placeholder="Buscar SOB, obra..." style="width:180px">
      </div>
    `;
    filterBar.querySelector('#f-contrato')?.addEventListener('change', (e) => store.setState({ filtros: { ...state.filtros, contrato: e.target.value } }));
    filterBar.querySelector('#f-busca')?.addEventListener('input', (e) => store.setState({ filtros: { ...state.filtros, busca: e.target.value } }));
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

// --- DASHBOARD GERENCIAL 100% COMPLETO COM TODOS OS GRÁFICOS DO PROTÓTIPO ---
function renderGerencial(svcs, state) {
  const container = document.querySelector('.view-container');
  if (!container) return;

  const totalValor = svcs.reduce((a, s) => a + s.v, 0);
  const estourados = svcs.filter(s => s.d > 5);

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:14px;max-width:1420px">
      <!-- 4 KPI Cards Féis ao Protótipo -->
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Serviços na Esteira</div>
          <div class="kpi-val">${svcs.length}</div>
          <div style="font-size:11.5px;color:#71807a;margin-top:4px">${svcs.length + 3} no total (com finalizados)</div>
        </div>
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Valor na Esteira</div>
          <div class="kpi-val">R$ ${(totalValor/1000).toFixed(1)} mil</div>
          <div style="font-size:11.5px;color:#71807a;margin-top:4px">soma dos serviços ativos</div>
        </div>
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Por Macroetapa</div>
          <div style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin-top:12px;background:#f0f3f2">
            <div style="width:40%;background:#1c5f4b" title="Medição 9"></div>
            <div style="width:25%;background:#b03a28" title="Pendências 6"></div>
            <div style="width:20%;background:#d97706" title="Faturamento 3"></div>
            <div style="width:15%;background:#2563eb" title="Conciliação 3"></div>
          </div>
          <div style="font-size:10.5px;color:#71807a;margin-top:8px">Medição 9 · Pendências 6 · Faturamento 3</div>
        </div>
        <div class="kpi-card">
          <div style="font-size:10.5px;font-weight:600;color:#71807a;text-transform:uppercase">Tempo Médio na Etapa</div>
          <div class="kpi-val">5,2 d</div>
          <div style="font-size:11.5px;color:var(--color-alert);margin-top:4px;font-weight:600">${estourados.length} com SLA estourado</div>
        </div>
      </div>

      <!-- Bloco 1 & Bloco 2: Gráfico de Status e Valor Parado por Macroetapa -->
      <div style="display:grid;grid-template-columns:1.55fr 1fr;gap:14px">
        <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px">
          <div style="display:flex;justify-content:space-between;align-items:baseline">
            <span style="font-size:13px;font-weight:700">Serviços por status</span>
            <span style="font-size:11px;color:#8a9791">${svcs.length} serviços com os filtros atuais</span>
          </div>
          <div style="display:flex;align-items:flex-end;gap:5px;height:158px;margin-top:14px">
            ${Object.keys(STATUS_DEFS).map(stId => {
              const def = STATUS_DEFS[stId];
              const c = svcs.filter(s => s.st === Number(stId)).length;
              const h = Math.min(130, c * 35 + 8);
              return `
                <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%">
                  <span style="font-family:var(--font-mono);font-size:10px;color:#5b6b65">${c}</span>
                  <div style="width:100%;max-width:24px;height:${h}px;background:${def.color};border-radius:4px 4px 0 0" title="0${stId}. ${def.n}"></div>
                  <span style="font-family:var(--font-mono);font-size:9.5px;color:#8a9791;margin-top:4px">0${stId}</span>
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px">
          <span style="font-size:13px;font-weight:700">Valor parado por macroetapa</span>
          <div style="margin-top:14px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:11px">
              <span style="width:86px;font-size:11.5px">Medição</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:85%;height:100%;background:#1c5f4b"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ 279,8 mil</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:11px">
              <span style="width:86px;font-size:11.5px">Pendências</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:35%;height:100%;background:#b03a28"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ 72 mil</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:11px">
              <span style="width:86px;font-size:11.5px">Faturamento</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:50%;height:100%;background:#9333ea"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ 131,8 mil</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px">
              <span style="width:86px;font-size:11.5px">Conciliação</span>
              <div style="flex:1;height:14px;background:#f0f3f2;border-radius:4px;overflow:hidden"><div style="width:30%;height:100%;background:#0891b2"></div></div>
              <span style="font-weight:600;font-family:var(--font-mono);font-size:11.5px">R$ 78,9 mil</span>
            </div>
          </div>
          <div style="margin-top:16px;background:#eaf2ee;border:1px solid #cfe0d8;border-radius:8px;padding:10px 12px;font-size:12px;color:#14483a">
            <b>R$ 79,8 mil</b> aguardando validação do cliente (04)
          </div>
        </div>
      </div>

      <!-- Bloco 3 & Bloco 4: Medido x Faturado & Gargalos -->
      <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:14px">
        <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px">
          <div style="display:flex;justify-content:space-between;align-items:baseline">
            <span style="font-size:13px;font-weight:700">Medido × Faturado no mês</span>
            <span style="font-size:11px;color:#5b6b65">■ Medido ■ Faturado</span>
          </div>
          <div style="display:flex;align-items:flex-end;gap:16px;height:136px;margin-top:14px">
            ${['06/07', '13/07', '20/07', '27/07', '03/08', '10/08'].map(w => `
              <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%">
                <div style="display:flex;align-items:flex-end;gap:3px">
                  <div style="width:15px;height:70px;background:#3f4f49;border-radius:3px 3px 0 0"></div>
                  <div style="width:15px;height:50px;background:var(--ac-primary);border-radius:3px 3px 0 0"></div>
                </div>
                <span style="font-family:var(--font-mono);font-size:10px;color:#8a9791;margin-top:5px">${w}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px">
          <span style="font-size:13px;font-weight:700">Gargalos — tempo médio por etapa</span>
          <div style="margin-top:11px">
            <div style="margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;font-size:11.5px">
                <span><b>12</b> Pgto a Menor — Em Disputa</span>
                <span style="color:var(--color-alert);font-weight:600">12 d <small style="color:#71807a">SLA 15d</small></span>
              </div>
              <div style="height:6px;background:#f0f3f2;border-radius:3px;margin-top:4px"><div style="width:80%;height:100%;background:#9333ea;border-radius:3px"></div></div>
            </div>
            <div style="margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;font-size:11.5px">
                <span><b>11</b> Pgto a Menor — Cobrar Cliente</span>
                <span style="color:var(--color-alert);font-weight:600">9 d <small style="color:#71807a">SLA 7d</small></span>
              </div>
              <div style="height:6px;background:#f0f3f2;border-radius:3px;margin-top:4px"><div style="width:100%;height:100%;background:var(--color-alert);border-radius:3px"></div></div>
            </div>
            <div>
              <div style="display:flex;justify-content:space-between;font-size:11.5px">
                <span><b>08</b> Faturado — Aguard. Conciliação</span>
                <span style="font-weight:600">7 d <small style="color:#71807a">SLA 10d</small></span>
              </div>
              <div style="height:6px;background:#f0f3f2;border-radius:3px;margin-top:4px"><div style="width:70%;height:100%;background:#2563eb;border-radius:3px"></div></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Radar de SLA -->
      <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
        <div style="padding:14px 18px;border-bottom:1px solid var(--border-subtle);font-size:13px;font-weight:700">Radar de SLA — Serviços Estourados</div>
        ${estourados.map(s => {
          const stDef = STATUS_DEFS[s.st];
          return `
            <div class="row-svc" data-id="${s.id}" style="display:grid;grid-template-columns:180px 140px 1fr 90px 120px 80px;gap:10px;align-items:center;padding:10px 18px;border-bottom:1px solid #eef1f0;cursor:pointer">
              <span class="badge-status" style="background:${stDef.bg};color:${stDef.fg}">
                <span class="badge-status-num">0${s.st}</span> ${stDef.n}
              </span>
              <span style="font-family:var(--font-mono);font-weight:600">${s.id}</span>
              <span>${s.ob} (${s.tp})</span>
              <span style="color:var(--color-alert);font-weight:700;font-family:var(--font-mono)">${s.d} dias</span>
              <span style="font-weight:600;font-family:var(--font-mono);text-align:right">R$ ${s.v.toLocaleString('pt-BR')}</span>
              <span style="color:var(--ac-primary);font-weight:600;text-align:right">Abrir →</span>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;

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

  container.innerHTML = `
    <div style="display:flex;gap:14px;align-items:flex-start">
      <div style="flex:1;min-width:0;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left;font-size:10.5px;color:#71807a;font-weight:700">
              <th style="padding:10px 12px;width:28px"><input type="checkbox" id="check-all-med"></th>
              <th style="padding:10px">STATUS</th>
              <th style="padding:10px">SERVIÇO</th>
              <th style="padding:10px">NOTA</th>
              <th style="padding:10px">DATA</th>
              <th style="padding:10px">DEP.</th>
              <th style="padding:10px;text-align:right">VALOR</th>
              <th style="padding:10px">RETORNO</th>
              <th style="padding:10px">SLA</th>
            </tr>
          </thead>
          <tbody>
            ${svcs.map(s => {
              const def = STATUS_DEFS[s.st];
              const isSel = state.selecionados.includes(s.id);
              const isAlert = s.d > 5;
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
                  <td style="padding:10px;font-family:var(--font-mono)">${s.nota || '—'}</td>
                  <td style="padding:10px;font-family:var(--font-mono)">${s.data || '—'}</td>
                  <td style="padding:10px">${s.dep || '—'}</td>
                  <td style="padding:10px;text-align:right;font-weight:600;font-family:var(--font-mono)">R$ ${s.v.toLocaleString('pt-BR')}</td>
                  <td style="padding:10px;font-size:11px;color:#71807a">${s.ret || '—'}</td>
                  <td style="padding:10px">
                    <span class="${isAlert ? 'badge-sla-alert' : 'badge-sla-ok'}">${s.d} d</span>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
        
        <div class="table-footer">
          <span><b>${state.selecionados.length}</b> selecionado(s)</span>
          <span><b>${svcs.length}</b> serviço(s) na fila</span>
        </div>
      </div>

      <div style="width:280px;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
          <h4 style="margin:0;font-size:13px;font-weight:700">TRATATIVAS</h4>
          <span style="background:#3c4a45;color:#fff;font-size:10px;font-weight:700;border-radius:12px;padding:2px 8px;font-family:var(--font-mono)">${state.selecionados.length} sel.</span>
        </div>

        <div style="margin-bottom:18px">
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Alterar status</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:8px">Individual ou em massa — ex.: 01 → 07.</div>
          <select id="select-bulk-status" class="select-input" style="width:100%;margin-bottom:8px">
            <option value="">Novo status...</option>
            ${Object.keys(STATUS_DEFS).map(k => `<option value="${k}">0${k}. ${STATUS_DEFS[k].n}</option>`).join('')}
          </select>
          <button id="btn-apply-bulk" class="btn-primary" style="width:100%">Aplicar aos selecionados</button>
        </div>

        <div style="margin-bottom:18px;border-top:1px solid var(--border-subtle);padding-top:14px">
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Baixar / Tramitar</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:8px">Avança para a próxima etapa sugerida (ex.: 01 → 03).</div>
          <button id="btn-tramitar-bulk" class="btn-secondary" style="width:100%">Tramitar selecionados</button>
        </div>

        <div style="border-top:1px solid var(--border-subtle);padding-top:14px">
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Grupo de pendências</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:10px">Envia os selecionados para 02. Pendências com os tipos marcados.</div>
          
          <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:12px">
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Documentos"> Documentos</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Fotos"> Fotos</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Materiais"> Materiais</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Retorno"> Retorno</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check" value="Outros"> Outros</label>
          </div>

          <button id="btn-enviar-pend" style="width:100%;background:#fdf3e3;color:#8a5a0d;border:1px solid #ecd9b7;border-radius:8px;padding:8px;font-size:12px;font-weight:600">Enviar para 02. Pendências</button>
        </div>
      </div>
    </div>
  `;

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

  const foco = svcs.find(s => s.id === state.servicoFocoId) || svcs[0];

  container.innerHTML = `
    <div style="display:flex;gap:14px;align-items:flex-start">
      <div style="flex:1;min-width:0;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left;font-size:10.5px;color:#71807a;font-weight:700">
              <th style="padding:10px">STATUS</th>
              <th style="padding:10px">SERVIÇO</th>
              <th style="padding:10px">PENDÊNCIAS</th>
              <th style="padding:10px">DATA</th>
              <th style="padding:10px">SLA</th>
              <th style="padding:10px;text-align:right">VALOR</th>
            </tr>
          </thead>
          <tbody>
            ${svcs.map(s => {
              const def = STATUS_DEFS[s.st];
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
                  <td style="padding:10px">
                    <div style="display:flex;flex-wrap:wrap;gap:4px">
                      ${(s.pend || []).map(p => `
                        <span style="padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;background:${p.tr ? '#d1fae5' : '#fee2e2'};color:${p.tr ? '#065f46' : '#991b1b'}">
                          ${p.tr ? '✓' : '✕'} ${p.t}
                        </span>
                      `).join('')}
                    </div>
                  </td>
                  <td style="padding:10px;font-family:var(--font-mono)">${s.data || '—'}</td>
                  <td style="padding:10px">
                    <span class="badge-sla-alert">${s.d} d</span>
                  </td>
                  <td style="padding:10px;text-align:right;font-weight:600;font-family:var(--font-mono)">R$ ${s.v.toLocaleString('pt-BR')}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
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

          <div style="display:flex;justify-content:space-between;font-size:11px;color:#71807a;margin:10px 0 4px">
            <span>Progresso:</span>
            <span><b>${(foco.pend || []).filter(p=>p.tr).length} de ${(foco.pend || []).length} tratada(s)</b></span>
          </div>

          <div style="margin-top:10px">
            ${(foco.pend || []).map((p, idx) => `
              <div class="card-pendencia">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                  <div style="display:flex;align-items:center;gap:8px">
                    <button class="btn-check-pend" data-idx="${idx}" style="width:24px;height:24px;border-radius:6px;border:none;background:${p.tr ? '#d1fae5' : '#fee2e2'};color:${p.tr ? '#065f46' : '#991b1b'};font-weight:700;cursor:pointer">
                      ${p.tr ? '✓' : '✕'}
                    </button>
                    <span style="font-size:13px;font-weight:700">${p.t}</span>
                  </div>
                  <span class="badge-pend-status ${p.tr ? 'badge-pend-tratado' : 'badge-pend-pendente'}">
                    ${p.tr ? 'TRATADO' : 'PENDENTE'}
                  </span>
                </div>

                <input class="text-input input-det-pend" data-idx="${idx}" value="${p.det || ''}" placeholder="Detalhamento da tratativa..." style="width:100%;font-size:11.5px">

                <div style="display:flex;align-items:center;gap:8px">
                  <button class="btn-anexo btn-trigger-anexo" data-idx="${idx}">+ Anexo</button>
                  <input type="file" class="file-input-hidden" data-idx="${idx}" style="display:none">
                  ${p.anx ? `<span style="font-size:10.5px;color:var(--ac-primary);font-weight:600">📎 ${p.anx}</span>` : ''}
                </div>
              </div>
            `).join('')}
          </div>

          <div style="margin-top:16px;background:#f7f9f8;border-radius:8px;padding:12px;font-size:11.5px;color:#5b6b65;line-height:1.45;border:1px solid var(--border-subtle)">
            Ao tratar <b>todas</b> as pendências, o serviço retorna automaticamente para <b>01. Aguardando Conferência</b>.
          </div>
        ` : `<div style="color:#71807a">Selecione um serviço para tratar as pendências.</div>`}
      </div>
    </div>
  `;

  container.querySelectorAll('.row-foco').forEach(row => {
    row.addEventListener('click', () => {
      const id = row.getAttribute('data-id');
      store.setState({ servicoFocoId: id });
    });
  });

  container.querySelector('#btn-open-drawer-foco')?.addEventListener('click', () => {
    if (foco) store.setState({ drawerServicoId: foco.id });
  });

  container.querySelectorAll('.btn-check-pend').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = Number(btn.getAttribute('data-idx'));
      if (foco) store.tratarPendenciaItem(foco.id, idx);
    });
  });

  container.querySelectorAll('.input-det-pend').forEach(input => {
    input.addEventListener('change', (e) => {
      const idx = Number(input.getAttribute('data-idx'));
      if (foco) store.tratarPendenciaItem(foco.id, idx, e.target.value);
    });
  });

  container.querySelectorAll('.btn-trigger-anexo').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = btn.getAttribute('data-idx');
      const fileInput = container.querySelector(`.file-input-hidden[data-idx="${idx}"]`);
      if (fileInput) fileInput.click();
    });
  });

  container.querySelectorAll('.file-input-hidden').forEach(fileInput => {
    fileInput.addEventListener('change', (e) => {
      const idx = Number(fileInput.getAttribute('data-idx'));
      if (e.target.files && e.target.files[0] && foco) {
        const fileObj = e.target.files[0];
        store.tratarPendenciaItem(foco.id, idx, null, fileObj.name);
        store.notifyToast(`Anexo "${fileObj.name}" adicionado à pendência!`);
      }
    });
  });
}

function renderGenericScreen(pageId, svcs) {
  const container = document.querySelector('.view-container');
  if (!container) return;
  const info = TELAS_DEF.find(t => t.id === pageId) || { label: pageId };

  container.innerHTML = `
    <div style="background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:20px">
      <h3 style="margin:0 0 10px">${info.label}</h3>
      <p style="color:#71807a">Exibindo serviços ativos nesta fila de trabalho:</p>
      <table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:14px">
        <thead>
          <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left">
            <th style="padding:10px">Status</th>
            <th style="padding:10px">Serviço</th>
            <th style="padding:10px">Nota</th>
            <th style="padding:10px;text-align:right">Valor</th>
          </tr>
        </thead>
        <tbody>
          ${svcs.map(s => {
            const def = STATUS_DEFS[s.st];
            return `
              <tr class="row-svc" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;cursor:pointer">
                <td style="padding:10px">
                  <span class="badge-status" style="background:${def.bg};color:${def.fg}">
                    <span class="badge-status-num">0${s.st}</span> ${def.n}
                  </span>
                </td>
                <td style="padding:10px"><b>${s.id}</b> — ${s.ob} (${s.tp})</td>
                <td style="padding:10px">${s.nota || '—'}</td>
                <td style="padding:10px;text-align:right;font-weight:600">R$ ${s.v.toLocaleString('pt-BR')}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;

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
          <h3 style="margin:0">${s.id} — R$ ${s.v.toLocaleString('pt-BR')}</h3>
          <span style="font-size:11.5px;color:#71807a">${s.ob} (${s.tp})</span>
        </div>
        <button id="btn-close-drawer" style="background:none;border:none;font-size:22px;cursor:pointer">×</button>
      </div>
      <div style="padding:20px;flex:1;overflow-y:auto;font-size:12px">
        <p><b>Contrato:</b> ${CONTRATOS[s.ct] || s.ct}</p>
        <p><b>Status Atual:</b> 0${s.st}. ${STATUS_DEFS[s.st]?.n}</p>

        <h4 style="margin:16px 0 8px">Itens de Baremo Medidos:</h4>
        <table style="width:100%;border-collapse:collapse;font-size:11.5px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left">
              <th style="padding:6px">Cód</th>
              <th style="padding:6px">Descrição</th>
              <th style="padding:6px;text-align:right">Valor</th>
            </tr>
          </thead>
          <tbody>
            ${(s.bar || []).map(b => `
              <tr style="border-bottom:1px solid #eef1f0">
                <td style="padding:6px;font-family:var(--font-mono)">${b.cod}</td>
                <td style="padding:6px">${b.desc}</td>
                <td style="padding:6px;text-align:right;font-family:var(--font-mono);font-weight:600">R$ ${b.med.toLocaleString('pt-BR')}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
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
