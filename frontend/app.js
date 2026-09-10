/* ==========================================================================
   SIGES - SISTEMA DE GESTÃO DE ETAPAS DE SERVIÇOS (COSAMPA)
   Front-end SPA com Paginação de 10 itens por página e Conexão Real MySQL
   ========================================================================== */

const STATUS_DEFS = {
  1: { n: 'Aguardando Conferência', a: 'Fechamento', m: 'med', sla: 3, color: '#1c5f4b', bg: '#eaf2ee', fg: '#14483a' },
  2: { n: 'Pendências Operacionais Cosampa', a: 'Operação', m: 'pen', sla: 5, color: '#b03a28', bg: '#fdf2f0', fg: '#b03a28' },
  3: { n: 'Aguard. Envio p/ Validação', a: 'Fechamento', m: 'med', sla: 2, color: '#2b6e58', bg: '#eef6f3', fg: '#1c5f4b' },
  4: { n: 'Pendências Distribuidora', a: 'Fechamento', m: 'pen', sla: 5, color: '#d97706', bg: '#fef3c7', fg: '#92400e' },
  5: { n: 'Aguard. Validação do Cliente', a: 'Faturamento', m: 'fat', sla: 7, color: '#d97706', bg: '#fef3c7', fg: '#92400e' },
  6: { n: 'Rejeitado na Validação (Fech.)', a: 'Fechamento', m: 'med', sla: 3, color: '#dc2626', bg: '#fee2e2', fg: '#991b1b' },
  7: { n: 'Rejeitado na Validação (Oper.)', a: 'Operação', m: 'pen', sla: 5, color: '#dc2626', bg: '#fee2e2', fg: '#991b1b' },
  8: { n: 'Validado — Aguard. Autorização', a: 'Faturamento', m: 'fat', sla: 3, color: '#059669', bg: '#d1fae5', fg: '#065f46' },
  9: { n: 'Faturado — Aguard. Conciliação', a: 'Faturamento', m: 'con', sla: 10, color: '#2563eb', bg: '#dbeafe', fg: '#1e40af' },
  10: { n: 'Análise de Conciliação', a: 'Faturamento', m: 'con', sla: 5, color: '#4f46e5', bg: '#e0e7ff', fg: '#3730a3' },
  11: { n: 'Conciliado c/ Divergências', a: 'Fechamento', m: 'med', sla: 4, color: '#ea580c', bg: '#ffedd5', fg: '#9a3412' },
  12: { n: 'Pgto a Menor — Cobrar Cliente', a: 'Fechamento', m: 'med', sla: 7, color: '#c026d3', bg: '#fae8ff', fg: '#86198f' },
  13: { n: 'Pgto a Menor — Em Disputa', a: 'Fechamento', m: 'med', sla: 15, color: '#9333ea', bg: '#f3e8ff', fg: '#6b21a8' },
  14: { n: 'Faturado Total', a: 'Geral', m: 'fin', sla: null, color: '#16a34a', bg: '#dcfce7', fg: '#15803d' },
  15: { n: 'Faturado a Maior', a: 'Geral', m: 'fin', sla: null, color: '#0891b2', bg: '#cffafe', fg: '#155e75' }
};

const DICIONARIO_COLUNAS = {
  sel: 'Checkbox (Seleção)',
  st: 'Status',
  svc_data: 'Serviço e Data',
  id: 'Número do Serviço',
  data: 'Data de Execução',
  pep_tdc: 'PEP Obra / TDC',
  cli_ct: 'Cliente / Contrato',
  origem: 'Origem do Sistema',
  v: 'Valor',
  ret: 'Retorno / Pendências',
  ob: 'Obra / Bairro / Localidade',
  tp: 'Tipo de Serviço',
  d: 'SLA (Dias)',
  nota: 'Nota de Medição',
  dep: 'Departamento',
  supervisor: 'Supervisor',
  equipe: 'Equipe',
  obs: 'Observações'
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
      servicos: [],
      perfisTela: [],
      perfilTelaAtivoId: null,
      wizardImportacao: {
        aberto: false,
        passo: 1,
        arquivoTempId: null,
        abasDisponiveis: [],
        abaSelecionada: "",
        linhasPrevisualizacao: [],
        colunasPlanilha: [],
        linhaCabecalhoIndex: 0,
        mapeamentoAtivo: {},
        erro: null,
        carregando: false,
        sucesso: null,
        faltamMapeamentos: []
      }
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

  async carregarPerfisTelaAPI() {
    try {
      if (!authService.usuarioLogado) return;
      const uid = authService.usuarioLogado.id;
      const res = await fetch(`/api/perfis_tela?user_id=${uid}`);
      if (res.ok) {
        const perfis = await res.json();
        const pAtivo = localStorage.getItem('siges_perfil_tela_ativo');
        let ativoId = pAtivo ? parseInt(pAtivo) : (perfis.length > 0 ? perfis[0].id : null);
        // Fallback caso o ID salvo não exista mais
        if (!perfis.find(p => p.id === ativoId) && perfis.length > 0) {
          ativoId = perfis[0].id;
        }
        this.setState({ perfisTela: perfis, perfilTelaAtivoId: ativoId });
      }
    } catch (e) {
      console.warn('Erro ao buscar API /api/perfis_tela:', e);
    }
  }

  notifyToast(msg) {
    this.setState({ toast: msg });
    setTimeout(() => {
      if (this.state.toast === msg) this.setState({ toast: null });
    }, 4000);
  }

  getServicosFiltrados() {
    const f = this.state.filtros;
    return this.state.servicos.filter(s => {
      if (f.contrato !== 'todos' && s.ct !== f.contrato) return false;
      if (f.tipo !== 'todos' && s.tp !== f.tipo) return false;
      if (f.status && f.status !== 'todos' && s.st !== Number(f.status)) return false;
      if (f.supervisor && f.supervisor !== 'todos' && s.supervisor !== f.supervisor) return false;
      if (f.busca) {
        const q = f.busca.toLowerCase();
        if (!`${s.id} ${s.ob} ${s.tp} ${s.ct} ${s.pep||''} ${s.tdc||''} ${s.supervisor||''} ${s.equipe||''}`.toLowerCase().includes(q)) return false;
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
  
  // Carrega perfis primeiro, depois os serviços
  store.carregarPerfisTelaAPI().then(() => {
    store.carregarServicosAPI();
  });
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

function renderToolbarPerfis(state) {
  if (!state.perfisTela || state.perfisTela.length === 0) return '';
  const ativo = state.perfisTela.find(p => p.id === state.perfilTelaAtivoId) || state.perfisTela[0];
  
  const colunasOptions = Object.keys(DICIONARIO_COLUNAS).map(k => {
    const isChecked = ativo.colunas_visiveis.includes(k) ? 'checked' : '';
    return `<label style="display:flex;align-items:center;gap:6px;font-size:11.5px;padding:4px"><input type="checkbox" class="cb-coluna" value="${k}" ${isChecked}> ${DICIONARIO_COLUNAS[k]}</label>`;
  }).join('');

  return `
    <div style="background:#fff;border-top:1px solid #eef1f0;padding:8px 14px;display:flex;align-items:center;gap:12px;font-size:12px">
      <div style="font-weight:600;color:#5b6b65">Perfil de Tabela:</div>
      <select id="sel-perfil-tela" style="padding:4px 8px;border:1px solid #d7dedb;border-radius:4px;font-size:11.5px">
        ${state.perfisTela.map(p => `<option value="${p.id}" ${p.id === ativo.id ? 'selected' : ''}>${p.tipo === 'global' ? '🌍' : '🔒'} ${p.nome}</option>`).join('')}
      </select>
      
      <div style="position:relative">
        <button id="btn-toggle-colunas" style="padding:4px 10px;border:1px solid #d7dedb;background:#f7f9f8;border-radius:4px;cursor:pointer;font-size:11.5px">Configurar Colunas ⚙️</button>
        <div id="dropdown-colunas" style="display:none;position:absolute;top:100%;left:0;margin-top:4px;background:#fff;border:1px solid #d7dedb;border-radius:6px;padding:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);z-index:100;width:220px;max-height:300px;overflow-y:auto">
          <div style="font-weight:600;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #eef1f0">Colunas Visíveis</div>
          ${colunasOptions}
          <div style="margin-top:8px;display:flex;gap:4px">
             <button id="btn-save-perfil" class="btn-primary" style="flex:1;padding:4px;font-size:11px">Salvar Alterações</button>
             <button id="btn-new-perfil" class="btn-secondary" style="flex:1;padding:4px;font-size:11px">Salvar como Novo</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function bindToolbarEvents(container, state) {
  const selPerfil = container.querySelector('#sel-perfil-tela');
  if (selPerfil) {
    selPerfil.addEventListener('change', (e) => {
      const id = parseInt(e.target.value);
      localStorage.setItem('siges_perfil_tela_ativo', id);
      store.setState({ perfilTelaAtivoId: id });
    });
  }

  const btnToggle = container.querySelector('#btn-toggle-colunas');
  const dropColunas = container.querySelector('#dropdown-colunas');
  if (btnToggle && dropColunas) {
    btnToggle.addEventListener('click', () => {
      dropColunas.style.display = dropColunas.style.display === 'none' ? 'block' : 'none';
    });
  }

  container.querySelector('#btn-save-perfil')?.addEventListener('click', async () => {
    const ativo = state.perfisTela.find(p => p.id === state.perfilTelaAtivoId);
    if (!ativo) return;
    
    const checkboxes = Array.from(container.querySelectorAll('.cb-coluna:checked'));
    const selecionadas = checkboxes.map(cb => cb.value);

    try {
      const res = await fetch(`/api/perfis_tela/${ativo.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ colunas_visiveis: selecionadas, user_id: authService.usuarioLogado.id })
      });
      const data = await res.json();
      if (res.ok) {
        store.notifyToast('Perfil atualizado com sucesso!');
        store.carregarPerfisTelaAPI();
      } else {
        alert(data.erro || 'Erro ao atualizar');
      }
    } catch (e) {
      alert('Erro na requisição: ' + e);
    }
  });

  container.querySelector('#btn-new-perfil')?.addEventListener('click', async () => {
    const nome = prompt("Nome do novo perfil privado:");
    if (!nome) return;

    const checkboxes = Array.from(container.querySelectorAll('.cb-coluna:checked'));
    const selecionadas = checkboxes.map(cb => cb.value);

    try {
      const res = await fetch(`/api/perfis_tela`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: nome,
          colunas_visiveis: selecionadas,
          criado_por_id: authService.usuarioLogado.id,
          tipo: 'privado'
        })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('siges_perfil_tela_ativo', data.id);
        store.notifyToast('Novo perfil criado!');
        store.carregarPerfisTelaAPI();
      }
    } catch (e) {
      alert('Erro na requisição: ' + e);
    }
  });
}

function renderDynamicTableHeaders(state) {
  if (!state.perfisTela || state.perfisTela.length === 0) return '';
  const ativo = state.perfisTela.find(p => p.id === state.perfilTelaAtivoId) || state.perfisTela[0];
  
  return ativo.colunas_visiveis.map(colKey => {
    if (colKey === 'sel') {
      const allSelected = state.servicos.length > 0 && state.selecionados.length === state.servicos.length;
      return `<th style="padding:10px 12px;width:28px"><input type="checkbox" id="check-all-dynamic" ${allSelected ? 'checked' : ''}></th>`;
    }
    const label = DICIONARIO_COLUNAS[colKey] || colKey;
    const align = (colKey === 'v') ? 'right' : 'left';
    return `<th style="padding:10px;text-align:${align}">${label.toUpperCase()}</th>`;
  }).join('');
}

function renderDynamicTableRow(s, state, isIrma = false) {
  if (!state.perfisTela || state.perfisTela.length === 0) return '';
  const ativo = state.perfisTela.find(p => p.id === state.perfilTelaAtivoId) || state.perfisTela[0];
  const def = STATUS_DEFS[s.st] || STATUS_DEFS[1];
  const isSel = state.selecionados.includes(s.id);
  
  return ativo.colunas_visiveis.map(colKey => {
    if (colKey === 'sel') return `<td style="padding:10px 12px" onclick="event.stopPropagation()"><input type="checkbox" class="check-svc" data-id="${s.id}" ${isSel ? 'checked' : ''}></td>`;
    if (colKey === 'st') return `<td style="padding:10px"><span class="badge-status" style="background:${def.bg};color:${def.fg}"><span class="badge-status-num">0${s.st}</span> ${def.n}</span></td>`;
    if (colKey === 'svc_data') return `<td style="padding:10px"><b>${s.id}</b> ${isIrma ? `<span style="background:#e0f2fe;color:#0369a1;font-size:9.5px;padding:2px 5px;border-radius:4px;font-weight:700">SOB Irmã</span>` : ''}<br><small style="color:#71807a">${s.tp} · <b>${s.data || '—'}</b></small></td>`;
    if (colKey === 'id') return `<td style="padding:10px"><b>${s.id}</b></td>`;
    if (colKey === 'data') return `<td style="padding:10px">${s.data || '—'}</td>`;
    if (colKey === 'pep_tdc') return `<td style="padding:10px;font-family:var(--font-mono);font-size:11px"><b>${s.pep||'—'}</b><br><small style="color:#71807a">${s.tdc||'—'}</small></td>`;
    if (colKey === 'cli_ct') return `<td style="padding:10px;font-size:11px"><b>${s.cliente || '—'}</b><br><small style="font-weight:600;color:#5b6b65">${s.ct}</small></td>`;
    if (colKey === 'origem') return `<td style="padding:10px;font-family:var(--font-mono);font-size:11px">${s.origem || 'PDA'}</td>`;
    if (colKey === 'v') return `<td style="padding:10px;text-align:right;font-weight:600;font-family:var(--font-mono)">R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>`;
    if (colKey === 'ret') return `<td style="padding:10px;font-size:11px;color:#71807a">${s.ret || '—'}</td>`;
    if (colKey === 'ob') return `<td style="padding:10px"><b>${s.ob}</b></td>`;
    if (colKey === 'tp') return `<td style="padding:10px">${s.tp}</td>`;
    if (colKey === 'd') return `<td style="padding:10px;text-align:center">${s.d}</td>`;
    if (colKey === 'nota') return `<td style="padding:10px">${s.nota}</td>`;
    if (colKey === 'dep') return `<td style="padding:10px">${s.dep}</td>`;
    if (colKey === 'supervisor') return `<td style="padding:10px">${s.supervisor || '—'}</td>`;
    if (colKey === 'equipe') return `<td style="padding:10px">${s.equipe || '—'}</td>`;
    if (colKey === 'obs') return `<td style="padding:10px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${s.obs_servico||''}">${s.obs_servico || '—'}</td>`;
    return `<td style="padding:10px">${s[colKey] || '—'}</td>`;
  }).join('');
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
          ${['medicao', 'pendencias', 'gerencial'].includes(pageId) ? `
            <button id="btn-abrir-importacao" class="btn-primary" style="padding:6px 12px;display:flex;align-items:center;gap:6px">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"></path></svg>
              Importar Planilha
            </button>
          ` : ''}
          <div style="text-align:right">
            <div style="font-size:12px;font-weight:700">${user.nome}</div>
            <div style="font-size:10.5px;color:#71807a">Perfil: <b>${perfilAtivo.nome}</b></div>
          </div>
          <button id="btn-logout" class="btn-secondary" style="font-size:11px;padding:5px 10px">Sair</button>
        </div>
      </div>
    `;
    header.querySelector('#btn-logout')?.addEventListener('click', () => authService.logout());
    
    header.querySelector('#btn-abrir-importacao')?.addEventListener('click', () => {
      store.setState({
        wizardImportacao: {
          ...store.getState().wizardImportacao,
          aberto: true,
          passo: 1,
          arquivoTempId: null,
          abasDisponiveis: [],
          abaSelecionada: "",
          linhasPrevisualizacao: [],
          colunasPlanilha: [],
          linhaCabecalhoIndex: 0,
          mapeamentoAtivo: {},
          erro: null,
          sucesso: null,
          faltamMapeamentos: []
        }
      });
    });
  }

  // FilterBar Dinâmica
  const filterBar = document.getElementById('filterbar-container');
  if (filterBar && pageId !== 'gestao_acessos') {
    const contratosUnicos = Array.from(new Set(state.servicos.map(s => s.ct))).filter(Boolean);
    const tiposUnicos = Array.from(new Set(state.servicos.map(s => s.tp))).filter(Boolean);
    const supervisoresUnicos = Array.from(new Set(state.servicos.map(s => s.supervisor))).filter(Boolean);

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
        <select id="f-supervisor" class="select-input" title="Filtro Hierárquico de Supervisor (RN-05)">
          <option value="todos" ${state.filtros.supervisor==='todos'?'selected':''}>Supervisores (RN-05)</option>
          ${supervisoresUnicos.map(sup => `<option value="${sup}" ${state.filtros.supervisor===sup?'selected':''}>👤 ${sup}</option>`).join('')}
        </select>
        <input id="f-busca" class="text-input" value="${state.filtros.busca}" placeholder="Buscar SOB, PEP, TDC, obra..." style="width:200px">
      </div>
      
      <!-- Toolbar Perfis de Tela (CDU V4) -->
      ${renderToolbarPerfis(state)}
      
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
    filterBar.querySelector('#f-supervisor')?.addEventListener('change', (e) => {
      store.setState({ filtros: { ...store.getState().filtros, supervisor: e.target.value }, paginaAtual: 1 });
    });
    filterBar.querySelector('#f-busca')?.addEventListener('input', (e) => {
      store.setState({ filtros: { ...store.getState().filtros, busca: e.target.value }, paginaAtual: 1 });
    });
    
    bindToolbarEvents(filterBar, state);
  }

  // Renderização da Tela
  if (pageId === 'gerencial') renderGerencial(servicosFiltrados, state);
  else if (pageId === 'medicao') renderMedicao(servicosFiltrados, state);
  else if (pageId === 'pendencias') renderPendencias(servicosFiltrados.filter(s => [2, 4, 6, 7].includes(s.st)), state);
  else if (pageId === 'gestao_acessos') renderGestaoAcessos();
  else renderGenericScreen(pageId, servicosFiltrados);

  renderDrawer(state);
  renderToast(state.toast);
  renderWizardImportacao(state);
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
        <!-- Barra de Ações Rápidas em Lote -->
        <div style="padding:10px 14px;background:#f8faf9;border-bottom:1px solid var(--border-subtle);display:flex;align-items:center;justify-content:space-between">
          <span style="font-size:12px;font-weight:700;color:#1c5f4b">Ações de Medição & Validação (CDU-01 / CDU-02 / CDU-06)</span>
          <div style="display:flex;gap:8px">
            <button id="btn-modal-cdu02" class="btn-primary" style="font-size:11px;padding:5px 10px">🚀 Enviar Lote p/ Validação (CDU-02)</button>
            <button id="btn-modal-cdu06" class="btn-secondary" style="font-size:11px;padding:5px 10px">📥 Importar Rejeições Cliente (CDU-06)</button>
          </div>
        </div>

        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f7f9f8;border-bottom:1px solid var(--border-subtle);text-align:left;font-size:10.5px;color:#71807a;font-weight:700">
              ${renderDynamicTableHeaders(state)}
            </tr>
          </thead>
          <tbody>
            ${pagItens.map((s, idx) => {
              const isIrma = idx > 0 && pagItens[idx-1].ct === s.ct;
              return `
                <tr class="row-svc" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;background:${state.selecionados.includes(s.id) ? '#eaf2ee' : '#fff'};cursor:pointer">
                  ${renderDynamicTableRow(s, state, isIrma)}
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
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Pendência Cosampa (Status 02)</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:10px">Selecione os itens e envie para a Operação.</div>
          
          <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:12px">
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check-cosampa" value="Fotos (S/ Evidência, Baixa Qualidade)"> Fotos (S/ Evidência, Baixa Qualidade)</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check-cosampa" value="Materiais (Incorretos, Sobras)"> Materiais (Incorretos, Sobras)</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check-cosampa" value="Documentação (Sem croqui, croqui incorreto)"> Documentação (S/ Croqui, Croqui Errado)</label>
          </div>
          <button id="btn-enviar-pend-cosampa" style="width:100%;background:#fdf3e3;color:#8a5a0d;border:1px solid #ecd9b7;border-radius:8px;padding:8px;font-size:11px;font-weight:600;margin-bottom:14px">Gerar Pendência Cosampa (02)</button>
        </div>

        <div style="border-top:1px solid var(--border-subtle);padding-top:14px">
          <div style="font-weight:700;font-size:12px;margin-bottom:2px">Pendência Distribuidora (Status 04)</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:10px">Selecione os itens e bloqueie a SOB.</div>
          
          <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:12px">
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check-dist" value="Vozes não cadastradas no Contrato"> Vozes não cadastradas</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check-dist" value="Serviço não despachado para Cosampa"> Serviço não despachado</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" class="gp-check-dist" value="Ordem já faturada"> Ordem já faturada</label>
          </div>
          <button id="btn-enviar-pend-distribuidora" style="width:100%;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;border-radius:8px;padding:8px;font-size:11px;font-weight:600">Gerar Pend. Distribuidora (04)</button>
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

  // Modal CDU-02: Enviar Lote para Validação do Cliente
  container.querySelector('#btn-modal-cdu02')?.addEventListener('click', async () => {
    if (state.selecionados.length === 0) return alert('Selecione pelo menos 1 serviço para enviar em lote.');
    const sistemaFat = prompt('Informe o Sistema de Faturamento (ex: Eorder, Synergia, SacBt):', 'Eorder');
    if (!sistemaFat) return;
    const mesInicial = prompt('Informe o Mês de Medição Inicial (OBRIGATÓRIO formatado como MM/AAAA):', '08/2026');
    if (!mesInicial) return alert('O Mês de Medição Inicial (MM/AAAA) é obrigatório (CDU-02).');

    try {
      const res = await fetch('/api/servicos/lote/enviar-validacao', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          servico_ids: state.selecionados,
          sistema_faturamento: sistemaFat,
          mes_medicao_inicial: mesInicial,
          usuario_nome: 'Analista Fechamento'
        })
      });
      const data = await res.json();
      if (res.ok && data.status === 'sucesso') {
        const novos = store.getState().servicos.map(s => state.selecionados.includes(s.id) ? { ...s, st: 5, sistema_faturamento: sistemaFat, mes_medicao_inicial: mesInicial } : s);
        store.setState({ servicos: novos, selecionados: [] });
        store.notifyToast(`CDU-02: ${data.tramitados} serviço(s) enviados para 05. Aguardando Validação do Cliente (Mês: ${mesInicial})!`);
      } else {
        alert(data.mensagem || 'Falha ao enviar lote.');
      }
    } catch (e) {
      alert('Erro na requisição: ' + e);
    }
  });

  // Modal CDU-06: Importar Rejeições do Cliente com Roteamento Padrão para Status 06
  container.querySelector('#btn-modal-cdu06')?.addEventListener('click', async () => {
    const rawIds = prompt('Digite o ID das SOBs rejeitadas pelo cliente separadas por vírgula (ex: SOB-300001525, SOB-300001608):');
    if (!rawIds) return;
    const arr = rawIds.split(',').map(x => x.trim()).filter(Boolean);
    if (arr.length === 0) return;

    const destinoInput = prompt('Informe o destino da rejeição (digite "operacao" para Status 07 ou DEIXE EM BRANCO para aplicar a RN de Roteamento Padrão -> Status 06. Fechamento):', '');

    try {
      const rejeicoesPayload = arr.map(id => ({ id, motivo: 'Rejeição importada do cliente', destino: destinoInput }));
      const res = await fetch('/api/servicos/lote/importar-rejeicoes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rejeicoes: rejeicoesPayload, usuario_nome: 'Analista Fechamento' })
      });
      const data = await res.json();
      if (res.ok && data.status === 'sucesso') {
        const targetSt = destinoInput.toLowerCase() === 'operacao' ? 7 : 6;
        const novos = store.getState().servicos.map(s => arr.includes(s.id) ? { ...s, st: targetSt } : s);
        store.setState({ servicos: novos, selecionados: [] });
        store.notifyToast(`CDU-06: ${data.processados} rejeição(ões) processada(s) com Roteamento Padrão para Status 0${targetSt}!`);
      } else {
        alert(data.mensagem || 'Falha ao importar rejeições.');
      }
    } catch (e) {
      alert('Erro na requisição: ' + e);
    }
  });

  container.querySelector('#btn-apply-bulk')?.addEventListener('click', () => {
    const st = container.querySelector('#select-bulk-status').value;
    if (!st || state.selecionados.length === 0) return alert('Selecione serviços e um novo status.');
    const novos = state.servicos.map(s => state.selecionados.includes(s.id) ? { ...s, st: Number(st) } : s);
    store.setState({ servicos: novos, selecionados: [] });
    store.notifyToast(`Status alterado para ${state.selecionados.length} serviço(s)!`);
  });

  container.querySelector('#btn-enviar-pend-cosampa')?.addEventListener('click', () => {
    if (state.selecionados.length === 0) return alert('Selecione serviços para gerar pendência.');
    const gps = Array.from(container.querySelectorAll('.gp-check-cosampa:checked')).map(c => c.value);
    const pItems = (gps.length ? gps : ['Geral Cosampa']).map(t => ({ t, tr: false, det: '', anx: null }));

    const novos = state.servicos.map(s => {
      if (state.selecionados.includes(s.id)) {
        return { ...s, st: 2, pend: pItems };
      }
      return s;
    });

    store.setState({ servicos: novos, selecionados: [] });
    store.notifyToast(`${state.selecionados.length} serviço(s) enviado(s) para 02. Pendências Operacionais Cosampa!`);
  });

  container.querySelector('#btn-enviar-pend-distribuidora')?.addEventListener('click', () => {
    if (state.selecionados.length === 0) return alert('Selecione serviços para gerar pendência.');
    const gps = Array.from(container.querySelectorAll('.gp-check-dist:checked')).map(c => c.value);
    const pItems = (gps.length ? gps : ['Geral Distribuidora']).map(t => ({ t, tr: false, det: '', anx: null }));

    const novos = state.servicos.map(s => {
      if (state.selecionados.includes(s.id)) {
        return { ...s, st: 4, pend: pItems }; // Status 04 Distribuidora
      }
      return s;
    });

    store.setState({ servicos: novos, selecionados: [] });
    store.notifyToast(`${state.selecionados.length} serviço(s) enviado(s) para 04. Pendências Distribuidora!`);
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
              ${renderDynamicTableHeaders(state)}
            </tr>
          </thead>
          <tbody>
            ${pagItens.map((s, idx) => {
              const isFoco = foco && foco.id === s.id;
              const isIrma = idx > 0 && pagItens[idx-1].ct === s.ct;
              return `
                <tr class="row-foco" data-id="${s.id}" style="border-bottom:1px solid #eef1f0;background:${isFoco ? '#eaf2ee' : '#fff'};cursor:pointer">
                  ${renderDynamicTableRow(s, state, isIrma)}
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>

        ${renderPaginador(svcs.length, pag, 10)}
      </div>

      <div style="width:360px;background:#fff;border:1px solid var(--border-subtle);border-radius:10px;padding:16px">
        ${foco ? `
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
            <h3 style="margin:0;font-size:15px;font-family:var(--font-mono)">${foco.id}</h3>
            <span id="btn-open-drawer-foco" style="font-size:11.5px;font-weight:600;color:var(--ac-primary);cursor:pointer">Detalhamento ↗</span>
          </div>

          <span class="badge-status" style="background:#ffedd5;color:#9a3412;margin-bottom:12px">
            <span class="badge-status-num">0${foco.st}</span> ${STATUS_DEFS[foco.st]?.n || 'Pendências'}
          </span>

          <div style="margin-top:10px;display:flex;flex-direction:column;gap:10px">
            <div style="font-size:11px;color:#71807a">Supervisor: <b>${foco.supervisor || '—'}</b> · Equipe: <b>${foco.equipe || '—'}</b></div>
            
            <div style="font-weight:700;font-size:12px;color:#1c5f4b">${foco.st === 4 ? 'Itens de Correção Distribuidora' : 'Itens de Correção Cosampa (RN-04)'}</div>
            ${(foco.pend && foco.pend.length > 0 ? foco.pend : [
              { t: 'Evidências de Fotos de Campo', tr: false, det: foco.ret || 'Retorno de campo', anx: null },
              { t: 'Materiais Aplicados / Retirados', tr: false, det: 'Aguardando verificação', anx: null }
            ]).map((item, idx) => `
              <div class="card-pendencia" style="background:#fcfdfd;border:1px solid #eef1f0;padding:10px;border-radius:8px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                  <span style="font-size:12px;font-weight:700">${item.t}</span>
                  <label style="font-size:11px;cursor:pointer;display:flex;align-items:center;gap:4px">
                    <input type="checkbox" class="check-item-tratado" data-idx="${idx}" ${item.tr ? 'checked' : ''}>
                    <span style="color:${item.tr ? '#16a34a' : '#dc2626'};font-weight:700">${item.tr ? 'TRATADO' : 'PENDENTE'}</span>
                  </label>
                </div>
                <input class="text-input input-det-pend-${idx}" value="${item.det || ''}" placeholder="Justificativa técnica..." style="width:100%;font-size:11px;margin-bottom:6px">
                <div style="display:flex;align-items:center;gap:6px">
                  <button class="btn-anexo btn-trigger-anexo-${idx}" style="font-size:11px;padding:3px 8px">+ Anexo Evidência</button>
                  <span class="file-name-span-${idx}" style="font-size:10.5px;color:#71807a">${item.anx ? item.anx : 'Nenhum anexo'}</span>
                </div>
              </div>
            `).join('')}

            <div style="border-top:1px solid var(--border-subtle);padding-top:8px">
              <label style="font-size:11.5px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:6px">
                <input type="checkbox" id="check-reprogramar"> Necessita Reprogramar Visitada em Campo
              </label>
              <div id="box-reprogramacao" style="display:none;margin-top:6px">
                <span style="font-size:11px;color:#71807a">Data da Programação (obrigatório):</span>
                <input type="date" id="input-dt-reprogramacao" class="text-input" style="width:100%;margin-top:4px">
              </div>
            </div>

            <button id="btn-salvar-tratativa-rn04" class="btn-primary" style="width:100%;margin-top:4px">Salvar Tratativa & Retorno Automático (RN-04)</button>
          </div>
        ` : `<div style="color:#71807a">Nenhum serviço em pendência operacional nesta amostragem.</div>`}
      </div>
    </div>
  `;

  bindPaginadorEvents(container, svcs.length);

  container.querySelector('#check-reprogramar')?.addEventListener('change', (e) => {
    container.querySelector('#box-reprogramacao').style.display = e.target.checked ? 'block' : 'none';
  });

  container.querySelectorAll('.check-item-tratado').forEach(cb => {
    cb.addEventListener('change', (e) => {
      const isTratado = e.target.checked;
      const spanLabel = cb.nextElementSibling;
      if (spanLabel) {
        spanLabel.textContent = isTratado ? 'TRATADO' : 'PENDENTE';
        spanLabel.style.color = isTratado ? '#16a34a' : '#dc2626';
      }
    });
  });

  container.querySelector('#btn-salvar-tratativa-rn04')?.addEventListener('click', async () => {
    if (!foco) return;
    const cbs = container.querySelectorAll('.check-item-tratado');
    let totalItems = cbs.length;
    let tratadosCount = 0;
    cbs.forEach(cb => { if (cb.checked) tratadosCount++; });

    const necessitaReprog = container.querySelector('#check-reprogramar')?.checked;
    const dtReprog = container.querySelector('#input-dt-reprogramacao')?.value;

    if (necessitaReprog && !dtReprog) {
      return alert('Preencha a Data da Programação para a reprogramação do serviço.');
    }

    if (tratadosCount === totalItems && totalItems > 0) {
      // RN-04: Retorno Automático para Status 01 (Aguardando Conferência) ou 03
      // CDU V2: Status 04 (Dist) retorna para 03. Status 07 (Op) retorna para 03. Status 02 (Cos) retorna para 01.
      let statusRetorno = 1;
      if (foco.st === 7 || foco.st === 4) statusRetorno = 3;

      try {
        const res = await fetch(`/api/servicos/${foco.id}/tramitar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ novo_status_id: statusRetorno, usuario_nome: 'Supervisor Operacional' })
        });
        const data = await res.json();
        if (res.ok && data.status === 'sucesso') {
          const novos = store.getState().servicos.map(x => x.id === foco.id ? { ...x, st: statusRetorno, pend: [] } : x);
          store.setState({ servicos: novos, servicoFocoId: null });
          store.notifyToast(`RN-04: 100% dos itens tratados! SOB ${foco.id} retornou automaticamente para 0${statusRetorno}. Aguardando Conferência!`);
        } else {
          alert(data.mensagem || 'Erro ao realizar retorno automático.');
        }
      } catch (e) {
        alert('Erro de requisição: ' + e);
      }
    } else {
      store.notifyToast(`Tratativa parcial gravada (${tratadosCount}/${totalItems} itens tratados). SOB mantida em pendências.`);
    }
  });

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

async function renderGestaoAcessos() {
  const container = document.getElementById('gestao-acessos-container') || document.querySelector('.view-container');
  if (!container) return;

  const mode = store.getState().modeGestao || 'perfil';
  const perfis = authService.perfis;
  const usuarios = authService.usuarios;
  const usuarioFocoId = store.getState().usuarioGestaoId || usuarios[0].id;
  const usuarioFoco = usuarios.find(u => u.id === usuarioFocoId) || usuarios[0];

  let todosPerfis = store.getState().todosPerfisGestao;
  if (!todosPerfis) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:#71807a">Carregando permissões...</div>';
    try {
      const res = await fetch('/api/perfis_tela/todos');
      todosPerfis = await res.json();
      store.setState({ todosPerfisGestao: todosPerfis });
    } catch (e) {
      todosPerfis = [];
    }
  }

  let perfisUsuarioFoco = [];
  if (mode === 'usuario' && usuarioFoco.perfil !== 'Master') {
    try {
      const res = await fetch(`/api/usuarios/${usuarioFoco.id}/perfis_tela`);
      perfisUsuarioFoco = await res.json();
    } catch (e) {
      console.warn("Erro ao buscar perfis do usuario");
    }
  }

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

            ${usuarioFoco.perfil !== 'Master' ? `
              <div style="margin-bottom:16px;position:relative;z-index:10">
                <div style="font-size:12px;font-weight:700;margin-bottom:6px">Perfis de Tela Disponíveis:</div>
                <div class="dropdown-perfis-gestao" style="position:relative;display:inline-block;width:100%">
                  <button class="btn-secondary" style="width:100%;text-align:left;display:flex;justify-content:space-between;padding:8px 12px;background:#fff">
                    <span>Selecionar Perfis de Tela...</span> <span style="font-size:10px">▼</span>
                  </button>
                  <div class="dropdown-content-perfis" style="display:none;position:absolute;top:100%;left:0;width:100%;background:#fff;border:1px solid var(--border-subtle);border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,0.1);z-index:100;max-height:300px;overflow-y:auto;margin-top:4px;padding:8px">
                    <div style="font-size:11px;font-weight:700;color:#71807a;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #eef1f0">PERFIS GLOBAIS / MASTER</div>
                    ${todosPerfis.filter(p => p.tipo === 'global' || p.criado_por_id === 1).map(p => `
                      <label style="display:flex;align-items:center;gap:6px;font-size:12px;padding:6px 4px;cursor:pointer">
                        <input type="checkbox" class="cb-perfil-usuario" value="${p.id}" ${perfisUsuarioFoco.includes(p.id) ? 'checked' : ''}> 
                        <span>${p.tipo==='global'?'🌍':'🔒'} ${p.nome}</span>
                      </label>
                    `).join('')}
                    
                    <div class="sub-dropdown-trigger" style="margin-top:8px;padding:8px;background:#f7f9f8;border-radius:4px;cursor:pointer;font-size:11.5px;font-weight:600;display:flex;flex-direction:column;position:relative">
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <span>Perfis criados por usuários</span> <span style="color:#71807a">▾</span>
                      </div>
                      <div class="sub-dropdown-content" style="display:none;margin-top:8px;border-top:1px solid #eef1f0;padding-top:6px;display:flex;flex-direction:column;gap:4px">
                        ${todosPerfis.filter(p => p.tipo !== 'global' && Number(p.criado_por_id) !== 1).length > 0 
                          ? todosPerfis.filter(p => p.tipo !== 'global' && Number(p.criado_por_id) !== 1).map(p => `
                            <label style="display:flex;align-items:center;gap:6px;font-size:12px;padding:4px;cursor:pointer;font-weight:400">
                              <input type="checkbox" class="cb-perfil-usuario" value="${p.id}" ${perfisUsuarioFoco.includes(p.id) ? 'checked' : ''}> 
                              <span>👤 ${p.nome}</span>
                            </label>
                          `).join('')
                          : '<div style="font-size:11px;color:#a0aba6;padding:4px;font-weight:400">Nenhum perfil criado por usuários.</div>'
                        }
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <button id="btn-save-user-perms" class="btn-primary">Salvar Permissões do Usuário</button>
            ` : ''}
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

  container.querySelector('#btn-save-user-perms')?.addEventListener('click', async () => {
    const cbs = container.querySelectorAll('.check-perm-user');
    const telas = [];
    cbs.forEach(cb => { if (cb.checked) telas.push(cb.getAttribute('data-tela')); });
    authService.atualizarPermissoesUsuario(usuarioFoco.id, telas);

    // Salvar perfis de tela
    const perfisCbs = container.querySelectorAll('.cb-perfil-usuario:checked');
    const perfisSelecionados = Array.from(perfisCbs).map(cb => parseInt(cb.value));
    
    try {
      const res = await fetch(`/api/usuarios/${usuarioFoco.id}/perfis_tela`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ perfis: perfisSelecionados })
      });
      if (res.ok) {
        store.notifyToast(`Permissões e perfis salvos para o usuário ${usuarioFoco.nome}!`);
      } else {
        alert('Erro ao salvar perfis no banco.');
      }
    } catch (e) {
      alert('Erro ao salvar perfis: ' + e);
    }
  });

  const ddBtn = container.querySelector('.dropdown-perfis-gestao button');
  const ddContent = container.querySelector('.dropdown-content-perfis');
  if (ddBtn && ddContent) {
    ddBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      ddContent.style.display = ddContent.style.display === 'none' ? 'block' : 'none';
    });
    
    const subTrigger = container.querySelector('.sub-dropdown-trigger');
    const subContent = container.querySelector('.sub-dropdown-content');
    if (subTrigger && subContent) {
      // Toggle accordion on click, but ignore clicks on the content itself
      subTrigger.addEventListener('click', (e) => {
        if (e.target.closest('.sub-dropdown-content')) return; // let checkboxes work
        e.stopPropagation();
        subContent.style.display = subContent.style.display === 'none' ? 'flex' : 'none';
      });
    }
    
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.dropdown-perfis-gestao')) {
        ddContent.style.display = 'none';
      }
    });
  }

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

  const stDef = STATUS_DEFS[s.st] || STATUS_DEFS[1];

  container.innerHTML = `
    <div class="drawer-panel" style="width:480px;background:#fff;border-left:1px solid var(--border-subtle);display:flex;flex-direction:column;position:fixed;right:0;top:0;bottom:0;z-index:9999;box-shadow:-4px 0 20px rgba(0,0,0,0.1)">
      <div style="padding:16px 20px;border-bottom:1px solid var(--border-subtle);display:flex;justify-content:space-between;align-items:center;background:#f8faf9">
        <div>
          <h3 style="margin:0;font-size:16px;font-family:var(--font-mono)">${s.id} — R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</h3>
          <span style="font-size:11.5px;color:#71807a">PEP: <b>${s.pep||'—'}</b> · TDC: <b>${s.tdc||'—'}</b></span>
        </div>
        <button id="btn-close-drawer" style="background:none;border:none;font-size:24px;cursor:pointer;color:#71807a">×</button>
      </div>

      <div style="padding:16px 20px;flex:1;overflow-y:auto;font-size:12px;display:flex;flex-direction:column;gap:14px">
        <div style="display:flex;align-items:center;justify-content:space-between">
          <span class="badge-status" style="background:${stDef.bg};color:${stDef.fg};font-size:12px;padding:4px 10px">
            <span class="badge-status-num">0${s.st}</span> ${stDef.n}
          </span>
          <span style="font-size:11px;color:#5b6b65">SLA: <b>${s.d || 3} dias</b></span>
        </div>

        <!-- Seção 1: Dados do Serviço (GPM) -->
        <div style="background:#f7f9f8;padding:12px;border-radius:8px;border:1px solid #eef1f0">
          <div style="font-weight:700;font-size:12px;margin-bottom:8px;color:#1c5f4b">📍 Informações da Atividade de Campo</div>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:6px">
            <div><b>Contrato:</b> ${s.ct}</div>
            <div><b>Origem:</b> ${s.origem || 'PDA'}</div>
            <div><b>Tipo Atividade:</b> ${s.tp}</div>
            <div><b>Centro Serviço:</b> ${s.dep || '—'}</div>
            <div><b>Data Execução:</b> ${s.data || '—'}</div>
            <div><b>Incidência:</b> ${s.incidencia || '—'}</div>
          </div>
          <div style="margin-top:6px"><b>Local da Obra:</b> ${s.ob}</div>
          <div><b>Endereço:</b> ${s.endereco || s.ob}</div>
        </div>

        <!-- Seção 2: Equipe e Veículo -->
        <div style="background:#f7f9f8;padding:12px;border-radius:8px;border:1px solid #eef1f0">
          <div style="font-weight:700;font-size:12px;margin-bottom:8px;color:#1c5f4b">👥 Hierarquia e Equipe de Campo (RN-05)</div>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:6px">
            <div><b>Coordenador:</b> ${s.coordenador || '—'}</div>
            <div><b>Supervisor:</b> ${s.supervisor || '—'}</div>
            <div><b>Equipe:</b> ${s.equipe || '—'}</div>
            <div><b>Turno:</b> ${s.turno || '—'}</div>
            <div><b>Placa Veículo:</b> ${s.placa || '—'}</div>
            <div><b>Modelo Veículo:</b> ${s.modelo_veiculo || '—'}</div>
          </div>
          <div style="margin-top:6px"><b>Membros:</b> ${s.membros || '—'}</div>
        </div>

        <!-- Secao V2 Dinamica: Validacao (05) e Conciliacao (11, 12) -->
        ${s.st === 5 ? `
        <div style="background:#fff;border:1px solid #d97706;padding:14px;border-radius:8px">
          <div style="font-weight:700;font-size:12px;margin-bottom:6px;color:#92400e">✅ Aprovar Medição (Cliente)</div>
          <div style="display:flex;gap:8px;margin-bottom:10px">
            <input type="date" id="drawer-data-validacao" class="text-input" style="flex:1" placeholder="Data da 1ª Validação">
            <button id="btn-hoje-validacao" class="btn-secondary" style="padding:0 8px;font-size:11px">Hoje</button>
          </div>
          <button id="btn-aprovar-05" class="btn-primary" style="width:100%;background:#059669;border-color:#059669">Aprovar Medição (Avança p/ 08)</button>
        </div>
        ` : ''}

        ${s.st === 11 ? `
        <div style="background:#fff;border:1px solid #ea580c;padding:14px;border-radius:8px">
          <div style="font-weight:700;font-size:12px;margin-bottom:6px;color:#9a3412">⚖️ Comparativo Financeiro-Operacional</div>
          <div style="display:flex;gap:10px;margin-bottom:10px">
            <div style="flex:1;background:#f8faf9;padding:8px;border-radius:4px;border:1px solid #eef1f0">
              <div style="font-size:10px;color:#71807a">Valor Executado (Cosampa)</div>
              <div style="font-weight:700;font-size:14px">R$ ${s.v.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
            </div>
            <div style="flex:1;background:#fefce8;padding:8px;border-radius:4px;border:1px solid #fef08a">
              <div style="font-size:10px;color:#854d0e">Valor Pago (Distribuidora)</div>
              <div style="font-weight:700;font-size:14px;color:#854d0e">R$ ${(s.valor_pago || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
            </div>
          </div>
          <input type="text" id="drawer-justificativa-11" class="text-input" style="width:100%;margin-bottom:10px" placeholder="Justificativa da Divergência da Conciliação..." value="${s.divergencia_conciliacao || ''}">
          <div style="display:flex;gap:8px">
            <button id="btn-encaminhar-12" class="btn-primary" style="flex:1;background:#c026d3;border-color:#c026d3;font-size:11px">Cobrar Cliente (Ir p/ 12)</button>
          </div>
        </div>
        ` : ''}

        ${s.st === 12 ? `
        <div style="background:#fff;border:1px solid #c026d3;padding:14px;border-radius:8px">
          <div style="font-weight:700;font-size:12px;margin-bottom:6px;color:#86198f">📅 Mês de Reapresentação</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:8px">Defina o mês de reapresentação para tramitar para o status 13 (Em Disputa).</div>
          <input type="month" id="drawer-mes-reapresentacao" class="text-input" style="width:100%;margin-bottom:10px" value="${s.mes_reapresentacao || ''}">
          <button id="btn-encaminhar-13" class="btn-primary" style="width:100%;background:#9333ea;border-color:#9333ea">Iniciar Disputa (Avança p/ 13)</button>
        </div>
        ` : ''}

        <!-- Seção 3: Tramitação com Trava RN-03 -->
        <div style="background:#fff;border:1px solid var(--border-subtle);padding:14px;border-radius:8px">
          <div style="font-weight:700;font-size:12px;margin-bottom:6px">⚡ Tramitar Status (CDU-01 / RN-03)</div>
          <div style="font-size:11px;color:#71807a;margin-bottom:8px">Avanço bloqueado automaticamente se houver pendência pendente (RN-03).</div>
          <div style="display:flex;gap:8px">
            <select id="drawer-select-next-status" class="select-input" style="flex:1">
              ${Object.keys(STATUS_DEFS).map(k => `<option value="${k}" ${s.st===Number(k)?'selected':''}>0${k}. ${STATUS_DEFS[k].n}</option>`).join('')}
            </select>
            <button id="drawer-btn-tramitar" class="btn-primary">Avançar</button>
          </div>
        </div>

        <!-- Seção 4: Log de Auditoria RN-01 -->
        <div style="border-top:1px solid var(--border-subtle);padding-top:12px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <div style="font-weight:700;font-size:12px">📜 Histórico de Auditoria (RN-01)</div>
            <button id="btn-load-auditoria" class="btn-secondary" style="font-size:11px;padding:4px 8px">Carregar Logs</button>
          </div>
          <div id="auditoria-list-container" style="max-height:140px;overflow-y:auto;background:#fafcfb;padding:8px;border-radius:6px;border:1px solid #eef1f0;font-size:11px;color:#5b6b65">
            Clique no botão acima para carregar os logs de auditoria desta SOB.
          </div>
        </div>
      </div>
    </div>
  `;

  container.querySelector('#btn-close-drawer')?.addEventListener('click', () => store.setState({ drawerServicoId: null }));

  container.querySelector('#drawer-btn-tramitar')?.addEventListener('click', async () => {
    const nxt = container.querySelector('#drawer-select-next-status').value;
    if (!nxt) return;
    try {
      const res = await fetch(`/api/servicos/${s.id}/tramitar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ novo_status_id: Number(nxt), usuario_nome: 'Analista Fechamento' })
      });
      const data = await res.json();
      if (res.ok && data.status === 'sucesso') {
        const novos = store.getState().servicos.map(x => x.id === s.id ? { ...x, st: Number(nxt) } : x);
        store.setState({ servicos: novos, drawerServicoId: null });
        store.notifyToast(`SOB ${s.id} tramitada com sucesso para 0${nxt}!`);
      } else {
        alert(data.mensagem || 'Falha ao tramitar serviço.');
      }
    } catch (e) {
      console.error(e);
      alert('Erro na API');
    }
  });

  container.querySelector('#btn-hoje-validacao')?.addEventListener('click', () => {
    const d = new Date();
    const str = d.toISOString().split('T')[0];
    const input = container.querySelector('#drawer-data-validacao');
    if (input) input.value = str;
  });

  container.querySelector('#btn-aprovar-05')?.addEventListener('click', async () => {
    const dt = container.querySelector('#drawer-data-validacao').value;
    if (!dt) return alert("Data da 1ª Validação é obrigatória para aprovação.");
    
    // 1. Atualizar dados
    await fetch(`/api/servicos/${s.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data_primeira_validacao: dt, usuario_nome: 'Validador Cliente' })
    });
    
    // 2. Tramitar para 08
    const res = await fetch(`/api/servicos/${s.id}/tramitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ novo_status_id: 8, usuario_nome: 'Validador Cliente' })
    });
    if (res.ok) {
      const novos = store.getState().servicos.map(x => x.id === s.id ? { ...x, st: 8, data_primeira_validacao: dt } : x);
      store.setState({ servicos: novos, drawerServicoId: null });
      store.notifyToast('Serviço aprovado e enviado para Faturamento!');
    }
  });

  container.querySelector('#btn-encaminhar-12')?.addEventListener('click', async () => {
    const just = container.querySelector('#drawer-justificativa-11').value;
    if (!just) return alert("Justificativa obrigatória.");
    await fetch(`/api/servicos/${s.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ divergencia_conciliacao: just })
    });
    const res = await fetch(`/api/servicos/${s.id}/tramitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ novo_status_id: 12 })
    });
    if (res.ok) {
      const novos = store.getState().servicos.map(x => x.id === s.id ? { ...x, st: 12, divergencia_conciliacao: just } : x);
      store.setState({ servicos: novos, drawerServicoId: null });
      store.notifyToast('Enviado para Cobrança (Status 12)!');
    }
  });

  container.querySelector('#btn-encaminhar-13')?.addEventListener('click', async () => {
    const mes = container.querySelector('#drawer-mes-reapresentacao').value;
    if (!mes) return alert("Mês de Reapresentação é obrigatório.");
    await fetch(`/api/servicos/${s.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mes_reapresentacao: mes })
    });
    const res = await fetch(`/api/servicos/${s.id}/tramitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ novo_status_id: 13 })
    });
    if (res.ok) {
      const novos = store.getState().servicos.map(x => x.id === s.id ? { ...x, st: 13, mes_reapresentacao: mes } : x);
      store.setState({ servicos: novos, drawerServicoId: null });
      store.notifyToast('Disputa Iniciada (Status 13)!');
    }
  });

  container.querySelector('#btn-load-auditoria')?.addEventListener('click', async () => {
    const listCont = container.querySelector('#auditoria-list-container');
    listCont.innerHTML = 'Carregando logs...';
    try {
      const res = await fetch(`/api/servicos/${s.id}/auditoria`);
      if (res.ok) {
        const logs = await res.json();
        if (logs.length === 0) {
          listCont.innerHTML = 'Nenhum log de auditoria registrado para esta SOB até o momento.';
        } else {
          listCont.innerHTML = logs.map(l => `
            <div style="border-bottom:1px solid #eef1f0;padding:4px 0;margin-bottom:4px">
              <b>${l.usuario_nome}</b> (${l.data_hora})<br>
              Campo <i>${l.campo_alterado}</i>: de <span style="color:#b03a28">${l.valor_anterior}</span> ➔ <span style="color:#1c5f4b">${l.novo_valor}</span>
            </div>
          `).join('');
        }
      } else {
        listCont.innerHTML = 'Erro ao buscar auditoria.';
      }
    } catch (e) {
      listCont.innerHTML = 'Erro de rede ao buscar logs.';
    }
  });
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

// --- CDU-08: WIZARD DE IMPORTACAO DE PLANILHA ---
function renderWizardImportacao(state) {
  const wizard = state.wizardImportacao;
  if (!wizard.aberto) {
    const existing = document.getElementById('modal-wizard-importacao');
    if (existing) existing.remove();
    return;
  }
  
  let modal = document.getElementById('modal-wizard-importacao');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'modal-wizard-importacao';
    modal.style.position = 'fixed';
    modal.style.top = '0'; modal.style.left = '0'; modal.style.width = '100vw'; modal.style.height = '100vh';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.display = 'flex'; modal.style.justifyContent = 'center'; modal.style.alignItems = 'center';
    modal.style.zIndex = '9999';
    document.body.appendChild(modal);
  }
  
  const fechar = () => store.setState({ wizardImportacao: { ...wizard, aberto: false } });
  
  let conteudo = '';
  if (wizard.passo === 1) {
    conteudo = `
      <div style="font-size:14px;color:#5b6b65;margin-bottom:12px">Passo 1: Selecione o arquivo XLSX/CSV</div>
      <input type="file" id="input-arquivo-importacao" accept=".xlsx,.xls,.csv" style="margin-bottom:12px;width:100%">
      ${wizard.abasDisponiveis.length > 0 ? `
        <div style="margin-top:12px">
          <label style="font-size:12px;font-weight:600">Selecione a aba da planilha:</label>
          <select id="select-aba" class="text-input" style="width:100%;margin-top:4px">
            <option value="">Selecione...</option>
            ${wizard.abasDisponiveis.map(a => `<option value="${a}" ${wizard.abaSelecionada === a ? 'selected' : ''}>${a}</option>`).join('')}
          </select>
        </div>
      ` : ''}
    `;
  } else if (wizard.passo === 2) {
    conteudo = `
      <div style="font-size:14px;color:#5b6b65;margin-bottom:12px">Passo 2: Qual a linha do cabeçalho?</div>
      <div style="max-height:300px;overflow:auto;font-size:11px;border:1px solid #eef1f0;border-radius:6px">
        <table style="width:100%;border-collapse:collapse;white-space:nowrap">
          <thead>
            <tr style="background:#f4f6f5;border-bottom:2px solid #eef1f0;text-align:left;color:#5b6b65;font-weight:600">
              <th style="padding:6px;width:30px;text-align:center">#</th>
              ${wizard.colunasPlanilha.map((col, i) => `<th style="padding:6px">Coluna ${i+1}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
          ${wizard.linhasPrevisualizacao.slice(0,5).map((row, idx) => `
            <tr style="cursor:pointer;background:${wizard.linhaCabecalhoIndex === idx ? '#eaf2ee' : '#fff'};border-bottom:1px solid #eef1f0" class="row-cabecalho" data-idx="${idx}">
              <td style="padding:6px;width:30px;text-align:center;font-weight:700;color:${wizard.linhaCabecalhoIndex === idx ? '#1c5f4b' : '#a1b0aa'}">${idx}</td>
              ${wizard.colunasPlanilha.map(col => `<td style="padding:6px">${row[col] !== null ? row[col] : ''}</td>`).join('')}
            </tr>
          `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } else if (wizard.passo === 3) {
    // Opcoes do select de colunas do excel
    const excelCols = wizard.colunasPlanilha.map(c => `<option value="${c}">${c}</option>`).join('');
    
    // Lista de mapeamentos ativos
    const mapList = Object.entries(wizard.mapeamentoAtivo).map(([internalKey, excelCol]) => {
      // checa se excelCol tem vazios na pre-visualizacao
      let temBrancos = false;
      if (excelCol) {
         temBrancos = wizard.linhasPrevisualizacao.slice(wizard.linhaCabecalhoIndex+1).some(r => r[excelCol] === null || String(r[excelCol]).trim() === '');
      }
      
      const internalDef = store.getState().wizardImportacao.colunasInternasDisponiveis?.find(c => c.id === internalKey) || {label: internalKey};
      
      return `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;padding:8px;border:1px solid #eef1f0;border-radius:6px;background:#fcfdfd">
          <div style="flex:1;font-size:12px;font-weight:600">${internalDef.label} ${internalKey==='num_servico'?'<span style="color:#b03a28">*</span>':''}</div>
          <div style="flex:1">
            <select class="text-input select-mapeamento" data-key="${internalKey}" style="width:100%;border-color:${temBrancos?'#d97706':'#d7dedb'}">
              <option value="">Selecione a coluna...</option>
              ${wizard.colunasPlanilha.map(c => `<option value="${c}" ${excelCol === c ? 'selected' : ''}>${c}</option>`).join('')}
            </select>
            ${temBrancos ? `<div style="font-size:10px;color:#d97706;margin-top:2px">⚠️ Contém células vazias (serão ignoradas)</div>` : ''}
          </div>
          <button class="btn-remover-mapeamento" data-key="${internalKey}" style="background:transparent;border:none;color:#b03a28;cursor:pointer;font-size:14px">×</button>
        </div>
      `;
    }).join('');

    // Colunas disponiveis para adicionar
    const colunasParaAdicionar = (store.getState().wizardImportacao.colunasInternasDisponiveis || [
      { id: "num_servico", label: "Número do Serviço (Chave Obrigatória)" },
      { id: "cod_pep_obra", label: "Código PEP Obra" },
      { id: "tdc", label: "Código TDC" },
      { id: "cliente", label: "Cliente" },
      { id: "supervisor", label: "Supervisor" },
      { id: "coordenador", label: "Coordenador" },
      { id: "equipe", label: "Equipe" },
      { id: "data_primeira_validacao", label: "Data Validação" }
    ]).filter(c => !wizard.mapeamentoAtivo.hasOwnProperty(c.id));
    
    // Atualiza estado interno de cols disponiveis se for a primeira vez
    if (!store.getState().wizardImportacao.colunasInternasDisponiveis) {
       setTimeout(() => store.setState({ wizardImportacao: { ...wizard, colunasInternasDisponiveis: [
          { id: "num_servico", label: "Número do Serviço (Chave Obrigatória)" },
          { id: "cod_pep_obra", label: "Código PEP Obra" },
          { id: "tdc", label: "Código TDC" },
          { id: "cliente", label: "Cliente" },
          { id: "supervisor", label: "Supervisor" },
          { id: "coordenador", label: "Coordenador" },
          { id: "equipe", label: "Equipe" },
          { id: "data_primeira_validacao", label: "Data Validação" }
       ] } }), 0);
    }

    conteudo = `
      <div style="font-size:14px;color:#5b6b65;margin-bottom:12px">Passo 3: Mapeamento de Colunas</div>
      <div style="display:flex;gap:12px;margin-bottom:8px">
        <div style="flex:1;font-size:11px;font-weight:700;color:#71807a;text-transform:uppercase">Informação do Sistema</div>
        <div style="flex:1;font-size:11px;font-weight:700;color:#71807a;text-transform:uppercase">Coluna da Planilha</div>
        <div style="width:20px"></div>
      </div>
      <div style="max-height:250px;overflow:auto;margin-bottom:12px">
        ${mapList}
      </div>
      ${colunasParaAdicionar.length > 0 ? `
        <div style="display:flex;align-items:center;gap:8px">
          <select id="select-nova-coluna" class="text-input" style="flex:1">
            <option value="">+ Selecione uma coluna para mapear...</option>
            ${colunasParaAdicionar.map(c => `<option value="${c.id}">${c.label}</option>`).join('')}
          </select>
          <button id="btn-add-mapeamento" class="btn-secondary" style="padding:6px 12px">Adicionar</button>
        </div>
      ` : ''}
    `;
  }
  
  modal.innerHTML = `
    <div style="background:#fff;border-radius:12px;width:700px;max-width:90vw;box-shadow:0 10px 25px rgba(0,0,0,0.15);overflow:hidden;display:flex;flex-direction:column">
      <div style="padding:16px 24px;border-bottom:1px solid #eef1f0;display:flex;justify-content:space-between;align-items:center">
        <div style="font-size:18px;font-weight:700;color:#14483a">Importação de Planilha</div>
        <button id="btn-fechar-wizard" style="background:none;border:none;font-size:20px;cursor:pointer;color:#a1b0aa">&times;</button>
      </div>
      
      <div style="padding:24px;flex:1">
        ${wizard.erro ? `<div style="background:#fdf2f0;color:#b03a28;padding:12px;border-radius:6px;margin-bottom:12px;font-size:12px">${wizard.erro}</div>` : ''}
        ${wizard.sucesso ? `<div style="background:#eaf2ee;color:#1c5f4b;padding:12px;border-radius:6px;margin-bottom:12px;font-size:12px">${wizard.sucesso}</div>` : ''}
        ${wizard.carregando && wizard.passo === 3 ? `
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:250px;gap:16px">
             <div style="width:40px;height:40px;border:4px solid #eef1f0;border-top:4px solid #1c5f4b;border-radius:50%;animation:spin 1s linear infinite"></div>
             <div style="font-weight:600;color:#14483a;font-size:16px">Sincronizando Banco de Dados...</div>
             <div style="font-size:13px;color:#71807a;text-align:center">Comparando e atualizando serviços. Isso pode levar alguns<br>segundos dependendo do tamanho da sua planilha.<br><b>Por favor, não feche esta janela.</b></div>
             <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
          </div>
        ` : conteudo}
      </div>
      
      <div style="padding:16px 24px;border-top:1px solid #eef1f0;background:#f7f9f8;display:flex;justify-content:space-between;align-items:center">
        <button id="btn-voltar-wizard" style="background:none;border:none;color:#0f52ba;font-size:13px;font-weight:600;cursor:pointer;${wizard.passo === 1 ? 'visibility:hidden' : ''}">
          &lsaquo; Voltar
        </button>
        <button id="btn-avancar-wizard" class="btn-primary" style="padding:8px 16px;opacity:${wizard.carregando ? 0.6 : 1}" ${wizard.carregando ? 'disabled' : ''}>
          ${wizard.carregando ? 'Processando...' : (wizard.passo === 3 ? 'Confirmar e Sincronizar' : 'Continuar')}
        </button>
      </div>
    </div>
  `;
  
  // Eventos UI
  modal.querySelector('#btn-fechar-wizard').addEventListener('click', fechar);
  
  modal.querySelector('#btn-voltar-wizard')?.addEventListener('click', () => {
    store.setState({ wizardImportacao: { ...wizard, passo: wizard.passo - 1, erro: null } });
  });
  
  // Eventos Passo 1
  if (wizard.passo === 1) {
    modal.querySelector('#input-arquivo-importacao')?.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      store.setState({ wizardImportacao: { ...wizard, carregando: true, erro: null } });
      const fd = new FormData();
      fd.append('file', file);
      try {
        const res = await fetch('/api/servicos/upload-temp', { method: 'POST', body: fd });
        const data = await res.json();
        if (res.ok) {
          store.setState({ wizardImportacao: { ...wizard, arquivoTempId: data.arquivo_temp_id, abasDisponiveis: data.abas, abaSelecionada: data.abas[0], carregando: false } });
        } else throw new Error(data.mensagem);
      } catch(err) {
        store.setState({ wizardImportacao: { ...wizard, carregando: false, erro: err.message } });
      }
    });
    
    modal.querySelector('#select-aba')?.addEventListener('change', (e) => {
      store.setState({ wizardImportacao: { ...wizard, abaSelecionada: e.target.value } });
    });
  }
  
  // Eventos Passo 2
  if (wizard.passo === 2) {
    modal.querySelectorAll('.row-cabecalho').forEach(r => {
      r.addEventListener('click', () => {
        store.setState({ wizardImportacao: { ...wizard, linhaCabecalhoIndex: Number(r.getAttribute('data-idx')) } });
      });
    });
  }
  
  // Eventos Passo 3
  if (wizard.passo === 3) {
    modal.querySelector('#btn-add-mapeamento')?.addEventListener('click', () => {
      const select = modal.querySelector('#select-nova-coluna');
      const val = select.value;
      if (val) {
        store.setState({ wizardImportacao: { ...wizard, mapeamentoAtivo: { ...wizard.mapeamentoAtivo, [val]: "" } } });
      }
    });
    
    modal.querySelectorAll('.btn-remover-mapeamento').forEach(btn => {
      btn.addEventListener('click', () => {
        const key = btn.getAttribute('data-key');
        const novos = {...wizard.mapeamentoAtivo};
        delete novos[key];
        store.setState({ wizardImportacao: { ...wizard, mapeamentoAtivo: novos } });
      });
    });
    
    modal.querySelectorAll('.select-mapeamento').forEach(sel => {
      sel.addEventListener('change', (e) => {
        const key = sel.getAttribute('data-key');
        const val = e.target.value;
        store.setState({ wizardImportacao: { ...wizard, mapeamentoAtivo: { ...wizard.mapeamentoAtivo, [key]: val } } });
      });
    });
  }
  
  // Avancar / Confirmar
  modal.querySelector('#btn-avancar-wizard')?.addEventListener('click', async () => {
    if (wizard.carregando) return;
    
    if (wizard.passo === 1) {
      if (!wizard.arquivoTempId || !wizard.abaSelecionada) {
        return store.setState({ wizardImportacao: { ...wizard, erro: 'Selecione um arquivo e uma aba.' } });
      }
      store.setState({ wizardImportacao: { ...wizard, carregando: true, erro: null } });
      try {
        const res = await fetch('/api/servicos/pre-visualizar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ arquivo_temp_id: wizard.arquivoTempId, aba_selecionada: wizard.abaSelecionada })
        });
        const data = await res.json();
        if (res.ok) {
           store.setState({ wizardImportacao: { ...wizard, passo: 2, linhasPrevisualizacao: data.linhas, colunasPlanilha: data.colunas, carregando: false } });
        } else throw new Error(data.mensagem);
      } catch(err) {
        store.setState({ wizardImportacao: { ...wizard, carregando: false, erro: err.message } });
      }
    } 
    else if (wizard.passo === 2) {
       // Extrai colunas da linha selecionada mantendo a ordem exata do backend
       const row = wizard.linhasPrevisualizacao[wizard.linhaCabecalhoIndex];
       const cols = wizard.colunasPlanilha.map(col => row[col]).filter(c => c && String(c).trim() !== '');
       
       // Pre-mapeamento automatico
       let novoMap = { "num_servico": "" }; // Sempre coloca o obrigatorio
       store.setState({ wizardImportacao: { ...wizard, passo: 3, colunasPlanilha: cols, mapeamentoAtivo: novoMap, erro: null } });
    }
    else if (wizard.passo === 3) {
       // Verifica validacao de chave
       if (!wizard.mapeamentoAtivo['num_servico']) {
          return store.setState({ wizardImportacao: { ...wizard, erro: "O mapeamento do 'Número do Serviço' é obrigatório para sincronizar os dados." } });
       }
       
       store.setState({ wizardImportacao: { ...wizard, carregando: true, erro: null } });
       try {
         const res = await fetch('/api/servicos/importar-dinamico', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
             arquivo_temp_id: wizard.arquivoTempId,
             aba_selecionada: wizard.abaSelecionada,
             linha_cabecalho: wizard.linhaCabecalhoIndex,
             mapeamento: wizard.mapeamentoAtivo,
             usuario_nome: 'Importador (Planilha)'
           })
         });
         const data = await res.json();
         if (res.ok && data.status === 'concluido') {
            const sucessos = data.atualizados;
            const falhas = data.nao_encontrados.length;
            const msg = `Sincronização concluída! ${sucessos} registros atualizados. ${falhas > 0 ? '('+falhas+' inconsistências não localizadas)' : ''}`;
            store.setState({ wizardImportacao: { ...wizard, sucesso: msg, carregando: false } });
            // Timeout para fechar e recarregar
            setTimeout(() => {
              store.setState({ wizardImportacao: { ...wizard, aberto: false } });
              window.location.reload(); // Recarrega os dados do banco
            }, 3000);
         } else throw new Error(data.mensagem);
       } catch(err) {
         store.setState({ wizardImportacao: { ...wizard, carregando: false, erro: err.message } });
       }
    }
  });
}
