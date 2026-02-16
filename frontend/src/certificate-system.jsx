// import React, { useState, useEffect } from 'react';
// import { Upload, CheckCircle, XCircle, Shield, FileText, Users, Lock, Eye, AlertTriangle, Download, LogOut } from 'lucide-react';

// //API////
// /////
// const API_BASE = "http://127.0.0.1:8000";

// // async function api(url, method = "GET", body = null, auth = true) {
// //   const headers = {};

// //   if (auth) {
// //     const token = localStorage.getItem("access");
// //     if (token) headers.Authorization = `Bearer ${token}`;
// //   }

// //   if (body && !(body instanceof FormData)) {
// //     headers["Content-Type"] = "application/json";
// //   }

// //   const response = await fetch(API_BASE + url, {
// //     method,
// //     headers,
// //     body: body ? JSON.stringify(body) : null,
// //   });

// //   if (!response.ok) {
// //     throw new Error("API error");
// //   }

// //   return response.json();
// // }


// async function api(url, method = "GET", body = null, auth = true) {
//   const headers = {};

//   if (auth) {
//     const token = localStorage.getItem("access");
//     if (token) headers.Authorization = `Bearer ${token}`;
//   }

//   const options = {
//     method,
//     headers,
//   };

//   if (body) {
//     if (body instanceof FormData) {
//       options.body = body;   // 🔥 DO NOT stringify
//     } else {
//       headers["Content-Type"] = "application/json";
//       options.body = JSON.stringify(body);
//     }
//   }

//   const response = await fetch(API_BASE + url, options);

//   if (!response.ok) {
//     const errorText = await response.text();
//     console.log("Backend error:", errorText); // debug
//     throw new Error("API error");
//   }

//   return response.json();
// }



// //fetch certificate from backend
// useEffect(() => {
//   loadCertificates();
// }, []);

// const loadCertificates = async () => {
//   try {
//     const data = await CertificateModule.listCertificates();
//     setCertificates(data);
//   } catch (err) {
//     console.error(err);
//   }
// };


// // ============================================================================
// // DATABASE & FILE STORAGE SIMULATION (Modules 8 & 9)
// // ============================================================================
// const DATABASE = {
//   users: [
//     { id: 1, username: 'issuer1', password: 'pass123', role: 'issuer', name: 'Sarah Johnson' },
//     { id: 2, username: 'holder1', password: 'pass123', role: 'holder', name: 'Michael Chen' },
//     { id: 3, username: 'verifier1', password: 'pass123', role: 'verifier', name: 'Emily Rodriguez' }
//   ],
//   certificates: [],
//   verificationLogs: [],
//   revocationRecords: []
// };

// const FILE_STORAGE = {};

// // ============================================================================
// // SECURITY & INTEGRITY MODULE (Module 4)
// // ============================================================================
// const SecurityModule = {
//   generateHash: (data) => {
//     // SHA-256 simulation
//     let hash = 0;
//     const str = JSON.stringify(data);
//     for (let i = 0; i < str.length; i++) {
//       const char = str.charCodeAt(i);
//       hash = ((hash << 5) - hash) + char;
//       hash = hash & hash;
//     }
//     return 'SHA256:' + Math.abs(hash).toString(16).padStart(16, '0') + Date.now().toString(16);
//   },
  
//   compareHash: (original, computed) => {
//     return original === computed;
//   }
// };

// // ============================================================================
// // CERTIFICATE MANAGEMENT MODULE (Module 3)
// // ============================================================================
// // const CertificateModule = {
// //   createCertificate: (issuerID, holderName, title, file) => {
// //     const certID = 'CERT-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9).toUpperCase();
// //     const metadata = {
// //       holderName,
// //       title,
// //       issuerID,
// //       issuedDate: new Date().toISOString()
// //     };
    
// //     const hash = SecurityModule.generateHash({ certID, metadata, fileName: file.name });
    
// //     const certificate = {
// //       id: certID,
// //       holderName,
// //       title,
// //       issuerID,
// //       issuedDate: metadata.issuedDate,
// //       hash,
// //       fileName: file.name,
// //       fileSize: file.size,
// //       status: 'valid'
// //     };
    
// //     DATABASE.certificates.push(certificate);
// //     FILE_STORAGE[certID] = file;
    
// //     AuditModule.log('certificate_issued', certID, issuerID, { holderName, title });
    
// //     return certificate;
// //   },
  
// //   getCertificate: (certID) => {
// //     return DATABASE.certificates.find(cert => cert.id === certID);
// //   }
// // };


// const handleCreateCertificate = async (e) => {
//   e.preventDefault();

//   if (!UserModule.authorize(currentUser, 'create_certificate')) {
//     showNotification('Unauthorized action', 'error');
//     return;
//   }

//   try {
//     const newCert = await CertificateModule.createCertificate(
//       currentUser.id,
//       certForm.holderName,
//       certForm.title,
//       certForm.file
//     );

//     // 🔥 ADD newly created certificate to state
//     setCertificates(prev => [newCert, ...prev]);

//     showNotification('Certificate created successfully!', 'success');

//     setCertForm({ holderName: '', title: '', file: null });

//   } catch (error) {
//     console.error(error);
//     showNotification('Failed to create certificate', 'error');
//   }
// };




// // ============================================================================
// // VERIFICATION MODULE (Module 5)
// // ============================================================================
// const VerificationModule = {
//   verifyCertificate: (certID, verifierID) => {
//     const cert = CertificateModule.getCertificate(certID);
    
//     if (!cert) {
//       AuditModule.log('verification_failed', certID, verifierID, { reason: 'Certificate not found' });
//       return { valid: false, reason: 'Certificate not found' };
//     }
    
//     // Recompute hash
//     const metadata = {
//       holderName: cert.holderName,
//       title: cert.title,
//       issuerID: cert.issuerID,
//       issuedDate: cert.issuedDate
//     };
//     const computedHash = SecurityModule.generateHash({ 
//       certID: cert.id, 
//       metadata, 
//       fileName: cert.fileName 
//     });
    
//     // Compare hashes
//     const hashMatch = SecurityModule.compareHash(cert.hash, computedHash);
    
//     // Check revocation
//     const isRevoked = cert.status === 'revoked';
    
//     const result = {
//       valid: hashMatch && !isRevoked,
//       certificate: cert,
//       hashMatch,
//       isRevoked,
//       verifiedAt: new Date().toISOString()
//     };
    
//     AuditModule.log('verification_attempted', certID, verifierID, result);
    
//     return result;
//   }
// };

// // ============================================================================
// // REVOCATION MODULE (Module 6)
// // ============================================================================
// const RevocationModule = {
//   revokeCertificate: (certID, issuerID, reason) => {
//     const cert = CertificateModule.getCertificate(certID);
    
//     if (!cert) {
//       return { success: false, message: 'Certificate not found' };
//     }
    
//     if (cert.issuerID !== issuerID) {
//       return { success: false, message: 'Unauthorized: You can only revoke certificates you issued' };
//     }
    
//     if (cert.status === 'revoked') {
//       return { success: false, message: 'Certificate already revoked' };
//     }
    
//     cert.status = 'revoked';
//     const revocationRecord = {
//       certID,
//       revokedBy: issuerID,
//       revokedAt: new Date().toISOString(),
//       reason
//     };
    
//     DATABASE.revocationRecords.push(revocationRecord);
//     AuditModule.log('certificate_revoked', certID, issuerID, { reason });
    
//     return { success: true, message: 'Certificate revoked successfully' };
//   }
// };

// // ============================================================================
// // AUDIT & LOGGING MODULE (Module 7)
// // ============================================================================
// const AuditModule = {
//   log: (action, certID, userID, details) => {
//     const logEntry = {
//       id: Date.now() + Math.random(),
//       action,
//       certID,
//       userID,
//       timestamp: new Date().toISOString(),
//       details
//     };
    
//     DATABASE.verificationLogs.push(logEntry);
//   },
  
//   getLogs: (filter = {}) => {
//     let logs = [...DATABASE.verificationLogs];
    
//     if (filter.certID) {
//       logs = logs.filter(log => log.certID === filter.certID);
//     }
    
//     return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
//   }
// };

// // ============================================================================
// // USER & ROLE MANAGEMENT MODULE (Module 2)
// // ============================================================================
// const UserModule = {
//   authenticate: (username, password) => {
//     const user = DATABASE.users.find(u => u.username === username && u.password === password);
//     if (user) {
//       AuditModule.log('user_login', null, user.id, { username });
//       return { success: true, user: { ...user, password: undefined } };
//     }
//     return { success: false, message: 'Invalid credentials' };
//   },
  
//   authorize: (user, action) => {
//     const permissions = {
//       issuer: ['create_certificate', 'revoke_certificate', 'view_certificates', 'view_logs'],
//       holder: ['view_own_certificates'],
//       verifier: ['verify_certificate', 'view_logs']
//     };
    
//     return permissions[user.role]?.includes(action) || false;
//   }
// };

// // ============================================================================
// // MAIN APPLICATION COMPONENT (Module 1 - UI Layer)
// // ============================================================================
// export default function CertificateManagementSystem() {
//   const [currentUser, setCurrentUser] = useState(null);
//   const [loginForm, setLoginForm] = useState({ username: '', password: '' });
//   const [activeTab, setActiveTab] = useState('dashboard');
  
//   // Certificate form state
//   const [certForm, setCertForm] = useState({ holderName: '', title: '', file: null });
//   const [verifyID, setVerifyID] = useState('');
//   const [verificationResult, setVerificationResult] = useState(null);
//   const [revokeForm, setRevokeForm] = useState({ certID: '', reason: '' });
//   const [notification, setNotification] = useState(null);

//   const showNotification = (message, type = 'info') => {
//     setNotification({ message, type });
//     setTimeout(() => setNotification(null), 4000);
//   };

//   // const handleLogin = (e) => {
//   //   e.preventDefault();
//   //   const result = UserModule.authenticate(loginForm.username, loginForm.password);
//   //   if (result.success) {
//   //     setCurrentUser(result.user);
//   //     showNotification(`Welcome, ${result.user.name}!`, 'success');
//   //   } else {
//   //     showNotification(result.message, 'error');
//   //   }
//   // };
//   const handleLogin = async (e) => {
//   e.preventDefault();

//   try {
//     const response = await fetch("http://127.0.0.1:8000/auth/login/", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({
//         username: loginForm.username,
//         password: loginForm.password,
//       }),
//     });

//     if (!response.ok) {
//       throw new Error("Invalid credentials");
//     }

//     const data = await response.json();

//     // Store JWT tokens
//     localStorage.setItem("access", data.tokens.access);
//     localStorage.setItem("refresh", data.tokens.refresh);

//     // Set logged-in user
//     setCurrentUser(data.user);

//     showNotification(`Welcome, ${data.user.username}!`, "success");
//   } catch (error) {
//     showNotification("Login failed. Check username/password.", "error");
//   }
// };


//   const handleLogout = () => {
//     AuditModule.log('user_logout', null, currentUser.id, {});
//     setCurrentUser(null);
//     setActiveTab('dashboard');
//     showNotification('Logged out successfully', 'info');
//   };

//   // const handleCreateCertificate = (e) => {
//   //   e.preventDefault();
//   //   if (!UserModule.authorize(currentUser, 'create_certificate')) {
//   //     showNotification('Unauthorized action', 'error');
//   //     return;
//   //   }
    
//   //   const cert = CertificateModule.createCertificate(
//   //     currentUser.id,
//   //     certForm.holderName,
//   //     certForm.title,
//   //     certForm.file
//   //   );
    
//   //   showNotification(`Certificate ${cert.id} created successfully!`, 'success');
//   //   setCertForm({ holderName: '', title: '', file: null });
//   // };
//   const handleCreateCertificate = async (e) => {
//   e.preventDefault();

//   if (!UserModule.authorize(currentUser, 'create_certificate')) {
//     showNotification('Unauthorized action', 'error');
//     return;
//   }

//   try {
//     const cert = await CertificateModule.createCertificate(
//       currentUser.id,
//       certForm.holderName,
//       certForm.title,
//       certForm.file
//     );

//     showNotification(`Certificate created successfully!`, 'success');

//     setCertForm({ holderName: '', title: '', file: null });

//   } catch (error) {
//     console.error(error);
//     showNotification('Failed to create certificate', 'error');
//   }
// };


//   const handleVerify = (e) => {
//     e.preventDefault();
//     const result = VerificationModule.verifyCertificate(verifyID, currentUser.id);
//     setVerificationResult(result);
//     setVerifyID('');
//   };

//   const handleRevoke = (e) => {
//     e.preventDefault();
//     const result = RevocationModule.revokeCertificate(
//       revokeForm.certID,
//       currentUser.id,
//       revokeForm.reason
//     );
    
//     showNotification(result.message, result.success ? 'success' : 'error');
//     if (result.success) {
//       setRevokeForm({ certID: '', reason: '' });
//     }
//   };

//   const getUserCertificates = () => {
//     if (currentUser.role === 'issuer') {
//       return DATABASE.certificates.filter(cert => cert.issuerID === currentUser.id);
//     }
//     return DATABASE.certificates.filter(cert => cert.holderName === currentUser.name);
//   };

//   // Login Screen
//   if (!currentUser) {
//     return (
//       <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
//         <div className="absolute inset-0 overflow-hidden pointer-events-none">
//           <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
//           <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
//         </div>
        
//         <div className="w-full max-w-md relative z-10">
//           <div className="text-center mb-8">
//             {/* <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl mb-4 shadow-2xl">
//               <Shield className="w-10 h-10 text-white" />
//             </div> */}
//             <h1 className="text-4xl font-bold text-white mb-2" style={{ fontFamily: 'Georgia, serif' }}>
//               ZeroID
//             </h1>
//             <p className="text-purple-200">Secure Certificate Management System</p>
//           </div>
          
//           <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/20">
//             <form onSubmit={handleLogin} className="space-y-6">
//               <div>
//                 <label className="block text-sm font-medium text-purple-200 mb-2">Username</label>
//                 <input
//                   type="text"
//                   value={loginForm.username}
//                   onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
//                   className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
//                   placeholder="Enter username"
//                   required
//                 />
//               </div>
              
//               <div>
//                 <label className="block text-sm font-medium text-purple-200 mb-2">Password</label>
//                 <input
//                   type="password"
//                   value={loginForm.password}
//                   onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
//                   className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
//                   placeholder="Enter password"
//                   required
//                 />
//               </div>
              
//               <button
//                 type="submit"
//                 className="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
//               >
//                 Sign In
//               </button>
//             </form>
            
//             {/* <div className="mt-6 pt-6 border-t border-white/10">
//               <p className="text-xs text-purple-300 mb-2">Demo Accounts:</p>
//               <div className="space-y-1 text-xs text-purple-200">
//                 <p>• Issuer: issuer1 / pass123</p>
//                 <p>• Holder: holder1 / pass123</p>
//                 <p>• Verifier: verifier1 / pass123</p>
//               </div> */}
//             {/* </div> */}
//           </div>
//         </div>
//       </div>
//     );
//   }

//   // Main Dashboard
//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
//       {/* Notification */}
//       {notification && (
//         <div className={`fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-2xl border-2 animate-slideIn ${
//           notification.type === 'success' ? 'bg-green-50 border-green-500 text-green-800' :
//           notification.type === 'error' ? 'bg-red-50 border-red-500 text-red-800' :
//           'bg-blue-50 border-blue-500 text-blue-800'
//         }`}>
//           {notification.message}
//         </div>
//       )}
      
//       {/* Header */}
//       <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
//         <div className="max-w-7xl mx-auto px-6 py-4">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center space-x-4">
//               {/* <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl shadow-lg">
//                 <Shield className="w-6 h-6 text-white" />
//               </div> */}
//               <div>
//                 <h1 className="text-2xl font-bold text-slate-800" style={{ fontFamily: 'Georgia, serif' }}>
//                   ZeroID
//                 </h1>
//                 <p className="text-sm text-slate-500">Certificate Management Platform</p>
//               </div>
//             </div>
            
//             <div className="flex items-center space-x-4">
//               <div className="text-right">
//                 <p className="text-sm font-semibold text-slate-800">{currentUser.name}</p>
//                 <p className="text-xs text-slate-500 capitalize">{currentUser.role}</p>
//               </div>
//               <button
//                 onClick={handleLogout}
//                 className="flex items-center space-x-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
//               >
//                 <LogOut className="w-4 h-4" />
//                 <span className="text-sm font-medium">Logout</span>
//               </button>
//             </div>
//           </div>
//         </div>
//       </header>

//       {/* Navigation Tabs */}
//       <div className="bg-white border-b border-slate-200">
//         <div className="max-w-7xl mx-auto px-6">
//           <nav className="flex space-x-1">
//             <button
//               onClick={() => setActiveTab('dashboard')}
//               className={`px-6 py-4 text-sm font-medium transition-all ${
//                 activeTab === 'dashboard'
//                   ? 'text-purple-600 border-b-2 border-purple-600'
//                   : 'text-slate-600 hover:text-slate-800'
//               }`}
//             >
//               Dashboard
//             </button>
            
//             {currentUser.role === 'issuer' && (
//               <>
//                 <button
//                   onClick={() => setActiveTab('create')}
//                   className={`px-6 py-4 text-sm font-medium transition-all ${
//                     activeTab === 'create'
//                       ? 'text-purple-600 border-b-2 border-purple-600'
//                       : 'text-slate-600 hover:text-slate-800'
//                   }`}
//                 >
//                   Create Certificate
//                 </button>
//                 <button
//                   onClick={() => setActiveTab('revoke')}
//                   className={`px-6 py-4 text-sm font-medium transition-all ${
//                     activeTab === 'revoke'
//                       ? 'text-purple-600 border-b-2 border-purple-600'
//                       : 'text-slate-600 hover:text-slate-800'
//                   }`}
//                 >
//                   Revoke
//                 </button>
//               </>
//             )}
            
//             {currentUser.role === 'verifier' && (
//               <button
//                 onClick={() => setActiveTab('verify')}
//                 className={`px-6 py-4 text-sm font-medium transition-all ${
//                   activeTab === 'verify'
//                     ? 'text-purple-600 border-b-2 border-purple-600'
//                     : 'text-slate-600 hover:text-slate-800'
//                 }`}
//               >
//                 Verify Certificate
//               </button>
//             )}
            
//             <button
//               onClick={() => setActiveTab('logs')}
//               className={`px-6 py-4 text-sm font-medium transition-all ${
//                 activeTab === 'logs'
//                   ? 'text-purple-600 border-b-2 border-purple-600'
//                   : 'text-slate-600 hover:text-slate-800'
//               }`}
//             >
//               Audit Logs
//             </button>
//           </nav>
//         </div>
//       </div>

//       {/* Main Content */}
//       <main className="max-w-7xl mx-auto px-6 py-8">
        
//         {/* Dashboard Tab */}
//         {activeTab === 'dashboard' && (
//           <div className="space-y-6">
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//               <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
//                 <div className="flex items-center justify-between mb-4">
//                   <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
//                     <FileText className="w-6 h-6 text-purple-600" />
//                   </div>
//                   <span className="text-3xl font-bold text-purple-600">{DATABASE.certificates.length}</span>
//                 </div>
//                 <h3 className="text-sm font-medium text-slate-600">Total Certificates</h3>
//               </div>
              
//               <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
//                 <div className="flex items-center justify-between mb-4">
//                   <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
//                     <CheckCircle className="w-6 h-6 text-green-600" />
//                   </div>
//                   <span className="text-3xl font-bold text-green-600">
//                     {DATABASE.certificates.filter(c => c.status === 'valid').length}
//                   </span>
//                 </div>
//                 <h3 className="text-sm font-medium text-slate-600">Valid Certificates</h3>
//               </div>
              
//               <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
//                 <div className="flex items-center justify-between mb-4">
//                   <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
//                     <XCircle className="w-6 h-6 text-red-600" />
//                   </div>
//                   <span className="text-3xl font-bold text-red-600">
//                     {DATABASE.certificates.filter(c => c.status === 'revoked').length}
//                   </span>
//                 </div>
//                 <h3 className="text-sm font-medium text-slate-600">Revoked Certificates</h3>
//               </div>
//             </div>

//             <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
//               <div className="px-6 py-4 border-b border-slate-200">
//                 <h2 className="text-lg font-semibold text-slate-800">
//                   {currentUser.role === 'issuer' ? 'My Issued Certificates' : 'My Certificates'}
//                 </h2>
//               </div>
              
//               <div className="p-6">
//                 {getUserCertificates().length === 0 ? (
//                   <div className="text-center py-12">
//                     <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
//                     <p className="text-slate-500">No certificates found</p>
//                   </div>
//                 ) : (
//                   <div className="space-y-3">
//                     {getUserCertificates().map(cert => (
//                       <div key={cert.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-purple-300 transition-colors">
//                         <div className="flex-1">
//                           <div className="flex items-center space-x-3 mb-2">
//                             <h3 className="font-semibold text-slate-800">{cert.title}</h3>
//                             <span className={`px-3 py-1 rounded-full text-xs font-medium ${
//                               cert.status === 'valid'
//                                 ? 'bg-green-100 text-green-700'
//                                 : 'bg-red-100 text-red-700'
//                             }`}>
//                               {cert.status}
//                             </span>
//                           </div>
//                           <p className="text-sm text-slate-600">Holder: {cert.holderName}</p>
//                           <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500">
//                             <span>ID: {cert.id}</span>
//                             <span>Issued: {new Date(cert.issuedDate).toLocaleDateString()}</span>
//                           </div>
//                         </div>
//                         <div className="flex items-center space-x-2">
//                           <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
//                             <Shield className="w-5 h-5 text-purple-600" />
//                           </div>
//                         </div>
//                       </div>
//                     ))}
//                   </div>
//                 )}
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Create Certificate Tab */}
//         {activeTab === 'create' && currentUser.role === 'issuer' && (
//           <div className="max-w-2xl">
//             <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
//               <div className="px-6 py-4 border-b border-slate-200">
//                 <h2 className="text-lg font-semibold text-slate-800">Issue New Certificate</h2>
//               </div>
              
//               <form onSubmit={handleCreateCertificate} className="p-6 space-y-6">
//                 <div>
//                   <label className="block text-sm font-medium text-slate-700 mb-2">
//                     Certificate Holder Name
//                   </label>
//                   <input
//                     type="text"
//                     value={certForm.holderName}
//                     onChange={(e) => setCertForm({ ...certForm, holderName: e.target.value })}
//                     className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                     placeholder="John Doe"
//                     required
//                   />
//                 </div>
                
//                 <div>
//                   <label className="block text-sm font-medium text-slate-700 mb-2">
//                     Certificate Title
//                   </label>
//                   <input
//                     type="text"
//                     value={certForm.title}
//                     onChange={(e) => setCertForm({ ...certForm, title: e.target.value })}
//                     className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                     placeholder="Bachelor of Science in Computer Science"
//                     required
//                   />
//                 </div>
                
//                 <div>
//                   <label className="block text-sm font-medium text-slate-700 mb-2">
//                     Upload Certificate File
//                   </label>
//                   <div className="relative">
//                     <input
//                       type="file"
//                       onChange={(e) => setCertForm({ ...certForm, file: e.target.files[0] })}
//                       className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                       accept=".pdf,.jpg,.jpeg,.png"
//                       required
//                     />
//                   </div>
//                   <p className="text-xs text-slate-500 mt-2">Supported formats: PDF, JPG, PNG</p>
//                 </div>
                
//                 <button
//                   type="submit"
//                   className="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transition-all shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center space-x-2"
//                 >
//                   <Upload className="w-5 h-5" />
//                   <span>Issue Certificate</span>
//                 </button>
//               </form>
//             </div>
//           </div>
//         )}

//         {/* Verify Certificate Tab */}
//         {activeTab === 'verify' && (
//           <div className="max-w-2xl">
//             <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
//               <div className="px-6 py-4 border-b border-slate-200">
//                 <h2 className="text-lg font-semibold text-slate-800">Verify Certificate</h2>
//               </div>
              
//               <form onSubmit={handleVerify} className="p-6 space-y-6">
//                 <div>
//                   <label className="block text-sm font-medium text-slate-700 mb-2">
//                     Certificate ID
//                   </label>
//                   <input
//                     type="text"
//                     value={verifyID}
//                     onChange={(e) => setVerifyID(e.target.value)}
//                     className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                     placeholder="CERT-XXXXXXXXXX"
//                     required
//                   />
//                 </div>
                
//                 <button
//                   type="submit"
//                   className="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transition-all shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center space-x-2"
//                 >
//                   <Eye className="w-5 h-5" />
//                   <span>Verify Certificate</span>
//                 </button>
//               </form>
              
//               {verificationResult && (
//                 <div className="px-6 pb-6">
//                   <div className={`p-6 rounded-xl border-2 ${
//                     verificationResult.valid
//                       ? 'bg-green-50 border-green-500'
//                       : 'bg-red-50 border-red-500'
//                   }`}>
//                     <div className="flex items-center space-x-3 mb-4">
//                       {verificationResult.valid ? (
//                         <CheckCircle className="w-8 h-8 text-green-600" />
//                       ) : (
//                         <XCircle className="w-8 h-8 text-red-600" />
//                       )}
//                       <h3 className={`text-xl font-bold ${
//                         verificationResult.valid ? 'text-green-800' : 'text-red-800'
//                       }`}>
//                         {verificationResult.valid ? 'Certificate Valid' : 'Certificate Invalid'}
//                       </h3>
//                     </div>
                    
//                     {verificationResult.certificate && (
//                       <div className="space-y-2 text-sm">
//                         <p className={verificationResult.valid ? 'text-green-700' : 'text-red-700'}>
//                           <strong>Title:</strong> {verificationResult.certificate.title}
//                         </p>
//                         <p className={verificationResult.valid ? 'text-green-700' : 'text-red-700'}>
//                           <strong>Holder:</strong> {verificationResult.certificate.holderName}
//                         </p>
//                         <p className={verificationResult.valid ? 'text-green-700' : 'text-red-700'}>
//                           <strong>Issued:</strong> {new Date(verificationResult.certificate.issuedDate).toLocaleDateString()}
//                         </p>
//                         <p className={verificationResult.valid ? 'text-green-700' : 'text-red-700'}>
//                           <strong>Hash Match:</strong> {verificationResult.hashMatch ? 'Yes' : 'No'}
//                         </p>
//                         <p className={verificationResult.valid ? 'text-green-700' : 'text-red-700'}>
//                           <strong>Status:</strong> {verificationResult.isRevoked ? 'Revoked' : 'Active'}
//                         </p>
//                       </div>
//                     )}
                    
//                     {!verificationResult.certificate && (
//                       <p className="text-red-700">{verificationResult.reason}</p>
//                     )}
//                   </div>
//                 </div>
//               )}
//             </div>
//           </div>
//         )}

//         {/* Revoke Certificate Tab */}
//         {activeTab === 'revoke' && currentUser.role === 'issuer' && (
//           <div className="max-w-2xl">
//             <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
//               <div className="px-6 py-4 border-b border-slate-200 bg-red-50">
//                 <div className="flex items-center space-x-3">
//                   <AlertTriangle className="w-6 h-6 text-red-600" />
//                   <h2 className="text-lg font-semibold text-red-800">Revoke Certificate</h2>
//                 </div>
//               </div>
              
//               <form onSubmit={handleRevoke} className="p-6 space-y-6">
//                 <div>
//                   <label className="block text-sm font-medium text-slate-700 mb-2">
//                     Certificate ID
//                   </label>
//                   <input
//                     type="text"
//                     value={revokeForm.certID}
//                     onChange={(e) => setRevokeForm({ ...revokeForm, certID: e.target.value })}
//                     className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
//                     placeholder="CERT-XXXXXXXXXX"
//                     required
//                   />
//                 </div>
                
//                 <div>
//                   <label className="block text-sm font-medium text-slate-700 mb-2">
//                     Revocation Reason
//                   </label>
//                   <textarea
//                     value={revokeForm.reason}
//                     onChange={(e) => setRevokeForm({ ...revokeForm, reason: e.target.value })}
//                     className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent h-24"
//                     placeholder="Explain why this certificate is being revoked..."
//                     required
//                   />
//                 </div>
                
//                 <button
//                   type="submit"
//                   className="w-full py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-semibold hover:from-red-600 hover:to-red-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center space-x-2"
//                 >
//                   <XCircle className="w-5 h-5" />
//                   <span>Revoke Certificate</span>
//                 </button>
//               </form>
//             </div>
//           </div>
//         )}

//         {/* Audit Logs Tab */}
//         {activeTab === 'logs' && (
//           <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
//             <div className="px-6 py-4 border-b border-slate-200">
//               <h2 className="text-lg font-semibold text-slate-800">Audit Trail</h2>
//             </div>
            
//             <div className="p-6">
//               {AuditModule.getLogs().length === 0 ? (
//                 <div className="text-center py-12">
//                   <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
//                   <p className="text-slate-500">No audit logs available</p>
//                 </div>
//               ) : (
//                 <div className="space-y-3 max-h-96 overflow-y-auto">
//                   {AuditModule.getLogs().map(log => (
//                     <div key={log.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
//                       <div className="flex items-start justify-between mb-2">
//                         <div className="flex items-center space-x-3">
//                           <div className={`w-2 h-2 rounded-full ${
//                             log.action.includes('issued') ? 'bg-green-500' :
//                             log.action.includes('revoked') ? 'bg-red-500' :
//                             log.action.includes('verified') || log.action.includes('verification') ? 'bg-blue-500' :
//                             'bg-slate-400'
//                           }`}></div>
//                           <span className="font-medium text-slate-800 capitalize">
//                             {log.action.replace(/_/g, ' ')}
//                           </span>
//                         </div>
//                         <span className="text-xs text-slate-500">
//                           {new Date(log.timestamp).toLocaleString()}
//                         </span>
//                       </div>
//                       {log.certID && (
//                         <p className="text-sm text-slate-600 ml-5">
//                           Certificate: <span className="font-mono text-xs">{log.certID}</span>
//                         </p>
//                       )}
//                       {log.details && Object.keys(log.details).length > 0 && (
//                         <div className="text-xs text-slate-500 ml-5 mt-1">
//                           {JSON.stringify(log.details, null, 2).slice(0, 100)}...
//                         </div>
//                       )}
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </div>
//           </div>
//         )}
//       </main>
      
//       <style>{`
//         @keyframes slideIn {
//           from {
//             transform: translateX(400px);
//             opacity: 0;
//           }
//           to {
//             transform: translateX(0);
//             opacity: 1;
//           }
//         }
        
//         .animate-slideIn {
//           animation: slideIn 0.3s ease-out;
//         }
//       `}</style>
//     </div>
//   );
// }



import React, { useState, useEffect } from "react";
import {
  Upload,
  CheckCircle,
  XCircle,
  Shield,
  FileText,
  Eye,
  AlertTriangle,
  LogOut,
} from "lucide-react";

/* ================================
   API CONFIG
================================ */

const API_BASE = "http://127.0.0.1:8000";

async function api(url, method = "GET", body = null, auth = true) {
  const headers = {};

  if (auth) {
    const token = localStorage.getItem("access");
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const options = { method, headers };

  if (body) {
    if (body instanceof FormData) {
      options.body = body;
    } else {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
  }

  const response = await fetch(API_BASE + url, options);

  if (!response.ok) {
    const errorText = await response.text();
    console.log("Backend error:", errorText);
    throw new Error("API error");
  }

  return response.json();
}

/* ================================
   CERTIFICATE MODULE (BACKEND)
================================ */

const CertificateModule = {
  createCertificate: async (holderName, title, file) => {
    const formData = new FormData();
    formData.append("holder_name", holderName);
    formData.append("title", title);
    formData.append("certificate_file", file);

    return await api("/certificates/", "POST", formData);
  },

  listCertificates: async () => {
    return await api("/certificates/");
  },
};

/* ================================
   MAIN COMPONENT
================================ */

export default function CertificateManagementSystem() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [certificates, setCertificates] = useState([]);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [certForm, setCertForm] = useState({
    holderName: "",
    title: "",
    file: null,
  });
  const [notification, setNotification] = useState(null);

  /* ================================
     LOAD CERTIFICATES AFTER LOGIN
  ================================= */

  useEffect(() => {
    if (currentUser) {
      loadCertificates();
    }
  }, [currentUser]);

  const loadCertificates = async () => {
    try {
      // const data = await CertificateModule.listCertificates();
      // setCertificates(data);
      const data = await CertificateModule.listCertificates();
      setCertificates(data.results || []);
    } catch (err) {
      console.error(err);
    }
  };

  /* ================================
     LOGIN
  ================================= */

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm),
      });

      if (!response.ok) throw new Error("Invalid credentials");

      const data = await response.json();

      localStorage.setItem("access", data.tokens.access);
      localStorage.setItem("refresh", data.tokens.refresh);

      setCurrentUser(data.user);
      showNotification("Login successful!", "success");
    } catch (error) {
      showNotification("Login failed", "error");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setCurrentUser(null);
    setCertificates([]);
  };

  /* ================================
     CREATE CERTIFICATE
  ================================= */

  const handleCreateCertificate = async (e) => {
    e.preventDefault();

    try {
      const newCert = await CertificateModule.createCertificate(
        certForm.holderName,
        certForm.title,
        certForm.file
      );

      setCertificates((prev) => [newCert, ...prev]);

      showNotification("Certificate created successfully!", "success");
      setCertForm({ holderName: "", title: "", file: null });
    } catch (error) {
      showNotification("Failed to create certificate", "error");
    }
  };

  /* ================================
     NOTIFICATION
  ================================= */

  const showNotification = (message, type = "info") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  /* ================================
     LOGIN SCREEN
  ================================= */

  if (!currentUser) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <form
          onSubmit={handleLogin}
          className="bg-white p-8 rounded-xl w-96 space-y-4"
        >
          <h2 className="text-xl font-bold text-center">ZeroID Login</h2>

          <input
            type="text"
            placeholder="Username"
            value={loginForm.username}
            onChange={(e) =>
              setLoginForm({ ...loginForm, username: e.target.value })
            }
            className="w-full border p-2 rounded"
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={loginForm.password}
            onChange={(e) =>
              setLoginForm({ ...loginForm, password: e.target.value })
            }
            className="w-full border p-2 rounded"
            required
          />

          <button className="w-full bg-purple-600 text-white py-2 rounded">
            Login
          </button>
        </form>
      </div>
    );
  }

  /* ================================
     MAIN DASHBOARD
  ================================= */

  return (
    <div className="min-h-screen bg-slate-100">

      {notification && (
        <div className="fixed top-4 right-4 bg-white p-4 shadow rounded">
          {notification.message}
        </div>
      )}

      {/* HEADER */}
      <header className="bg-white p-4 flex justify-between shadow">
        <h1 className="font-bold text-xl">ZeroID</h1>
        <button onClick={handleLogout} className="flex items-center gap-2">
          <LogOut size={16} /> Logout
        </button>
      </header>

      <main className="p-8 space-y-8">

        {/* STATS */}
        <div className="grid grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded shadow">
            <p className="text-sm">Total Certificates</p>
            <p className="text-2xl font-bold">{certificates.length}</p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <p className="text-sm">Valid</p>
            <p className="text-2xl font-bold text-green-600">
              {certificates.filter(c => c.status === "valid").length}
            </p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <p className="text-sm">Revoked</p>
            <p className="text-2xl font-bold text-red-600">
              {certificates.filter(c => c.status === "revoked").length}
            </p>
          </div>
        </div>

        {/* CREATE CERTIFICATE */}
        {currentUser.role === "issuer" && (
          <div className="bg-white p-6 rounded shadow max-w-xl">
            <h2 className="font-semibold mb-4">Issue Certificate</h2>

            <form onSubmit={handleCreateCertificate} className="space-y-4">
              <input
                type="text"
                placeholder="Holder Name"
                value={certForm.holderName}
                onChange={(e) =>
                  setCertForm({ ...certForm, holderName: e.target.value })
                }
                className="w-full border p-2 rounded"
                required
              />

              <input
                type="text"
                placeholder="Title"
                value={certForm.title}
                onChange={(e) =>
                  setCertForm({ ...certForm, title: e.target.value })
                }
                className="w-full border p-2 rounded"
                required
              />

              <input
                type="file"
                onChange={(e) =>
                  setCertForm({ ...certForm, file: e.target.files[0] })
                }
                className="w-full"
                required
              />

              <button className="bg-purple-600 text-white px-4 py-2 rounded flex items-center gap-2">
                <Upload size={16} />
                Issue Certificate
              </button>
            </form>
          </div>
        )}

        {/* CERTIFICATE LIST */}
        <div className="bg-white p-6 rounded shadow">
          <h2 className="font-semibold mb-4">Certificates</h2>

          {certificates.length === 0 ? (
            <p>No certificates yet</p>
          ) : (
            certificates.map((cert) => (
              <div
                key={cert.id}
                className="border p-4 rounded mb-3 flex justify-between"
              >
                <div>
                  <p className="font-semibold">{cert.title}</p>
                  <p className="text-sm text-gray-500">
                    Holder: {cert.holder_name}
                  </p>
                </div>

                <span
                  className={`px-3 py-1 text-sm rounded ${
                    cert.status === "valid"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {cert.status}
                </span>
              </div>
            ))
          )}
        </div>

      </main>
    </div>
  );
}
