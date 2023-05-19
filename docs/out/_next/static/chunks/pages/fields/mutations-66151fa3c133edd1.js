(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[41],{5382:function(s,e,n){(window.__NEXT_P=window.__NEXT_P||[]).push(["/fields/mutations",function(){return n(9217)}])},5484:function(s,e,n){"use strict";var i=n(2322);e.Z={logo:(0,i.jsx)("span",{children:"Rhubarb Documentation"}),project:{link:"https://github.com/hansonkd/rhubarb"}}},9217:function(s,e,n){"use strict";n.r(e);var i=n(2322),o=n(8287),t=n(6582),r=n(5484);n(6908);var l=n(5392);n(6577);let a={MDXContent:function(){let s=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},{wrapper:e}=Object.assign({},(0,l.ah)(),s.components);return e?(0,i.jsx)(e,{...s,children:(0,i.jsx)(c,{...s})}):c(s)},pageOpts:{filePath:"pages/fields/mutations.mdx",route:"/fields/mutations",headings:[{depth:1,value:"Mutations",id:"mutations"}],timestamp:1683702824e3,pageMap:[{kind:"Meta",data:{index:"Rhubarb",getting_started:"Getting Started",tables:"Working with Tables",fields:"Fields and Relations",auth:"User Authentication",pkg:"Other Integrations",advanced:"Advanced Usage",github_link:{title:"Github",href:"https://github.com/hansonkd/rhubarb"}}},{kind:"Folder",name:"advanced",route:"/advanced",children:[{kind:"Meta",data:{"default-where-clause":"Automatic Filtering","sql-functions":"SQL Functions",multi:"Multiple Selections without GQL","field-permissions":"Column and Field Permissions"}},{kind:"MdxPage",name:"default-where-clause",route:"/advanced/default-where-clause"},{kind:"MdxPage",name:"field-permissions",route:"/advanced/field-permissions"},{kind:"MdxPage",name:"multi",route:"/advanced/multi"},{kind:"MdxPage",name:"sql-functions",route:"/advanced/sql-functions"}]},{kind:"Folder",name:"auth",route:"/auth",children:[{kind:"Meta",data:{using:"Adding User Auth",impersonate:"Impersonating Users"}},{kind:"MdxPage",name:"impersonate",route:"/auth/impersonate"},{kind:"MdxPage",name:"using",route:"/auth/using"}]},{kind:"Folder",name:"contrib",route:"/contrib",children:[{kind:"MdxPage",name:"arq-tasks",route:"/contrib/arq-tasks"},{kind:"MdxPage",name:"auditing",route:"/contrib/auditing"},{kind:"MdxPage",name:"email",route:"/contrib/email"},{kind:"MdxPage",name:"redis",route:"/contrib/redis"},{kind:"MdxPage",name:"starlette",route:"/contrib/starlette"},{kind:"MdxPage",name:"webauthn",route:"/contrib/webauthn"},{kind:"Meta",data:{"arq-tasks":"Arq Tasks",auditing:"Auditing",email:"Email",redis:"Redis",starlette:"Starlette",webauthn:"Webauthn"}}]},{kind:"Folder",name:"fields",route:"/fields",children:[{kind:"Meta",data:{virtual_columns:"Virtual Columns and Fields",relations:"Relations and References to other Models",mutations:"Mutations",aggregations:"Aggregations","python-based-fields":"Computations in Python"}},{kind:"MdxPage",name:"aggregations",route:"/fields/aggregations"},{kind:"MdxPage",name:"mutations",route:"/fields/mutations"},{kind:"MdxPage",name:"python-based-fields",route:"/fields/python-based-fields"},{kind:"MdxPage",name:"relations",route:"/fields/relations"},{kind:"MdxPage",name:"virtual_columns",route:"/fields/virtual_columns"}]},{kind:"Folder",name:"getting_started",route:"/getting_started",children:[{kind:"Meta",data:{installation:"Installation","basic-usage":"Basic Usage","querying-data":"Querying Data",config:"Environment Configuration",optimizations:"Optimizations"}},{kind:"MdxPage",name:"basic-usage",route:"/getting_started/basic-usage"},{kind:"MdxPage",name:"config",route:"/getting_started/config"},{kind:"MdxPage",name:"installation",route:"/getting_started/installation"},{kind:"MdxPage",name:"optimizations",route:"/getting_started/optimizations"},{kind:"MdxPage",name:"querying-data",route:"/getting_started/querying-data"}]},{kind:"MdxPage",name:"index",route:"/"},{kind:"Folder",name:"tables",route:"/tables",children:[{kind:"Meta",data:{table_basics:"Table Basics",base_models:"Base Models",migrations:"Migrations",types:"Python and SQL Types",custom_types:"Custom Types","public-private-schemas":"Private and Public Schemas"}},{kind:"MdxPage",name:"base_models",route:"/tables/base_models"},{kind:"MdxPage",name:"custom_types",route:"/tables/custom_types"},{kind:"MdxPage",name:"migrations",route:"/tables/migrations"},{kind:"MdxPage",name:"public-private-schemas",route:"/tables/public-private-schemas"},{kind:"MdxPage",name:"table_basics",route:"/tables/table_basics"},{kind:"MdxPage",name:"types",route:"/tables/types"}]}],flexsearch:{codeblocks:!0},title:"Mutations"},pageNextRoute:"/fields/mutations",nextraLayout:t.ZP,themeConfig:r.Z};function c(s){let e=Object.assign({h1:"h1",p:"p",pre:"pre",code:"code",span:"span"},(0,l.ah)(),s.components);return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(e.h1,{children:"Mutations"}),"\n",(0,i.jsx)(e.p,{children:"Insert, Update, Delete are also optimized for GQL and can be used in Mutations."}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Schema"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelUpdater"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" RhubarbExtension"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"type"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"\\"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    get_conn"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" mutation"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" update"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" query"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" save"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"functions "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" concat"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" strawberry"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"types "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Info"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"type"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"Mutation"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@mutation"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"update_person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"info"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Info"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"person_id"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"UUID"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"new_name"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:") "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"->"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Person:"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"do"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelUpdater"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"Person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"]"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"):"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"            "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# With Update expressions, we can use computations and reference sql fields and joins."})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"            person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"title "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"concat"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"                new_name, "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"(Old Name: "'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", person.title, "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'")"'})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"            )"})}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"where"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"Person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"]"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"):"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"            "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"id "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"=="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" person_id"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Even though this mutation is not async, we are returning an UpdateSet which will"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# be executed by Rhubarb async middleware."})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"update"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"get_conn"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(info), Person, do, where, info"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"info, one"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"True"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@mutation"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"update_name"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"info"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Info"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"person_id"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"UUID"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"new_name"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    ) "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"->"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Person:"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        conn "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"get_conn"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(info)"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Or avoid the optimization extension and just use await statements."})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        obj "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"by_pk"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(conn, Person, person_id)."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"one"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        obj"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"title "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" new_name"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"save"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(conn, obj, info"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"info)"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"schema "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"Schema"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    query"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"Query,"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"    mutation"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"Mutation"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})})]})})]})}e.default=(0,o.j)(a)}},function(s){s.O(0,[774,282,888,179],function(){return s(s.s=5382)}),_N_E=s.O()}]);