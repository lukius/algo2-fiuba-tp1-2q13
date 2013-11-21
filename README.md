<div align="center">
Algoritmos y Programación II (75.04)<br>
Facultad de Ingeniería - UBA<br>
Segundo cuatrimestre de 2013<br>
</div>


#### Descripción

Juez de batalla para las implementaciones del TP 1  


#### Enunciado

Disponible en este mismo repositorio

#### Requisitos

El juez está implementado en Python 2.7, y utiliza Javascript para la parte visual. Los navegadores
principalmente recomendados son Chrome o Chromium (en ese orden). En caso de no existir ninguno,
sólo se podrá correr las simulaciones en texto plano.  

Además, tener en cuenta que fue íntegramente desarrollado y testeado en plataformas Linux.

#### Cómo utilizarlo

Para utilizar el juez, se debe ejecutar el archivo j especificando cada uno de los dos programas
cuya lucha se desee simular. A través de distintas opciones de línea de comando es posible determinar
la forma en la que se visualizará la simulación:
 * <b>-t</b>  Utilizar sólo texto plano para mostrar los resultados de la batalla (por defecto, se recurrirá al modo gráfico)
 * <b>-r</b>  Repetir la batalla, en caso de existir. El juez no la recreará sino que intentará visualizar la batalla a partir de los datos ya generados.  

Para mayor información, recurrir a la opción <b>-h</b>.  

#### Programa de prueba

El código en este repositorio incluye un programa (judge/prg/dummy) que implementa la interfaz requerida por el enunciado del TP.
Si bien es completamente aleatorio, puede utilizarse para recrear batallas al azar o bien para confrontarlo
con estrategias más inteligentes a los efectos de analizar la eficacia de las mismas.  

Las líneas siguientes muestran, entonces, una posible ejecución del juez para simular una batalla totalmente aleatoria:

```
$ ./j -t judge/prg/dummy judge/prg/dummy 
INFO: Posicionando soldados de dummy-89174
INFO: Posicionando soldados de dummy-56520
INFO: Procesando turno 1
INFO: Procesando turno 2
INFO: Procesando turno 3
INFO: Procesando turno 4
INFO: Procesando turno 5
INFO: Procesando turno 6
INFO: Procesando turno 7
INFO: Procesando turno 8
INFO: Procesando turno 9
INFO: Procesando turno 10
INFO: Batalla finalizada! Mostrando resultados...
INFO: dummy-56520: 1500 puntos -- dummy-89174: 1498 puntos
INFO: Ganador: dummy-56520
```

Este programa genera un valor numérico al azar para conformar su nombre de ejército.


#### Interfaz gráfica

Cuando la batalla se visualiza en forma gráfica, las flechas del teclado permiten avanzar y retroceder turnos. Esto
mismo, además, puede hacerse moviendo la barra de progreso de turnos, ubicada sobre el territorio. El botón Next, 
por otra parte, sólo avanza turnos al ser presionado.  

Al colocar el cursor del mouse sobre un soldado cualquiera, podrá conocerse su nombre y su rango de influencia.
El rango también puede verse pasando el cursor del mouse sobre los nombres de los soldados en la tabla ubicada
a la derecha del territorio.  

Un ejemplo de cómo se visualiza la batalla puede encontrarse [acá](http://lukius.github.io/algo2-fiuba-tp1-2q13/)
