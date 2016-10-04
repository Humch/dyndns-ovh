# -*- coding: utf8 -*-

import sys, argparse, os
import configparser
import bs4
import requests
from requests.auth import HTTPBasicAuth
import re
import time
import logging

# insertion du système de logging

logging.basicConfig(level=logging.INFO, filename='checkip.log', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def setup_script():
    
    config = configparser.ConfigParser()
    logging.info('démarrage de la configuration du script')
    
    if os.path.isfile('setup.cfg'):
        while True:
            reponse = input("La configuration existe, voulez vous la modifier ? Oui=O Non=N Supprimer=S\n")
            
            if reponse.lower() == 'o':
                while True:
                    reponse = input('Quel valeur est à modifier ?\nDomaine : D\nUtilisateur : U\nMot de passe : M\nQuitter : Q\n')
                    if reponse.lower() == 'd':
                        hostname = input('quel est le nom de domaine ?\n')
                        config['DEFAULT'] = {'hostname': hostname}
                    elif reponse.lower() == 'u':
                        nom_utilisateur = input("quel est le nom de l'utilisateur ?\n")
                        config['DEFAULT'] = {'nom_utilisateur' : nom_utilisateur}
                    elif reponse.lower() == 'm':
                        mot_de_passe = input("quel est le mot de passe ?\n")
                        config['DEFAULT'] = {'mot_de_passe' : mot_de_passe}
                    elif reponse.lower() == 'q':
                        with open('setup.cfg', 'w') as configfile:
                            config.write(configfile)
                        sys.exit('Configuration terminée.\nMerci de relancer check_ip.py')
                    else:
                        print('Je ne comprends pas votre réponse\nMerci de la reformuler...\n')
                    
                    with open('setup.cfg', 'w') as configfile:
                        config.write(configfile)
                        logging.info('Modification du script ok')
                    
            elif reponse.lower() == 'n':
                sys.exit('Ah, dommage :)\nMais que voulez vous alors?')
            elif reponse.lower() == 's':
                os.remove('setup.cfg')
                break
            else:
                print('Je ne comprends pas votre réponse\nMerci de la reformuler...\n')
    
    if not os.path.isfile('setup.cfg'):
        while True:
            reponse = input('pas de configuration detectée, voulez vous la créer? Oui=O Non=N\n')
        
            if reponse.lower() =='o':
                hostname = input('quel est le nom de domaine ?\n')
                nom_utilisateur = input("quel est le nom de l'utilisateur ?\n")
                mot_de_passe = input("quel est le mot de passe ?\n")
                print('vous avez saisi les informations suivantes:\nhostname : %s\nutilisateur : %s\nmot de passe : %s\nEst ce correct? Oui=O Non=N' %(hostname, nom_utilisateur, mot_de_passe))
                validation = input()
                if validation.lower() == 'o':
                    config['DEFAULT'] = {'hostname': hostname, 'nom_utilisateur' : nom_utilisateur, 'mot_de_passe' : mot_de_passe}
                    with open('setup.cfg', 'w') as configfile:
                        config.write(configfile)
                        logging.info('Configuration du script ok')
                        break
            
            elif reponse.lower() == 'n':
                sys.exit('Ah, dommage :)\nMais que voulez vous alors?')
            
            else:
                print('Je ne comprends pas votre réponse\nMerci de la reformuler...')

def majdyndns(webip):

    logging.info('Mise à jour du DynDNS OVH...')
    
    logging.info('Lecture de la configuration du script')
    config = configparser.ConfigParser()
    config.read('setup.cfg')
    
    payload = {'system': 'dyndns', 'hostname': config['DEFAULT']['hostname'], 'myip': webip}
    
    requests.get('http://www.ovh.com/nic/update', auth=HTTPBasicAuth(config['DEFAULT']['nom_utilisateur'], config['DEFAULT']['mot_de_passe']),params=payload)
    logging.info('Mise à jour OVH OK')

def ecriture_ip(webip):

    with open('ip_file', 'w') as f:
        logging.info('Mise à jour du fichier local en cours...')
        f.write(webip)
        f.close()
        logging.info('Mise à jour du fichier local OK.')

def lecture_ip():
    
    try:
        with open('ip_file') as f:
            monip = f.read()
            f.close()

    except:
        
        with open('ip_file', 'a') as f:
            monip = '0.0.0.0'
            f.write(monip)
            f.close()
    
    try:
        webip = requests.get('http://ip.42.pl/raw')
        
        if webip.text == monip:
            pass
        else:
            logging.info('Votre IP a changé')
            ecriture_ip(webip.text)
            majdyndns(webip.text)
        
    except:
        logging.info('Erreur de connexion')

def main(args):

    if args.setup:
        setup_script()
        sys.exit('Configuration terminée.\nMerci de relancer check_ip.py')
    
    if not os.path.isfile('setup.cfg'):
        sys.exit('Pas de configuration... \nMerci de lancer python3 check_ip.py --setup')
    
    while True:

        lecture_ip()
        time.sleep(600)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='configuration du DynDNS OVH')
    parser.add_argument("-s", "--setup", action='store_true', help="création et modification du fichier de configuration")
    args = parser.parse_args()
    main(args)