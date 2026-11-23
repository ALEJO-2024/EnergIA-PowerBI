(function(){const a=document.createElement("link").relList;if(a&&a.supports&&a.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))s(t);new MutationObserver(t=>{for(const c of t)if(c.type==="childList")for(const l of c.addedNodes)l.tagName==="LINK"&&l.rel==="modulepreload"&&s(l)}).observe(document,{childList:!0,subtree:!0});function o(t){const c={};return t.integrity&&(c.integrity=t.integrity),t.referrerPolicy&&(c.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?c.credentials="include":t.crossOrigin==="anonymous"?c.credentials="omit":c.credentials="same-origin",c}function s(t){if(t.ep)return;t.ep=!0;const c=o(t);fetch(t.href,c)}})();const oe=["Residencial","Industrial","Comercial","Oficial","Otros"],z=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];function v(e,a=0){return new Intl.NumberFormat("es-CO",{minimumFractionDigits:a,maximumFractionDigits:a}).format(e)}function A(e,a=0){return"$ "+v(e,a)}function w(e,a){return a?e.filter(o=>o.periodo===a):e}function R(e){return e?"en "+z[Number(e.slice(5))-1].toLowerCase()+" de 2021":"en 2021"}const se="energia-tema",re={tinta:"#102033",linea:"rgba(16, 32, 51, 0.12)",teal:"#0b7a68",marca:"rgba(11, 122, 104, 0.7)",punto:"rgba(11, 122, 104, 0.9)",rain:"#2f6f9e",gold:"#a67c2d",coral:"#c45d56"},ce={tinta:"#f7fafc",linea:"rgba(158, 188, 214, 0.16)",teal:"#2ee6c8",marca:"rgba(46, 230, 200, 0.55)",punto:"rgba(46, 230, 200, 0.85)",rain:"#9fd4ff",gold:"#e7c27a",coral:"#e08b84"};function ee(){return document.documentElement.dataset.tema==="dark"?"dark":"light"}function le(e){document.documentElement.dataset.tema=e,localStorage.setItem(se,e)}function ie(){const e=ee()==="dark"?"light":"dark";return le(e),e}function g(){return ee()==="dark"?ce:re}const P=document.createElement("div");P.className="tooltip";document.body.appendChild(P);function ue(e,a,o){P.style.display="block",P.textContent=o;const s=14,t=P.offsetWidth,c=P.offsetHeight,l=Math.min(e+s,window.innerWidth-t-8),i=Math.min(a+s,window.innerHeight-c-8);P.style.left=l+"px",P.style.top=i+"px"}function te(){P.style.display="none"}function B(e,a){var c;const o=((c=e.parentElement)==null?void 0:c.clientWidth)??640,s=Math.min(window.devicePixelRatio||1,2);e.width=Math.floor(o*s),e.height=Math.floor(a*s),e.style.width="100%",e.style.height=a+"px";const t=e.getContext("2d");if(!t)throw new Error("El navegador no dibujó el gráfico");return t.setTransform(s,0,0,s,0,0),t.clearRect(0,0,o,a),t.font="12px IBM Plex Sans",{ctx:t,ancho:o,alto:a}}function I(e){const a=Math.abs(e);return a>=1e6?(e/1e6).toFixed(1).replace(".",",")+" M":a>=1e4?Math.round(e/1e3)+" mil":a>=1e3?(e/1e3).toFixed(1).replace(".",",")+" mil":String(Math.round(e))}function Y(e,a){e.onmousemove=o=>{const s=e.getBoundingClientRect(),t=o.clientX-s.left,c=o.clientY-s.top,l=a.find(i=>t>=i.x&&t<=i.x+i.w&&c>=i.y&&c<=i.y+i.h);if(!l){te();return}ue(o.clientX,o.clientY,l.texto)},e.onmouseleave=te}function N(e,a,o,s=250,t={}){var L;const c=g(),l=t.ejesSeparados??!1,i=t.desdeCero??!0,{ctx:n,ancho:p}=B(e,s),m={l:58,r:l?58:12,t:16,b:28},r=o.map(b=>Math.max(...b.valores,1)),u=o.map(b=>i?0:Math.min(...b.valores)),f=Math.max(...r),d=i?0:Math.min(...u),h=Math.max(a.length,1),E=(p-m.l-m.r)/Math.max(h-1,1),T=s-m.b,C=s-m.t-m.b,j=(b,y)=>{const M=l?r[y]:f,S=l?u[y]:d;return T-(b-S)/(M-S||1)*C};n.strokeStyle=c.linea;for(let b=0;b<4;b++){const y=m.t+C*b/3;n.beginPath(),n.moveTo(m.l,y),n.lineTo(p-m.r,y),n.stroke();const M=1-b/3;n.fillStyle=((L=o[0])==null?void 0:L.color)??c.tinta;const S=l?u[0]+(r[0]-u[0])*M:d+(f-d)*M;n.fillText(I(S),4,y+4),l&&o[1]&&(n.fillStyle=o[1].color,n.fillText(I(u[1]+(r[1]-u[1])*M),p-m.r+8,y+4))}if(n.fillStyle=c.tinta,a.forEach((b,y)=>{h>12&&y%2||n.fillText(b,m.l+y*E-8,s-8)}),t.marca!=null&&t.marca>=0){const b=m.l+t.marca*E;n.save(),n.strokeStyle=c.marca,n.setLineDash([3,4]),n.beginPath(),n.moveTo(b,m.t),n.lineTo(b,T),n.stroke(),n.restore()}o.forEach((b,y)=>{n.beginPath(),n.strokeStyle=b.color,n.lineWidth=2,b.valores.forEach((M,S)=>{const F=m.l+S*E,W=j(M,y);S===0?n.moveTo(F,W):n.lineTo(F,W)}),n.stroke(),b.valores.forEach((M,S)=>{const F=m.l+S*E,W=j(M,y);n.fillStyle=b.color,n.beginPath(),n.arc(F,W,S===t.marca?5:3,0,Math.PI*2),n.fill()})});const q=a.map((b,y)=>({x:m.l+y*E-E/2,y:m.t,w:E,h:C,texto:`${b}
${o.map(M=>{var S;return`${M.nombre}: ${((S=M.detalle)==null?void 0:S[y])??I(M.valores[y])}`}).join(`
`)}`}));Y(e,q)}function O(e,a,o,s,t=250){const c=g(),l=s??c.teal,{ctx:i,ancho:n}=B(e,t),p={l:58,r:12,t:16,b:36},m=Math.max(1,...o),r=o.length||1,u=(n-p.l-p.r)/r,f=t-p.b,d=t-p.t-p.b;i.fillStyle=c.tinta,i.fillText(I(m),4,p.t+8);const h=o.map((E,T)=>{const C=E/m*d,j=p.l+T*u+u*.18,q=u*.64,L=f-C;return i.fillStyle=l,i.fillRect(j,L,q,C),i.fillStyle=c.tinta,i.fillText(a[T],j,t-16),{x:j,y:p.t,w:q,h:d,texto:`${a[T]}
${I(E)}`}});Y(e,h)}function de(e,a,o,s=250){const t=g(),{ctx:c,ancho:l}=B(e,s),i={l:48,r:12,t:16,b:36},n=a.map((h,E)=>o.reduce((T,C)=>T+C.valores[E],0)),p=Math.max(1,...n),m=a.length||1,r=(l-i.l-i.r)/m,u=s-i.b,f=s-i.t-i.b,d=a.map((h,E)=>{let T=u;const C=i.l+E*r+r*.18,j=r*.64;for(const L of o){const b=L.valores[E]/p*f;T-=b,c.fillStyle=L.color,c.fillRect(C,T,j,b)}c.fillStyle=t.tinta,c.fillText(h,C,s-16);const q=o.map(L=>`${L.nombre}: ${L.valores[E]}`).join(`
`);return{x:C,y:i.t,w:j,h:f,texto:`${h}
${q}`}});Y(e,d)}function pe(e,a,o=280){const s=g(),{ctx:t,ancho:c}=B(e,o),l={l:40,r:16,t:16,b:32},i=Math.max(10,...a.map(u=>u.x)),n=Math.max(1,...a.map(u=>u.y)),p=c-l.l-l.r,m=o-l.t-l.b;t.strokeStyle=s.linea,t.beginPath(),t.moveTo(l.l,l.t),t.lineTo(l.l,o-l.b),t.lineTo(c-l.r,o-l.b),t.stroke(),t.fillStyle=s.tinta,t.fillText("antigüedad",c-88,o-10),t.fillText("fallas",4,14);const r=a.map(u=>{const f=l.l+u.x/i*p,d=o-l.b-u.y/n*m;return t.fillStyle=s.punto,t.beginPath(),t.arc(f,d,4,0,Math.PI*2),t.fill(),{x:f-6,y:d-6,w:12,h:12,texto:u.texto}});Y(e,r)}function x(e){return e.reduce((a,o)=>a+o,0)}function $(e,a,o){return`<article class="kpi"><p class="etiqueta">${e}</p><strong>${a}</strong><em>${o}</em></article>`}function ae(e){return`<div class="leyenda">${e.map(a=>`<span><i style="background:${a.color}"></i>${a.nombre}</span>`).join("")}</div>`}function k(e){const a=document.getElementById(e);if(!(a instanceof HTMLCanvasElement))throw new Error("Falta el gráfico "+e);return a}function _(e,a,o){return Array.from({length:24},(s,t)=>{const c=w(e.consumo.por_hora,a).filter(n=>n.tipo===o&&n.hora===t),l=x(c.map(n=>n.kwh)),i=x(c.map(n=>n.n));return i?l/i:0})}function ne(e,a){if(!a)return null;const o=e.periodos.indexOf(a);return o<0?null:o}function J(e){const a=Math.max(...e,1e-4);return e.map(o=>o/a*100)}function X(e){return e.map(a=>v(a,2)+" kWh")}function me(e,a,o){const s=_(e,a,o);let t=0;return s.forEach((c,l)=>{c>s[t]&&(t=l)}),{hora:t,promedio:s[t]}}function fe(e,a){const o=w(e.consumo.por_tipo,a),s=x(o.map(u=>u.kwh)),t=oe.map(u=>x(o.filter(f=>f.tipo===u).map(f=>f.kwh))),c=[1,2,3,4,5,6].map(u=>x(w(e.consumo.por_estrato,a).filter(f=>f.estrato===u).map(f=>f.kwh))),l=me(e,a,"Residencial"),i=document.querySelector("#pagina");if(!i)return;i.innerHTML=`
    <p class="historia">La energía medida ${R(a)} no es una línea plana. En una casa pesa el final de la tarde. El estrato 3 suma más kWh que el 2, aunque hay más cuentas en el 2: cada casa de estrato alto gasta más, y el total lo mueven las cuentas del medio. Esta página mira el medidor, no la factura.</p>
    <section class="kpis">
      ${$("kWh medidos",v(s,0),"Suma de la muestra")}
      ${$("Por cliente",v(s/e.corte.clientes,0)+" kWh",v(e.corte.clientes)+" cuentas")}
      ${$("Hora residencial más alta",l.hora+":00",v(l.promedio,2)+" kWh promedio")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Consumo mes a mes</h2><canvas id="g-mes"></canvas></article>
      <article class="panel"><h2>Quién consume</h2><canvas id="g-tipo"></canvas></article>
    </section>
    <section class="rejilla igual">
      <article class="panel"><h2>Forma del día</h2>
        <p class="eje-nota">100 es la hora más alta de cada tipo. El residencial sube al anochecer; el industrial se mantiene de día.</p>
        ${ae([{nombre:"Residencial",color:g().teal},{nombre:"Comercial",color:g().rain},{nombre:"Industrial",color:g().gold}])}<canvas id="g-hora"></canvas></article>
      <article class="panel"><h2>Residencial por estrato</h2><canvas id="g-estrato"></canvas></article>
    </section>
    <p class="nota">Muestra de ${v(e.corte.clientes)} clientes en Medellín. No son los ${v(e.corte.suscriptores_publicados)} suscriptores que publicó el SUI, y estos kWh no se suman con los de la factura.</p>`;const n=e.periodos.map(u=>z[Number(u.slice(5))-1]);N(k("g-mes"),n,[{nombre:"kWh",color:g().teal,valores:e.periodos.map(u=>x(w(e.consumo.por_tipo,u).map(f=>f.kwh)))}],250,{marca:ne(e,a)}),O(k("g-tipo"),["Resid.","Indust.","Comerc.","Oficial","Otros"],t);const p=_(e,a,"Residencial"),m=_(e,a,"Comercial"),r=_(e,a,"Industrial");N(k("g-hora"),Array.from({length:24},(u,f)=>String(f)),[{nombre:"Residencial",color:g().teal,valores:J(p),detalle:X(p)},{nombre:"Comercial",color:g().rain,valores:J(m),detalle:X(m)},{nombre:"Industrial",color:g().gold,valores:J(r),detalle:X(r)}]),O(k("g-estrato"),["E1","E2","E3","E4","E5","E6"],c)}function he(e,a){const o=w(e.factura.por_mes,a),s=x(o.map(d=>d.valor)),t=x(o.map(d=>d.kwh)),c=x(o.map(d=>d.pagada)),l=x(o.map(d=>d.pendiente)),i=x(o.map(d=>d.mora)),n=document.querySelector("#pagina");if(!n)return;n.innerHTML=`
    <p class="historia">Cada cliente tiene una sola cuenta por mes. Esa cuenta es la suma de sus horas, multiplicada por el precio que EPM publicó. El valor puede subir aunque el medidor no lo haga, si la tarifa de ese mes subió.</p>
    <section class="kpis cinco">
      ${$("Valor facturado",A(s),R(a))}
      ${$("kWh facturados",v(t,0),"Ya incluye las horas del mes")}
      ${$("Pagadas",v(c),"Cuentas al día")}
      ${$("Pendientes",v(l),"Sin pago registrado")}
      ${$("En mora",v(i),"Pasaron la fecha")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Valor por mes</h2><canvas id="g-valor"></canvas></article>
      <article class="panel"><h2>Valor por tipo de cliente</h2><canvas id="g-tipo-valor"></canvas></article>
    </section>
    <article class="panel ancho"><h2>Precio medio de la muestra</h2><canvas id="g-tarifa"></canvas></article>
    <article class="panel ancho"><h2>Estado de las cuentas</h2>${ae([{nombre:"Pagada",color:g().teal},{nombre:"Pendiente",color:g().gold},{nombre:"En mora",color:g().coral}])}<canvas id="g-estado"></canvas></article>
    <p class="nota">El cliente C0001, en enero, midió 145,9701 kWh y su factura trae ese mismo número, a 573,05 pesos el kWh de estrato 1. El precio medio de arriba mezcla todos los estratos de la muestra.</p>`;const p=e.periodos,m=p.map(d=>z[Number(d.slice(5))-1]),r=d=>e.factura.por_mes.find(h=>h.periodo===d),u={marca:ne(e,a)};N(k("g-valor"),m,[{nombre:"Pesos",color:g().teal,valores:p.map(d=>{var h;return((h=r(d))==null?void 0:h.valor)??0})}],250,u),N(k("g-tarifa"),m,[{nombre:"Pesos / kWh",color:g().rain,valores:p.map(d=>{var h;return((h=r(d))==null?void 0:h.tarifa)??0})}],250,{...u,desdeCero:!1});const f=oe.map(d=>x(w(e.factura.por_tipo,a).filter(h=>h.tipo===d).map(h=>h.valor)));O(k("g-tipo-valor"),["Resid.","Indust.","Comerc.","Oficial","Otros"],f,g().rain),de(k("g-estado"),m,[{nombre:"Pagada",color:g().teal,valores:p.map(d=>{var h;return((h=r(d))==null?void 0:h.pagada)??0})},{nombre:"Pendiente",color:g().gold,valores:p.map(d=>{var h;return((h=r(d))==null?void 0:h.pendiente)??0})},{nombre:"En mora",color:g().coral,valores:p.map(d=>{var h;return((h=r(d))==null?void 0:h.mora)??0})}])}function be(e){const a=new Map;for(const o of e)a.set(o.cuando,(a.get(o.cuando)??0)+1);return[...a.entries()].map(([o,s])=>({cuando:o,n:s})).sort((o,s)=>s.n-o.n)}function ge(e){const a=new Map;for(const n of e){const p=a.get(n.activo)??{lat:n.lat,lon:n.lon,n:0,tipo:n.tipo};p.n+=1,a.set(n.activo,p)}const o=[...a.values()];if(!o.length)return'<p class="nota">No hay fallas en este mes.</p>';const s=Math.min(...o.map(n=>n.lat)),t=Math.max(...o.map(n=>n.lat)),c=Math.min(...o.map(n=>n.lon)),l=Math.max(...o.map(n=>n.lon));return`<svg class="mapa" viewBox="0 0 640 340" role="img" aria-label="Mapa de fallas en Medellín">${o.map(n=>{const p=40+(n.lon-c)/(l-c||1)*560,m=300-(n.lat-s)/(t-s||1)*250,r=4+Math.min(n.n,12);return`<circle class="punto" cx="${p.toFixed(1)}" cy="${m.toFixed(1)}" r="${r}"><title>${n.tipo}: ${n.n} fallas</title></circle>`}).join("")}</svg>`}function ve(e,a){var l;const o=w(e.fallas,a),s=be(o).slice(0,5),t=((l=s[0])==null?void 0:l.n)??1,c=document.querySelector("#pagina");c&&(c.innerHTML=`
    <p class="historia">Cada falla cae sobre un equipo que ya está dentro de Medellín. El mapa muestra dónde se juntan. El ranking ordena las horas con más eventos: es una lista, no un pronóstico. La lluvia va en el gráfico de abajo, una vez por mes, no dentro de cada falla.</p>
    <section class="kpis">
      ${$("Fallas",v(o.length),R(a))}
      ${$("Clientes alcanzados",v(x(o.map(i=>i.afectados))),"Suma de cada evento")}
      ${$("Minutos",v(x(o.map(i=>i.minutos))),"Duración acumulada")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Dónde ocurrieron</h2>${ge(o)}</article>
      <article class="panel"><h2>Horas con más fallas</h2>
        <ol class="lista">${s.map(i=>`<li><span>${i.cuando.slice(5,16)}</span><span class="barra"><span style="width:${i.n/t*100}%"></span></span><strong>${i.n}</strong></li>`).join("")}</ol>
      </article>
    </section>
    <article class="panel ancho"><h2>Lluvia del mes y número de fallas</h2>${ae([{nombre:"Fallas",color:g().teal},{nombre:"Lluvia, mm",color:g().rain}])}<canvas id="g-lluvia"></canvas></article>
    <p class="nota">Un mes con muchas fallas cuenta la lluvia una sola vez. La falla F00001, el 3 de marzo a la 01:00, afectó a 38 clientes durante 129 minutos. Esa hora no tuvo lluvia.</p>`,N(k("g-lluvia"),z,[{nombre:"Fallas",color:g().teal,valores:e.periodos.map(i=>e.fallas.filter(n=>n.periodo===i).length)},{nombre:"Lluvia mm",color:g().rain,valores:e.periodos.map(i=>{var n;return((n=e.lluvia.find(p=>p.periodo===i))==null?void 0:n.mm)??0})}],250,{ejesSeparados:!0}))}function ye(e,a){const o=w(e.fallas,a),s=w(e.mantenimiento,a),t=x(s.map(r=>r.costo)),c=x(s.filter(r=>r.tipo==="preventivo").map(r=>r.costo)),l=x(s.filter(r=>r.tipo==="correctivo").map(r=>r.costo)),i=["poste","transformador","linea","proteccion","subestacion"].map(r=>o.filter(u=>u.tipo===r).length),n=new Map;for(const r of o)n.set(r.activo,(n.get(r.activo)??0)+1);const p=[...n.entries()].sort((r,u)=>u[1]-r[1]).slice(0,5),m=document.querySelector("#pagina");m&&(m.innerHTML=`
    <p class="historia">Los ${v(e.corte.activos)} equipos no fallan igual. Un transformador viejo puede cargar más eventos que un poste nuevo. El mantenimiento es otra cuenta: un preventivo por equipo y un correctivo después de parte de las fallas.</p>
    <section class="kpis">
      ${$("Costo de atender",A(t),R(a))}
      ${$("Preventivo",A(c),"Trabajo programado")}
      ${$("Correctivo",A(l),"Después de una falla")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Fallas por tipo de equipo</h2><canvas id="g-equipo"></canvas></article>
      <article class="panel"><h2>Edad y número de fallas</h2><canvas id="g-edad"></canvas></article>
    </section>
    <article class="panel ancho"><h2>Equipos con más eventos</h2>
      <ol class="lista">${p.map(([r,u])=>{const f=e.equipos.find(d=>d.id===r);return`<li><span>${r}</span><span>${(f==null?void 0:f.tipo)??""} · ${(f==null?void 0:f.edad)??""} años</span><strong>${u}</strong></li>`}).join("")}</ol>
    </article>
    <p class="nota">El equipo no se une a un cliente. El estado en esta corrida es “en servicio”: la página ordena por lo que ya falló, no anuncia el próximo daño.</p>`,O(k("g-equipo"),["Poste","Transf.","Línea","Protec.","Subest."],i),pe(k("g-edad"),e.equipos.map(r=>({x:r.edad,y:n.get(r.id)??0,texto:`${r.id}
${r.tipo}, ${r.edad} años
${n.get(r.id)??0} fallas`}))))}function xe(e,a){var i;const o=a?Number(a.slice(5)):1,s=((i=e.contexto.tarifa.find(n=>n.mes===o))==null?void 0:i.precio)??0,t=e.contexto.sui.estratos,c=Math.max(...t.map(n=>n.usuarios)),l=document.querySelector("#pagina");l&&(l.innerHTML=`
    <p class="historia">Esta página no habla de un cliente de la muestra. Habla del municipio. Los habitantes, los suscriptores y el precio del kWh se miran juntos y no se suman entre sí. Tampoco se reparten entre las 1.000 cuentas de las páginas anteriores.</p>
    <section class="kpis">
      ${$("Habitantes",v(e.contexto.habitantes.total),"DANE, área Total, 2021")}
      ${$("Suscriptores",v(e.contexto.sui.suscriptores),"SUI, EPM, año 2021")}
      ${$("Tarifa estrato 1",A(s,2),a?R(a):"Enero, por encima de subsistencia")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Suscriptores por estrato</h2>
        <ol class="lista">${t.map(n=>`<li><span>E${n.estrato}</span><span class="barra"><span style="width:${n.usuarios/c*100}%"></span></span><strong>${v(n.usuarios)}</strong></li>`).join("")}</ol>
      </article>
      <article class="panel"><h2>Resto de cuentas</h2><canvas id="g-otros"></canvas></article>
    </section>
    <article class="panel ancho"><h2>Precio publicado por EPM en 2021</h2><canvas id="g-precio"></canvas></article>
    <p class="nota">Contexto publicado. La cabecera tiene ${v(e.contexto.habitantes.cabecera)} habitantes y el resto del municipio ${v(e.contexto.habitantes.resto)}. Esas dos cifras ya están dentro del total. La tarifa no tiene municipio.</p>`,O(k("g-otros"),e.contexto.sui.otros.map(n=>n.tipo),e.contexto.sui.otros.map(n=>n.usuarios)),N(k("g-precio"),z,[{nombre:"Pesos / kWh",color:g().teal,valores:e.contexto.tarifa.map(n=>n.precio)}],250,{desdeCero:!1,marca:a?Number(a.slice(5))-1:null}))}const H=[];let K=!1;function $e(e,a){const o=document.createElement("p");o.className="chat-burbuja "+a.rol,o.textContent=a.texto,e.appendChild(o),e.scrollTop=e.scrollHeight}async function Q(e,a){const o=a.value.trim();if(!o||K)return;a.value="",H.push({rol:"usuario",texto:o}),$e(e,H[H.length-1]),K=!0;const s=document.createElement("p");s.className="chat-burbuja asistente",s.textContent="Revisando las cifras…",e.appendChild(s),e.scrollTop=e.scrollHeight;try{const t=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({mensajes:H.slice(-8).map(i=>({rol:i.rol,texto:i.texto}))})}),c=await t.json(),l=t.ok?c.respuesta||"No hubo respuesta.":c.detail||"No se pudo consultar.";H.push({rol:"asistente",texto:l}),s.textContent=l}catch{const t="No se pudo consultar. Revisa que el tablero siga encendido.";H.push({rol:"asistente",texto:t}),s.textContent=t}finally{K=!1,e.scrollTop=e.scrollHeight,a.focus()}}function Ee(){var m;if(document.querySelector(".chat"))return;const e=document.createElement("div");e.className="chat",e.innerHTML=`
    <button type="button" class="chat-abrir" aria-expanded="false">Consulta</button>
    <section class="chat-panel" hidden>
      <header class="chat-cabecera">
        <div>
          <p>EnergIA</p>
          <strong>Consulta del negocio</strong>
        </div>
        <button type="button" class="chat-cerrar" aria-label="Cerrar">Cerrar</button>
      </header>
      <div class="chat-lista"></div>
      <div class="chat-ideas"></div>
      <form class="chat-forma">
        <textarea rows="2" maxlength="1500" placeholder="Pregunta sobre Medellín 2021"></textarea>
        <button type="submit">Enviar</button>
      </form>
    </section>`,document.body.appendChild(e);const a=e.querySelector(".chat-abrir"),o=e.querySelector(".chat-panel"),s=e.querySelector(".chat-lista"),t=e.querySelector(".chat-ideas"),c=e.querySelector(".chat-forma"),l=e.querySelector("textarea");if(!a||!o||!s||!t||!c||!l)return;const i=["¿Qué pasó con la cuenta en enero?","¿El estrato 3 midió más que el 2?"];for(const r of i){const u=document.createElement("button");u.type="button",u.textContent=r,u.addEventListener("click",()=>{l.value=r,Q(s,l)}),t.appendChild(u)}const n=document.createElement("p");n.className="chat-nota",n.textContent="Lee la base del proyecto y solo responde sobre el servicio eléctrico de Medellín en 2021.",s.appendChild(n);const p=r=>{o.hidden=!r,a.setAttribute("aria-expanded",r?"true":"false"),r&&l.focus()};a.addEventListener("click",()=>p(o.hidden)),(m=e.querySelector(".chat-cerrar"))==null||m.addEventListener("click",()=>p(!1)),c.addEventListener("submit",r=>{r.preventDefault(),Q(s,l)}),l.addEventListener("keydown",r=>{r.key==="Enter"&&!r.shiftKey&&(r.preventDefault(),Q(s,l))})}const G=[{id:"medidor",numero:"01",nombre:"Medidor",dibujar:fe},{id:"cuenta",numero:"02",nombre:"Cuenta",dibujar:he},{id:"fallas",numero:"03",nombre:"Fallas",dibujar:ve},{id:"equipos",numero:"04",nombre:"Equipos",dibujar:ye},{id:"contexto",numero:"05",nombre:"Contexto",dibujar:xe}];let U=null,Z="medidor",D=null;async function Me(){const e=document.querySelector("#app");if(!e)return;e.innerHTML='<p class="estado">Cargando el año de Medellín…</p>';const a=await fetch("/api/resumen");if(!a.ok){e.innerHTML='<p class="estado">No se pudo leer el resumen. Revisa que la API esté encendida.</p>';return}U=await a.json(),V(),Ee()}function V(){var s;const e=document.querySelector("#app");if(!e||!U)return;const a=ee()==="dark"?"Vista clara":"Vista oscura";e.innerHTML=`
    <main class="marco">
      <header class="cabecera">
        <div>
          <p class="ceja">EnergIA · Business intelligence</p>
          <h1>Medellín, un año de servicio</h1>
          <p class="bajada">2021, código 05001. Consumo, cuenta, fallas y el municipio que publican el DANE, el SUI y EPM.</p>
        </div>
        <button type="button" class="tema" id="tema">${a}</button>
      </header>
      <nav class="nav">${G.map(t=>`<button type="button" data-pagina="${t.id}" class="${t.id===Z?"activa":""}"><strong>${t.numero}</strong><span>${t.nombre}</span></button>`).join("")}</nav>
      <div class="filtros">
        <button type="button" data-periodo="" class="${D===null?"activa":""}">Año</button>
        ${U.periodos.map(t=>`<button type="button" data-periodo="${t}" class="${D===t?"activa":""}">${z[Number(t.slice(5))-1]}</button>`).join("")}
      </div>
      <section id="pagina"></section>
    </main>`,(s=document.querySelector("#tema"))==null||s.addEventListener("click",()=>{ie(),V()}),e.querySelectorAll("[data-pagina]").forEach(t=>{t.addEventListener("click",()=>{Z=t.dataset.pagina??"medidor",V()})}),e.querySelectorAll("[data-periodo]").forEach(t=>{t.addEventListener("click",()=>{D=t.dataset.periodo||null,V()})}),(G.find(t=>t.id===Z)??G[0]).dibujar(U,D)}Me();
