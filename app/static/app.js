let kind = 'clientes';
let data = {};
const labels = {clientes:'Clientes',servicios:'Servicios',citas:'Citas',ingresos:'Ingresos',gastos:'Gastos'};
const money = n => new Intl.NumberFormat('es-ES',{style:'currency',currency:'EUR'}).format(n);
function render() {
  document.querySelector('#titulo').textContent = labels[kind];
  document.querySelectorAll('nav button').forEach(b => b.classList.toggle('active',b.dataset.kind === kind));
  const fields = document.querySelector('#campos');
  fields.replaceChildren();
  const add = (text,name,type,value='') => {const label=document.createElement('label');label.textContent=text;const input=document.createElement('input');Object.assign(input,{name,type,value,required:true});if(type==='number'){input.min='0';input.step='0.01';if(name!=='base')input.max='100';}label.append(input);fields.append(label);};
  if (['ingresos','gastos','citas'].includes(kind)) add('Fecha', 'fecha',kind==='citas'?'datetime-local':'date');
  if (['ingresos','gastos','servicios'].includes(kind)) {add('Base sin IVA (€)','base','number');add('IVA (%)','iva','number','21');add('Afectación a la actividad (%) · pendiente de revisión','afectacion','number','100');}
  if (['ingresos','gastos'].includes(kind)) add('Número de factura o referencia','factura','text');
  const list=document.querySelector('#lista'); list.replaceChildren();
  if (!data[kind]?.length) list.textContent='Todavía no hay registros. Añade el primero con el formulario.';
  (data[kind]||[]).forEach(row=>{const el=document.createElement('article');const title=document.createElement('strong');title.textContent=row.nombre;el.append(title);const detail=document.createElement('p');detail.textContent=[row.fecha,row.base!==undefined?money(Number(row.base))+' de base · IVA '+row.iva+' %':null,row.revision?'Revisión fiscal pendiente':null,row.notas].filter(Boolean).join(' · ');el.append(detail);list.append(el);});
  if(['ingresos','gastos'].includes(kind)){const a=document.createElement('a');a.href='/exportar/'+kind;a.download=kind+'.csv';a.textContent='Descargar CSV para Excel';list.append(a);}
}
async function load(){const response=await fetch('/api/registros');if(!response.ok)throw Error('No se pudieron cargar los datos');data=await response.json();const summary=document.querySelector('#resumen');summary.replaceChildren();for(const [label,value] of [['Clientes',String(data.clientes.length)],['Citas registradas',String(data.citas.length)],['Ingresos · base',money(data.ingresos.reduce((s,r)=>s+Number(r.base),0))],['Gastos · base',money(data.gastos.reduce((s,r)=>s+Number(r.base),0))]]){const card=document.createElement('article');const text=document.createElement('span');text.textContent=label;const amount=document.createElement('strong');amount.textContent=value;card.append(text,amount);summary.append(card);}render();}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{kind=b.dataset.kind;document.querySelector('#alta').reset();render();});
document.querySelector('#alta').onsubmit=async e=>{e.preventDefault();const message=document.querySelector('#mensaje');try{const response=await fetch('/api/'+kind,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(e.target)))});if(!response.ok)throw Error((await response.json()).error);e.target.reset();await load();message.textContent='Registro guardado.';}catch(err){message.textContent=err.message;}};
load().catch(err=>document.querySelector('#mensaje').textContent=err.message);
