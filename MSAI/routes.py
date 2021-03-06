# -*- coding: utf-8 -*-

"""
Ce module permet de gérer les routes et vues de l'application MSAI.
"""

from shutil import copyfile
import os
import cv2
from bottle import route, view, request, run, redirect  # pylint: disable=no-name-in-module,unused-import
import bottle
import bottlesession
from utils import Utils
from matrix import Matrix
from database import Database
from emotion import emotionspresent, emotionscount
from objectmatrice import matricepresent

MY_UTILITY = Utils()
MY_MATRIX = Matrix()
MY_DATABASE = Database()
LIST_FILTER = []


SESSION_MANAGER = bottlesession.PickleSession()
SESSION_MANAGER = bottlesession.CookieSession()
VALID_USER = bottlesession.authenticator(SESSION_MANAGER)


@route('/')
@route('/home')
@view('index')
def home():
    """
    Cette fonction nous renvoie vers la page home.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    return dict(title='Accueil',
                user=connected_user,
                role=connected_user_role,
                year=MY_UTILITY.date.year)


@route('/contact')
@view('contact')
def contact():
    """
    Cette fonction nous renvoie vers la page contact.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    return dict(title='Contact',
                user=connected_user,
                role=connected_user_role,
                year=MY_UTILITY.date.year)


@route('/login')
@view('login')
def login():
    """
    Cette fonction nous renvoie vers la page login.
    """
    return dict(title='Login',
                message_connect_user='',
                color_connect_user='',
                year=MY_UTILITY.date.year)


@route('/connect', method='POST')
@view('login')
def connect():
    """
    Permet de se connecter à l'application.
    """
    session = SESSION_MANAGER.get_session()
    user_id = request.POST.dict['inputIdentifiant'][0]
    user_password = request.POST.dict['inputPassword'][0]
    message_connect_user, color_connect_user, connected, user_role = MY_DATABASE.connectionuser(
        user_id, user_password)
    session['valid'] = False

    if connected == 'true':
        session['identifiant'] = user_id
        session['role'] = user_role
        session['valid'] = True
        SESSION_MANAGER.save(session)
        redirect("/home")

    SESSION_MANAGER.save(session)
    return dict(title='Resultat',
                message_connect_user=message_connect_user,
                color_connect_user=color_connect_user)


@route('/main')
@view('main')
def main():
    """
    Cette fonction nous renvoie vers la page home.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    return dict(title='Page accueil',
                user=connected_user,
                role=connected_user_role,
                year=MY_UTILITY.date.year)


@route('/faq')
@view('faq')
def about():
    """
    Cette fonction nous renvoie vers la page FAQ.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    return dict(title='FAQ',
                message='FAQ',
                user=connected_user,
                role=connected_user_role,
                year=MY_UTILITY.date.year)


@route('/manage_users')
@view('manage_users')
def manageusers():
    """
    Affiche le panneau d'administration
    """
    list_user = []
    connected_user, connected_user_role = MY_UTILITY.verificationsession('admin')
    list_user = MY_DATABASE.getuser()

    return dict(title='Management Database',
                color_database_action='',
                message_database_action='',
                user=connected_user,
                role=connected_user_role,
                list_user=list_user,
                year=MY_UTILITY.date.year)


@route('/manage_emotions')
@view('manage_emotions')
def manageemotions():
    """
    Affiche l'onglet émotion
    """
    list_emotion = []
    connected_user, connected_user_role = MY_UTILITY.verificationsession('admin')
    list_emotion = MY_DATABASE.getemotion()

    return dict(title='Management Matrice',
                color_emotion_action='',
                message_emotion_action='',
                user=connected_user,
                role=connected_user_role,
                list_emotion=list_emotion,
                year=MY_UTILITY.date.year)


@route('/handler')
@view('handler')
def handler():
    """
    Cette fonction nous renvoie vers la page handler.
    """
    return dict(title='Erreur',
                message='Erreur Application',
                year=MY_UTILITY.date.year)


@route('/traitement')
@view('traitement')
def test():
    """
    Cette fonction nous renvoie vers la page traitement.
    """
    list_emotion = []
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    list_emotion = MY_DATABASE.getemotion()
    path = MY_MATRIX.dir_matrix
    if not os.path.exists(path):
        os.makedirs(path)
    dirs = os.listdir(path)
    del LIST_FILTER[:]
    for one_dir in dirs:
        if os.path.isfile(os.path.join(MY_MATRIX.dir_models, one_dir + "_classifier.xml")):
            LIST_FILTER.append(one_dir)
    return dict(title='Traitement',
                message='Traitement.',
                file='',
                year=MY_UTILITY.date.year,
                user=connected_user,
                role=connected_user_role,
                list_emotion=list_emotion,
                list_filter=LIST_FILTER)


@route('/traitement', method='POST')
@view('traitement')
def do_upload():
    """
    Cette fonction permet de réaliser le traitement.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    upload = request.files.get('upload')
    file_format = ''
    if not upload:
        return "No file uploaded."
    ext = os.path.splitext(upload.filename)[1]
    if ext in ('.png', '.jpg', '.jpeg', '.gif', '.PNG', '.JPG', '.JPEG', '.GIF'):
        file_format = 'img'
    elif ext in ('.mp4', '.wma', '.avi', '.mov', '.mpg', '.mkv', '.MP4',
                 '.WMA', '.AVI', '.MOV', '.MPG', '.MKV'):
        file_format = 'video'
    else:
        return "File extension not allowed."

    save_path = os.path.abspath(MY_UTILITY.dir_path + '/tmp')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.abspath(save_path + '/' + upload.filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

    upload.save(file_path)

    if file_format == 'img':
        dict_emotion, faces, bmatch, file_save, bmatchmatrice, name_select_matrice, nbmatchmatrice = launchimage(
            file_path, upload.filename)

    elif file_format == 'video':
        dict_emotion, faces, bmatch, file_save, bmatchmatrice, name_select_matrice, nbmatchmatrice = launchvideo(
            file_path, upload.filename)

    return dict(title='Resultat',
                message='Resultat',
                year=MY_UTILITY.date.year,
                file=file_save,
                user=connected_user,
                role=connected_user_role,
                list_filter=LIST_FILTER,
                faces=faces,
                dict_emotion=dict_emotion,
                emotion_all=emotionscount(dict_emotion),
                bmatch=bmatch,
                bmatchmatrice=bmatchmatrice,
                name_select_matrice=name_select_matrice,
                nbmatchmatrice=nbmatchmatrice,
                list_emotion=MY_DATABASE.list_emotion)


@route('/manage_matrix')
@view('manage_matrix')
def manage_matrix():
    """
    Cette fonction nous renvoie vers la page Manage Matrix.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    MY_MATRIX.update_directory_matrix()

    message_check, show_status = MY_MATRIX.status()

    return dict(title='Management Matrice',
                # color_do_matrix='',
                # message_do_matrix='',
                message_check_matrix=message_check,
                show_status=show_status,
                # Gestions des alertes"""
                # Message affiché et couleur de l'alerte - ajout d'une image dans une matrice
                message_add_pic='',
                color_add_pic="vide",
                # Message affiché et couleur de l'alerte - création d'une nouvelle matrice
                message_create_matrix='',
                color_add_matrix='',
                # Message affiché et couleur de l'alerte - supression d'une matrice
                message_delete_matrix='',
                color_suppr_matrix='',
                user=connected_user,
                role=connected_user_role,
                list_matrix=MY_MATRIX.list_dir_matrix,
                year=MY_UTILITY.date.year)


@route('/do_classifier', method='POST')
@view('manage_matrix')
def do_classifier():
    """
    Assignation des 2 valeurs de retour
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    name_matrix = request.POST.dict['select_list_matrix'][0]
    message_do_matrix, color_status_matrix = MY_MATRIX.generate(name_matrix)
    message_check, show_status = MY_MATRIX.status()

    return dict(title='Management Matrice',
                # Gestions des alertes"""
                message_check_matrix=message_check,
                show_status=show_status,
                # Message affiché et couleur de l'alerte - ajout d'une image dans une matrice
                message_add_pic='',
                color_add_pic="vide",
                # Message affiché et couleur de l'alerte - création d'une nouvelle matrice
                message_create_matrix='',
                color_add_matrix='',
                # Message affiché et couleur de l'alerte - supression d'une matrice
                message_delete_matrix='',
                color_suppr_matrix='',
                # Message affiché et couleur de l'alerte - lancement génération matrice
                message_do_matrix=message_do_matrix,
                color_do_matrix=color_status_matrix,
                user=connected_user,
                role=connected_user_role,
                list_matrix=MY_MATRIX.list_dir_matrix,
                year=MY_UTILITY.date.year)


@route('/add_matrix', method='POST')
@view('manage_matrix')
def add_matrix():
    """
    Ajout d'une nouvelle matrice.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    name_matrix = request.POST.dict['name_matrice'][0]
    message_create_matrix = ''
    color_status_matrix = ''

    # Assignation des 2 valeurs de retour
    message_create_matrix, color_status_matrix = MY_MATRIX.add_directory_matrix(
        name_matrix)

    MY_MATRIX.update_directory_matrix()
    message_check, show_status = MY_MATRIX.status()

    return dict(title='Resultat',
                # Gestions des alertes"""
                message_check_matrix=message_check,
                show_status=show_status,
                # Message affiché et couleur de l'alerte - ajout d'une image dans une matrice
                message_add_pic='',
                color_add_pic="vide",
                # Message affiché et couleur de l'alerte - création d'une nouvelle matrice
                message_create_matrix=message_create_matrix,
                color_add_matrix=color_status_matrix,
                # Message affiché et couleur de l'alerte - supression d'une matrice
                message_delete_matrix='',
                color_suppr_matrix='',
                user=connected_user,
                role=connected_user_role,
                list_matrix=MY_MATRIX.list_dir_matrix,
                year=MY_UTILITY.date.year)


@route('/add_pictures', method='POST')
@view('manage_matrix')
def add_pictures():
    """
    Ajout nouvelle image dans la matrice.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    print request.POST.dict
    name_matrix = request.POST.dict['select_list_matrix'][0]
    picture_type = request.POST.dict['typeImage'][0]
    uploads = request.files.getall('upload')

    for upload in uploads:
        ext = os.path.splitext(upload.filename)[1]
        message_add_pic, color_add_pic, filepath = MY_MATRIX.add_object(
            name_matrix, picture_type, ext, upload.filename)

        if color_add_pic == "alert alert-danger":
            break
        else:
            upload.save(filepath)

    MY_MATRIX.update_directory_matrix()
    message_check, show_status = MY_MATRIX.status()

    return dict(title='Resultat',
                # Gestions des alertes"""
                message_check_matrix=message_check,
                show_status=show_status,
                # Message affiché et couleur de l'alerte - ajout d'une image dans une matrice
                message_add_pic=message_add_pic,
                color_add_pic=color_add_pic,
                # Message affiché et couleur de l'alerte - création d'une nouvelle matrice
                message_create_matrix='',
                color_add_matrix='',
                # Message affiché et couleur de l'alerte - supression d'une matrice
                message_delete_matrix='',
                color_suppr_matrix='',
                user=connected_user,
                role=connected_user_role,
                list_matrix=MY_MATRIX.list_dir_matrix,
                year=MY_UTILITY.date.year)


@route('/delete_matrix', method='POST')
@view('manage_matrix')
def delete_matrix():
    """
    Suppression d'une matrice.
    """
    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')
    name_matrix = request.POST.dict['selected_matrix'][0]
    message_delete_matrix = ''
    color_suppr_matrix = ''

    # Assignation des 2 valeurs de retour
    message_delete_matrix, color_suppr_matrix = MY_MATRIX.delete_directory_matrix(
        name_matrix)
    MY_MATRIX.update_directory_matrix()
    message_check, show_status = MY_MATRIX.status()
    return dict(title='Resultat',
                # Gestions des alertes
                message_check_matrix=message_check,
                show_status=show_status,
                # Message affiché et couleur de l'alerte - ajout d'une image dans une matrice
                message_add_pic='',
                color_add_pic='',
                # Message affiché et couleur de l'alerte - création d'une nouvelle matrice
                message_create_matrix='',
                color_add_matrix='',
                # Message affiché et couleur de l'alerte - supression d'une matrice
                message_delete_matrix=message_delete_matrix,
                color_suppr_matrix=color_suppr_matrix,
                user=connected_user,
                role=connected_user_role,
                list_matrix=MY_MATRIX.list_dir_matrix,
                year=MY_UTILITY.date.year)


def launchimage(filepath, filename):
    """
    Cette fonction permet de lancer le traitement image.
    :param filepath: Chemin du fichier
    :param filename: Nom du fichier
    :type filepath: String
    :type filename: String
    :return dict_emotion: Dictionnaire des émotions
    :return faces: Nombre de visages
    :return bmatch: Emotion trouvé
    :return file_save: Nom de fichier sauvegardé
    :return bmatchmatrice: Matrice Objet trouvé
    :return name_select_matrice: Nom Matrice sélectionné
    :return nbmatch: Nombre de match
    :rtype dict_emotion: Dictionnary
    :rtype faces: String
    :rtype bmatch: Boolean
    :rtype file_save: String
    :rtype bmatchmatrice: Boolean
    :rtype name_select_matrice: String
    :rtype nbmatch: Integer
    """
    list_emotion = []
    list_emotion = request.POST.getall('emotion_filter')
    img = cv2.imread(filepath, 1)

    file_save = filename

    if not os.path.exists(os.path.abspath(MY_UTILITY.dir_path + '/static/pictures/')):
        os.makedirs(os.path.abspath(
            MY_UTILITY.dir_path + '/static/pictures/'))
    cv2.imwrite(os.path.abspath(MY_UTILITY.dir_path +
                                '/static/pictures/' + file_save), img)

    source = os.path.abspath(MY_UTILITY.dir_path +
                             '/static/pictures/' + file_save)

    try:
        if cv2.__version__ == '3.1.0':
            fisher_face = cv2.face.createFisherFaceRecognizer()
        else:
            fisher_face = cv2.createFisherFaceRecognizer()
        fisher_face.load('models/emotion_detection_model.xml')
    except AttributeError:
        return redirect("/handler")

    dict_emotion, faces, bmatch = emotionspresent(
        fisher_face, source, list_emotion)

    bmatchmatrice = False
    name_select_matrice = ""
    nbmatch = 0
    if len(request.POST.getall('matrice_filter')) > 0:
        bmatchmatrice, nbmatch = matricepresent(
            source, request.POST.getall('matrice_filter')[0])
        name_select_matrice = request.POST.getall('matrice_filter')[0]

    if os.path.isfile(filepath):
        os.remove(filepath)

    return dict_emotion, faces, bmatch, file_save, bmatchmatrice, name_select_matrice, nbmatch


def launchvideo(filepath, filename):
    """
    Cette fonction permet de lancer le traitement vidéo
    :param filepath: Chemin du fichier
    :param filename: Nom du fichier
    :type filepath: String
    :type filename: String
    :return dict_emotion: Dictionnaire des émotions
    :return faces: Nombre de visages
    :return bmatch: Emotion trouvé
    :return file_save: Nom de fichier sauvegardé
    :return bmatchmatrice: Matrice Objet trouvé
    :return name_select_matrice: Nom Matrice sélectionné
    :return nbmatch: Nombre de match
    :rtype dict_emotion: Dictionnary
    :rtype faces: String
    :rtype bmatch: Boolean
    :rtype file_save: String
    :rtype bmatchmatrice: Boolean
    :rtype name_select_matrice: String
    :rtype nbmatch: Integer
    """
    bmatch = False
    sortie = False
    sortie_emotion = False
    bmatchmatrice = False
    sortie_object = False
    name_select_matrice = ""
    incomplet_result = ""
    incomplet_dict = ""
    incomplet_result_nb_object = 0
    #variable pour le stockage d'une image provisoire lors d'une detection d'un seul élement
    provisoire_img = os.path.abspath(MY_UTILITY.dir_path +
                                     '/static/pictures/provisoire.jpg')
    list_emotion = []
    list_emotion = request.POST.getall('emotion_filter')
    if len(request.POST.getall('matrice_filter')) > 0:
        name_select_matrice = request.POST.getall('matrice_filter')[0]

    base = os.path.basename(filename)
    file_save = os.path.splitext(base)[0] + '.jpg'
    try:
        if cv2.__version__ == '3.1.0':
            fisher_face = cv2.face.createFisherFaceRecognizer()
        else:
            fisher_face = cv2.createFisherFaceRecognizer()
        fisher_face.load('models/emotion_detection_model.xml')
    except AttributeError:
        return redirect('/handler')

    cap = cv2.VideoCapture(filepath)
    if cap.isOpened():
        read_value, img = cap.read()
    else:
        return

    while read_value and not sortie:
        if not os.path.exists(os.path.abspath(MY_UTILITY.dir_path + '/static/pictures/')):
            os.makedirs(os.path.abspath(
                MY_UTILITY.dir_path + '/static/pictures/'))

        cv2.imwrite(os.path.abspath(MY_UTILITY.dir_path +
                                    '/static/pictures/' + file_save), img)

        source = os.path.abspath(MY_UTILITY.dir_path +
                                 '/static/pictures/' + file_save)
        if len(request.POST.getall('emotion_filter')) > 0:
            dict_emotion, faces, bmatch = emotionspresent(
                fisher_face, source, list_emotion)
            sortie_emotion = bool(bmatch)
        else:
            sortie_emotion = True
            dict_emotion = {}
            faces = 0
        nbmatch = 0
        if name_select_matrice != "":
            bmatchmatrice, nbmatch = matricepresent(
                source, name_select_matrice)
            sortie_object = bool(bmatchmatrice)
        else:
            sortie_object = True


        if sortie_emotion is True and sortie_object is True:
            sortie = True
        elif sortie_emotion is True:
            copyfile(source, provisoire_img)
            incomplet_result = 1
            incomplet_result_nb = faces
            incomplet_dict = dict_emotion
        elif sortie_object is True:
            copyfile(source, provisoire_img)
            incomplet_result = 2
            incomplet_result_nb = faces
            incomplet_dict = dict_emotion
            incomplet_result_nb_object = nbmatch

        read_value, img = cap.read()

    if incomplet_result != "" and sortie is False:
        #on copie l'image provisoire vers l'image source (qui est en fin de vidéo)
        copyfile(provisoire_img, source)
        #on réattribue le dernier match
        dict_emotion = incomplet_dict
        faces = incomplet_result_nb
        if incomplet_result == 1:
            bmatch = True
        else:
            bmatchmatrice = True
            nbmatch = incomplet_result_nb_object

    cap.release()
    return dict_emotion, faces, bmatch, file_save, bmatchmatrice, name_select_matrice, nbmatch


@route('/disconnect')
@view('index')
def disconnect():
    """
    Permet de déconnecter l'utilisateur.
    """
    session = SESSION_MANAGER.get_session()
    session['valid'] = False
    SESSION_MANAGER.save(session)
    redirect("/login")
    return dict(title='Resultat',
                message_connect_user='',
                color_connect_user='')


@route('/createUser', method='POST')
@view('manage_users')
def createuser():
    """
    Création d'un utilisateur.
    """
    list_user = []
    message_create_user = ''
    color_create_user = ''

    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')

    user_id = request.POST.dict['inputIdentifiant'][0]
    password_id = request.POST.dict['inputPassword'][0]
    role_id = request.POST.dict['inputRole'][0]

    # Assignation des 2 valeurs de retour
    message_create_user, color_create_user = MY_DATABASE.createuser(
        user_id, password_id, role_id)
    list_user = MY_DATABASE.getuser()

    return dict(title='Resultat',
                # Gestions des alertes
                # Message affiché et couleur de l'alerte - ajout d'un utilisateur
                color_database_action=color_create_user,
                message_database_action=message_create_user,
                user=connected_user,
                role=connected_user_role,
                list_user=list_user,
                year=MY_UTILITY.date.year)


@route('/createEmotion', method='POST')
@view('manage_emotions')
def createemotion():
    """
    Création de la liste des émotions.
    """
    list_emotion = []
    message_create_emotion = ''
    color_create_emotion = ''

    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')

    emotion_intitule = request.POST.dict['inputEmotion'][0]

    # Assignation des 2 valeurs de retour
    message_create_emotion, color_create_emotion = MY_DATABASE.createemotion(
        emotion_intitule)
    list_emotion = MY_DATABASE.getemotion()

    return dict(title='Resultat',
                # Gestions des alertes
                # Message affiché et couleur de l'alerte - ajout d'un utilisateur
                color_emotion_action=color_create_emotion,
                message_emotion_action=message_create_emotion,
                user=connected_user,
                role=connected_user_role,
                list_emotion=list_emotion,
                year=MY_UTILITY.date.year)


@route('/deleteUser', method='POST')
@view('manage_users')
def deleteuser():
    """
    Suppression d'un utilisateur.
    """
    list_user = []
    message_delete_user = ''
    color_delete_user = ''

    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')

    user_id = request.POST.dict['idUser'][0]

    # Assignation des 2 valeurs de retour
    message_delete_user, color_delete_user = MY_DATABASE.deleteuser(user_id)
    list_user = MY_DATABASE.getuser()

    return dict(title='Resultat',
                # Gestions des alertes
                # Message affiché et couleur de l'alerte - ajout d'un utilisateur
                color_database_action=color_delete_user,
                message_database_action=message_delete_user,
                user=connected_user,
                role=connected_user_role,
                list_user=list_user,
                year=MY_UTILITY.date.year)


@route('/deleteEmotion', method='POST')
@view('manage_emotions')
def deleteemotion():
    """
    Suppression de la liste des émotions.
    """
    list_emotion = []
    message_delete_emotion = ''
    color_delete_emotion = ''

    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')

    emotion_id = request.POST.dict['idEmotion'][0]

    # Assignation des 2 valeurs de retour
    message_delete_emotion, color_delete_emotion = MY_DATABASE.deleteemotion(
        emotion_id)
    list_emotion = MY_DATABASE.getemotion()

    return dict(title='Resultat',
                # Gestions des alertes
                # Message affiché et couleur de l'alerte - ajout d'un utilisateur
                color_emotion_action=color_delete_emotion,
                message_emotion_action=message_delete_emotion,
                user=connected_user,
                role=connected_user_role,
                list_emotion=list_emotion,
                year=MY_UTILITY.date.year)


@route('/updateUser', method='POST')
@view('manage_users')
def updateuser():
    """
    Modification d'un utilisateur.
    """
    list_user = []
    message_update_user = ''
    color_update_user = ''

    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')

    user_id = request.POST.dict['idMajUser'][0]
    user_identifiant = request.POST.dict['majIdentifiant'][0]
    user_role = request.POST.dict['majRole'][0]

    # Assignation des 2 valeurs de retour
    message_update_user, color_update_user = MY_DATABASE.updateuser(
        user_id, user_identifiant, user_role)
    list_user = MY_DATABASE.getuser()

    return dict(title='Resultat',
                # Gestions des alertes
                # Message affiché et couleur de l'alerte - ajout d'un utilisateur
                color_database_action=color_update_user,
                message_database_action=message_update_user,
                user=connected_user,
                role=connected_user_role,
                list_user=list_user,
                year=MY_UTILITY.date.year)


@route('/updateEmotion', method='POST')
@view('manage_emotions')
def updateemotion():
    """
    Modification de la liste des émotions.
    """
    list_emotion = []
    message_update_emotion = ''
    color_update_emotion = ''

    connected_user, connected_user_role = MY_UTILITY.verificationsession('user')

    emotion_id = request.POST.dict['idMajEmotion'][0]
    emotion_intitule = request.POST.dict['majEmotion'][0]

    # Assignation des 2 valeurs de retour
    message_update_emotion, color_update_emotion = MY_DATABASE.updateemotion(
        emotion_id, emotion_intitule)
    list_emotion = MY_DATABASE.getemotion()

    return dict(title='Resultat',
                # Gestions des alertes
                # Message affiché et couleur de l'alerte - ajout d'un utilisateur
                color_emotion_action=color_update_emotion,
                message_emotion_action=message_update_emotion,
                user=connected_user,
                role=connected_user_role,
                list_emotion=list_emotion,
                year=MY_UTILITY.date.year)
