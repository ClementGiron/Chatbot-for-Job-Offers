from functions import *

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

        # Full initial cleaned database of job offers
        self.database = pd.read_csv(database_name, header=0, encoding="utf8",dtype={"sect": str, "longitude": str, "latitude": str}, nrows=nrows)
        self.database.dropna(subset=["sect"], inplace=True, how="any")

        # Database of job offers truncated according to the user criteria
        self.current_database = pd.read_csv(database_name, header=0, encoding="utf8", dtype={"sect": str, "longitude": str, "latitude": str}, nrows=nrows)
        self.current_database.dropna(subset=["sect"], inplace=True, how="any")

        # Database containing the city cities and their gps coordinates
        self.city_gps_base = pd.read_csv("regions.csv", header=0, encoding="utf8", sep = ";")
        self.city_gps_base.index = self.city_gps_base.nom_commune

        # Questions that are going to be asked to the user
        self.question_list = ["Cherchez-vous un emploi à temps plein ou à temps partiel ? ",
                              "Quelle est votre ville ?",
                              "Quelle distance êtes-vous prêt à parcourir pour aller travailler en Km?",
                              "Dans quel secteur voulez-vous travailler ?",
                              "Quel emploi cherchez-vous ?",
                              "Voulez-vous lancer une nouvelle recherche ?",
                              "Etes-vous satisfait ?"]

        # For every question we defined a function which would return a response to that question
        self.answers_functions = [self.temps,
                                  self.emploi_adresse,
                                  self.emploi_distance,
                                  self.emploi_secteur,
                                  self.emploi]

    def compute_tf_idf(self, database):
        """Computes the TF-IDF matrix.

            Keyword arguments:
            database -- The database in a panda dataframe format
            """
        return TF_IDF_matrix(database)

    def temps(self, information):
        """Computes the answer for the question "Temps plein ou temps partiel ?".

            Keyword arguments:
            information -- The entry of the user in a string format
            """
        info_traitee = quel_temps(information)
        if info_traitee != "Faux":
            # We tuncate the database to the type of jobs requested by the user
            self.current_database = self.current_database[self.current_database['tps'] == info_traitee]
            self.step += 1
        else:
            self.answer = "Veuillez saisir partiel ou plein."

    def emploi_adresse(self, information):
        """Computes the answer for the question "Quelle est votre ville ?".

            Keyword arguments:
            information -- The entry of the user in a string format
            """
        gps = ville_to_gps(information, self.city_gps_base)
        if gps != 1:
            # We tuncate the database to locations requested by the user
            self.current_database['longlat'] = self.current_database['longitude'] + ' ' + self.current_database['latitude']
            self.current_database['distance'] = self.current_database['longlat'].apply(lambda x: calcule_distance(x,gps[0],gps[1]))
            self.step += 1
        else:
            self.answer = 'Je ne connais pas votre ville, essayez en une autre'

    def emploi_distance(self, information):
        """Computes the answer for the question "Quelle distance êtes-vous prêt à parcourir pour aller travailler en Km?".

            Keyword arguments:
            information -- The entry of the user in a string format
            """
        distance = extract_number(information)
        if distance != -1:
            # We tuncate the database to the type of jobs with a valid distance
            self.current_database = self.current_database[self.current_database['distance'] <= distance]
            self.step += 1
        else:
            self.answer = 'Veuillez entrer une distance en chiffres'

    def emploi_secteur(self, information):
        """Computes the answer for the question "Dans quel secteur voulez-vous travailler ?".

            Keyword arguments:
            information -- The entry of the user in a string format
            """
        # First we compute the TF matrix for the job sectors within the truncated database
        self.current_tf_matrix_secteur = frequence_matrix(self.current_database)

        # We check the sectors mentioned in the user request and truncate the database accordingly
        info_tokens = tokenize(information)
        secteurs = list(self.current_tf_matrix_secteur.columns)
        tokens_utiles = [e for e in info_tokens if e in secteurs]

        # We keep the offers which belong to the sectors requested by the user
        offres_utiles = []
        for e in tokens_utiles:
            offres_utiles += list(self.current_tf_matrix_secteur[self.current_tf_matrix_secteur[e] == 1].index)
            offres_utiles = list(ct.unique(offres_utiles))
            offres_utiles = sorted(offres_utiles)

        # If we found relevant job offers according to the sectors requested by the user, we update the database
        if len(offres_utiles) != 0:
            self.current_database = self.current_database.iloc[offres_utiles]

        self.step += 1

    def emploi(self, information):
        """Computes the answer for the question "Quel emploi cherchez-vous ?".

            Keyword arguments:
            information -- The entry of the user in a string format
            """

        # We compute the TF-IDF matrix for the current database
        self.tf_idf_matrix_offre, self.word_list = TF_IDF_matrix(self.current_database)
        self.current_database.index = list(range(self.current_database.shape[0]))
        self.current_nb_offres = self.tf_idf_matrix_offre.shape[0]

        # We compute a relevance score for the job offers after the truncation
        scores_offres = [(i, score_offre(information, self.word_list, self.tf_idf_matrix_offre[i,:]))
                         for i in range(self.current_nb_offres)]
        scores_offres_triees = sorted(scores_offres, key=lambda tup: tup[1], reverse = True)

        # We keep the top 10 solutions
        solution = []
        for i in range(10):
            solution.append(self.current_database.loc[scores_offres_triees[i][0], "desc"])

        # We preprocess the job offers list for displaying them
        self.liste_offres = nettoyage(l=solution, period=60)

        self.step += 1

    def run(self, information):
        """Computes the answer for the entry of the user.

            Keyword arguments:
            information -- The entry of the user in a string format
            """
        if self.step == -1 :
            # First question
            self.step += 1
            return self.question_list[0], self.answer
        else :
            # Calls the current step's corresponding function in order to answer the user request
            self.answers_functions[self.step](information)
            self.question = self.question_list[self.step]
        return self.question_list[self.step], self.answer

    def reset(self):
        """Resets all the attributes of the object chatbot"""
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