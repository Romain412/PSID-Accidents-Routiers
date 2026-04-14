from django.db import models

from django.db import models

class Accident(models.Model):
    """
    Rubrique CARACTERISTIQUES 
    Identifiant principal : Num_Acc 
    """
    Num_Acc = models.BigIntegerField(primary_key=True)
    jour = models.IntegerField(null=True, blank=True)
    mois = models.IntegerField(null=True, blank=True)
    an = models.IntegerField(null=True, blank=True)
    hrmn = models.TextField(null=True, blank=True)
    lum = models.IntegerField(null=True, blank=True)
    dep = models.CharField(max_length=3, null=True, blank=True)
    com = models.CharField(max_length=5, null=True, blank=True)
    agg = models.IntegerField(null=True, blank=True)
    
    # 'int' est un mot réservé en Python. On utilise db_column pour forcer le nom dans la base.
    intersection_col = models.IntegerField(db_column='int', null=True, blank=True) 
    
    atm = models.IntegerField(null=True, blank=True)
    col = models.IntegerField(null=True, blank=True)
    adr = models.TextField(null=True, blank=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    long = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return str(self.Num_Acc)

class Lieu(models.Model):
    """
    Rubrique LIEUX
    """
    # db_column='Num_Acc' force Django à utiliser ce nom exact au lieu du nom par défaut 'Num_Acc_id'
    Num_Acc = models.ForeignKey('Accident', on_delete=models.CASCADE, related_name='lieux', db_column='Num_Acc')
    catr = models.IntegerField(null=True, blank=True)
    voie = models.CharField(max_length=255, null=True, blank=True)
    V1 = models.IntegerField(null=True, blank=True) # Majuscule selon la doc [cite: 145]
    V2 = models.TextField(null=True, blank=True) # Majuscule selon la doc [cite: 148]
    circ = models.IntegerField(null=True, blank=True)
    nbv = models.IntegerField(null=True, blank=True)
    vosp = models.IntegerField(null=True, blank=True)
    prof = models.IntegerField(null=True, blank=True)
    pr = models.CharField(max_length=20, null=True, blank=True)
    pr1 = models.CharField(max_length=20, null=True, blank=True)
    plan = models.IntegerField(null=True, blank=True)
    lartpc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    larrout = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    surf = models.IntegerField(null=True, blank=True)
    infra = models.IntegerField(null=True, blank=True)
    situ = models.IntegerField(null=True, blank=True)
    vma = models.IntegerField(null=True, blank=True)

class Vehicule(models.Model):
    """
    Rubrique VEHICULES 
    """
    id_vehicule = models.CharField(max_length=15)
    Num_Acc = models.ForeignKey('Accident', on_delete=models.CASCADE, related_name='vehicules', db_column='Num_Acc')
    Num_Veh = models.CharField(max_length=10) # Majuscule selon la doc [cite: 233]
    senc = models.IntegerField(null=True, blank=True)
    catv = models.IntegerField(null=True, blank=True)
    obs = models.IntegerField(null=True, blank=True)
    obsm = models.IntegerField(null=True, blank=True)
    choc = models.IntegerField(null=True, blank=True)
    manv = models.IntegerField(null=True, blank=True)
    motor = models.IntegerField(null=True, blank=True)
    occutc = models.IntegerField(null=True, blank=True)

class Usager(models.Model):
    """
    Rubrique USAGERS impliqués [cite: 41, 384]
    Relie un usager à son véhicule via id_vehicule[cite: 44, 45].
    """
    id_usager = models.BigIntegerField(primary_key=True)
    Num_Acc = models.ForeignKey('Accident', on_delete=models.CASCADE, related_name='usagers', db_column='Num_Acc')
    id_vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='occupants', db_column='id_vehicule')
    num_Veh = models.CharField(max_length=10, null=True, blank=True) # Minuscule 'n' selon la doc de cette rubrique [cite: 391]
    place = models.IntegerField(null=True, blank=True)
    catu = models.IntegerField(null=True, blank=True)
    grav = models.IntegerField(null=True, blank=True)
    sexe = models.IntegerField(null=True, blank=True)
    An_nais = models.IntegerField(null=True, blank=True) # Majuscule 'A' selon la doc [cite: 426]
    trajet = models.IntegerField(null=True, blank=True)
    secu1 = models.IntegerField(null=True, blank=True)
    secu2 = models.IntegerField(null=True, blank=True)
    secu3 = models.IntegerField(null=True, blank=True)
    locp = models.IntegerField(null=True, blank=True)
    actp = models.CharField(max_length=2, null=True, blank=True)
    etatp = models.IntegerField(null=True, blank=True)