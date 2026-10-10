const $=id=>document.getElementById(id);let records=[],page=0,selected=null;const size=6;
function node(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
function filtered(){const q=$('search').value.toLowerCase();return records.filter(r=>(r.caso_id+' '+r.modelo).toLowerCase().includes(q)&&(!$('model').value||r.modelo===$('model').value))}
function detail(r){selected=r.execucao_id;const d=$('detail');d.replaceChildren(node('div','RESULTADO PERSISTIDO','eyebrow'),node('h2',r.caso_id));const dl=node('dl');for(const [k,v]of Object.entries({'Idade':r.entrada_json.idade+' anos','Diagnóstico':r.entrada_json.diagnostico_principal,'Internações anteriores':r.entrada_json.internacoes_anteriores_12_meses,'Origem':'Sintética'})){dl.append(node('dt',k),node('dd',v))}d.append(dl,node('h3','Resumo do Gemini'),node('p',r.resposta_json.resumo||'Resumo não disponível'),node('h3','Limitações declaradas'));const ul=node('ul');for(const t of r.resposta_json.limitacoes||[])ul.append(node('li',t));d.append(ul);const audit=node('details');audit.append(node('summary','Consultar rastreabilidade'));for(const [k,v]of Object.entries({'Execução':r.execucao_id,'Modelo':r.modelo,'Prompt':r.versao_prompt,'SHA-256':r.resposta_sha256})){audit.append(node('h3',k),node('code',v))}d.append(audit);render()}
function render(){const rows=filtered();page=Math.min(page,Math.max(0,Math.ceil(rows.length/size)-1));$('rows').replaceChildren();for(const r of rows.slice(page*size,(page+1)*size)){const tr=node('tr');if(r.execucao_id===selected)tr.className='selected';tr.append(node('td',r.caso_id),node('td',r.criado_em));const td=node('td'),btn=node('button','Ver');btn.setAttribute('aria-label','Ver detalhes de '+r.caso_id+' em '+r.criado_em);btn.onclick=()=>detail(r);td.append(btn);tr.append(td);$('rows').append(tr)}if(!rows.length){const tr=node('tr'),td=node('td','Nenhum registro encontrado.');td.colSpan=3;tr.append(td);$('rows').append(tr)}$('count').textContent=rows.length+' resultados';$('page').textContent=rows.length?'Página '+(page+1)+' de '+Math.ceil(rows.length/size):'Sem resultados';$('prev').disabled=page===0;$('next').disabled=(page+1)*size>=rows.length}
async function load(){$('refresh').disabled=true;$('message').textContent='Consultando registros…';try{const res=await fetch('/api/painel');if(!res.ok)throw Error();const d=await res.json();records=d.registros;selected=null;$('detail').replaceChildren(node('h3','Selecione um resultado'),node('p','Consulte o resumo, as limitações e a rastreabilidade.'));$('connection').textContent=d.online?'● MySQL conectado':'○ MySQL indisponível';$('connection').className='pill '+(d.online?'success':'failure');$('message').textContent=d.erro||'';$('total').textContent=d.online?records.length:'—';$('cases').textContent=d.online?new Set(records.map(r=>r.caso_id)).size:'—';$('runs').textContent=d.relatorios.filter(r=>r.sucesso).length;$('time').textContent=new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});const model=$('model');model.replaceChildren(new Option('Todos os modelos',''));for(const m of new Set(records.map(r=>r.modelo)))model.append(new Option(m,m));$('reports').replaceChildren();for(const r of d.relatorios.slice(0,8)){const row=node('div',undefined,'report');row.append(node('span',r.data?new Date(r.data).toLocaleString('pt-BR'):'Data não registrada'),node('span',r.casos.length+' casos'),node('span',r.sucesso?'Concluída':'Com falha','pill '+(r.sucesso?'success':'failure')));$('reports').append(row)}if(!d.relatorios.length)$('reports').append(node('p','Nenhum relatório local encontrado.'));page=0;render()}catch{$('message').textContent='Não foi possível atualizar. Verifique se o servidor do painel continua aberto.';$('connection').textContent='○ Sem conexão';records=[];render()}finally{$('refresh').disabled=false}}
$('search').oninput=()=>{page=0;render()};$('model').onchange=()=>{page=0;render()};$('prev').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};$('refresh').onclick=load;load();

const riskForm=$('risk-form');let riskBusy=false;
riskForm.addEventListener('input',()=>{if(!riskBusy){$('risk-status').textContent='';$('risk-result').replaceChildren(node('h3','Resultado da avaliação'),node('p','Dados alterados. Execute uma nova avaliação.'));}});
async function riskRequest(e,validateOnly=false){
 e.preventDefault();if(riskBusy||!riskForm.reportValidity())return;
 riskBusy=true;for(const el of riskForm.elements)el.disabled=true;
 $('risk-result').replaceChildren(node('h3','Resultado da avaliação'),node('p',validateOnly?'Aguardando avaliação.':'Processando os dados…'));
 $('risk-status').textContent=validateOnly?'Validando…':'Avaliando e salvando. Aguarde sem reenviar.';
 const payload={paciente_id:$('patient').value.trim(),idade:Number($('age').value),diagnostico_principal:$('cid').value.trim(),internacoes_anteriores_12_meses:Number($('admissions').value)};
 try{
  const response=await fetch(validateOnly?'/api/validar':'/api/avaliar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!(response.headers.get('content-type')||'').includes('application/json'))throw Error('O servidor não carregou esta função (HTTP '+response.status+'). Reinicie o painel; se persistir, verifique processos duplicados na porta 8503.');
  const result=await response.json();if(!response.ok||!result.sucesso)throw Error(result.erro||'Avaliação não confirmada.');
  if(validateOnly){$('risk-status').textContent=result.mensagem;return;}
  const r=result.dados,p=Number(r.probabilidade_estimada);
  if(r.status!=='OK'||r.probabilidade_estimada==null||!Number.isFinite(p)||p<0||p>1||!['BAIXO','MEDIO','ALTO'].includes(r.risco_readmissao))throw Error('A API não retornou uma classificação válida. Confira o registro antes de repetir.');
  const box=$('risk-result');box.replaceChildren(node('div','ÁRVORE DE DECISÃO · COORTE SINTÉTICA','eyebrow'),node('h3','Resultado · '+payload.paciente_id));
  const summary=node('div',undefined,'risk-summary');summary.append(node('div',r.risco_readmissao,'risk-value'),node('div',(p*100).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+'%','risk-value'));const visual=node('div',undefined,'risk-visual risk-'+r.risco_readmissao.toLowerCase());visual.append(summary,riskGauge(p));box.append(visual);
  const meter=node('meter',String(p*100)+'%','risk-meter');meter.min=0;meter.max=1;meter.value=p;meter.setAttribute('aria-label','Probabilidade estimada pelo modelo sintético');box.append(meter,node('p','Modelo '+r.modelo_versao+' · Classificação #'+r.classificacao_id),node('h3','Fatores retornados pelo modelo'));
  const list=node('ul');for(const f of r.fatores_relevantes||[])list.append(node('li',f.descricao));box.append(list);if(!list.children.length)box.append(node('p','Nenhum fator destacado para este caso.'));
  box.append(node('small','As importâncias do modelo são globais; não representam causalidade individual.'));
  if(r.explicacao){box.append(node('h3','Explicação complementar'),node('p',r.explicacao.texto||'Sem explicação.'),node('small','Origem: '+r.explicacao.origem+' · Status: '+r.explicacao.status));}
  $('risk-status').textContent='Classificação #'+r.classificacao_id+' salva pela API anterior. O histórico E2 abaixo contém apenas resumos da baseline.';
 }catch(err){$('risk-result').replaceChildren(node('h3','Sem resultado confirmado'));$('risk-status').textContent=err.message||'Falha de comunicação. Confira o registro antes de repetir.';}
 finally{riskBusy=false;for(const el of riskForm.elements)el.disabled=false;}
}
riskForm.addEventListener('submit',riskRequest);$('validate-risk').addEventListener('click',e=>riskRequest(e,true));

let pendingReviews=[];
async function reviewApi(path,payload){
 const response=await fetch(path,payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}:{});
 if(!(response.headers.get('content-type')||'').includes('application/json'))throw Error('Servidor desatualizado. Reinicie o painel (HTTP '+response.status+').');
 const r=await response.json();if(!response.ok||!r.sucesso)throw Error(r.erro||'Operação não confirmada.');return r.dados;
}
function showPending(){
 const r=pendingReviews.find(r=>String(r.classificacao_id)===$('review-case').value);const box=$('review-detail');box.replaceChildren();
 if(!r){box.append(node('p','Nenhum caso selecionado.'));return;}
 box.append(node('h3','Classificação #'+r.classificacao_id+' · '+(r.paciente_ref||'Sem referência')));
 for(const [label,value] of Object.entries({'Idade':r.idade,'CID':r.diagnostico_principal,'Internações em 12 meses':r.internacoes_anteriores_12_meses,'Risco':r.risco_readmissao,'Estimativa':r.probabilidade_estimada==null?'Não disponível':(Number(r.probabilidade_estimada)*100).toFixed(1)+'%','Explicação':r.explicacao_texto||'Não disponível','Origem da explicação':r.explicacao_origem||'Não informada'}))box.append(node('p',label+': '+value));
}
async function refreshReviews(){
 $('review-refresh').disabled=true;
 try{const [users,cases]=await Promise.all([reviewApi('/api/usuarios'),reviewApi('/api/pendentes')]);
 const selected=$('review-user').value;$('review-user').replaceChildren(new Option('Selecione o revisor',''));for(const u of users.usuarios)$('review-user').append(new Option(u.nome+' ('+u.papel+')',u.usuario_id));$('review-user').value=selected;
 pendingReviews=cases.pendentes;$('review-case').replaceChildren(new Option('Selecione a classificação',''));for(const c of pendingReviews)$('review-case').append(new Option('#'+c.classificacao_id+' · '+(c.paciente_ref||'Sem referência')+' · '+c.risco_readmissao,c.classificacao_id));showPending();
 $('review-load-status').textContent=pendingReviews.length+' pendências exibidas (até 100).';
 }catch(e){$('review-load-status').textContent=e.message;}finally{$('review-refresh').disabled=false;}
}
$('review-refresh').onclick=refreshReviews;$('review-case').onchange=()=>{showPending();$('review-note').value='';};
$('review-form').onsubmit=async e=>{e.preventDefault();if(!$('review-form').reportValidity())return;const btn=$('review-save');btn.disabled=true;const payload={classificacao_id:Number($('review-case').value),usuario_id:Number($('review-user').value),parecer:$('review-verdict').value,observacao:$('review-note').value.trim()};
 try{const r=await reviewApi('/api/revisao',payload);$('review-status').textContent='Parecer '+payload.parecer+' registrado · revisão #'+r.revisao_id+' · classificação #'+payload.classificacao_id;await refreshReviews();}catch(e){$('review-status').textContent=e.message+' Confira o registro antes de reenviar.';}finally{btn.disabled=false;}
};
$('review-register').onsubmit=async e=>{e.preventDefault();const btn=$('review-register-button');btn.disabled=true;try{const r=await reviewApi('/api/usuarios',{nome:$('review-name').value.trim(),papel:$('review-role').value});await refreshReviews();$('review-user').value=String(r.usuario_id);$('review-status').textContent='Revisor cadastrado e selecionado.';}catch(e){$('review-status').textContent=e.message;}finally{btn.disabled=false;}};

function riskGauge(p){
 const ns='http://www.w3.org/2000/svg';
 function svgNode(tag,attrs,text){const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e;}
 const figure=node('figure',undefined,'risk-gauge');
 const percent=(p*100).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+'%';
 const svg=svgNode('svg',{viewBox:'0 0 260 165',role:'img','aria-label':'Estimativa demonstrativa de risco: '+percent+'. Escala de 0 a 100 por cento.'});
 function point(v,r=98){const a=Math.PI*(1-v);return [130+r*Math.cos(a),116-r*Math.sin(a)];}
 for(const [start,end,color] of [[0,.3,'#23846b'],[.3,.6,'#b57a13'],[.6,1,'#bc4853']]){
 const a=point(start),b=point(end);svg.append(svgNode('path',{d:'M '+a.join(' ')+' A 98 98 0 0 1 '+b.join(' '),fill:'none',stroke:color,'stroke-width':17}));}
 for(const v of [0,.3,.6,1]){const q=point(v,119);svg.append(svgNode('text',{x:q[0],y:q[1]+4,'text-anchor':'middle',class:'gauge-tick'},Math.round(v*100)));}
 const tip=point(p,80);svg.append(svgNode('line',{x1:130,y1:116,x2:tip[0],y2:tip[1],stroke:'#18343c','stroke-width':3,'stroke-linecap':'round'}),svgNode('circle',{cx:130,cy:116,r:6,fill:'#18343c'}),svgNode('text',{x:130,y:151,'text-anchor':'middle',class:'gauge-percent'},percent));
 figure.append(svg,node('figcaption','Estimativa do modelo sintético'));
 return figure;
}
