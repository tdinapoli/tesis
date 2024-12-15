

espectros 0.3800_0.0500 corridos en 1nm. debería arrancar en 370 y arrancó en 369, y siguió consistentemente con 1nm menos hasta que se quedó sin memoria en 454. Abajo hablo del problema de la memoria.

Problema: Me quedé sin memoria

```python
  File "/root/scripts/2024-09-02/spectrum.py", line 137, in main
    df = measure_spectrum(
  File "/root/scripts/2024-09-02/spectrum.py", line 61, in meas_spectrum
    df = spec.get_emission(
  File "/root/refurbishedPTI/src/refurbishedPTI/instruments.py", line 608, in get_emission
    df = self.get_spectrum(
  File "/root/refurbishedPTI/src/refurbishedPTI/instruments.py", line 656, in get_spectrum
    for el in spectrum_iterator:
  File "/root/refurbishedPTI/src/refurbishedPTI/instruments.py", line 684, in _yield_spectrum
    photons, time_measured = self.get_intensity(
  File "/root/refurbishedPTI/src/refurbishedPTI/instruments.py", line 694, in get_intensity
    photons += self.integrate(seconds, feed_data=feed_data)
  File "/root/refurbishedPTI/src/refurbishedPTI/instruments.py", line 715, in integrate
    feed_data(data, rep) 
  File "/root/scripts/2024-09-02/spectrum.py", line 88, in _feed_data
    np.save(p, data)
  File "<__array_function__ internals>", line 5, in save
  File "/usr/lib/python3/dist-packages/numpy/lib/npyio.py", line 529, in save
    format.write_array(fid, arr, allow_pickle=allow_pickle,
  File "/usr/lib/python3/dist-packages/numpy/lib/format.py", line 683, in write_array
    array.T.tofile(fp)
OSError: 32500 requested and 27120 written
```

No entiendo por qué porque cada tanto iba copiando los datos y borrandolos (quizás no lo hice lo suficientemente rápido parece).

Solución: creé una nueva particion con el espacio sin usar usando gparted. mkpart primary ext4. En esta nueva particion tengo 23 gigas libres, así que voy a empezar a usar esa para copiar los datos de ahora en más.

Reanudo la medición de antes, ahora arrancando de 454. Esta vez las longitudes de onda no estan desfasadas. En 546 me volví a fijar y estaba desfasado por +1 nm de vuelta.

Freno la medición en 577 cuentas. Al hacer el gráfico del potencial en función del tiempo para los picos más altos veo que está saturando el sensor. Por ejemplo, el gráfico para wl=542 da

![alt text](./analysis/images/señal_en_pico_lejos.png "Title")

![alt text](./analysis/images/señal_en_pico_cerca.png "Title")

A solucionar para mañana.

# 2024-09-03

tomo el primer espectro con 0.38 A, optical power varía pero ~0.238W. De 370 a 700.
Lo hago con 1/4 de vuelta de rendija porque la intensidad en 542, el pico más alto era muy alta con 1/2 de vuelta, las señales eran puro pico.
Ahora (en 608), la potencia está en 0.248, 0.25. Va fluctuando bastante. Se podría medir para cada punto.

Se me "acabo la memoria" en ~ 690. "Sigue escribiendo", no se cómoo.

Para el espectro con 0.34 A ahora si me dice, no space left, luego de medir la longitud de onda 666. copié todos los datos hasta 545.

# 2024-09-04

Sigo midiendo. Ahora el cuello de botella es la trasnferencia de datos. Cada directorio con datos tarda ~23 segs mientras que medir dicho directorio tarda ~13 segs. 
Cada espectro, es decir los directorios de 370 a 699 (cada wl) con sus correspondientes 384 (para 0.1s de tiempo de integración) dataframes.pickle pesa ~22gb. 
Luego de comprimirlo en una tarball pesan ~14gb.

Guardo los datos en:
directorio base = /home/tomi/Documents/academicos/facultad/tesis/tesis
1. mi pc sin comprimir, directorios base/measurement_scripts/2024-08-29/data y base/measurement_scripts/2024-08-09/get_data_testing/data_testing.
1. mi pc, en los mismos directorios que antes pero comprimidos con tarball.
1. mi drive, carpeta tesis/data/paper-nanoscale/2024-09-03. subidas como tarballs
1. datos crudos en el disco externo que estaba en el LEC para SPIM. El disco este es lentísimo, no se q le pasa así que dejo de copiar.

corto el espectro de /mnt/data/2024-09-04/0.2759_0.1000 en 617 nm y me voy a jugar al fulbo.
Y la copia de archivos la corto en 410, es decir 410 lo tengo que copiar de vuelta.
Nuevamente medí todos los espectros con 1/4 de vuelta de rendija.

# 2024-09-05

Nada destacable

# 2024-09-06

hago analisis de los picos en data_analysis/peak_counting

# 2024-09-09

Termino de tomar espectro con potencia 0.24 y tomo con 0.20.
Además, tomo espectro de vuelta con 0.38, pero esta vez con la tercera decimación.
La idea es que cunado llego a casa puedo verificar si da más o menos lo mismo tomar con la tercera decimación que con la segunda. 
Si es así, tomar cada espectro me tomaría la mitad de tiempo y pesaría la mitad (guardandome los datos crudos).
Estaba tomando el espectro con potencia 0.38 y se clavó el laser porque estaba muy alta la temperatura cuando estaba tomando 678/677. 
Me voy un rato y cuando vuelvo retomo.

# 2024-09-11

Vuelvo a medir espectros. 
Ahora arranco en 0.18A y voy bajando. 
Además, mido los espectros con decimación 3, y de ahora en más, hasta que cambie, con tiempo de integración 0.5.
Por lo tanto, para cada punto tengo 961 pantallas de osciloscopio.
Además, cambié la técnica de conteo a la de strats.negative_original con threshold de 1.5

Corto la medición en 409 nm porque:
1. Como tengo 961 pantallas por wl, me iba a quedar sin memoria
1. Si hago eso, no voy a poder adquirir los datos porque de vuelta me va a pasar lo del cuello de botella de copiar los datos.

Las cuentas que habían aparecido hasta el momento son:
```python
{'wavelength': 370, 'counts': 391, 'integration_time': 0.00052}
{'wavelength': 371, 'counts': 313, 'integration_time': 0.00052}
{'wavelength': 372, 'counts': 406, 'integration_time': 0.00052}
{'wavelength': 373, 'counts': 451, 'integration_time': 0.00052}
{'wavelength': 374, 'counts': 528, 'integration_time': 0.00052}
{'wavelength': 375, 'counts': 784, 'integration_time': 0.00052}
{'wavelength': 376, 'counts': 2540, 'integration_time': 0.00052}
{'wavelength': 377, 'counts': 5609, 'integration_time': 0.00052}
{'wavelength': 378, 'counts': 9575, 'integration_time': 0.00052}
{'wavelength': 379, 'counts': 11166, 'integration_time': 0.00052}
{'wavelength': 380, 'counts': 9626, 'integration_time': 0.00052}
{'wavelength': 381, 'counts': 8879, 'integration_time': 0.00052}
{'wavelength': 382, 'counts': 9639, 'integration_time': 0.00052}
{'wavelength': 383, 'counts': 10478, 'integration_time': 0.00052}
{'wavelength': 384, 'counts': 8746, 'integration_time': 0.00052}
{'wavelength': 385, 'counts': 4953, 'integration_time': 0.00052}
{'wavelength': 386, 'counts': 2539, 'integration_time': 0.00052}
{'wavelength': 387, 'counts': 1269, 'integration_time': 0.00052}
{'wavelength': 388, 'counts': 908, 'integration_time': 0.00052}
{'wavelength': 389, 'counts': 653, 'integration_time': 0.00052}
{'wavelength': 390, 'counts': 496, 'integration_time': 0.00052}
{'wavelength': 391, 'counts': 398, 'integration_time': 0.00052}
{'wavelength': 392, 'counts': 366, 'integration_time': 0.00052}
{'wavelength': 393, 'counts': 323, 'integration_time': 0.00052}
{'wavelength': 394, 'counts': 302, 'integration_time': 0.00052}
{'wavelength': 395, 'counts': 294, 'integration_time': 0.00052}
{'wavelength': 396, 'counts': 320, 'integration_time': 0.00052}
{'wavelength': 397, 'counts': 304, 'integration_time': 0.00052}
{'wavelength': 398, 'counts': 358, 'integration_time': 0.00052}
{'wavelength': 399, 'counts': 563, 'integration_time': 0.00052}
{'wavelength': 400, 'counts': 879, 'integration_time': 0.00052}
{'wavelength': 401, 'counts': 1583, 'integration_time': 0.00052}
{'wavelength': 402, 'counts': 1944, 'integration_time': 0.00052}
{'wavelength': 403, 'counts': 2320, 'integration_time': 0.00052}
{'wavelength': 404, 'counts': 3922, 'integration_time': 0.00052}
{'wavelength': 405, 'counts': 15151, 'integration_time': 0.00052}
{'wavelength': 406, 'counts': 34623, 'integration_time': 0.00052}
{'wavelength': 407, 'counts': 46922, 'integration_time': 0.00052}
{'wavelength': 408, 'counts': 51854, 'integration_time': 0.00052}
{'wavelength': 409, 'counts': 69962, 'integration_time': 0.00052}
```

Aprovecho para notar: antes de cortar, en cada medición estaba grabando los datos al disco. 
Además estaba conectado con otra conexión ssh a la RP (es decir con 2 en total), y estaba copiando los datos por scp con el script de python. 
Ahora no hago nada de eso: sólo imprimo un diccionario para cada punto del espectro. 
Antes, el tiempo de adquisición para cada punto era de ~26 segundos.
Ahora es ~17 segundos.

Convertí el espectro de 0.18 a pickle de la siguiente forma (estaba partido en 2 por lo que comenté antes)

```python
missing = [
{'wavelength': 370, 'counts': 391, 'integration_time': 0.00052},
{'wavelength': 371, 'counts': 313, 'integration_time': 0.00052},
{'wavelength': 372, 'counts': 406, 'integration_time': 0.00052},
{'wavelength': 373, 'counts': 451, 'integration_time': 0.00052},
{'wavelength': 374, 'counts': 528, 'integration_time': 0.00052},
{'wavelength': 375, 'counts': 784, 'integration_time': 0.00052},
{'wavelength': 376, 'counts': 2540, 'integration_time': 0.00052},
{'wavelength': 377, 'counts': 5609, 'integration_time': 0.00052},
{'wavelength': 378, 'counts': 9575, 'integration_time': 0.00052},
{'wavelength': 379, 'counts': 11166, 'integration_time': 0.00052},
{'wavelength': 380, 'counts': 9626, 'integration_time': 0.00052},
{'wavelength': 381, 'counts': 8879, 'integration_time': 0.00052},
{'wavelength': 382, 'counts': 9639, 'integration_time': 0.00052},
{'wavelength': 383, 'counts': 10478, 'integration_time': 0.00052},
{'wavelength': 384, 'counts': 8746, 'integration_time': 0.00052},
{'wavelength': 385, 'counts': 4953, 'integration_time': 0.00052},
{'wavelength': 386, 'counts': 2539, 'integration_time': 0.00052},
{'wavelength': 387, 'counts': 1269, 'integration_time': 0.00052},
{'wavelength': 388, 'counts': 908, 'integration_time': 0.00052},
{'wavelength': 389, 'counts': 653, 'integration_time': 0.00052},
{'wavelength': 390, 'counts': 496, 'integration_time': 0.00052},
{'wavelength': 391, 'counts': 398, 'integration_time': 0.00052},
{'wavelength': 392, 'counts': 366, 'integration_time': 0.00052},
{'wavelength': 393, 'counts': 323, 'integration_time': 0.00052},
{'wavelength': 394, 'counts': 302, 'integration_time': 0.00052},
{'wavelength': 395, 'counts': 294, 'integration_time': 0.00052},
{'wavelength': 396, 'counts': 320, 'integration_time': 0.00052},
{'wavelength': 397, 'counts': 304, 'integration_time': 0.00052},
{'wavelength': 398, 'counts': 358, 'integration_time': 0.00052},
{'wavelength': 399, 'counts': 563, 'integration_time': 0.00052},
{'wavelength': 400, 'counts': 879, 'integration_time': 0.00052},
{'wavelength': 401, 'counts': 1583, 'integration_time': 0.00052},
{'wavelength': 402, 'counts': 1944, 'integration_time': 0.00052},
{'wavelength': 403, 'counts': 2320, 'integration_time': 0.00052},
{'wavelength': 404, 'counts': 3922, 'integration_time': 0.00052},
{'wavelength': 405, 'counts': 15151, 'integration_time': 0.00052},
{'wavelength': 406, 'counts': 34623, 'integration_time': 0.00052},
{'wavelength': 407, 'counts': 46922, 'integration_time': 0.00052},
{'wavelength': 408, 'counts': 51854, 'integration_time': 0.00052}]
df2 = pd.read_pickle('/home/tomi/Documents/academicos/facultad/tesis/tesis/measurement_scripts/2024-08-29/data/spectrums/409_700_1_0.5_0.180.pickle')
current = df2.to_dict('records')
df3 = pd.DataFrame(missing+current)
df3
```

Al tomar el espectro con 0.16A obtengo el error:
```python
Traceback (most recent call last):
  File "/root/scripts/2024-09-03/spectrum.py", line 148, in <module>
    main()
  File "/root/scripts/2024-09-03/spectrum.py", line 143, in main
    df.to_pickle(f"{data_path}/{starting_wl}_{ending_wl}_{wl_step}_{integration_time}_{current:.3f}.pickle")
  File "/usr/lib/python3/dist-packages/pandas/core/generic.py", line 2957, in to_pickle
    to_pickle(
  File "/usr/lib/python3/dist-packages/pandas/io/pickle.py", line 94, in to_pickle
    with get_handle(
  File "/usr/lib/python3/dist-packages/pandas/io/common.py", line 711, in get_handle
    handle = open(handle, ioargs.mode)
FileNotFoundError: [Errno 2] No such file or directory: '/mnt/data/2024-09-11/0.1618_0.5000/370_700_1_0.5_0.162.pickle'
```

Por suerte, estaban impresos los datos en la consola:

```python
{'wavelength': 370, 'counts': 157, 'integration_time': 0.00052}
{'wavelength': 371, 'counts': 152, 'integration_time': 0.00052}
{'wavelength': 372, 'counts': 182, 'integration_time': 0.00052}
{'wavelength': 373, 'counts': 215, 'integration_time': 0.00052}
{'wavelength': 374, 'counts': 271, 'integration_time': 0.00052}
{'wavelength': 375, 'counts': 503, 'integration_time': 0.00052}
{'wavelength': 376, 'counts': 1838, 'integration_time': 0.00052}
{'wavelength': 377, 'counts': 4091, 'integration_time': 0.00052}
{'wavelength': 378, 'counts': 7236, 'integration_time': 0.00052}
{'wavelength': 379, 'counts': 8072, 'integration_time': 0.00052}
{'wavelength': 380, 'counts': 7046, 'integration_time': 0.00052}
{'wavelength': 381, 'counts': 6633, 'integration_time': 0.00052}
{'wavelength': 382, 'counts': 7186, 'integration_time': 0.00052}
{'wavelength': 383, 'counts': 7623, 'integration_time': 0.00052}
{'wavelength': 384, 'counts': 6475, 'integration_time': 0.00052}
{'wavelength': 385, 'counts': 3581, 'integration_time': 0.00052}
{'wavelength': 386, 'counts': 1539, 'integration_time': 0.00052}
{'wavelength': 387, 'counts': 828, 'integration_time': 0.00052}
{'wavelength': 388, 'counts': 580, 'integration_time': 0.00052}
{'wavelength': 389, 'counts': 451, 'integration_time': 0.00052}
{'wavelength': 390, 'counts': 272, 'integration_time': 0.00052}
{'wavelength': 391, 'counts': 205, 'integration_time': 0.00052}
{'wavelength': 392, 'counts': 191, 'integration_time': 0.00052}
{'wavelength': 393, 'counts': 186, 'integration_time': 0.00052}
{'wavelength': 394, 'counts': 189, 'integration_time': 0.00052}
{'wavelength': 395, 'counts': 184, 'integration_time': 0.00052}
{'wavelength': 396, 'counts': 209, 'integration_time': 0.00052}
{'wavelength': 397, 'counts': 210, 'integration_time': 0.00052}
{'wavelength': 398, 'counts': 223, 'integration_time': 0.00052}
{'wavelength': 399, 'counts': 323, 'integration_time': 0.00052}
{'wavelength': 400, 'counts': 605, 'integration_time': 0.00052}
{'wavelength': 401, 'counts': 1076, 'integration_time': 0.00052}
{'wavelength': 402, 'counts': 1371, 'integration_time': 0.00052}
{'wavelength': 403, 'counts': 1749, 'integration_time': 0.00052}
{'wavelength': 404, 'counts': 3260, 'integration_time': 0.00052}
{'wavelength': 405, 'counts': 12631, 'integration_time': 0.00052}
{'wavelength': 406, 'counts': 25761, 'integration_time': 0.00052}
{'wavelength': 407, 'counts': 34964, 'integration_time': 0.00052}
{'wavelength': 408, 'counts': 38782, 'integration_time': 0.00052}
{'wavelength': 409, 'counts': 52790, 'integration_time': 0.00052}
{'wavelength': 410, 'counts': 51569, 'integration_time': 0.00052}
{'wavelength': 411, 'counts': 40224, 'integration_time': 0.00052}
{'wavelength': 412, 'counts': 40354, 'integration_time': 0.00052}
{'wavelength': 413, 'counts': 40825, 'integration_time': 0.00052}
{'wavelength': 414, 'counts': 34793, 'integration_time': 0.00052}
{'wavelength': 415, 'counts': 17337, 'integration_time': 0.00052}
{'wavelength': 416, 'counts': 10168, 'integration_time': 0.00052}
{'wavelength': 417, 'counts': 4584, 'integration_time': 0.00052}
{'wavelength': 418, 'counts': 2648, 'integration_time': 0.00052}
{'wavelength': 419, 'counts': 1686, 'integration_time': 0.00052}
{'wavelength': 420, 'counts': 1168, 'integration_time': 0.00052}
{'wavelength': 421, 'counts': 908, 'integration_time': 0.00052}
{'wavelength': 422, 'counts': 630, 'integration_time': 0.00052}
{'wavelength': 423, 'counts': 403, 'integration_time': 0.00052}
{'wavelength': 424, 'counts': 375, 'integration_time': 0.00052}
{'wavelength': 425, 'counts': 326, 'integration_time': 0.00052}
{'wavelength': 426, 'counts': 272, 'integration_time': 0.00052}
{'wavelength': 427, 'counts': 246, 'integration_time': 0.00052}
{'wavelength': 428, 'counts': 266, 'integration_time': 0.00052}
{'wavelength': 429, 'counts': 221, 'integration_time': 0.00052}
{'wavelength': 430, 'counts': 189, 'integration_time': 0.00052}
{'wavelength': 431, 'counts': 236, 'integration_time': 0.00052}
{'wavelength': 432, 'counts': 207, 'integration_time': 0.00052}
{'wavelength': 433, 'counts': 220, 'integration_time': 0.00052}
{'wavelength': 434, 'counts': 191, 'integration_time': 0.00052}
{'wavelength': 435, 'counts': 233, 'integration_time': 0.00052}
{'wavelength': 436, 'counts': 195, 'integration_time': 0.00052}
{'wavelength': 437, 'counts': 159, 'integration_time': 0.00052}
{'wavelength': 438, 'counts': 218, 'integration_time': 0.00052}
{'wavelength': 439, 'counts': 206, 'integration_time': 0.00052}
{'wavelength': 440, 'counts': 222, 'integration_time': 0.00052}
{'wavelength': 441, 'counts': 263, 'integration_time': 0.00052}
{'wavelength': 442, 'counts': 281, 'integration_time': 0.00052}
{'wavelength': 443, 'counts': 252, 'integration_time': 0.00052}
{'wavelength': 444, 'counts': 257, 'integration_time': 0.00052}
{'wavelength': 445, 'counts': 235, 'integration_time': 0.00052}
{'wavelength': 446, 'counts': 247, 'integration_time': 0.00052}
{'wavelength': 447, 'counts': 278, 'integration_time': 0.00052}
{'wavelength': 448, 'counts': 468, 'integration_time': 0.00052}
{'wavelength': 449, 'counts': 602, 'integration_time': 0.00052}
{'wavelength': 450, 'counts': 620, 'integration_time': 0.00052}
{'wavelength': 451, 'counts': 538, 'integration_time': 0.00052}
{'wavelength': 452, 'counts': 709, 'integration_time': 0.00052}
{'wavelength': 453, 'counts': 807, 'integration_time': 0.00052}
{'wavelength': 454, 'counts': 713, 'integration_time': 0.00052}
{'wavelength': 455, 'counts': 571, 'integration_time': 0.00052}
{'wavelength': 456, 'counts': 501, 'integration_time': 0.00052}
{'wavelength': 457, 'counts': 377, 'integration_time': 0.00052}
{'wavelength': 458, 'counts': 314, 'integration_time': 0.00052}
{'wavelength': 459, 'counts': 227, 'integration_time': 0.00052}
{'wavelength': 460, 'counts': 193, 'integration_time': 0.00052}
{'wavelength': 461, 'counts': 208, 'integration_time': 0.00052}
{'wavelength': 462, 'counts': 167, 'integration_time': 0.00052}
{'wavelength': 463, 'counts': 184, 'integration_time': 0.00052}
{'wavelength': 464, 'counts': 179, 'integration_time': 0.00052}
{'wavelength': 465, 'counts': 253, 'integration_time': 0.00052}
{'wavelength': 466, 'counts': 207, 'integration_time': 0.00052}
{'wavelength': 467, 'counts': 373, 'integration_time': 0.00052}
{'wavelength': 468, 'counts': 480, 'integration_time': 0.00052}
{'wavelength': 469, 'counts': 513, 'integration_time': 0.00052}
{'wavelength': 470, 'counts': 402, 'integration_time': 0.00052}
{'wavelength': 471, 'counts': 317, 'integration_time': 0.00052}
{'wavelength': 472, 'counts': 219, 'integration_time': 0.00052}
{'wavelength': 473, 'counts': 183, 'integration_time': 0.00052}
{'wavelength': 474, 'counts': 218, 'integration_time': 0.00052}
{'wavelength': 475, 'counts': 221, 'integration_time': 0.00052}
{'wavelength': 476, 'counts': 269, 'integration_time': 0.00052}
{'wavelength': 477, 'counts': 279, 'integration_time': 0.00052}
{'wavelength': 478, 'counts': 267, 'integration_time': 0.00052}
{'wavelength': 479, 'counts': 252, 'integration_time': 0.00052}
{'wavelength': 480, 'counts': 245, 'integration_time': 0.00052}
{'wavelength': 481, 'counts': 236, 'integration_time': 0.00052}
{'wavelength': 482, 'counts': 230, 'integration_time': 0.00052}
{'wavelength': 483, 'counts': 238, 'integration_time': 0.00052}
{'wavelength': 484, 'counts': 225, 'integration_time': 0.00052}
{'wavelength': 485, 'counts': 235, 'integration_time': 0.00052}
{'wavelength': 486, 'counts': 279, 'integration_time': 0.00052}
{'wavelength': 487, 'counts': 366, 'integration_time': 0.00052}
{'wavelength': 488, 'counts': 419, 'integration_time': 0.00052}
{'wavelength': 489, 'counts': 492, 'integration_time': 0.00052}
{'wavelength': 490, 'counts': 530, 'integration_time': 0.00052}
{'wavelength': 491, 'counts': 502, 'integration_time': 0.00052}
{'wavelength': 492, 'counts': 427, 'integration_time': 0.00052}
{'wavelength': 493, 'counts': 388, 'integration_time': 0.00052}
{'wavelength': 494, 'counts': 358, 'integration_time': 0.00052}
{'wavelength': 495, 'counts': 333, 'integration_time': 0.00052}
{'wavelength': 496, 'counts': 310, 'integration_time': 0.00052}
{'wavelength': 497, 'counts': 260, 'integration_time': 0.00052}
{'wavelength': 498, 'counts': 284, 'integration_time': 0.00052}
{'wavelength': 499, 'counts': 284, 'integration_time': 0.00052}
{'wavelength': 500, 'counts': 393, 'integration_time': 0.00052}
{'wavelength': 501, 'counts': 536, 'integration_time': 0.00052}
{'wavelength': 502, 'counts': 817, 'integration_time': 0.00052}
{'wavelength': 503, 'counts': 1296, 'integration_time': 0.00052}
{'wavelength': 504, 'counts': 1573, 'integration_time': 0.00052}
{'wavelength': 505, 'counts': 1340, 'integration_time': 0.00052}
{'wavelength': 506, 'counts': 901, 'integration_time': 0.00052}
{'wavelength': 507, 'counts': 738, 'integration_time': 0.00052}
{'wavelength': 508, 'counts': 670, 'integration_time': 0.00052}
{'wavelength': 509, 'counts': 606, 'integration_time': 0.00052}
{'wavelength': 510, 'counts': 706, 'integration_time': 0.00052}
{'wavelength': 511, 'counts': 957, 'integration_time': 0.00052}
{'wavelength': 512, 'counts': 1350, 'integration_time': 0.00052}
{'wavelength': 513, 'counts': 1929, 'integration_time': 0.00052}
{'wavelength': 514, 'counts': 2528, 'integration_time': 0.00052}
{'wavelength': 515, 'counts': 3368, 'integration_time': 0.00052}
{'wavelength': 516, 'counts': 4358, 'integration_time': 0.00052}
{'wavelength': 517, 'counts': 11029, 'integration_time': 0.00052}
{'wavelength': 518, 'counts': 36301, 'integration_time': 0.00052}
{'wavelength': 519, 'counts': 49266, 'integration_time': 0.00052}
{'wavelength': 520, 'counts': 55084, 'integration_time': 0.00052}
{'wavelength': 521, 'counts': 81685, 'integration_time': 0.00052}
{'wavelength': 522, 'counts': 105563, 'integration_time': 0.00052}
{'wavelength': 523, 'counts': 87090, 'integration_time': 0.00052}
{'wavelength': 524, 'counts': 74921, 'integration_time': 0.00052}
{'wavelength': 525, 'counts': 72207, 'integration_time': 0.00052}
{'wavelength': 526, 'counts': 67180, 'integration_time': 0.00052}
{'wavelength': 527, 'counts': 65547, 'integration_time': 0.00052}
{'wavelength': 528, 'counts': 74870, 'integration_time': 0.00052}
{'wavelength': 529, 'counts': 89570, 'integration_time': 0.00052}
{'wavelength': 530, 'counts': 91653, 'integration_time': 0.00052}
{'wavelength': 531, 'counts': 76933, 'integration_time': 0.00052}
{'wavelength': 532, 'counts': 52609, 'integration_time': 0.00052}
{'wavelength': 533, 'counts': 34638, 'integration_time': 0.00052}
{'wavelength': 534, 'counts': 25900, 'integration_time': 0.00052}
{'wavelength': 535, 'counts': 21719, 'integration_time': 0.00052}
{'wavelength': 536, 'counts': 23094, 'integration_time': 0.00052}
{'wavelength': 537, 'counts': 30152, 'integration_time': 0.00052}
{'wavelength': 538, 'counts': 54229, 'integration_time': 0.00052}
{'wavelength': 539, 'counts': 192659, 'integration_time': 0.00052}
{'wavelength': 540, 'counts': 336709, 'integration_time': 0.00052}
{'wavelength': 541, 'counts': 358594, 'integration_time': 0.00052}
{'wavelength': 542, 'counts': 326807, 'integration_time': 0.00052}
{'wavelength': 543, 'counts': 261724, 'integration_time': 0.00052}
{'wavelength': 544, 'counts': 196415, 'integration_time': 0.00052}
{'wavelength': 545, 'counts': 172698, 'integration_time': 0.00052}
{'wavelength': 546, 'counts': 190831, 'integration_time': 0.00052}
{'wavelength': 547, 'counts': 185925, 'integration_time': 0.00052}
{'wavelength': 548, 'counts': 159352, 'integration_time': 0.00052}
{'wavelength': 549, 'counts': 168677, 'integration_time': 0.00052}
{'wavelength': 550, 'counts': 188903, 'integration_time': 0.00052}
{'wavelength': 551, 'counts': 174667, 'integration_time': 0.00052}
{'wavelength': 552, 'counts': 123589, 'integration_time': 0.00052}
{'wavelength': 553, 'counts': 82120, 'integration_time': 0.00052}
{'wavelength': 554, 'counts': 63998, 'integration_time': 0.00052}
{'wavelength': 555, 'counts': 50469, 'integration_time': 0.00052}
{'wavelength': 556, 'counts': 48637, 'integration_time': 0.00052}
{'wavelength': 557, 'counts': 45549, 'integration_time': 0.00052}
{'wavelength': 558, 'counts': 31897, 'integration_time': 0.00052}
{'wavelength': 559, 'counts': 22031, 'integration_time': 0.00052}
{'wavelength': 560, 'counts': 14251, 'integration_time': 0.00052}
{'wavelength': 561, 'counts': 9152, 'integration_time': 0.00052}
{'wavelength': 562, 'counts': 6796, 'integration_time': 0.00052}
{'wavelength': 563, 'counts': 4825, 'integration_time': 0.00052}
{'wavelength': 564, 'counts': 3668, 'integration_time': 0.00052}
{'wavelength': 565, 'counts': 3054, 'integration_time': 0.00052}
{'wavelength': 566, 'counts': 2434, 'integration_time': 0.00052}
{'wavelength': 567, 'counts': 1704, 'integration_time': 0.00052}
{'wavelength': 568, 'counts': 1411, 'integration_time': 0.00052}
{'wavelength': 569, 'counts': 1089, 'integration_time': 0.00052}
{'wavelength': 570, 'counts': 905, 'integration_time': 0.00052}
{'wavelength': 571, 'counts': 643, 'integration_time': 0.00052}
{'wavelength': 572, 'counts': 529, 'integration_time': 0.00052}
{'wavelength': 573, 'counts': 470, 'integration_time': 0.00052}
{'wavelength': 574, 'counts': 363, 'integration_time': 0.00052}
{'wavelength': 575, 'counts': 380, 'integration_time': 0.00052}
{'wavelength': 576, 'counts': 285, 'integration_time': 0.00052}
{'wavelength': 577, 'counts': 308, 'integration_time': 0.00052}
{'wavelength': 578, 'counts': 265, 'integration_time': 0.00052}
{'wavelength': 579, 'counts': 261, 'integration_time': 0.00052}
{'wavelength': 580, 'counts': 257, 'integration_time': 0.00052}
{'wavelength': 581, 'counts': 231, 'integration_time': 0.00052}
{'wavelength': 582, 'counts': 216, 'integration_time': 0.00052}
{'wavelength': 583, 'counts': 271, 'integration_time': 0.00052}
{'wavelength': 584, 'counts': 233, 'integration_time': 0.00052}
{'wavelength': 585, 'counts': 261, 'integration_time': 0.00052}
{'wavelength': 586, 'counts': 266, 'integration_time': 0.00052}
{'wavelength': 587, 'counts': 236, 'integration_time': 0.00052}
{'wavelength': 588, 'counts': 202, 'integration_time': 0.00052}
{'wavelength': 589, 'counts': 201, 'integration_time': 0.00052}
{'wavelength': 590, 'counts': 177, 'integration_time': 0.00052}
{'wavelength': 591, 'counts': 203, 'integration_time': 0.00052}
{'wavelength': 592, 'counts': 177, 'integration_time': 0.00052}
{'wavelength': 593, 'counts': 204, 'integration_time': 0.00052}
{'wavelength': 594, 'counts': 193, 'integration_time': 0.00052}
{'wavelength': 595, 'counts': 207, 'integration_time': 0.00052}
{'wavelength': 596, 'counts': 207, 'integration_time': 0.00052}
{'wavelength': 597, 'counts': 199, 'integration_time': 0.00052}
{'wavelength': 598, 'counts': 190, 'integration_time': 0.00052}
{'wavelength': 599, 'counts': 205, 'integration_time': 0.00052}
{'wavelength': 600, 'counts': 189, 'integration_time': 0.00052}
{'wavelength': 601, 'counts': 179, 'integration_time': 0.00052}
{'wavelength': 602, 'counts': 216, 'integration_time': 0.00052}
{'wavelength': 603, 'counts': 246, 'integration_time': 0.00052}
{'wavelength': 604, 'counts': 264, 'integration_time': 0.00052}
{'wavelength': 605, 'counts': 277, 'integration_time': 0.00052}
{'wavelength': 606, 'counts': 203, 'integration_time': 0.00052}
{'wavelength': 607, 'counts': 210, 'integration_time': 0.00052}
{'wavelength': 608, 'counts': 211, 'integration_time': 0.00052}
{'wavelength': 609, 'counts': 251, 'integration_time': 0.00052}
{'wavelength': 610, 'counts': 261, 'integration_time': 0.00052}
{'wavelength': 611, 'counts': 208, 'integration_time': 0.00052}
{'wavelength': 612, 'counts': 265, 'integration_time': 0.00052}
{'wavelength': 613, 'counts': 284, 'integration_time': 0.00052}
{'wavelength': 614, 'counts': 258, 'integration_time': 0.00052}
{'wavelength': 615, 'counts': 209, 'integration_time': 0.00052}
{'wavelength': 616, 'counts': 235, 'integration_time': 0.00052}
{'wavelength': 617, 'counts': 245, 'integration_time': 0.00052}
{'wavelength': 618, 'counts': 221, 'integration_time': 0.00052}
{'wavelength': 619, 'counts': 293, 'integration_time': 0.00052}
{'wavelength': 620, 'counts': 247, 'integration_time': 0.00052}
{'wavelength': 621, 'counts': 206, 'integration_time': 0.00052}
{'wavelength': 622, 'counts': 199, 'integration_time': 0.00052}
{'wavelength': 623, 'counts': 224, 'integration_time': 0.00052}
{'wavelength': 624, 'counts': 251, 'integration_time': 0.00052}
{'wavelength': 625, 'counts': 269, 'integration_time': 0.00052}
{'wavelength': 626, 'counts': 257, 'integration_time': 0.00052}
{'wavelength': 627, 'counts': 267, 'integration_time': 0.00052}
{'wavelength': 628, 'counts': 211, 'integration_time': 0.00052}
{'wavelength': 629, 'counts': 231, 'integration_time': 0.00052}
{'wavelength': 630, 'counts': 231, 'integration_time': 0.00052}
{'wavelength': 631, 'counts': 268, 'integration_time': 0.00052}
{'wavelength': 632, 'counts': 272, 'integration_time': 0.00052}
{'wavelength': 633, 'counts': 342, 'integration_time': 0.00052}
{'wavelength': 634, 'counts': 405, 'integration_time': 0.00052}
{'wavelength': 635, 'counts': 518, 'integration_time': 0.00052}
{'wavelength': 636, 'counts': 666, 'integration_time': 0.00052}
{'wavelength': 637, 'counts': 893, 'integration_time': 0.00052}
{'wavelength': 638, 'counts': 1083, 'integration_time': 0.00052}
{'wavelength': 639, 'counts': 1449, 'integration_time': 0.00052}
{'wavelength': 640, 'counts': 1768, 'integration_time': 0.00052}
{'wavelength': 641, 'counts': 1944, 'integration_time': 0.00052}
{'wavelength': 642, 'counts': 2387, 'integration_time': 0.00052}
{'wavelength': 643, 'counts': 3013, 'integration_time': 0.00052}
{'wavelength': 644, 'counts': 3706, 'integration_time': 0.00052}
{'wavelength': 645, 'counts': 4936, 'integration_time': 0.00052}
{'wavelength': 646, 'counts': 7040, 'integration_time': 0.00052}
{'wavelength': 647, 'counts': 11328, 'integration_time': 0.00052}
{'wavelength': 648, 'counts': 19920, 'integration_time': 0.00052}
{'wavelength': 649, 'counts': 28879, 'integration_time': 0.00052}
{'wavelength': 650, 'counts': 42266, 'integration_time': 0.00052}
{'wavelength': 651, 'counts': 48046, 'integration_time': 0.00052}
{'wavelength': 652, 'counts': 52942, 'integration_time': 0.00052}
{'wavelength': 653, 'counts': 78368, 'integration_time': 0.00052}
{'wavelength': 654, 'counts': 107042, 'integration_time': 0.00052}
{'wavelength': 655, 'counts': 100869, 'integration_time': 0.00052}
{'wavelength': 656, 'counts': 80137, 'integration_time': 0.00052}
{'wavelength': 657, 'counts': 71946, 'integration_time': 0.00052}
{'wavelength': 658, 'counts': 73212, 'integration_time': 0.00052}
{'wavelength': 659, 'counts': 76266, 'integration_time': 0.00052}
{'wavelength': 660, 'counts': 75947, 'integration_time': 0.00052}
{'wavelength': 661, 'counts': 79408, 'integration_time': 0.00052}
{'wavelength': 662, 'counts': 78511, 'integration_time': 0.00052}
{'wavelength': 663, 'counts': 68991, 'integration_time': 0.00052}
{'wavelength': 664, 'counts': 63520, 'integration_time': 0.00052}
{'wavelength': 665, 'counts': 54151, 'integration_time': 0.00052}
{'wavelength': 666, 'counts': 47449, 'integration_time': 0.00052}
{'wavelength': 667, 'counts': 37171, 'integration_time': 0.00052}
{'wavelength': 668, 'counts': 31647, 'integration_time': 0.00052}
{'wavelength': 669, 'counts': 25659, 'integration_time': 0.00052}
{'wavelength': 670, 'counts': 21214, 'integration_time': 0.00052}
{'wavelength': 671, 'counts': 14465, 'integration_time': 0.00052}
{'wavelength': 672, 'counts': 9966, 'integration_time': 0.00052}
{'wavelength': 673, 'counts': 7330, 'integration_time': 0.00052}
{'wavelength': 674, 'counts': 5730, 'integration_time': 0.00052}
{'wavelength': 675, 'counts': 4740, 'integration_time': 0.00052}
{'wavelength': 676, 'counts': 3886, 'integration_time': 0.00052}
{'wavelength': 677, 'counts': 3091, 'integration_time': 0.00052}
{'wavelength': 678, 'counts': 2695, 'integration_time': 0.00052}
{'wavelength': 679, 'counts': 2173, 'integration_time': 0.00052}
{'wavelength': 680, 'counts': 1750, 'integration_time': 0.00052}
{'wavelength': 681, 'counts': 1411, 'integration_time': 0.00052}
{'wavelength': 682, 'counts': 1239, 'integration_time': 0.00052}
{'wavelength': 683, 'counts': 1018, 'integration_time': 0.00052}
{'wavelength': 684, 'counts': 872, 'integration_time': 0.00052}
{'wavelength': 685, 'counts': 608, 'integration_time': 0.00052}
{'wavelength': 686, 'counts': 595, 'integration_time': 0.00052}
{'wavelength': 687, 'counts': 486, 'integration_time': 0.00052}
{'wavelength': 688, 'counts': 513, 'integration_time': 0.00052}
{'wavelength': 689, 'counts': 635, 'integration_time': 0.00052}
{'wavelength': 690, 'counts': 663, 'integration_time': 0.00052}
{'wavelength': 691, 'counts': 669, 'integration_time': 0.00052}
{'wavelength': 692, 'counts': 642, 'integration_time': 0.00052}
{'wavelength': 693, 'counts': 654, 'integration_time': 0.00052}
{'wavelength': 694, 'counts': 566, 'integration_time': 0.00052}
{'wavelength': 695, 'counts': 458, 'integration_time': 0.00052}
{'wavelength': 696, 'counts': 380, 'integration_time': 0.00052}
{'wavelength': 697, 'counts': 479, 'integration_time': 0.00052}
{'wavelength': 698, 'counts': 1094, 'integration_time': 0.00052}
{'wavelength': 699, 'counts': 1198, 'integration_time': 0.00052}
```

Agrego a la carpeta spectrums_processed los espectros pero procesados.
Los espectros crudos que tomé tienen la cantidad de cuentas, pero no la cantidad de cuentas por segundo.
En esta carpeta, pongo los espectros con cuentas por segundo, y además corrijo desviaciones en la longitud de onda (para la medición de 0.2003 no se si por algún mal contacto del fin de carrera, la longitud de onda de home estaba en 1 nm menos que lo normal, entonces quedó todo el espectro corrido.).

Corto el espectro de 0.1453 A en 530. 
Hasta ese momento, el output fue:

```python
{'wavelength': 370, 'counts': 107, 'integration_time': 0.00052}
{'wavelength': 371, 'counts': 149, 'integration_time': 0.00052}
{'wavelength': 372, 'counts': 163, 'integration_time': 0.00052}
{'wavelength': 373, 'counts': 161, 'integration_time': 0.00052}
{'wavelength': 374, 'counts': 264, 'integration_time': 0.00052}
{'wavelength': 375, 'counts': 418, 'integration_time': 0.00052}
{'wavelength': 376, 'counts': 1129, 'integration_time': 0.00052}
{'wavelength': 377, 'counts': 3109, 'integration_time': 0.00052}
{'wavelength': 378, 'counts': 5060, 'integration_time': 0.00052}
{'wavelength': 379, 'counts': 5968, 'integration_time': 0.00052}
{'wavelength': 380, 'counts': 4933, 'integration_time': 0.00052}
{'wavelength': 381, 'counts': 4645, 'integration_time': 0.00052}
{'wavelength': 382, 'counts': 5145, 'integration_time': 0.00052}
{'wavelength': 383, 'counts': 5522, 'integration_time': 0.00052}
{'wavelength': 384, 'counts': 4821, 'integration_time': 0.00052}
{'wavelength': 385, 'counts': 2785, 'integration_time': 0.00052}
{'wavelength': 386, 'counts': 1148, 'integration_time': 0.00052}
{'wavelength': 387, 'counts': 687, 'integration_time': 0.00052}
{'wavelength': 388, 'counts': 505, 'integration_time': 0.00052}
{'wavelength': 389, 'counts': 319, 'integration_time': 0.00052}
{'wavelength': 390, 'counts': 266, 'integration_time': 0.00052}
{'wavelength': 391, 'counts': 245, 'integration_time': 0.00052}
{'wavelength': 392, 'counts': 193, 'integration_time': 0.00052}
{'wavelength': 393, 'counts': 160, 'integration_time': 0.00052}
{'wavelength': 394, 'counts': 183, 'integration_time': 0.00052}
{'wavelength': 395, 'counts': 178, 'integration_time': 0.00052}
{'wavelength': 396, 'counts': 180, 'integration_time': 0.00052}
{'wavelength': 397, 'counts': 327, 'integration_time': 0.00052}
{'wavelength': 398, 'counts': 229, 'integration_time': 0.00052}
{'wavelength': 399, 'counts': 273, 'integration_time': 0.00052}
{'wavelength': 400, 'counts': 431, 'integration_time': 0.00052}
{'wavelength': 401, 'counts': 849, 'integration_time': 0.00052}
{'wavelength': 402, 'counts': 1051, 'integration_time': 0.00052}
{'wavelength': 403, 'counts': 1226, 'integration_time': 0.00052}
{'wavelength': 404, 'counts': 2252, 'integration_time': 0.00052}
{'wavelength': 405, 'counts': 9103, 'integration_time': 0.00052}
{'wavelength': 406, 'counts': 18694, 'integration_time': 0.00052}
{'wavelength': 407, 'counts': 25204, 'integration_time': 0.00052}
{'wavelength': 408, 'counts': 27699, 'integration_time': 0.00052}
{'wavelength': 409, 'counts': 38400, 'integration_time': 0.00052}
{'wavelength': 410, 'counts': 38306, 'integration_time': 0.00052}
{'wavelength': 411, 'counts': 29175, 'integration_time': 0.00052}
{'wavelength': 412, 'counts': 29185, 'integration_time': 0.00052}
{'wavelength': 413, 'counts': 30367, 'integration_time': 0.00052}
{'wavelength': 414, 'counts': 23051, 'integration_time': 0.00052}
{'wavelength': 415, 'counts': 13100, 'integration_time': 0.00052}
{'wavelength': 416, 'counts': 7296, 'integration_time': 0.00052}
{'wavelength': 417, 'counts': 3256, 'integration_time': 0.00052}
{'wavelength': 418, 'counts': 1885, 'integration_time': 0.00052}
{'wavelength': 419, 'counts': 1321, 'integration_time': 0.00052}
{'wavelength': 420, 'counts': 935, 'integration_time': 0.00052}
{'wavelength': 421, 'counts': 622, 'integration_time': 0.00052}
{'wavelength': 422, 'counts': 472, 'integration_time': 0.00052}
{'wavelength': 423, 'counts': 307, 'integration_time': 0.00052}
{'wavelength': 424, 'counts': 248, 'integration_time': 0.00052}
{'wavelength': 425, 'counts': 217, 'integration_time': 0.00052}
{'wavelength': 426, 'counts': 196, 'integration_time': 0.00052}
{'wavelength': 427, 'counts': 192, 'integration_time': 0.00052}
{'wavelength': 428, 'counts': 197, 'integration_time': 0.00052}
{'wavelength': 429, 'counts': 202, 'integration_time': 0.00052}
{'wavelength': 430, 'counts': 176, 'integration_time': 0.00052}
{'wavelength': 431, 'counts': 163, 'integration_time': 0.00052}
{'wavelength': 432, 'counts': 197, 'integration_time': 0.00052}
{'wavelength': 433, 'counts': 160, 'integration_time': 0.00052}
{'wavelength': 434, 'counts': 154, 'integration_time': 0.00052}
{'wavelength': 435, 'counts': 170, 'integration_time': 0.00052}
{'wavelength': 436, 'counts': 140, 'integration_time': 0.00052}
{'wavelength': 437, 'counts': 156, 'integration_time': 0.00052}
{'wavelength': 438, 'counts': 180, 'integration_time': 0.00052}
{'wavelength': 439, 'counts': 214, 'integration_time': 0.00052}
{'wavelength': 440, 'counts': 153, 'integration_time': 0.00052}
{'wavelength': 441, 'counts': 192, 'integration_time': 0.00052}
{'wavelength': 442, 'counts': 232, 'integration_time': 0.00052}
{'wavelength': 443, 'counts': 217, 'integration_time': 0.00052}
{'wavelength': 444, 'counts': 227, 'integration_time': 0.00052}
{'wavelength': 445, 'counts': 250, 'integration_time': 0.00052}
{'wavelength': 446, 'counts': 257, 'integration_time': 0.00052}
{'wavelength': 447, 'counts': 265, 'integration_time': 0.00052}
{'wavelength': 448, 'counts': 362, 'integration_time': 0.00052}
{'wavelength': 449, 'counts': 440, 'integration_time': 0.00052}
{'wavelength': 450, 'counts': 470, 'integration_time': 0.00052}
{'wavelength': 451, 'counts': 439, 'integration_time': 0.00052}
{'wavelength': 452, 'counts': 541, 'integration_time': 0.00052}
{'wavelength': 453, 'counts': 573, 'integration_time': 0.00052}
{'wavelength': 454, 'counts': 489, 'integration_time': 0.00052}
{'wavelength': 455, 'counts': 400, 'integration_time': 0.00052}
{'wavelength': 456, 'counts': 364, 'integration_time': 0.00052}
{'wavelength': 457, 'counts': 312, 'integration_time': 0.00052}
{'wavelength': 458, 'counts': 225, 'integration_time': 0.00052}
{'wavelength': 459, 'counts': 194, 'integration_time': 0.00052}
{'wavelength': 460, 'counts': 195, 'integration_time': 0.00052}
{'wavelength': 461, 'counts': 224, 'integration_time': 0.00052}
{'wavelength': 462, 'counts': 232, 'integration_time': 0.00052}
{'wavelength': 463, 'counts': 241, 'integration_time': 0.00052}
{'wavelength': 464, 'counts': 186, 'integration_time': 0.00052}
{'wavelength': 465, 'counts': 185, 'integration_time': 0.00052}
{'wavelength': 466, 'counts': 190, 'integration_time': 0.00052}
{'wavelength': 467, 'counts': 302, 'integration_time': 0.00052}
{'wavelength': 468, 'counts': 364, 'integration_time': 0.00052}
{'wavelength': 469, 'counts': 449, 'integration_time': 0.00052}
{'wavelength': 470, 'counts': 345, 'integration_time': 0.00052}
{'wavelength': 471, 'counts': 267, 'integration_time': 0.00052}
{'wavelength': 472, 'counts': 211, 'integration_time': 0.00052}
{'wavelength': 473, 'counts': 191, 'integration_time': 0.00052}
{'wavelength': 474, 'counts': 170, 'integration_time': 0.00052}
{'wavelength': 475, 'counts': 171, 'integration_time': 0.00052}
{'wavelength': 476, 'counts': 152, 'integration_time': 0.00052}
{'wavelength': 477, 'counts': 166, 'integration_time': 0.00052}
{'wavelength': 478, 'counts': 185, 'integration_time': 0.00052}
{'wavelength': 479, 'counts': 164, 'integration_time': 0.00052}
{'wavelength': 480, 'counts': 188, 'integration_time': 0.00052}
{'wavelength': 481, 'counts': 183, 'integration_time': 0.00052}
{'wavelength': 482, 'counts': 189, 'integration_time': 0.00052}
{'wavelength': 483, 'counts': 192, 'integration_time': 0.00052}
{'wavelength': 484, 'counts': 204, 'integration_time': 0.00052}
{'wavelength': 485, 'counts': 229, 'integration_time': 0.00052}
{'wavelength': 486, 'counts': 245, 'integration_time': 0.00052}
{'wavelength': 487, 'counts': 252, 'integration_time': 0.00052}
{'wavelength': 488, 'counts': 310, 'integration_time': 0.00052}
{'wavelength': 489, 'counts': 309, 'integration_time': 0.00052}
{'wavelength': 490, 'counts': 385, 'integration_time': 0.00052}
{'wavelength': 491, 'counts': 326, 'integration_time': 0.00052}
{'wavelength': 492, 'counts': 326, 'integration_time': 0.00052}
{'wavelength': 493, 'counts': 292, 'integration_time': 0.00052}
{'wavelength': 494, 'counts': 283, 'integration_time': 0.00052}
{'wavelength': 495, 'counts': 280, 'integration_time': 0.00052}
{'wavelength': 496, 'counts': 246, 'integration_time': 0.00052}
{'wavelength': 497, 'counts': 218, 'integration_time': 0.00052}
{'wavelength': 498, 'counts': 190, 'integration_time': 0.00052}
{'wavelength': 499, 'counts': 193, 'integration_time': 0.00052}
{'wavelength': 500, 'counts': 253, 'integration_time': 0.00052}
{'wavelength': 501, 'counts': 358, 'integration_time': 0.00052}
{'wavelength': 502, 'counts': 558, 'integration_time': 0.00052}
{'wavelength': 503, 'counts': 906, 'integration_time': 0.00052}
{'wavelength': 504, 'counts': 1135, 'integration_time': 0.00052}
{'wavelength': 505, 'counts': 962, 'integration_time': 0.00052}
{'wavelength': 506, 'counts': 681, 'integration_time': 0.00052}
{'wavelength': 507, 'counts': 490, 'integration_time': 0.00052}
{'wavelength': 508, 'counts': 470, 'integration_time': 0.00052}
{'wavelength': 509, 'counts': 481, 'integration_time': 0.00052}
{'wavelength': 510, 'counts': 583, 'integration_time': 0.00052}
{'wavelength': 511, 'counts': 724, 'integration_time': 0.00052}
{'wavelength': 512, 'counts': 1035, 'integration_time': 0.00052}
{'wavelength': 513, 'counts': 1484, 'integration_time': 0.00052}
{'wavelength': 514, 'counts': 1806, 'integration_time': 0.00052}
{'wavelength': 515, 'counts': 2502, 'integration_time': 0.00052}
{'wavelength': 516, 'counts': 3709, 'integration_time': 0.00052}
{'wavelength': 517, 'counts': 10190, 'integration_time': 0.00052}
{'wavelength': 518, 'counts': 24462, 'integration_time': 0.00052}
{'wavelength': 519, 'counts': 38135, 'integration_time': 0.00052}
{'wavelength': 520, 'counts': 43270, 'integration_time': 0.00052}
{'wavelength': 521, 'counts': 62031, 'integration_time': 0.00052}
{'wavelength': 522, 'counts': 82064, 'integration_time': 0.00052}
{'wavelength': 523, 'counts': 68769, 'integration_time': 0.00052}
{'wavelength': 524, 'counts': 58584, 'integration_time': 0.00052}
{'wavelength': 525, 'counts': 55826, 'integration_time': 0.00052}
{'wavelength': 526, 'counts': 51686, 'integration_time': 0.00052}
{'wavelength': 527, 'counts': 50888, 'integration_time': 0.00052}
{'wavelength': 528, 'counts': 58919, 'integration_time': 0.00052}
{'wavelength': 529, 'counts': 70196, 'integration_time': 0.00052}
{'wavelength': 530, 'counts': 71522, 'integration_time': 0.00052}
```

# 2024-09-12

Retomo la medición de ayer, para 0.14 A desde 531 nm.
Sonó una alarma, me cagué en las patas y apagué todo, pero era de otro lado y la gente ni se inmutó así que retomo. Hasta ese momento tomé los datos:

```python
{'wavelength': 531, 'counts': 52211, 'integration_time': 0.00052}
{'wavelength': 532, 'counts': 35735, 'integration_time': 0.00052}
{'wavelength': 533, 'counts': 24316, 'integration_time': 0.00052}
{'wavelength': 534, 'counts': 17621, 'integration_time': 0.00052}
{'wavelength': 535, 'counts': 14797, 'integration_time': 0.00052}
{'wavelength': 536, 'counts': 16061, 'integration_time': 0.00052}
{'wavelength': 537, 'counts': 20749, 'integration_time': 0.00052}
{'wavelength': 538, 'counts': 38765, 'integration_time': 0.00052}
{'wavelength': 539, 'counts': 142548, 'integration_time': 0.00052}
{'wavelength': 540, 'counts': 252423, 'integration_time': 0.00052}
{'wavelength': 541, 'counts': 267082, 'integration_time': 0.00052}
{'wavelength': 542, 'counts': 242747, 'integration_time': 0.00052}
{'wavelength': 543, 'counts': 194085, 'integration_time': 0.00052}
{'wavelength': 544, 'counts': 143289, 'integration_time': 0.00052}
{'wavelength': 545, 'counts': 124625, 'integration_time': 0.00052}
{'wavelength': 546, 'counts': 141593, 'integration_time': 0.00052}
{'wavelength': 547, 'counts': 135147, 'integration_time': 0.00052}
{'wavelength': 548, 'counts': 114682, 'integration_time': 0.00052}
{'wavelength': 549, 'counts': 122892, 'integration_time': 0.00052}
{'wavelength': 550, 'counts': 138892, 'integration_time': 0.00052}
{'wavelength': 551, 'counts': 122521, 'integration_time': 0.00052}
{'wavelength': 552, 'counts': 85627, 'integration_time': 0.00052}
{'wavelength': 553, 'counts': 58832, 'integration_time': 0.00052}
{'wavelength': 554, 'counts': 43550, 'integration_time': 0.00052}
{'wavelength': 555, 'counts': 35403, 'integration_time': 0.00052}
{'wavelength': 556, 'counts': 33447, 'integration_time': 0.00052}
{'wavelength': 557, 'counts': 30280, 'integration_time': 0.00052}
{'wavelength': 558, 'counts': 21804, 'integration_time': 0.00052}
{'wavelength': 559, 'counts': 14178, 'integration_time': 0.00052}
{'wavelength': 560, 'counts': 8986, 'integration_time': 0.00052}
{'wavelength': 561, 'counts': 6311, 'integration_time': 0.00052}
{'wavelength': 562, 'counts': 4363, 'integration_time': 0.00052}
{'wavelength': 563, 'counts': 3447, 'integration_time': 0.00052}
{'wavelength': 564, 'counts': 2742, 'integration_time': 0.00052}
{'wavelength': 565, 'counts': 2201, 'integration_time': 0.00052}
{'wavelength': 566, 'counts': 1657, 'integration_time': 0.00052}
{'wavelength': 567, 'counts': 1329, 'integration_time': 0.00052}
{'wavelength': 568, 'counts': 1052, 'integration_time': 0.00052}
{'wavelength': 569, 'counts': 813, 'integration_time': 0.00052}
{'wavelength': 570, 'counts': 612, 'integration_time': 0.00052}
{'wavelength': 571, 'counts': 522, 'integration_time': 0.00052}
{'wavelength': 572, 'counts': 487, 'integration_time': 0.00052}
{'wavelength': 573, 'counts': 369, 'integration_time': 0.00052}
{'wavelength': 574, 'counts': 354, 'integration_time': 0.00052}
{'wavelength': 575, 'counts': 280, 'integration_time': 0.00052}
{'wavelength': 576, 'counts': 268, 'integration_time': 0.00052}
{'wavelength': 577, 'counts': 268, 'integration_time': 0.00052}
{'wavelength': 578, 'counts': 250, 'integration_time': 0.00052}
{'wavelength': 579, 'counts': 283, 'integration_time': 0.00052}
{'wavelength': 580, 'counts': 259, 'integration_time': 0.00052}
{'wavelength': 581, 'counts': 238, 'integration_time': 0.00052}
{'wavelength': 582, 'counts': 199, 'integration_time': 0.00052}
{'wavelength': 583, 'counts': 211, 'integration_time': 0.00052}
{'wavelength': 584, 'counts': 217, 'integration_time': 0.00052}
{'wavelength': 585, 'counts': 195, 'integration_time': 0.00052}
{'wavelength': 586, 'counts': 182, 'integration_time': 0.00052}
{'wavelength': 587, 'counts': 172, 'integration_time': 0.00052}
{'wavelength': 588, 'counts': 81, 'integration_time': 0.00052}
```

Los puntos que quedan son:

```python
{'wavelength': 589, 'counts': 200, 'integration_time': 0.00052}
{'wavelength': 590, 'counts': 177, 'integration_time': 0.00052}
{'wavelength': 591, 'counts': 172, 'integration_time': 0.00052}
{'wavelength': 592, 'counts': 159, 'integration_time': 0.00052}
{'wavelength': 593, 'counts': 206, 'integration_time': 0.00052}
{'wavelength': 594, 'counts': 180, 'integration_time': 0.00052}
{'wavelength': 595, 'counts': 178, 'integration_time': 0.00052}
{'wavelength': 596, 'counts': 203, 'integration_time': 0.00052}
{'wavelength': 597, 'counts': 220, 'integration_time': 0.00052}
{'wavelength': 598, 'counts': 188, 'integration_time': 0.00052}
{'wavelength': 599, 'counts': 184, 'integration_time': 0.00052}
{'wavelength': 600, 'counts': 178, 'integration_time': 0.00052}
{'wavelength': 601, 'counts': 220, 'integration_time': 0.00052}
{'wavelength': 602, 'counts': 181, 'integration_time': 0.00052}
{'wavelength': 603, 'counts': 172, 'integration_time': 0.00052}
{'wavelength': 604, 'counts': 201, 'integration_time': 0.00052}
{'wavelength': 605, 'counts': 190, 'integration_time': 0.00052}
{'wavelength': 606, 'counts': 162, 'integration_time': 0.00052}
{'wavelength': 607, 'counts': 192, 'integration_time': 0.00052}
{'wavelength': 608, 'counts': 145, 'integration_time': 0.00052}
{'wavelength': 609, 'counts': 159, 'integration_time': 0.00052}
{'wavelength': 610, 'counts': 190, 'integration_time': 0.00052}
{'wavelength': 611, 'counts': 178, 'integration_time': 0.00052}
{'wavelength': 612, 'counts': 168, 'integration_time': 0.00052}
{'wavelength': 613, 'counts': 142, 'integration_time': 0.00052}
{'wavelength': 614, 'counts': 168, 'integration_time': 0.00052}
{'wavelength': 615, 'counts': 190, 'integration_time': 0.00052}
{'wavelength': 616, 'counts': 166, 'integration_time': 0.00052}
{'wavelength': 617, 'counts': 172, 'integration_time': 0.00052}
{'wavelength': 618, 'counts': 205, 'integration_time': 0.00052}
{'wavelength': 619, 'counts': 181, 'integration_time': 0.00052}
{'wavelength': 620, 'counts': 176, 'integration_time': 0.00052}
{'wavelength': 621, 'counts': 138, 'integration_time': 0.00052}
{'wavelength': 622, 'counts': 191, 'integration_time': 0.00052}
{'wavelength': 623, 'counts': 138, 'integration_time': 0.00052}
{'wavelength': 624, 'counts': 162, 'integration_time': 0.00052}
{'wavelength': 625, 'counts': 148, 'integration_time': 0.00052}
{'wavelength': 626, 'counts': 187, 'integration_time': 0.00052}
{'wavelength': 627, 'counts': 189, 'integration_time': 0.00052}
{'wavelength': 628, 'counts': 181, 'integration_time': 0.00052}
{'wavelength': 629, 'counts': 196, 'integration_time': 0.00052}
{'wavelength': 630, 'counts': 207, 'integration_time': 0.00052}
{'wavelength': 631, 'counts': 203, 'integration_time': 0.00052}
{'wavelength': 632, 'counts': 231, 'integration_time': 0.00052}
{'wavelength': 633, 'counts': 269, 'integration_time': 0.00052}
{'wavelength': 634, 'counts': 280, 'integration_time': 0.00052}
{'wavelength': 635, 'counts': 312, 'integration_time': 0.00052}
{'wavelength': 636, 'counts': 465, 'integration_time': 0.00052}
{'wavelength': 637, 'counts': 611, 'integration_time': 0.00052}
{'wavelength': 638, 'counts': 789, 'integration_time': 0.00052}
{'wavelength': 639, 'counts': 992, 'integration_time': 0.00052}
{'wavelength': 640, 'counts': 1202, 'integration_time': 0.00052}
{'wavelength': 641, 'counts': 1447, 'integration_time': 0.00052}
{'wavelength': 642, 'counts': 1685, 'integration_time': 0.00052}
{'wavelength': 643, 'counts': 2036, 'integration_time': 0.00052}
{'wavelength': 644, 'counts': 2545, 'integration_time': 0.00052}
{'wavelength': 645, 'counts': 3298, 'integration_time': 0.00052}
{'wavelength': 646, 'counts': 4840, 'integration_time': 0.00052}
{'wavelength': 647, 'counts': 8089, 'integration_time': 0.00052}
{'wavelength': 648, 'counts': 13853, 'integration_time': 0.00052}
{'wavelength': 649, 'counts': 19865, 'integration_time': 0.00052}
{'wavelength': 650, 'counts': 29356, 'integration_time': 0.00052}
{'wavelength': 651, 'counts': 33159, 'integration_time': 0.00052}
{'wavelength': 652, 'counts': 36789, 'integration_time': 0.00052}
{'wavelength': 653, 'counts': 57982, 'integration_time': 0.00052}
{'wavelength': 654, 'counts': 75309, 'integration_time': 0.00052}
{'wavelength': 655, 'counts': 68643, 'integration_time': 0.00052}
{'wavelength': 656, 'counts': 56836, 'integration_time': 0.00052}
{'wavelength': 657, 'counts': 49541, 'integration_time': 0.00052}
{'wavelength': 658, 'counts': 50775, 'integration_time': 0.00052}
{'wavelength': 659, 'counts': 53087, 'integration_time': 0.00052}
{'wavelength': 660, 'counts': 53160, 'integration_time': 0.00052}
{'wavelength': 661, 'counts': 55949, 'integration_time': 0.00052}
{'wavelength': 662, 'counts': 53976, 'integration_time': 0.00052}
{'wavelength': 663, 'counts': 48348, 'integration_time': 0.00052}
{'wavelength': 664, 'counts': 43559, 'integration_time': 0.00052}
{'wavelength': 665, 'counts': 37665, 'integration_time': 0.00052}
{'wavelength': 666, 'counts': 32535, 'integration_time': 0.00052}
{'wavelength': 667, 'counts': 25594, 'integration_time': 0.00052}
{'wavelength': 668, 'counts': 21531, 'integration_time': 0.00052}
{'wavelength': 669, 'counts': 18329, 'integration_time': 0.00052}
{'wavelength': 670, 'counts': 13676, 'integration_time': 0.00052}
{'wavelength': 671, 'counts': 9276, 'integration_time': 0.00052}
{'wavelength': 672, 'counts': 6760, 'integration_time': 0.00052}
{'wavelength': 673, 'counts': 4814, 'integration_time': 0.00052}
{'wavelength': 674, 'counts': 3813, 'integration_time': 0.00052}
{'wavelength': 675, 'counts': 3177, 'integration_time': 0.00052}
{'wavelength': 676, 'counts': 2585, 'integration_time': 0.00052}
{'wavelength': 677, 'counts': 2128, 'integration_time': 0.00052}
{'wavelength': 678, 'counts': 1765, 'integration_time': 0.00052}
{'wavelength': 679, 'counts': 1506, 'integration_time': 0.00052}
{'wavelength': 680, 'counts': 1282, 'integration_time': 0.00052}
{'wavelength': 681, 'counts': 995, 'integration_time': 0.00052}
{'wavelength': 682, 'counts': 900, 'integration_time': 0.00052}
{'wavelength': 683, 'counts': 734, 'integration_time': 0.00052}
{'wavelength': 684, 'counts': 575, 'integration_time': 0.00052}
{'wavelength': 685, 'counts': 499, 'integration_time': 0.00052}
{'wavelength': 686, 'counts': 471, 'integration_time': 0.00052}
{'wavelength': 687, 'counts': 391, 'integration_time': 0.00052}
{'wavelength': 688, 'counts': 420, 'integration_time': 0.00052}
{'wavelength': 689, 'counts': 497, 'integration_time': 0.00052}
{'wavelength': 690, 'counts': 485, 'integration_time': 0.00052}
{'wavelength': 691, 'counts': 471, 'integration_time': 0.00052}
{'wavelength': 692, 'counts': 444, 'integration_time': 0.00052}
{'wavelength': 693, 'counts': 488, 'integration_time': 0.00052}
{'wavelength': 694, 'counts': 478, 'integration_time': 0.00052}
{'wavelength': 695, 'counts': 351, 'integration_time': 0.00052}
{'wavelength': 696, 'counts': 285, 'integration_time': 0.00052}
{'wavelength': 697, 'counts': 438, 'integration_time': 0.00052}
{'wavelength': 698, 'counts': 680, 'integration_time': 0.00052}
{'wavelength': 699, 'counts': 849, 'integration_time': 0.00052}
```

Ahora mido espectros con menos potencia, y también bajo el tiempo de integración para que se hagan rápido.
Mido 0.0618 A con tiempo de integración 0.1.
Está corrido en 1nm.

Datos:

```python
{'wavelength': 370, 'counts': 33, 'integration_time': 0.00052}
{'wavelength': 371, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 372, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 373, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 374, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 375, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 376, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 377, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 378, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 379, 'counts': 40, 'integration_time': 0.00052}
{'wavelength': 380, 'counts': 39, 'integration_time': 0.00052}
{'wavelength': 381, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 382, 'counts': 33, 'integration_time': 0.00052}
{'wavelength': 383, 'counts': 41, 'integration_time': 0.00052}
{'wavelength': 384, 'counts': 34, 'integration_time': 0.00052}
{'wavelength': 385, 'counts': 11, 'integration_time': 0.00052}
{'wavelength': 386, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 387, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 388, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 389, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 390, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 391, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 392, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 393, 'counts': 13, 'integration_time': 0.00052}
{'wavelength': 394, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 395, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 396, 'counts': 42, 'integration_time': 0.00052}
{'wavelength': 397, 'counts': 35, 'integration_time': 0.00052}
{'wavelength': 398, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 399, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 400, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 401, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 402, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 403, 'counts': 11, 'integration_time': 0.00052}
{'wavelength': 404, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 405, 'counts': 31, 'integration_time': 0.00052}
{'wavelength': 406, 'counts': 54, 'integration_time': 0.00052}
{'wavelength': 407, 'counts': 74, 'integration_time': 0.00052}
{'wavelength': 408, 'counts': 64, 'integration_time': 0.00052}
{'wavelength': 409, 'counts': 96, 'integration_time': 0.00052}
{'wavelength': 410, 'counts': 122, 'integration_time': 0.00052}
{'wavelength': 411, 'counts': 57, 'integration_time': 0.00052}
{'wavelength': 412, 'counts': 74, 'integration_time': 0.00052}
{'wavelength': 413, 'counts': 82, 'integration_time': 0.00052}
{'wavelength': 414, 'counts': 59, 'integration_time': 0.00052}
{'wavelength': 415, 'counts': 47, 'integration_time': 0.00052}
{'wavelength': 416, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 417, 'counts': 33, 'integration_time': 0.00052}
{'wavelength': 418, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 419, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 420, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 421, 'counts': 33, 'integration_time': 0.00052}
{'wavelength': 422, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 423, 'counts': 39, 'integration_time': 0.00052}
{'wavelength': 424, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 425, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 426, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 427, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 428, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 429, 'counts': 15, 'integration_time': 0.00052}
{'wavelength': 430, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 431, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 432, 'counts': 41, 'integration_time': 0.00052}
{'wavelength': 433, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 434, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 435, 'counts': 31, 'integration_time': 0.00052}
{'wavelength': 436, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 437, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 438, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 439, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 440, 'counts': 35, 'integration_time': 0.00052}
{'wavelength': 441, 'counts': 34, 'integration_time': 0.00052}
{'wavelength': 442, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 443, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 444, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 445, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 446, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 447, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 448, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 449, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 450, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 451, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 452, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 453, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 454, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 455, 'counts': 14, 'integration_time': 0.00052}
{'wavelength': 456, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 457, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 458, 'counts': 36, 'integration_time': 0.00052}
{'wavelength': 459, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 460, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 461, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 462, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 463, 'counts': 34, 'integration_time': 0.00052}
{'wavelength': 464, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 465, 'counts': 15, 'integration_time': 0.00052}
{'wavelength': 466, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 467, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 468, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 469, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 470, 'counts': 34, 'integration_time': 0.00052}
{'wavelength': 471, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 472, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 473, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 474, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 475, 'counts': 34, 'integration_time': 0.00052}
{'wavelength': 476, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 477, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 478, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 479, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 480, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 481, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 482, 'counts': 35, 'integration_time': 0.00052}
{'wavelength': 483, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 484, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 485, 'counts': 13, 'integration_time': 0.00052}
{'wavelength': 486, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 487, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 488, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 489, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 490, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 491, 'counts': 38, 'integration_time': 0.00052}
{'wavelength': 492, 'counts': 34, 'integration_time': 0.00052}
{'wavelength': 493, 'counts': 15, 'integration_time': 0.00052}
{'wavelength': 494, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 495, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 496, 'counts': 31, 'integration_time': 0.00052}
{'wavelength': 497, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 498, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 499, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 500, 'counts': 15, 'integration_time': 0.00052}
{'wavelength': 501, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 502, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 503, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 504, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 505, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 506, 'counts': 31, 'integration_time': 0.00052}
{'wavelength': 507, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 508, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 509, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 510, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 511, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 512, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 513, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 514, 'counts': 31, 'integration_time': 0.00052}
{'wavelength': 515, 'counts': 45, 'integration_time': 0.00052}
{'wavelength': 516, 'counts': 45, 'integration_time': 0.00052}
{'wavelength': 517, 'counts': 82, 'integration_time': 0.00052}
{'wavelength': 518, 'counts': 175, 'integration_time': 0.00052}
{'wavelength': 519, 'counts': 277, 'integration_time': 0.00052}
{'wavelength': 520, 'counts': 282, 'integration_time': 0.00052}
{'wavelength': 521, 'counts': 407, 'integration_time': 0.00052}
{'wavelength': 522, 'counts': 550, 'integration_time': 0.00052}
{'wavelength': 523, 'counts': 436, 'integration_time': 0.00052}
{'wavelength': 524, 'counts': 371, 'integration_time': 0.00052}
{'wavelength': 525, 'counts': 394, 'integration_time': 0.00052}
{'wavelength': 526, 'counts': 416, 'integration_time': 0.00052}
{'wavelength': 527, 'counts': 420, 'integration_time': 0.00052}
{'wavelength': 528, 'counts': 431, 'integration_time': 0.00052}
{'wavelength': 529, 'counts': 501, 'integration_time': 0.00052}
{'wavelength': 530, 'counts': 512, 'integration_time': 0.00052}
{'wavelength': 531, 'counts': 427, 'integration_time': 0.00052}
{'wavelength': 532, 'counts': 294, 'integration_time': 0.00052}
{'wavelength': 533, 'counts': 211, 'integration_time': 0.00052}
{'wavelength': 534, 'counts': 168, 'integration_time': 0.00052}
{'wavelength': 535, 'counts': 118, 'integration_time': 0.00052}
{'wavelength': 536, 'counts': 121, 'integration_time': 0.00052}
{'wavelength': 537, 'counts': 165, 'integration_time': 0.00052}
{'wavelength': 538, 'counts': 359, 'integration_time': 0.00052}
{'wavelength': 539, 'counts': 1225, 'integration_time': 0.00052}
{'wavelength': 540, 'counts': 2245, 'integration_time': 0.00052}
{'wavelength': 541, 'counts': 2388, 'integration_time': 0.00052}
{'wavelength': 542, 'counts': 2147, 'integration_time': 0.00052}
{'wavelength': 543, 'counts': 1756, 'integration_time': 0.00052}
{'wavelength': 544, 'counts': 1105, 'integration_time': 0.00052}
{'wavelength': 545, 'counts': 1011, 'integration_time': 0.00052}
{'wavelength': 546, 'counts': 1209, 'integration_time': 0.00052}
{'wavelength': 547, 'counts': 1169, 'integration_time': 0.00052}
{'wavelength': 548, 'counts': 914, 'integration_time': 0.00052}
{'wavelength': 549, 'counts': 1045, 'integration_time': 0.00052}
{'wavelength': 550, 'counts': 1137, 'integration_time': 0.00052}
{'wavelength': 551, 'counts': 981, 'integration_time': 0.00052}
{'wavelength': 552, 'counts': 653, 'integration_time': 0.00052}
{'wavelength': 553, 'counts': 432, 'integration_time': 0.00052}
{'wavelength': 554, 'counts': 282, 'integration_time': 0.00052}
{'wavelength': 555, 'counts': 206, 'integration_time': 0.00052}
{'wavelength': 556, 'counts': 139, 'integration_time': 0.00052}
{'wavelength': 557, 'counts': 138, 'integration_time': 0.00052}
{'wavelength': 558, 'counts': 109, 'integration_time': 0.00052}
{'wavelength': 559, 'counts': 89, 'integration_time': 0.00052}
{'wavelength': 560, 'counts': 73, 'integration_time': 0.00052}
{'wavelength': 561, 'counts': 53, 'integration_time': 0.00052}
{'wavelength': 562, 'counts': 43, 'integration_time': 0.00052}
{'wavelength': 563, 'counts': 43, 'integration_time': 0.00052}
{'wavelength': 564, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 565, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 566, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 567, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 568, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 569, 'counts': 35, 'integration_time': 0.00052}
{'wavelength': 570, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 571, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 572, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 573, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 574, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 575, 'counts': 14, 'integration_time': 0.00052}
{'wavelength': 576, 'counts': 8, 'integration_time': 0.00052}
{'wavelength': 577, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 578, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 579, 'counts': 13, 'integration_time': 0.00052}
{'wavelength': 580, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 581, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 582, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 583, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 584, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 585, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 586, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 587, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 588, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 589, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 590, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 591, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 592, 'counts': 13, 'integration_time': 0.00052}
{'wavelength': 593, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 594, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 595, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 596, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 597, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 598, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 599, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 600, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 601, 'counts': 10, 'integration_time': 0.00052}
{'wavelength': 602, 'counts': 15, 'integration_time': 0.00052}
{'wavelength': 603, 'counts': 10, 'integration_time': 0.00052}
{'wavelength': 604, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 605, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 606, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 607, 'counts': 11, 'integration_time': 0.00052}
{'wavelength': 608, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 609, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 610, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 611, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 612, 'counts': 11, 'integration_time': 0.00052}
{'wavelength': 613, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 614, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 615, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 616, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 617, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 618, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 619, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 620, 'counts': 11, 'integration_time': 0.00052}
{'wavelength': 621, 'counts': 14, 'integration_time': 0.00052}
{'wavelength': 622, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 623, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 624, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 625, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 626, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 627, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 628, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 629, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 630, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 631, 'counts': 24, 'integration_time': 0.00052}
{'wavelength': 632, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 633, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 634, 'counts': 17, 'integration_time': 0.00052}
{'wavelength': 635, 'counts': 10, 'integration_time': 0.00052}
{'wavelength': 636, 'counts': 9, 'integration_time': 0.00052}
{'wavelength': 637, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 638, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 639, 'counts': 32, 'integration_time': 0.00052}
{'wavelength': 640, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 641, 'counts': 19, 'integration_time': 0.00052}
{'wavelength': 642, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 643, 'counts': 32, 'integration_time': 0.00052}
{'wavelength': 644, 'counts': 35, 'integration_time': 0.00052}
{'wavelength': 645, 'counts': 27, 'integration_time': 0.00052}
{'wavelength': 646, 'counts': 58, 'integration_time': 0.00052}
{'wavelength': 647, 'counts': 45, 'integration_time': 0.00052}
{'wavelength': 648, 'counts': 89, 'integration_time': 0.00052}
{'wavelength': 649, 'counts': 118, 'integration_time': 0.00052}
{'wavelength': 650, 'counts': 222, 'integration_time': 0.00052}
{'wavelength': 651, 'counts': 188, 'integration_time': 0.00052}
{'wavelength': 652, 'counts': 230, 'integration_time': 0.00052}
{'wavelength': 653, 'counts': 338, 'integration_time': 0.00052}
{'wavelength': 654, 'counts': 417, 'integration_time': 0.00052}
{'wavelength': 655, 'counts': 356, 'integration_time': 0.00052}
{'wavelength': 656, 'counts': 308, 'integration_time': 0.00052}
{'wavelength': 657, 'counts': 259, 'integration_time': 0.00052}
{'wavelength': 658, 'counts': 299, 'integration_time': 0.00052}
{'wavelength': 659, 'counts': 301, 'integration_time': 0.00052}
{'wavelength': 660, 'counts': 288, 'integration_time': 0.00052}
{'wavelength': 661, 'counts': 305, 'integration_time': 0.00052}
{'wavelength': 662, 'counts': 327, 'integration_time': 0.00052}
{'wavelength': 663, 'counts': 272, 'integration_time': 0.00052}
{'wavelength': 664, 'counts': 218, 'integration_time': 0.00052}
{'wavelength': 665, 'counts': 206, 'integration_time': 0.00052}
{'wavelength': 666, 'counts': 182, 'integration_time': 0.00052}
{'wavelength': 667, 'counts': 149, 'integration_time': 0.00052}
{'wavelength': 668, 'counts': 132, 'integration_time': 0.00052}
{'wavelength': 669, 'counts': 106, 'integration_time': 0.00052}
{'wavelength': 670, 'counts': 104, 'integration_time': 0.00052}
{'wavelength': 671, 'counts': 59, 'integration_time': 0.00052}
{'wavelength': 672, 'counts': 52, 'integration_time': 0.00052}
{'wavelength': 673, 'counts': 44, 'integration_time': 0.00052}
{'wavelength': 674, 'counts': 26, 'integration_time': 0.00052}
{'wavelength': 675, 'counts': 36, 'integration_time': 0.00052}
{'wavelength': 676, 'counts': 30, 'integration_time': 0.00052}
{'wavelength': 677, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 678, 'counts': 38, 'integration_time': 0.00052}
{'wavelength': 679, 'counts': 33, 'integration_time': 0.00052}
{'wavelength': 680, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 681, 'counts': 39, 'integration_time': 0.00052}
{'wavelength': 682, 'counts': 25, 'integration_time': 0.00052}
{'wavelength': 683, 'counts': 31, 'integration_time': 0.00052}
{'wavelength': 684, 'counts': 12, 'integration_time': 0.00052}
{'wavelength': 685, 'counts': 15, 'integration_time': 0.00052}
{'wavelength': 686, 'counts': 28, 'integration_time': 0.00052}
{'wavelength': 687, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 688, 'counts': 23, 'integration_time': 0.00052}
{'wavelength': 689, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 690, 'counts': 20, 'integration_time': 0.00052}
{'wavelength': 691, 'counts': 29, 'integration_time': 0.00052}
{'wavelength': 692, 'counts': 18, 'integration_time': 0.00052}
{'wavelength': 693, 'counts': 16, 'integration_time': 0.00052}
{'wavelength': 694, 'counts': 22, 'integration_time': 0.00052}
{'wavelength': 695, 'counts': 21, 'integration_time': 0.00052}
{'wavelength': 696, 'counts': 10, 'integration_time': 0.00052}
{'wavelength': 697, 'counts': 13, 'integration_time': 0.00052}
{'wavelength': 698, 'counts': 8, 'integration_time': 0.00052}
{'wavelength': 699, 'counts': 24, 'integration_time': 0.00052}
```

Ahora lo que hago es medir el pico de yellow para distintas potencias, en particular para las potencias bajas q me faltan datos.
Mido con 1 segundo de tiempo de integración 