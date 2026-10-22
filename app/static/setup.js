const setupForm = document.querySelector('#configuracion');
async function requestJSON(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const result = await response.json();
  if (!response.ok) throw Error(result.error || 'No se pudo completar la solicitud');
  return result;
}
function connectionStatus(profile) {
  const list = document.querySelector('#estado-conexiones');list.replaceChildren();
  for (const channel of ['gmail','chatgpt','whatsapp']) {
    const item=document.createElement('li');
    item.textContent=channel+': '+(profile?.canales.includes(channel)?'Solicitado · conexión real pendiente de implementar y autorizar':'No solicitado');list.append(item);
  }
}
async function loadSetup(){
  const result=await requestJSON('/api/configuracion');
  if(result.perfil){
    for(const [key,value] of Object.entries(result.perfil)){
      const field=setupForm.elements.namedItem(key);
      if(field && key!=='privado_confirmado')field.value=value;
    }
    // Renovar la declaración en cada guardado; no equivale a comprobar GitHub.
    setupForm.elements.privado_confirmado.checked=false;
    setupForm.querySelectorAll('[name=canal]').forEach(c=>c.checked=result.perfil.canales.includes(c.value));
    document.querySelector('#config-mensaje').textContent='Configuración local recuperada.';
  }
  connectionStatus(result.perfil);
}
setupForm.onsubmit=async event=>{
  event.preventDefault();const fields=new FormData(setupForm);const body=Object.fromEntries(fields);
  delete body.canal;body.canales=fields.getAll('canal');body.privado_confirmado=setupForm.elements.privado_confirmado.checked;
  try{const profile=await requestJSON('/api/configuracion',body);connectionStatus(profile);document.querySelector('#config-mensaje').textContent='Preferencias guardadas localmente. Ninguna cuenta está conectada todavía.';}
  catch(error){document.querySelector('#config-mensaje').textContent=error.message;}
};
async function loadEvents(){
  const rows=await requestJSON('/api/eventos');const list=document.querySelector('#eventos');list.replaceChildren();
  if(!rows.length)list.textContent='No hay entradas de prueba.';
  for(const row of rows){const article=document.createElement('article');const title=document.createElement('strong');title.textContent=row.canal+' · '+row.externo+' · Pendiente de revisión';const text=document.createElement('p');text.textContent=row.texto;article.append(title,text);list.append(article);}
}
document.querySelector('#simulador').onsubmit=async event=>{
  event.preventDefault();try{const result=await requestJSON('/api/eventos/simular',Object.fromEntries(new FormData(event.target)));document.querySelector('#evento-mensaje').textContent=result.duplicado?'Evento ya recibido: no se ha duplicado.':'Entrada de prueba guardada para revisión.';await loadEvents();}catch(error){document.querySelector('#evento-mensaje').textContent=error.message;}
};
loadSetup().catch(error=>document.querySelector('#config-mensaje').textContent=error.message);
loadEvents().catch(error=>document.querySelector('#evento-mensaje').textContent=error.message);
