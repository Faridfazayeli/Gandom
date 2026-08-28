const base=import.meta.env.VITE_API_URL||'/api/v1';
export async function api<T>(path:string,init:RequestInit={}){const token=localStorage.getItem('gandom_access');const r=await fetch(base+path,{...init,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{ }),...(init.headers||{})}});if(!r.ok){let m='Request failed';try{m=(await r.json()).detail||m}catch{}throw new Error(m)}return r.json() as Promise<T>}
export const login=(body:any)=>api('/auth/login',{method:'POST',body:JSON.stringify(body)});
export const register=(body:any)=>api('/auth/register',{method:'POST',body:JSON.stringify(body)});
