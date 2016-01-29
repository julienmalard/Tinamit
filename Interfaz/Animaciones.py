import time
import math as mat


def intercambiar(actual, nuevo, dirección):
    x_act = actual.winfo_x()
    y_act = actual.winfo_y()
    ancho_act = actual.winfo_width()
    altura_act = actual.winfo_height()

    if dirección == 'izquierda':
        nuevo.place(x=(x_act + ancho_act), y=y_act)
        pos_inic = [x_act, x_act + ancho_act]
        distancia = ancho_act
    elif dirección == 'derecha':
        nuevo.place(x=(x_act - ancho_act), y=y_act)
        pos_inic = [x_act, x_act - ancho_act]
        distancia = ancho_act
    elif dirección == 'arriba':
        nuevo.place(x=x_act, y=(y_act + altura_act))
        pos_inic = [y_act, y_act + altura_act]
        distancia = altura_act
    elif dirección == 'abajo':
        nuevo.place(x=x_act, y=(y_act - altura_act))
        pos_inic = [y_act, y_act - altura_act]
        distancia = altura_act
    else:
        raise ValueError

    nuevo.lift()
    deslizar([actual, nuevo], pos_inic, dirección, distancia, paso=0.025, tiempo=0.5)


def sobreponer(actual, nuevo, dirección):
    x_act = actual.winfo_x()
    y_act = actual.winfo_y()
    ancho_act = actual.winfo_width()
    altura_act = actual.winfo_height()

    if dirección == 'izquierda':
        nuevo.place(x=(x_act + ancho_act), y=y_act)
        pos_inic = [x_act + ancho_act]
        distancia = ancho_act
    elif dirección == 'derecha':
        nuevo.place(x=(x_act - ancho_act), y=y_act)
        pos_inic = [x_act - ancho_act]
        distancia = ancho_act
    elif dirección == 'arriba':
        nuevo.place(x=x_act, y=(y_act + altura_act))
        pos_inic = [y_act - altura_act]
        distancia = altura_act
    elif dirección == 'abajo':
        nuevo.place(x=x_act, y=(y_act - altura_act))
        pos_inic = [y_act + altura_act]
        distancia = altura_act
    else:
        raise ValueError
    nuevo.lift()

    deslizar([nuevo], pos_inic, dirección, distancia, paso=0.025, tiempo=0.5)


def quitar(actual, dirección):
    x_act = actual.winfo_x()
    y_act = actual.winfo_y()
    ancho_act = actual.winfo_width()
    altura_act = actual.winfo_height()

    if dirección == 'izquierda' or dirección == 'derecha':
        pos_inic = [x_act]
        distancia = ancho_act
    elif dirección == 'arriba' or dirección == 'abajo':
        pos_inic = [y_act]
        distancia = altura_act
    else:
        raise ValueError

    deslizar([actual], pos_inic, dirección, distancia, paso=0.025, tiempo=.5)
    actual.lower()


def deslizar(objetos, pos_inic, dirección, distancia, paso=0.025, método='logístico', tiempo=0.5):

    for i in range(1, int(tiempo/paso) + 1):
        t = i*paso
        if método == 'logístico':
            nueva_pos = mat.ceil(distancia/(1+mat.exp(-12/tiempo * (t-tiempo/2))))
        elif método == 'linear':
            nueva_pos = mat.ceil(distancia*t/tiempo)
        else:
            raise ValueError
        if i == int(tiempo/paso):
            nueva_pos = distancia

        if dirección == 'izquierda':
            for n, o in enumerate(objetos):
                o.place(x=pos_inic[n] - nueva_pos)
                o.update()
        elif dirección == 'derecha':
            for n, o in enumerate(objetos):
                o.place(x=pos_inic[n] + nueva_pos)
                o.update()
        elif dirección == 'arriba':
            for n, o in enumerate(objetos):
                o.place(y=pos_inic[n] - nueva_pos)
                o.update()
        elif dirección == 'abajo':
            for n, o in enumerate(objetos):
                o.place(y=pos_inic[n] + nueva_pos)
                o.update()
        else:
            raise ValueError

        time.sleep(paso)
