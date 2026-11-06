document.addEventListener("DOMContentLoaded",()=>{
 const menu=document.querySelector(".menu-toggle"),nav=document.querySelector(".main-nav");
 if(menu&&nav) menu.addEventListener("click",()=>nav.classList.toggle("open"));
 document.querySelectorAll("[data-copy]").forEach(btn=>btn.addEventListener("click",async()=>{
  const value=btn.dataset.copy||"";
  if(!value||value==="YOUR-SERVER-IP"){btn.innerHTML='<i class="bi bi-exclamation-circle"></i>';return}
  try{await navigator.clipboard.writeText(value);btn.innerHTML='<i class="bi bi-check2"></i>';setTimeout(()=>btn.innerHTML='<i class="bi bi-copy"></i>',1600)}
  catch(e){btn.innerHTML='<i class="bi bi-x"></i>'}
 }));
 const count=document.getElementById("online-count"),state=document.getElementById("server-state"),hero=document.getElementById("hero-online"),version=document.getElementById("version-label");
 if(state){
  fetch("/api/status").then(r=>r.json()).then(data=>{
   if(!data.configured){state.textContent="NOT SET";if(count)count.textContent="—";if(hero)hero.textContent="SERVER NOT SET";if(version)version.textContent="IP سرور هنوز تنظیم نشده است";return}
   if(data.online){state.textContent="ONLINE";if(count)count.textContent=data.players??0;if(hero)hero.textContent=(data.players??0)+" PLAYERS ONLINE";if(version)version.textContent=(data.version||"Minecraft")+" · ONLINE"}
   else{state.textContent="OFFLINE";if(count)count.textContent="۰";if(hero)hero.textContent="SERVER OFFLINE";if(version)version.textContent=data.message||"سرور در دسترس نیست"}
  }).catch(()=>{state.textContent="UNKNOWN";if(version)version.textContent="وضعیت سرور دریافت نشد"});
 }
});