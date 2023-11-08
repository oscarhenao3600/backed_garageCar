# nombres usados para seguridad
# envio de token = into
# nombre de usuario = Nuat
# rol =n3yB6PZnGE8n7F
# admin=J8p4SBfJgRfZCo
# tecnico=H7qm7gQr6DBGfM
# usuario=hbh2jFVsQM7RUy


from flask.views import MethodView
from flask import jsonify, request, session
import hashlib
import pymysql.cursors
import bcrypt
import jwt
from config import KEY_TOKEN_AUTH
from config import HOST 
from config import USER
from config import PASSWORD
from config import PORT 
from config import DATA_BASE
import datetime
import random
from validators import CreateRegisterSchema
from validators import CreateLoginSchema

def gen_codigo(tamaño):
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwyz01234567890')
    random.shuffle(chars)
    chars = ''.join(chars)
    sha1 = hashlib.sha1(chars.encode('utf8'))
    codigo = sha1.hexdigest()[:tamaño]
    return codigo

def crear_conexion():
    try:
        conexion = pymysql.connect(host = HOST ,user = USER ,password= PASSWORD,
                                   port= PORT, db = DATA_BASE,charset='utf8mb4')
        return conexion 
    except pymysql.Error as error:
        print('Se ha producido un error al crear la conexión:', error)
        
create_register_schema = CreateRegisterSchema()
create_login_schema = CreateLoginSchema()

class LoginControllers(MethodView):
    def post(self):
        print("Login y creacion de jwt para navegacion")
        content = request.get_json()
        #Instanciar la clase
        print(content)
        create_login_schema = CreateLoginSchema()
        errors = create_login_schema.validate(content)
        if errors:
            return errors, 403
        
        clave = content.get("password")
        id = content.get("id")
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE documento=%s",(id,)
        )
        auto = cursor.fetchone()
        conexion.close()  
        print("datos", auto)
        if auto == None:
            return jsonify({"Status": "usuario no registrado"}), 403
        if (auto[4] == id):
            if  bcrypt.checkpw(clave.encode('utf8'), auto[3].encode('utf8')):
                # encoded_jwt = jwt.encode(
                #     {'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
                #     'user':auto[0],
                #     'rol':auto[2]},  
                #     KEY_TOKEN_AUTH , algorithm='HS256')
                return jsonify({"Status": "login exitoso",'Nuat':auto[0],'rol':auto[2],'doc':auto[4]}), 200
            else:
                return jsonify({"Status": "Clave incorrecta"}), 403
        return jsonify({"Status": "Clave incorrecta"}),403


class RegisterControllers(MethodView):
    def post(self):
        print('------')
        content = request.get_json()
        nombre = content.get("nombre_completo")
        telefono = content.get("telefono")
        rol= content.get("rol")
        documento = content.get("documento")
        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(bytes(str(documento), encoding= 'utf-8'), salt)
        errors = create_register_schema.validate(content)
        if errors:
            return errors, 403
        conexion=crear_conexion()
        print(conexion)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT nombre, clave FROM  users WHERE documento=%s", (documento, ))
        auto=cursor.fetchone()
        if auto==None:
            cursor.execute(
                 "INSERT INTO users (nombre,telefono,rol,clave,documento) VALUES(%s,%s,%s,%s,%s)", (nombre,telefono,rol,hash_password,documento,))
            conexion.commit()
            conexion.close()
            return jsonify({"Status": "Bienvenido registro exitoso"}), 201
        else :    
            conexion.commit()
            conexion.close()
            return jsonify({"Status": "El usuario ya esta registrado"}), 403

# class RegisterAdminControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         documento= content.get("cedula")
#         nombres = content.get("nombres")
#         apellidos = content.get("apellidos")
#         email = content.get("email")
#         telefono = content.get("telefono")
#         direccion= content.get("direccion")
#         password = content.get("cedula")
#         roll=content.get("rol")
#         salt = bcrypt.gensalt()
#         hash_password = bcrypt.hashpw(bytes(str(password), encoding= 'utf-8'), salt)
#         if (request.headers.get('Authorization')):
#             token = request.headers.get('Authorization').split(" ")
#             try:
#                 data = jwt.decode(token[1], KEY_TOKEN_AUTH , algorithms=['HS256'])
#                 if (data.get('rol')=='J8p4SBfJgRfZCo'):
#                     conexion=crear_conexion()
#                     print(conexion)
#                     cursor = conexion.cursor()
#                     cursor.execute("SELECT clave,correo FROM usuarios WHERE correo=%s", (email, ))
#                     auto=cursor.fetchone()
#                     print(auto)
#                     if auto==None:
#                         print ("entra a guardar los datos en la bd",content)
#                         cursor.execute(
#                             "INSERT INTO usuarios (documento,nombres,apellidos,correo,telefono,direccion,rol,clave) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (documento,nombres.capitalize(),apellidos.capitalize(),email.lower(),telefono,direccion,roll,hash_password,)
#                             )
#                         conexion.commit()
#                         conexion.close()
#                         return jsonify({"Status": "Bienvenido ha sido registrado"}), 201
#                     else :
#                         conexion.commit()
#                         conexion.close()
#                         return jsonify({"Status": "El usuario ya en la BD"}), 200
#                     # conexion.commit()
#                     # conexion.close()
#                 else:
#                     return jsonify({"Status": "No autorizado por token"}), 498
#                 return jsonify({"Status": "Autorizado por token"}), 202
#             except:
#                 return jsonify({"Status": "TOKEN NO VALIDO"}), 403

# class ConsultaUsuarioControllers(MethodView):
#     def get(self):
#         documentoUsuario = request.args.get("documento")
#         conexion=crear_conexion()
#         cursor = conexion.cursor(pymysql.cursors.DictCursor)       
#         cursor.execute(
#             "SELECT correo,nombres,apellidos,documento,telefono,direccion FROM usuarios WHERE documento=%s", (documentoUsuario,)
#         )
#         auto = cursor.fetchone()
#         conexion.close()
#         if auto==None:
#             return jsonify({"Status": "usuario no registrado"}), 403
#         else:
#             return jsonify({"Status":"datos de usuario","data":auto}), 200

# class ConsultaDiagnosticoControllers(MethodView):
#     def get(self):
#         print ("consulta las ordenes de servicio asignadas al tecnico")
#         nombreTec = request.args.get("nombreTecnico")
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "historicos"]

#         myquery = { "nombreTecnico": nombreTec,"estado":"abierta" }
#         ordenes = mycol.find(myquery)

#         keys = ["_id"]
#         ordenesOutput = []
#         for orden in ordenes:
#             ordenesOutput.append({x:orden[x] for x in orden if x not in keys})
#         print("Lista de ordenes",ordenes)
#         return jsonify({'data':ordenesOutput}), 200

# class ConsultaHistoricoUsuarioControllers(MethodView):
#     def get(self):
#         print ("consulta las ordenes de servicio asignadas al tecnico")
#         nombre = request.args.get("nombre")
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "historicos"]

#         myquery = { "nombreCliente":{"$regex": f"^{nombre}"},"estado":"abierta" }
#         ordenes = mycol.find(myquery)

#         keys = ["_id"]
#         ordenesOutput = []
#         for orden in ordenes:
#             ordenesOutput.append({x:orden[x] for x in orden if x not in keys})
#         print("Lista de ordenes",ordenes)
#         return jsonify({'data':ordenesOutput}), 200

# class ConsultaOrdenTecnicosControllers(MethodView):
#     def get(self):
#         print ("consulta todos los tecnicos con ordenes activas")
#         nombreTec= request.args.get("tecnico") # asi es que envia por cabecera la categoría seleccionada - headers idproducto - R001
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "historicos"]

#         myquery = { "nombreTecnico":nombreTec,"estado":"cerrada" }
#         tecnicos = mycol.find(myquery)

#         keys = ["_id"]
#         output = []
#         for tecnico in tecnicos:
#             output.append({x:tecnico[x] for x in tecnico if x not in keys})
#         print("Lista de productos",tecnicos)
#         return jsonify({'data':output}), 200

# class ConsultaDispositivoOrdenControllers(MethodView):
#     def get(self):
#         codigo = request.args.get("orden")
#         print ("consulta las ordenes",codigo)
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "historicos"]

#         myquery = { "ordenServicio": codigo,"estado":"abierta" }
#         tarea = mycol.find_one(myquery)
#         tarea.pop("_id")        
#         return jsonify({'data':tarea}), 200

# class ConsultaEquipoControllers(MethodView):
#     def get(self):
#         serEquipo = request.args.get("serial")
#         print ("consulta por serial",serEquipo)
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "historicos"]

#         myquery = { "serialEquipo": serEquipo }
#         equipo = mycol.find_one(myquery)
#         equipo.pop("_id")        
#         return jsonify({'data':equipo}), 200

# class ConsultaEstadoOrdenControllers(MethodView):
#     def get(self):
#         orden = request.args.get("orden")
#         print ("consulta por serial",orden)
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "historicos"]

#         myquery = { "ordenServicio": orden }
#         historia = mycol.find_one(myquery)
#         historia.pop("_id")
#         return jsonify({'data':historia}), 200

# class ConsultaTecnicosControllers(MethodView):
#     def get(self):
#         conexion=crear_conexion()
#         cursor = conexion.cursor()
#         cursor.execute(
#             f" SELECT nombres FROM usuarios WHERE rol like '{'H7qm7gQr6DBGfM'}%'")
#         listatecnicos=cursor.fetchall()
#         tecnicos = [tecnico[0] for tecnico in listatecnicos];
#         conexion.close()
#         return jsonify({"Status":"Lista de técnicos",'data':tecnicos}), 200
#         conexion.close()

# class ConsultaOrdenControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         correo = content.get("email")
#         nombres = content.get("nombres")
#         apellidos=content.get("apellidos")
#         telefono= content.get("telefono")
#         documento= content.get("cedula")
#         conexion=crear_conexion()
#         cursor = conexion.cursor(pymysql.cursors.DictCursor)
#         if(correo!=""):
#             sql = "SELECT correo,nombres,apellidos,documento,telefono FROM usuarios WHERE correo=%s"
#             adr= correo
#             cursor.execute(sql,adr) 
#             datos=cursor.fetchone()
#         elif(documento!=""):
#             sql = "SELECT correo,nombres,apellidos,documento,telefono FROM usuarios WHERE documento=%s"
#             adr= documento
#             cursor.execute(sql,adr) 
#             datos=cursor.fetchone()
#         elif(telefono!=""):
#             sql = "SELECT correo,nombres,apellidos,documento,telefono FROM usuarios WHERE telefono=%s"
#             adr= telefono
#             cursor.execute(sql,adr) 
#             datos=cursor.fetchone()
#             if datos==None:
#                 sql = "UPDATE usuarios SET telefono = %s WHERE documento = %s"
#                 val = (telefono,documento)
#                 cursor.execute(sql,val)
#                 print("numero telefonico actualizado")
#         if datos==None:
#             return jsonify({"Status": "El usuario no se encuentra registrado"}), 201
#         else :
#             return jsonify({"Status": "El usuario si esta registrado", "data":datos}), 200 

# ## para el modulo de tienda cargar los productos de la base de datos
# #http://127.0.0.1:5000/productos/tipo=?R o P o E
# class ProductosControllers(MethodView):
#     def get(self):
#         print ("consulta todos los productos de la tienda")
#         Tproducto= request.args.get("tipo") # asi es que envia por cabecera la categoría seleccionada - headers idproducto - R001
#         #consulta base de datos
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         cliente=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)

#         mydb = cliente[ "dbproductos"]
#         mycol = mydb[ "productos"]

#         myquery = { "idproducto": { "$regex": Tproducto} }
#         productos = mycol.find(myquery)

#         keys = ["_id"]
#         output = []
#         for producto in productos:
#             output.append({x:producto[x] for x in producto if x not in keys})
#         print("imagen a mostrar",producto["rutaimagen"])
#         print("Lista de productos",productos)
#         return jsonify({'data':output}), 200

# ## consulta a la base de datos el producto y se le agrega al usuario
# #http://127.0.0.1:5000/productoId/id_producto=?R120 o P349 o E998
# class ProductoIdControllers(MethodView):
#     def get(self):
#         print ("consulta un producto de la tienda")
#         id_producto=request.args.get("idproducto") # asi es que envia por cabecera la categoría seleccionada - headers idproducto - R001
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         myclient= pymongo.MongoClient("mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/")
#         mydb= myclient["dbproductos"]
#         mycol = mydb["productos"]
#         producto=mycol.find_one({ "idproducto":id_producto})
#         if(producto!=None):
#             producto.pop("_id")
#             return jsonify({'status':'envio ok','data':producto}), 200
#         return jsonify({'status':'Producto no encontrado'}), 403

# #http://127.0.0.1:5000/buscarProductos
# class ProductosBuscarControllers(MethodView):
#     def get(self):
#         nombre = request.args.get("buscarproducto")
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#         mongo=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
#         mydb = mongo["dbproductos"]
#         mycol = mydb["productos"]
#         myquery = { "nombre": { "$regex": f"^{nombre}" } }  
#         result = mycol.find(myquery)
#         keys = ["_id"]
#         lista_productos = []
#         for producto in result:
#             lista_productos.append({ llave:producto[llave] for llave in producto if llave not in keys })
#         print("dato del producto",lista_productos)
#         return jsonify({'status':'Lista de productos','data':lista_productos}), 200

# ## para modulo admin, creacion de productos
# class CrearControllers(MethodView):
#     def post(self):
#         print ("crear producto en la tienda")
#         content = request.get_json()
#         numero=content.get("idproducto")
#         tipodispositivo=content.get("tipodispositivo")
#         precio = content.get("precio")
#         nombre = content.get("nombre")
#         cantidad= content.get("cantidad")
#         imagen=content.get("imagen")
#         descripcion=content.get("descripcionproductos")

#         id_producto=tipodispositivo+numero

#         if (request.headers.get('Authorization')):
#             token = request.headers.get('Authorization').split(" ")
#             try:
#                 data = jwt.decode(token[1], KEY_TOKEN_AUTH , algorithms=['HS256'])
#                 if (data.get('rol')=='J8p4SBfJgRfZCo'):

#                     MONGO_HOST="jhtserverconnection.ddns.net"
#                     MONGO_PUERTO="39011"
#                     MONGO_TIEMPO_FUERA=1000
#                     MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#                     mongo=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
#                     mydb = mongo["dbproductos"]
#                     mycol = mydb["productos"]
#                     myproduc = { "idproducto": id_producto, "precio": float(precio) ,"nombre":nombre,"cantidad":int(cantidad),"rutaimagen":imagen,"descripcionproductos":descripcion }
#                     mycol.insert_one(myproduc)

#                     print("--Artuculo guardado en la BD--")
#                 else:
#                     return jsonify({"Status": "No autorizado por token"}), 498
#                 return jsonify({"Status": "Autorizado por token", "emailextraido": data.get("email"),}), 202
#             except:
#                 return jsonify({"Status": "TOKEN NO VALIDO"}), 403
#         return jsonify({"Status": "No ha enviado un token"}), 403

# ## para modulo admin, eliminar de productos
# class EliminarProductoControllers(MethodView):
#     def get(self):
#         id_producto= request.args.get("idproe")
#         print ("eliminar producto de la tienda")
#         if (request.headers.get('Authorization')):
#             token = request.headers.get('Authorization').split(" ")
#             try:
#                 data = jwt.decode(token[1], KEY_TOKEN_AUTH , algorithms=['HS256'])
#                 if (data.get('rol')=='J8p4SBfJgRfZCo'):

#                     MONGO_HOST="jhtserverconnection.ddns.net"
#                     MONGO_PUERTO="39011"
#                     MONGO_TIEMPO_FUERA=1000
#                     MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#                     mongo=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
#                     mydb = mongo["dbproductos"]
#                     mycol = mydb["productos"]

#                     myquery = { "idproducto":id_producto}
#                     mycol.delete_one(myquery)

#                     print("--Artuculo eliminado de la BD--")
#                 else:
#                     return jsonify({"Status": "No autorizado por token"}), 498
#                 return jsonify({"Status": "Autorizado por token"}), 202
#             except:
#                 return jsonify({"Status": "TOKEN NO VALIDO"}), 403
#         return jsonify({"Status": "No ha enviado un token"}), 403

# ## para modulo admin, eliminar de productos

# class EliminarUserControllers(MethodView):
#     def get(self):
#         correo= request.args.get("correo")
#         print ("eliminar usuario del sistema")
#         if (request.headers.get('Authorization')):
#             token = request.headers.get('Authorization').split(" ")
#             try:
#                 data = jwt.decode(token[1], KEY_TOKEN_AUTH , algorithms=['HS256'])
#                 if (data.get('rol')==('J8p4SBfJgRfZCo')):
#                     conexion=crear_conexion()
#                     cursor = conexion.cursor()
#                     cursor.execute("DELETE FROM usuarios WHERE correo=%s",(correo,))
#                     conexion.commit()
#                     conexion.close()
#                     print("--Usuario eliminado de la BD--")
#                 else:
#                     return jsonify({"Status": "No autorizado por token"}), 498
#                 return jsonify({"Status": "Autorizado por token"}), 200
#             except:
#                 return jsonify({"Status": "TOKEN NO VALIDO"}), 498
#         return jsonify({"Status": "No ha enviado un token"}), 203

# class CambioClaveControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         email =content.get("email") 
#         newPassword =content.get("password")
#         salt = bcrypt.gensalt()
#         hash_password = bcrypt.hashpw(bytes(str(newPassword), encoding= 'utf-8'), salt)
#         errors = create_login_schema.validate(content)
#         if errors:
#             return errors, 403
#         conexion=crear_conexion()
#         cursor = conexion.cursor()
#         sql = "UPDATE usuarios SET clave = %s WHERE correo = %s"
#         val = (hash_password,email)
#         cursor.execute(sql,val)
#         conexion.commit()
#         conexion.close()
#         return jsonify({'status':'clave actualizada satisfactoriamente'}), 200

# class OrdenServicioControllers(MethodView):
#     def post(self):
#         rol="hbh2jFVsQM7RUy"
#         content = request.get_json()
#         print("######## estos son los datos enviados desde el front ####",content)
#         nombreCliente = content.get("nombres")
#         apellidosCliente = content.get("apellidos")
#         telefono = content.get("telefono")
#         cedula = content.get("cedula")
#         correo=content.get("email")
#         ordenServicio = gen_codigo(5)
#         nombreTecnico = content.get("nombtecnico")
#         serialEquipo=content.get("serial_equipo")
#         marcaEquipo = content.get("marcadispositivo")
#         tipoDispositivo = content.get("tipodispositivo")
#         accesoriosDispositivos = content.get("accesorios")
#         diagnosticoInicial = content.get("diaginicial")
#         tiposervicio = content.get("tiposervicio")
#         fecha = content.get("fecha")+content.get("hora")
# ## consulta a bd sql para saber si el usuario esta registrado en el sistema, si no se crea y el passwor inicial
# ## sera el el documento de identidad 
#         conexion=crear_conexion()
#         cursor = conexion.cursor(pymysql.cursors.DictCursor)
#         sql = "SELECT correo,nombres,apellidos FROM usuarios WHERE correo=%s"
#         adr= correo
#         cursor.execute(sql,adr) 
#         datos=cursor.fetchone()
#         if datos==None:
#             salt = bcrypt.gensalt()
#             hash_password = bcrypt.hashpw(bytes(str(cedula), encoding= 'utf-8'), salt)
#             cursor.execute("INSERT INTO usuarios (correo,nombres,apellidos,clave,documento,rol,telefono) VALUES(%s,%s,%s,%s,%s,%s,%s)", (correo.lower(),nombreCliente.capitalize(),apellidosCliente.capitalize(),hash_password,cedula,rol,telefono,))
#             conexion.commit()
#             conexion.close()
#             print("usuario creado en la base de datos SQL")
#             #return jsonify({"Status": "El usuario se a registrado para crear la orden de servicio"}), 201
#         else :
#             print("usuario esta en base de datos")
#             #return jsonify({"Status": "El usuario esta registrado"}), 200
#         nombreCompleto=nombreCliente.capitalize() +" "+ apellidosCliente.capitalize()
#         diagnostico= str(fecha) + " " + tiposervicio + " " + nombreTecnico + " " + " " + diagnosticoInicial
#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         myclient= pymongo.MongoClient("mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/")
#         mydb= myclient["dbproductos"]
#         mycol = mydb["historicos"]
#         mydict = {  "nombreCliente":str(nombreCompleto),
#                     "telefono":str(telefono),
#                     "ordenServicio":str(ordenServicio),                   
#                     "nombreTecnico":str(nombreTecnico),
#                     "serialEquipo":str(serialEquipo),
#                     "marcaEquipo":str(marcaEquipo),
#                     "tipoDispositivo":str(tipoDispositivo),
#                     "accesoriosDispositivos":str(accesoriosDispositivos),
#                     "diagnosticoInicial":str(diagnostico),
#                     "fecha":str(fecha),
#                     "estado":"abierta"
#                     }
#         datos = mycol.insert_one(mydict)
#         print("datos guardados en mongo", datos)
#         return jsonify({"Status": "Orden de servicio almacenada correctamente"}), 200

# class ActualizarUsuarioControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         nombres = content.get("nombres")
#         apellidos = content.get("apellidos")
#         email = content.get("email")
#         telefono = content.get("telefono")
#         direccion= content.get("direccion")
#         roll=content.get("rol")

#         print("llegada de datos del front",content)
#         if (request.headers.get('Authorization')):
#             token = request.headers.get('Authorization').split(" ")
#             try:
#                 data = jwt.decode(token[1], KEY_TOKEN_AUTH , algorithms=['HS256'])
#                 if (data.get('rol')==('J8p4SBfJgRfZCo')):
#                     print("si entra a la comparacion de rol")
#                     conexion=crear_conexion()
#                     print(conexion)
#                     cursor = conexion.cursor()
#                     sql = "UPDATE usuarios SET nombres=%s,apellidos=%s,telefono=%s,direccion=%s,rol=%s WHERE correo = %s"
#                     val = (nombres.capitalize(),apellidos.capitalize(),telefono,direccion,roll,email.lower())
#                     cursor.execute(sql,val)
#                     conexion.commit()
#                     conexion.close()
#                     return jsonify({'status':'Usuario Actualizado Satisfactoriamente'}), 200
#                     print("--Usuario Actualizado--")
#                 else:
#                     return jsonify({"Status": "No autorizado por token"}), 498
#                 return jsonify({"Status": "Autorizado por token"}), 202
#             except:
#                 return jsonify({"Status": "TOKEN NO VALIDO"}), 403
#         return jsonify({"Status": "No ha enviado un token"}), 403

# class ActualizarProductoControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         numero=content.get("idproducto")
#         tipodispositivo=content.get("tipodispositivo")
#         id_producto = content.get("idproducto")
#         precio = content.get("precio")
#         nombre = content.get("nombre")
#         cantidad = content.get("cantidad")
#         imagen= content.get("imagen")
#         descripcion=content.get("descripcionproductos")

#         id_producto=str(tipodispositivo+numero)

#         print("llegada de datos del front",id_producto)
#         if (request.headers.get('Authorization')):
#             token = request.headers.get('Authorization').split(" ")
#             try:
#                 data = jwt.decode(token[1], KEY_TOKEN_AUTH , algorithms=['HS256'])
#                 if (data.get('rol')==('J8p4SBfJgRfZCo')):
                    
#                     MONGO_HOST="jhtserverconnection.ddns.net"
#                     MONGO_PUERTO="39011"
#                     MONGO_TIEMPO_FUERA=1000
#                     MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"
#                     mongo=pymongo.MongoClient(MONGO_URI,serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
#                     mydb = mongo["dbproductos"]
#                     mycol = mydb["productos"]
#                     myquery = { "idproducto": id_producto }
#                     newvalues = { "$set": { "precio": float(precio) ,"nombre":nombre,"cantidad":int(cantidad),"rutaimagen":imagen, "descripcionproductos":descripcion } }

#                     mycol.update_many(myquery, newvalues)

#                     return jsonify({'status':'Usuario Actualizado Satisfactoriamente'}), 200
#                     print("--Articulo Actualizado--")
#                 else:
#                     return jsonify({"Status": "No autorizado por token"}), 498
#                 return jsonify({"Status": "Autorizado por token"}), 202
#             except:
#                 return jsonify({"Status": "TOKEN NO VALIDO"}), 403
#         return jsonify({"Status": "No ha enviado un token"}), 403

# class ActualizarHistoriaControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         codigo = content.get("ordenServio")
#         escalarservicio = content.get("escalar")
#         reporte = content.get("reporte")

#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         #conexion al servidor y a la base de datos de mongo.
#         myclient= pymongo.MongoClient("mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/")
#         mydb= myclient["dbproductos"]
#         mycol = mydb["historicos"]
#         mycol.update_many({ "ordenServicio":codigo}, {"$set": {"diagnosticoDetallado":reporte },"$set": {"escalarServicio":escalarservicio}})
#         return jsonify({"Status": "Historia Actualizada"}), 201

# class ActualizarSalidaControllers(MethodView):
#     def post(self):
#         content = request.get_json()
#         serialequipo=request.get_json("serial")
#         entrega = content.get("Observacion")
#         fecha = content.get("fecha")
#         salida= str(fecha)+" "+entrega

#         MONGO_HOST="jhtserverconnection.ddns.net"
#         MONGO_PUERTO="39011"
#         MONGO_TIEMPO_FUERA=1000
#         #conexion al servidor y a la base de datos de mongo.
#         myclient= pymongo.MongoClient("mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/")
#         mydb= myclient["dbproductos"]
#         mycol = mydb["historicos"]
#         mycol.update_many({ "serialEquipo":serialequipo}, {"$set": {"historicoCierre":salida },"$set": {"estado":"cerrado"}})
#         return jsonify({"Status": "Historia Actualizada"}), 201

# class TokenContrasenaControllers(MethodView):
#     def post(self):
#         usuario="Querido usuario"
#         content = request.get_json()
#         email =content.get("email")
#         cod=gen_codigo(8)
#         korreo.send_correo(usuario,email,cod)
#         return jsonify({'Status':'Token generado','CodigoR':cod}), 200

# class FacturacionControllers(MethodView):
#     def post(self):
#         content = request.get_json()

#         #korreo.send_send_info(usuario,correo,mensaje)
#         print(content)
#         return jsonify({'Status':'dato para facturacion'}), 200
