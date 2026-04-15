import os
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Accident, Lieu, Vehicule, Usager

class Command(BaseCommand):
    help = 'Importe les données BAAC 2024 depuis les fichiers CSV'

    def handle(self, *args, **kwargs):
        # Chemin vers le dossier data
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        
        self.stdout.write(self.style.WARNING('Début de l\'importation... Cela peut prendre une minute.'))

        # ==========================================
        # 1. IMPORT DES CARACTÉRISTIQUES (Accidents)
        # ==========================================
        self.stdout.write('Lecture de caract_2024.csv...')
        df_caract = pd.read_csv(os.path.join(data_dir, 'caract_2024.csv'), sep=';', decimal=',', low_memory=False)
        df_caract = df_caract.replace({np.nan: None}) # Remplace les cases vides par None pour Django

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
                intersection_col=row.get('int'), # Correspondance avec notre modèle
                atm=row.get('atm'),
                col=row.get('col'),
                adr=row.get('adr'),
                lat=row.get('lat'),
                long=row.get('long')
            ))
        
        # ignore_conflicts=True permet de relancer le script sans créer de doublons
        Accident.objects.bulk_create(accidents, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'{len(accidents)} accidents importés.'))

        # ==========================================
        # 2. IMPORT DES LIEUX
        # ==========================================
        self.stdout.write('Lecture de lieux_2024.csv...')
        df_lieux = pd.read_csv(os.path.join(data_dir, 'lieux_2024.csv'), sep=';', decimal=',', low_memory=False)
        df_lieux = df_lieux.replace({np.nan: None})

        lieux = []
        for row in df_lieux.to_dict('records'):
            lieux.append(Lieu(
                Num_Acc_id=row.get('Num_Acc'), # _id permet de lier la ForeignKey directement
                catr=row.get('catr'),
                voie=row.get('voie'),
                V1=row.get('v1') or row.get('V1'), # Gère les variations de majuscules
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
        self.stdout.write('Lecture de vehicules_2024.csv...')
        df_veh = pd.read_csv(os.path.join(data_dir, 'vehicules_2024.csv'), sep=';', low_memory=False)
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
        self.stdout.write('Lecture de usagers_2024.csv...')
        df_usagers = pd.read_csv(os.path.join(data_dir, 'usagers_2024.csv'), sep=';', low_memory=False)
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