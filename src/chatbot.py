from src.functions import *

class Chatbot:

    def __init__(self, database_name, nrows):

        self.step = -1
        self.nrows = nrows
        self.database_name = database_name
        self.question = ""
        self.answer = " "
        self.tf_idf_matrix_offre = 0
        self.word_list = 0
        self.current_nb_offres = 0
        self.liste_offres = []
        self.current_tf_matrix_secteur = 0

        self.database = pd.read_csv(database_name, header=0, encoding="utf8",dtype={"sect": str, "longitude": str, "latitude": str}, nrows=nrows)
        self.database.dropna(subset=["sect"], inplace=True)

        self.current_database = pd.read_csv(database_name, header=0, encoding="utf8", dtype={"sect": str, "longitude": str, "latitude": str}, nrows=nrows)
        self.current_database.dropna(subset=["sect"], inplace=True)

        self.city_gps_base = pd.read_csv("regions.csv", header=0, encoding="utf8", sep = ";")
        self.city_gps_base.index = self.city_gps_base.nom_commune

        self.question_list = ["Cherchez-vous un emploi à temps plein ou à temps partiel ? ",
                              "Quelle est votre ville ?",
                              "Quelle distance êtes-vous prêt à parcourir pour aller travailler en Km?",
                              "Dans quel secteur voulez-vous travailler ?",
                              "Quel emploi cherchez-vous ?",
                              "Voulez-vous lancer une nouvelle recherche ?",
                              "Etes-vous satisfait ?"]

        self.answers_functions = [self.temps,
                                  self.emploi_adresse,
                                  self.emploi_distance,
                                  self.emploi_secteur,
                                  self.emploi]

    def compute_tf_idf(self, database):
        return TF_IDF_matrix(database)

    def temps(self, information):
        info_traitee = quel_temps(information)
        if info_traitee != "#Boloss" :
            self.current_database = self.current_database[self.current_database['tps'] == info_traitee]
            self.step += 1
        else :
            self.answer = "Vous êtes incapable de saisir partiel ou plein ! Essayez encore."

    def emploi_adresse(self, information):
        gps = ville_to_gps(information, self.city_gps_base)
        if gps != 1:
            self.current_database['longlat'] = self.current_database['longitude'] + ' ' + self.current_database['latitude']
            self.current_database['distance'] = self.current_database['longlat'].apply(lambda x: calcule_distance(x,gps[0],gps[1]))
            self.step += 1
        else:
            self.answer = 'Je ne connais pas votre ville, essayez en une autre'

    def emploi_distance(self, information):
        distance = extract_number(information)
        if distance != -1:
            self.current_database = self.current_database[self.current_database['distance'] <= distance]
            self.step += 1
        else:
            self.answer = 'Veuillez entrer une distance en chiffres'

    def emploi_secteur(self, information):
        info_tokens = tokenize(information)
        print(info_tokens)
        self.current_tf_matrix_secteur = frequence_matrix(self.current_database)
        secteurs = list(self.current_tf_matrix_secteur.columns)
        print('secteurs' , secteurs)
        tokens_utiles = [e for e in info_tokens if e in secteurs]
        print("tokens_utiles", tokens_utiles)
        offres_utiles = []
        for e in tokens_utiles:
            offres_utiles += list(self.current_tf_matrix_secteur[self.current_tf_matrix_secteur[e] == 1].index)
            offres_utiles = list(ct.unique(offres_utiles))
            offres_utiles = sorted(offres_utiles)

        print("offres_utiles", offres_utiles)
        if len(offres_utiles) != 0:
            self.current_database = self.current_database.iloc[offres_utiles]
        self.step += 1

    def emploi(self, information):
        self.tf_idf_matrix_offre, self.word_list = TF_IDF_matrix(self.current_database)
        self.current_database.index = list(range(self.current_database.shape[0]))
        self.current_nb_offres = self.tf_idf_matrix_offre.shape[0]
        scores_offres = [(i, score_offre(information, self.word_list, self.tf_idf_matrix_offre[i,:]))
                         for i in range(self.current_nb_offres)]
        scores_offres_triees = sorted(scores_offres, key=lambda tup: tup[1], reverse = True)
        solution = []
        for i in range(10):
            solution.append(self.current_database.loc[scores_offres_triees[i][0], "desc"])
        self.liste_offres = nettoyage(l = solution, period=60)
        self.step += 1

    def run(self, information):
        if self.step == -1 :
            self.step += 1
            return self.question_list[0], self.answer
        else :
            self.answers_functions[self.step](information)
            self.question = self.question_list[self.step]
        return self.question_list[self.step], self.answer

    def reset(self):
        self.step = -1
        self.question = ""
        self.answer = " "
        self.tf_idf_matrix_offre = 0
        self.word_list = 0
        self.current_nb_offres = 0
        self.liste_offres = []
        self.current_tf_matrix_secteur = 0
        self.current_database = pd.read_csv(self.database_name, header=0, encoding="utf8", dtype={"sect": str, "longitude": str, "latitude": str}, nrows=self.nrows)
        self.current_database.dropna(subset=["sect"], inplace=True)