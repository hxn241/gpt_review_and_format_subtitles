import sys
sys.path.append("/Users/albert.verges/Library/CloudStorage/GoogleDrive-albert.verges@letsrebold.com/Unitats compartides/Data Science/I+D/chatgpt")

from assistant import AssistantManager, TOOLS_LIST


ASSISTANT_INSTRUCTIONS = """
Eres un experto en lengua y subtitulado. Tu función es asistir en la corrección del pautado de los subtítulos, es decir, revisar unos subtítulos proporcionados, ya pautados, y ajustarlos a la norma UNE, dadas las siguientes consideraciones:
1. Formato de datos: Los datos proporcionados tienen la siguiente estructura.
    tiempo_inicio—> tiempo_fin
    subtitulo_1
    \n
    tiempo_inicio—> tiempo_fin
    subtitulo_2
    …
    tiempo_inicio—> tiempo_fin
    subtitulo_N
2. Respetar limitación: En ningún caso el subtítulo puede superar los 15 caracteres por segundo. En el caso que se exceda la limitación, reformula el subtítulo manteniendo el significado y cumpliendo los requisitos. Utiliza una herramienta para calcular el número de caracteres.
3. División de líneas: Cada línea debe cumplir los criterios de división siguientes: 
    - Artículo y sustantivo irán siempre juntos, no se pueden partir en un cambio de línea.
    - No separar verbos compuestos en un cambio de línea.
    - No pueden acabar los subtítulos con un artículo determinante sin el sustantivo, deberán ir juntos.
    - Devuelve debajo del subtítulo la división de los caracteres de los subtítulos entre los segundos de duración. ejemplo: 9 caracteres
    - El máximo de caracteres por línea será 37 caracteres.
    - El final de un subtítulo con el inicio del siguiente ha que tener el mismo sentido que el original.

El proceso para la corrección será el siguiente:
1. Calcular los caracteres por segundo de cada subtitulo. Utiliza la herramienta character_count_by_sec para el cálculo. Al final de este proceso tendrás unos datos con la estructura siguiente:
    tiempo_inicio—> tiempo_fin
    subtitulo_1
    cps: catacteres_por_segundo_s1
    \n
    tiempo_inicio—> tiempo_fin
    subtitulo_2
    cps: catacteres_por_segundo_s2
    …
    tiempo_inicio—> tiempo_fin
    subtitulo_N
    cps: catacteres_por_segundo_sn
2. Corrige los subtítulos para que cumplan todas las restricciones especificadas.
3. Revisa el cumplimiento y comprueba el número de caracteres finales de cada subtítulo. Vuelve a utilizar la herramienta character_count_by_sec.
4. Responde con los subtítulos corregidos directamente.
"""

SUBTITLES_DATA = """
00:14:23:22 --> 00:14:27:02
poder poner algún tipo de sanción
porque no teníamos potestad.

00:14:27:04 --> 00:14:30:02
En la calle se aplaude que
se pueda sancionar un uso no

00:14:30:03 --> 00:14:33:13
eficiente del agua, como ya se
había aprobado en Torremolinos.

00:14:33:15 --> 00:14:36:07
La gente no está consciente
de que no hay agua.

00:14:36:09 --> 00:14:39:17
¿No somos responsables hasta que nos
tocan el bolsillo o nos sancionan?

00:14:39:17 --> 00:14:42:16
Yo veo que sí, se
diría que es sancionar.

00:14:46:18 --> 00:14:52:04
Ben Almádena no ha decidido aún si se podrán
usar las piscinas tampoco la axarquía que

00:14:52:05 --> 00:14:57:19
ha acordado en la reunión de Axaragua con
sensuar entre municipios la posible apertura.

00:14:57:21 --> 00:15:01:13
Este tono naranjado que ven es la calima
y es un episodio meteorológico cada vez

00:15:01:14 --> 00:15:05:05
más frecuente en Andalucía y, como no,
tiene sus efectos para los ciudadanos.

00:15:05:07 --> 00:15:08:06
Pues sí, porque el polvo en suspensión
afecta a los enfermos pulmonares y a la

00:15:08:07 --> 00:15:11:10
población en general que también padece
la contaminación urbana y sufre alergias.

00:15:11:12 --> 00:15:14:09
La prevención ayuda
a rebajar los síntomas.

00:15:16:01 --> 00:15:18:23
La calima se produce cuando
el viento sur arrastra polvo desde

00:15:18:24 --> 00:15:22:01
África, penetra en los pulmones
y agrava patologías respiratorias.

00:15:22:02 --> 00:15:23:12
Lo que tienen es una cualidad en sus

00:15:23:13 --> 00:15:25:09
bronquios que es la
hiperrespuesta bronquial.

00:15:25:11 --> 00:15:28:09
Es decir, ante un pequeño
estímulo, mis bronquios

00:15:28:10 --> 00:15:31:04
lo que hacen es que
reaccionan y se contraen.

00:15:31:06 --> 00:15:33:22
Bueno, pues la calima lo
que está haciendo es irritar

00:15:33:23 --> 00:15:36:11
la vía aérea de estos
pacientes y tienen síntomas.

00:15:36:11 --> 00:15:38:15
Para quienes los pasan
peor es bueno ponerse

00:15:38:16 --> 00:15:41:07
mascarilla, informarse de
la situación en los medios.

00:15:41:09 --> 00:15:44:02
Y atención al verano,
potencia la contaminación,

00:15:44:03 --> 00:15:46:08
la luz solar en el
suelo, forma ozono.

00:15:46:10 --> 00:15:49:18
Ese efecto de oxidación
en el aparato respiratorio

00:15:49:19 --> 00:15:53:15
también potencia estas
reacciones de inflamación y demás.
"""


def create_subtitle_reviewer_assistant():
    manager = AssistantManager(model="gpt-4-turbo")
    manager.create_assistant(
        name="SubtitleReviewer",
        instructions=ASSISTANT_INSTRUCTIONS,
        tools=TOOLS_LIST
    )

    return manager.assistant


def review_subtitles():
    manager = AssistantManager()
    manager.create_thread()
    # Create content given instructions
    manager.submit_and_run_task_to_thread(
        role="user",
        prompt=f"""
        A continuación se proporcionan los subtítulos que debes revisar y corregir para adaptarse a las directrices:
        ---
        {SUBTITLES_DATA}
        ---
        """
    )
    manager.wait_for_completion()
    print(f"::::CORRECTED SUBTITLES::::\n{manager.responses[-1]}")
    manager.submit_and_run_task_to_thread(
        role="user",
        prompt="""
        Haz una revisión de los resultados anteriores para validar que se cumplen todas las directrices indicadas, tanto de número de caracteres por segundo como de división de líneas.
        Para comprobar los caracteres por segundo, utiliza de nuevo la herramienta character_count_by_sec para recalcular y validar que se cumple la condición. 
        En el caso que se exceda el número máximo de caacteres por segundo o que la división de línea sea incorrecta, modifica el subtítulo para que se ajusto a los requerimientos.
        Responde directamente con el resultado final de todos los subtítulos, incluyendo los corregidos y los no corregidos.
        """
    )
    manager.wait_for_completion()
    print(f"::::REVIEWED SUBTITLES::::\n{manager.responses[-1]}")
    return manager.responses[-1]


if __name__ == "__main__":
    # create_subtitle_reviewer_assistant()
    sbt = review_subtitles()

