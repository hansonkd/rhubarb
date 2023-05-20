(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[14],{5383:function(e,t,n){(window.__NEXT_P=window.__NEXT_P||[]).push(["/tables/types",function(){return n(7226)}])},5484:function(e,t,n){"use strict";var i=n(2322);t.Z={logo:(0,i.jsx)("span",{children:"Rhubarb Documentation"}),project:{link:"https://github.com/hansonkd/rhubarb"},docsRepositoryBase:"https://github.com/hansonkd/rhubarb"}},7226:function(e,t,n){"use strict";n.r(t);var i=n(2322),a=n(8287),s=n(6582),d=n(5484);n(6908);var r=n(5392);n(6577);let l={MDXContent:function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},{wrapper:t}=Object.assign({},(0,r.ah)(),e.components);return t?(0,i.jsx)(t,{...e,children:(0,i.jsx)(c,{...e})}):c(e)},pageOpts:{filePath:"pages/tables/types.mdx",route:"/tables/types",headings:[{depth:1,value:"Built-in Column / Sql Types",id:"built-in-column--sql-types"}],timestamp:1684534015e3,pageMap:[{kind:"Meta",data:{index:"Rhubarb",getting_started:"Getting Started",tables:"Working with Tables",fields:"Fields and Relations",auth:"User Authentication",pkg:"Other Integrations",advanced:"Advanced Usage",github_link:{title:"Github",href:"https://github.com/hansonkd/rhubarb"}}},{kind:"Folder",name:"advanced",route:"/advanced",children:[{kind:"Meta",data:{"default-where-clause":"Automatic Filtering","sql-functions":"SQL Functions",multi:"Multiple Selections without GQL","field-permissions":"Column and Field Permissions"}},{kind:"MdxPage",name:"default-where-clause",route:"/advanced/default-where-clause"},{kind:"MdxPage",name:"field-permissions",route:"/advanced/field-permissions"},{kind:"MdxPage",name:"multi",route:"/advanced/multi"},{kind:"MdxPage",name:"sql-functions",route:"/advanced/sql-functions"}]},{kind:"Folder",name:"auth",route:"/auth",children:[{kind:"Meta",data:{using:"Adding User Auth",impersonate:"Impersonating Users"}},{kind:"MdxPage",name:"impersonate",route:"/auth/impersonate"},{kind:"MdxPage",name:"using",route:"/auth/using"}]},{kind:"Folder",name:"contrib",route:"/contrib",children:[{kind:"MdxPage",name:"arq-tasks",route:"/contrib/arq-tasks"},{kind:"MdxPage",name:"auditing",route:"/contrib/auditing"},{kind:"MdxPage",name:"email",route:"/contrib/email"},{kind:"MdxPage",name:"redis",route:"/contrib/redis"},{kind:"MdxPage",name:"starlette",route:"/contrib/starlette"},{kind:"MdxPage",name:"webauthn",route:"/contrib/webauthn"},{kind:"Meta",data:{"arq-tasks":"Arq Tasks",auditing:"Auditing",email:"Email",redis:"Redis",starlette:"Starlette",webauthn:"Webauthn"}}]},{kind:"Folder",name:"fields",route:"/fields",children:[{kind:"Meta",data:{virtual_columns:"Virtual Columns and Fields",relations:"Relations and References to other Models",mutations:"Mutations",aggregations:"Aggregations","python-based-fields":"Computations in Python"}},{kind:"MdxPage",name:"aggregations",route:"/fields/aggregations"},{kind:"MdxPage",name:"mutations",route:"/fields/mutations"},{kind:"MdxPage",name:"python-based-fields",route:"/fields/python-based-fields"},{kind:"MdxPage",name:"relations",route:"/fields/relations"},{kind:"MdxPage",name:"virtual_columns",route:"/fields/virtual_columns"}]},{kind:"Folder",name:"getting_started",route:"/getting_started",children:[{kind:"Meta",data:{installation:"Installation","basic-usage":"Basic Usage","querying-data":"Querying Data",config:"Environment Configuration",optimizations:"Optimizations"}},{kind:"MdxPage",name:"basic-usage",route:"/getting_started/basic-usage"},{kind:"MdxPage",name:"config",route:"/getting_started/config"},{kind:"MdxPage",name:"installation",route:"/getting_started/installation"},{kind:"MdxPage",name:"optimizations",route:"/getting_started/optimizations"},{kind:"MdxPage",name:"querying-data",route:"/getting_started/querying-data"}]},{kind:"MdxPage",name:"index",route:"/"},{kind:"Folder",name:"tables",route:"/tables",children:[{kind:"Meta",data:{table_basics:"Table Basics",base_models:"Base Models",migrations:"Migrations",types:"Python and SQL Types",custom_types:"Custom Types","public-private-schemas":"Private and Public Schemas"}},{kind:"MdxPage",name:"base_models",route:"/tables/base_models"},{kind:"MdxPage",name:"custom_types",route:"/tables/custom_types"},{kind:"MdxPage",name:"migrations",route:"/tables/migrations"},{kind:"MdxPage",name:"public-private-schemas",route:"/tables/public-private-schemas"},{kind:"MdxPage",name:"table_basics",route:"/tables/table_basics"},{kind:"MdxPage",name:"types",route:"/tables/types"}]}],flexsearch:{codeblocks:!0},title:"Built-in Column / Sql Types"},pageNextRoute:"/tables/types",nextraLayout:s.ZP,themeConfig:d.Z};function c(e){let t=Object.assign({h1:"h1",p:"p",table:"table",thead:"thead",tr:"tr",th:"th",tbody:"tbody",td:"td"},(0,r.ah)(),e.components);return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(t.h1,{children:"Built-in Column / Sql Types"}),"\n",(0,i.jsx)(t.p,{children:"When creating tables, refer to this Guide about the mappings between Python Type and Postgres Type"}),"\n",(0,i.jsxs)(t.table,{children:[(0,i.jsx)(t.thead,{children:(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.th,{align:"left",children:"Python"}),(0,i.jsx)(t.th,{align:"center",children:"Postgres"}),(0,i.jsx)(t.th,{align:"center",children:"Notes"})]})}),(0,i.jsxs)(t.tbody,{children:[(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"bool"}),(0,i.jsx)(t.td,{align:"center",children:"BOOLEAN"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"int"}),(0,i.jsx)(t.td,{align:"center",children:"BIGINT"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"float"}),(0,i.jsx)(t.td,{align:"center",children:"FLOAT"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"decimal.Decimal"}),(0,i.jsx)(t.td,{align:"center",children:"DECIMAL"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"str"}),(0,i.jsx)(t.td,{align:"center",children:"TEXT"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"bytes"}),(0,i.jsx)(t.td,{align:"center",children:"BYTEA"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"datetime.datetime"}),(0,i.jsx)(t.td,{align:"center",children:"TIMESTAMPTZ"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"datetime.date"}),(0,i.jsx)(t.td,{align:"center",children:"DATE"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"uuid.UUID"}),(0,i.jsx)(t.td,{align:"center",children:"UUID"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"typing.Optional"}),(0,i.jsx)(t.td,{align:"center",children:"Null columns"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"rhubarb.PhoneNumber"}),(0,i.jsx)(t.td,{align:"center",children:"TEXT"}),(0,i.jsx)(t.td,{align:"center",children:"decodes as phonenumbers.PhoneNumber"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"rhubarb.Email"}),(0,i.jsx)(t.td,{align:"center",children:"TEXT"}),(0,i.jsx)(t.td,{align:"center",children:"Wraps str"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"dict"}),(0,i.jsx)(t.td,{align:"center",children:"JSONB"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"list"}),(0,i.jsx)(t.td,{align:"center",children:"JSONB"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"strawberry.scalars.JSON"}),(0,i.jsx)(t.td,{align:"center",children:"JSONB"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"strawberry.scalars.Base64"}),(0,i.jsx)(t.td,{align:"center",children:"BYTEA"}),(0,i.jsx)(t.td,{align:"center",children:"decodes as str"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"strawberry.scalars.Base32"}),(0,i.jsx)(t.td,{align:"center",children:"BYTEA"}),(0,i.jsx)(t.td,{align:"center",children:"decodes as str"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"strawberry.scalars.Base16"}),(0,i.jsx)(t.td,{align:"center",children:"BYTEA"}),(0,i.jsx)(t.td,{align:"center",children:"decodes as str"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"rhubarb.SmallInt"}),(0,i.jsx)(t.td,{align:"center",children:"SMALLINT"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"rhubarb.core.Binary"}),(0,i.jsx)(t.td,{align:"center",children:"BYTEA"}),(0,i.jsx)(t.td,{align:"center",children:"decodes as bytes"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"rhubarb.core.Serial"}),(0,i.jsx)(t.td,{align:"center",children:"SERIAL"}),(0,i.jsx)(t.td,{align:"center"})]}),(0,i.jsxs)(t.tr,{children:[(0,i.jsx)(t.td,{align:"left",children:"None"}),(0,i.jsx)(t.td,{align:"center",children:"NULL"}),(0,i.jsx)(t.td,{align:"center",children:"cannot use as column type, only value"})]})]})]})]})}t.default=(0,a.j)(l)}},function(e){e.O(0,[774,282,888,179],function(){return e(e.s=5383)}),_N_E=e.O()}]);