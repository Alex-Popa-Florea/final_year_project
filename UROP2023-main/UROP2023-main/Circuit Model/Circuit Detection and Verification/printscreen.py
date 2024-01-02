class col:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	WARNING = '\033[93m'
	RED = '\033[31m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	CYAN = '\033[36m'
	UNDERLINE = '\033[4m'
	WHITE = '\033[37m'

def print_piece_list(list):
	print (col.BLUE + "[",end=' ')
	for p in list:
		print (col.BLUE + p.name, end=',')
	print (col.BLUE + "]")
		
def print_paths(all_paths):
	if (not all_paths):
		print (col.RED + "\n There are no paths that form a circuit \n")
		return
	print (col.BLUE + "\n The following possible paths have been found that form a circuit:")
	for path in all_paths:
		print_piece_list(path)
		print (col.BLUE + "\n")

def printWarning(text, ending = "\n"):
	print (col.RED + text, end = ending)
	
def printPiece(text):
	print (col.GREEN + text)
	
def printSkill(text, ending = "\n"):
	print (col.CYAN + text, end = ending)
	
def printInfo(text, ending = "\n"):
	print (col.WHITE + str(text), end = ending)
