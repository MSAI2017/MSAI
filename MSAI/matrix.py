# coding: utf-8

import os
import shutil
import subprocess
from utils import Utils

class Matrix(object):
    """Variables"""
    dir_matrix = ''
    dir_models = ''
    list_dir_matrix = []
    list_matrix = []
    my_utility = ''

    """Fonctions"""
    def __init__(self):
        self.my_utility = Utils()
        self.dir_matrix = os.path.join(self.my_utility.dir_path, "matrices")
        self.dir_models = os.path.join(self.my_utility.dir_path, "models")

        if not os.path.exists(self.dir_matrix):
            os.makedirs(self.dir_matrix)
        if not os.path.exists(self.dir_models):
            os.makedirs(self.dir_models)

        #A Supprimer des que list_matrix sera fonctionnel dans /test, POST
        self.face = os.path.join(self.dir_models, 'haarcascade_frontalface_default.xml')
        self.eye = os.path.join(self.dir_models, 'haarcascade_eye.xml')

        self.UpdateDirectoryMatrix()
        self.UpdateMatrix()


    def generate(self, name_matrix):
        """
        Permet de lancer la génération de la matrice name_matrix.
        """
        if name_matrix == '' or name_matrix is None:
            message_create_matrix = "Erreur, vous n'avez pas selectionné de matrice !"
            color_status_matrix = "alert alert-danger"
        elif os.path.isfile(os.path.join(self.dir_models, name_matrix+"_classifier.xml")):
            message_create_matrix = "La matrice " + name_matrix + " a déjà été generé !"
            color_status_matrix = "alert alert-danger"
        else:
            current_matrix = os.path.join(self.dir_matrix, name_matrix)
            cmd="ps -aef | grep generate_matrice_"+name_matrix+" | grep -v grep | wc -l"
            #cmd = "ps -aef | grep generate_matrice | grep -v grep | wc -l"
            in_progress = subprocess.check_output([cmd], shell=True)
            print "test :"+format(in_progress)
            print in_progress==format(0)
            print "test"
            if format(in_progress) >= 1:
                #print format(in_progress)>0
                message_create_matrix = "La matrice "+name_matrix+" est déjà cours de génération. "
                color_status_matrix = "alert alert-danger"
            else:
                dir_script = os.path.abspath(self.my_utility.dir_path + "/doMatrice/screen.sh")
                os.chmod(dir_script, 0777)
                #Obliger d'utiliser une "," pour passer les paramètres (on passe le chemin pour generate)
                subprocess.call(['. ' + dir_script, current_matrix, name_matrix], shell=True)
                print "blablalba"
                message_create_matrix = "La matrice est désormais cours de génération, vous pouvez consulter son avancement par le check."
                color_status_matrix = "alert alert-success"
        return message_create_matrix, color_status_matrix

    def status(self, name_matrix):
        """
        Permet de check le statut de génération d'une matrice.
        """
        #il faut regarder le repertoire classifier de la matrice
        classifier_matrix = os.path.join(self.dir_matrix, name_matrix+"/classifier")
        matrix_path = os.path.join(self.dir_matrix, name_matrix)
        if os.path.isfile(classifier_matrix + "/cascade.xml"):
            result = "La génération de la matrice "+ name_matrix +" est terminé"
        else:
            result = "Aucune génération en cours pour la matrice "+name_matrix
            #commande pour recuperer si un proc generate_matrice est en marche
            #cmd="ps -aef | grep generate_matrice_"+name_matrix+" | grep -v grep | wc -l"
            cmd = "ps -aef | grep generate_matrice | grep -v grep | wc -l"
            in_progress = subprocess.check_output([cmd], shell=True)
            if format(in_progress) >= 1:
                result = "La matrice "+name_matrix+" est en cours de génération. "
                i = 19
                fin = False
                while (i >= 0 and fin is False):
                    if os.path.isfile(classifier_matrix + "/stage"+str(i)+".xml"):
                        fin = True
                        result = result + os.linesep +"Génération en cours : étape "+str(i)+"/19"
                    i = i-1
                if fin is False:
                    result = result + os.linesep + "Génération en cours : étape 0/19"
        return result

    def AddDirectoryMatrix(self, name_matrix):
        message_create_matrix = ''
        color_status_matrix = ''

        if name_matrix == '' or name_matrix is None:
            message_create_matrix = "Erreur, vous n'avez pas nommée la matrice à créer !"
            color_status_matrix = "alert alert-danger"
        elif os.path.isdir(os.path.join(self.dir_matrix, name_matrix)) == True :
            message_create_matrix = "Erreur, la matrice " + name_matrix + " existe déjà !"
            color_status_matrix = "alert alert-danger"
        else :
            os.mkdir(os.path.join(self.dir_matrix, name_matrix))
            os.mkdir(os.path.abspath(self.dir_matrix + '/' + name_matrix + '/' + "positive_img"))
            os.mkdir(os.path.abspath(self.dir_matrix + '/' + name_matrix + '/' + "negative_img"))
            os.mkdir(os.path.abspath(self.dir_matrix + '/' + name_matrix + '/' + "classifier"))
            os.mkdir(os.path.abspath(self.dir_matrix + '/' + name_matrix + '/' + "samples"))

            message_create_matrix = "La matrice a bien été créée."
            color_status_matrix = "alert alert-success"
        return message_create_matrix, color_status_matrix

    def UpdateDirectoryMatrix(self):
        """Actualisation de la liste des répertoires de matrice"""
        self.list_dir_matrix = []
        dirs = os.listdir(self.dir_matrix)
        for dir in dirs:
            if os.path.isdir(os.path.join(self.dir_matrix, dir)):
                #juste pour les test
                #if dir!='balle':
                self.list_dir_matrix.append(dir)
        return self.list_dir_matrix

    def DeleteDirectoryMatrix(self, name_matrix):
        message_delete_matrix = ''
        color_status_matrix = ''

        if name_matrix == '' or name_matrix is None :
            message_delete_matrix = 'Erreur, le nom de la matrice est vide !'
            color_status_matrix = "alert alert-danger"
        elif os.path.isdir(os.path.join(self.dir_matrix, name_matrix)) == False :
            message_delete_matrix = 'Erreur, le répertoire de la matrice' + name_matrix + ' est introuvable !'
            color_status_matrix = "alert alert-danger"
        else :
            shutil.rmtree(os.path.join(self.dir_matrix, name_matrix))
            message_delete_matrix = 'Le répertoire de la matrice ' + name_matrix + ' a bien été supprimé.'
            color_status_matrix = "alert alert-success"
        return message_delete_matrix, color_status_matrix

    def UpdateMatrix(self):
        """Actualisation de la liste des matrices"""
        self.list_matrix = []
        files = os.listdir(self.dir_models)
        for file in files:
            full_file = os.path.join(self.dir_models, file)
            if os.path.isfile(full_file):
                self.list_matrix.append(full_file)
        return self.list_matrix
