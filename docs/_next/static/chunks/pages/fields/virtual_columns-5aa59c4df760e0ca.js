(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[801],{9342:function(s,e,n){(window.__NEXT_P=window.__NEXT_P||[]).push(["/fields/virtual_columns",function(){return n(4715)}])},5484:function(s,e,n){"use strict";var i=n(2322);e.Z={logo:(0,i.jsx)("span",{children:"Rhubarb Documentation"}),project:{link:"https://github.com/hansonkd/rhubarb"},docsRepositoryBase:"https://github.com/hansonkd/rhubarb"}},4715:function(s,e,n){"use strict";n.r(e);var i=n(2322),t=n(8287),o=n(6582),r=n(5484);n(6908);var l=n(5392);n(6577);let a={MDXContent:function(){let s=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},{wrapper:e}=Object.assign({},(0,l.ah)(),s.components);return e?(0,i.jsx)(e,{...s,children:(0,i.jsx)(c,{...s})}):c(s)},pageOpts:{filePath:"pages/fields/virtual_columns.mdx",route:"/fields/virtual_columns",headings:[{depth:1,value:"Virtual Columns",id:"virtual-columns"}],timestamp:1684534015e3,pageMap:[{kind:"Meta",data:{index:"Rhubarb",getting_started:"Getting Started",tables:"Working with Tables",fields:"Fields and Relations",auth:"User Authentication",pkg:"Other Integrations",advanced:"Advanced Usage",github_link:{title:"Github",href:"https://github.com/hansonkd/rhubarb"}}},{kind:"Folder",name:"advanced",route:"/advanced",children:[{kind:"Meta",data:{"default-where-clause":"Automatic Filtering","sql-functions":"SQL Functions",multi:"Multiple Selections without GQL","field-permissions":"Column and Field Permissions"}},{kind:"MdxPage",name:"default-where-clause",route:"/advanced/default-where-clause"},{kind:"MdxPage",name:"field-permissions",route:"/advanced/field-permissions"},{kind:"MdxPage",name:"multi",route:"/advanced/multi"},{kind:"MdxPage",name:"sql-functions",route:"/advanced/sql-functions"}]},{kind:"Folder",name:"auth",route:"/auth",children:[{kind:"Meta",data:{using:"Adding User Auth",impersonate:"Impersonating Users"}},{kind:"MdxPage",name:"impersonate",route:"/auth/impersonate"},{kind:"MdxPage",name:"using",route:"/auth/using"}]},{kind:"Folder",name:"contrib",route:"/contrib",children:[{kind:"MdxPage",name:"arq-tasks",route:"/contrib/arq-tasks"},{kind:"MdxPage",name:"auditing",route:"/contrib/auditing"},{kind:"MdxPage",name:"email",route:"/contrib/email"},{kind:"MdxPage",name:"redis",route:"/contrib/redis"},{kind:"MdxPage",name:"starlette",route:"/contrib/starlette"},{kind:"MdxPage",name:"webauthn",route:"/contrib/webauthn"},{kind:"Meta",data:{"arq-tasks":"Arq Tasks",auditing:"Auditing",email:"Email",redis:"Redis",starlette:"Starlette",webauthn:"Webauthn"}}]},{kind:"Folder",name:"fields",route:"/fields",children:[{kind:"Meta",data:{virtual_columns:"Virtual Columns and Fields",relations:"Relations and References to other Models",mutations:"Mutations",aggregations:"Aggregations","python-based-fields":"Computations in Python"}},{kind:"MdxPage",name:"aggregations",route:"/fields/aggregations"},{kind:"MdxPage",name:"mutations",route:"/fields/mutations"},{kind:"MdxPage",name:"python-based-fields",route:"/fields/python-based-fields"},{kind:"MdxPage",name:"relations",route:"/fields/relations"},{kind:"MdxPage",name:"virtual_columns",route:"/fields/virtual_columns"}]},{kind:"Folder",name:"getting_started",route:"/getting_started",children:[{kind:"Meta",data:{installation:"Installation","basic-usage":"Basic Usage","querying-data":"Querying Data",config:"Environment Configuration",optimizations:"Optimizations"}},{kind:"MdxPage",name:"basic-usage",route:"/getting_started/basic-usage"},{kind:"MdxPage",name:"config",route:"/getting_started/config"},{kind:"MdxPage",name:"installation",route:"/getting_started/installation"},{kind:"MdxPage",name:"optimizations",route:"/getting_started/optimizations"},{kind:"MdxPage",name:"querying-data",route:"/getting_started/querying-data"}]},{kind:"MdxPage",name:"index",route:"/"},{kind:"Folder",name:"tables",route:"/tables",children:[{kind:"Meta",data:{table_basics:"Table Basics",base_models:"Base Models",migrations:"Migrations",types:"Python and SQL Types",custom_types:"Custom Types","public-private-schemas":"Private and Public Schemas"}},{kind:"MdxPage",name:"base_models",route:"/tables/base_models"},{kind:"MdxPage",name:"custom_types",route:"/tables/custom_types"},{kind:"MdxPage",name:"migrations",route:"/tables/migrations"},{kind:"MdxPage",name:"public-private-schemas",route:"/tables/public-private-schemas"},{kind:"MdxPage",name:"table_basics",route:"/tables/table_basics"},{kind:"MdxPage",name:"types",route:"/tables/types"}]}],flexsearch:{codeblocks:!0},title:"Virtual Columns"},pageNextRoute:"/fields/virtual_columns",nextraLayout:o.ZP,themeConfig:r.Z};function c(s){let e=Object.assign({h1:"h1",p:"p",code:"code",pre:"pre",span:"span"},(0,l.ah)(),s.components);return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(e.h1,{children:"Virtual Columns"}),"\n",(0,i.jsxs)(e.p,{children:["Rhubarb tables are different from standard Python objects. methods decorated with ",(0,i.jsx)(e.code,{children:"virtual_column"})," and ",(0,i.jsx)(e.code,{children:"field"})," are not executed in Python. These methods are pushed down and transformed into SQL to be executed on the Postgres Server."]}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"  BaseModel"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" column"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" table"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" virtual_column"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"functions "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" concat"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" case"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" val"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@table"})}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"Person"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"BaseModel"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"):"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    first_name"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"column"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    last_name"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"column"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    favorite_number"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"int"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"column"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    score"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"int"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"column"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@virtual_column"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"full_name"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector) "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"->"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"concat"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(self.first_name, self.last_name)"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@virtual_column"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"favorite_number_is_42"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector) "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"->"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"bool"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" self"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"favorite_number "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"=="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"42"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@virtual_column"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"case_computation"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector) "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"->"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"case"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"            (self.score "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"=="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"0"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"val"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"Bad"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")),"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"            (self.score "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"<"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"5"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"val"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"Poor"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")),"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"            (self.score "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"<"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"7"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"val"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"Good"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")),"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"            default"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"val"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"Excellent"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"        )"})})]})})]})}e.default=(0,t.j)(a)}},function(s){s.O(0,[774,282,888,179],function(){return s(s.s=9342)}),_N_E=s.O()}]);