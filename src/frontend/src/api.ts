import type {Deviation,SiteRisk} from './types';
const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000';
async function get<T>(path:string):Promise<T>{const r=await fetch(`${BASE}${path}`);if(!r.ok)throw new Error(await r.text());return r.json()}
export const api={risks:()=>get<SiteRisk[]>('/sites/risk'),deviations:(query='')=>get<Deviation[]>(`/deviations?limit=300&${query}`),
async allDeviations(){const records:Deviation[]=[];for(let offset=0;;offset+=1000){const batch=await get<Deviation[]>(`/deviations?limit=1000&offset=${offset}`);records.push(...batch);if(batch.length<1000)return records;}},
async capa(deviation_id:string,format='pdf'){const r=await fetch(`${BASE}/capa/generate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({deviation_id,format})});if(!r.ok)throw new Error(await r.text());if(format==='markdown')return r.json();const blob=await r.blob();const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=`CAPA-${deviation_id}.${format}`;a.click();URL.revokeObjectURL(u)}};
