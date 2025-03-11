"use strict";var G=Object.create;var E=Object.defineProperty;var j=Object.getOwnPropertyDescriptor;var H=Object.getOwnPropertyNames;var J=Object.getPrototypeOf,K=Object.prototype.hasOwnProperty;var Q=(r,t,e,s)=>{if(t&&typeof t=="object"||typeof t=="function")for(let i of H(t))!K.call(r,i)&&i!==e&&E(r,i,{get:()=>t[i],enumerable:!(s=j(t,i))||s.enumerable});return r};var C=(r,t,e)=>(e=r!=null?G(J(r)):{},Q(t||!r||!r.__esModule?E(e,"default",{value:r,enumerable:!0}):e,r));var D=require("crypto"),U=require("node:net"),V=require("os"),q=C(require("path")),P=C(require("readline"));var O=require("child_process"),M=(r,t)=>{let e,s=!1,i=[t];if(r){let[n,...o]=r.split(" ");e=n,i=[...o,t]}else switch(process.platform){case"win32":e="cmd",s=!0,i=["/c","start",'""',`"${t}"`];break;case"darwin":e="open";break;case"linux":default:e="xdg-open";break}return new Promise((n,o)=>{let a="",c=(0,O.spawn)(e,i,{stdio:"pipe",shell:s,env:{...process.env,ELECTRON_RUN_AS_NODE:void 0}});c.stdout.setEncoding("utf8").on("data",h=>a+=h),c.stderr.setEncoding("utf8").on("data",h=>a+=h),c.on("error",o),c.on("exit",h=>{h!==0?o(new Error(`Failed to open: ${a}`)):n()})})};function x(){return globalThis._VSCODE_NLS_LANGUAGE}var ve=x()==="pseudo"||typeof document<"u"&&document.location&&typeof document.location.hash=="string"&&document.location.hash.indexOf("pseudo=true")>=0;var m="en",S=!1,_=!1,b=!1,Z=!1,ee=!1,F=!1,ne=!1,te=!1,oe=!1,re=!1,v,w=m,k=m,se,u,g=globalThis,l;typeof g.vscode<"u"&&typeof g.vscode.process<"u"?l=g.vscode.process:typeof process<"u"&&typeof process?.versions?.node=="string"&&(l=process);var A=typeof l?.versions?.electron=="string",ie=A&&l?.type==="renderer";if(typeof l=="object"){S=l.platform==="win32",_=l.platform==="darwin",b=l.platform==="linux",Z=b&&!!l.env.SNAP&&!!l.env.SNAP_REVISION,ne=A,oe=!!l.env.CI||!!l.env.BUILD_ARTIFACTSTAGINGDIRECTORY,v=m,w=m;let r=l.env.VSCODE_NLS_CONFIG;if(r)try{let t=JSON.parse(r);v=t.userLocale,k=t.osLocale,w=t.resolvedLanguage||m,se=t.languagePack?.translationsConfigFile}catch{}ee=!0}else typeof navigator=="object"&&!ie?(u=navigator.userAgent,S=u.indexOf("Windows")>=0,_=u.indexOf("Macintosh")>=0,te=(u.indexOf("Macintosh")>=0||u.indexOf("iPad")>=0||u.indexOf("iPhone")>=0)&&!!navigator.maxTouchPoints&&navigator.maxTouchPoints>0,b=u.indexOf("Linux")>=0,re=u?.indexOf("Mobi")>=0,F=!0,w=x()||m,v=navigator.language.toLowerCase(),k=v):console.error("Unable to resolve platform.");var N=0;_?N=1:S?N=3:b&&(N=2);var R=S;var ae=F&&typeof g.importScripts=="function",we=ae?g.origin:void 0;var d=u,p=w,le;(s=>{function r(){return p}s.value=r;function t(){return p.length===2?p==="en":p.length>=3?p[0]==="e"&&p[1]==="n"&&p[2]==="-":!1}s.isDefaultVariant=t;function e(){return p==="en"}s.isDefault=e})(le||={});var ce=typeof g.postMessage=="function"&&!g.importScripts,Se=(()=>{if(ce){let r=[];g.addEventListener("message",e=>{if(e.data&&e.data.vscodeScheduleAsyncWork)for(let s=0,i=r.length;s<i;s++){let n=r[s];if(n.id===e.data.vscodeScheduleAsyncWork){r.splice(s,1),n.callback();return}}});let t=0;return e=>{let s=++t;r.push({id:s,callback:e}),g.postMessage({vscodeScheduleAsyncWork:s},"*")}}return r=>setTimeout(r)})();var de=!!(d&&d.indexOf("Chrome")>=0),Le=!!(d&&d.indexOf("Firefox")>=0),Ie=!!(!de&&d&&d.indexOf("Safari")>=0),Pe=!!(d&&d.indexOf("Edg/")>=0),Ne=!!(d&&d.indexOf("Android")>=0);var W=require("stream"),L=class extends W.Transform{constructor(e){super();this.prefix=[];this.splitSuffix=Buffer.alloc(0);if(typeof e=="string"&&e.length===1)this.splitter=e.charCodeAt(0);else if(typeof e=="number")this.splitter=e;else throw new Error("not implemented here")}_transform(e,s,i){let n=0;for(;n<e.length;){let o=e.indexOf(this.splitter,n);if(o===-1)break;let a=e.subarray(n,o),c=this.prefix.length||this.splitSuffix.length?Buffer.concat([...this.prefix,a,this.splitSuffix]):a;this.push(c),this.prefix.length=0,n=o+1}n<e.length&&this.prefix.push(e.subarray(n)),i()}_flush(e){this.prefix.length&&this.push(Buffer.concat([...this.prefix,this.splitSuffix])),e()}};var T=R?`\r
`:`
`,I=class{constructor(t){this.stream=t;this.methods=new Map;this.pendingRequests=new Map;this.idCounter=0,this.stream.pipe(new L(`
`)).on("data",e=>this.handleData(e)),this.ended=new Promise(e=>this.stream.on("end",e))}registerMethod(t,e){this.methods.set(t,e)}async callMethod(t,e){let s=this.idCounter++,i={id:s,method:t,params:e},n=new Promise((o,a)=>{this.pendingRequests.set(s,{resolve:o,reject:a})});return this.stream.write(JSON.stringify(i)+T),Promise.race([n,this.ended])}async handleData(t){let e=JSON.parse(t.toString());if("method"in e){let{id:s,method:i,params:n}=e,o={id:s};try{if(this.methods.has(i)){let a=await this.methods.get(i)(n);o.result=a}else throw new Error(`Method not found: ${i}`)}catch(a){o.error={code:-1,message:String(a)}}this.stream.write(JSON.stringify(o)+T)}else{let{id:s,result:i,error:n}=e,o=this.pendingRequests.get(s);this.pendingRequests.delete(s),n!==void 0?o?.reject(new Error(n.message)):o?.resolve(i)}}};var[Ae,Re,ue,ge,...y]=process.argv;var f={"--print":!1,"--no-cache":!1,"--help":!1,"--save":!1,"--once":!1};for(;y.length&&f.hasOwnProperty(y[0]);)f[y.shift()]=!0;(!y.length||f["--help"])&&(console.log(`Usage: copilot-debug [${Object.keys(f).join("] [")}] <command> <args...>`),console.log(""),console.log("Options:"),console.log("  --print     Print the generated configuration without running it"),console.log("  --no-cache  Generate a new configuration without checking the cache."),console.log("  --save      Save the configuration to your launch.json."),console.log("  --once      Exit after the debug session ends."),console.log("  --help      Print this help."),process.exit(f["--help"]?0:1));var z=P.createInterface({input:process.stdin,output:process.stdout});P.emitKeypressEvents(process.stdin);process.stdin.setRawMode(!0);var fe=(0,U.createServer)(r=>{clearInterval(pe);let t=new I(r);t.registerMethod("output",({category:n,output:o})=>(n==="stderr"?process.stderr.write(o):n==="stdout"?process.stdout.write(o):n!=="telemetry"&&o&&console.log(o),Promise.resolve())),t.registerMethod("exit",async({code:n,error:o})=>{o&&!e&&console.error(o),await Promise.all([new Promise(a=>process.stdout.end(a)),new Promise(a=>process.stderr.end(a))]).then(()=>process.exit(n))});let e=!1;function s(){e?process.exit(1):(e=!0,r.end(()=>{process.exit(1)}))}process.on("SIGINT",s),process.stdin.on("keypress",(n,o)=>{(o.sequence===""||o.name==="c"&&(o.ctrl||o.meta))&&s()}),t.registerMethod("question",n=>new Promise(o=>{if(n.singleKey){console.log(n.message);let a=c=>{c&&(process.stdout.write("\b"),process.stdin.off("keypress",a),o(c===`
`||c==="\r"?"Enter":c?.toUpperCase()||""))};process.stdin.on("keypress",a)}else z.question(`${n.message} [${n.defaultValue}] `,o)})),t.registerMethod("confirm",n=>new Promise(o=>{z.question(`${n.message} [${n.defaultValue?"Y/n":"y/N"}] `,a=>{o(a===""?n.defaultValue:a.toLowerCase()[0]==="y")})}));let i={cwd:process.cwd(),args:y,forceNew:f["--no-cache"],printOnly:f["--print"],save:f["--save"],once:f["--once"]};t.callMethod("start",i)}),pe=setInterval(()=>{console.log("> Waiting for VS Code to connect...")},2e3),B=`copilot-dbg.${process.pid}-${(0,D.randomBytes)(4).toString("hex")}.sock`,$=q.join(process.platform==="win32"?"\\\\.\\pipe\\":(0,V.tmpdir)(),B);fe.listen($,()=>{M(ge,ue+(process.platform==="win32"?`/${B}`:$)).then(()=>{},r=>{console.error("Failed to open the activation URI:",r),process.exit(1)})});
//!!! DO NOT modify, this file was COPIED from 'microsoft/vscode'
