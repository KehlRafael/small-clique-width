import networkx as nx
from networkx.classes.function import *
import numpy as np
import time
import sys
from xml.dom import minidom

# VARIAVEIS GLOBAIS
Eps = 0.0001
D = []
V = dict()
k = 0

# FUNCOES
def isZero(i,j):
    if (abs(i-j)<Eps):
        return True
    else:
        return False

def matrixIsZero(M):
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if not (isZero(M[i,j],0)):
                return False
    return True

def peek(stack):
    if len(stack) > 0:
        return stack[-1]
    return None

def sons(T,n):
    neigh = []
    left = 0
    right = 0
    try:
        neigh = list(all_neighbors(T, n))
        neigh.remove(T.nodes[n]['parent'])
    except ValueError:
        neigh = list(all_neighbors(T, n))

    if (neigh != None):
        if (len(neigh) == 2):
            if (T.nodes[neigh[0]]['side'] == 1):
                left = neigh[0]
                right = neigh[1]
            else:
                left = neigh[1]
                right = neigh[0]
        else:
            if (len(neigh) == 1):
                if (T.nodes[neigh[0]]['side'] == 1):
                    left  = neigh[0]
                    right = 0
                else:
                    left  = 0
                    right = neigh[0]
    return [left, right]

def createBox(c,i):
    return (0, 1,np.array([[-c]]),np.array([[i,2]]))

def combineBoxes(left,right,S,L,R,V):
    lin = []
    col = []

    # INICIALIZA E CRIA MATRIZES
    M = np.vstack((left[2], np.zeros((right[2].shape[0], left[2].shape[1]))))
    N = np.vstack((np.zeros((left[2].shape[0], right[2].shape[1])), right[2]))

    M = np.hstack((M,N))
    N = np.vstack((left[3], right[3]))

    # LIGA OS VERTICES COM ROTULOS EM S
    if (S != None):
        for pair in S:
            # Pega as linhas do par
            for i in range(left[2].shape[0]):
                if (N[i][1] == 2 and pair[0]==V[N[i][0]]):
                    lin.append(i)
            # Pega as colunas do par
            for j in range(left[2].shape[0],M.shape[0]):
                if (N[j][1] == 2 and pair[1]==V[N[j][0]]):
                    col.append(j)
            # Liga os pares
            for i in lin:
                for j in col:
                    M[i,j] = 1
                    M[j,i] = 1
            lin = []
            col = []

    # TROCA OS LABEL EM L E R
    if (L != None):
        for l in L:
            for i in range(left[2].shape[0]):
                if (V[N[i][0]]==l[0]):
                    V[N[i][0]] = l[1]
    if (R != None):
        for r in R:
            for i in range(left[2].shape[0],M.shape[0]):
                if (V[N[i][0]]==r[0]):
                    V[N[i][0]] = r[1]

    return (left[0] + right[0],left[1] + right[1],M,N)

def diagonalize(box):
    global V
    global k
    k1 = box[0]
    k2 = box[1]
    M  = box[2]
    N  = box[3]
    result = dict()

    # Garantir a unicidade em label tipo 2
    for i in range(M.shape[0]):
        if (N[i][1] == 2 and i+1 < M.shape[0]):
            for j in range(M.shape[0]-1,i,-1):
                if (N[j][1] == 2 and V[N[j][0]] == V[N[i][0]]):
                    M = lemma6(M,i,j)
                    k1 += 1
                    k2 -= 1
                    N[i][1] = 1
                    break
    # AGORA FAZER k1 <= k2
    if (k1>k2):
        while(True):
            for i in range(M.shape[0]):
                if(N[i][1] == 1):
                    # E tipo 1 e nao nula
                    if(not isZero(M[i,i],0)):
                        result = lemma7(M,N,i)
                        # Diagonalizou uma linha
                        M = result['M']
                        N = result['N']
                        k1 -= 1
                        break
                    # Tipo 1 e nula
                    elif(isZero(M[i,i],0) and i+1 < M.shape[0]):
                        for j in range(i+1,M.shape[0]):
                            if (N[j][1] == 1 and isZero(M[j, j], 0) and (not isZero(M[i,j],0)) and i!=j):
                                M = lemma7_0(M,i,j)
                                break
            # Verifica se terminou o Lemma 7
            if(lemma7done(M,N)):
                break
    # Checa a necessidade do Lemma 8
    if(k1>k2):
        result = lemma8(M,N,k1,k2)
        M = result['M']
        N = result['N']
        k1 = result['k1']

    return (k1,k2,M,N)

def lemma6(M,i,j):
    # Aplica na linha
    for u in range(M.shape[0]):
        M[i][u] = M[i][u]-M[j][u]
    # Aplica na coluna
    for u in range(M.shape[0]):
        M[u][i] = M[u][i]-M[u][j]
    return M

def lemma7(M,N,i):
    global D

    for j in range(M.shape[0]):
        if (i!=j):
            v = (M[i][j]/M[i][i])
            # Aplica passo na linha
            for u in range(M.shape[0]):
                M[j][u] = M[j][u] - v*M[i][u]
            # Aplica passo na coluna
            for u in range(M.shape[0]):
                M[u][j] = M[u][j] - v*M[u][i]

    D.append(M[i,i])
    M = np.delete(M, i, axis=0)
    M = np.delete(M, i, axis=1)
    N = np.delete(N, i, axis=0)

    return {'M':M,'N':N}

def lemma7_0(M,i,j):
    v = 1/2
    # Aplica primeiro passo na linha
    for u in range(M.shape[0]):
        M[j][u] = M[j][u] + v*M[i][u]
    # Aplica primeiro passo na coluna
    for u in range(M.shape[0]):
        M[u][j] = M[u][j] + v*M[u][i]

    # Aplica segundo passo na linha
    for u in range(M.shape[0]):
        M[i][u] = M[i][u] - M[j][u]
    # Aplica segundo passo na coluna
    for u in range(M.shape[0]):
        M[u][i] = M[u][i] - M[u][j]

    return M

def lemma7done(M,N):
    d = []
    T = M
    for i in range(M.shape[0]):
        if(N[i][1] == 2):
            d.append(i)

    T = np.delete(M, d, axis=0)
    T = np.delete(T, d, axis=1)

    if(T.shape[0] == 0):
        return True
    elif(matrixIsZero(T)):
        return True
    return False

def lemma8(M,N,k1,k2):
    global D
    result = dict()
    v = 0

    # Rever esse trecho
    result = cleanM(M,N,k1)
    k1 = result['k1']
    M = result['M']
    N = result['N']
    ###################
    result = groupM(M,N)
    M = result['M']
    N = result['N']

    # Caminha por M1 aplicando nas linhas
    for j in range(k1, k1 + k2):
        for i in range(j - k1 + 1, k1):
            # Constante pra zerar M[i,j]
            v = M[i,j]/M[j-k1,j]

            # Aplica pivo na linha i de M1
            for u in range(k1, k1 + k2):
                M[i][u] = M[i][u] - v * M[j-k1][u]
    # Caminha por M1 aplicando nas colunas
    for j in range(k1, k1 + k2):
        for i in range(j - k1 + 1, k1):
            # Constante pra zerar M[i,j]
            v = M[j, i] / M[j, j - k1]

            # Aplica pivo na linha i de M1
            for u in range(k1, k1 + k2):
                M[u][i] = M[u][i] - v * M[u][j - k1]

    # Limpa matriz e retorna
    result = cleanM(M, N, k1)

    return result

def groupM(M,N):
    for i in range(M.shape[0]):
        if(N[i][1] == 2 and i+1 < M.shape[0]):
            for j in range(M.shape[0]-1,i,-1):
                if(N[j][1] == 1):
                    # Troca a linha e coluna para agrupar os tipos
                    M[:, [i, j]] = M[:, [j, i]]
                    M[[i, j], :] = M[[j, i], :]
                    N[[i, j], :] = N[[j, i], :]
    return {'M':M,'N':N}

def cleanM(M,N,k1):
    global D
    v = True
    d = []
    k = 0

    i = 0
    while (i < M.shape[0]):
        j = 0
        while (j < M.shape[0]):
            if ((not isZero(M[i, j], 0)) and i != j):
                v = False
                j = M.shape[0]
            else:
                j += 1
        if (v):
            d.append(i)
            D.append(M[i, i])
        v = True
        i += 1

    M = np.delete(M, d, axis=0)
    M = np.delete(M, d, axis=1)
    N = np.delete(N, d, axis=0)
    k = len(d)

    return {'M':M,'N':N,'k1':k1-k}

def cleanD():
    global D
    for i in range(len(D)):
        if(isZero(D[i],0)):
            D[i]=0

# PROGRAMA PRINCIPAL
if __name__ == "__main__":
    global V
	global D
	global k

    # INICIALIZACOES
	xmlarq = sys.argv[1]
	C = []
	for i in range(2,len(sys.argv)):
		C.append(float(sys.argv[i]))

	xmldoc = minidom.parse(xmlarq)
	nodelist = xmldoc.getElementsByTagName('node')
	T = nx.Graph()
	S = dict()
	L = dict()
	R = dict()
	neigh = []
	stack = []
	id = 0
	root = 0
	left = 0
	right = 0

	# Para as iteracoes
	Vbase = dict()
	# Caso o array nao zerado
	N = 0
	M = 0

	currentTime = time.perf_counter()

	# IMPORTACAO DA ARVORE SINTATICA
	for n in nodelist:
		id = int(n.attributes['id'].value)
		T.add_node(id, parent=int(n.attributes['parent'].value), side=int(n.attributes['side'].value), leaf=int(n.attributes['leaf'].value))
		if(n.attributes['parent'].value != '0'):
		    T.add_edge(id, int(n.attributes['parent'].value))

		if(n.attributes['leaf'].value == '0'):
		    Slist = n.childNodes[1]
		    for pair in Slist.childNodes:
		        if (pair.nodeType == pair.ELEMENT_NODE):
		            S.setdefault(id, []).append([int(pair.attributes['L'].value), int(pair.attributes['R'].value)])

		    Llist = n.childNodes[3]
		    for pair in Llist.childNodes:
		        if (pair.nodeType == pair.ELEMENT_NODE):
		            L.setdefault(id, []).append([int(pair.attributes['L'].value), int(pair.attributes['R'].value)])

		    Rlist = n.childNodes[5]
		    for pair in Rlist.childNodes:
		        if (pair.nodeType == pair.ELEMENT_NODE):
		            R.setdefault(id, []).append([int(pair.attributes['L'].value), int(pair.attributes['R'].value)])
		else:
		    Vbase[id] = int(n.childNodes[1].firstChild.data)

	print('\nTempo de importacao da Arvore Sintatica')
	print(time.perf_counter()-currentTime)
	print('-------------------------------------------')

	# CALCULO DO k
	for n in V:
		if not (V[n] in stack):
		    stack.append(V[n])
	k = len(stack)
	for c in C:
		V = Vbase.copy()
		stack = []
		boxes = dict()
		# EXECUCAO DO ALGORITMO
		currentTime = time.perf_counter()
		# Acha a raiz
		for n in nodes(T):
		    if(T.nodes[n]['parent'] == 0):
		        root = n
		        break
		# Caminhamento Pos Fixado
		while(True):
		    while(root != 0):
		        neigh = sons(T, root)
		        if (neigh[1]!=0):
		            stack.append(neigh[1])
		        stack.append(root)
		        root = neigh[0]

		    root = stack.pop()
		    neigh = sons(T, root)

		    if (neigh[1]!=0 and
		        peek(stack) == neigh[1]):
		        stack.pop()
		        stack.append(root)
		        root = neigh[1]
		        neigh = sons(T,root)
		    else:
		        # Aplica o Algoritmo
		        if(T.nodes[root]['leaf']==1):
		            # Cria a box quando e folha
		            boxes[root] = createBox(c,root)
		        else:
		            # Combina as boxes caso contrario
		            boxes[root] = combineBoxes(boxes[neigh[0]],boxes[neigh[1]],S.get(root),L.get(root),R.get(root),V)
		            del boxes[neigh[0]]
		            del boxes[neigh[1]]
		            # Processa a box
		            boxes[root] = diagonalize(boxes[root])

		        root = 0
		    if (len(stack) <= 0):
		        break
		# Testa pra ver se terminou
		for i in boxes:
		    M = boxes[i][2]
		if(M.shape[0] != 1):
		    N = boxes[i][3]
		    N[:,1] = 1
		    boxes[i] = diagonalize((boxes[i][0]+boxes[i][1], 0,boxes[i][2],N))
		    M = boxes[i][2]
		if(M.shape[0] == 1):
		    D.append(M[0,0])
		# Limpa e imprime D
		print('Tempo de execucao do algoritmo para c =', c)
		print(time.perf_counter()-currentTime)
		cleanD()
		print('Vetor dos valores da diagonal')
		print(D)
		print('-------------------------------------------')
		D = []
		N = 0
		M = 0
