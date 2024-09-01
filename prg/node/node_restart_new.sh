#!/bin/bash

# Arrête l'application Node.js en cours d'exécution s'il y en a une
killall node

sleep 2

# Assurez-vous d'être dans le répertoire de l'application
cd /home/web/bonnezic.com/node

# Lancez l'application Node.js
/usr/bin/node current.js
