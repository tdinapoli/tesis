
<hr>

## instrumentación

<hr>

requisitos: ninguno
objetivo general: Automatizar el control del experimento para que pueda ser controlado desde una página web
objetivos específicos:
1. Diseñar el control
1. Programar controladores funcionando desde el software (python) de la red pitaya
    1. RPTTL
    2. A4988
    3. MOTOR
    4. SPECTROMETER
    5. fuente ITC4020
1. Comprobar que funcionan de forma esperada
    1. RPTTL
        1. Devuelve el estado correcto (ON/OFF)
        2. Se pueden enviar pulsos y tienen el delay correcto
    1. A4988: No hay forma de chequear
    1. MOTOR
        1. Rotar ángulo absoluto con un punto de referencia inicial
        1. Rotar ángulo relativo
        1. Rotar pasos: calcular relación paso/ángulo
    1. fuente ITC4020
        1. Medir potencia a mano vs controlada
        1. Medir intensidad en función del  tiempo para duty cycle a mano vs controlada
    1. SPECTROMETER
        1. Seguridad: que no se pueda pasar de las longitudes de onda máximas del espectrómetro
        1. Exactitud: ver que la longitud de onda seteada por software es efectivamente la que mide
        1. Precisión: Cuál es la menor longitud de onda que se puede correr al mover el motor?
    1. Tomar muestra de fluorescencia conocida y medir su espectro varias veces (ida y vuelta)
    1. Medir scattering de una muestra (emisión con el monocromador de emisión para tener pico angosto)
1. Implementar página web para realizar las mediciones

<hr>

## medición

<hr>

requisitos: 
1. instrumentación 4)
objetivo general: medir los tiempos de vida de los estados excitados de las UCNPs
1. Medir espectros
    1. 
2. Medir tiempos de vida
    1. Reproducir mediciones ya realizadas con los mismos parámetros y comparar resultados

<hr>

## modelado

<hr>

requisitos:
objetivo general: Modelar las ecucaciones diferenciales de los mecanismos de excitación de los estados de las UCNPs
objetivos específicos:
1. Escribir en poincare el "experimento": excitar f(t) y mirar em(t, lambda) y hacer em
1. Juan
2. Pollnau
3. Zhao

<hr>

## smartexp

<hr>
requisitos:
objetivo general: Hacer un software que elija inteligentemente el próximo punto a medir en un experimento con error
objetivos específicos:

1. ??
