# ***********************************************************************************
#   OpenGLBasico3D-V5.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa exibe dois Cubos em OpenGL
#   Para maiores informações, consulte
# 
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Outro exemplo de código em Python, usando OpenGL3D pode ser obtido em
#   http://openglsamples.sourceforge.net/cube_py.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# 
# ***********************************************************************************
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import Ponto
from Linha import Linha
from ListaDeCoresRGB import *
#from PIL import Image
import time
import random as ALE

import numpy as np
from PIL import Image

import time

Texturas = []

CantoEsquerdo = Ponto (-20,-1,-10)
ALVO = Ponto()
OBS = Ponto()
V1 = Ponto()

Angulo = 0.0

# **********************************************************************
# LoadTexture
# Retorna o id da textura lida
# **********************************************************************
def LoadTexture(nome) -> int:
    # carrega a imagem
    image = Image.open(nome)
    # print ("X:", image.size[0])
    # print ("Y:", image.size[1])
    # converte para o formato de OpenGL 
    #img_data = np.array(list(image.getdata()), np.uint8)
    img_data = np.array(list(image.get_flattened_data()), np.uint8)

    # Habilita o uso de textura
    glEnable ( GL_TEXTURE_2D )

    #Cria um ID para texura
    texture = glGenTextures(1)
    errorCode =  glGetError()
    if errorCode == GL_INVALID_OPERATION: 
        print ("Erro: glGenTextures chamada entre glBegin/glEnd.")
        return -1

    # Define a forma de armazenamento dos pixels na textura (1= alihamento por byte)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    # Define que tipo de textura ser usada
    # GL_TEXTURE_2D ==> define que ser· usada uma textura 2D (bitmaps)
    # e o nro dela
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    errorCode = glGetError()
    if errorCode != GL_NO_ERROR:
        print ("Houve algum erro na criacao da textura.")
        return -1

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    # neste ponto, "texture" tem o nro da textura que foi carregada
    errorCode = glGetError()
    if errorCode == GL_INVALID_OPERATION:
        print ("Erro: glTexImage2D chamada entre glBegin/glEnd.")
        return -1

    if errorCode != GL_NO_ERROR:
        print ("Houve algum erro na criacao da textura.")
        return -1
    #image.show()
    return texture

# **********************************************************************
#  Habilita o uso de textura 'NroDaTextura'
#  Se 'NroDaTextura' <0, desabilita o uso de texturas
#  Se 'NroDaTextura' for maior que a quantidade de texturas, gera
#  mensagem de erro e desabilita o uso de texturas
# **********************************************************************
def UseTexture (NroDaTextura: int):
    global Texturas
    if (NroDaTextura>len(Texturas)):
        print ("Numero invalido da textura.")
        glDisable (GL_TEXTURE_2D)
        return
    if (NroDaTextura < 0):
        glDisable (GL_TEXTURE_2D)
    else:
        glEnable (GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, Texturas[NroDaTextura])



# **********************************************************************
#  init()
#  Inicializa os parÃ¢metros globais de OpenGL
#/ **********************************************************************
def init():
    # Define a cor do fundo da tela (BRANCO) 
    glClearColor(1.0, 1.0, 0.0, 1.0)  # Fundo de tela amarelo
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)

    #image = Image.open("Tex.png")
    #print ("X:", image.size[0])
    #print ("Y:", image.size[1])
    #image.show()
    #print ("RANDOMICO: ", random.randint(0,10))

    global ALVO, OBS, V1
    ALVO = Ponto (0,1,0)
    OBS = Ponto (0,1,10)
    V1 = ALVO - OBS

    # Carrega texturas
    global Texturas 
    Texturas += [LoadTexture("bricks.jpg")] 
    Texturas += [LoadTexture("Piso.jpg")] 
    Texturas += [LoadTexture("CROSS.jpg")]

    
# **********************************************************************
#  reshape( w: int, h: int )
#  trata o redimensionamento da janela OpenGL
#
# **********************************************************************
def reshape(w: int, h: int):
    global AspectRatio
	# Evita divisÃ£o por zero, no caso de uam janela com largura 0.
    if h == 0:
        h = 1
    # Ajusta a relacao entre largura e altura para evitar distorcao na imagem.
    # Veja funcao "PosicUser".
    AspectRatio = w / h
	# Reset the coordinate system before modifying
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Seta a viewport para ocupar toda a janela
    glViewport(0, 0, w, h)
    
    PosicUser()
# **********************************************************************
def DefineLuz():
    # Define cores para um objeto dourado
    LuzAmbiente = [0.4, 0.4, 0.4] 
    LuzDifusa   = [0.7, 0.7, 0.7]
    LuzEspecular = [0.9, 0.9, 0.9]
    PosicaoLuz0  = [2.0, 3.0, 0.0 ]  # PosiÃ§Ã£o da Luz
    Especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable ( GL_COLOR_MATERIAL )

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, LuzAmbiente)
    # Define os parametros da luz numero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, LuzAmbiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, LuzDifusa  )
    glLightfv(GL_LIGHT0, GL_SPECULAR, LuzEspecular  )
    glLightfv(GL_LIGHT0, GL_POSITION, PosicaoLuz0 )
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT,GL_SPECULAR, Especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT,GL_SHININESS,51)

# **********************************************************************
# DesenhaCubos()
# Desenha o cenario
#
# **********************************************************************
def DesenhaCubo():
    glutSolidCube(1)
    
def PosicUser():

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Seta a viewport para ocupar toda a janela
    # glViewport(0, 0, 500, 500)
    #print ("AspectRatio", AspectRatio)
    
    gluPerspective(60,AspectRatio,0.01,50) # Projecao perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(OBS.x,OBS.y, OBS.z, ALVO.x,ALVO.y, ALVO.z, 0.0,1.0,0.0)

# **********************************************************************
# void DesenhaLadrilho(int corBorda, int corDentro)
# Desenha uma cÃ©lula do piso.
# O ladrilho tem largula 1, centro no (0,0,0) e estÃ¡ sobre o plano XZ
# **********************************************************************
def DesenhaLadrilho(corBorda, corDentro):
    glColor3f(0,0,1) # desenha QUAD preenchido
    defineCor(corDentro)
    glBegin ( GL_QUADS )
    glNormal3f(0,1,0)
    glVertex3f(-0.5,  0.0, -0.5)
    glVertex3f(-0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0, -0.5)
    glEnd()

    
    glColor3f(1,1,1) # desenha a borda da QUAD 
    defineCor(corBorda)
    glLineWidth(3)
    glBegin ( GL_LINE_STRIP )
    glNormal3f(0,1,0)
    glVertex3f(-0.5,  0.0, -0.5)
    glVertex3f(-0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0, -0.5)
    glEnd()
    glLineWidth(1)


# **********************************************************************
# void DesenhaLadrilhoTEX(int corBorda, int corDentro)
# Desenha uma celula do piso.
# O ladrilho tem largula 1, centro no (0,0,0) e esta' sobre o plano XZ
# **********************************************************************
def DesenhaLadrilhoTEX(idTextura):

    glColor3f(1,1,1) # desenha QUAD em branco, pois vai usa textura
    UseTexture(idTextura) # Habilita a textura id_textura

    glBegin ( GL_QUADS )
    glNormal3f(0,1,0)
    glTexCoord(0,0)
    glVertex3f(-0.5,  0.0, -0.5)
    glTexCoord(0,1)
    glVertex3f(-0.5,  0.0,  0.5)
    glTexCoord(1,1)
    glVertex3f( 0.5,  0.0,  0.5)
    glTexCoord(1,0)
    glVertex3f( 0.5,  0.0, -0.5)
    glEnd()
    
    glColor3f(1,1,1) # desenha a borda da QUAD 
    glBegin ( GL_LINE_LOOP )
    glNormal3f(0,1,0)
    glVertex3f(-0.5,  0.0, -0.5)
    glVertex3f(-0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0, -0.5)
    glEnd()
    
# **********************************************************************
#
# **********************************************************************
def DesenhaPlacas():
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    DesenhaLadrilhoTEX(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1, 1, 0)
    glRotatef(90, 1, 0, 0)
    DesenhaLadrilhoTEX(0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-1, 1, 0)
    glRotatef(90, 1, 0, 0)
    glRotatef(Angulo, 0, 1, 0)
    DesenhaLadrilhoTEX(2)
    glPopMatrix()


# **********************************************************************
def DesenhaPiso():
    ALE.seed(0) # Usa uma semente fixa para gerar sempre as mesmas cores no piso
    glPushMatrix()
#    glTranslated(-20,-1,-10)
    glTranslated(CantoEsquerdo.x,CantoEsquerdo.y,CantoEsquerdo.z)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            DesenhaLadrilho(White, ALE.randint(0, 30))
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

# **********************************************************************
#  void DesenhaCentro()
# **********************************************************************
def DesenhaCentro():
    glColor3f(0.7,0,0);
    glutSolidSphere(0.3, 20, 20);

# **********************************************************************
# display()
# Funcao que exibe os desenhos na tela
#
# **********************************************************************
def display():
    global Angulo
    # Limpa a tela com  a cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    DefineLuz()
    PosicUser()

    glMatrixMode(GL_MODELVIEW)

    UseTexture (-1) # desabilita o uso de texturas
    DesenhaPiso() 
    glColor3f(0.5,0.0,0.0) # Vermelho
    glPushMatrix()
    glTranslatef(5,-1,3)
    glRotatef(Angulo,0,1,0)
    DesenhaCubo()
    glPopMatrix()
    
    glColor3f(0.5,0.5,0.0) # Amarelo
    glPushMatrix()
    glTranslatef(7,0,-1)
    glRotatef(-Angulo,0,1,0)
    DesenhaCubo()
    glPopMatrix()

    Angulo = Angulo + 1

    DesenhaPlacas()
    UseTexture (-1) # desabilita o uso de texturas

    DesenhaCentro()

    glutSwapBuffers()


# **********************************************************************
# animate()
# Funcao chama enquanto o programa esta ocioso
# Calcula o FPS e numero de interseccao detectadas, junto com outras informacoes
#
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
    
    if AccumDeltaT > 1.0/30:  # fixa a atualizaÃ§Ã£o da tela em 30
        AccumDeltaT = 0
        glutPostRedisplay()

    

# **********************************************************************
#  keyboard ( key: int, x: int, y: int )
#
# **********************************************************************
ESCAPE = b'\x1b'
def keyboard(*args):
    global image
    #print (args)
    # If escape is pressed, kill everything.

    if args[0] == ESCAPE:   # Termina o programa qdo
        os._exit(0)         # a tecla ESC for pressionada

    if args[0] == b' ':
        init()

    if args[0] == b'i':
        image.show()

    # ForÃ§a o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************

def arrow_keys(a_keys: int, x: int, y: int):

    global ALVO, OBS, V1

    # ALVO.imprime("ALVO:")
    # OBS.imprime("OBS: ")
    # V1.imprime("V1: ")
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        V1 = ALVO-OBS
        V1.versor()
        OBS = OBS + V1
        ALVO = ALVO + V1

    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        V1 = ALVO-OBS
        V1.versor()
        OBS = OBS - V1
        ALVO = ALVO - V1    
    
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        V1 = ALVO-OBS
        V1.rotacionaY(5)
        ALVO = OBS + V1

    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        V1 = ALVO-OBS
        V1.rotacionaY(-5)
        ALVO = OBS + V1

    glutPostRedisplay()


def mouse(button: int, state: int, x: int, y: int):
    glutPostRedisplay()

def mouseMove(x: int, y: int):
    glutPostRedisplay()

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA|GLUT_DEPTH | GLUT_RGB)
glutInitWindowPosition(0, 0)

# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(900, 450)
# Cria a janela na tela, definindo o nome da
# que aparecera na barra de tÃ­tulo da janela.
glutInitWindowPosition(100, 100)
wind = glutCreateWindow(b"OpenGL 3D")

# executa algumas inicializaÃ§Ãµes
init ()

# Define que o tratador de evento para
# o redesenho da tela. A funcao "display"
# serÃ¡ chamada automaticamente quando
# for necessÃ¡rio redesenhar a janela
glutDisplayFunc(display)
glutIdleFunc (animate)

# o redimensionamento da janela. A funcao "reshape"
# Define que o tratador de evento para
# serÃ¡ chamada automaticamente quando
# o usuÃ¡rio alterar o tamanho da janela
glutReshapeFunc(reshape)

# Define que o tratador de evento para
# as teclas. A funcao "keyboard"
# serÃ¡ chamada automaticamente sempre
# o usuÃ¡rio pressionar uma tecla comum
glutKeyboardFunc(keyboard)
    
# Define que o tratador de evento para
# as teclas especiais(F1, F2,... ALT-A,
# ALT-B, Teclas de Seta, ...).
# A funcao "arrow_keys" serÃ¡ chamada
# automaticamente sempre o usuÃ¡rio
# pressionar uma tecla especial
glutSpecialFunc(arrow_keys)

#glutMouseFunc(mouse)
#glutMotionFunc(mouseMove)


try:
    # inicia o tratamento dos eventos
    glutMainLoop()
except SystemExit:
    pass
