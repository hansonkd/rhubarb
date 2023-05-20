(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[631],{2794:function(e,s,n){(window.__NEXT_P=window.__NEXT_P||[]).push(["/fields/relations",function(){return n(8773)}])},5484:function(e,s,n){"use strict";var i=n(2322);s.Z={logo:(0,i.jsx)("span",{children:"Rhubarb Documentation"}),project:{link:"https://github.com/hansonkd/rhubarb"},docsRepositoryBase:"https://github.com/hansonkd/rhubarb"}},8773:function(e,s,n){"use strict";n.r(s);var i=n(2322),t=n(8287),o=n(6582),r=n(5484);n(6908);var a=n(5392);n(6577);let l={MDXContent:function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},{wrapper:s}=Object.assign({},(0,a.ah)(),e.components);return s?(0,i.jsx)(s,{...e,children:(0,i.jsx)(c,{...e})}):c(e)},pageOpts:{filePath:"pages/fields/relations.mdx",route:"/fields/relations",headings:[{depth:1,value:"Relations",id:"relations"},{depth:2,value:"Specify a SQL Reference Constraint",id:"specify-a-sql-reference-constraint"},{depth:2,value:"Relation with One or None objects",id:"relation-with-one-or-none-objects"},{depth:2,value:"Relationships with Many Objects",id:"relationships-with-many-objects"}],timestamp:1684534015e3,pageMap:[{kind:"Meta",data:{index:"Rhubarb",getting_started:"Getting Started",tables:"Working with Tables",fields:"Fields and Relations",auth:"User Authentication",pkg:"Other Integrations",advanced:"Advanced Usage",github_link:{title:"Github",href:"https://github.com/hansonkd/rhubarb"}}},{kind:"Folder",name:"advanced",route:"/advanced",children:[{kind:"Meta",data:{"default-where-clause":"Automatic Filtering","sql-functions":"SQL Functions",multi:"Multiple Selections without GQL","field-permissions":"Column and Field Permissions"}},{kind:"MdxPage",name:"default-where-clause",route:"/advanced/default-where-clause"},{kind:"MdxPage",name:"field-permissions",route:"/advanced/field-permissions"},{kind:"MdxPage",name:"multi",route:"/advanced/multi"},{kind:"MdxPage",name:"sql-functions",route:"/advanced/sql-functions"}]},{kind:"Folder",name:"auth",route:"/auth",children:[{kind:"Meta",data:{using:"Adding User Auth",impersonate:"Impersonating Users"}},{kind:"MdxPage",name:"impersonate",route:"/auth/impersonate"},{kind:"MdxPage",name:"using",route:"/auth/using"}]},{kind:"Folder",name:"contrib",route:"/contrib",children:[{kind:"MdxPage",name:"arq-tasks",route:"/contrib/arq-tasks"},{kind:"MdxPage",name:"auditing",route:"/contrib/auditing"},{kind:"MdxPage",name:"email",route:"/contrib/email"},{kind:"MdxPage",name:"redis",route:"/contrib/redis"},{kind:"MdxPage",name:"starlette",route:"/contrib/starlette"},{kind:"MdxPage",name:"webauthn",route:"/contrib/webauthn"},{kind:"Meta",data:{"arq-tasks":"Arq Tasks",auditing:"Auditing",email:"Email",redis:"Redis",starlette:"Starlette",webauthn:"Webauthn"}}]},{kind:"Folder",name:"fields",route:"/fields",children:[{kind:"Meta",data:{virtual_columns:"Virtual Columns and Fields",relations:"Relations and References to other Models",mutations:"Mutations",aggregations:"Aggregations","python-based-fields":"Computations in Python"}},{kind:"MdxPage",name:"aggregations",route:"/fields/aggregations"},{kind:"MdxPage",name:"mutations",route:"/fields/mutations"},{kind:"MdxPage",name:"python-based-fields",route:"/fields/python-based-fields"},{kind:"MdxPage",name:"relations",route:"/fields/relations"},{kind:"MdxPage",name:"virtual_columns",route:"/fields/virtual_columns"}]},{kind:"Folder",name:"getting_started",route:"/getting_started",children:[{kind:"Meta",data:{installation:"Installation","basic-usage":"Basic Usage","querying-data":"Querying Data",config:"Environment Configuration",optimizations:"Optimizations"}},{kind:"MdxPage",name:"basic-usage",route:"/getting_started/basic-usage"},{kind:"MdxPage",name:"config",route:"/getting_started/config"},{kind:"MdxPage",name:"installation",route:"/getting_started/installation"},{kind:"MdxPage",name:"optimizations",route:"/getting_started/optimizations"},{kind:"MdxPage",name:"querying-data",route:"/getting_started/querying-data"}]},{kind:"MdxPage",name:"index",route:"/"},{kind:"Folder",name:"tables",route:"/tables",children:[{kind:"Meta",data:{table_basics:"Table Basics",base_models:"Base Models",migrations:"Migrations",types:"Python and SQL Types",custom_types:"Custom Types","public-private-schemas":"Private and Public Schemas"}},{kind:"MdxPage",name:"base_models",route:"/tables/base_models"},{kind:"MdxPage",name:"custom_types",route:"/tables/custom_types"},{kind:"MdxPage",name:"migrations",route:"/tables/migrations"},{kind:"MdxPage",name:"public-private-schemas",route:"/tables/public-private-schemas"},{kind:"MdxPage",name:"table_basics",route:"/tables/table_basics"},{kind:"MdxPage",name:"types",route:"/tables/types"}]}],flexsearch:{codeblocks:!0},title:"Relations"},pageNextRoute:"/fields/relations",nextraLayout:o.ZP,themeConfig:r.Z};function c(e){let s=Object.assign({h1:"h1",p:"p",h2:"h2",pre:"pre",code:"code",span:"span"},(0,a.ah)(),e.components);return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(s.h1,{children:"Relations"}),"\n",(0,i.jsx)(s.p,{children:"Rhubarb will follow child selections and inline as many queries for relation data as possible. This means that most relations that return 1 or 0 objects can be inlined in the same Query as their parent object."}),"\n",(0,i.jsx)(s.h2,{id:"specify-a-sql-reference-constraint",children:"Specify a SQL Reference Constraint"}),"\n",(0,i.jsx)(s.p,{children:"When defining your model, specify a reference to another model's table."}),"\n",(0,i.jsx)(s.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsx)(s.code,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"owner_id"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"UUID "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"references"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(MyModel)"})]})})}),"\n",(0,i.jsx)(s.p,{children:"You can also do it lazily if the Model is defined after it."}),"\n",(0,i.jsx)(s.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsx)(s.code,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"owner_id"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"UUID "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"references"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"lambda"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:": MyModel)"})]})})}),"\n",(0,i.jsx)(s.h2,{id:"relation-with-one-or-none-objects",children:"Relation with One or None objects"}),"\n",(0,i.jsx)(s.p,{children:"By default a relation field computes one or None related objects. you create a relation field by decorating a method that returns a boolean selector."}),"\n",(0,i.jsx)(s.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(s.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsx)(s.span,{className:"line",children:(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"@table"})}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"Pet"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    owner_id"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"UUID "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"references"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(Person)"})]}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"@relation"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"owner"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" ModelSelector"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"Pet"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"],"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-parameter)"},children:"owner"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" Person):"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" self"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"owner_id "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"=="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" owner"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"id"})]})]})}),"\n",(0,i.jsx)(s.h2,{id:"relationships-with-many-objects",children:"Relationships with Many Objects"}),"\n",(0,i.jsxs)(s.p,{children:["If you have a parent with many children, you can return a list of children by specifying that you want to return a list using ",(0,i.jsx)(s.code,{children:"graphql_type"})," like so ",(0,i.jsx)(s.code,{children:"@relation(graphql_type=list[Pet])"}),"."]}),"\n",(0,i.jsxs)(s.p,{children:["Because Rhubarb Aggressively inlines all possible fields into a SQL Query, if you return a ",(0,i.jsx)(s.code,{children:"list"})," from a Relation, there is an optimization fence in which Rhubarb will no longer try to inline the relation. Rhubarb will instead start a new tree and start inlining as many children as possible. This is to avoid exploding cartesian products."]}),"\n",(0,i.jsx)(s.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(s.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"  BaseModel"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" column"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" table"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" relation"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" references"})]}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsx)(s.span,{className:"line",children:(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"@table"})}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"Pet"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"BaseModel"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"):"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    name"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"column"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    owner_id"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" uuid"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"UUID "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"references"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"lambda"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:": Person)"})]}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-comment)"},children:"# Default relation returns a single object"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"@relation"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"owner"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-parameter)"},children:"owner"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"Person"'}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"):"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" self"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"owner_id "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"=="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" owner"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"id"})]}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsx)(s.span,{className:"line",children:(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"@table"})}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"Person"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"BaseModel"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"):"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    name"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"column"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsx)(s.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-comment)"},children:"# Specify relation list of objects. Optimization fence."})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"@relation"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(graphql_type"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"list[Pet])"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-function)"},children:"pets"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-parameter)"},children:"self"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-parameter)"},children:"pet"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" Pet):"})]}),"\n",(0,i.jsxs)(s.span,{className:"line",children:[(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" self"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"id "}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-keyword)"},children:"=="}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:" pet"}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(s.span,{style:{color:"var(--shiki-color-text)"},children:"owner_id"})]})]})})]})}s.default=(0,t.j)(l)}},function(e){e.O(0,[774,282,888,179],function(){return e(e.s=2794)}),_N_E=e.O()}]);