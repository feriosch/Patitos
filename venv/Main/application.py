from flask import Flask,render_template,request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import dropbox
import datetime

dbx = dropbox.Dropbox("uLQxcVq_gSAAAAAAAAAADX50ce1j-fy3qtTAb9ricooFDS1GFb5zv7sk_nnI4DMR")

app = Flask(__name__)
app.secret_key = "ElPatatota"
app.config["MONGO_URI"] =  "mongodb+srv://Master:CiscoCLass@ssei-bwmef.mongodb.net/test?retryWrites=true"
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
            return render_template("home.html")
        else:
            return "Not found"

    else:
        session.pop('username',None)
        return render_template("index.html")


@app.route('/view/<imagen>')
def visualizarImagenes(imagen):
    return render_template("visual.html", imagen)


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
                    return render_template("material.html", materiales=diccionarioMateriales, materialExiste=True)
                diccionarioMateriales = mongo.db.material.find({})
                return render_template("material.html", materiales=diccionarioMateriales)

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
            return render_template("tecnico.html", tecnicos=diccionarioTecnicos)
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
            print(diccionarioMaterialesArray)

            return render_template("inventarios.html", diccRela=arrTemp, tecnicos=diccionarioTecnicos,
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
            print(material_id)
            material_id = ObjectId(material_id)
            print(material_id)
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
            return render_template("sucursal.html", sucursales=diccionarioSucursales)
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
                                              'estatusExterno': 'Pendiente', 'fechaDeCreacion': datetime.datetime.now(),
                                              'fechaDeVencimiento': servicioFechaDeVencimiento})
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
            # NOTA: Tenemos que llamar los servicios por orden inverso
            diccionarioSucursales = mongo.db.sucursal.find({})
            diccionarioTecnicos = mongo.db.tecnico.find({'estado':'Activo'}).sort('nombre', 1)

            pipeline = [{'$lookup': {
                'from': 'sucursal', 'localField': 'sucursal_ID', 'foreignField': '_id', 'as': 'valsSucursal'}
            }, {'$lookup': {
                'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as': 'valsTecnico'}
            }
                # hay que sortear la pipeline
            ]

            arrTemp = []
            for doc in (mongo.db.servicio.aggregate(pipeline)):
                arrTemp.append(doc)

            diccionarioSucursalesArray = []
            for element in diccionarioSucursales:
                diccionarioSucursalesArray.append([element["nombre"], element["_id"]])

            diccionarioTecnicosArray = []
            for element in diccionarioTecnicos:
                diccionarioTecnicosArray.append([element["nombre"], element["_id"]])


            return render_template("servicio.html", servicios=arrTemp, sucursales=diccionarioSucursalesArray,
                                   tecnicos=diccionarioTecnicosArray)
    else:
        return render_template("index.html")


@app.route('/empresa',methods=['GET','POST'])
def empresas():
    return render_template("empresa.html")

@app.route('/reporte',methods=['GET','POST'])
def reportes():
    return render_template("reporte.html")

@app.route('/nomina',methods=['GET','POST'])
def nominas():
    return render_template("nomina.html")

