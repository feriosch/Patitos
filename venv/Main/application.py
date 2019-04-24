from flask import Flask,render_template,request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import dropbox
import datetime
import io


dbx = dropbox.Dropbox("uLQxcVq_gSAAAAAAAAAADX50ce1j-fy3qtTAb9ricooFDS1GFb5zv7sk_nnI4DMR")

app = Flask(__name__)
app.secret_key = "ElPatatota"
app.config["MONGO_URI"] = "mongodb://Master:CiscoCLass@ssei-shard-00-00-bwmef.mongodb.net:27017,ssei-shard-00-01-bwmef.mongodb.net:27017,ssei-shard-00-02-bwmef.mongodb.net:27017/test?ssl=true&replicaSet=SSEI-shard-0&authSource=admin&retryWrites=true"
#app.config["MONGO_URI"] =  "mongodb+srv://Master:CiscoCLass@ssei-bwmef.mongodb.net/test?retryWrites=true"
mongo = PyMongo(app)


@app.route('/', methods=['GET','POST'])
def home_page():
    if request.method == 'POST':
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")
        usuarioPrueba = mongo.db.usuarios.find_one({'nombre':usuario,'contrasena':contrasena})
        if usuarioPrueba is not None:
            session['username'] = usuario
            session['tipo'] = usuarioPrueba['tipo']
            session['tecnicoID'] = str(usuarioPrueba['tecnicoID'])
            if(session['tipo'] == "tecnico"):
                return render_template("hometecnico.html")
            else:
                return render_template("home.html")
        else:
            return "Not found"

    else:
        session.pop('username',None)
        session.pop('tipo',None)
        session.pop('tecnicoID',None)
        return render_template("index.html")


@app.route('/FirmaDig/Tecnico/<servicioID>')
def visualizarImagenes(servicioID):
    return render_template("FirmaDig.html")


@app.route('/FirmaDig/Usuario/<servicioID>')
def visualizarImagenesDos(servicioID):
    return render_template("FirmaDig.html")

@app.route('/subirFirma', methods= ['POST'])
def subirFirma():
    print(request.files)
    return render_template("FirmaDig.html")

@app.route('/material',methods=['GET','POST'])
def materiales():
    if 'username' in session:
        if request.method == 'POST':
            if request.form["btn"] == "Anadir":
                materialNombre = request.form.get("materialNombre")
                materialDescripcion = request.form.get("materialDescripcion")
                flag = mongo.db.material.find_one({'nombre': materialNombre})

                if flag is None:
                    mongo.db.material.insert_one({'nombre': materialNombre, 'descripcion': materialDescripcion})
                else:
                    diccionarioMateriales = mongo.db.material.find({})
                    return redirect(url_for('materiales'))
                diccionarioMateriales = mongo.db.material.find({})
                return redirect(url_for('materiales'))

            elif request.form["btn"] == "Guardar":
                materialNombre = request.form.get("materialNombre")
                materialDescripcion = request.form.get("materialDescripcion")
                id = request.form.get("materialID")
                id = ObjectId(id)
                mongo.db.material.update_one({'_id': id}, {"$set": {'nombre': materialNombre,
                                                                    'descripcion': materialDescripcion}})
                return redirect(url_for('materiales'))
        else:
            diccionarioMateriales = mongo.db.material.find({})
            if (session['tipo'] == "tecnico"):
                return render_template("materialtecnico.html",materiales=diccionarioMateriales)
            else:
                return render_template("material.html",materiales=diccionarioMateriales)

    else:
        return redirect(url_for('home_page'))



@app.route('/material/eliminar',methods=['GET','POST'])
def eliminarMaterial():
    id = request.form.get("id")
    id = ObjectId(id)
    mongo.db.material.delete_one({'_id': id})
    diccionarioMateriales = mongo.db.material.find({})
    return render_template("material.html", materiales=diccionarioMateriales)

@app.route('/tecnico',methods=['GET','POST'])
def tecnico():
    if 'username' in session:
        if request.method == 'POST':
            if request.form["btn"] == "Anadir":
                tecnicoNombre = request.form.get("tecnicoNombre")
                tecnicoFoto = request.files['tecnicoFoto']
                tecnicoNacimiento = request.form.get("tecnicoNacimiento")
                tecnicoTelefono = request.form.get("tecnicoTelefono")

                # Aqui se tiene que subir la foto a Dropbox
                id = ObjectId()
                idString = str(id)
                route = '/FotosTecnicos/'+idString+'.jpg'
                dbx.files_upload(tecnicoFoto.read(), route)
                link = dbx.sharing_create_shared_link(route).url
                url = list(link)
                url[-1] = '1'
                url = ''.join(url)

                mongo.db.tecnico.insert_one({'_id': id, 'nombre': tecnicoNombre, 'fechaDeNacimiento': tecnicoNacimiento,
                                             'telefono': tecnicoTelefono, 'foto': url, 'estado': 'Activo'})

                return redirect(url_for('tecnico'))
            elif request.form["btn"] == "Guardar":
                conFoto = True

                tecnicoNombre = request.form.get("tecnicoNombre")
                tecnicoNacimiento = request.form.get("tecnicoFechaDeNacimiento")
                tecnicoTelefono = request.form.get("tecnicoTelefono")
                id = request.form.get("tecnicoID")

                try:
                    tecnicoFoto = request.files['tecnicoFoto']
                except:
                    conFoto = False

                if conFoto:
                    route = '/FotosTecnicos/' + id + '.jpg'
                    dbx.files_upload(tecnicoFoto.read(), route, mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)

                    id = ObjectId(id)

                    mongo.db.tecnico.update_one({'_id': id},
                                                {"$set": {'nombre': tecnicoNombre, 'fechaDeNacimiento': tecnicoNacimiento,
                                                          'telefono': tecnicoTelefono, 'foto': url, 'estado': 'Activo'}})
                else:
                    id = ObjectId(id)

                    mongo.db.tecnico.update_one({'_id': id},
                                                {"$set": {'nombre': tecnicoNombre, 'fechaDeNacimiento': tecnicoNacimiento,
                                                          'telefono': tecnicoTelefono,  'estado': 'Activo'}})
                return redirect(url_for('tecnico'))
            elif request.form["btn"] == "Desactivar":
                id = request.form.get("tecnicoID")
                id = ObjectId(id)
                mongo.db.tecnico.update_one({'_id': id}, {"$set": {'estado': 'Inactivo'}})
                return redirect(url_for('tecnico'))
            elif request.form["btn"] == "Reactivar":
                id = request.form.get("tecnicoID")
                id = ObjectId(id)
                mongo.db.tecnico.update_one({'_id': id},
                                            {"$set": {'estado': 'Activo'}})
                return redirect(url_for('tecnico'))
        else:
            diccionarioTecnicos = mongo.db.tecnico.find({})
            if (session['tipo'] != "tecnico"):
                return render_template("tecnico.html", tecnicos=diccionarioTecnicos)
            else:
                return redirect(url_for('home_page'))

    else:
        return redirect(url_for('home_page'))


@app.route('/tecnico/desactivar', methods=['GET', 'POST'])
def desactivarTecnico():
    id = request.form.get("id")
    id = ObjectId(id)
    mongo.db.tecnico.update_one({'_id': id}, {"$set": {'estado': 'Desactivado'}})
    return redirect(url_for('tecnico'))


@app.route('/inventarios',methods=['GET','POST'])
def inventario():
    if 'username' in session:
        if request.method == 'POST':

            return redirect(url_for('inventario'))
        else:
            if (session['tipo'] != "tecnico"):
                pipeline = [{'$lookup': {
                    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'patatita'}
                }, {'$lookup': {
                    'from': 'material', 'localField': 'material_ID', 'foreignField': '_id', 'as': 'tomatito'}
                    }
                ]
                arrTemp = []
                for doc in (mongo.db.materialesTecnico.aggregate(pipeline)):
                    arrTemp.append(doc)
                diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo'})
                diccionarioMateriales = mongo.db.material.find({})
                diccionarioMaterialesArray = []
                for element in diccionarioMateriales:
                    diccionarioMaterialesArray.append([element["nombre"],str(element["_id"])])


                    return render_template("inventarios.html", diccRela=arrTemp, tecnicos=diccionarioTecnicos,
                                           materiales=diccionarioMaterialesArray)
            else:
                pipeline = [{'$lookup': {
                    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'patatita'}
                }, {'$lookup': {
                    'from': 'material', 'localField': 'material_ID', 'foreignField': '_id', 'as': 'tomatito'}
                }
                ]
                arrTemp = []
                for doc in (mongo.db.materialesTecnico.aggregate(pipeline)):
                    arrTemp.append(doc)
                tempID = session['tecnicoID']
                tempID = ObjectId(tempID)
                diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo','_id':tempID })
                diccionarioMateriales = mongo.db.material.find({})
                diccionarioMaterialesArray = []
                for element in diccionarioMateriales:
                    diccionarioMaterialesArray.append([element["nombre"], str(element["_id"])])


                return render_template("materialestecnico.html", diccRela=arrTemp, tecnicos=diccionarioTecnicos,
                                       materiales=diccionarioMaterialesArray)


    else:
        return redirect(url_for('home_page'))



@app.route('/inventarios/agregarInventario',methods=['GET', 'POST'])
def agregarInventario():
    if 'username' in session:
        if request.method == 'POST':
            tecnico_id = request.form.get("tecnico_id")
            tecnico_id = ObjectId(tecnico_id)
            material_id = request.form.get("material_id")
            material_id = ObjectId(material_id)
            cantidad = int(request.form.get("cantidad"))

            relExistente = mongo.db.materialesTecnico.find_one({'material_ID': material_id, 'tecnico_ID': tecnico_id})
            if relExistente is None:
                mongo.db.materialesTecnico.insert_one({'material_ID': material_id, 'tecnico_ID': tecnico_id,
                                                       'cantidad': cantidad})
            else:
                mongo.db.materialesTecnico.update_one({'_id': relExistente['_id']},
                                                      {"$set": {'cantidad': cantidad+relExistente['cantidad']}})
            return redirect(url_for('inventario'))
        else:
            pass
    else:
        return redirect(url_for('home_page'))



@app.route('/claves', methods=['GET', 'POST'])
def claves():
    if 'username' in session:
        if request.method == 'POST':
            if request.form["btn"] == "Anadir":
                claveID = request.form.get("claveID")
                claveCodigo = request.form.get("claveCodigo")
                claveConcepto = request.form.get('claveConcepto')
                claveUnidad = request.form.get("claveUnidad")
                clavePrecioUnitario = request.form.get("clavePrecioUnitario")
                clavePrecioUnitarioTecnico = request.form.get("clavePrecioUnitarioTecnico")
                claveDescripcion = request.form.get("claveDescripcion")
                mongo.db.clave.insert_one({'_id': claveID, 'codigo': claveCodigo, 'concepto': claveConcepto,
                                           'unidad': claveUnidad, 'precioUnitario': clavePrecioUnitario,
                                           'precioUnitarioTecnico': clavePrecioUnitarioTecnico,
                                           'descripcion': claveDescripcion})
                return redirect(url_for('claves'))

            elif request.form["btn"] == "Guardar":
                claveID = request.form.get("claveId")
                claveCodigo = request.form.get("claveCodigo")
                claveConcepto = request.form.get('claveConcepto')
                claveUnidad = request.form.get("claveUnidad")
                clavePrecioUnitario = request.form.get("clavePrecioUnitario")
                clavePrecioUnitarioTecnico = request.form.get("clavePrecioUnitarioTecnico")
                claveDescripcion = request.form.get("claveDescripcion")

                mongo.db.clave.update_one({'_id': claveID},
                                          {"$set": {'codigo': claveCodigo, 'concepto': claveConcepto, 'unidad': claveUnidad,
                                                    'precioUnitario': clavePrecioUnitario,
                                                    'precioUnitarioTecnico': clavePrecioUnitarioTecnico,
                                                    'descripcion': claveDescripcion}})
                return redirect(url_for('claves'))
        else:
            diccionarioClaves = mongo.db.clave.find({})
            if (session['tipo'] == "tecnico"):
                return render_template("conceptotecnico.html", claves=diccionarioClaves)
            else:
                return render_template("clave.html", claves=diccionarioClaves)

    else:
        return redirect(url_for('home_page'))



@app.route('/sucursales',methods=['GET','POST'])
def sucursales():
    if 'username' in session:
        if request.method == 'POST':
            sucursalNombre = request.form.get("sucursalNombre")
            sucursalNucleo = request.form.get("sucursalNucleo")
            sucursalDireccion = request.form.get('sucursalDireccion')
            sucursalCoordenadaX = request.form.get("sucursalCoordenadaX")
            sucursalCoordenadaY = request.form.get("sucursalCoordenadaY")
            id = ObjectId()

            mongo.db.sucursal.insert_one({'_id': id, 'nombre': sucursalNombre, 'nucleo': sucursalNucleo,
                                          'direccion': sucursalDireccion, 'coordenadaX': sucursalCoordenadaX,
                                          'coordenadaY': sucursalCoordenadaY})
            return redirect(url_for('sucursales'))
        else:
            diccionarioSucursales = mongo.db.sucursal.find({})
            if (session['tipo'] != "tecnico"):
                return render_template("empresa.html", sucursales=diccionarioSucursales)
            else:
                return redirect(url_for('home_page'))

    else:
        return redirect(url_for('home_page'))

@app.route('/sucursal/editar',methods=['POST'])
def editarSucursal():
    id = request.form.get("id")
    id = ObjectId(id)
    sucursalNombre = request.form.get("sucursalNombre")
    sucursalNucleo = request.form.get("sucursalNucleo")
    sucursalDireccion = request.form.get('sucursalDireccion')
    sucursalCoordenadaX = request.form.get("sucursalCoordenadaX")
    sucursalCoordenadaY = request.form.get("sucursalCoordenadaY")

    mongo.db.sucursal.update_one({'_id': id}, {"$set": {'nombre': sucursalNombre, 'nucleo': sucursalNucleo,
                                                        'direccion': sucursalDireccion,
                                                        'coordenadaX': sucursalCoordenadaX,
                                                        'coordenadaY': sucursalCoordenadaY}})
    return redirect(url_for('sucursales'))


@app.route('/servicios', methods=['GET', 'POST'])
def servicios():
    if 'username' in session:
        if request.method == 'POST':
            if request.form["btn"]=="Anadir":
                servicioSucursalNombre = request.form.get("servicioSucursal")
                servicioSolicitante = request.form.get("servicioSolicitante")
                servicioTicket = request.form.get("servicioTicket")

                servicioTicket= int(servicioTicket)
                servicioTicket= str(servicioTicket)
                servicioPrioridad = request.form.get('servicioPrioridad')
                servicioTipoDeMantenimiento = request.form.get("servicioTipoDeMantenimiento")
                servicioTecnicoNombre = request.form.get("servicioTecnico")
                servicioFechaDeVencimiento = request.form.get("servicioFechaDeVencimiento")

                servicioSucursalId = request.form.get("servicioSucursal")
                servicioSucursalId = ObjectId(servicioSucursalId)

                servicioTecnicoId = request.form.get("servicioTecnico")
                servicioTecnicoId = ObjectId(servicioTecnicoId)

                id = servicioTicket

                mongo.db.servicio.insert_one({'_id': id, 'sucursal_ID': servicioSucursalId, 'presupuesto_ID': None,
                                              'tecnico_ID': servicioTecnicoId, 'ticket': servicioTicket,
                                              'solicitante': servicioSolicitante, 'prioridad': servicioPrioridad,
                                              'tipoDeMantenimiento': servicioTipoDeMantenimiento, 'paginaDeInternet': None,
                                              'autorizacion': None, 'plano': None, 'estatusInterno': 'Pendiente',
                                              'estatusExterno': 'Falta Autorizacion', 'fechaDeCreacion': datetime.datetime.now(),
                                              'fechaDeVencimiento': servicioFechaDeVencimiento, 'HoraInicio': None, 'HoraFin': None,

                                              'fechaHoraInicio': None, 'fechaHoraFin': None, 'descripcionServicio': None,
                                              'solucionServicio': None, 'observacionesServicio': None,
                                              'firmaUsuario:': None, 'croquis': None,
                                              'firmaTecnico': None, 'selloSucursal': None, 'nombreFirmaFM': None,
                                              'collageEvidencia': None,

                                              'cliente': None, 'subtotal': 0, 'total': 0})
                return redirect(url_for('servicios'))
            elif request.form["btn"]=="Guardar":
                conFotoInternet = True
                conFotoAutorizacion = True
                conFotoPlano = True

                servicioSolicitante = request.form.get("servicioSolicitante")
                servicioPrioridad = request.form.get("servicioPrioridad")
                servicioTipoDeMantenimiento = request.form.get("servicioTipoDeMantenimiento")
                servicioFechaDeVencimiento = request.form.get("servicioFechaDeVencimiento")
                servicioSucursalId = request.form.get("servicioSucursal")
                servicioSucursalId = ObjectId(servicioSucursalId)
                servicioTecnicoId = request.form.get("servicioTecnico")
                servicioTecnicoId = ObjectId(servicioTecnicoId)
                servicioEstatusExterno = request.form.get("servicioEstatusExterno")

                servicioId = request.form.get("idticket")

                try:
                    servicioPagaDeInternet = request.files['servicioPaginaDeInternet']
                except:
                    conFotoInternet = False

                try:
                    servicioAutorizacion = request.files['servicioAutorizacion']
                except:
                    conFotoAutorizacion = False

                try:
                    servicioPlano = request.files['servicioPlano']
                except:
                    conFotoPlano = False

                if conFotoInternet:
                    route = '/FotosServicios/PaginasDeInternet/' + servicioId + 'paginaInternet.jpg'
                    dbx.files_upload(servicioPagaDeInternet.read(), route,mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioId}, {"$set": {'paginaDeInternet': url}})
                if conFotoAutorizacion:
                    route = '/FotosServicios/Autorizaciones/' + servicioId + 'autorizacion.jpg'
                    dbx.files_upload(servicioAutorizacion.read(), route,mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioId}, {"$set": {'autorizacion': url}})
                if conFotoPlano:
                    route = '/FotosServicios/Planos/' + servicioId + 'plano.jpg'
                    dbx.files_upload(servicioPlano.read(), route,mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioId}, {"$set": {'plano': url}})

                mongo.db.servicio.update_one({'_id': servicioId},
                                             {"$set": {'solicitante': servicioSolicitante, 'prioridad': servicioPrioridad,
                                                       'tipoDeMantenimiento': servicioTipoDeMantenimiento,
                                                       'fechaDeVencimiento': servicioFechaDeVencimiento,
                                                       'estatusExterno': servicioEstatusExterno,
                                                       'sucursal_ID': servicioSucursalId, "tecnico_ID": servicioTecnicoId}})
                return redirect(url_for('servicios'))
        else:
            if session['tipo'] != "tecnico":
                diccionarioSucursales = mongo.db.sucursal.find({})
                diccionarioTecnicos = mongo.db.tecnico.find({'estado':'Activo'}).sort('nombre', 1)

                pipeline = [{'$lookup': {
                    'from': 'sucursal', 'localField': 'sucursal_ID', 'foreignField': '_id', 'as': 'valsSucursal'}
                }, {'$lookup': {
                    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'valsTecnico'}
                }
                ]

                arrTemp = []
                for doc in (mongo.db.servicio.aggregate(pipeline)):
                    arrTemp.append(doc)

                arrTemp = sorted(arrTemp, key=lambda k: k['fechaDeCreacion'],reverse=True)
                diccionarioSucursalesArray = []
                for element in diccionarioSucursales:
                    diccionarioSucursalesArray.append([element["nombre"], element["_id"]])

                diccionarioTecnicosArray = []
                for element in diccionarioTecnicos:
                    diccionarioTecnicosArray.append([element["nombre"], element["_id"]])

                if (session['tipo'] == "tecnico"):
                    return render_template("serviciotecnico.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray)
                else:
                    return render_template("servicio.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray)

            else:
                diccionarioSucursales = mongo.db.sucursal.find({})
                tempID = ObjectId(session['tecnicoID'])
                diccionarioTecnicos = mongo.db.tecnico.find({'_id': tempID})

                pipeline = [{'$match': {'tecnico_ID': tempID}},{'$lookup': {
                    'from': 'sucursal', 'localField': 'sucursal_ID', 'foreignField': '_id', 'as': 'valsSucursal'}
                }, {'$lookup': {
                    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'valsTecnico'}
                }
                ]

                arrTemp = []
                for doc in (mongo.db.servicio.aggregate(pipeline)):
                    arrTemp.append(doc)

                arrTemp = sorted(arrTemp, key=lambda k: k['fechaDeCreacion'], reverse=True)
                diccionarioSucursalesArray = []
                for element in diccionarioSucursales:
                    diccionarioSucursalesArray.append([element["nombre"], element["_id"]])

                diccionarioTecnicosArray = []
                for element in diccionarioTecnicos:
                    diccionarioTecnicosArray.append([element["nombre"], element["_id"]])

                if (session['tipo'] == "tecnico"):
                    return render_template("serviciotecnico.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray)
                else:
                    return render_template("servicio.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray)

    else:
        return redirect(url_for('home_page'))


@app.route('/empresa',methods=['GET','POST'])
def empresas():
    if 'username' in session:
        if request.method == 'POST':
            sucursalNombre = request.form.get("sucursalNombre")
            sucursalNucleo = request.form.get("sucursalNucleo")
            sucursalDireccion = request.form.get('sucursalDireccion')
            sucursalCoordenadaX = request.form.get("sucursalCoordenadaX")
            sucursalCoordenadaY = request.form.get("sucursalCoordenadaY")
            id = ObjectId()

            mongo.db.sucursal.insert_one({'_id': id, 'nombre': sucursalNombre, 'nucleo': sucursalNucleo,
                                          'direccion': sucursalDireccion, 'coordenadaX': sucursalCoordenadaX,
                                          'coordenadaY': sucursalCoordenadaY})
            return redirect(url_for('empresas'))
        else:
            diccionarioSucursales = mongo.db.sucursal.find({})

            if (session['tipo'] != "tecnico"):
                return render_template("empresa.html", sucursales=diccionarioSucursales)
            else:
                return redirect(url_for('home_page'))

    else:
        return redirect(url_for('home_page'))

@app.route('/reporte',methods=['GET','POST'])
def reportes():
    if 'username' in session:
        if request.method == 'POST':
            if request.form["btn"] == "Anadir":
                servicioID = request.form.get("idOrden")
                servicioFechaInicio = request.form.get("servicioFechaInicio")
                servicioFechaFin = request.form.get("servicioFechaFin")
                servicioDescripcion = request.form.get("servicioDescripcion")
                servicioHoraInicio = request.form.get("servicioHoraInicio")
                servicioHoraFin = request.form.get("servicioHoraFin")
                servicioSolucion = request.form.get("servicioSolucion")
                servicioObservaciones = request.form.get("servicioObservaciones")

                listaClaves = [[]]
                clave1 = request.form.get("clave1")
                cantidad1 = request.form.get("cantidad1")
                cantidad1 = int(cantidad1)
                if clave1 != "nada" and cantidad1 > 0:
                    listaClaves.append([clave1, cantidad1])

                clave2 = request.form.get("clave2")
                cantidad2 = request.form.get("cantidad2")
                cantidad2 = int(cantidad2)
                if clave2 != "nada" and cantidad2 > 0:
                    listaClaves.append([clave2, cantidad2])

                clave3 = request.form.get("clave3")
                cantidad3 = request.form.get("cantidad3")
                cantidad3 = int(cantidad3)
                if clave3 != "nada" and cantidad3 > 0:
                    listaClaves.append([clave3, cantidad3])

                clave4 = request.form.get("clave4")
                cantidad4 = request.form.get("cantidad4")
                cantidad4 = int(cantidad4)
                if clave4 != "nada" and cantidad4 > 0:
                    listaClaves.append([clave4, cantidad4])

                clave5 = request.form.get("clave5")
                cantidad5 = request.form.get("cantidad5")
                cantidad5 = int(cantidad5)
                if clave5 != "nada" and cantidad5 > 0:
                    listaClaves.append([clave5, cantidad5])

                clave6 = request.form.get("clave6")
                cantidad6 = request.form.get("cantidad6")
                cantidad6 = int(cantidad6)
                if clave6 != "nada" and cantidad6 > 0:
                    listaClaves.append([clave6, cantidad6])

                conFotoCroquis = True
                conFotoSelloSucursal = True
                conFotoNombreFirmaFM = True
                conFotoCollage = True

                try:
                    servicioCroquis = request.files['servicioCroquis']
                except:
                    conFotoCroquis = False

                try:
                    servicioSelloSucursal = request.files['servicioSelloSucursal']
                except:
                    conFotoSelloSucursal = False

                try:
                    servicioNombreFirmaFM = request.files['servicioNombreFirmaFM']
                except:
                    conFotoNombreFirmaFM = False

                try:
                    servicioCollage = request.files['servicioCollage']
                except:
                    conFotoCollage = False

                if conFotoCroquis:
                    route = '/FotosServicios/Croquis/' + servicioID + 'croquis.jpg'
                    dbx.files_upload(servicioCroquis.read(), route, mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioID}, {"$set": {'croquis': url}})

                if conFotoSelloSucursal:
                    route = '/FotosServicios/FirmasSellos/' + servicioID + 'selloSucursal.jpg'
                    dbx.files_upload(servicioSelloSucursal.read(), route, mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioID}, {"$set": {'selloSucursal': url}})

                if conFotoNombreFirmaFM:
                    route = '/FotosServicios/FirmasSellos/' + servicioID + 'nombreFirmaFM.jpg'
                    dbx.files_upload(servicioNombreFirmaFM.read(), route, mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioID}, {"$set": {'nombreFirmaFM': url}})

                if conFotoCollage:
                    route = '/FotosServicios/FirmasSellos/' + servicioID + 'collage.jpg'
                    dbx.files_upload(servicioCollage.read(), route, mode=dropbox.files.WriteMode.overwrite)
                    link = dbx.sharing_create_shared_link(route).url
                    url = list(link)
                    url[-1] = '1'
                    url = ''.join(url)
                    mongo.db.servicio.update_one({'_id': servicioID}, {"$set": {'collageEvidencia': url}})

                print(servicioID)
                mongo.db.servicio.update_one({'_id': servicioID},
                                             {"$set": {'fechaHoraInicio': servicioFechaInicio,
                                                       'fechaHoraFin': servicioFechaFin,
                                                       'descripcionServicio': servicioDescripcion,
                                                       'solucionServicio': servicioSolucion,
                                                       'observacionesServicio': servicioObservaciones,
                                                       'HoraInicio': servicioHoraInicio,
                                                       'HoraFin': servicioHoraFin}})
                mongo.db.servicio.update_one({'_id': servicioID},
                                             {"$set": {'conceptos': listaClaves}})
                return redirect(url_for('reportes'))
            # PDFS
            elif request.form["btn"] == "PDF":
                servicioID = request.form.get("servicioID")
                print(servicioID)
                servicio = mongo.db.servicio.find_one({'_id': servicioID})
                tecnico = mongo.db.tecnico.find_one({'_id': servicio['tecnico_ID']})
                sucursal = mongo.db.sucursal.find_one({'_id': servicio['sucursal_ID']})
                conceptosPDF = []
                for i in range (1,len(servicio['conceptos'])):
                    conceptosPDF.append(mongo.db.clave.find_one({'_id': servicio['conceptos'][i][0]}))

                # Crear buffer para el pdf
                bufferPDF = io.BytesIO()

                # c = canvas.Canvas("PDF_" + servicioID +".pdf")
                c = canvas.Canvas(bufferPDF)


                #PAGINA 1
                c.drawImage("TemplatePDF.png", 0, 0, width=580, height=830)
                c.drawString(77, 723, sucursal['nombre'])
                c.drawString(77, 668, str(servicio['fechaDeCreacion']))
                #falta el cruce

                #PAGINA 2
                subtotal = 0.0
                x = 0
                for concepto in conceptosPDF:
                    c.drawString(20, 610 - 20 * x, concepto['codigo'])
                    c.drawString(77, 610 - 20 * x, concepto['concepto'])
                    c.drawString(350, 610 - 20 * x, concepto['unidad'])
                    c.drawString(400, 610 - 20 * x, str(servicio['conceptos'][x+1][1]))
                    c.drawString(445, 610 - 20 * x, "$"+concepto['precioUnitario'])
                    c.drawString(497, 610 - 20 * x, "$"+str(servicio['conceptos'][x+1][1] * float(concepto['precioUnitario'])))
                    subtotal += servicio['conceptos'][x + 1][1] * float(concepto['precioUnitario'])
                    x = x+1

                total = subtotal + subtotal * 0.16
                c.drawString(497, 95, str(subtotal))
                c.drawString(497, 75, str(subtotal * 0.16))
                c.drawString(497, 55, str(total))
                # PAGINA 2
                c.showPage()
                c.drawImage("TemplatePDF_Croquis1.0.png", 0, 0, width=580, height=830)
                c.drawString(115, 755, servicioID)

                x = 0

                for concepto in conceptosPDF:
                    c.drawString(33, 710 - 15 * x, concepto['codigo'])
                    c.drawString(93, 710 - 15 * x, concepto['descripcion'])

                    c.drawString(33, 600 - 20 * x, concepto['unidad'])
                    c.drawString(270, 600 - 20 * x, str(x) + " cm")
                    c.drawString(325, 600 - 20 * x, str(x) + " cm")
                    c.drawString(375, 600 - 20 * x, str(x) + " cm")
                    c.drawString(420, 600 - 20 * x, str(servicio['conceptos'][x+1][1]))
                    c.drawString(480, 600 - 20 * x, "$"+str(servicio['conceptos'][x+1][1] *
                                                            float(concepto['precioUnitario'])))

                    x = x+1



                # subir los totales a mongo
                mongo.db.servicio.update_one({'_id': servicioID},
                                             {"$set": {'subtotal': subtotal, 'total': total}})

                # croquis
                try:
                    file_bytes = io.BytesIO()
                    metadata, res = dbx.files_download("/FotosServicios/Croquis/" + servicioID + "croquis.jpg")
                    file_bytes.write(res.content)
                    img = ImageReader(file_bytes)
                    c.drawImage(img, 33, 90, width=500, height=360)
                except:
                    return "No hay croquis"

                # PAGINA 3
                c.showPage()
                c.drawImage("TemplatePDF_Croquis1.0.png", 0, 0, width=580, height=830)
                c.drawString(115, 755, servicioID)

                x = 0
                for concepto in conceptosPDF:
                    c.drawString(33, 710 - 15 * x, concepto['codigo'])
                    c.drawString(93, 710 - 15 * x, concepto['descripcion'])

                    c.drawString(33, 600 - 20 * x, concepto['unidad'])
                    c.drawString(270, 600 - 20 * x, str(x) + " cm")
                    c.drawString(325, 600 - 20 * x, str(x) + " cm")
                    c.drawString(375, 600 - 20 * x, str(x) + " cm")
                    c.drawString(420, 600 - 20 * x, str(servicio['conceptos'][x + 1][1]))
                    c.drawString(480, 600 - 20 * x,
                                 "$" + str(servicio['conceptos'][x + 1][1] * float(concepto['precioUnitario'])))
                    x = x+1
                # collage evidencia
                try:
                    file_bytes = io.BytesIO()
                    metadata, res = dbx.files_download("/FotosServicios/FirmasSellos/" + servicioID + "collage.jpg")
                    file_bytes.write(res.content)
                    img = ImageReader(file_bytes)
                    c.drawImage(img, 33, 90, width=500, height=360)
                except:
                    return "No hay collage"

                c.drawString(490, 65, "TOTAL")

                # PAGINA 4
                c.showPage()
                # whatsapp
                try:
                    file_bytes = io.BytesIO()
                    metadata, res = dbx.files_download("/FotosServicios/Autorizaciones/" + servicioID + "autorizacion.jpg")
                    file_bytes.write(res.content)
                    img = ImageReader(file_bytes)
                    c.drawImage(img, 20, 20, width=550, height=800)
                except:
                    return "No hay autorizacion"

                # PAGINA 5
                c.showPage()
                # pagina de Internet
                try:
                    file_bytes = io.BytesIO()
                    metadata, res = dbx.files_download("/FotosServicios/PaginasDeInternet/" + servicioID + "paginaInternet.jpg")
                    file_bytes.write(res.content)
                    img = ImageReader(file_bytes)
                    c.drawImage(img, 20, 20, width=550, height=800)
                except:
                    return "No hay fotografia de Pagina de Internet"
                c.save()

                #Reiniciar Posicio del BufferPDF
                bufferPDF.seek(io.SEEK_SET)

                #Subir PDF a Dropbox
                route = '/PDFServicios/' + servicioID + '.pdf'
                dbx.files_upload(bufferPDF.read(), route, mode=dropbox.files.WriteMode.overwrite)
                link = dbx.sharing_create_shared_link(route).url
                url = list(link)
                url[-1] = '1'
                url = ''.join(url)
                mongo.db.servicio.update_one({'_id': servicioID}, {"$set": {'pdf': url}})
                return redirect(url, code=302)

        else:
            if session['tipo'] != "tecnico":
                diccionarioSucursales = mongo.db.sucursal.find({})
                diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo'}).sort('nombre', 1)
                diccionarioClaves = mongo.db.clave.find({})

                pipeline = [{'$lookup': {
                    'from': 'sucursal', 'localField': 'sucursal_ID', 'foreignField': '_id', 'as': 'valsSucursal'}
                }, {'$lookup': {
                    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'valsTecnico'}
                }
                ]

                arrTemp = []
                for doc in (mongo.db.servicio.aggregate(pipeline)):
                    arrTemp.append(doc)

                arrTemp = sorted(arrTemp, key=lambda k: k['fechaDeCreacion'], reverse=True)
                diccionarioSucursalesArray = []
                for element in diccionarioSucursales:
                    diccionarioSucursalesArray.append([element["nombre"], element["_id"]])

                diccionarioTecnicosArray = []
                for element in diccionarioTecnicos:
                    diccionarioTecnicosArray.append([element["nombre"], element["_id"]])

                diccionarioClavesArray = []
                for element in diccionarioClaves:
                    diccionarioClavesArray.append([element["_id"], element["codigo"], element["concepto"]])

                if (session['tipo'] == "tecnico"):
                    return render_template("reportetecnico.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray, claves=diccionarioClavesArray)
                else:
                    return render_template("reporte.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray, claves=diccionarioClavesArray)


            else:
                diccionarioSucursales = mongo.db.sucursal.find({})
                diccionarioClaves = mongo.db.clave.find({})
                tempID = ObjectId(session['tecnicoID'])
                diccionarioTecnicos = mongo.db.tecnico.find({'_id': tempID})

                pipeline = [{'$match': {'tecnico_ID': tempID}}, {'$lookup': {
                    'from': 'sucursal', 'localField': 'sucursal_ID', 'foreignField': '_id', 'as': 'valsSucursal'}
                }, {'$lookup': {
                    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'valsTecnico'}
                            }
                            ]

                arrTemp = []
                for doc in (mongo.db.servicio.aggregate(pipeline)):
                    arrTemp.append(doc)


                arrTemp = sorted(arrTemp, key=lambda k: k['fechaDeCreacion'], reverse=True)
                diccionarioSucursalesArray = []
                for element in diccionarioSucursales:
                    diccionarioSucursalesArray.append([element["nombre"], element["_id"]])

                diccionarioTecnicosArray = []
                for element in diccionarioTecnicos:
                    diccionarioTecnicosArray.append([element["nombre"], element["_id"]])

                diccionarioClavesArray = []
                for element in diccionarioClaves:
                    diccionarioClavesArray.append([element["_id"], element["codigo"], element["concepto"]])

                if (session['tipo'] == "tecnico"):
                    return render_template("reportetecnico.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray, claves=diccionarioClavesArray)
                else:
                    return render_template("reporte.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                           tecnicos=diccionarioTecnicosArray, claves=diccionarioClavesArray)

    else:
        return redirect(url_for('home_page'))

@app.route('/nomina',methods=['GET','POST'])
def nominas():
    if 'username' in session:
        if request.method == 'POST':
            metaData = mongo.db.nominaMetaData.find_one({})
            diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo'})
            nuevaFecha = datetime.datetime.now()
            for tecnico in diccionarioTecnicos:

                pipeline = [{'$match': {'tecnico_ID': tecnico['_id'] }}]

                diccionarioServicios = []
                arrayTemp=[]
                total = 0

                for doc in (mongo.db.servicio.aggregate(pipeline)):

                    if datetime.datetime.strptime(doc['fechaHoraFin'], '%Y-%m-%d') > metaData['fecha']:
                        diccionarioServicios.append(doc)
                        subtotal = 0
                        for i in range(1,len(doc['conceptos'])):
                            conTemp = mongo.db.clave.find_one({'_id':doc['conceptos'][i][0]})
                            subtotal = subtotal+float(conTemp['precioUnitarioTecnico'])
                        total = total+subtotal
                        arrayTemp.append([doc['_id'], subtotal])


                mongo.db.nominas.insert_one({'tecnico_ID': tecnico['_id'], 'total': total, 'detalles': arrayTemp,
                                             'fecha': nuevaFecha})


            mongo.db.nominaMetaData.update_one({'_id': metaData['_id']}, {"$set": {'fecha':nuevaFecha}})
            return redirect(url_for('nominas'))
        else:
            diccionarioNominas = []
            metaData = mongo.db.nominaMetaData.find_one({})
            for doc in (mongo.db.nominas.find({})):
                if doc['fecha'] > metaData['fecha']:
                    diccionarioNominas.append(doc)

            diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo'})
            diccionarioTecnicosArray = []
            for doc in diccionarioTecnicos:
                diccionarioTecnicosArray.append(doc)
            if (session['tipo'] == "tecnico"):
                tempID = session['tecnicoID']
                tempID = ObjectId(tempID)
                diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo', '_id': tempID})
                diccionarioTecnicosArray = []
                for doc in diccionarioTecnicos:
                    diccionarioTecnicosArray.append(doc)
                return render_template("nominatecnico.html", tecnicos=diccionarioTecnicosArray, nominas=diccionarioNominas, fecha=metaData['fecha'])
            else:
                return render_template("nomina.html", tecnicos=diccionarioTecnicosArray, nominas=diccionarioNominas, fecha=metaData['fecha'])

    else:
        return redirect(url_for('home_page'))


@app.route('/usuarios',methods=['GET','POST'])
def usuarios():
    if 'username' in session:
        if request.method == 'POST':
            nombreDeUsuario = request.form.get("usn")
            contrasena = request.form.get("psw")
            tipo = request.form.get("tipoDeUsuario")
            if (tipo == "admin"):
                mongo.db.usuarios.insert_one({'nombre': nombreDeUsuario, 'contrasena': contrasena, 'tipo': "admin", 'tecnicoID': "None"})
            elif (tipo == "tecnic"):
                tecnicoID = request.form.get("tecnicoID")
                tecnicoID = ObjectId(tecnicoID)
                mongo.db.usuarios.insert_one({'nombre': nombreDeUsuario, 'contrasena': contrasena, 'tipo': "tecnico", 'tecnicoID': tecnicoID})

            return redirect(url_for('usuarios'))
        else:
            diccionarioTecnicos = mongo.db.tecnico.find({'estado': 'Activo'})

            if (session['tipo'] == "superadmin"):
                return render_template("usuario.html", tecnicos = diccionarioTecnicos)
            else:
                return redirect(url_for('home_page'))

    else:
        return redirect(url_for('home_page'))