(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[628],{3149:function(s,e,n){(window.__NEXT_P=window.__NEXT_P||[]).push(["/contrib/redis",function(){return n(3544)}])},5484:function(s,e,n){"use strict";var i=n(2322);e.Z={logo:(0,i.jsx)("span",{children:"Rhubarb Documentation"}),project:{link:"https://github.com/hansonkd/rhubarb"},docsRepositoryBase:"https://github.com/hansonkd/rhubarb"}},3544:function(s,e,n){"use strict";n.r(e);var i=n(2322),o=n(8287),t=n(6582),r=n(5484);n(6908);var l=n(5392);n(6577);let a={MDXContent:function(){let s=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},{wrapper:e}=Object.assign({},(0,l.ah)(),s.components);return e?(0,i.jsx)(e,{...s,children:(0,i.jsx)(c,{...s})}):c(s)},pageOpts:{filePath:"pages/contrib/redis.mdx",route:"/contrib/redis",headings:[{depth:1,value:"Redis",id:"redis"},{depth:2,value:"General usage",id:"general-usage"},{depth:2,value:"Caching",id:"caching"},{depth:3,value:"Clear the cache",id:"clear-the-cache"},{depth:3,value:"A note about Local Caching",id:"a-note-about-local-caching"},{depth:2,value:"Rate limiting",id:"rate-limiting"},{depth:2,value:"Config",id:"config"}],timestamp:1684534015e3,pageMap:[{kind:"Meta",data:{index:"Rhubarb",getting_started:"Getting Started",tables:"Working with Tables",fields:"Fields and Relations",auth:"User Authentication",pkg:"Other Integrations",advanced:"Advanced Usage",github_link:{title:"Github",href:"https://github.com/hansonkd/rhubarb"}}},{kind:"Folder",name:"advanced",route:"/advanced",children:[{kind:"Meta",data:{"default-where-clause":"Automatic Filtering","sql-functions":"SQL Functions",multi:"Multiple Selections without GQL","field-permissions":"Column and Field Permissions"}},{kind:"MdxPage",name:"default-where-clause",route:"/advanced/default-where-clause"},{kind:"MdxPage",name:"field-permissions",route:"/advanced/field-permissions"},{kind:"MdxPage",name:"multi",route:"/advanced/multi"},{kind:"MdxPage",name:"sql-functions",route:"/advanced/sql-functions"}]},{kind:"Folder",name:"auth",route:"/auth",children:[{kind:"Meta",data:{using:"Adding User Auth",impersonate:"Impersonating Users"}},{kind:"MdxPage",name:"impersonate",route:"/auth/impersonate"},{kind:"MdxPage",name:"using",route:"/auth/using"}]},{kind:"Folder",name:"contrib",route:"/contrib",children:[{kind:"MdxPage",name:"arq-tasks",route:"/contrib/arq-tasks"},{kind:"MdxPage",name:"auditing",route:"/contrib/auditing"},{kind:"MdxPage",name:"email",route:"/contrib/email"},{kind:"MdxPage",name:"redis",route:"/contrib/redis"},{kind:"MdxPage",name:"starlette",route:"/contrib/starlette"},{kind:"MdxPage",name:"webauthn",route:"/contrib/webauthn"},{kind:"Meta",data:{"arq-tasks":"Arq Tasks",auditing:"Auditing",email:"Email",redis:"Redis",starlette:"Starlette",webauthn:"Webauthn"}}]},{kind:"Folder",name:"fields",route:"/fields",children:[{kind:"Meta",data:{virtual_columns:"Virtual Columns and Fields",relations:"Relations and References to other Models",mutations:"Mutations",aggregations:"Aggregations","python-based-fields":"Computations in Python"}},{kind:"MdxPage",name:"aggregations",route:"/fields/aggregations"},{kind:"MdxPage",name:"mutations",route:"/fields/mutations"},{kind:"MdxPage",name:"python-based-fields",route:"/fields/python-based-fields"},{kind:"MdxPage",name:"relations",route:"/fields/relations"},{kind:"MdxPage",name:"virtual_columns",route:"/fields/virtual_columns"}]},{kind:"Folder",name:"getting_started",route:"/getting_started",children:[{kind:"Meta",data:{installation:"Installation","basic-usage":"Basic Usage","querying-data":"Querying Data",config:"Environment Configuration",optimizations:"Optimizations"}},{kind:"MdxPage",name:"basic-usage",route:"/getting_started/basic-usage"},{kind:"MdxPage",name:"config",route:"/getting_started/config"},{kind:"MdxPage",name:"installation",route:"/getting_started/installation"},{kind:"MdxPage",name:"optimizations",route:"/getting_started/optimizations"},{kind:"MdxPage",name:"querying-data",route:"/getting_started/querying-data"}]},{kind:"MdxPage",name:"index",route:"/"},{kind:"Folder",name:"tables",route:"/tables",children:[{kind:"Meta",data:{table_basics:"Table Basics",base_models:"Base Models",migrations:"Migrations",types:"Python and SQL Types",custom_types:"Custom Types","public-private-schemas":"Private and Public Schemas"}},{kind:"MdxPage",name:"base_models",route:"/tables/base_models"},{kind:"MdxPage",name:"custom_types",route:"/tables/custom_types"},{kind:"MdxPage",name:"migrations",route:"/tables/migrations"},{kind:"MdxPage",name:"public-private-schemas",route:"/tables/public-private-schemas"},{kind:"MdxPage",name:"table_basics",route:"/tables/table_basics"},{kind:"MdxPage",name:"types",route:"/tables/types"}]}],flexsearch:{codeblocks:!0},title:"Redis"},pageNextRoute:"/contrib/redis",nextraLayout:t.ZP,themeConfig:r.Z};function c(s){let e=Object.assign({h1:"h1",p:"p",h2:"h2",code:"code",pre:"pre",span:"span",h3:"h3"},(0,l.ah)(),s.components);return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(e.h1,{children:"Redis"}),"\n",(0,i.jsx)(e.p,{children:"Rhubarb has built in integrations with Redis for caching, ratelimiting and pubsub."}),"\n",(0,i.jsx)(e.h2,{id:"general-usage",children:"General usage"}),"\n",(0,i.jsxs)(e.p,{children:["You can get a redis connection from the currently configured pool with ",(0,i.jsx)(e.code,{children:"from rhubarb.pkg.redis.connection import connection"})," and use it like normal."]}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"pkg"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"redis"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"connection "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" connection"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"use_redis"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"():"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"with"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"connection"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"as"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" r"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" r"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"set"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"some_key"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"some_value"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" r"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"get"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"some_key"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]})]})}),"\n",(0,i.jsx)(e.h2,{id:"caching",children:"Caching"}),"\n",(0,i.jsx)(e.p,{children:"Rhubarb has builtin support for caching function results in Redis."}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"pkg"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"redis"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"cache "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" local_cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" local_only_cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:","}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" clear_cache"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" aiohttp"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Cache a function in Redis for a minute"})}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(ttl_seconds"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"60"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"cached_fn"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"():"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        resp "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" aiohttp"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"get"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"http://example.com"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" resp"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"json"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Cache a function locally and in Redis. On Read, prioritize local memory."})}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@local_cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(ttl_seconds"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"60"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"cached_fn"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"():"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        resp "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" aiohttp"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"get"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"http://example.com"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" resp"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"json"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Cache a function locally only."})}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@local_only_cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(ttl_seconds"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"60"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"local_only_cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"():"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    resp "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" aiohttp"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"get"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"http://example.com"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" resp"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"json"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]})]})}),"\n",(0,i.jsx)(e.h3,{id:"clear-the-cache",children:"Clear the cache"}),"\n",(0,i.jsxs)(e.p,{children:["Clear a function's cache by passing the decorated function into ",(0,i.jsx)(e.code,{children:"clear_cache"})]}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsx)(e.code,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"clear_cache"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(cached_fn)"})]})})}),"\n",(0,i.jsx)(e.h3,{id:"a-note-about-local-caching",children:"A note about Local Caching"}),"\n",(0,i.jsxs)(e.p,{children:["Be careful, clearing cache with local if your app is distributed. Clearing a local cache will only clear the local cache on the current machine. Therefore ",(0,i.jsx)(e.code,{children:"local_cache"})," and ",(0,i.jsx)(e.code,{children:"local_only_cache"})," should only be used with data that doesn't get stale (i.e. immutable data)"]}),"\n",(0,i.jsx)(e.h2,{id:"rate-limiting",children:"Rate limiting"}),"\n",(0,i.jsx)(e.p,{children:"Rhubarb has built-in a rate limit context manager and decorator. It is synchronized by Redis so can be used in distributed apps to secure parts of the code from bad actors."}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" starlette"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"requests "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Request"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"from"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rhubarb"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"pkg"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"redis"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"rate_limit "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"import"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" rate_limit"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Rate limit by IP. Once a minute."})}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"once_a_minute"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-parameter)"},children:"request"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Request):"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"with"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"rate_limit"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(key"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"f"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"my_action-'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"{"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"request.client.host"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"}"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", max_times"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"1"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", ttl_seconds"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"60"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"):"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"        "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"some_other_function"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:" "}),"\n",(0,i.jsx)(e.span,{className:"line",children:(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-comment)"},children:"# Rate limit as a decorator (this ratelimit would use the same key for all users)."})}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@rate_limit"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(key"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"f"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"my_action"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", max_times"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"1"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", ttl_seconds"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"60"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"async"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"def"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"once_a_minute"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"():"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"return"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"await"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"some_other_function"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"()"})]})]})}),"\n",(0,i.jsx)(e.h2,{id:"config",children:"Config"}),"\n",(0,i.jsx)(e.pre,{"data-language":"python","data-theme":"default",children:(0,i.jsxs)(e.code,{"data-language":"python","data-theme":"default",children:[(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"@dataclasses"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"."}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"dataclass"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"(frozen"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"True"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"class"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"RedisConfig"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:":"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    host"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"str_env"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"REDIS_HOST"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"127.0.0.1"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    port"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"int"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"int_env"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"REDIS_PORT"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"6379"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    username"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Optional"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"]"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"str_env"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"REDIS_USERNAME"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"None"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    password"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Optional"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"str"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"]"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"str_env"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"REDIS_PASSWORD"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"None"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    db"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"int"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"int_env"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"REDIS_DB"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:", "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"0"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]}),"\n",(0,i.jsxs)(e.span,{className:"line",children:[(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:"    max_connections"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:":"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" Optional"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"["}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-constant)"},children:"int"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"]"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-keyword)"},children:"="}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-color-text)"},children:" "}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-function)"},children:"int_env"}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:"("}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-string-expression)"},children:'"REDIS_MAX_CONNECTIONS"'}),(0,i.jsx)(e.span,{style:{color:"var(--shiki-token-punctuation)"},children:")"})]})]})})]})}e.default=(0,o.j)(a)}},function(s){s.O(0,[774,282,888,179],function(){return s(s.s=3149)}),_N_E=s.O()}]);