# small-clique-width
 Implementação do algoritmo para localização de autovalores em grafos de pequeno clique-width publicado pela Springer [aqui](https://link.springer.com/chapter/10.1007/978-3-319-77404-6_35), disponível [aqui no repositório](small-clique-width.pdf). O programa recebe como input um arquivo XML com a árvore sintática de uma k-expressão e retorna os valores da diagonal da matriz congruente à matriz de adjacências do grafo.
 
## Execução
 O script usa Numpy, Networkx e Minidom. O script pode ser executado com:
 ```
 python diagSCW.py xml_input
 ```
 Onde o arquivo XML possui a seguinte estrutura:
 ```xml
 <OpTree>
	<node id="" parent="" side="" leaf="">
		<S>
			<pair L="" R=""></pair>
		</S>
		<L>
			<pair L="" R=""></pair>
		</L>
		<R>
			<pair L="" R=""></pair>
		</R>
		<label></label>
	</node>
</OpTree>
 ```
 Os atributos de `node` são `id`,`parent`, `side` e `leaf`. `id` é o índice do nodo, `parent` é o índice do nodo pai na árvore e `0` para a raiz, `side` é o lado na árvore, com `1` para esquerda e `2` para direita, e `leaf`, que indica se o vértice é uma folha ou não. Dentro de cada `node` onde `leaf` é `1` temos um `label`, o nome do vértice que foi adicionado no grafo. Dentro de cada `node` onde `leaf` é `0` temos `S`, `L` e `R` que, por sua vez, possuem um número arbitrário de `pair`, os pares ordenados dos vértices envolvidos na operação. Cada `pair` possui os atributos `L` e `R`, que são, respectivamente, o `label` do vértice da esquerda e direita na operação.
 
## Algoritmo
 O algoritmo, bem como seus parâmetros, é descrito em detalhes no artigo e a implementação é detalhada na [apresentação](SIC/Apresentacao.pdf). Em resumo, é feito um caminhamento pós-fixado à esquerda na árvore sintática e processa a k-box (também detalhada no [artigo](https://link.springer.com/chapter/10.1007/978-3-319-77404-6_35) e [apresentação](SIC/Apresentacao.pdf)) de cada vértice até chegar na raiz.
 
## Apresentação
Esse trabalho foi apresentado no Salão de Iniciação Científica da UFRGS em 2018. A publicação do trabalho no repositório digital da UFRGS pode ser acessada [aqui](https://lume.ufrgs.br/handle/10183/191369). O [resumo](SIC/Resumo.pdf), [apresentação](SIC/Apresentacao.pdf) e [pôster](SIC/Poster.pdf) também estão disponíveis no repositório junto com os exemplos utilizados na apresentação.
