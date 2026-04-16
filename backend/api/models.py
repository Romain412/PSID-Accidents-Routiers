from django.db import models

class Accident(models.Model):
    """
    Rubrique CARACTERISTIQUES 
    Identifiant principal : Num_Acc 
    """
    Num_Acc = models.BigIntegerField(primary_key=True) # INTACT
    jour = models.CharField(max_length=255, null=True, blank=True)
    mois = models.CharField(max_length=255, null=True, blank=True)
    an = models.CharField(max_length=255, null=True, blank=True)
    hrmn = models.CharField(max_length=10, null=True, blank=True) 
    lum = models.CharField(max_length=255, null=True, blank=True)
    dep = models.CharField(max_length=3, null=True, blank=True)
    com = models.CharField(max_length=255, null=True, blank=True)
    agg = models.CharField(max_length=255, null=True, blank=True)
    
    # 'int' est un mot réservé. On utilise db_column pour forcer le nom dans la base.
    intersection_col = models.CharField(db_column='int', max_length=255, null=True, blank=True) 
    
    atm = models.CharField(max_length=255, null=True, blank=True)
    col = models.CharField(max_length=255, null=True, blank=True)
    adr = models.TextField(null=True, blank=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True) # INTACT
    long = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True) # INTACT

    def __str__(self):
        return str(self.Num_Acc)

class Lieu(models.Model):
    """
    Rubrique LIEUX
    """
    Num_Acc = models.ForeignKey('Accident', on_delete=models.CASCADE, related_name='lieux', db_column='Num_Acc')
    catr = models.CharField(max_length=255, null=True, blank=True)
    voie = models.CharField(max_length=255, null=True, blank=True)
    V1 = models.CharField(max_length=255, null=True, blank=True) 
    V2 = models.CharField(max_length=10, null=True, blank=True) 
    circ = models.CharField(max_length=255, null=True, blank=True)
    nbv = models.CharField(max_length=10, null=True, blank=True) 
    vosp = models.CharField(max_length=255, null=True, blank=True)
    prof = models.CharField(max_length=255, null=True, blank=True)
    pr = models.CharField(max_length=20, null=True, blank=True)
    pr1 = models.CharField(max_length=20, null=True, blank=True)
    plan = models.CharField(max_length=255, null=True, blank=True)
    lartpc = models.CharField(max_length=255, null=True, blank=True)
    larrout = models.CharField(max_length=255, null=True, blank=True)
    surf = models.CharField(max_length=255, null=True, blank=True)
    infra = models.CharField(max_length=255, null=True, blank=True)
    situ = models.CharField(max_length=255, null=True, blank=True)
    vma = models.IntegerField(null=True, blank=True) # INTACT

class Vehicule(models.Model):
    """
    Rubrique VEHICULES 
    """
    id_vehicule = models.CharField(max_length=50, primary_key=True) 
    Num_Acc = models.ForeignKey('Accident', on_delete=models.CASCADE, related_name='vehicules', db_column='Num_Acc')
    num_veh = models.CharField(max_length=10, null=True, blank=True) 
    senc = models.CharField(max_length=255, null=True, blank=True)
    catv = models.CharField(max_length=255, null=True, blank=True)
    obs = models.CharField(max_length=255, null=True, blank=True)
    obsm = models.CharField(max_length=255, null=True, blank=True)
    choc = models.CharField(max_length=255, null=True, blank=True)
    manv = models.CharField(max_length=255, null=True, blank=True)
    motor = models.CharField(max_length=255, null=True, blank=True)
    occutc = models.CharField(max_length=255, null=True, blank=True)

class Usager(models.Model):
    """
    Rubrique USAGERS impliqués
    """
    id_usager = models.CharField(max_length=50, primary_key=True) 
    Num_Acc = models.ForeignKey('Accident', on_delete=models.CASCADE, related_name='usagers', db_column='Num_Acc')
    id_vehicule = models.ForeignKey('Vehicule', on_delete=models.CASCADE, related_name='occupants', db_column='id_vehicule') 
    num_veh = models.CharField(max_length=10, null=True, blank=True) 
    place = models.CharField(max_length=255, null=True, blank=True)
    catu = models.CharField(max_length=255, null=True, blank=True)
    grav = models.CharField(max_length=255, null=True, blank=True)
    sexe = models.CharField(max_length=255, null=True, blank=True)
    an_nais = models.CharField(max_length=255, null=True, blank=True) 
    trajet = models.CharField(max_length=255, null=True, blank=True)
    secu1 = models.CharField(max_length=255, null=True, blank=True)
    secu2 = models.CharField(max_length=255, null=True, blank=True)
    secu3 = models.CharField(max_length=255, null=True, blank=True)
    locp = models.CharField(max_length=255, null=True, blank=True)
    actp = models.CharField(max_length=10, null=True, blank=True)
    etatp = models.CharField(max_length=255, null=True, blank=True)