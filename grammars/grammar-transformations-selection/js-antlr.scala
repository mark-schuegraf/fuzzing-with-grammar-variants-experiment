import de.cispa.se.tribble.dsl._

Grammar(

  'program
    := 'sourceElements,

'sourceElement
  := 'Export.? ~ 'statement,

'statement
  := 'block
| 'variableStatement
  | 'emptyStatement
  | 'expressionStatement
  | 'ifStatement
  | 'iterationStatement
  | 'continueStatement
  | 'breakStatement
  | 'returnStatement
  | 'withStatement
  | 'labelledStatement
  | 'switchStatement
  | 'throwStatement
  | 'tryStatement
  | 'debuggerStatement
  | 'functionDeclaration
  | 'classDeclaration,

'block
  := "{" ~ 'statementList.? ~ "}",

'statementList
  := 'statement.rep(1),

'variableStatement
  := 'varModifier ~ 'variableDeclarationList ~ 'eos,

'variableDeclarationList
  := 'variableDeclaration ~ ("," ~ 'variableDeclaration).rep,

'variableDeclaration
  := ('Identifier | 'arrayLiteral | 'objectLiteral) ~ ("=" ~ 'singleExpression).? // ECMAScript 6: Array & Object Matching
,

'emptyStatement
  := 'SemiColon,

'expressionStatement
  := 'expressionSequence ~ 'eos,

'ifStatement
  := 'If ~ "(" ~ 'expressionSequence ~ ")" ~ 'statement ~ ('Else ~ 'statement).?,


'iterationStatement
  := 'Do ~ 'statement ~ 'While ~ "(" ~ 'expressionSequence ~ ")" ~ 'eos
| 'While ~ "(" ~ 'expressionSequence ~ ")" ~ 'statement
| 'For ~ "(" ~ 'expressionSequence.? ~ ";" ~ 'expressionSequence.? ~ ";" ~ 'expressionSequence.? ~ ")" ~ 'statement
| 'For ~ "(" ~ 'varModifier ~ 'variableDeclarationList ~ ";" ~ 'expressionSequence.? ~ ";" ~ 'expressionSequence.? ~ ")" ~ 'statement
| 'For ~ "(" ~ 'singleExpression ~ ('In | 'Identifier) ~ 'expressionSequence ~ ")" ~ 'statement
| 'For ~ "(" ~ 'varModifier ~ 'variableDeclaration ~ ('In | 'Identifier) ~ 'expressionSequence ~ ")" ~ 'statement,

'varModifier // let, const - ECMAScript 6
  := 'Var
  | 'Let
  | 'Const,

'continueStatement
  := 'Continue ~ 'eos,

'breakStatement
  := 'Break ~ 'eos,

'returnStatement
  := 'Return ~ 'eos,

'withStatement
  := 'With ~ "(" ~ 'expressionSequence ~  ")" ~ 'statement,

'switchStatement
  := 'Switch ~ "(" ~ 'expressionSequence ~ ")" ~ 'caseBlock,

'caseBlock
  := "{" ~ 'caseClauses.? ~ ('defaultClause ~ 'caseClauses.?).? ~ "}",

'caseClauses
  := 'caseClause.rep(1),

'caseClause
  := 'Case ~ 'expressionSequence ~ ":" ~ 'statementList.?,

'defaultClause
  := 'Default ~ ":" ~ 'statementList.?,

'labelledStatement
  := 'Identifier ~ ":" ~ 'statement,

'throwStatement
  := 'Throw ~  'expressionSequence ~ 'eos,

'tryStatement
  := 'Try ~ 'block ~ ('catchProduction ~ 'finallyProduction.? | 'finallyProduction),

'catchProduction
  := 'Catch ~ "(" ~ 'Identifier ~ ")" ~ 'block,

'finallyProduction
  := 'Finally ~ 'block,

'debuggerStatement
  := 'Debugger ~ 'eos,

'functionDeclaration
  := 'Function ~ 'Identifier ~  "(" ~ 'formalParameterList.? ~ ")" ~ "{" ~ 'functionBody ~ "}",

'classDeclaration
  := 'Class ~ 'Identifier ~ 'classTail,

'classTail
  := ('Extends ~ 'singleExpression).? ~ "{" ~ 'classElement.rep ~ "}",

'classElement
  := ('Static | 'Identifier).? ~ 'methodDefinition
| 'emptyStatement,

'methodDefinition
  := 'propertyName ~ "(" ~ 'formalParameterList.? ~ ")" ~ "{" ~ 'functionBody ~ "}"
| 'getter ~ "(){" ~ 'functionBody ~ "}"
  | 'setter ~ "(" ~ 'formalParameterList.? ~ ")" ~ "{" ~ 'functionBody ~ "}"
| 'generatorMethod,

'generatorMethod
  := "*".? ~ 'Identifier ~ "(" ~ 'formalParameterList.? ~ ")" ~ "{" ~ 'functionBody ~ "}",

'formalParameterList
  := 'formalParameterArg ~ ("," ~ 'formalParameterArg).rep ~ ("," ~ 'lastFormalParameterArg).?
  | 'lastFormalParameterArg
  | 'arrayLiteral // ECMAScript 6: Parameter Context Matching
  | 'objectLiteral // ECMAScript 6: Parameter Context Matching
,

'formalParameterArg
  := 'Identifier ~ ("=" ~ 'singleExpression).? // ECMAScript 6: Initialization
,

'lastFormalParameterArg // ECMAScript 6: Rest Parameter
  := 'Ellipsis ~ 'Identifier,

'functionBody
  := 'sourceElements.?,

'sourceElements
  := 'sourceElement.rep(1),

'arrayLiteral
  := "[" ~ ",".rep ~  'elementList.?  ~ ",".rep ~ "]",

'elementList
  := 'singleExpression ~ (",".rep(1) ~ 'singleExpression).rep ~ (",".rep(1) ~ 'lastElement).?
  | 'lastElement,

'lastElement // ECMAScript 6: Spread Operator
  := 'Ellipsis ~ 'Identifier,

'objectLiteral
  := "{" ~ ('propertyAssignment ~ ("," ~ 'propertyAssignment).rep).? ~ ",".? ~ "}",

'propertyAssignment
  := 'propertyName ~ (":" | "=") ~ 'singleExpression
| "[" ~ 'singleExpression ~ "]" ~ ":" ~ 'singleExpression
| 'getter ~ "(){" ~ 'functionBody ~ "}"
| 'setter ~ "(" ~ 'Identifier ~ "){" ~ 'functionBody ~ "}"
| 'generatorMethod
| 'Identifier,

'propertyName
  := 'identifierName
| 'StringLiteral
  | 'numericLiteral,

'arguments
  := "(" ~ (
  'singleExpression ~ ("," ~ 'singleExpression).rep ~ ("," ~ 'lastArgument).? |
    'lastArgument
  ).? ~ ")",

'lastArgument // ECMAScript 6: Spread Operator
  := 'Ellipsis ~ 'Identifier,

'expressionSequence
  := 'singleExpression ~ ("," ~ 'singleExpression).rep,

'singleExpression
  := 'Function ~ 'Identifier.? ~ "(" ~ 'formalParameterList.? ~ "){" ~ 'functionBody ~ "}"
| 'Class ~ 'Identifier.? ~ 'classTail
| 'singleExpression ~ "[" ~ 'expressionSequence ~ "]"
| 'singleExpression ~ "." ~ 'identifierName
| 'singleExpression ~ 'arguments
| 'New ~ 'singleExpression ~ 'arguments.?
| 'singleExpression ~ "++"
| 'singleExpression ~ "--"
| 'Delete ~ 'singleExpression
| 'Void ~ 'singleExpression
| 'Typeof ~ 'singleExpression
| "++" ~'singleExpression
| "--" ~'singleExpression
| "+" ~ 'singleExpression
| "-" ~  'singleExpression
| "~" ~  'singleExpression
| "!" ~  'singleExpression
| 'singleExpression ~  ("*" | "/" | "%") ~ 'singleExpression
| 'singleExpression ~  ("+" | "-") ~ 'singleExpression
| 'singleExpression ~  ("<<" | ">>" | ">>>") ~ 'singleExpression
| 'singleExpression ~  ("<" | ">" | "<=" | ">=") ~'singleExpression
| 'singleExpression ~  'Instanceof ~ 'singleExpression
| 'singleExpression ~  'In ~ 'singleExpression
| 'singleExpression ~  ("==" | "!=" | "===" | "!==") ~'singleExpression
| 'singleExpression ~  "&"  ~ 'singleExpression
| 'singleExpression ~  "^"  ~ 'singleExpression
| 'singleExpression ~  "|"  ~ 'singleExpression
| 'singleExpression ~  "&&"  ~ 'singleExpression
| 'singleExpression ~  "||"  ~ 'singleExpression
| 'singleExpression ~  "?"  ~ 'singleExpression ~ ":" ~ 'singleExpression
| 'singleExpression ~  "="  ~ 'singleExpression
| 'singleExpression ~  'assignmentOperator ~ 'singleExpression
| 'singleExpression ~  'TemplateStringLiteral // ECMAScript 6
| 'This
| 'Identifier
| 'Super
| 'literal
| 'arrayLiteral
| 'objectLiteral
| "(" ~ 'expressionSequence ~ ")"
| 'arrowFunctionParameters ~ "=>" ~ 'arrowFunctionBody
,

'arrowFunctionParameters
  := 'Identifier
| "(" ~ 'formalParameterList.? ~ ")",

'arrowFunctionBody
  := 'singleExpression
| "{" ~ 'functionBody ~ "}",

'assignmentOperator
:= "*="
|  "/="
|  "%="
|  "+="
|  "-="
|  "<<="
|  ">>="
|  ">>>="
|  "&="
|  "^="
|  "|="
,

'literal
  := 'NullLiteral
| 'BooleanLiteral
  | 'StringLiteral
  | 'TemplateStringLiteral
  | 'RegularExpressionLiteral
  | 'numericLiteral,

'numericLiteral
  := 'DecimalLiteral
| 'HexIntegerLiteral
  | 'OctalIntegerLiteral
  | 'OctalIntegerLiteral2
  | 'BinaryIntegerLiteral,

'identifierName
  := 'Identifier
| 'reservedWord,

'reservedWord
  := 'keyword
| 'NullLiteral
  | 'BooleanLiteral,

'keyword
  := 'Break
| 'Do
  | 'Instanceof
  | 'Typeof
  | 'Case
  | 'Else
  | 'New
  | 'Var
  | 'Catch
  | 'Finally
  | 'Return
  | 'Void
  | 'Continue
  | 'For
  | 'Switch
  | 'While
  | 'Debugger
  | 'Function
  | 'This
  | 'With
  | 'Default
  | 'If
  | 'Throw
  | 'Delete
  | 'In
  | 'Try

| 'Class
  | 'Enum
  | 'Extends
  | 'Super
  | 'Const
  | 'Export
  | 'Import
  | 'Implements
  | 'Let
  | 'Private
  | 'Public
  | 'Interface
  | 'Package
  | 'Protected
  | 'Static
  | 'Yield,

'getter
  := 'Identifier ~ 'propertyName,

'setter
  := 'Identifier ~ 'propertyName,

'eos
  := 'SemiColon,


'RegularExpressionLiteral := "/" ~ 'RegularExpressionFirstChar ~ 'RegularExpressionChar.rep ~ "/" ~ 'IdentifierPart.rep,


'SemiColon := ";",
'Ellipsis := "...",

/// Null Literals

'NullLiteral := "null",

/// Boolean Literals

'BooleanLiteral := "true" | "false",

/// Numeric Literals

'DecimalLiteral := 'DecimalIntegerLiteral ~ "." ~ "[0-9]*".regex ~ 'ExponentPart.?
  | "." ~ "[0-9]+".regex ~ 'ExponentPart.?
  | 'DecimalIntegerLiteral ~ 'ExponentPart.?,

/// Numeric Literals

'HexIntegerLiteral := "0[xX]".regex ~ 'HexDigit.rep(1),
'OctalIntegerLiteral := "0[0-7]+".regex ,
'OctalIntegerLiteral2 := "0[oO][0-7]+".regex,
'BinaryIntegerLiteral := "0[bB][01]+".regex,

/// Keywords

'Break := " break ",
'Do := " do ",
'Instanceof := " instanceof ",
'Typeof := " typeof ",
'Case := " case ",
'Else := " else ",
'New := " new ",
'Var := " var ",
'Catch := " catch ",
'Finally := " finally ",
'Return := " return ",
'Void := " void ",
'Continue := " continue ",
'For := " for ",
'Switch := " switch ",
'While := " while ",
'Debugger := " debugger ",
'Function := " function ",
'This := " this ",
'With := " with ",
'Default := " default ",
'If := " if ",
'Throw := " throw ",
'Delete := " delete ",
'In := " in ",
'Try := " try ",

/// Future Reserved Words

'Class := " class ",
'Enum := " enum ",
'Extends := " extends ",
'Super := " super ",
'Const := " const ",
'Export := " export ",
'Import := " import ",

/// The following tokens are also considered to be FutureReservedWords 
/// when parsing strict mode

'Implements := " implements ",
'Let := " let ",
'Private := " private ",
'Public := " public ",
'Interface := " interface ",
'Package := " package ",
'Protected := " protected ",
'Static := " static ",
'Yield := " yield ",

/// Identifier Names and Identifiers

'Identifier := 'IdentifierStart ~  'IdentifierPart.rep,

/// String Literals
'StringLiteral := ("\"" ~ 'DoubleStringCharacter.rep ~ "\""
  | "'" ~ 'SingleStringCharacter.rep ~ "'"),

'TemplateStringLiteral := "`" ~ ( "\\`" | "~`".regex).rep ~ "`",

/*
'WhiteSpaces :=[\ t \ u000B \ u000C \ u0020 \ u00A0] + -> channel (HIDDEN),
'LineTerminator :=[\ r \ n \ u2028 \ u2029] -> channel (HIDDEN),
/// Comments
'HtmlComment := '<!-- '.*? '--> ' -> channel (HIDDEN),
'CDataComment := '<![CDATA[ '.*? ']] > ' -> channel (HIDDEN),
'UnexpectedCharacter :=.-> channel (ERROR),
*/

// Fragment rules

'DoubleStringCharacter
  := "[^\"\\\\\r\n]".regex
  | "\\"~ 'EscapeSequence
  | 'LineContinuation,

'SingleStringCharacter
  := "[^'\\\\\r\n]".regex
| "\\"~ 'EscapeSequence
  | 'LineContinuation,

'EscapeSequence
  := 'CharacterEscapeSequence
| "0" // no digit ahead! TODO
| 'HexEscapeSequence
  | 'UnicodeEscapeSequence
  | 'ExtendedUnicodeEscapeSequence,

'CharacterEscapeSequence
  := 'SingleEscapeCharacter
| 'NonEscapeCharacter,

'HexEscapeSequence
  := "x"~ 'HexDigit ~ 'HexDigit,

'UnicodeEscapeSequence
  := "u" ~'HexDigit ~'HexDigit ~'HexDigit ~'HexDigit,

'ExtendedUnicodeEscapeSequence
  := "u" ~ "{" ~ 'HexDigit.rep(1) ~ "}",

'SingleEscapeCharacter
  := "['\"\\\\bfnrtv]".regex,

'NonEscapeCharacter
  := "[^'\"\\\\bfnrtv0-9xu\r\n]".regex,

'LineContinuation
  := "\\" ~ "[\r\n\u2028\u2029]".regex,

'HexDigit
  := "[0-9a-fA-F]".regex,

'DecimalIntegerLiteral
  := "0"
| "[1-9][0-9]*".regex,

'ExponentPart
  := "[eE][+-]?[0-9]+".regex,

'IdentifierPart
  := 'IdentifierStart
  | 'UnicodeCombiningMark
  | 'UnicodeDigit
  | 'UnicodeConnectorPunctuation
  | "\u200C"
  | "\u200D",

'IdentifierStart
  := 'UnicodeLetter
| "[$_]".regex
| "\\" ~ 'UnicodeEscapeSequence,

'UnicodeLetter
  := "[\u0041-\u005A]".regex
|"[\u0061-\u007A]".regex
|"\u00AA"
|"\u00B5"
|"\u00BA"
|"[\u00C0-\u00D6]".regex
|"[\u00D8-\u00F6]".regex
|"[\u00F8-\u021F]".regex
|"[\u0222-\u0233]".regex
|"[\u0250-\u02AD]".regex
|"[\u02B0-\u02B8]".regex
|"[\u02BB-\u02C1]".regex
|"[\u02D0-\u02D1]".regex
|"[\u02E0-\u02E4]".regex
|"\u02EE"
|"\u037A"
|"\u0386"
|"[\u0388-\u038A]".regex
|"\u038C"
|"[\u038E-\u03A1]".regex
|"[\u03A3-\u03CE]".regex
|"[\u03D0-\u03D7]".regex
|"[\u03DA-\u03F3]".regex
|"[\u0400-\u0481]".regex
|"[\u048C-\u04C4]".regex
|"[\u04C7-\u04C8]".regex
|"[\u04CB-\u04CC]".regex
|"[\u04D0-\u04F5]".regex
|"[\u04F8-\u04F9]".regex
|"[\u0531-\u0556]".regex
|"\u0559"
|"[\u0561-\u0587]".regex
|"[\u05D0-\u05EA]".regex
|"[\u05F0-\u05F2]".regex
|"[\u0621-\u063A]".regex
|"[\u0640-\u064A]".regex
|"[\u0671-\u06D3]".regex
|"\u06D5"
|"[\u06E5-\u06E6]".regex
|"[\u06FA-\u06FC]".regex
|"\u0710"
|"[\u0712-\u072C]".regex
|"[\u0780-\u07A5]".regex
|"[\u0905-\u0939]".regex
|"\u093D"
|"\u0950"
|"[\u0958-\u0961]".regex
|"[\u0985-\u098C]".regex
|"[\u098F-\u0990]".regex
|"[\u0993-\u09A8]".regex
|"[\u09AA-\u09B0]".regex
|"\u09B2"
|"[\u09B6-\u09B9]".regex
|"[\u09DC-\u09DD]".regex
|"[\u09DF-\u09E1]".regex
|"[\u09F0-\u09F1]".regex
|"[\u0A05-\u0A0A]".regex
|"[\u0A0F-\u0A10]".regex
|"[\u0A13-\u0A28]".regex
|"[\u0A2A-\u0A30]".regex
|"[\u0A32-\u0A33]".regex
|"[\u0A35-\u0A36]".regex
|"[\u0A38-\u0A39]".regex
|"[\u0A59-\u0A5C]".regex
|"\u0A5E"
|"[\u0A72-\u0A74]".regex
|"[\u0A85-\u0A8B]".regex
|"\u0A8D"
|"[\u0A8F-\u0A91]".regex
|"[\u0A93-\u0AA8]".regex
|"[\u0AAA-\u0AB0]".regex
|"[\u0AB2-\u0AB3]".regex
|"[\u0AB5-\u0AB9]".regex
|"\u0ABD"
|"\u0AD0"
|"\u0AE0"
|"[\u0B05-\u0B0C]".regex
|"[\u0B0F-\u0B10]".regex
|"[\u0B13-\u0B28]".regex
|"[\u0B2A-\u0B30]".regex
|"[\u0B32-\u0B33]".regex
|"[\u0B36-\u0B39]".regex
|"\u0B3D"
|"[\u0B5C-\u0B5D]".regex
|"[\u0B5F-\u0B61]".regex
|"[\u0B85-\u0B8A]".regex
|"[\u0B8E-\u0B90]".regex
|"[\u0B92-\u0B95]".regex
|"[\u0B99-\u0B9A]".regex
|"\u0B9C"
|"[\u0B9E-\u0B9F]".regex
|"[\u0BA3-\u0BA4]".regex
|"[\u0BA8-\u0BAA]".regex
|"[\u0BAE-\u0BB5]".regex
|"[\u0BB7-\u0BB9]".regex
|"[\u0C05-\u0C0C]".regex
|"[\u0C0E-\u0C10]".regex
|"[\u0C12-\u0C28]".regex
|"[\u0C2A-\u0C33]".regex
|"[\u0C35-\u0C39]".regex
|"[\u0C60-\u0C61]".regex
|"[\u0C85-\u0C8C]".regex
|"[\u0C8E-\u0C90]".regex
|"[\u0C92-\u0CA8]".regex
|"[\u0CAA-\u0CB3]".regex
|"[\u0CB5-\u0CB9]".regex
|"\u0CDE"
|"[\u0CE0-\u0CE1]".regex
|"[\u0D05-\u0D0C]".regex
|"[\u0D0E-\u0D10]".regex
|"[\u0D12-\u0D28]".regex
|"[\u0D2A-\u0D39]".regex
|"[\u0D60-\u0D61]".regex
|"[\u0D85-\u0D96]".regex
|"[\u0D9A-\u0DB1]".regex
|"[\u0DB3-\u0DBB]".regex
|"\u0DBD"
|"[\u0DC0-\u0DC6]".regex
|"[\u0E01-\u0E30]".regex
|"[\u0E32-\u0E33]".regex
|"[\u0E40-\u0E46]".regex
|"[\u0E81-\u0E82]".regex
|"\u0E84"
|"[\u0E87-\u0E88]".regex
|"\u0E8A"
|"\u0E8D"
|"[\u0E94-\u0E97]".regex
|"[\u0E99-\u0E9F]".regex
|"[\u0EA1-\u0EA3]".regex
|"\u0EA5"
|"\u0EA7"
|"[\u0EAA-\u0EAB]".regex
|"[\u0EAD-\u0EB0]".regex
|"[\u0EB2-\u0EB3]".regex
|"[\u0EBD-\u0EC4]".regex
|"\u0EC6"
|"[\u0EDC-\u0EDD]".regex
|"\u0F00"
|"[\u0F40-\u0F6A]".regex
|"[\u0F88-\u0F8B]".regex
|"[\u1000-\u1021]".regex
|"[\u1023-\u1027]".regex
|"[\u1029-\u102A]".regex
|"[\u1050-\u1055]".regex
|"[\u10A0-\u10C5]".regex
|"[\u10D0-\u10F6]".regex
|"[\u1100-\u1159]".regex
|"[\u115F-\u11A2]".regex
|"[\u11A8-\u11F9]".regex
|"[\u1200-\u1206]".regex
|"[\u1208-\u1246]".regex
|"\u1248"
|"[\u124A-\u124D]".regex
|"[\u1250-\u1256]".regex
|"\u1258"
|"[\u125A-\u125D]".regex
|"[\u1260-\u1286]".regex
|"\u1288"
|"[\u128A-\u128D]".regex
|"[\u1290-\u12AE]".regex
|"\u12B0"
|"[\u12B2-\u12B5]".regex
|"[\u12B8-\u12BE]".regex
|"\u12C0"
|"[\u12C2-\u12C5]".regex
|"[\u12C8-\u12CE]".regex
|"[\u12D0-\u12D6]".regex
|"[\u12D8-\u12EE]".regex
|"[\u12F0-\u130E]".regex
|"\u1310"
|"[\u1312-\u1315]".regex
|"[\u1318-\u131E]".regex
|"[\u1320-\u1346]".regex
|"[\u1348-\u135A]".regex
|"[\u13A0-\u13B0]".regex
|"[\u13B1-\u13F4]".regex
|"[\u1401-\u1676]".regex
|"[\u1681-\u169A]".regex
|"[\u16A0-\u16EA]".regex
|"[\u1780-\u17B3]".regex
|"[\u1820-\u1877]".regex
|"[\u1880-\u18A8]".regex
|"[\u1E00-\u1E9B]".regex
|"[\u1EA0-\u1EE0]".regex
|"[\u1EE1-\u1EF9]".regex
|"[\u1F00-\u1F15]".regex
|"[\u1F18-\u1F1D]".regex
|"[\u1F20-\u1F39]".regex
|"[\u1F3A-\u1F45]".regex
|"[\u1F48-\u1F4D]".regex
|"[\u1F50-\u1F57]".regex
|"\u1F59"
|"\u1F5B"
|"\u1F5D"
|"[\u1F5F-\u1F7D]".regex
|"[\u1F80-\u1FB4]".regex
|"[\u1FB6-\u1FBC]".regex
|"\u1FBE"
|"[\u1FC2-\u1FC4]".regex
|"[\u1FC6-\u1FCC]".regex
|"[\u1FD0-\u1FD3]".regex
|"[\u1FD6-\u1FDB]".regex
|"[\u1FE0-\u1FEC]".regex
|"[\u1FF2-\u1FF4]".regex
|"[\u1FF6-\u1FFC]".regex
|"\u207F"
|"\u2102"
|"\u2107"
|"[\u210A-\u2113]".regex
|"\u2115"
|"[\u2119-\u211D]".regex
|"\u2124"
|"\u2126"
|"\u2128"
|"[\u212A-\u212D]".regex
|"[\u212F-\u2131]".regex
|"[\u2133-\u2139]".regex
|"[\u2160-\u2183]".regex
|"[\u3005-\u3007]".regex
|"[\u3021-\u3029]".regex
|"[\u3031-\u3035]".regex
|"[\u3038-\u303A]".regex
|"[\u3041-\u3094]".regex
|"[\u309D-\u309E]".regex
|"[\u30A1-\u30FA]".regex
|"[\u30FC-\u30FE]".regex
|"[\u3105-\u312C]".regex
|"[\u3131-\u318E]".regex
|"[\u31A0-\u31B7]".regex
|"\u3400"
|"\u4DB5"
|"\u4E00"
|"\u9FA5"
|"[\uA000-\uA48C]".regex
|"\uAC00"
|"\uD7A3"
|"[\uF900-\uFA2D]".regex
|"[\uFB00-\uFB06]".regex
|"[\uFB13-\uFB17]".regex
|"\uFB1D"
|"[\uFB1F-\uFB28]".regex
|"[\uFB2A-\uFB36]".regex
|"[\uFB38-\uFB3C]".regex
|"\uFB3E"
|"[\uFB40-\uFB41]".regex
|"[\uFB43-\uFB44]".regex
|"[\uFB46-\uFBB1]".regex
|"[\uFBD3-\uFD3D]".regex
|"[\uFD50-\uFD8F]".regex
|"[\uFD92-\uFDC7]".regex
|"[\uFDF0-\uFDFB]".regex
|"[\uFE70-\uFE72]".regex
|"\uFE74"
|"[\uFE76-\uFEFC]".regex
|"[\uFF21-\uFF3A]".regex
|"[\uFF41-\uFF5A]".regex
|"[\uFF66-\uFFBE]".regex
|"[\uFFC2-\uFFC7]".regex
|"[\uFFCA-\uFFCF]".regex
|"[\uFFD2-\uFFD7]".regex
|"[\uFFDA-\uFFDC]".regex,

'UnicodeCombiningMark
  :=
 "[\u0300-\u034E]".regex
|"[\u0360-\u0362]".regex
|"[\u0483-\u0486]".regex
|"[\u0591-\u05A1]".regex
|"[\u05A3-\u05B9]".regex
|"[\u05BB-\u05BD]".regex
|"\u05BF"
|"[\u05C1-\u05C2]".regex
|"\u05C4"
|"[\u064B-\u0655]".regex
|"\u0670"
|"[\u06D6-\u06DC]".regex
|"[\u06DF-\u06E4]".regex
|"[\u06E7-\u06E8]".regex
|"[\u06EA-\u06ED]".regex
|"\u0711"
|"[\u0730-\u074A]".regex
|"[\u07A6-\u07B0]".regex
|"[\u0901-\u0903]".regex
|"\u093C"
|"[\u093E-\u094D]".regex
|"[\u0951-\u0954]".regex
|"[\u0962-\u0963]".regex
|"[\u0981-\u0983]".regex
|"[\u09BC-\u09C4]".regex
|"[\u09C7-\u09C8]".regex
|"[\u09CB-\u09CD]".regex
|"\u09D7"
|"[\u09E2-\u09E3]".regex
|"\u0A02"
|"\u0A3C"
|"[\u0A3E-\u0A42]".regex
|"[\u0A47-\u0A48]".regex
|"[\u0A4B-\u0A4D]".regex
|"[\u0A70-\u0A71]".regex
|"[\u0A81-\u0A83]".regex
|"\u0ABC"
|"[\u0ABE-\u0AC5]".regex
|"[\u0AC7-\u0AC9]".regex
|"[\u0ACB-\u0ACD]".regex
|"[\u0B01-\u0B03]".regex
|"\u0B3C"
|"[\u0B3E-\u0B43]".regex
|"[\u0B47-\u0B48]".regex
|"[\u0B4B-\u0B4D]".regex
|"[\u0B56-\u0B57]".regex
|"[\u0B82-\u0B83]".regex
|"[\u0BBE-\u0BC2]".regex
|"[\u0BC6-\u0BC8]".regex
|"[\u0BCA-\u0BCD]".regex
|"\u0BD7"
|"[\u0C01-\u0C03]".regex
|"[\u0C3E-\u0C44]".regex
|"[\u0C46-\u0C48]".regex
|"[\u0C4A-\u0C4D]".regex
|"[\u0C55-\u0C56]".regex
|"[\u0C82-\u0C83]".regex
|"[\u0CBE-\u0CC4]".regex
|"[\u0CC6-\u0CC8]".regex
|"[\u0CCA-\u0CCD]".regex
|"[\u0CD5-\u0CD6]".regex
|"[\u0D02-\u0D03]".regex
|"[\u0D3E-\u0D43]".regex
|"[\u0D46-\u0D48]".regex
|"[\u0D4A-\u0D4D]".regex
|"\u0D57"
|"[\u0D82-\u0D83]".regex
|"\u0DCA"
|"[\u0DCF-\u0DD4]".regex
|"\u0DD6"
|"[\u0DD8-\u0DDF]".regex
|"[\u0DF2-\u0DF3]".regex
|"\u0E31"
|"[\u0E34-\u0E3A]".regex
|"[\u0E47-\u0E4E]".regex
|"\u0EB1"
|"[\u0EB4-\u0EB9]".regex
|"[\u0EBB-\u0EBC]".regex
|"[\u0EC8-\u0ECD]".regex
|"[\u0F18-\u0F19]".regex
|"\u0F35"
|"\u0F37"
|"\u0F39"
|"[\u0F3E-\u0F3F]".regex
|"[\u0F71-\u0F84]".regex
|"[\u0F86-\u0F87]".regex
|"[\u0F90-\u0F97]".regex
|"[\u0F99-\u0FBC]".regex
|"\u0FC6"
|"[\u102C-\u1032]".regex
|"[\u1036-\u1039]".regex
|"[\u1056-\u1059]".regex
|"[\u17B4-\u17D3]".regex
|"\u18A9"
|"[\u20D0-\u20DC]".regex
|"\u20E1"
|"[\u302A-\u302F]".regex
|"[\u3099-\u309A]".regex
|"\uFB1E"
|"[\uFE20-\uFE23]".regex,

'UnicodeDigit
  :=
 "[\u0030-\u0039]".regex
|"[\u0660-\u0669]".regex
|"[\u06F0-\u06F9]".regex
|"[\u0966-\u096F]".regex
|"[\u09E6-\u09EF]".regex
|"[\u0A66-\u0A6F]".regex
|"[\u0AE6-\u0AEF]".regex
|"[\u0B66-\u0B6F]".regex
|"[\u0BE7-\u0BEF]".regex
|"[\u0C66-\u0C6F]".regex
|"[\u0CE6-\u0CEF]".regex
|"[\u0D66-\u0D6F]".regex
|"[\u0E50-\u0E59]".regex
|"[\u0ED0-\u0ED9]".regex
|"[\u0F20-\u0F29]".regex
|"[\u1040-\u1049]".regex
|"[\u1369-\u1371]".regex
|"[\u17E0-\u17E9]".regex
|"[\u1810-\u1819]".regex
|"[\uFF10-\uFF19]".regex,

'UnicodeConnectorPunctuation
  :=
 "\u005F"
|"[\u203F-\u2040]".regex
|"\u30FB"
|"[\uFE33-\uFE34]".regex
|"[\uFE4D-\uFE4F]".regex
|"\uFF3F"
|"\uFF65",

'RegularExpressionFirstChar
  := "[^*\\/\r\n\u2028\u2029\\\\\\[]".regex
  | 'RegularExpressionBackslashSequence
  | "[" ~ 'RegularExpressionClassChar.rep ~ "]",

'RegularExpressionChar
  := "[^\\/\r\n\u2028\u2029\\\\\\[]".regex
  | 'RegularExpressionBackslashSequence
  | "[" ~ 'RegularExpressionClassChar.rep ~ "]",

'RegularExpressionClassChar
  := "[^\r\n\u2028\u2029\\]\\\\]".regex
| 'RegularExpressionBackslashSequence,

'RegularExpressionBackslashSequence
  := "\\" ~ "[^\r\n\u2028\u2029]".regex
)
