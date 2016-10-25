#!/usr/bin/python
# encoding: utf-8

# Sous licence GNU AGPL v3
# https://www.gnu.org/licenses/agpl-3.0.html
# (C) Pierre-Jean Grenier, X2015

import sys
import subprocess
import munkres
import time

def read_arguments():
	dict_arg = {'-s':False, '-f':None, '-p':3, '-w':None, '-dnr':False}
	for i, arg in enumerate(sys.argv):
		if arg == '-f': # input file
			dict_arg[arg] = sys.argv[i+1]
		elif arg == '-s': # [show mode] activate
			dict_arg[arg] = True
		elif arg == '-p': # [show mode] Pause between results, in seconds
			dict_arg[arg] = int(sys.argv[i+1])
		elif arg == '-w': # write results to given file
			dict_arg[arg] = sys.argv[i+1]
		elif arg == '-dnr': # Do not erase : don't ever clean terminal output
			dict_arg[arg] = True
		elif arg == '-h': # Help
			print u"""GendGouilleuse - magouilleuse pour les stages en gendarmerie
Usage :
\tpython main.py -f input_file [-w output_file] [-s [-p PAUSE]] [-dnr]

Options :
\t-f\t\tFichier d'entrée
\t-w\t\tFichier de sortie, récapitulatif des affectations
\t-s\t\tRésultats en direct : 'show' mode
\t-p\t\tPause entre deux résultats en 'show' mode
\t-dnr\t\tNe jamais effacer le contenu de la console

Exemple :
\tpython main.py -f input_file -w results -s -p 3 """
			exit()
	return dict_arg
					

def main():
	dict_arg = read_arguments()
	path = dict_arg['-f']
	pause = dict_arg['-p']
	
	def clear():
		if not dict_arg['-dnr']:
			subprocess.call('clear',shell=True)
	
	file = open(path, 'r')
	read_lines = file.readlines()
	file.close()
	
	if '\n' in read_lines:
		read_lines.remove('\n')
	
	# Expected as follows:
	# 
	# internship1, internship2, internship3, internship4, internship5 ...
	# name1, choice1, choice2, choice3, choice4 ...
	# name2, choice1, choice2, choice3, choice4 ...
	# ...
	#
	# see INPUT_FILE for further details
	
	# Choices are read on the first line
	choices = read_lines[0].strip().split(', ')
	nb_choices = len(choices)
	
	# Making a reverse dictionary to later fill the matrix
	reverse_dict_choices = {choices[k]:k for k in range(nb_choices)}
	
	list_names = []
	
	# Dictionary giving for each name a dictionary, filled with
	#   {internship: rank}
	# Thus, the structure is
	#   {'name1': {'internship1': rank1, 'internship2': rank1, ...}, ...}
	reverse_dict_names_choices = {}
	
	# Creating matrix of costs
	matrix = []
	for i in range(1, len(read_lines)):
		current_line = read_lines[i].strip().split(', ')
		
		# Default rank is infinity. This means you can't have choices
		# you did not ranked.
		line_matrix = [float('inf')] * nb_choices
		
		name = current_line[0]
		reverse_dict_names_choices[name] = {}
		list_names.append(name)
		
		for j, choice in enumerate(current_line[1:]):
			# j+1 to avoid index 0
			# otherwise costs would be 0 then 1 and then 4
			# this would be another approach of the problem
			line_matrix[reverse_dict_choices[choice]] = (j+1)**2
			reverse_dict_names_choices[name][choice] = j+1
		
		matrix.append(line_matrix)
	
	# Make a square matrix if more choices than people
	for i in range(nb_choices-len(list_names)):
		matrix.append([0]*nb_choices)
	
	# Compute
	m = munkres.Munkres()
	indexes = m.compute(matrix)
	
	results = {}
	for i in range(len(list_names)):
		row, column = indexes[i]
		results[list_names[row]] = choices[column]	
	
	# Show results
	ascii_art = u"""***************************************************************************************************
    ________                   .___________             .__.__  .__                              
   /  _____/  ____   ____    __| _/  _____/  ____  __ __|__|  | |  |   ____  __ __  ______ ____  
  /   \  ____/ __ \ /    \  / __ /   \  ___ /  _ \|  |  \  |  | |  | _/ __ \|  |  \/  ___// __ \ 
  \    \_\  \  ___/|   |  \/ /_/ \    \_\  (  <_> )  |  /  |  |_|  |_\  ___/|  |  /\___ \\  ___/ 
   \______  /\___  >___|  /\____ |\______  /\____/|____/|__|____/____/\___  >____//____  >\___  >
          \/     \/     \/      \/       \/                               \/           \/     \/ 
***************************************************************************************************
		"""
	
	# Live results
	if dict_arg['-s']:
		print ascii_art
		for name in list_names:
			internship = results[name]
			clear()
			print ascii_art
			print u"\t\t%s :" % name
			print "\n\n"
			time.sleep(pause)
			print u"\t\t\t\t%s\n\n\t\t\t\t(choix numéro %i)" % (internship, reverse_dict_names_choices[name][internship])
			time.sleep(pause)
	
	# Summary
	clear()
	print ascii_art
	print u"Récapitulatif"
	
	text = u""
	for name in list_names:
		internship = results[name]
		line = u"%s : %s (choix numéro %i)" % (name, internship, reverse_dict_names_choices[name][internship])
		text += line + '\n'
		print line
	
	# Write to an output file if asked to
	if dict_arg['-w']:
		file = open(dict_arg['-w'], 'w')
		file.write(text.encode('utf-8'))
		file.close()
	
if __name__ == '__main__':
	main()
