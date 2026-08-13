window.initSIGES = function(DCLogic) {
class Component extends DCLogic {
  constructor(props){
    super(props);
    this.ST={
      1:{n:'Aguardando Conferência',a:'Fechamento',m:'med',sla:3},
      2:{n:'Pendências Operacionais',a:'Operação',m:'pen',sla:5},
      3:{n:'Aguard. Envio p/ Validação',a:'Fechamento',m:'med',sla:2},
      4:{n:'Aguard. Validação do Cliente',a:'Faturamento',m:'fat',sla:7},
      5:{n:'Rejeitado na Validação (Fech.)',a:'Fechamento',m:'med',sla:3},
      6:{n:'Rejeitado na Validação (Oper.)',a:'Operação',m:'pen',sla:5},
      7:{n:'Validado — Aguard. Autorização',a:'Faturamento',m:'fat',sla:3},
      8:{n:'Faturado — Aguard. Conciliação',a:'Faturamento',m:'con',sla:10},
      9:{n:'Análise de Conciliação',a:'Faturamento',m:'con',sla:5},
      10:{n:'Conciliado c/ Divergências',a:'Fechamento',m:'med',sla:4},
      11:{n:'Pgto a Menor — Cobrar Cliente',a:'Fechamento',m:'med',sla:7},
      12:{n:'Pgto a Menor — Em Disputa',a:'Fechamento',m:'med',sla:15},
      13:{n:'Faturado Total',a:'Geral',m:'fin',sla:null},
      14:{n:'Faturado a Maior',a:'Geral',m:'fin',sla:null},
      15:{n:'Faturado a Menor',a:'Geral',m:'fin',sla:null}};
    this.MC={
      med:{lb:'Medição',bg:'oklch(0.93 0.035 250)',fg:'oklch(0.38 0.09 250)',bar:'oklch(0.56 0.1 250)'},
      pen:{lb:'Pendências',bg:'oklch(0.95 0.05 80)',fg:'oklch(0.45 0.1 70)',bar:'oklch(0.65 0.11 75)'},
      fat:{lb:'Faturamento',bg:'oklch(0.94 0.035 300)',fg:'oklch(0.42 0.09 300)',bar:'oklch(0.58 0.1 300)'},
      con:{lb:'Conciliação',bg:'oklch(0.94 0.04 210)',fg:'oklch(0.4 0.08 210)',bar:'oklch(0.58 0.09 210)'},
      fin:{lb:'Finalizado',bg:'oklch(0.94 0.05 160)',fg:'oklch(0.38 0.09 160)',bar:'oklch(0.56 0.1 160)'}};
    this.CONTR={A:'CT-2024/018 · Dist. Leste',B:'CT-2025/007 · Dist. Sul',C:'CT-2023/031 · Ilum. Pública ZL'};
    this.NEXT={1:3,3:4,5:3,10:3};
    this.TIPOS=['Documentos','Fotos','Materiais','Retorno','Outros'];
    const CHAIN={1:[1],2:[1,2],3:[1,3],4:[1,3,4],5:[1,3,4,5],6:[1,3,4,6],7:[1,3,4,7],8:[1,3,4,7,8],9:[1,3,4,7,8,9],10:[1,3,4,7,8,9,10],11:[1,3,4,7,8,9,11],12:[1,3,4,7,8,9,11,12],13:[1,3,4,7,8,9,13],14:[1,3,4,7,8,9,14],15:[1,3,4,7,8,9,15]};
    const CAT={
      'Rede':[['3.1','Lançamento de cabo BT (m)'],['3.4','Instalação de cruzeta'],['5.2','Aterramento de estrutura']],
      'Transformador':[['4.1','Instalação de transformador'],['4.3','Chave fusível'],['5.2','Aterramento de estrutura']],
      'Medidor':[['6.1','Troca de medidor'],['6.2','Lacração'],['6.4','Vistoria de campo']],
      'Ramal':[['2.1','Ramal de ligação'],['2.3','Conector perfurante'],['6.4','Vistoria de campo']],
      'Poste':[['1.1','Implantação de poste'],['1.3','Escavação e reaterro'],['5.2','Aterramento de estrutura']],
      'Iluminação':[['7.1','Luminária LED'],['7.2','Braço de IP'],['7.4','Relé fotoelétrico']]};
    const P=(t,tr,det,ax)=>({t:t,tr:!!tr,det:det||'',ax:ax||0});
    const svc=[
      {id:'SOB-2026-0341',ct:'A',ob:'Vila Prudente',tp:'Rede',st:1,v:12400,d:11,nota:'NM-0873'},
      {id:'SOB-2026-0347',ct:'A',ob:'Vila Prudente',tp:'Medidor',st:1,v:980,d:8,nota:'NM-0879'},
      {id:'SOB-2026-0352',ct:'B',ob:'Jd. Ângela',tp:'Transformador',st:1,v:38200,d:12,nota:'NM-0881'},
      {id:'SOB-2026-0298',ct:'A',ob:'Penha',tp:'Rede',st:2,v:21500,d:4,pend:[P('Fotos'),P('Materiais')]},
      {id:'SOB-2026-0301',ct:'B',ob:'Capela do Socorro',tp:'Ramal',st:2,v:3400,d:7,pend:[P('Documentos'),P('Retorno')]},
      {id:'SOB-2026-0315',ct:'C',ob:'Itaquera',tp:'Poste',st:2,v:7250,d:10,pend:[P('Fotos')]},
      {id:'SOB-2026-0322',ct:'C',ob:'São Mateus',tp:'Iluminação',st:2,v:5600,d:9,pend:[P('Materiais'),P('Outros',1,'Aguardando reposição do almoxarifado',1)]},
      {id:'SOB-2026-0289',ct:'A',ob:'Penha',tp:'Rede',st:3,v:45900,d:12,nota:'NM-0851'},
      {id:'SOB-2026-0293',ct:'B',ob:'Grajaú',tp:'Transformador',st:3,v:61300,d:10,nota:'NM-0854'},
      {id:'SOB-2026-0276',ct:'A',ob:'Mooca',tp:'Rede',st:4,v:78500,d:6,nota:'NM-0812'},
      {id:'SOB-2026-0281',ct:'C',ob:'Guaianases',tp:'Medidor',st:4,v:1250,d:9,nota:'NM-0836'},
      {id:'SOB-2026-0269',ct:'B',ob:'Parelheiros',tp:'Rede',st:5,v:18700,d:11,nota:'NM-0842',ret:'Baremo divergente na atividade 3.1'},
      {id:'SOB-2026-0262',ct:'A',ob:'Tatuapé',tp:'Ramal',st:6,v:4800,d:5,ret:'Fotos ilegíveis — refazer',pend:[P('Fotos'),P('Documentos',1,'ART reenviada em 06/08',1)]},
      {id:'SOB-2026-0255',ct:'C',ob:'Cidade Líder',tp:'Transformador',st:6,v:29400,d:8,ret:'Falta ART assinada',pend:[P('Documentos')]},
      {id:'SOB-2026-0248',ct:'A',ob:'Belém',tp:'Rede',st:7,v:52000,d:11,nota:'NM-0790'},
      {id:'SOB-2026-0237',ct:'B',ob:'Santo Amaro',tp:'Rede',st:8,v:66800,d:3,nota:'NF-4521'},
      {id:'SOB-2026-0231',ct:'A',ob:'Brás',tp:'Iluminação',st:8,v:9800,d:9,nota:'NF-4498'},
      {id:'SOB-2026-0224',ct:'C',ob:'Ermelino Matarazzo',tp:'Medidor',st:9,v:2300,d:7,nota:'NF-4476'},
      {id:'SOB-2026-0216',ct:'A',ob:'Sapopemba',tp:'Rede',st:10,v:33500,d:6,nota:'NF-4460',ret:'Divergência de R$ 1.240 no baremo'},
      {id:'SOB-2026-0209',ct:'B',ob:'Pirituba',tp:'Transformador',st:11,v:41200,d:4,nota:'NF-4447',ret:'Pago a menor: R$ 38.900'},
      {id:'SOB-2026-0198',ct:'C',ob:'Lapa',tp:'Rede',st:12,v:27600,d:1,nota:'NF-4431',ret:'Em disputa desde 01/08'},
      {id:'SOB-2026-0187',ct:'A',ob:'Sé',tp:'Rede',st:13,v:15300,d:8,nota:'NF-4432'},
      {id:'SOB-2026-0176',ct:'B',ob:'Butantã',tp:'Medidor',st:14,v:1900,d:5,nota:'NF-4419',ret:'Pago a maior: + R$ 120'},
      {id:'SOB-2026-0164',ct:'C',ob:'Freguesia do Ó',tp:'Poste',st:15,v:6400,d:2,nota:'NF-4401',ret:'Pago a menor aceito pelo contrato'}];
    svc.forEach(s=>{
      s.hist=(CHAIN[s.st]||[s.st]).map((st,i,arr)=>({st:st,d:s.d-(arr.length-1-i)*2}));
      const cat=CAT[s.tp],sh=[0.55,0.3,0.15];
      s.bar=cat.map((c,i)=>{
        const med=Math.round(s.v*sh[i]);let pago=null;
        if(s.st===13)pago=med;
        else if(s.st===14)pago=Math.round(med*1.02);
        else if(s.st===11||s.st===12||s.st===15)pago=Math.round(med*0.92);
        else if(s.st===10)pago=i===0?Math.round(med*0.88):med;
        return {cod:c[0],desc:c[1],qtd:1+((s.v+i*37)%9),med:med,pago:pago};});});
    this.state={tela:'gerencial',perfil:'Fechamento',pin:!(props&&props.menuRecolhido),hov:false,
      f:{periodo:'mes',contrato:'todos',tipo:'todos',area:'todas',status:'todos',busca:''},
      presets:[{nome:'Dist. Leste · 7 dias',f:{periodo:'7d',contrato:'A',tipo:'todos',area:'todas',status:'todos',busca:''}}],
      salvando:false,pNome:'',sel:[],alvo:'',
      gp:{Documentos:false,Fotos:false,Materiais:false,Retorno:false,Outros:false},
      foco:null,drawer:null,prem:false,toast:null,min:7,svc:svc};
  }
  componentDidMount(){
    this.tick=setInterval(()=>this.setState(s=>({min:s.min+1})),60000);
    this.esc=(e)=>{if(e.key==='Escape')this.setState({drawer:null,prem:false});};
    window.addEventListener('keydown',this.esc);
  }
  componentWillUnmount(){clearInterval(this.tick);clearTimeout(this.tt);window.removeEventListener('keydown',this.esc);}
  avisar(m){clearTimeout(this.tt);this.setState({toast:m});this.tt=setTimeout(()=>this.setState({toast:null}),4200);}
  dias(s){return 13-s.d;}
  over(s){const l=this.ST[s.st].sla;return l!=null&&this.dias(s)>l;}
  fdate(d){return d<1?String(31+d).padStart(2,'0')+'/07':String(d).padStart(2,'0')+'/08';}
  money(v){return 'R$ '+v.toLocaleString('pt-BR',{maximumFractionDigits:0});}
  kf(v){return v>=1e6?'R$ '+(v/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mi':(v>=1000?'R$ '+(v/1000).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mil':this.money(v));}
  num(st){return String(st).padStart(2,'0');}
  n1(x){return x.toLocaleString('pt-BR',{maximumFractionDigits:1});}
  filtra(){const f=this.state.f;return this.state.svc.filter(s=>{
    if(f.contrato!=='todos'&&s.ct!==f.contrato)return false;
    if(f.tipo!=='todos'&&s.tp!==f.tipo)return false;
    if(f.area!=='todas'&&this.ST[s.st].a!==f.area)return false;
    if(f.status!=='todos'&&s.st!==+f.status)return false;
    if(f.periodo==='7d'&&s.d<7)return false;
    if(f.periodo==='3d'&&s.d<11)return false;
    if(f.busca){const q=f.busca.toLowerCase();if(!((s.id+' '+s.ob+' '+s.tp+' '+this.CONTR[s.ct]).toLowerCase().includes(q)))return false;}
    return true;});}
  mover(s,st){s.st=st;s.d=13;s.hist.push({st:st,d:13});}
  sf(k){return (e)=>{const f=Object.assign({},this.state.f);f[k]=e.target.value;this.setState({f:f});};}
  chip(st){const m=this.MC[this.ST[st].m];return{cNum:this.num(st),cNome:this.ST[st].n,cBg:m.bg,cFg:m.fg};}
  slaCell(s){const l=this.ST[s.st].sla,d=this.dias(s);
    if(l==null)return{slaLb:'—',sBg:'transparent',sFg:'#8a9791',slaTip:'Finalizado — sem SLA'};
    const o=d>l;
    return{slaLb:d+' d',sBg:o?'#f8e7e3':'transparent',sFg:o?'#b03a28':'#5b6b65',slaTip:'Na etapa há '+d+(d===1?' dia':' dias')+' · SLA '+l+' d'+(o?' — ESTOURADO':'')};}
  linha(s){const sel=this.state.sel.includes(s.id);const ab=(s.pend||[]).filter(p=>!p.tr).length;
    return Object.assign({key:s.id,id:s.id,ob:s.ob,tp:s.tp,ctLb:this.CONTR[s.ct],nota:s.nota||'—',data:this.fdate(s.d),
      dep:ab>0?'Pend. ('+ab+')':([10,11,12].indexOf(s.st)>=0?'Conciliação':'—'),
      valor:this.money(s.v),ret:s.ret||'—',sel:sel,bg:sel?'#eaf2ee':'#fff',
      abrir:()=>this.setState({drawer:s.id}),
      toggleSel:()=>{const c=this.state.sel.slice();const i=c.indexOf(s.id);if(i>=0)c.splice(i,1);else c.push(s.id);this.setState({sel:c});}},
      this.chip(s.st),this.slaCell(s));}
  renderVals(){
    const S=this.state,ST=this.ST,MC=this.MC;
    const all=this.filtra();
    const byM=(m)=>all.filter(s=>ST[s.st].m===m);
    const med=byM('med'),pen=byM('pen'),fat=byM('fat'),con=byM('con'),fin=byM('fin');
    const ativos=all.filter(s=>ST[s.st].m!=='fin');
    const sum=(l)=>l.reduce((a,s)=>a+s.v,0);
    const avg=(l)=>l.length?l.reduce((a,s)=>a+this.dias(s),0)/l.length:0;
    const estour=ativos.filter(s=>this.over(s));
    const aberto=S.pin||S.hov;
    const ACCESS={'Fechamento':['gerencial','medicao','pendencias','finalizados','relatorios'],
      'Operação':['gerencial','pendencias','finalizados','relatorios'],
      'Faturamento':['gerencial','medicao','pendencias','faturamento','conciliacoes','finalizados','relatorios']};
    const MENUDEF=[['gerencial','★','Gerencial'],['medicao','01','01. Medição'],['pendencias','02','02. Pendências'],['faturamento','03','03. Faturamento'],['conciliacoes','04','04. Conciliações'],['finalizados','05','05. Finalizados'],['relatorios','C·R','Consultas + Relatórios']];
    const menu=MENUDEF.map(md=>{const id=md[0],ic=md[1],lb=md[2];const en=ACCESS[S.perfil].indexOf(id)>=0;const at=S.tela===id;
      return{ic:ic,lb:lb,bg:at?'var(--ac,#1c5f4b)':'transparent',fg:at?'#ffffff':(en?'#c6d2cc':'#5c6a64'),
        op:en?'1':'0.55',cur:en?'pointer':'not-allowed',fw:at?'600':'500',
        tip:en?lb:(lb+' — sem acesso no perfil '+S.perfil),
        ir:()=>{if(!en){this.avisar('O perfil '+S.perfil+' não tem acesso a '+lb+'.');return;}this.setState({tela:id,sel:[],drawer:null,foco:null});}};});
    const TITLES={gerencial:'Gerencial',medicao:'01. Medição',pendencias:'02. Pendências',faturamento:'03. Faturamento',conciliacoes:'04. Conciliações',finalizados:'05. Finalizados',relatorios:'Consultas + Relatórios'};
    const macroSeg=[['med',med],['pen',pen],['fat',fat],['con',con]].map(x=>({lb:MC[x[0]].lb,c:String(x[1].length),w:ativos.length?Math.max(x[1].length/ativos.length*100,2):2,color:MC[x[0]].bar}));
    const counts=[];for(let i=1;i<=15;i++)counts.push(all.filter(s=>s.st===i).length);
    const cmax=Math.max.apply(null,counts.concat([1]));
    const barsStatus=counts.map((c,i)=>({lb:this.num(i+1),cLb:String(c),h:c===0?3:8+Math.round(c/cmax*100),color:c===0?'#e2e8e5':MC[ST[i+1].m].bar,tip:this.num(i+1)+'. '+ST[i+1].n+' — '+c+' serviço(s)'}));
    const vmDefs=[['med',med],['pen',pen],['fat',fat],['con',con]];
    const vmax=Math.max.apply(null,vmDefs.map(x=>sum(x[1])).concat([1]));
    const valMacro=vmDefs.map(x=>({lb:MC[x[0]].lb,val:this.kf(sum(x[1])),w:Math.max(sum(x[1])/vmax*100,1.5),color:MC[x[0]].bar}));
    const SEM=[['06/07',182,121],['13/07',205,150],['20/07',174,168],['27/07',231,155],['03/08',198,176],['10/08',126,92]];
    const semanas=SEM.map(w=>({lb:w[0],mH:Math.round(w[1]/231*108),fH:Math.round(w[2]/231*108),mTip:'Medido: R$ '+w[1]+' mil',fTip:'Faturado: R$ '+w[2]+' mil'}));
    const gstats=[];for(let i=1;i<=12;i++){const l=ativos.filter(s=>s.st===i);if(l.length)gstats.push({st:i,avg:avg(l)});}
    gstats.sort((a,b)=>b.avg-a.avg);
    const gmax=gstats.length?Math.max(gstats[0].avg,1):1;
    const gargalos=gstats.slice(0,5).map(g=>{const m=MC[ST[g.st].m];const ov=ST[g.st].sla!=null&&g.avg>ST[g.st].sla;
      return{num:this.num(g.st),nome:ST[g.st].n,bg:m.bg,fg:m.fg,dias:this.n1(g.avg)+' d',slaLb:'SLA '+ST[g.st].sla+' d',diasFg:ov?'#b03a28':'#1f2a26',w:Math.max(g.avg/gmax*100,3),barColor:m.bar};});
    const radar=estour.slice().sort((a,b)=>(this.dias(b)-ST[b.st].sla)-(this.dias(a)-ST[a.st].sla)).slice(0,6)
      .map(s=>Object.assign({key:s.id,id:s.id,obLb:s.ob+' · '+s.tp,diasLb:this.dias(s)+' d',limLb:'SLA '+ST[s.st].sla+' d',valor:this.money(s.v),abrir:()=>this.setState({drawer:s.id})},this.chip(s.st)));
    const medEst=med.filter(s=>this.over(s));
    const st3=all.filter(s=>s.st===3);
    const conc=all.filter(s=>[10,11,12].indexOf(s.st)>=0);
    const maxMed=medEst.length?Math.max.apply(null,medEst.map(s=>this.dias(s))):0;
    const insightsMed=[
      {t:medEst.length?medEst.length+' serviço(s) com SLA estourado na fila — o mais antigo há '+maxMed+' dias.':'Nenhum serviço com SLA estourado na fila de medição.'},
      {t:st3.length?this.kf(sum(st3))+' em '+st3.length+' serviço(s) prontos para envio à validação do cliente (03).':'Nenhum serviço aguardando envio para validação (03).'},
      {t:conc.length?conc.length+' retorno(s) de conciliação a retrabalhar (10–12), somando '+this.kf(sum(conc))+'.':'Nenhum retorno de conciliação pendente (10–12).'}];
    const rowsMed=med.map(s=>this.linha(s));
    const selAll=med.length>0&&med.every(s=>S.sel.indexOf(s.id)>=0);
    const pendAb=pen.reduce((a,s)=>a+(s.pend||[]).filter(p=>!p.tr).length,0);
    const maxPen=pen.length?Math.max.apply(null,pen.map(s=>this.dias(s))):0;
    const tCounts=this.TIPOS.map(t=>pen.reduce((a,s)=>a+((s.pend||[]).some(p=>p.t===t&&!p.tr)?1:0),0));
    const tmax=Math.max.apply(null,tCounts.concat([1]));
    const tiposChart=this.TIPOS.map((t,i)=>({lb:t,c:String(tCounts[i]),w:Math.max(tCounts[i]/tmax*100,2)}));
    const rowsPen=pen.map(s=>{const base=this.linha(s);base.bg=S.foco===s.id?'#eaf2ee':'#fff';
      base.tipos=(s.pend||[]).map(p=>({lb:(p.tr?'✓ ':'✕ ')+p.t,bg:p.tr?'#e4f1ea':'#f8e7e3',fg:p.tr?'#1c6b4f':'#b03a28'}));
      base.focar=()=>this.setState({foco:s.id});return base;});
    const fs=S.foco?S.svc.find(x=>x.id===S.foco):null;
    const focoOn=!!(fs&&(fs.st===2||fs.st===6));
    let pendItens=[],focoProgW=0,focoProgLb='',focoChip={cNum:'',cNome:'',cBg:'transparent',cFg:'#1f2a26'},focoId='';
    if(focoOn){focoId=fs.id;focoChip=this.chip(fs.st);
      const tot=fs.pend.length,tr=fs.pend.filter(p=>p.tr).length;
      focoProgW=tot?Math.round(tr/tot*100):0;focoProgLb=tr+' de '+tot+' tratada(s)';
      pendItens=fs.pend.map(p=>({t:p.t,ic:p.tr?'✓':'✕',icBg:p.tr?'#e4f1ea':'#f8e7e3',icFg:p.tr?'#1c6b4f':'#b03a28',icBd:p.tr?'#bfdccd':'#eec9c0',
        stLb:p.tr?'tratada':'pendente',stFg:p.tr?'#1c6b4f':'#b03a28',det:p.det,anxLb:p.ax?' ('+p.ax+')':'',
        toggle:()=>{p.tr=!p.tr;
          if(fs.pend.every(x=>x.tr)){this.mover(fs,1);this.avisar(fs.id+' — todas as pendências tratadas. Retornou para 01. Aguardando Conferência.');this.setState({foco:null,svc:this.state.svc});}
          else this.setState({svc:this.state.svc});},
        setDet:(e)=>{p.det=e.target.value;this.setState({svc:this.state.svc});},
        anexar:()=>{p.ax++;this.avisar('Anexo adicionado em "'+p.t+'" ('+fs.id+') — simulação.');this.setState({svc:this.state.svc});}}));}
    const SIMMAP={faturamento:fat,conciliacoes:con,finalizados:fin};
    const rowsSim=(SIMMAP[S.tela]||[]).map(s=>this.linha(s));
    const selSvc=()=>S.sel.map(id=>S.svc.find(x=>x.id===id)).filter(Boolean);
    const aplicarStatus=()=>{const l=selSvc();if(!l.length){this.avisar('Selecione ao menos um serviço na tabela.');return;}
      if(!S.alvo){this.avisar('Escolha o novo status no seletor.');return;}
      const st=+S.alvo;l.forEach(s=>{this.mover(s,st);if(st===2&&!(s.pend||[]).some(p=>!p.tr))s.pend=[{t:'Outros',tr:false,det:'',ax:0}];});
      this.avisar(l.length+' serviço(s) movido(s) para '+this.num(st)+'. '+ST[st].n+'.');
      this.setState({sel:[],alvo:'',svc:S.svc});};
    const tramitar=()=>{const l=selSvc();if(!l.length){this.avisar('Selecione ao menos um serviço na tabela.');return;}
      let mov=0,skip=0;l.forEach(s=>{const nx=this.NEXT[s.st];if(nx){this.mover(s,nx);mov++;}else skip++;});
      this.avisar(mov+' serviço(s) tramitado(s)'+(skip?' · '+skip+' sem próxima etapa sugerida — use Alterar status.':'.'));
      this.setState({sel:[],svc:S.svc});};
    const enviarPend=()=>{const l=selSvc();if(!l.length){this.avisar('Selecione ao menos um serviço na tabela.');return;}
      const tipos=this.TIPOS.filter(t=>S.gp[t]);if(!tipos.length){this.avisar('Marque ao menos um tipo de pendência.');return;}
      l.forEach(s=>{s.pend=tipos.map(t=>({t:t,tr:false,det:'',ax:0}));this.mover(s,2);});
      this.avisar(l.length+' serviço(s) enviado(s) para 02. Pendências ('+tipos.join(', ')+').');
      this.setState({sel:[],gp:{Documentos:false,Fotos:false,Materiais:false,Retorno:false,Outros:false},svc:S.svc});};
    const gpItens=this.TIPOS.map(t=>({t:t,on:S.gp[t],toggle:()=>{const g=Object.assign({},this.state.gp);g[t]=!g[t];this.setState({gp:g});}}));
    const ds=S.drawer?S.svc.find(x=>x.id===S.drawer):null;
    const dOn=!!ds;
    let det={},baremo=[],hist=[],pendDet=[],pendDetOn=false,bTotMed='',bTotPago='';
    if(ds){const l=ST[ds.st].sla;
      det=Object.assign({id:ds.id,valor:this.money(ds.v),contrato:this.CONTR[ds.ct],ob:ds.ob,tp:ds.tp,area:ST[ds.st].a,
        nota:ds.nota||'—',data:this.fdate(ds.d),
        tempo:this.dias(ds)+(this.dias(ds)===1?' dia':' dias'),tempoFg:this.over(ds)?'#b03a28':'#1f2a26',
        slaLb:l==null?'— (finalizado)':l+' dias'},this.chip(ds.st));
      baremo=ds.bar.map(b=>{const dif=b.pago==null?null:b.pago-b.med;
        return{cod:b.cod,desc:b.desc,qtd:String(b.qtd),med:this.money(b.med),pago:b.pago==null?'—':this.money(b.pago),
          dif:dif==null?'—':(dif===0?'=':(dif>0?'+ ':'− ')+this.money(Math.abs(dif)).slice(3)),
          difFg:dif==null?'#8a9791':(dif<0?'#b03a28':(dif>0?'#1c6b4f':'#8a9791'))};});
      bTotMed=this.money(ds.bar.reduce((a,b)=>a+b.med,0));
      const anyP=ds.bar.some(b=>b.pago!=null);
      bTotPago=anyP?this.money(ds.bar.reduce((a,b)=>a+(b.pago||0),0)):'—';
      hist=ds.hist.slice().reverse().map((h,i)=>{const m=MC[ST[h.st].m];
        return{num:this.num(h.st),nome:ST[h.st].n,bg:m.bg,fg:m.fg,data:this.fdate(h.d),dot:i===0?'var(--ac,#1c5f4b)':'#cfd8d4',cur:i===0?'· etapa atual':''};});
      pendDet=(ds.pend||[]).map(p=>({t:p.t,lb:p.tr?'tratada':'pendente',fg:p.tr?'#1c6b4f':'#b03a28',txt:p.det||'Sem detalhamento registrado.'}));
      pendDetOn=pendDet.length>0;}
    const PR=['Acesso por perfil: Gerencial, 05. Finalizados e Consultas + Relatórios visíveis a todos; matriz exata de permissões a confirmar.',
      'SLA por etapa assumido (dias): 01→3 · 02→5 · 03→2 · 04→7 · 05→3 · 06→5 · 07→3 · 08→10 · 09→5 · 10→4 · 11→7 · 12→15. Ilustrativo, a calibrar.',
      '“Baixar / Tramitar” avança só onde a próxima etapa é inequívoca (01→03, 03→04, 05→03, 10→03); demais casos exigem “Alterar status”.',
      'Retorno automático para 01 quando todas as pendências são tratadas: aplicado aos status 02 e 06 (o esboço define para 02).',
      '“Alterar status” para 02 sem tipos marcados gera pendência genérica “Outros”.',
      'Colunas padronizadas: Nota = nº da nota de medição/NF · Dep. = pendências/dependências vinculadas · Retorno = último motivo registrado.',
      'Insights, série “Medido × Faturado” e baremos/atividades são ilustrativos (dados fictícios).',
      'Telas 03. Faturamento, 04. Conciliações, 05. Finalizados e Consultas + Relatórios sem esboço — exibidas como listas mínimas provisórias.',
      'Presets de filtro mantidos apenas em memória (sem persistência) neste protótipo.',
      '“Última atualização” simulada; na implantação, automação periódica (~15 min) por última modificação no GPM.',
      'Fotos e edição de dados só no GPM — aqui somente avanço de etapa, tratativa de pendência e consulta (“Abrir no GPM”).'];
    const prItens=PR.map((t,i)=>({n:this.num(i+1),t:t}));
    const f=S.f;
    const temFiltro=f.periodo!=='mes'||f.contrato!=='todos'||f.tipo!=='todos'||f.area!=='todas'||f.status!=='todos'||!!f.busca;
    return {
      acVar:(this.props&&this.props.acento)||'#1c5f4b',
      rpVar:((this.props&&this.props.densidade)||'compacta')==='confortavel'?'11px':'7px',
      sbW:aberto?236:62,menuAberto:aberto,
      sbEnter:()=>this.setState({hov:true}),sbLeave:()=>this.setState({hov:false}),
      togglePin:()=>this.setState({pin:!this.state.pin}),
      pinChar:S.pin?'«':'»',pinTip:S.pin?'Recolher menu (fica só com ícones)':'Fixar menu aberto',
      menu:menu,titulo:TITLES[S.tela],
      updLbl:S.min===0?'agora':'há '+S.min+' min',
      sync:()=>{this.setState({min:0});this.avisar('Base sincronizada com o GPM (simulação).');},
      nPrem:PR.length,abrirPremissas:()=>this.setState({prem:true}),
      perfil:S.perfil,
      setPerfil:(e)=>{const p=e.target.value;const ok=ACCESS[p].indexOf(S.tela)>=0;this.setState({perfil:p,tela:ok?S.tela:'gerencial',sel:[]});if(!ok)this.avisar('Tela indisponível para o perfil '+p+' — voltando à Gerencial.');},
      f:f,sfPeriodo:this.sf('periodo'),sfContrato:this.sf('contrato'),sfTipo:this.sf('tipo'),sfArea:this.sf('area'),sfStatus:this.sf('status'),sfBusca:this.sf('busca'),
      temFiltro:temFiltro,
      limpar:()=>this.setState({f:{periodo:'mes',contrato:'todos',tipo:'todos',area:'todas',status:'todos',busca:''}}),
      presets:S.presets.map((p,i)=>({nome:p.nome,aplicar:()=>this.setState({f:Object.assign({},p.f)}),
        remover:(e)=>{e.stopPropagation();const c=this.state.presets.slice();c.splice(i,1);this.setState({presets:c});}})),
      salvando:S.salvando,naoSalvando:!S.salvando,pNome:S.pNome,
      setPNome:(e)=>this.setState({pNome:e.target.value}),
      iniciarSalvar:()=>this.setState({salvando:true}),
      cancelarPreset:()=>this.setState({salvando:false,pNome:''}),
      confirmarPreset:()=>{const n=S.pNome.trim()||('Preset '+(S.presets.length+1));this.setState({presets:S.presets.concat([{nome:n,f:Object.assign({},S.f)}]),salvando:false,pNome:''});this.avisar('Filtros salvos no preset "'+n+'".');},
      telaGer:S.tela==='gerencial',telaMed:S.tela==='medicao',telaPen:S.tela==='pendencias',
      telaSim:['faturamento','conciliacoes','finalizados'].indexOf(S.tela)>=0,telaRel:S.tela==='relatorios',
      kEsteira:String(ativos.length),kEsteiraSub:all.length+' no total (com finalizados)',
      kValor:this.kf(sum(ativos)),kValorSub:'soma dos serviços ativos',
      kTempo:this.n1(avg(ativos))+' d',kTempoSub:estour.length+' com SLA estourado',kTempoSubFg:estour.length?'#b03a28':'#71807a',
      macroSeg:macroSeg,nTotalLb:all.length+' serviços com os filtros atuais',
      barsStatus:barsStatus,valMacro:valMacro,calloutVal:this.kf(sum(all.filter(s=>s.st===4))),
      semanas:semanas,gargalos:gargalos,radar:radar,radarVazio:radar.length===0,
      cM1v:String(med.length),cM1s:this.kf(sum(med)),
      cM2v:String(medEst.length),cM2s:medEst.length?'mais antigo há '+maxMed+' d':'tudo dentro do prazo',cM2fg:medEst.length?'#b03a28':'#1f2a26',
      cM3v:String(st3.length),cM3s:this.kf(sum(st3)),
      insightsMed:insightsMed,rowsMed:rowsMed,medVazia:rowsMed.length===0,
      selAll:selAll,
      toggleAll:()=>{const ids=med.map(s=>s.id);const todos=ids.length&&ids.every(id=>this.state.sel.indexOf(id)>=0);
        const c=todos?this.state.sel.filter(id=>ids.indexOf(id)<0):Array.from(new Set(this.state.sel.concat(ids)));
        this.setState({sel:c});},
      stopProp:(e)=>e.stopPropagation(),
      selLb:S.sel.length+' selecionado(s)',nMedLb:med.length+' serviço(s) na fila',nSel:String(S.sel.length),
      alvo:S.alvo,setAlvo:(e)=>this.setState({alvo:e.target.value}),
      aplicarStatus:aplicarStatus,tramitar:tramitar,gpItens:gpItens,enviarPend:enviarPend,
      cP1v:String(pen.length),cP1s:this.kf(sum(pen)),
      cP2v:String(pendAb),cP2s:'em '+pen.length+' serviço(s)',
      cP3v:this.n1(avg(pen))+' d',cP3s:pen.length?'mais antigo: '+maxPen+' d':'—',
      tiposChart:tiposChart,rowsPen:rowsPen,penVazia:rowsPen.length===0,
      focoOn:focoOn,focoOff:!focoOn,focoId:focoId,focoChip:focoChip,focoProgW:focoProgW,focoProgLb:focoProgLb,
      focoAbrirDet:()=>this.setState({drawer:this.state.foco}),
      pendItens:pendItens,
      rowsSim:rowsSim,simVazia:rowsSim.length===0,
      dOn:dOn,det:det,baremo:baremo,bTotMed:bTotMed,bTotPago:bTotPago,hist:hist,pendDet:pendDet,pendDetOn:pendDetOn,
      fecharDrawer:()=>this.setState({drawer:null}),
      abrirGpm:()=>this.avisar('Somente leitura aqui — o serviço seria aberto no GPM (repositório oficial).'),
      prOn:S.prem,prItens:prItens,fecharPremissas:()=>this.setState({prem:false}),
      scrimOn:dOn||S.prem,fecharTudo:()=>this.setState({drawer:null,prem:false}),
      toastOn:!!S.toast,toastMsg:S.toast||''
    };
  }
}
  return Component;
}
