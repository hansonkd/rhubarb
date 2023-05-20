(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[821],{8560:function(e,n,s){(window.__NEXT_P=window.__NEXT_P||[]).push(["/contrib/auditing",function(){return s(9118)}])},5484:function(e,n,s){"use strict";var i=s(2322);n.Z={logo:(0,i.jsx)("span",{children:"Rhubarb Documentation"}),project:{link:"https://github.com/hansonkd/rhubarb"},docsRepositoryBase:"https://github.com/hansonkd/rhubarb"}},9118:function(e,n,s){"use strict";s.r(n);var i=s(2322),t=s(8287),a=s(6582),o=s(5484);s(6908);var r=s(5392);s(6577);let l={MDXContent:function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},{wrapper:n}=Object.assign({},(0,r.ah)(),e.components);return n?(0,i.jsx)(n,{...e,children:(0,i.jsx)(c,{...e})}):c(e)},pageOpts:{filePath:"pages/contrib/auditing.mdx",route:"/contrib/auditing",headings:[{depth:1,value:"Auditing",id:"auditing"},{depth:2,value:"Builtin Events",id:"builtin-events"},{depth:2,value:"Custom Events",id:"custom-events"},{depth:2,value:"Config",id:"config"}],timestamp:1684534015e3,pageMap:[{kind:"Meta",data:{index:"Rhubarb",getting_started:"Getting Started",tables:"Working with Tables",fields:"Fields and Relations",auth:"User Authentication",pkg:"Other Integrations",advanced:"Advanced Usage",github_link:{title:"Github",href:"https://github.com/hansonkd/rhubarb"}}},{kind:"Folder",name:"advanced",route:"/advanced",children:[{kind:"Meta",data:{"default-where-clause":"Automatic Filtering","sql-functions":"SQL Functions",multi:"Multiple Selections without GQL","field-permissions":"Column and Field Permissions"}},{kind:"MdxPage",name:"default-where-clause",route:"/advanced/default-where-clause"},{kind:"MdxPage",name:"field-permissions",route:"/advanced/field-permissions"},{kind:"MdxPage",name:"multi",route:"/advanced/multi"},{kind:"MdxPage",name:"sql-functions",route:"/advanced/sql-functions"}]},{kind:"Folder",name:"auth",route:"/auth",children:[{kind:"Meta",data:{using:"Adding User Auth",impersonate:"Impersonating Users"}},{kind:"MdxPage",name:"impersonate",route:"/auth/impersonate"},{kind:"MdxPage",name:"using",route:"/auth/using"}]},{kind:"Folder",name:"contrib",route:"/contrib",children:[{kind:"MdxPage",name:"arq-tasks",route:"/contrib/arq-tasks"},{kind:"MdxPage",name:"auditing",route:"/contrib/auditing"},{kind:"MdxPage",name:"email",route:"/contrib/email"},{kind:"MdxPage",name:"redis",route:"/contrib/redis"},{kind:"MdxPage",name:"starlette",route:"/contrib/starlette"},{kind:"MdxPage",name:"webauthn",route:"/contrib/webauthn"},{kind:"Meta",data:{"arq-tasks":"Arq Tasks",auditing:"Auditing",email:"Email",redis:"Redis",starlette:"Starlette",webauthn:"Webauthn"}}]},{kind:"Folder",name:"fields",route:"/fields",children:[{kind:"Meta",data:{virtual_columns:"Virtual Columns and Fields",relations:"Relations and References to other Models",mutations:"Mutations",aggregations:"Aggregations","python-based-fields":"Computations in Python"}},{kind:"MdxPage",name:"aggregations",route:"/fields/aggregations"},{kind:"MdxPage",name:"mutations",route:"/fields/mutations"},{kind:"MdxPage",name:"python-based-fields",route:"/fields/python-based-fields"},{kind:"MdxPage",name:"relations",route:"/fields/relations"},{kind:"MdxPage",name:"virtual_columns",route:"/fields/virtual_columns"}]},{kind:"Folder",name:"getting_started",route:"/getting_started",children:[{kind:"Meta",data:{installation:"Installation","basic-usage":"Basic Usage","querying-data":"Querying Data",config:"Environment Configuration",optimizations:"Optimizations"}},{kind:"MdxPage",name:"basic-usage",route:"/getting_started/basic-usage"},{kind:"MdxPage",name:"config",route:"/getting_started/config"},{kind:"MdxPage",name:"installation",route:"/getting_started/installation"},{kind:"MdxPage",name:"optimizations",route:"/getting_started/optimizations"},{kind:"MdxPage",name:"querying-data",route:"/getting_started/querying-data"}]},{kind:"MdxPage",name:"index",route:"/"},{kind:"Folder",name:"tables",route:"/tables",children:[{kind:"Meta",data:{table_basics:"Table Basics",base_models:"Base Models",migrations:"Migrations",types:"Python and SQL Types",custom_types:"Custom Types","public-private-schemas":"Private and Public Schemas"}},{kind:"MdxPage",name:"base_models",route:"/tables/base_models"},{kind:"MdxPage",name:"custom_types",route:"/tables/custom_types"},{kind:"MdxPage",name:"migrations",route:"/tables/migrations"},{kind:"MdxPage",name:"public-private-schemas",route:"/tables/public-private-schemas"},{kind:"MdxPage",name:"table_basics",route:"/tables/table_basics"},{kind:"MdxPage",name:"types",route:"/tables/types"}]}],flexsearch:{codeblocks:!0},title:"Auditing"},pageNextRoute:"/contrib/auditing",nextraLayout:a.ZP,themeConfig:o.Z};function c(e){let n=Object.assign({h1:"h1",p:"p",code:"code",pre:"pre",span:"span",h2:"h2"},(0,r.ah)(),e.components);return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(n.h1,{children:"Auditing"}),"\n",(0,i.jsx)(n.p,{children:"Rhubarb comes with built-in Auditing extension that can record all queries, subscriptions, and mutations."}),"\n",(0,i.jsx)(n.p,{children:"By default, the auditing extension will use a new connection to the database different from the current executing connection of the schema. This is to prevent Transaction rollbacks from deleting written audit events. It also allows you to specify an alternative auditing database (like TimeseriesDB) to silo your events."}),"\n",(0,i.jsxs)(n.p,{children:["The default configuration only logs mutations. This is configurable with ",(0,i.jsx)(n.code,{children:"AuditConfig"}),"."]}),"\n",(0,i.jsx)(n.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(n.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" Schema"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"pkg"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"audit"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"extensions "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" AuditingExtension"})]}),"\n",(0,i.jsx)(n.span,{className:"line",children:" "}),"\n",(0,i.jsx)(n.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"schema "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"Schema"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    query"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"...,"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    mutation"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"...,"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    extensions"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["})]}),"\n",(0,i.jsx)(n.span,{className:"line",children:(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"        AuditingExtension,"})}),"\n",(0,i.jsx)(n.span,{className:"line",children:(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    ]"})}),"\n",(0,i.jsx)(n.span,{className:"line",children:(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})})]})}),"\n",(0,i.jsx)(n.h2,{id:"builtin-events",children:"Builtin Events"}),"\n",(0,i.jsx)(n.p,{children:"Extra events are recorded for login, logout, impersonate, stop_impersonating separately from the GQL mutation when auditing is in (if it is in one)."}),"\n",(0,i.jsx)(n.h2,{id:"custom-events",children:"Custom Events"}),"\n",(0,i.jsxs)(n.p,{children:["You an save custom Audit events with ",(0,i.jsx)(n.code,{children:"rhubarb.pkg.audit.models.log_event"})]}),"\n",(0,i.jsx)(n.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(n.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"log_event"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(event_name"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"my_custom_event"'}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:", variables"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"{"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"wow"'}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:": "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"1"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"})"})]}),"\n",(0,i.jsx)(n.span,{className:"line",children:" "}),"\n",(0,i.jsx)(n.span,{className:"line",children:" "}),"\n",(0,i.jsx)(n.span,{className:"line",children:(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-comment)"},children:"# Passing request will fill in the current user, IP, etc from the request object."})}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"log_event"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(request, event_name"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"my_custom_event"'}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:", variables"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"{"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"wow"'}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:": "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"1"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"})"})]})]})}),"\n",(0,i.jsx)(n.h2,{id:"config",children:"Config"}),"\n",(0,i.jsx)(n.p,{children:"By default, audit will use the same DB configuration as your App. You can configure the audit database by specifying an enviornment variable."}),"\n",(0,i.jsxs)(n.p,{children:[(0,i.jsx)(n.code,{children:"PG_AUDIT_URI"})," - Connection String that describes a Postgres connection (e.g. ",(0,i.jsx)(n.code,{children:"postgres://USER:PASSWORD@HOST:PORT/DATABASE"}),")"]}),"\n",(0,i.jsx)(n.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(n.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"@dataclasses"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"dataclass"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(frozen"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"True"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"AuditConfig"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"    audit_mutations"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"bool"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"True"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"    audit_queries"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"bool"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"False"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"    audit_subscriptions"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"bool"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"False"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"    reuse_conn"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"bool"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-constant)"},children:"False"})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:"    postgres"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" PostgresConfig "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-color-text)"},children:" dataclasses"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"field"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("})]}),"\n",(0,i.jsxs)(n.span,{className:"line",children:[(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"        default_factory"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-keyword)"},children:"=lambda"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:": "}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-function)"},children:"load_postgres_config"}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"PG_AUDIT_URI"'}),(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsx)(n.span,{className:"line",children:(0,i.jsx)(n.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    )"})})]})})]})}n.default=(0,t.j)(l)}},function(e){e.O(0,[774,282,888,179],function(){return e(e.s=8560)}),_N_E=e.O()}]);