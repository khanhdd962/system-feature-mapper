'use strict';
const payload=JSON.parse(document.getElementById('map-data').textContent), data=payload.map;
const byId=new Map(data.features.map(f=>[f.id,f])), children=new Map(data.features.map(f=>[f.id,[]]));
for(const f of data.features)if(f.parentId!==null)children.get(f.parentId).push(f.id);
const expanded=new Set([data.rootId]), svg=document.getElementById('map'), viewport=document.getElementById('viewport');
let selected=null, positions=new Map(), transform={x:40,y:40,k:1};
const NS='http://www.w3.org/2000/svg', palette=['#288b9b','#7c68ad','#d78a45','#4b9a73','#b46887'];
function el(tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
function ancestry(id){const a=[];while(id){a.unshift(id);id=byId.get(id).parentId;}return a;}
function applyTransform(){viewport.setAttribute('transform',`translate(${transform.x} ${transform.y}) scale(${transform.k})`);}
function render(){
 const active=document.activeElement?.dataset?.nodeId;positions=new Map();let row=0;
 const stack=[{id:data.rootId,depth:0,color:'#288b9b',exit:false}];
 while(stack.length){const item=stack.pop(),{id,depth,color}=item, cs=expanded.has(id)?children.get(id):[];
  if(!item.exit){stack.push({...item,exit:true});for(let i=cs.length-1;i>=0;i--)stack.push({id:cs[i],depth:depth+1,color:depth===0?palette[i%palette.length]:color,exit:false});}
  else{const y=cs.length?(positions.get(cs[0]).y+positions.get(cs.at(-1)).y)/2:row++*76;positions.set(id,{x:depth*300,y,color});}
 }
 const edges=document.getElementById('edges'),nodes=document.getElementById('nodes');edges.replaceChildren();nodes.replaceChildren();
 for(const [id,p]of positions){const f=byId.get(id);if(f.parentId&&positions.has(f.parentId)){const q=positions.get(f.parentId);edges.append(el('path',{class:'edge',stroke:p.color,d:`M${q.x+236},${q.y+24} C${q.x+270},${q.y+24} ${p.x-40},${p.y+24} ${p.x},${p.y+24}`}));}
 const g=el('g',{class:'node'+(id===selected?' selected':''),transform:`translate(${p.x} ${p.y})`});
 const hit=el('g',{role:'button',tabindex:'0','aria-label':f.name,'data-node-id':id});hit.append(el('rect',{width:236,height:48,rx:10}),el('title',{},f.name),el('text',{x:14,y:29},f.name.length>26?f.name.slice(0,25)+'…':f.name));
 hit.addEventListener('click',()=>openFeature(id));hit.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openFeature(id);}if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();if(e.key==='ArrowRight')expanded.add(id);else expanded.delete(id);render();}if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();const a=[...positions.keys()],i=a.indexOf(id),next=a[i+(e.key==='ArrowDown'?1:-1)];focusNode(next);}});g.append(hit);
 if(children.get(id).length){const t=el('g',{class:'toggle',role:'button',tabindex:0,'aria-label':(expanded.has(id)?'Thu gọn ':'Mở ')+f.name,'aria-expanded':expanded.has(id),transform:'translate(249 24)'});t.append(el('circle',{r:10}),el('text',{'text-anchor':'middle',y:5},expanded.has(id)?'−':'+'));const toggle=()=>{expanded.has(id)?expanded.delete(id):expanded.add(id);render();};t.addEventListener('click',toggle);t.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();toggle();}});g.append(t);}nodes.append(g);
 }
 applyTransform();if(active)focusNode(active);
}
function focusNode(id){for(const n of document.querySelectorAll('[data-node-id]'))if(n.dataset.nodeId===id){n.focus();return n;}}
function reveal(id){for(const a of ancestry(id).slice(0,-1))expanded.add(a);selected=id;render();const p=positions.get(id);transform.x=svg.clientWidth/2-(p.x+118)*transform.k;transform.y=svg.clientHeight/2-(p.y+24)*transform.k;applyTransform();}
function fit(){const ps=[...positions.values()],w=Math.max(...ps.map(p=>p.x))+265,h=Math.max(...ps.map(p=>p.y))+60;transform.k=Math.max(.08,Math.min(1.3,(svg.clientWidth-60)/w,(svg.clientHeight-60)/h));transform.x=30;transform.y=(svg.clientHeight-h*transform.k)/2;applyTransform();}
function zoom(factor,x=svg.clientWidth/2,y=svg.clientHeight/2){const prev=transform.k,k=Math.max(.08,Math.min(3,prev*factor));transform.x=x-(x-transform.x)*k/prev;transform.y=y-(y-transform.y)*k/prev;transform.k=k;applyTransform();}
let drag=null;
svg.addEventListener('pointerdown',e=>{if(e.button!==0||e.target.closest('.node'))return;drag={x:e.clientX,y:e.clientY,tx:transform.x,ty:transform.y};svg.setPointerCapture(e.pointerId);svg.classList.add('dragging');});
svg.addEventListener('pointermove',e=>{if(!drag)return;transform.x=drag.tx+e.clientX-drag.x;transform.y=drag.ty+e.clientY-drag.y;applyTransform();});
for(const event of ['pointerup','pointercancel'])svg.addEventListener(event,()=>{drag=null;svg.classList.remove('dragging');});
svg.addEventListener('wheel',e=>{e.preventDefault();const r=svg.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.001),e.clientX-r.left,e.clientY-r.top);},{passive:false});
document.getElementById('zoom-in').onclick=()=>zoom(1.2);document.getElementById('zoom-out').onclick=()=>zoom(1/1.2);document.getElementById('fit').onclick=fit;
document.getElementById('reset').onclick=()=>{expanded.clear();expanded.add(data.rootId);render();fit();};document.getElementById('expand-all').onclick=()=>{for(const id of byId.keys())expanded.add(id);render();fit();};document.getElementById('collapse-all').onclick=()=>{expanded.clear();expanded.add(data.rootId);render();fit();};
function normalize(s){return s.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d');}
document.getElementById('search').addEventListener('input',e=>{const q=normalize(e.target.value.trim()),results=document.getElementById('results');results.replaceChildren(new Option('Chọn kết quả',''));let count=0;if(q)for(const f of data.features)if(normalize([f.name,f.shortDescription,...(f.aliases||[])].join(' ')).includes(q)){results.add(new Option(f.name,f.id));count++;}document.getElementById('result-count').textContent=q?`${count} kết quả`:'';});
document.getElementById('results').onchange=e=>{if(e.target.value)openFeature(e.target.value);};
document.getElementById('project-title').textContent=data.project.name;document.getElementById('project-description').textContent=data.project.description;document.title=data.project.name+' · Feature Map';
render();fit();window.addEventListener('resize',fit);
