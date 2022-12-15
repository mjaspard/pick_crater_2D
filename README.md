# insarviz_gps


git clone https://github.com/mjaspard/pick_crater_2D.git		# cloner le repo modifié

cd pick_crater_2D								# aller dans le repertoire

python -m venv env								# créer un environnement python 
	
source env/bin/activate							# activer l’environnement

python -m pip install -r requirements.txt				# Installer tous les packages python nécessaire


# Lancer le script principal "Picker_profile.py_" avec comme argument le fichier csv correspondant.


ex: python Picker_profile.py /Users/maxime/Project/Pick_Crater/pick_crater_2D/DATA_SAR_AMPLI_NYIR21_FOR_PICKING/picking_ALL_updated.csv 
