# ccmt-python
## Pré requis
* Windows 10
* Framework .net à jour (Windows 10 à jour)
* Python 3.7
* Émetteur Bluetooth Low Energy
## Pour démarrer
Ouvrir l'invite de commadne dans le dossier python  
Écrire : 
```
python main.py
```
## Utilisation
Pour se connecter à une camera :
* Dans le menu, choisissez l'option : ```Connect to a device```
* Entrez le numéro
* S'il n'est pas déjà paired, entrez le code pin à 6 chiffres

Les fonctionnalitées de la camera :
* Set timecode : Entrez l'heure, les minutes, les secondes et les frames séparés par deux points. Ex: ```09:53:00:00```
* Set focus : Entrez un nombre entier entre 0 et 8 pour ajuster le focus
* Start record pour lancer l'enregistrement.
* Stop record pour arrêter l'enregistrement.
