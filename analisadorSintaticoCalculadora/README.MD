Igor Mendes Domingues Miras e Gabriel Menezes

--------------------------------
 Descricao da gramatica de LALG
--------------------------------

 1. <programa>      ::= program <ident> ; <corpo> .
 2. <corpo>         ::= <dc> begin <comandos> end
 3. <dc>            ::= <dc_c> <dc_v> <dc_p> <dc_func>
 4. <dc_c>          ::= const <ident> = <numero> ; <dc_c> | lambda
 5. <dc_v>          ::= var <variaveis> : <tipo_var> ; <dc_v> | lambda
 6. <tipo_var>      ::= real | integer | char
 7. <variaveis>     ::= <ident> <mais_var>
 8. <mais_var>      ::= , <variaveis> | lambda
 9. <dc_p>          ::= procedure <ident> <parametros> ; <corpo_p> <dc_p> | lambda
10. <dc_func>       ::= function <ident> <parametros> : <tipo_var> ; <dc_func> | lambda
11. <parametros>    ::= ( <lista_par> ) | lambda
12. <lista_par>     ::= <variaveis> : <tipo_var> <mais_par>
13. <mais_par>      ::= ; <lista_par> | lambda
14. <corpo_p>       ::= <dc_loc> begin <comandos> end ;
15. <dc_loc>        ::= <dc_v>
16. <lista_arg>     ::= ( <argumentos> ) | lambda
17. <argumentos>    ::= <ident> <mais_ident>
18. <mais_ident>    ::= ; <argumentos> | lambda
19. <pfalsa>        ::= else <cmd> | lambda
20. <comandos>      ::= <cmd> ; <comandos> | lambda
21. <cmd>           ::= read ( <variaveis> ) |
                        write ( <variaveis> ) |
                        while ( <condicao> ) do <cmd> |
                        if <condicao> then <cmd> <pfalsa> |
                        <ident> := <expressao> |
                        <ident> := <char> |
                        <ident> <lista_arg> |
                        begin <comandos> end |
                        repeat <comandos> until <condicao> |
                        for <ident> := <expressao> to <numero_int> do begin <comandos> end
22. <condicao>      ::= <expressao> <relacao> <expressao>
23. <relacao>       ::= = | <> | >= | <= | > | <
24. <expressao>     ::= <termo> <outros_termos>
25. <op_un>         ::= + | - | lambda
26. <outros_termos> ::= <op_ad> <termo> <outros_termos> | lambda
27. <op_ad>         ::= + | -
28. <termo>         ::= <op_un> <fator> <mais_fatores>
29. <mais_fatores>  ::= <op_mul> <fator> <mais_fatores> | lambda
30. <op_mul>        ::= * | /
31. <fator>         ::= <ident> | <numero> | ( <expressao> )
32. <numero>        ::= <numero_int> | <numero_real>


Comentarios de unica linha //

<char>        ::= caractere imprimivel entre aspas simples escapado ou nao com
<ident>       ::= sequencia de letras e digitos, comecando por letra
<numero_int>  ::= sequencia de digitos
<numero_real> ::= pelo menos um digito, seguido de um ponto decimal, seguido de uma sequencia de um ou mais digitos

Nao tem uso na gramatica em si, mas apenas para documentacao e implementacao:
<desconhecido> ::= representa um token que nao e' conhecido pela linguagem