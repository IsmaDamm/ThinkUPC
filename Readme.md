# Backend with Django
## API RESTful de base documental con Openai
<br/>

### **Ejecución del servidor**
Para lanzar el servidor Django, ejecutar el archo `run.bat`. La primera vez que se ejcute instalará todos los paquetes necesarios (puede tardar unos minutos).

En caso de que no vaya o de error, ejecutar los sigueinte comandos:
* `pip install virtualenv`
* `virtualenv venv`
* `.\venv\Scripts\activate`
* `pip install -r requirements.txt`
* `python manage.py runserver <puerto>`

<br/>

### **Endpoints**
* `/api/file` | **METHOD:** <u>POST</u>

    Guarda, procesa y carga un nuevo archivo PDF en la base documental
    ### **Body**:
    * ***pdf_file***: Debe ser el nuevo arhivo PDF a guardar. **Importante: **Content-Type: application/pdf****

    ### **Success Response**:
    ```json
    {
        "message": "Success",
        "result": {
            "name": "Daniel García Serrano",
            "tlf": "+34 640 24 69 20",
            "email": "daniieelgs@gmail.com",
            "address": "C/ Camí Can Quintana 08350, Arenys de Mar",
            "gender": "Hombre",
            "age": "20",
            "url": "/public/10052023012937128942.pdf",
            "id": "10052023012937128942"
        }
    }
    ```

    * **url**: Url pública para acceder al archivo guardado
    * **id**: Id del archivo guardado
    * **name**: Nombre del autor del CV
    * **tlf**: Número de telefono del autor
    * **email**: Correo electrónico del autor
    * **address**: Dirección de vivienda del autor
    * **gender**: Género o sexo del autor
    * **age**: Edad del autor
    
<br/>

* `/api/query` | **METHOD:** <u>GET</u>

    Realiza una consulta a la base documental
    ### **Params**:
    * [str] ***q*** : Consulta a realizar

    ### Ej:
    [/api/query/?qDame%20a%20los%20dos%20con%20mas%20experiencia](http://127.0.0.1:8000/api/query/?q=Dame%20a%20los%20dos%20con%20mas%20experiencia)

    ```json
    
    {
        "message": "Success",
        "result": {
            "response": "Los dos empleados con más experiencia son Daniel García Serrano y Arnau Fugarolas Barbena, ya que ambos cuentan con 7 años de experiencia en el desarrollo de software y además Arnau Fugarolas Barbena ha realizado un Erasmus de dos meses de duración.",
            "id_results": [
                {
                    "id": "4052023003237107848",
                    "text": "Experiencia DUAL en Pasiona Adquiriendo experiencia aplicando mis conocimientos académicos en proyectos empresariales [...]",
                    "url": "/public/4052023003237107848.pdf",
                    "name": "Daniel García Serrano"
                },
                {
                    "id": "4052023011610715379",
                    "text": "es una consultora que recluta i forma programadores para diferentes empressas, además de llevar proyectos de desarrollo [...]",
                    "url": "/public/4052023011610715379.pdf",
                    "name": "Aranu Fugarolas Barbena"
                }
            ],
            "query": "Dame a los dos con mas experiencia"
        }
    }

     ```
    * **response**: Resultado de la respuesta generada
    * **id_results**: Lista de resultados donde ha extraido la información

        * **id**: Id del archivo
        * **text**: Texto del cual ha extraido la información
        * **url**: URL pública del archivo completo
        * **name**: Nombre del autor

    * **query**: Consulta realizada

<br/>

* `/api/file/<id>/` | **METHOD:** <u>DELETE</u>

    Elimina el archivo PDF y todos los registros de la base documental
    ### **Values**:
    * [int] ***id*** : Id a eliminar

<br/>

* `/api/file/remove/` | **METHOD:** <u>DELETE</u>

    Elimina todos los archivos PDF y todos los registros de la base documental

<br>

* `/api/file/` | **METHOD:** <u>GET</u>

    Obtiene un listado de datos de todos los documentos subidos

    ### Ej:
    [/api/file/](http://127.0.0.1:8000/api/file/)

    ```json
    {
        "message": "Success",
        "result": [
            {
                "id": 8052023222120350600,
                "url": "/public/8052023222120350600.pdf",
                "name": "Ismael El Hassouni El Fhayel",
                "tlf": "+34 613515224",
                "email": "issmaelhassouni@gmail.com",
                "address": "Enrique Granados, 43 3-3, 08330 Premia De Mar (Spain)",
                "gender": "Male",
                "age": "20"
            },
            {
                "id": 8052023223326490765,
                "url": "/public/8052023223326490765.pdf",
                "name": "Daniel García Serrano",
                "tlf": "+34 640 24 69 20",
                "email": "daniieelgs@gmail.com",
                "address": "C/ Camí Can Quintana 08350, Arenys de Mar",
                "gender": "Hombre",
                "age": "20"
            }
        ]
    }
     ```
    * **id**: Id del documento
    * **url**: URL pública del archivo completo
    * **name**: Nombre del autor del CV
    * **tlf**: Número de telefono del autor
    * **email**: Correo electrónico del autor
    * **address**: Dirección de vivienda del autor
    * **gender**: Género o sexo del autor
    * **age**: Edad del autor


<br>

* `/api/file/<id>` | **METHOD:** <u>GET</u>

    Obtiene datos del documento subido

    ### **Values**:
    * [int] ***id*** : Id del documento

    ### Ej:
    [/api/file/8052023223326490765](http://127.0.0.1:8000/api/file/8052023223326490765)

    ```json
    {
        "message": "Success",
        "result": {
            "id": 8052023223326490765,
            "url": "/public/8052023223326490765.pdf",
            "name": "Daniel García Serrano",
            "tlf": "+34 640 24 69 20",
            "email": "daniieelgs@gmail.com",
            "address": "C/ Camí Can Quintana 08350, Arenys de Mar",
            "gender": "Hombre",
            "age": "20"
        }
    }
     ```
    * **id**: Id del documento
    * **url**: URL pública del archivo completo
    * **name**: Nombre del autor del CV
    * **tlf**: Número de telefono del autor
    * **email**: Correo electrónico del autor
    * **address**: Dirección de vivienda del autor
    * **gender**: Género o sexo del autor
    * **age**: Edad del autor

<br>

* `/api/file/<id>` | **METHOD:** <u>POST</u>

    Actualiza el archivo PDF identificado de la base documental

    ### **Values**:
    * [int] ***id*** : Id del documento
    ### **Body**:
    * ***pdf_file***: Debe ser el nuevo arhivo PDF a actualizar. **Importante: **Content-Type: application/pdf****

    ### **Success Response**:
    ```json
    {
        "message": "Success",
        "result": {
            "url": "/public/8052023223326490765.pdf"
        }
    }
    ```

    * **url**: Url pública para acceder al archivo actualizado

<br/>

* `/api/file/<id>` | **METHOD:** <u>PUT</u>

    Actualiza los datos generados a partir del archivo PDF subido identificado

    ### **Values**:
    * [int] ***id*** : Id del documento
    ### **Body JSON**:
    * ***name \****: Nuevo nombre del autor.
    * ***tlf \****: Nuevo número de teléfono del autor. 
    * ***email \****: Nuevo email del autor. 
    * ***address \****: Nueva dirección del autor. 
    * ***gender \****: Nuevo género del autor. 
    * ***age \****: Nueva edad del autor. 
    ### Ej:
    ```json
    {
        "name": "Daniel García Serrano",
        "tlf": "+34 640 24 69 20",
        "email": "daniieelgs@gmail.com",
        "address": "C/ Camí Can Quintana 08350, Arenys de Mar, Barcelona, Cataluña, Spain",
        "gender": "Hombre",
        "age": "19"
    }
    ```
    ### **Success Response**:
    ```json
    {
        "message": "Success",
        "result": {
            "id": "10052023012937128942",
            "name": "Daniel García Serrano",
            "tlf": "+34 640 24 69 20",
            "email": "daniieelgs@gmail.com",
            "address": "C/ Camí Can Quintana 08350, Arenys de Mar, Barcelona, Cataluña, Spain",
            "gender": "Hombre",
            "age": "19",
            "url": "/public/10052023012937128942.pdf"
        }
    }
    ```

    * **id**: Id del documento
    * **url**: URL pública del archivo completo
    * **name**: Nombre del autor del CV
    * **tlf**: Número de telefono del autor
    * **email**: Correo electrónico del autor
    * **address**: Dirección de vivienda del autor
    * **gender**: Género o sexo del autor
    * **age**: Edad del autor

<br/>

* `/api/file/<id>` | **METHOD:** <u>PATCH</u>

    Actualiza los datos generados a partir del archivo PDF subido identificado

    ### **Values**:
    * [int] ***id*** : Id del documento
    ### **Body JSON**:
    * ***name***: Nuevo nombre del autor.
    * ***tlf***: Nuevo número de teléfono del autor. 
    * ***email***: Nuevo email del autor. 
    * ***address***: Nueva dirección del autor. 
    * ***gender***: Nuevo género del autor. 
    * ***age***: Nueva edad del autor.     
    ### Ej:
    ```json
    {
        "age": "19"
    }
    ```
    ### **Success Response**:
    ```json
    {
        "id": "10052023012332375068",
        "name": "Ismael El Hassouni El Fhayel",
        "tlf": "+34 613515224",
        "email": "issmaelhassouni@gmail.com",
        "address": "Enrique Granados, 43 3-3, 08330 Premia De Mar (Spain)",
        "gender": "Male",
        "age": "19",
        "url": "/public/10052023012332375068.pdf"
    }
    ```

    * **id**: Id del documento
    * **name**: Nombre del autor del CV
    * **tlf**: Número de telefono del autor
    * **email**: Correo electrónico del autor
    * **address**: Dirección de vivienda del autor
    * **gender**: Género o sexo del autor
    * **age**: Edad del autor

<br/>

* `/api/file/upload` | **METHOD:** <u>POST</u>

    Guarda un nuevo archivo PDF en la base documental
    ### **Body**:
    * ***pdf_file***: Debe ser el nuevo arhivo PDF a guardar. **Importante: **Content-Type: application/pdf****

    ### **Success Response**:
    ```json
    {
        "message": "Success",
        "result": {
            "id": "11052023110406936174",
            "url": "/public/11052023110406936174.pdf"
        }
    }
    ```

    * **url**: Url pública para acceder al archivo guardado
    * **id**: Id del archivo guardado
    
<br/>

* `/api/file/process/<id>`

    Hace el preprocesado del archivo (generación de chunks y embeddings)
    ### **Values**:
    * [int] ***id*** : Id del documento

    ### **Success Response**:
    ```json
    {
        "message": "Success",
        "result": ""
    }
    ```

<br/>

* `/api/file/load/<id>`

    Extrae y carga los datos del autor del PDF
    ### **Values**:
    * [int] ***id*** : Id del documento

    ### **Success Response**:
    ```json
    {
        "message": "Success",
        "result": {
            "id": "11052023110406936174",
            "name": "Daniel García Serrano",
            "tlf": "+34 640 24 69 20",
            "email": "daniieelgs@gmail.com",
            "address": "C/ Camí Can Quintana 08350, Arenys de Mar",
            "gender": "Hombre",
            "age": "20"
        }
    }
    ```

    * **id**: Id del documento
    * **name**: Nombre del autor del CV
    * **tlf**: Número de telefono del autor
    * **email**: Correo electrónico del autor
    * **address**: Dirección de vivienda del autor
    * **gender**: Género o sexo del autor
    * **age**: Edad del autor

<br/>


> © Pasiona


