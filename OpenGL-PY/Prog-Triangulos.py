# **********************************************************************
# PUCRS/Escola Politecnica
# COMPUTACAO GRAFICA
#
# Programa basico para criar aplicacoes 2D em OpenGL
#
# Marcio Sarroglia Pinho
# pinho@pucrs.br
# **********************************************************************

import os
import random
import sys
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ListaDeCoresRGB import *

from Ponto import *
from Triangulo import Triangulo

# Limites logicos da area de desenho
Min = Ponto()
Max = Ponto()

desenha = False

angulo = 0.0

PosicaoDoCampoDeVisao = Ponto()
PontoClicado = Ponto()

FoiClicado = False
imprimeMat = False

Triangulos = []

# Controle de exibição das Bounding Boxes / Envelopes
exibeAABB = False
exibeOBB = False
exibeCoberturaConvexa = False


# **********************************************************************
# Aleatorio(minimo, maximo)
#      Gera e retorna um numero real aleatorio no intervalo [minimo, maximo].
# **********************************************************************
def Aleatorio(minimo, maximo):
    return random.uniform(minimo, maximo)

# **********************************************************************
# CriaTriangulos()
#      Cria triangulos com vertices e cores aleatorias.
# **********************************************************************
def CriaTriangulos():
    for i in range(10):
        P1 = Ponto(Aleatorio(Min.x, Max.x), Aleatorio(Min.y, Max.y))
        P2 = Ponto(Aleatorio(Min.x, Max.x), Aleatorio(Min.y, Max.y))
        P3 = Ponto(Aleatorio(Min.x, Max.x), Aleatorio(Min.y, Max.y))

        cor = random.randint(0, GreenCopper) 
        #print ("Cor sorteada:", cor)

        Triangulos.append(Triangulo(P1, P2, P3, cor))


# **********************************************************************
# init()
#      Inicializa os parametros da aplicacao e cria os triangulos.
# **********************************************************************
def init():
    global Min, Max

    # Define a cor do fundo da tela
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Define os limites da janela de selecao (Window)
    Min = Ponto(-10, -5)
    Max = Ponto(10, 5)

    # Gera os triangulos aleatorios
    CriaTriangulos()


# **********************************************************************
# ImprimeModelView()
#      Imprime a matriz MODELVIEW corrente.
# **********************************************************************
def ImprimeModelView():
    M = glGetFloatv(GL_MODELVIEW_MATRIX)

    print("Matriz MODELVIEW:")

    for lin in range(4):
        for col in range(4):
            print("%8.3f" % M[col][lin], end=" ")
        print()

# **********************************************************************
# animate()
# Funcao chama enquanto o programa esta ocioso
# Calcula o FPS e numero de interseccao detectadas, junto com outras informacoes
# **********************************************************************
# Variaveis Globais
nFrames, TempoTotal, AccumDeltaT = 0, 0, 0
oldTime = time.time()

def animate():
    global nFrames, TempoTotal, AccumDeltaT, oldTime

    nowTime = time.time()
    dt = nowTime - oldTime
    oldTime = nowTime

    AccumDeltaT += dt
    TempoTotal += dt
    nFrames += 1
    
    if AccumDeltaT > 1.0/30:  # fixa a atualizacao da tela em 30s
        AccumDeltaT = 0
        glutPostRedisplay()
    if TempoTotal > 5.0:
        print ("Tempo Acumulado: ", TempoTotal," segundos. ")
        print ("Nros de Frames sem desenho: ", nFrames)
        print ("FPS(sem desenho): ", nFrames/TempoTotal)
        TempoTotal = 0
        nFrames = 0

# **********************************************************************
# reshape(w, h)
#      Trata o redimensionamento da janela OpenGL.
# **********************************************************************
def reshape(w, h):
    # Reset the coordinate system before modifying
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Define a area a ser ocupada pela area OpenGL dentro da Janela
    glViewport(0, 0, w, h)

    # Define os limites logicos da area OpenGL dentro da Janela
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# **********************************************************************
# DesenhaEixos()
#      Desenha os eixos horizontal e vertical da area de desenho.
# **********************************************************************
def DesenhaEixos():
    Meio = Ponto()

    Meio.x = (Max.x + Min.x) / 2
    Meio.y = (Max.y + Min.y) / 2
    Meio.z = (Max.z + Min.z) / 2

    glLineWidth(3)

    glBegin(GL_LINES)

    # Eixo horizontal
    glVertex2f(Min.x, Meio.y)
    glVertex2f(Max.x, Meio.y)

    # Eixo vertical
    glVertex2f(Meio.x, Min.y)
    glVertex2f(Meio.x, Max.y)

    glEnd()

    glLineWidth(1)


# **********************************************************************
# RotacionaAoRedorDeUmPonto(alfa, P)
#      Define uma rotacao de alfa graus ao redor do ponto P.
# **********************************************************************
def RotacionaAoRedorDeUmPonto(alfa, P):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0, 0, 1)
    glTranslatef(-P.x, -P.y, -P.z)


# **********************************************************************
# DesenhaTriangulos()
#      Desenha todos os triangulos e suas bounding boxes ativas.
# **********************************************************************
def DesenhaTriangulos():
    for T in Triangulos:
        T.Desenha()
        if exibeAABB:
            T.DesenhaAABB()
        if exibeOBB:
            T.DesenhaOBB()
        if exibeCoberturaConvexa:
            T.DesenhaCoberturaConvexa()


# **********************************************************************
# PintaTriangulosQueContemPonto(P)
#      Pinta todos os triangulos que contem o ponto P.
# **********************************************************************
def PintaTriangulosQueContemPonto(P):
    for T in Triangulos:
        if T.PontoNoTriangulo(P):
            T.Pinta()


# **********************************************************************
# DesenhaPontoClicado()
#      Desenha o ultimo ponto clicado pelo usuario.
# **********************************************************************
def DesenhaPontoClicado():
    glPointSize(8)

    defineCor(Black)

    glBegin(GL_POINTS)
    glVertex2f(PontoClicado.x, PontoClicado.y)
    glEnd()

    glPointSize(1)


# **********************************************************************
# display()
#      Desenha a cena e destaca os triangulos que contem o ponto clicado.
# **********************************************************************
def display():
    # Limpa a tela com a cor de fundo
    glClear(GL_COLOR_BUFFER_BIT)

    # Define os limites logicos da area OpenGL dentro da Janela
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # Coloque aqui as chamadas das rotinas que desenham os objetos
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    glLineWidth(1)
    glColor3f(0, 0, 0)

    DesenhaEixos()

    DesenhaTriangulos()

    if FoiClicado:
        PintaTriangulosQueContemPonto(PontoClicado)
        DesenhaPontoClicado()

    glutSwapBuffers()


# **********************************************************************
# ConverteMouseParaUniverso(x, y)
#      Converte as coordenadas do mouse para as coordenadas do universo.
# **********************************************************************
def ConverteMouseParaUniverso(x, y):
    viewport = glGetIntegerv(GL_VIEWPORT)

    vx = viewport[0]
    vy = viewport[1]
    largura = viewport[2]
    altura = viewport[3]

    ux = Min.x + ((x - vx) / largura) * (Max.x - Min.x)
    uy = Max.y - ((y - vy) / altura) * (Max.y - Min.y)

    return Ponto(ux, uy, 0)

# **********************************************************************
# Mouse(button, state, x, y)
#      Trata o clique do botao esquerdo do mouse.
# **********************************************************************
def Mouse(button, state, x, y):
    global PontoClicado, FoiClicado

    if state != GLUT_DOWN:
        return

    if button != GLUT_LEFT_BUTTON:
        return

    PontoClicado = ConverteMouseParaUniverso(x, y)

    FoiClicado = True

    PontoClicado.imprime("- Ponto no universo:")

    glutPostRedisplay()


# **********************************************************************
# The function called whenever a key is pressed. 
# # Note the use of Python tuples to pass in: (key, x, y)
# 
# **********************************************************************
ESCAPE = b'\x1b'
def keyboard(*args):
    global exibeAABB, exibeOBB, exibeCoberturaConvexa

    print(args)
    key = args[0]

    # Teclas para alternar a exibição das Bounding Boxes
    if key == b'1':
        exibeAABB = not exibeAABB
        print("Exibir AABB (Vermelho):", exibeAABB)
    elif key == b'2':
        exibeOBB = not exibeOBB
        print("Exibir OBB (Azul):", exibeOBB)
    elif key == b'3':
        exibeCoberturaConvexa = not exibeCoberturaConvexa
        print("Exibir Cobertura Convexa (Verde):", exibeCoberturaConvexa)
    elif key == b'0':
        exibeAABB = False
        exibeOBB = False
        exibeCoberturaConvexa = False
        print("Todas as Bounding Boxes ocultadas.")

    # Se a tecla ESC ou 'q' for pressionada, encerra o programa.
    if key == b'q' or key == ESCAPE:
        os._exit(0)

    glutPostRedisplay()


# **********************************************************************
# arrow_keys(a_keys, x, y)
#      Trata as teclas especiais pressionadas pelo usuario.
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        pass
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        pass
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        pass
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        pass

    glutPostRedisplay()


# **********************************************************************
# main()
#      Inicializa o GLUT, registra as funcoes de callback e inicia o programa.
# **********************************************************************
glutInit(sys.argv)

glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_RGB)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(1000, 500)

# Cria a janela na tela, definindo o nome da
# que aparecera na barra de titulo da janela.
glutInitWindowPosition(100, 100)

wind = glutCreateWindow(b"Trabalho 1 - Triangulos")

# executa algumas inicializacoes
init()

# Define que o tratador de evento para
# o redesenho da tela. A funcao "display"
# serah chamada automaticamente quando
# for necessario redesenhar a janela
glutDisplayFunc(display)
glutIdleFunc(animate)

# o redimensionamento da janela. A funcao "reshape"
# Define que o tratador de evento para
# serah chamada automaticamente quando
# o usuaio alterar o tamanho da janela
glutReshapeFunc(reshape)

# Define que o tratador de evento para
# as teclas. A funcao "keyboard"
# serah chamada automaticamente sempre
# o usuario pressionar uma tecla comum
glutKeyboardFunc(keyboard)
    
# Define que o tratador de evento para
# as teclas especiais(F1, F2,... ALT-A,
# ALT-B, Teclas de Seta, ...).
# A funcao "arrow_keys" serÃ¡ chamada
# automaticamente sempre o usuÃ¡rio
# pressionar uma tecla especial
glutSpecialFunc(arrow_keys)

glutMouseFunc(Mouse)
#glutMotionFunc(mouseMove)

try:
    glutMainLoop()
except SystemExit:
    pass