# -*- coding: utf8 -*-

import sys, argparse, os
import bs4
import requests
from requests.auth import HTTPBasicAuth
import re
import time
import logging

# insertion du système de logging

logging.basicConfig(level=logging.INFO, filename='checkip.log', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def majdyndns(webip):

    logging.info('Mise à jour du DynDNS OVH...')
    payload = {'system': 'dyndns', 'hostname': 'me.nixtech.fr', 'myip': webip}
    requests.get('http://www.ovh.com/nic/update', auth=HTTPBasicAuth(nom_utilisateur, mot_de_passe),params=payload)
    logging.info('Mise à jour OVH OK')

def ecriture_ip(webip):

    with open('/home/auxilium/scripts/mon_ip', 'w') as f:
        logging.info('Mise à jour du fichier local en cours...')
        f.write(webip)
        f.close()
        logging.info('Mise à jour du fichier local OK.')

def lecture_ip():

    with open('/home/auxilium/scripts/mon_ip') as f:
        monip = f.read()
        f.close()

    lecturewebip = requests.get('http://www.adresseip.com')

    soup = bs4.BeautifulSoup(lecturewebip.text, "lxml")
    webip = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',str(soup))

    if webip[0] == monip:
        pass
    else:
        logging.info('Votre IP a changé')
        ecriture_ip(webip[0])
        majdyndns(webip[0])

def main(argv):
    
    if not os.path.isfile('setup.cfg'):
        sys.exit('Pas de configuration... \nMerci de lancer python3 check_ip.py --setup')
    
    while True:

        lecture_ip()
        time.sleep(600)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='configuration du DynDNS OVH')
    parser.add_argument("-s", "--setup", nargs='0',help="création et modification du fichier de configuration")
    parser.parse_args()
    main(sys.argv[1:])