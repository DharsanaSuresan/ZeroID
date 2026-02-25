// import React, { useState, useEffect } from "react";
// import {
//   CheckCircle, XCircle, Shield, LogOut, Loader2,
//   AlertTriangle, ExternalLink, RefreshCw, Copy,
// } from "lucide-react";

// const API_BASE = "http://127.0.0.1:8000";

// async function api(url, method = "GET", body = null, auth = true) {
//   const headers = {};
//   if (auth) {
//     const token = localStorage.getItem("access");
//     if (token) headers.Authorization = `Bearer ${token}`;
//   }
//   const options = { method, headers };
//   if (body) {
//     if (body instanceof FormData) options.body = body;
//     else { headers["Content-Type"] = "application/json"; options.body = JSON.stringify(body); }
//   }
//   const res = await fetch(API_BASE + url, options);
//   if (!res.ok) { const t = await res.text(); throw new Error(t || "API Error"); }
//   return res.json();
// }

// const CertAPI = {
//   list:   ()              => api("/certificates/"),
//   create: (holderName, title, file) => {
//     const fd = new FormData();
//     fd.append("holder_name", holderName);
//     fd.append("title", title);
//     fd.append("certificate_file", file);
//     return api("/certificates/", "POST", fd);
//   },
//   revoke: (id, reason)   => api("/revoke/", "POST", { certificate_id: id, reason: reason || "Revoked by issuer" }),
//   verify: (id)           => api("/verify/", "POST", { certificate_id: id }, false),
// };

// /* ── small helpers ── */
// function Badge({ valid, revoked }) {
//   if (valid)    return <span style={styles.badgeGreen}>✓ Valid</span>;
//   if (revoked)  return <span style={styles.badgeRed}>✕ Revoked</span>;
//   return              <span style={styles.badgeYellow}>⚠ Invalid</span>;
// }

// function CopyBtn({ text }) {
//   const [ok, setOk] = useState(false);
//   return (
//     <button style={styles.copyBtn} title="Copy"
//       onClick={() => { navigator.clipboard.writeText(text); setOk(true); setTimeout(()=>setOk(false),1500); }}>
//       {ok ? <CheckCircle size={12} color="#16a34a"/> : <Copy size={12}/>}
//     </button>
//   );
// }

// /* ── styles object (plain CSS-in-JS, no Tailwind needed) ── */
// const C = {
//   bg:       "#f8fafc",
//   white:    "#ffffff",
//   border:   "#e2e8f0",
//   text:     "#1e293b",
//   muted:    "#64748b",
//   accent:   "#4f46e5",
//   green:    "#16a34a",
//   red:      "#dc2626",
//   yellow:   "#d97706",
//   greenBg:  "#f0fdf4",
//   redBg:    "#fef2f2",
//   yellowBg: "#fffbeb",
// };

// const styles = {
//   page:       { minHeight:"100vh", background:C.bg, fontFamily:"system-ui,sans-serif", color:C.text },
//   header:     { background:C.white, borderBottom:`1px solid ${C.border}`, padding:"14px 24px", display:"flex", alignItems:"center", justifyContent:"space-between" },
//   headerLeft: { display:"flex", alignItems:"center", gap:10 },
//   logo:       { fontWeight:700, fontSize:18, color:C.text, letterSpacing:"-0.02em" },
//   roleTag:    { fontSize:12, padding:"3px 10px", borderRadius:20, background:"#eef2ff", color:C.accent, fontWeight:600, textTransform:"capitalize" },
//   logoutBtn:  { display:"flex", alignItems:"center", gap:6, fontSize:13, color:C.muted, background:"none", border:"none", cursor:"pointer", padding:"6px 10px", borderRadius:8 },
//   main:       { maxWidth:820, margin:"0 auto", padding:"28px 20px" },
//   card:       { background:C.white, border:`1px solid ${C.border}`, borderRadius:12, padding:24, marginBottom:20 },
//   cardTitle:  { fontSize:16, fontWeight:600, marginBottom:16, color:C.text },
//   label:      { fontSize:12, fontWeight:600, color:C.muted, marginBottom:5, display:"block", textTransform:"uppercase", letterSpacing:".04em" },
//   input:      { width:"100%", border:`1px solid ${C.border}`, borderRadius:8, padding:"9px 12px", fontSize:14, outline:"none", color:C.text, background:C.white, boxSizing:"border-box" },
//   row:        { display:"grid", gridTemplateColumns:"1fr 1fr", gap:14, marginBottom:14 },
//   btn:        { display:"inline-flex", alignItems:"center", gap:7, padding:"9px 18px", borderRadius:8, fontSize:14, fontWeight:500, cursor:"pointer", border:"none", transition:"opacity .15s" },
//   btnPrimary: { background:C.accent, color:"#fff" },
//   btnDanger:  { background:"none", color:C.red, border:`1px solid #fca5a5` },
//   btnGhost:   { background:"none", color:C.muted, border:`1px solid ${C.border}` },
//   btnCyan:    { background:"#0284c7", color:"#fff" },
//   btnDis:     { opacity:.5, cursor:"not-allowed" },
//   certCard:   { border:`1px solid ${C.border}`, borderRadius:10, padding:16, marginBottom:10, background:C.white },
//   certCardRev:{ border:"1px solid #fca5a5", borderRadius:10, padding:16, marginBottom:10, background:C.redBg },
//   badgeGreen: { fontSize:12, fontWeight:600, padding:"2px 10px", borderRadius:20, background:C.greenBg, color:C.green, border:`1px solid #bbf7d0` },
//   badgeRed:   { fontSize:12, fontWeight:600, padding:"2px 10px", borderRadius:20, background:C.redBg,   color:C.red,   border:`1px solid #fca5a5` },
//   badgeYellow:{ fontSize:12, fontWeight:600, padding:"2px 10px", borderRadius:20, background:C.yellowBg,color:C.yellow,border:`1px solid #fde68a` },
//   badgeCyan:  { fontSize:11, padding:"2px 8px", borderRadius:20, background:"#e0f2fe", color:"#0284c7", border:"1px solid #bae6fd" },
//   badgeGray:  { fontSize:11, padding:"2px 8px", borderRadius:20, background:"#f1f5f9", color:C.muted,   border:`1px solid ${C.border}` },
//   link:       { display:"inline-flex", alignItems:"center", gap:4, fontSize:12, color:C.accent, textDecoration:"none" },
//   mono:       { fontFamily:"monospace", fontSize:12, color:C.muted },
//   divider:    { height:1, background:C.border, margin:"14px 0" },
//   checkRow:   { display:"flex", alignItems:"center", gap:8, fontSize:13, padding:"5px 0" },
//   filterRow:  { display:"flex", gap:6 },
//   pill:       { fontSize:13, padding:"5px 14px", borderRadius:20, border:"none", cursor:"pointer", fontWeight:500 },
//   pillOn:     { background:C.accent, color:"#fff" },
//   pillOff:    { background:"#f1f5f9", color:C.muted },
//   stats:      { display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12, marginBottom:20 },
//   statBox:    { background:C.white, border:`1px solid ${C.border}`, borderRadius:10, padding:"14px 18px", textAlign:"center" },
//   statNum:    { fontSize:26, fontWeight:700, color:C.text },
//   statLbl:    { fontSize:12, color:C.muted, marginTop:2 },
//   copyBtn:    { background:"none", border:"none", cursor:"pointer", color:C.muted, padding:"0 2px", lineHeight:1 },
//   toast:      { position:"fixed", top:16, right:16, zIndex:9999, padding:"11px 18px", borderRadius:10, fontSize:13, fontWeight:500, display:"flex", alignItems:"center", gap:8, boxShadow:"0 4px 16px rgba(0,0,0,.1)" },
//   toastOk:    { background:C.greenBg, color:C.green, border:`1px solid #bbf7d0` },
//   toastErr:   { background:C.redBg,   color:C.red,   border:`1px solid #fca5a5` },
// };

// /* ════════════════════════════════
//    MAIN
// ════════════════════════════════ */
// export default function App() {
//   const [user, setUser]           = useState(null);
//   const [form, setForm]           = useState({ username:"", password:"" });
//   const [certs, setCerts]         = useState([]);
//   const [newCert, setNewCert]     = useState({ holderName:"", title:"", file:null });
//   const [issuing, setIssuing]     = useState(false);
//   const [revoking, setRevoking]   = useState(null);
//   const [filter, setFilter]       = useState("all");
//   const [loading, setLoading]     = useState(false);
//   const [vid, setVid]             = useState("");
//   const [vResult, setVResult]     = useState(null);
//   const [verifying, setVerifying] = useState(false);
//   const [toast, setToast]         = useState(null);

//   useEffect(() => {
//     if (user && user.role !== "verifier") loadCerts();
//   }, [user]);

//   const notify = (msg, type="success") => {
//     setToast({ msg, type });
//     setTimeout(() => setToast(null), 3500);
//   };

//   const loadCerts = async () => {
//     setLoading(true);
//     try { const d = await CertAPI.list(); setCerts(d.results || d); }
//     catch { notify("Failed to load certificates","error"); }
//     finally { setLoading(false); }
//   };

//   /* login */
//   const login = async e => {
//     e.preventDefault();
//     try {
//       const res = await fetch(`${API_BASE}/auth/login/`, {
//         method:"POST", headers:{"Content-Type":"application/json"},
//         body: JSON.stringify(form),
//       });
//       if (!res.ok) { notify("Invalid credentials","error"); return; }
//       const d = await res.json();
//       localStorage.setItem("access", d.tokens.access);
//       localStorage.setItem("refresh", d.tokens.refresh);
//       setUser(d.user);
//     } catch { notify("Login failed","error"); }
//   };

//   const logout = () => { localStorage.clear(); setUser(null); setCerts([]); setVResult(null); };

//   /* issue */
//   const issue = async e => {
//     e.preventDefault();
//     if (!newCert.holderName || !newCert.title || !newCert.file) { notify("All fields required","error"); return; }
//     setIssuing(true);
//     try {
//       await CertAPI.create(newCert.holderName, newCert.title, newCert.file);
//       notify("Certificate issued & anchored to blockchain");
//       loadCerts();
//       setNewCert({ holderName:"", title:"", file:null });
//     } catch { notify("Issuance failed","error"); }
//     finally { setIssuing(false); }
//   };

//   /* revoke */
//   const revoke = async (id, title) => {
//     if (!window.confirm(`Revoke "${title}"? This cannot be undone.`)) return;
//     setRevoking(id);
//     try { await CertAPI.revoke(id); notify("Certificate revoked"); loadCerts(); }
//     catch { notify("Revocation failed","error"); }
//     finally { setRevoking(null); }
//   };

//   /* verify */
//   const verify = async () => {
//     if (!vid.trim()) { notify("Enter a certificate ID","error"); return; }
//     setVerifying(true); setVResult(null);
//     try { setVResult(await CertAPI.verify(vid.trim())); }
//     catch { setVResult({ valid:false, failure_reason:"Network error — server unreachable" }); }
//     finally { setVerifying(false); }
//   };

//   const filtered = certs.filter(c => filter === "all" || c.status === filter);

//   /* ── LOGIN ── */
//   if (!user) return (
//     <div style={{ ...styles.page, display:"flex", alignItems:"center", justifyContent:"center" }}>
//       <div style={{ ...styles.card, width:360, margin:0 }}>
//         <div style={{ textAlign:"center", marginBottom:24 }}>
//           <Shield size={32} color={C.accent} style={{ marginBottom:10 }}/>
//           <div style={styles.logo}>ZeroID</div>
//           <div style={{ fontSize:13, color:C.muted, marginTop:4 }}>Blockchain Certificate System</div>
//         </div>
//         <form onSubmit={login} style={{ display:"flex", flexDirection:"column", gap:14 }}>
//           <div>
//             <label style={styles.label}>Username</label>
//             <input style={styles.input} placeholder="Username" value={form.username}
//               onChange={e => setForm({...form, username:e.target.value})}/>
//           </div>
//           <div>
//             <label style={styles.label}>Password</label>
//             <input style={styles.input} type="password" placeholder="Password" value={form.password}
//               onChange={e => setForm({...form, password:e.target.value})}/>
//           </div>
//           <button type="submit" style={{...styles.btn, ...styles.btnPrimary, justifyContent:"center", marginTop:4}}>
//             Sign In
//           </button>
//         </form>
//       </div>
//     </div>
//   );

//   /* ── DASHBOARD ── */
//   return (
//     <div style={styles.page}>
//       {/* Toast */}
//       {toast && (
//         <div style={{ ...styles.toast, ...(toast.type==="error" ? styles.toastErr : styles.toastOk) }}>
//           {toast.type==="error" ? <XCircle size={15}/> : <CheckCircle size={15}/>}
//           {toast.msg}
//         </div>
//       )}

//       {/* Header */}
//       <header style={styles.header}>
//         <div style={styles.headerLeft}>
//           <Shield size={20} color={C.accent}/>
//           <span style={styles.logo}>ZeroID</span>
//           <span style={styles.roleTag}>{user.role}</span>
//         </div>
//         <div style={{ display:"flex", alignItems:"center", gap:12 }}>
//           <span style={{ fontSize:13, color:C.muted }}>{user.username}</span>
//           <button style={styles.logoutBtn} onClick={logout}>
//             <LogOut size={14}/> Logout
//           </button>
//         </div>
//       </header>

//       <div style={styles.main}>

//         {/* ═══ ISSUER ═══ */}
//         {user.role === "issuer" && <>

//           {/* Stats */}
//           <div style={styles.stats}>
//             <div style={styles.statBox}>
//               <div style={styles.statNum}>{certs.length}</div>
//               <div style={styles.statLbl}>Total Issued</div>
//             </div>
//             <div style={styles.statBox}>
//               <div style={{...styles.statNum, color:C.green}}>{certs.filter(c=>c.status==="valid").length}</div>
//               <div style={styles.statLbl}>Valid</div>
//             </div>
//             <div style={styles.statBox}>
//               <div style={{...styles.statNum, color:C.red}}>{certs.filter(c=>c.status==="revoked").length}</div>
//               <div style={styles.statLbl}>Revoked</div>
//             </div>
//           </div>

//           {/* Issue form */}
//           <div style={styles.card}>
//             <div style={styles.cardTitle}>Issue Certificate</div>
//             <form onSubmit={issue}>
//               <div style={styles.row}>
//                 <div>
//                   <label style={styles.label}>Holder Name</label>
//                   <input style={styles.input} placeholder="Full name" value={newCert.holderName}
//                     onChange={e => setNewCert({...newCert, holderName:e.target.value})}/>
//                 </div>
//                 <div>
//                   <label style={styles.label}>Title</label>
//                   <input style={styles.input} placeholder="e.g. Bachelor of Science" value={newCert.title}
//                     onChange={e => setNewCert({...newCert, title:e.target.value})}/>
//                 </div>
//               </div>
//               <div style={{ marginBottom:16 }}>
//                 <label style={styles.label}>Certificate File</label>
//                 <input style={styles.input} type="file"
//                   onChange={e => setNewCert({...newCert, file:e.target.files[0]})}/>
//               </div>
//               <button type="submit" style={{...styles.btn, ...styles.btnPrimary, ...(issuing?styles.btnDis:{})}} disabled={issuing}>
//                 {issuing ? <><Loader2 size={14} style={{animation:"spin 1s linear infinite"}}/> Issuing...</> : "Issue Certificate"}
//               </button>
//             </form>
//           </div>

//           {/* Certificate list */}
//           <div style={styles.card}>
//             <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:16 }}>
//               <div style={styles.cardTitle}>Certificates ({filtered.length})</div>
//               <div style={{ display:"flex", alignItems:"center", gap:10 }}>
//                 <button onClick={loadCerts} style={{...styles.logoutBtn, padding:6}}>
//                   <RefreshCw size={14} style={loading?{animation:"spin 1s linear infinite"}:{}}/>
//                 </button>
//                 <div style={styles.filterRow}>
//                   {["all","valid","revoked"].map(f => (
//                     <button key={f} style={{...styles.pill, ...(filter===f?styles.pillOn:styles.pillOff)}}
//                       onClick={()=>setFilter(f)}>{f}</button>
//                   ))}
//                 </div>
//               </div>
//             </div>

//             {loading && <div style={{ textAlign:"center", padding:"30px 0", color:C.muted }}>
//               <Loader2 size={20} style={{ animation:"spin 1s linear infinite" }}/>
//             </div>}

//             {!loading && filtered.length === 0 && (
//               <p style={{ color:C.muted, fontSize:14, textAlign:"center", padding:"20px 0" }}>No certificates found.</p>
//             )}

//             {!loading && filtered.map(cert => {
//               const tx = cert.blockchain_transactions?.[0];
//               const txHash = tx?.tx_hash;
//               const synced = tx?.status === "confirmed";
//               const isRevoking = revoking === cert.certificate_id;
//               return (
//                 <div key={cert.id} style={cert.status==="revoked" ? styles.certCardRev : styles.certCard}>
//                   <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:12 }}>
//                     <div style={{ flex:1, minWidth:0 }}>
//                       {/* Title + badges */}
//                       <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap", marginBottom:6 }}>
//                         <span style={{ fontWeight:600, fontSize:15 }}>{cert.title}</span>
//                         <span style={cert.status==="valid" ? styles.badgeGreen : styles.badgeRed}>
//                           {cert.status==="valid" ? "✓ Valid" : "✕ Revoked"}
//                         </span>
//                         <span style={synced ? styles.badgeCyan : styles.badgeGray}>
//                           {synced ? "⛓ Synced" : "⛓ Not synced"}
//                         </span>
//                       </div>

//                       <p style={{ fontSize:13, color:C.muted, marginBottom:6 }}>Holder: {cert.holder_name}</p>

//                       {/* ID */}
//                       <div style={{ display:"flex", alignItems:"center", gap:4, marginBottom:8 }}>
//                         <span style={styles.mono}>{cert.certificate_id}</span>
//                         <CopyBtn text={cert.certificate_id}/>
//                       </div>

//                       {/* Gas */}
//                       {tx?.gas_used && (
//                         <p style={{ fontSize:12, color:C.muted, marginBottom:6 }}>⛽ Gas: {tx.gas_used.toLocaleString()}</p>
//                       )}

//                       {/* Links */}
//                       <div style={{ display:"flex", gap:14, flexWrap:"wrap" }}>
//                         {txHash && !txHash.startsWith("failed") && (
//                           <a href={`https://sepolia.etherscan.io/tx/${txHash}`} target="_blank" rel="noreferrer" style={styles.link}>
//                             <ExternalLink size={11}/> Etherscan
//                           </a>
//                         )}
//                         {cert.ipfs_cid && (
//                           <a href={`https://gateway.pinata.cloud/ipfs/${cert.ipfs_cid}`} target="_blank" rel="noreferrer" style={styles.link}>
//                             <ExternalLink size={11}/> IPFS
//                           </a>
//                         )}
//                       </div>
//                     </div>

//                     {/* Revoke btn */}
//                     <button
//                       style={{...styles.btn, ...styles.btnDanger, ...(cert.status==="revoked"||isRevoking?styles.btnDis:{})}}
//                       onClick={() => revoke(cert.certificate_id, cert.title)}
//                       disabled={cert.status==="revoked" || isRevoking}
//                     >
//                       {isRevoking ? <><Loader2 size={13} style={{animation:"spin 1s linear infinite"}}/> Revoking...</> : cert.status==="revoked" ? "Revoked" : "Revoke"}
//                     </button>
//                   </div>
//                 </div>
//               );
//             })}
//           </div>
//         </>}

//         {/* ═══ HOLDER ═══ */}
//         {user.role === "holder" && (
//           <div style={styles.card}>
//             <div style={styles.cardTitle}>My Certificates</div>
//             {loading && <div style={{ textAlign:"center", padding:"20px 0", color:C.muted }}><Loader2 size={20} style={{animation:"spin 1s linear infinite"}}/></div>}
//             {!loading && certs.length === 0 && <p style={{ color:C.muted, fontSize:14 }}>No certificates found.</p>}
//             {!loading && certs.map(cert => (
//               <div key={cert.id} style={cert.status==="revoked" ? styles.certCardRev : styles.certCard}>
//                 <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
//                   <div>
//                     <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
//                       <span style={{ fontWeight:600 }}>{cert.title}</span>
//                       <span style={cert.status==="valid" ? styles.badgeGreen : styles.badgeRed}>
//                         {cert.status==="valid" ? "✓ Valid" : "✕ Revoked"}
//                       </span>
//                     </div>
//                     <p style={{ fontSize:13, color:C.muted, marginBottom:4 }}>Issuer: {cert.issuer_name || cert.issuer}</p>
//                     <div style={{ display:"flex", alignItems:"center", gap:4 }}>
//                       <span style={styles.mono}>{cert.certificate_id}</span>
//                       <CopyBtn text={cert.certificate_id}/>
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}

//         {/* ═══ VERIFIER ═══ */}
//         {user.role === "verifier" && (
//           <div>
//             <div style={styles.card}>
//               <div style={styles.cardTitle}>Verify Certificate</div>
//               <div style={{ display:"flex", gap:10 }}>
//                 <input style={{...styles.input, fontFamily:"monospace", fontSize:13}}
//                   placeholder="Paste Certificate ID"
//                   value={vid} onChange={e => setVid(e.target.value)}
//                   onKeyDown={e => e.key==="Enter" && verify()}/>
//                 <button style={{...styles.btn, ...styles.btnCyan, ...(verifying?styles.btnDis:{})}}
//                   onClick={verify} disabled={verifying}>
//                   {verifying ? <><Loader2 size={14} style={{animation:"spin 1s linear infinite"}}/> Verifying...</> : <><Shield size={14}/> Verify</>}
//                 </button>
//                 {vResult && (
//                   <button style={{...styles.btn, ...styles.btnGhost}}
//                     onClick={()=>{setVResult(null);setVid("");}}>Clear</button>
//                 )}
//               </div>
//             </div>

//             {vResult && (
//               <div style={{
//                 ...styles.card,
//                 borderColor: vResult.valid ? "#bbf7d0" : vResult.is_revoked ? "#fca5a5" : "#fde68a",
//                 background:  vResult.valid ? C.greenBg  : vResult.is_revoked ? C.redBg   : C.yellowBg,
//               }}>
//                 {/* Status */}
//                 <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:16 }}>
//                   {vResult.valid
//                     ? <CheckCircle size={28} color={C.green}/>
//                     : vResult.is_revoked
//                     ? <XCircle size={28} color={C.red}/>
//                     : <AlertTriangle size={28} color={C.yellow}/>}
//                   <div>
//                     <div style={{ fontWeight:700, fontSize:18, color: vResult.valid?C.green:vResult.is_revoked?C.red:C.yellow }}>
//                       {vResult.valid ? "Certificate is VALID"
//                         : vResult.is_revoked ? "Certificate has been REVOKED"
//                         : "Certificate is INVALID"}
//                     </div>
//                     {vResult.message && <p style={{ fontSize:13, color:C.muted, marginTop:2 }}>{vResult.message}</p>}
//                   </div>
//                 </div>

//                 {/* Failure reason */}
//                 {!vResult.valid && vResult.failure_reason && (
//                   <div style={{ background:"#fff", border:"1px solid #fca5a5", borderRadius:8, padding:"10px 14px", marginBottom:14 }}>
//                     <span style={{ fontSize:12, fontWeight:600, color:C.red }}>Reason: </span>
//                     <span style={{ fontSize:13, color:"#7f1d1d" }}>{vResult.failure_reason}</span>
//                   </div>
//                 )}

//                 {/* Check grid */}
//                 <div style={{ background:"#fff", borderRadius:8, padding:"12px 16px", display:"grid", gridTemplateColumns:"1fr 1fr", gap:"4px 0", marginBottom:14 }}>
//                   {[
//                     { label:"Hash Integrity",  ok:vResult.hash_match },
//                     { label:"Not Revoked",      ok:!vResult.is_revoked },
//                     { label:"Merkle Proof",     ok:vResult.blockchain_verified },
//                     { label:"Blockchain Live",  ok:vResult.blockchain_connected, warn:!vResult.blockchain_connected },
//                   ].map(({label,ok,warn}) => (
//                     <div key={label} style={styles.checkRow}>
//                       {ok ? <CheckCircle size={14} color={C.green}/>
//                         : warn ? <AlertTriangle size={14} color={C.yellow}/>
//                         : <XCircle size={14} color={C.red}/>}
//                       <span style={{ color:ok?C.green:warn?C.yellow:C.red, fontSize:13 }}>{label}</span>
//                     </div>
//                   ))}
//                 </div>

//                 {/* Certificate details */}
//                 {vResult.certificate && (
//                   <>
//                     <div style={styles.divider}/>
//                     <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8, marginBottom:12 }}>
//                       {[
//                         ["Title",   vResult.certificate.title],
//                         ["Holder",  vResult.certificate.holder_name],
//                         ["Issuer",  vResult.certificate.issuer_name || vResult.certificate.issuer],
//                         ["Issued",  vResult.certificate.issued_date],
//                       ].filter(([,v])=>v).map(([k,v]) => (
//                         <div key={k}>
//                           <div style={{ fontSize:11, color:C.muted, fontWeight:600, textTransform:"uppercase", letterSpacing:".04em", marginBottom:2 }}>{k}</div>
//                           <div style={{ fontSize:13, color:C.text }}>{v}</div>
//                         </div>
//                       ))}
//                     </div>
//                   </>
//                 )}

//                 {/* Footer */}
//                 <div style={styles.divider}/>
//                 <div style={{ display:"flex", flexWrap:"wrap", gap:14, alignItems:"center" }}>
//                   {vResult.gas_used && <span style={{ fontSize:12, color:C.muted }}>⛽ {vResult.gas_used.toLocaleString()} gas</span>}
//                   {vResult.certificate?.ipfs_cid && (
//                     <a href={`https://gateway.pinata.cloud/ipfs/${vResult.certificate.ipfs_cid}`}
//                       target="_blank" rel="noreferrer" style={styles.link}>
//                       <ExternalLink size={11}/> IPFS
//                     </a>
//                   )}
//                   {vResult.certificate?.blockchain_transactions?.[0]?.tx_hash &&
//                     !vResult.certificate.blockchain_transactions[0].tx_hash.startsWith("failed") && (
//                     <a href={`https://sepolia.etherscan.io/tx/${vResult.certificate.blockchain_transactions[0].tx_hash}`}
//                       target="_blank" rel="noreferrer" style={styles.link}>
//                       <ExternalLink size={11}/> Etherscan
//                     </a>
//                   )}
//                   {vResult.verified_at && (
//                     <span style={{ fontSize:11, color:C.muted, marginLeft:"auto" }}>
//                       {new Date(vResult.verified_at).toLocaleString()}
//                     </span>
//                   )}
//                 </div>
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

import React, { useState, useEffect } from "react";
import {
  CheckCircle, XCircle, Shield, LogOut, Loader2,
  AlertTriangle, ExternalLink, RefreshCw, Copy,
} from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";

async function api(url, method = "GET", body = null, auth = true) {
  const headers = {};
  if (auth) {
    const token = localStorage.getItem("access");
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const options = { method, headers };
  if (body) {
    if (body instanceof FormData) options.body = body;
    else { headers["Content-Type"] = "application/json"; options.body = JSON.stringify(body); }
  }
  const res = await fetch(API_BASE + url, options);
  if (!res.ok) { const t = await res.text(); throw new Error(t || "API Error"); }
  return res.json();
}

const CertAPI = {
  list:   ()                        => api("/certificates/"),
  create: (holderName, title, file) => {
    const fd = new FormData();
    fd.append("holder_name", holderName);
    fd.append("title", title);
    fd.append("certificate_file", file);
    return api("/certificates/", "POST", fd);
  },
  revoke: (id, reason) => api("/revoke/", "POST", { certificate_id: id, reason: reason || "Revoked by issuer" }),
  verify: (id)         => api("/verify/", "POST", { certificate_id: id }, false),
};

/* ── small helpers ── */
function CopyBtn({ text }) {
  const [ok, setOk] = useState(false);
  return (
    <button style={styles.copyBtn} title="Copy"
      onClick={() => { navigator.clipboard.writeText(text); setOk(true); setTimeout(() => setOk(false), 1500); }}>
      {ok ? <CheckCircle size={12} color="#16a34a" /> : <Copy size={12} />}
    </button>
  );
}

/* ── styles ── */
const C = {
  bg: "#f8fafc", white: "#ffffff", border: "#e2e8f0",
  text: "#1e293b", muted: "#64748b", accent: "#4f46e5",
  green: "#16a34a", red: "#dc2626", yellow: "#d97706",
  greenBg: "#f0fdf4", redBg: "#fef2f2", yellowBg: "#fffbeb",
};

const styles = {
  page:        { minHeight: "100vh", background: C.bg, fontFamily: "system-ui,sans-serif", color: C.text },
  header:      { background: C.white, borderBottom: `1px solid ${C.border}`, padding: "14px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" },
  headerLeft:  { display: "flex", alignItems: "center", gap: 10 },
  logo:        { fontWeight: 700, fontSize: 18, color: C.text, letterSpacing: "-0.02em" },
  roleTag:     { fontSize: 12, padding: "3px 10px", borderRadius: 20, background: "#eef2ff", color: C.accent, fontWeight: 600, textTransform: "capitalize" },
  logoutBtn:   { display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: C.muted, background: "none", border: "none", cursor: "pointer", padding: "6px 10px", borderRadius: 8 },
  main:        { maxWidth: 820, margin: "0 auto", padding: "28px 20px" },
  card:        { background: C.white, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24, marginBottom: 20 },
  cardTitle:   { fontSize: 16, fontWeight: 600, marginBottom: 16, color: C.text },
  label:       { fontSize: 12, fontWeight: 600, color: C.muted, marginBottom: 5, display: "block", textTransform: "uppercase", letterSpacing: ".04em" },
  input:       { width: "100%", border: `1px solid ${C.border}`, borderRadius: 8, padding: "9px 12px", fontSize: 14, outline: "none", color: C.text, background: C.white, boxSizing: "border-box" },
  row:         { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 14 },
  btn:         { display: "inline-flex", alignItems: "center", gap: 7, padding: "9px 18px", borderRadius: 8, fontSize: 14, fontWeight: 500, cursor: "pointer", border: "none", transition: "opacity .15s" },
  btnPrimary:  { background: C.accent, color: "#fff" },
  btnDanger:   { background: "none", color: C.red, border: `1px solid #fca5a5` },
  btnGhost:    { background: "none", color: C.muted, border: `1px solid ${C.border}` },
  btnCyan:     { background: "#0284c7", color: "#fff" },
  btnDis:      { opacity: .5, cursor: "not-allowed" },
  certCard:    { border: `1px solid ${C.border}`, borderRadius: 10, padding: 16, marginBottom: 10, background: C.white },
  certCardRev: { border: "1px solid #fca5a5", borderRadius: 10, padding: 16, marginBottom: 10, background: C.redBg },
  badgeGreen:  { fontSize: 12, fontWeight: 600, padding: "2px 10px", borderRadius: 20, background: C.greenBg, color: C.green, border: `1px solid #bbf7d0` },
  badgeRed:    { fontSize: 12, fontWeight: 600, padding: "2px 10px", borderRadius: 20, background: C.redBg, color: C.red, border: `1px solid #fca5a5` },
  badgeYellow: { fontSize: 12, fontWeight: 600, padding: "2px 10px", borderRadius: 20, background: C.yellowBg, color: C.yellow, border: `1px solid #fde68a` },
  badgeCyan:   { fontSize: 11, padding: "2px 8px", borderRadius: 20, background: "#e0f2fe", color: "#0284c7", border: "1px solid #bae6fd" },
  badgeGray:   { fontSize: 11, padding: "2px 8px", borderRadius: 20, background: "#f1f5f9", color: C.muted, border: `1px solid ${C.border}` },
  link:        { display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: C.accent, textDecoration: "none" },
  mono:        { fontFamily: "monospace", fontSize: 12, color: C.muted },
  divider:     { height: 1, background: C.border, margin: "14px 0" },
  checkRow:    { display: "flex", alignItems: "center", gap: 8, fontSize: 13, padding: "5px 0" },
  filterRow:   { display: "flex", gap: 6 },
  pill:        { fontSize: 13, padding: "5px 14px", borderRadius: 20, border: "none", cursor: "pointer", fontWeight: 500 },
  pillOn:      { background: C.accent, color: "#fff" },
  pillOff:     { background: "#f1f5f9", color: C.muted },
  stats:       { display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 20 },
  statBox:     { background: C.white, border: `1px solid ${C.border}`, borderRadius: 10, padding: "14px 18px", textAlign: "center" },
  statNum:     { fontSize: 26, fontWeight: 700, color: C.text },
  statLbl:     { fontSize: 12, color: C.muted, marginTop: 2 },
  copyBtn:     { background: "none", border: "none", cursor: "pointer", color: C.muted, padding: "0 2px", lineHeight: 1 },
  toast:       { position: "fixed", top: 16, right: 16, zIndex: 9999, padding: "11px 18px", borderRadius: 10, fontSize: 13, fontWeight: 500, display: "flex", alignItems: "center", gap: 8, boxShadow: "0 4px 16px rgba(0,0,0,.1)" },
  toastOk:     { background: C.greenBg, color: C.green, border: `1px solid #bbf7d0` },
  toastErr:    { background: C.redBg, color: C.red, border: `1px solid #fca5a5` },
};

/* ════════════════════════════════
   MAIN
════════════════════════════════ */
export default function App() {
  const [user, setUser]               = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [form, setForm]               = useState({ username: "", password: "" });
  const [certs, setCerts]             = useState([]);
  const [newCert, setNewCert]         = useState({ holderName: "", title: "", file: null });
  const [issuing, setIssuing]         = useState(false);
  const [revoking, setRevoking]       = useState(null);
  const [filter, setFilter]           = useState("all");
  const [loading, setLoading]         = useState(false);
  const [vid, setVid]                 = useState("");
  const [vResult, setVResult]         = useState(null);
  const [verifying, setVerifying]     = useState(false);
  const [toast, setToast]             = useState(null);

  /* ── Restore session on page load / refresh ── */
  useEffect(() => {
    const token     = localStorage.getItem("access");
    const savedUser = localStorage.getItem("user");
    if (token && savedUser) {
      try { setUser(JSON.parse(savedUser)); } catch { localStorage.clear(); }
    }
    setAuthLoading(false);
  }, []);

  /* ── Load certs whenever user is set ────────────────────────────────────── */
  useEffect(() => {
    if (user && user.role !== "verifier") loadCerts();
  }, [user]);

  const notify = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const loadCerts = async () => {
    setLoading(true);
    try { const d = await CertAPI.list(); setCerts(d.results || d); }
    catch { notify("Failed to load certificates", "error"); }
    finally { setLoading(false); }
  };

  /* ── Login ──────────────────────────────────────────────────────────────── */
  const login = async e => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) { notify("Invalid credentials", "error"); return; }
      const d = await res.json();
      localStorage.setItem("access", d.tokens.access);
      localStorage.setItem("refresh", d.tokens.refresh);
      localStorage.setItem("user", JSON.stringify(d.user)); // ← persists across reload
      setUser(d.user);
    } catch { notify("Login failed", "error"); }
  };

  /* ── Logout ─────────────────────────────────────────────────────────────── */
  const logout = () => {
    localStorage.clear();
    setUser(null);
    setCerts([]);
    setVResult(null);
  };

  /* ── Issue ──────────────────────────────────────────────────────────────── */
  const issue = async e => {
    e.preventDefault();
    if (!newCert.holderName || !newCert.title || !newCert.file) {
      notify("All fields required", "error"); return;
    }
    setIssuing(true);
    try {
      await CertAPI.create(newCert.holderName, newCert.title, newCert.file);
      notify("Certificate issued & anchored to blockchain");
      loadCerts();
      setNewCert({ holderName: "", title: "", file: null });
    } catch { notify("Issuance failed", "error"); }
    finally { setIssuing(false); }
  };

  /* ── Revoke ─────────────────────────────────────────────────────────────── */
  const revoke = async (id, title) => {
    if (!window.confirm(`Revoke "${title}"? This cannot be undone.`)) return;
    setRevoking(id);
    try { await CertAPI.revoke(id); notify("Certificate revoked"); loadCerts(); }
    catch { notify("Revocation failed", "error"); }
    finally { setRevoking(null); }
  };

  /* ── Verify ─────────────────────────────────────────────────────────────── */
  const verify = async () => {
    if (!vid.trim()) { notify("Enter a certificate ID", "error"); return; }
    setVerifying(true); setVResult(null);
    try { setVResult(await CertAPI.verify(vid.trim())); }
    catch { setVResult({ valid: false, failure_reason: "Network error — server unreachable" }); }
    finally { setVerifying(false); }
  };

  const filtered = certs.filter(c => filter === "all" || c.status === filter);

  /* ── Session restore spinner ────────────────────────────────────────────── */
  if (authLoading) return (
    <div style={{ ...styles.page, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ textAlign: "center", color: C.muted }}>
        <Loader2 size={32} color={C.accent} style={{ animation: "spin 1s linear infinite", marginBottom: 12 }} />
        <p style={{ fontSize: 14 }}>Loading...</p>
      </div>
    </div>
  );

  /* ── Login screen ───────────────────────────────────────────────────────── */
  if (!user) return (
    <div style={{ ...styles.page, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ ...styles.card, width: 360, margin: 0 }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <Shield size={32} color={C.accent} style={{ marginBottom: 10 }} />
          <div style={styles.logo}>ZeroID</div>
          <div style={{ fontSize: 13, color: C.muted, marginTop: 4 }}>Blockchain Certificate System</div>
        </div>
        <form onSubmit={login} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={styles.label}>Username</label>
            <input style={styles.input} placeholder="Username" value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })} />
          </div>
          <div>
            <label style={styles.label}>Password</label>
            <input style={styles.input} type="password" placeholder="Password" value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })} />
          </div>
          <button type="submit" style={{ ...styles.btn, ...styles.btnPrimary, justifyContent: "center", marginTop: 4 }}>
            Sign In
          </button>
        </form>
      </div>
    </div>
  );

  /* ── Dashboard ──────────────────────────────────────────────────────────── */
  return (
    <div style={styles.page}>

      {/* Toast */}
      {toast && (
        <div style={{ ...styles.toast, ...(toast.type === "error" ? styles.toastErr : styles.toastOk) }}>
          {toast.type === "error" ? <XCircle size={15} /> : <CheckCircle size={15} />}
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <Shield size={20} color={C.accent} />
          <span style={styles.logo}>ZeroID</span>
          <span style={styles.roleTag}>{user.role}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 13, color: C.muted }}>{user.username}</span>
          <button style={styles.logoutBtn} onClick={logout}>
            <LogOut size={14} /> Logout
          </button>
        </div>
      </header>

      <div style={styles.main}>

        {/* ═══════════════ ISSUER ═══════════════ */}
        {user.role === "issuer" && <>

          {/* Stats row */}
          <div style={styles.stats}>
            <div style={styles.statBox}>
              <div style={styles.statNum}>{certs.length}</div>
              <div style={styles.statLbl}>Total Issued</div>
            </div>
            <div style={styles.statBox}>
              <div style={{ ...styles.statNum, color: C.green }}>{certs.filter(c => c.status === "valid").length}</div>
              <div style={styles.statLbl}>Valid</div>
            </div>
            <div style={styles.statBox}>
              <div style={{ ...styles.statNum, color: C.red }}>{certs.filter(c => c.status === "revoked").length}</div>
              <div style={styles.statLbl}>Revoked</div>
            </div>
          </div>

          {/* Issue form */}
          <div style={styles.card}>
            <div style={styles.cardTitle}>Issue Certificate</div>
            <form onSubmit={issue}>
              <div style={styles.row}>
                <div>
                  <label style={styles.label}>Holder Name</label>
                  <input style={styles.input} placeholder="Full name" value={newCert.holderName}
                    onChange={e => setNewCert({ ...newCert, holderName: e.target.value })} />
                </div>
                <div>
                  <label style={styles.label}>Title</label>
                  <input style={styles.input} placeholder="e.g. Bachelor of Science" value={newCert.title}
                    onChange={e => setNewCert({ ...newCert, title: e.target.value })} />
                </div>
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={styles.label}>Certificate File</label>
                <input style={styles.input} type="file"
                  onChange={e => setNewCert({ ...newCert, file: e.target.files[0] })} />
              </div>
              <button type="submit"
                style={{ ...styles.btn, ...styles.btnPrimary, ...(issuing ? styles.btnDis : {}) }}
                disabled={issuing}>
                {issuing
                  ? <><Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} /> Issuing...</>
                  : "Issue Certificate"}
              </button>
            </form>
          </div>

          {/* Certificate list */}
          <div style={styles.card}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <div style={styles.cardTitle}>Certificates ({filtered.length})</div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <button onClick={loadCerts} style={{ ...styles.logoutBtn, padding: 6 }}>
                  <RefreshCw size={14} style={loading ? { animation: "spin 1s linear infinite" } : {}} />
                </button>
                <div style={styles.filterRow}>
                  {["all", "valid", "revoked"].map(f => (
                    <button key={f}
                      style={{ ...styles.pill, ...(filter === f ? styles.pillOn : styles.pillOff) }}
                      onClick={() => setFilter(f)}>
                      {f}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {loading && (
              <div style={{ textAlign: "center", padding: "30px 0", color: C.muted }}>
                <Loader2 size={20} style={{ animation: "spin 1s linear infinite" }} />
              </div>
            )}

            {!loading && filtered.length === 0 && (
              <p style={{ color: C.muted, fontSize: 14, textAlign: "center", padding: "20px 0" }}>
                No certificates found.
              </p>
            )}

            {!loading && filtered.map(cert => {
              const tx         = cert.blockchain_transactions?.[0];
              const txHash     = tx?.tx_hash;
              const synced     = tx?.status === "confirmed";
              const isRevoking = revoking === cert.certificate_id;
              return (
                <div key={cert.id} style={cert.status === "revoked" ? styles.certCardRev : styles.certCard}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                    <div style={{ flex: 1, minWidth: 0 }}>

                      {/* Title + status badges */}
                      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
                        <span style={{ fontWeight: 600, fontSize: 15 }}>{cert.title}</span>
                        <span style={cert.status === "valid" ? styles.badgeGreen : styles.badgeRed}>
                          {cert.status === "valid" ? "✓ Valid" : "✕ Revoked"}
                        </span>
                        <span style={synced ? styles.badgeCyan : styles.badgeGray}>
                          {synced ? "⛓ Synced" : "⛓ Not synced"}
                        </span>
                      </div>

                      <p style={{ fontSize: 13, color: C.muted, marginBottom: 6 }}>
                        Holder: {cert.holder_name}
                      </p>

                      {/* Certificate ID + copy button */}
                      <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 8 }}>
                        <span style={styles.mono}>{cert.certificate_id}</span>
                        <CopyBtn text={cert.certificate_id} />
                      </div>

                      {/* Gas used */}
                      {tx?.gas_used && (
                        <p style={{ fontSize: 12, color: C.muted, marginBottom: 6 }}>
                          ⛽ Gas: {tx.gas_used.toLocaleString()}
                        </p>
                      )}

                      {/* External links */}
                      <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
                        {txHash && !txHash.startsWith("failed") && (
                          <a href={`https://sepolia.etherscan.io/tx/${txHash}`}
                            target="_blank" rel="noreferrer" style={styles.link}>
                            <ExternalLink size={11} /> Etherscan
                          </a>
                        )}
                        {cert.ipfs_cid && (
                          <a href={`https://gateway.pinata.cloud/ipfs/${cert.ipfs_cid}`}
                            target="_blank" rel="noreferrer" style={styles.link}>
                            <ExternalLink size={11} /> IPFS
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Revoke button */}
                    <button
                      style={{ ...styles.btn, ...styles.btnDanger, ...(cert.status === "revoked" || isRevoking ? styles.btnDis : {}) }}
                      onClick={() => revoke(cert.certificate_id, cert.title)}
                      disabled={cert.status === "revoked" || isRevoking}
                    >
                      {isRevoking
                        ? <><Loader2 size={13} style={{ animation: "spin 1s linear infinite" }} /> Revoking...</>
                        : cert.status === "revoked" ? "Revoked" : "Revoke"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </>}

        {/* ═══════════════ HOLDER ═══════════════ */}
        {user.role === "holder" && (
          <div style={styles.card}>
            <div style={styles.cardTitle}>My Certificates</div>
            {loading && (
              <div style={{ textAlign: "center", padding: "20px 0", color: C.muted }}>
                <Loader2 size={20} style={{ animation: "spin 1s linear infinite" }} />
              </div>
            )}
            {!loading && certs.length === 0 && (
              <p style={{ color: C.muted, fontSize: 14 }}>No certificates found.</p>
            )}
            {!loading && certs.map(cert => (
              <div key={cert.id} style={cert.status === "revoked" ? styles.certCardRev : styles.certCard}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <span style={{ fontWeight: 600 }}>{cert.title}</span>
                      <span style={cert.status === "valid" ? styles.badgeGreen : styles.badgeRed}>
                        {cert.status === "valid" ? "✓ Valid" : "✕ Revoked"}
                      </span>
                    </div>
                    <p style={{ fontSize: 13, color: C.muted, marginBottom: 4 }}>
                      Issuer: {cert.issuer_name || cert.issuer}
                    </p>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <span style={styles.mono}>{cert.certificate_id}</span>
                      <CopyBtn text={cert.certificate_id} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ═══════════════ VERIFIER ═══════════════ */}
        {user.role === "verifier" && (
          <div>
            <div style={styles.card}>
              <div style={styles.cardTitle}>Verify Certificate</div>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  style={{ ...styles.input, fontFamily: "monospace", fontSize: 13 }}
                  placeholder="Paste Certificate ID"
                  value={vid}
                  onChange={e => setVid(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && verify()}
                />
                <button
                  style={{ ...styles.btn, ...styles.btnCyan, ...(verifying ? styles.btnDis : {}) }}
                  onClick={verify}
                  disabled={verifying}
                >
                  {verifying
                    ? <><Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} /> Verifying...</>
                    : <><Shield size={14} /> Verify</>}
                </button>
                {vResult && (
                  <button style={{ ...styles.btn, ...styles.btnGhost }}
                    onClick={() => { setVResult(null); setVid(""); }}>
                    Clear
                  </button>
                )}
              </div>
            </div>

            {vResult && (
              <div style={{
                ...styles.card,
                borderColor: vResult.valid ? "#bbf7d0" : vResult.is_revoked ? "#fca5a5" : "#fde68a",
                background:  vResult.valid ? C.greenBg : vResult.is_revoked ? C.redBg : C.yellowBg,
              }}>

                {/* Status headline */}
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                  {vResult.valid
                    ? <CheckCircle size={28} color={C.green} />
                    : vResult.is_revoked
                    ? <XCircle size={28} color={C.red} />
                    : <AlertTriangle size={28} color={C.yellow} />}
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 18, color: vResult.valid ? C.green : vResult.is_revoked ? C.red : C.yellow }}>
                      {vResult.valid
                        ? "Certificate is VALID"
                        : vResult.is_revoked
                        ? "Certificate has been REVOKED"
                        : "Certificate is INVALID"}
                    </div>
                    {vResult.message && (
                      <p style={{ fontSize: 13, color: C.muted, marginTop: 2 }}>{vResult.message}</p>
                    )}
                  </div>
                </div>

                {/* Failure reason box */}
                {!vResult.valid && vResult.failure_reason && (
                  <div style={{ background: "#fff", border: "1px solid #fca5a5", borderRadius: 8, padding: "10px 14px", marginBottom: 14 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: C.red }}>Reason: </span>
                    <span style={{ fontSize: 13, color: "#7f1d1d" }}>{vResult.failure_reason}</span>
                  </div>
                )}

                {/* 4-check grid */}
                <div style={{ background: "#fff", borderRadius: 8, padding: "12px 16px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 0", marginBottom: 14 }}>
                  {[
                    { label: "Hash Integrity",  ok: vResult.hash_match },
                    { label: "Not Revoked",     ok: !vResult.is_revoked },
                    { label: "Merkle Proof",    ok: vResult.blockchain_verified },
                    { label: "Blockchain Live", ok: vResult.blockchain_connected, warn: !vResult.blockchain_connected },
                  ].map(({ label, ok, warn }) => (
                    <div key={label} style={styles.checkRow}>
                      {ok
                        ? <CheckCircle size={14} color={C.green} />
                        : warn
                        ? <AlertTriangle size={14} color={C.yellow} />
                        : <XCircle size={14} color={C.red} />}
                      <span style={{ color: ok ? C.green : warn ? C.yellow : C.red, fontSize: 13 }}>
                        {label}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Certificate details */}
                {vResult.certificate && (
                  <>
                    <div style={styles.divider} />
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
                      {[
                        ["Title",  vResult.certificate.title],
                        ["Holder", vResult.certificate.holder_name],
                        ["Issuer", vResult.certificate.issuer_name || vResult.certificate.issuer],
                        ["Issued", vResult.certificate.issued_date],
                      ].filter(([, v]) => v).map(([k, v]) => (
                        <div key={k}>
                          <div style={{ fontSize: 11, color: C.muted, fontWeight: 600, textTransform: "uppercase", letterSpacing: ".04em", marginBottom: 2 }}>{k}</div>
                          <div style={{ fontSize: 13, color: C.text }}>{v}</div>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                {/* Footer row */}
                <div style={styles.divider} />
                <div style={{ display: "flex", flexWrap: "wrap", gap: 14, alignItems: "center" }}>
                  {vResult.gas_used && (
                    <span style={{ fontSize: 12, color: C.muted }}>⛽ {vResult.gas_used.toLocaleString()} gas</span>
                  )}
                  {vResult.certificate?.ipfs_cid && (
                    <a href={`https://gateway.pinata.cloud/ipfs/${vResult.certificate.ipfs_cid}`}
                      target="_blank" rel="noreferrer" style={styles.link}>
                      <ExternalLink size={11} /> IPFS
                    </a>
                  )}
                  {vResult.certificate?.blockchain_transactions?.[0]?.tx_hash &&
                    !vResult.certificate.blockchain_transactions[0].tx_hash.startsWith("failed") && (
                    <a href={`https://sepolia.etherscan.io/tx/${vResult.certificate.blockchain_transactions[0].tx_hash}`}
                      target="_blank" rel="noreferrer" style={styles.link}>
                      <ExternalLink size={11} /> Etherscan
                    </a>
                  )}
                  {vResult.verified_at && (
                    <span style={{ fontSize: 11, color: C.muted, marginLeft: "auto" }}>
                      {new Date(vResult.verified_at).toLocaleString()}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}