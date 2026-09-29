# ************************************************
#   Triangulo.py
#   Define a classe Triangulo
#   Autor: Marcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import *
from ListaDeCoresRGB import defineCor, Red, Blue, Green, Black


""" Classe Triangulo """
class Triangulo:
    def __init__(self, *args):
        self.Vertices = [Ponto(), Ponto(), Ponto()]
        self.Envelope = [Ponto(), Ponto()]  # AABB min e max
        self.OBBVertices = []                # Vértices do retângulo OBB
        self.cor = 0

        # Construtor que recebe somente a cor
        if len(args) == 1:
            self.cor = args[0]

        # Construtor que recebe um vetor de vertices e a cor
        elif len(args) == 2:
            V, cor = args
            for i in range(3):
                self.Vertices[i] = Ponto(V[i].x, V[i].y, V[i].z)
            self.cor = cor

        # Construtor que recebe tres pontos e a cor
        elif len(args) == 4:
            P1, P2, P3, cor = args
            self.Vertices[0] = Ponto(P1.x, P1.y, P1.z)
            self.Vertices[1] = Ponto(P2.x, P2.y, P2.z)
            self.Vertices[2] = Ponto(P3.x, P3.y, P3.z)
            self.cor = cor

        else:
            raise TypeError("Parametros invalidos para o construtor de Triangulo")

        self.CalculaEnvelope()
        self.CalculaOBB()

    # **********************************************************************
    # CalculaEnvelope()
    #      Calcula o envelope (AABB) do triangulo.
    #      Envelope[0] = ponto minimo e Envelope[1] = ponto maximo.
    # **********************************************************************
    def CalculaEnvelope(self):
        self.Envelope[0] = Ponto(self.Vertices[0].x, self.Vertices[0].y, self.Vertices[0].z)
        self.Envelope[1] = Ponto(self.Vertices[0].x, self.Vertices[0].y, self.Vertices[0].z)

        for i in range(1, 3):
            self.Envelope[0] = ObtemMinimo(self.Envelope[0], self.Vertices[i])
            self.Envelope[1] = ObtemMaximo(self.Envelope[1], self.Vertices[i])

    # **********************************************************************
    # CalculaOBB()
    #      Calcula a Oriented Bounding Box (OBB) alinhando-se com a maior
    #      aresta do triângulo.
    # **********************************************************************
    def CalculaOBB(self):
        # Encontra a maior aresta para definir o eixo principal da OBB
        max_dist_sq = -1
        idx_a, idx_b = 0, 1

        for i in range(3):
            j = (i + 1) % 3
            dx = self.Vertices[j].x - self.Vertices[i].x
            dy = self.Vertices[j].y - self.Vertices[i].y
            dist_sq = dx * dx + dy * dy
            if dist_sq > max_dist_sq:
                max_dist_sq = dist_sq
                idx_a, idx_b = i, j

        # Vetor diretor u (eixo longo) e vetor v (perpendicular)
        ax = self.Vertices[idx_b].x - self.Vertices[idx_a].x
        ay = self.Vertices[idx_b].y - self.Vertices[idx_a].y
        comprimento = math.sqrt(ax * ax + ay * ay)

        if comprimento < 1e-6:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = ax / comprimento, ay / comprimento

        vx, vy = -uy, ux  # Vetor perpendicular

        # Projeta os 3 vértices nos eixos u e v para encontrar min/max
        min_u, max_u = float('inf'), float('-inf')
        min_v, max_v = float('inf'), float('-inf')

        for vert in self.Vertices:
            proj_u = vert.x * ux + vert.y * uy
            proj_v = vert.x * vx + vert.y * vy

            min_u = min(min_u, proj_u)
            max_u = max(max_u, proj_u)
            min_v = min(min_v, proj_v)
            max_v = max(max_v, proj_v)

        # Reconstrói os 4 cantos da OBB no espaço global 2D
        # Canto 1: min_u, min_v
        # Canto 2: max_u, min_v
        # Canto 3: max_u, max_v
        # Canto 4: min_u, max_v
        self.OBBVertices = [
            Ponto(min_u * ux + min_v * vx, min_u * uy + min_v * vy),
            Ponto(max_u * ux + min_v * vx, max_u * uy + min_v * vy),
            Ponto(max_u * ux + max_v * vx, max_u * uy + max_v * vy),
            Ponto(min_u * ux + max_v * vx, min_u * uy + max_v * vy)
        ]

    # **********************************************************************
    # setCor(C)
    #      Define a cor do triangulo.
    # **********************************************************************
    def setCor(self, C):
        self.cor = C

    # **********************************************************************
    # getCor()
    #      Retorna a cor do triangulo.
    # **********************************************************************
    def getCor(self):
        return self.cor

    # **********************************************************************
    # Pinta(cor=None)
    #      Desenha o triangulo preenchido.
    #      Se uma cor for informada, usa esta cor somente neste desenho.
    # **********************************************************************
    def Pinta(self, cor=None):
        if cor is None:
            cor = self.cor

        defineCor(cor)

        glBegin(GL_TRIANGLES)
        glVertex2f(self.Vertices[0].x, self.Vertices[0].y)
        glVertex2f(self.Vertices[1].x, self.Vertices[1].y)
        glVertex2f(self.Vertices[2].x, self.Vertices[2].y)
        glEnd()

    # **********************************************************************
    # Desenha(cor=None)
    #      Desenha as arestas do triangulo.
    #      Se uma cor for informada, usa esta cor somente neste desenho.
    # **********************************************************************
    def Desenha(self, cor=None):
        if cor is None:
            cor = self.cor

        defineCor(cor)

        glBegin(GL_LINE_LOOP)
        glVertex2f(self.Vertices[0].x, self.Vertices[0].y)
        glVertex2f(self.Vertices[1].x, self.Vertices[1].y)
        glVertex2f(self.Vertices[2].x, self.Vertices[2].y)
        glEnd()

    # **********************************************************************
    # DesenhaAABB()
    #      Desenha o envelope alinhado aos eixos (AABB) do triangulo em vermelho.
    # **********************************************************************
    def DesenhaAABB(self):
        defineCor(Red)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.Envelope[0].x, self.Envelope[0].y)
        glVertex2f(self.Envelope[1].x, self.Envelope[0].y)
        glVertex2f(self.Envelope[1].x, self.Envelope[1].y)
        glVertex2f(self.Envelope[0].x, self.Envelope[1].y)
        glEnd()
        glLineWidth(1)

    # **********************************************************************
    # DesenhaEnvelope()
    #      Mantido por compatibilidade. Chamada para DesenhaAABB.
    # **********************************************************************
    def DesenhaEnvelope(self):
        self.DesenhaAABB()

    # **********************************************************************
    # DesenhaOBB()
    #      Desenha a Oriented Bounding Box (OBB) do triangulo em azul.
    # **********************************************************************
    def DesenhaOBB(self):
        defineCor(Blue)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        for p in self.OBBVertices:
            glVertex2f(p.x, p.y)
        glEnd()
        glLineWidth(1)

    # **********************************************************************
    # DesenhaCoberturaConvexa()
    #      Desenha a Cobertura Convexa (Convex Hull) em verde.
    #      Para um triângulo 2D, a Cobertura Convexa é o próprio contorno.
    # **********************************************************************
    def DesenhaCoberturaConvexa(self):
        defineCor(Green)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.Vertices[0].x, self.Vertices[0].y)
        glVertex2f(self.Vertices[1].x, self.Vertices[1].y)
        glVertex2f(self.Vertices[2].x, self.Vertices[2].y)
        glEnd()
        glLineWidth(1)

    # **********************************************************************
    # getVertices(i=None)
    #      Sem parametro, retorna todos os vertices do triangulo.
    #      Com um indice, retorna somente o vertice indicado.
    # **********************************************************************
    def getVertices(self, i=None):
        if i is None:
            return self.Vertices

        if i >= 0 and i < 3:
            return self.Vertices[i]

        return Ponto()

    # **********************************************************************
    # imprime()
    #      Imprime as coordenadas dos vertices do triangulo.
    # **********************************************************************
    def imprime(self):
        print("[", end="")

        for i in range(3):
            print("(", self.Vertices[i].x, ", ",
                  self.Vertices[i].y, ")", sep="", end="")

            if i < 2:
                print(" - ", end="")

        print("]")

    # **********************************************************************
    # PontoNoTriangulo(P)
    #      Verifica se o ponto P esta dentro do triangulo.
    #      Pontos sobre as arestas ou vertices sao considerados internos.
    # **********************************************************************
    def PontoNoTriangulo(self, P):
        # Calcula a orientacao de P em relacao a cada aresta
        d1 = (P.x - self.Vertices[1].x) * (self.Vertices[0].y - self.Vertices[1].y) - \
             (self.Vertices[0].x - self.Vertices[1].x) * (P.y - self.Vertices[1].y)

        d2 = (P.x - self.Vertices[2].x) * (self.Vertices[1].y - self.Vertices[2].y) - \
             (self.Vertices[1].x - self.Vertices[2].x) * (P.y - self.Vertices[2].y)

        d3 = (P.x - self.Vertices[0].x) * (self.Vertices[2].y - self.Vertices[0].y) - \
             (self.Vertices[2].x - self.Vertices[0].x) * (P.y - self.Vertices[0].y)

        # Verifica se existem orientacoes com sinais diferentes
        temNegativo = (d1 < 0) or (d2 < 0) or (d3 < 0)
        temPositivo = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (temNegativo and temPositivo)