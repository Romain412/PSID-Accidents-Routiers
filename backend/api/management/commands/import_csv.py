import os
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Accident, Lieu, Vehicule, Usager

class Command(BaseCommand):
    help = 'Importe les données BAAC 2024 depuis les fichiers CSV avec mapping des valeurs'

    def apply_mapping(self, df, col_name, mapping):
        """
        Fonction utilitaire pour appliquer un dictionnaire de correspondance à une colonne Pandas.
        Gère automatiquement le nettoyage des '.0' générés par Pandas pour les nombres avec valeurs nulles.
        """
        if col_name in df.columns:
            # 1. ASTUCE ICI : On force d'abord la colonne entière à accepter du texte
            df[col_name] = df[col_name].astype(object)
            
            # 2. On convertit en string et on retire le '.0'
            clean_col = df[col_name].dropna().astype(str).str.replace(r'\.0$', '', regex=True)
            
            # 3. On mappe avec le dictionnaire
            df.loc[clean_col.index, col_name] = clean_col.map(mapping).fillna(clean_col)

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.stdout.write(self.style.WARNING('Début de l\'importation avec mapping... Cela peut prendre quelques minutes.'))

        # ==========================================
        # DICTIONNAIRES DE MAPPING (Basés sur la doc officielle BAAC)
        # ==========================================
        
        # MAPPINGS CARACTÉRISTIQUES
        MAP_LUM = {'1': 'Plein jour', '2': 'Crépuscule ou aube', '3': 'Nuit sans éclairage public', '4': 'Nuit avec éclairage public non allumé', '5': 'Nuit avec éclairage public allumé'} 
        MAP_AGG = {'1': 'Hors agglomération', '2': 'En agglomération'} # [cite: 88-89]
        MAP_INT = {'1': 'Hors intersection', '2': 'Intersection en X', '3': 'Intersection en T', '4': 'Intersection en Y', '5': 'Intersection à plus de 4 branches', '6': 'Giratoire', '7': 'Place', '8': 'Passage à niveau', '9': 'Autre intersection'} # [cite: 90-100]
        MAP_ATM = {'-1': 'Non renseigné', '1': 'Normale', '2': 'Pluie légère', '3': 'Pluie forte', '4': 'Neige - grêle', '5': 'Brouillard - fumée', '6': 'Vent fort - tempête', '7': 'Temps éblouissant', '8': 'Temps couvert', '9': 'Autre'} # [cite: 102-112]
        MAP_COL = {'-1': 'Non renseigné', '1': 'Deux véhicules - frontale', '2': 'Deux véhicules - par l\'arrière', '3': 'Deux véhicules - par le coté', '4': 'Trois véhicules et plus - en chaîne', '5': 'Trois véhicules et plus - collisions multiples', '6': 'Autre collision', '7': 'Sans collision'} # [cite: 113-123]

        # MAPPINGS LIEUX
        MAP_CATR = {'1': 'Autoroute', '2': 'Route nationale', '3': 'Route Départementale', '4': 'Voie Communales', '5': 'Hors réseau public', '6': 'Parc de stationnement ouvert à la circulation publique', '7': 'Routes de métropole urbaine', '9': 'Autre'} # [cite: 133-142]
        MAP_CIRC = {'-1': 'Non renseigné', '1': 'A sens unique', '2': 'Bidirectionnelle', '3': 'A chaussées séparées', '4': 'Avec voies d\'affectation variable'} 
        MAP_VOSP = {'-1': 'Non renseigné', '0': 'Sans objet', '1': 'Piste cyclable', '2': 'Bande cyclable', '3': 'Voie réservée'} 
        MAP_PROF = {'-1': 'Non renseigné', '1': 'Plat', '2': 'Pente', '3': 'Sommet de côte', '4': 'Bas de côte'} 
        MAP_PLAN = {'-1': 'Non renseigné', '1': 'Partie rectiligne', '2': 'En courbe à gauche', '3': 'En courbe à droite', '4': 'En S'} # [cite: 178-184]
        MAP_SURF = {'-1': 'Non renseigné', '1': 'Normale', '2': 'Mouillée', '3': 'Flaques', '4': 'Inondée', '5': 'Enneigée', '6': 'Boue', '7': 'Verglacée', '8': 'Corps gras - huile', '9': 'Autre'} # [cite: 189-201]
        MAP_INFRA = {'-1': 'Non renseigné', '0': 'Aucun', '1': 'Souterrain - tunnel', '2': 'Pont - autopont', '3': 'Bretelle d\'échangeur ou de raccordement', '4': 'Voie ferrée', '5': 'Carrefour aménagé', '6': 'Zone piétonne', '7': 'Zone de péage', '8': 'Chantier', '9': 'Autres'} # [cite: 202-214]
        MAP_SITU = {'-1': 'Non renseigné', '0': 'Aucun', '1': 'Sur chaussée', '2': 'Sur bande d\'arrêt d\'urgence', '3': 'Sur accotement', '4': 'Sur trottoir', '5': 'Sur piste cyclable', '6': 'Sur autre voie spéciale', '8': 'Autres'} # [cite: 215-225]

        # MAPPINGS VEHICULES
        MAP_SENC = {'-1': 'Non renseigné', '0': 'Inconnu', '1': 'PK/PR ou adresse croissant', '2': 'PK/PR ou adresse décroissant', '3': 'Absence de repère'} # [cite: 235-242]
        MAP_CATV = {'0': 'Indéterminable', '1': 'Bicyclette', '2': 'Cyclomoteur <50cm3', '3': 'Voiturette', '7': 'VL seul', '10': 'VU seul 1,5T <= PTAC <= 3,5T', '13': 'PL seul 3,5T <PTCA <= 7,5T', '14': 'PL seul > 7,5T', '15': 'PL > 3,5T + remorque', '16': 'Tracteur routier seul', '17': 'Tracteur routier + semi-remorque', '20': 'Engin spécial', '21': 'Tracteur agricole', '30': 'Scooter < 50 cm3', '31': 'Motocyclette > 50 cm3 et <= 125 cm3', '32': 'Scooter > 50 cm3 et <= 125 cm3', '33': 'Motocyclette > 125 cm3', '34': 'Scooter > 125 cm3', '35': 'Quad léger <= 50 cm3', '36': 'Quad lourd > 50 cm3', '37': 'Autobus', '38': 'Autocar', '39': 'Train', '40': 'Tramway', '41': '3RM <= 50 cm3', '42': '3RM 50 cm3 <= 125 cm3', '43': '3RM > 125 cm3', '50': 'EDP à moteur', '60': 'EDP sans moteur', '80': 'VAE', '99': 'Autre véhicule'} # [cite: 243-283]
        MAP_OBS = {'-1': 'Non renseigné', '0': 'Sans objet', '1': 'Véhicule en stationnement', '2': 'Arbre', '3': 'Glissière métallique', '4': 'Glissière béton', '5': 'Autre glissière', '6': 'Bâtiment, mur, pile de pont', '7': 'Support de signalisation', '8': 'Poteau', '9': 'Mobilier urbain', '10': 'Parapet', '11': 'Ilot, refuge, borne haute', '12': 'Bordure de trottoir', '13': 'Fossé, talus, paroi rocheuse', '14': 'Autre obstacle fixe sur chaussée', '15': 'Autre obstacle fixe sur trottoir', '16': 'Sortie de chaussée sans obstacle', '17': 'Buse - tête d\'aqueduc'} # [cite: 284-309]
        MAP_OBSM = {'-1': 'Non renseigné', '0': 'Aucun', '1': 'Piéton', '2': 'Véhicule', '4': 'Véhicule sur rail', '5': 'Animal domestique', '6': 'Animal sauvage', '9': 'Autre'} # [cite: 310-319]
        MAP_CHOC = {'-1': 'Non renseigné', '0': 'Aucun', '1': 'Avant', '2': 'Avant droit', '3': 'Avant gauche', '4': 'Arrière', '5': 'Arrière droit', '6': 'Arrière gauche', '7': 'Côté droit', '8': 'Côté gauche', '9': 'Chocs multiples (tonneaux)'} # [cite: 320-332]
        MAP_MANV = {'-1': 'Non renseigné', '0': 'Inconnue', '1': 'Sans changement de direction', '2': 'Même sens, même file', '3': 'Entre 2 files', '4': 'En marche arrière', '5': 'A contresens', '6': 'En franchissant le terre-plein central', '7': 'Dans le couloir bus, même sens', '8': 'Dans le couloir bus, sens inverse', '9': 'En s\'insérant', '10': 'En faisant demi-tour sur la chaussée', '11': 'Changeant de file à gauche', '12': 'Changeant de file à droite', '13': 'Déporté à gauche', '14': 'Déporté à droite', '15': 'Tournant à gauche', '16': 'Tournant à droite', '17': 'Dépassant à gauche', '18': 'Dépassant à droite', '19': 'Traversant la chaussée', '20': 'Manœuvre de stationnement', '21': 'Manœuvre d\'évitement', '22': 'Ouverture de porte', '23': 'Arrêté (hors stationnement)', '24': 'En stationnement (avec occupants)', '25': 'Circulant sur trottoir', '26': 'Autres manœuvres'} # [cite: 333-371]
        MAP_MOTOR = {'-1': 'Non renseigné', '0': 'Inconnue', '1': 'Hydrocarbures', '2': 'Hybride électrique', '3': 'Electrique', '4': 'Hydrogène', '5': 'Humaine', '6': 'Autre'} # [cite: 372-381]

        # MAPPINGS USAGERS
        MAP_CATU = {'1': 'Conducteur', '2': 'Passager', '3': 'Piéton'} # [cite: 411-415]
        MAP_GRAV = {'1': 'Indemne', '2': 'Tué', '3': 'Blessé hospitalisé', '4': 'Blessé léger'} # [cite: 416-421]
        MAP_SEXE = {'1': 'Masculin', '2': 'Féminin'} # [cite: 422-425]
        MAP_TRAJET = {'-1': 'Non renseigné', '0': 'Non renseigné', '1': 'Domicile - travail', '2': 'Domicile - école', '3': 'Courses - achats', '4': 'Utilisation professionnelle', '5': 'Promenade - loisirs', '9': 'Autre'} # [cite: 428-437]
        MAP_SECU = {'-1': 'Non renseigné', '0': 'Aucun équipement', '1': 'Ceinture', '2': 'Casque', '3': 'Dispositif enfants', '4': 'Gilet réfléchissant', '5': 'Airbag (2RM/3RM)', '6': 'Gants (2RM/3RM)', '7': 'Gants + Airbag (2RM/3RM)', '8': 'Non déterminable', '9': 'Autre'} # [cite: 441-478]
        MAP_LOCP = {'-1': 'Non renseigné', '0': 'Sans objet', '1': 'Sur chaussée à +50m du passage piéton', '2': 'Sur chaussée à -50m du passage piéton', '3': 'Sur passage piéton sans signal lum', '4': 'Sur passage piéton avec signal lum', '5': 'Sur trottoir', '6': 'Sur accotement', '7': 'Sur refuge ou BAU', '8': 'Sur contre allée', '9': 'Inconnue'} # [cite: 479-494]
        MAP_ACTP = {'-1': 'Non renseigné', '0': 'Non renseigné ou sans objet', '1': 'Sens véhicule heurtant', '2': 'Sens inverse du véhicule', '3': 'Traversant', '4': 'Masqué', '5': 'Jouant - courant', '6': 'Avec animal', '9': 'Autre', 'A': 'Monte/descend du véhicule', 'B': 'Inconnue'} # [cite: 495-510]
        MAP_ETATP = {'-1': 'Non renseigné', '1': 'Seul', '2': 'Accompagné', '3': 'En groupe'} # [cite: 511-516]


        # ==========================================
        # 1. IMPORT DES CARACTÉRISTIQUES (Accidents)
        # ==========================================
        self.stdout.write('Lecture et formatage de caract_2024.csv...')
        df_caract = pd.read_csv(os.path.join(data_dir, 'caract_2024.csv'), sep=';', decimal=',', low_memory=False)
        
        # Application des mappings
        self.apply_mapping(df_caract, 'lum', MAP_LUM)
        self.apply_mapping(df_caract, 'agg', MAP_AGG)
        self.apply_mapping(df_caract, 'int', MAP_INT)
        self.apply_mapping(df_caract, 'atm', MAP_ATM)
        self.apply_mapping(df_caract, 'col', MAP_COL)
        
        df_caract = df_caract.replace({np.nan: None})

        accidents = []
        for row in df_caract.to_dict('records'):
            accidents.append(Accident(
                Num_Acc=row.get('Num_Acc'),
                jour=row.get('jour'),
                mois=row.get('mois'),
                an=row.get('an'),
                hrmn=row.get('hrmn'),
                lum=row.get('lum'),
                dep=row.get('dep'),
                com=row.get('com'),
                agg=row.get('agg'),
                intersection_col=row.get('int'), 
                atm=row.get('atm'),
                col=row.get('col'),
                adr=row.get('adr'),
                lat=row.get('lat'),
                long=row.get('long')
            ))
        
        Accident.objects.bulk_create(accidents, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'{len(accidents)} accidents importés.'))

        # ==========================================
        # 2. IMPORT DES LIEUX
        # ==========================================
        self.stdout.write('Lecture et formatage de lieux_2024.csv...')
        df_lieux = pd.read_csv(os.path.join(data_dir, 'lieux_2024.csv'), sep=';', decimal=',', low_memory=False)
        
        # Application des mappings
        self.apply_mapping(df_lieux, 'catr', MAP_CATR)
        self.apply_mapping(df_lieux, 'circ', MAP_CIRC)
        self.apply_mapping(df_lieux, 'vosp', MAP_VOSP)
        self.apply_mapping(df_lieux, 'prof', MAP_PROF)
        self.apply_mapping(df_lieux, 'plan', MAP_PLAN)
        self.apply_mapping(df_lieux, 'surf', MAP_SURF)
        self.apply_mapping(df_lieux, 'infra', MAP_INFRA)
        self.apply_mapping(df_lieux, 'situ', MAP_SITU)

        df_lieux = df_lieux.replace({np.nan: None})

        lieux = []
        for row in df_lieux.to_dict('records'):
            lieux.append(Lieu(
                Num_Acc_id=row.get('Num_Acc'),
                catr=row.get('catr'),
                voie=row.get('voie'),
                V1=row.get('v1') or row.get('V1'), 
                V2=row.get('v2') or row.get('V2'),
                circ=row.get('circ'),
                nbv=row.get('nbv'),
                vosp=row.get('vosp'),
                prof=row.get('prof') or row.get('prf'),
                pr=row.get('pr'),
                pr1=row.get('pr1'),
                plan=row.get('plan'),
                lartpc=row.get('lartpc'),
                larrout=row.get('larrout'),
                surf=row.get('surf'),
                infra=row.get('infra'),
                situ=row.get('situ'),
                vma=row.get('vma')
            ))
        Lieu.objects.bulk_create(lieux, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'{len(lieux)} lieux importés.'))

        # ==========================================
        # 3. IMPORT DES VÉHICULES
        # ==========================================
        self.stdout.write('Lecture et formatage de vehicules_2024.csv...')
        df_veh = pd.read_csv(os.path.join(data_dir, 'vehicules_2024.csv'), sep=';', low_memory=False)
        
        # Application des mappings
        self.apply_mapping(df_veh, 'senc', MAP_SENC)
        self.apply_mapping(df_veh, 'catv', MAP_CATV)
        self.apply_mapping(df_veh, 'obs', MAP_OBS)
        self.apply_mapping(df_veh, 'obsm', MAP_OBSM)
        self.apply_mapping(df_veh, 'choc', MAP_CHOC)
        self.apply_mapping(df_veh, 'manv', MAP_MANV)
        self.apply_mapping(df_veh, 'motor', MAP_MOTOR)

        df_veh = df_veh.replace({np.nan: None})

        vehicules = []
        for row in df_veh.to_dict('records'):
            vehicules.append(Vehicule(
                id_vehicule=str(row.get('id_vehicule')),
                Num_Acc_id=row.get('Num_Acc'),
                num_veh=row.get('num_veh'),
                senc=row.get('senc'),
                catv=row.get('catv'),
                obs=row.get('obs'),
                obsm=row.get('obsm'),
                choc=row.get('choc'),
                manv=row.get('manv'),
                motor=row.get('motor'),
                occutc=row.get('occutc')
            ))
        Vehicule.objects.bulk_create(vehicules, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'{len(vehicules)} véhicules importés.'))

        # ==========================================
        # 4. IMPORT DES USAGERS
        # ==========================================
        self.stdout.write('Lecture et formatage de usagers_2024.csv...')
        df_usagers = pd.read_csv(os.path.join(data_dir, 'usagers_2024.csv'), sep=';', low_memory=False)
        
        # Application des mappings
        self.apply_mapping(df_usagers, 'catu', MAP_CATU)
        self.apply_mapping(df_usagers, 'grav', MAP_GRAV)
        self.apply_mapping(df_usagers, 'sexe', MAP_SEXE)
        self.apply_mapping(df_usagers, 'trajet', MAP_TRAJET)
        self.apply_mapping(df_usagers, 'secu1', MAP_SECU)
        self.apply_mapping(df_usagers, 'secu2', MAP_SECU)
        self.apply_mapping(df_usagers, 'secu3', MAP_SECU)
        self.apply_mapping(df_usagers, 'locp', MAP_LOCP)
        self.apply_mapping(df_usagers, 'actp', MAP_ACTP)
        self.apply_mapping(df_usagers, 'etatp', MAP_ETATP)

        df_usagers = df_usagers.replace({np.nan: None})

        usagers = []
        for row in df_usagers.to_dict('records'):
            usagers.append(Usager(
                id_usager=str(row.get('id_usager')),
                Num_Acc_id=row.get('Num_Acc'),
                id_vehicule_id=str(row.get('id_vehicule')),
                num_veh=row.get('num_veh'),
                place=row.get('place'),
                catu=row.get('catu'),
                grav=row.get('grav'),
                sexe=row.get('sexe'),
                an_nais=row.get('an_nais'),
                trajet=row.get('trajet'),
                secu1=row.get('secu1') or row.get('secu 1'),
                secu2=row.get('secu2') or row.get('secu 2'),
                secu3=row.get('secu3') or row.get('secu 3'),
                locp=row.get('locp'),
                actp=row.get('actp'),
                etatp=row.get('etatp')
            ))
        Usager.objects.bulk_create(usagers, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'{len(usagers)} usagers importés avec succès !'))
        
        self.stdout.write(self.style.SUCCESS('--- IMPORTATION TERMINÉE ---'))