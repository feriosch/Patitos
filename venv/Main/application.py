from flask import Flask,render_template,request
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
            return "Que pendejo eres"
    else:
        return render_template("index.html")


@app.route('/tu',methods=['POST'])
def checar():
    return "HOLA K ASE OTRA VEZ"

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
        dbx.files_upload(tecnicoFoto.read(),route)
        link = dbx.sharing_create_shared_link(route).url
        url = list(link)
        url[-1] = '1'
        url = ''.join(url)

        mongo.db.tecnico.insert_one({'_id':id,'nombre':tecnicoNombre,'fechaDeNacimiento':tecnicoNacimiento,
                                     'telefono':tecnicoTelefono,'foto':url,'estado':'Activo'})

        diccionarioTecnicos = mongo.db.tecnico.find({})
        return render_template("tecnico.html",tecnicos=diccionarioTecnicos)
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

    diccionarioTecnicos = mongo.db.tecnico.find({})
    return render_template("tecnico.html", tecnicos=diccionarioTecnicos)

