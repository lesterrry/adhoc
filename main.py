#!/usr/bin/env python3
#
# Handcrafted by Aydar N.
# 2023
#
# me@aydar.media
#

#
# You may need to run this prior to running everything else
#
# from cltk.data.fetch import FetchCorpus
# corpus = FetchCorpus('lat')
# corpus.import_corpus('lat_models_cltk')
# exit()


import sys
from tabulate import tabulate

VERSION = '0.1.0'

RED = "\033[31m"
ORG = "\033[33m"
BLD = "\033[1m"
RES = "\033[0m"

def my_except_hook(exctype, value, traceback):
	if exctype is not KeyboardInterrupt:
		print(f'{RED + BLD}FATAL:{RES} {value}')
		exit(1)
def recoverable_error(exception):
	print(f'{RED + BLD}ERROR:{RES} {exception}')
sys.excepthook = my_except_hook

text = None
conf = {'definitions_enabled': False}

argv = sys.argv
if '-v' in argv or '--version' in argv:
	print(f'Ad Hoc v{VERSION}')
	exit()
if len(argv) == 2:
	print('Will run once with word from argv')
	text = argv[1]

print('Importing CLTK...\n')
from cltk import NLP
from cltk.morphology.lat import CollatinusDecliner

nlp = NLP(language='lat')

nlp.pipeline.processes.pop(0)
nlp.pipeline.processes.pop(1)
nlp.pipeline.processes.pop(1)
print(f'{ORG}NOTE:{RES} actually running `LatinStanzaProcess`, `LatinLexiconProcess` only\n')

def analyze(with_text):
	print('Analyzing...')
	try:
		word = nlp.analyze(text=with_text).words[0]
	except Exception as e:
		recoverable_error(e)

	print('Declining...')
	try:
		decliner = CollatinusDecliner()
		declinations = decliner.decline(word.lemma, flatten=True)
	except Exception as e:
		recoverable_error(e)
		declinations = None
	if declinations is None:
		declinations_str = 'None'
	else:
		if len(declinations[3]) < 2 or len(declinations[4]) < 2:
			declinations = [(f'{declinations[0]}_{n}' if declinations[0] != n else n) for n in declinations]
		declinations_str = tabulate(
				[['Nom', declinations[0], declinations[6]],
				['Gen', declinations[3], declinations[9]],
				['Dat', declinations[4], declinations[10]],
				['Acc', declinations[2], declinations[8]],
				['Abl', declinations[5], declinations[11]],
				['Voc', declinations[1], declinations[7]]],
				headers=['    ', 'SING', 'PLUR']
			).replace('\n', '\n		')
	try:
		case_str = str(word.features['Case'][0])
	except:
		case_str = 'unknown'
	try:
		num_str = str(word.features['Number'][0])
	except:
		num_str = 'unknown'
	if conf['definitions_enabled']:
		def_str = word.definition.replace('\n', '\n	')
	else:
		def_str = 'disabled'

	print(f"""
	{word.string.title()}
	{BLD}POS:{RES} {str(word.pos)}
	{BLD}NUM:{RES} {num_str}
	{BLD}CASE:{RES} {case_str}
	{BLD}DECL:{RES}
		{declinations_str}
	{BLD}DEF:{RES}
	{str(def_str)}
		""")
def handle_command(command):
	global conf
	if command == '/list':
		print('/list', '/exit', '/endef', '/disdef')
	elif command == '/exit':
		exit(0)
	elif command == '/endef':
		conf['definitions_enabled'] = True
		print('Definitions enabled')
	elif command == '/disdef':
		conf['definitions_enabled'] = False
		print('Definitions disabled')
	else:
		print('Command unknown, use /list')

if text is not None:
	analyze(text)
	exit(0)

while True:
	text = input('Enter word > ')
	if text[0] == '/':
		handle_command(text)
		continue
	analyze(text)
