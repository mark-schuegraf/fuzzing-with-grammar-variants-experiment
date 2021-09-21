// translated from https://github.com/antlr/grammars-v4/blob/master/url/url.g4
// as of commit 320f7f284210754b37b72b6e2fe90bb999d74847

Grammar(
    'url := 'uri,

    'uri := 'scheme ~ "://" ~ 'login.? ~ 'host ~ (":" ~ 'port).? ~ ("/"/*@3*/ ~ 'path).? ~ 'query.? ~ 'frag.? ~ 'WS.?,

    'scheme := 'string/*@9*/ ,

    'host := "/"/*@2*/ .? ~ 'hostname,

    'hostname := "[" ~ 'v6host ~ "]" | 'string/*@3*/ ~ ("." ~ 'string).rep,

    'v6host := "::".? ~ ('DIGITS/*@1*/ | 'string/*@5*/) ~ ((":"/*@1*/ | "::"/*@1*/) ~ ('DIGITS/*@2*/ | 'string/*@6*/)).rep,

    'port := 'DIGITS/*@4*/ ,

    'path := 'string/*@1*/ ~ ("/" ~ 'string).rep ~ "/"/*@1*/ .?,

    'user := 'string/*@10*/ ,

    'login := 'user ~ (":"/*@2*/ ~ 'password).? ~ "@",

    'password := 'string/*@11*/ ,

    'frag := "#" ~ ('DIGITS | 'string),

    'query := "?" ~ 'search,

    'search := 'searchparameter ~ ("&" ~ 'searchparameter).rep,

    'searchparameter := 'string/*@7*/ ~ ("=" ~ ('DIGITS/*@3*/ | 'HEX | 'string/*@8*/)).?,

    'string := 'STRING,

    'DIGITS := "[0-9]+".regex,

    'HEX := "(%[a-fA-F0-9][a-fA-F0-9])+".regex,

    'STRING := ('HEX/*@1*/ | "[a-zA-Z~0-9]".regex) ~ ('HEX/*@2*/ | "[a-zA-Z0-9.+-]".regex).rep,

    'WS := "[\r\n]+".regex
)
