from flask import Flask,render_template,request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import dropbox

dbx = dropbox.Dropbox("uLQxcVq_gSAAAAAAAAAADX50ce1j-fy3qtTAb9ricooFDS1GFb5zv7sk_nnI4DMR")

app = Flask(__name__)
app.config["MONGO_URI"] =  "mongodb+srv://Master:CiscoCLass@ssei-bwmef.mongodb.net/test?retryWrites=true"
mongo = PyMongo(app)

@app.route('/',methods=['GET','POST'])
def home_page():
    if request.method == 'POST':
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")
        usuarioPrueba = mongo.db.usuarios.find_one({'nombre':usuario,'contrasena':contrasena})
        if(usuarioPrueba!=None):
            return render_template("home.html")
        else:
            return "Not found"

    else:
        return render_template("index.html")

@app.route('/material/editar',methods=['GET','POST'])
def editarMaterial():
    materialExiste = False
    materialNombre = request.form.get("materialNombre")
    materialDescripcion = request.form.get("materialDescripcion")
    flag = mongo.db.material.find_one({'nombre': materialNombre})
    id = request.form.get("id")
    id = ObjectId(id)
    if flag == None:
        print(type(id))
        mongo.db.material.update_one({'_id': id},
                                     {"$set": {'nombre': materialNombre, 'descripcion': materialDescripcion}})
        diccionarioMateriales = mongo.db.material.find({})
        return render_template("material.html", materiales=diccionarioMateriales)
    else:
        if flag['_id'] == id:
            mongo.db.material.update_one({'_id': id},
                                         {"$set": {'nombre': materialNombre, 'descripcion': materialDescripcion}})
            diccionarioMateriales = mongo.db.material.find({})
            return render_template("material.html", materiales=diccionarioMateriales)
        diccionarioMateriales = mongo.db.material.find({})
        return render_template("material.html", materiales=diccionarioMateriales, materialExiste=True)


@app.route('/material',methods=['GET','POST'])
def materiales():
    materialExiste = False
    if request.method == 'POST':
        materialNombre = request.form.get("materialNombre")
        materialDescripcion = request.form.get("materialDescripcion")
        flag = mongo.db.material.find_one({'nombre': materialNombre})

        if flag == None:
            mongo.db.material.insert_one({'nombre':materialNombre,'descripcion':materialDescripcion})
        else:
            diccionarioMateriales = mongo.db.material.find({})
            return render_template("material.html", materiales=diccionarioMateriales, materialExiste=True)
        diccionarioMateriales = mongo.db.material.find({})
        return render_template("material.html",materiales=diccionarioMateriales)
    else:
        diccionarioMateriales = mongo.db.material.find({})
        return render_template("material.html",materiales=diccionarioMateriales)

@app.route('/material/eliminar',methods=['GET','POST'])
def eliminarMaterial():
    id = request.form.get("id")
    id = ObjectId(id)
    mongo.db.material.delete_one({'_id': id})
    diccionarioMateriales = mongo.db.material.find({})
    return render_template("material.html", materiales=diccionarioMateriales)

@app.route('/tecnico',methods=['GET','POST'])
def tecnico():
    if request.method == 'POST':
        tecnicoNombre = request.form.get("tecnicoNombre")
        tecnicoFoto = request.files['tecnicoFoto']
        tecnicoNacimiento = request.form.get("tecnicoNacimiento")
        tecnicoTelefono = request.form.get("tecnicoTelefono")

        #Aqui se tiene que subir la foto a Dropbox
        id = ObjectId()
        idString = str(id)
        route = '/FotosTecnicos/'+idString+'.jpg'
        dbx.files_upload(tecnicoFoto.read(), route)
        link = dbx.sharing_create_shared_link(route).url
        url = list(link)
        url[-1] = '1'
        url = ''.join(url)

        mongo.db.tecnico.insert_one({'_id':id,'nombre':tecnicoNombre,'fechaDeNacimiento':tecnicoNacimiento,
                                     'telefono':tecnicoTelefono,'foto':url,'estado':'Activo'})

        return redirect(url_for('tecnico'))
    else:
        diccionarioTecnicos = mongo.db.tecnico.find({})
        return render_template("tecnico.html", tecnicos=diccionarioTecnicos)

@app.route('/tecnico/editar',methods=['GET','POST'])
def editarTecnico():
    tecnicoNombre = request.form.get("tecnicoNombre")
    tecnicoFoto = request.files['tecnicoFoto']
    tecnicoNacimiento = request.form.get("tecnicoNacimiento")
    tecnicoTelefono = request.form.get("tecnicoTelefono")

    id = request.form.get("id")

    route = '/FotosTecnicos/' + id + '.jpg'
    dbx.files_upload(tecnicoFoto.read(), route,mode=dropbox.files.WriteMode.overwrite)
    link = dbx.sharing_create_shared_link(route).url
    url = list(link)
    url[-1] = '1'
    url = ''.join(url)

    id = ObjectId(id)

    mongo.db.tecnico.update_one({'_id': id},
                                    {"$set": {'nombre':tecnicoNombre,'fechaDeNacimiento':tecnicoNacimiento,
                                    'telefono':tecnicoTelefono,'foto':url,'estado':'Activo'}})

    return redirect(url_for('tecnico'))

@app.route('/tecnico/desactivar',methods=['GET','POST'])
def desactivarTecnico():
    id = request.form.get("id")
    id = ObjectId(id)
    mongo.db.tecnico.update_one({'_id': id},{"$set":{'estado':'Desactivado'}})
    return redirect(url_for('tecnico'))

@app.route('/inventarios',methods=['GET','POST'])
def inventario():
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
        print(arrTemp)
        diccionarioTecnicos = mongo.db.tecnico.find({})
        diccionarioMateriales = mongo.db.material.find({})
        diccionarioMaterialesArray = []
        for element in diccionarioMateriales:
            diccionarioMaterialesArray.append([element["nombre"],str(element["_id"])])
        print(diccionarioMaterialesArray)

        return render_template("inventarios.html", diccRela=arrTemp,tecnicos=diccionarioTecnicos,materiales=diccionarioMaterialesArray)

@app.route('/inventarios/agregarInventario',methods=['GET','POST'])
def agregarInventario():
    if request.method == 'POST':
        tecnico_id = request.form.get("tecnico_id")
        tecnico_id = ObjectId(tecnico_id)
        material_id = request.form.get("material_id")
        print(material_id)
        material_id = ObjectId(material_id)
        print(material_id)
        cantidad = int(request.form.get("cantidad"))

        relExistente = mongo.db.materialesTecnico.find_one({'material_ID':material_id, 'tecnico_ID':tecnico_id})
        if(relExistente == None):
            mongo.db.materialesTecnico.insert_one({'material_ID':material_id,'tecnico_ID':tecnico_id,'cantidad':cantidad})
        else:
            mongo.db.materialesTecnico.update_one({'_id':relExistente['_id']},{"$set":{'cantidad':cantidad+relExistente
            ['cantidad']}})
        return redirect(url_for('inventario'))

@app.route('/claves',methods=['GET','POST'])
def claves():
    if request.method == 'POST':
        claveID = request.form.get("claveID")
        claveConcepto = request.form.get('claveConcepto')
        claveUnidad = request.form.get("claveUnidad")
        clavePrecioUnitario = request.form.get("clavePrecioUnitario")
        clavePrecioUnitarioTecnico = request.form.get("clavePrecioUnitarioTecnico")
        claveDescripcion = request.form.get("claveDescripcion")

        mongo.db.clave.insert_one({'_id': claveID, 'concepto': claveConcepto, 'unidad': claveUnidad,
                                    'precioUnitario': clavePrecioUnitario, 'precioUnitarioTecnico': clavePrecioUnitarioTecnico,
                                   'descripcion': claveDescripcion})

        return redirect(url_for('claves'))
    else:
        diccionarioClaves = mongo.db.clave.find({})
        return render_template("clave.html", claves=diccionarioClaves)

@app.route('/claves/editar',methods=['GET','POST'])
def editarClave():
    id = request.form.get("id")
    claveConcepto = request.form.get('claveConcepto')
    claveUnidad = request.form.get("claveUnidad")
    clavePrecioUnitario = request.form.get("clavePrecioUnitario")
    clavePrecioUnitarioTecnico = request.form.get("clavePrecioUnitarioTecnico")
    claveDescripcion = request.form.get("claveDescripcion")

    mongo.db.clave.update_one({'_id': id},
                                    {"$set": {'concepto':claveConcepto,'unidad':claveUnidad,
                                    'precioUnitario':clavePrecioUnitario,
                                    'precioUnitarioTecnico':clavePrecioUnitarioTecnico,
                                    'descripcion':claveDescripcion}})

    return redirect(url_for('claves'))

@app.route('/sucursales',methods=['GET','POST'])
def sucursales():
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

@app.route('/sucursal/editar',methods=['GET','POST'])
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

@app.route('/servicios',methods=['GET','POST'])
def servicios():
    if request.method == 'POST':
        servicioSucursal = request.form.get("servicioSucursal")
        servicioSolicitante = request.form.get("servicioSolicitante")
        servicioPrioridad = request.form.get('servicioPrioridad')
        servicioTipoDeMantenimiento = request.form.get("servicioTipoDeMantenimiento")
        servicioTecnico = request.form.get("servicioTecnico")
        id = ObjectId()

        mongo.db.servicio.insert_one({'_id': id, 'servicio': servicioSucursal, 'solicitante': servicioSolicitante,
                                      'prioridad': servicioPrioridad, 'tipoDeMantenimiento': servicioTipoDeMantenimiento,
                                      'tecnico': servicioTecnico})
        return redirect(url_for('servicios'))
    else:
        diccionarioServicios = mongo.db.servicio.find({})
        return render_template("servicio.html", servicios=diccionarioServicios)


