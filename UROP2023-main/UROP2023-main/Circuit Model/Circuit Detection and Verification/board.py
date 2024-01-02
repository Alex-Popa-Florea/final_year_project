
import cv2
import masks
import numpy as np

letterToLocation = {}

def whatAngle(boardBW):
    '''
    Return the angle of the board
    '''
	coords = np.column_stack(np.where(boardBW > 0))
	angle = cv2.minAreaRect(coords)[-1]

	if angle < -45:
		angle = -(90 + angle)
	 
	else:
		angle = -angle
		
	return angle


def tilt(image, angle):
	# rotate the image to deskew it
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	rotated = cv2.warpAffine(image, M, (w, h),
	flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

	return rotated



def get_edges(image):

	minRow = 1000000
	minColumn = 1000000
	maxRow = -10000000
	maxColumn = -1000000
	
	for row in range(0,len(image)):
		for column in range(0,len(image[0])):
			pixelValue = image[row][column]
			if pixelValue > 0:
				if minRow > row:
					minRow = row
				if maxRow < row:
					maxRow = row
				if minColumn > column:
					minColumn = column
				if maxColumn < column:
					maxColumn = column
					
	extLeft = minColumn
	extRight = maxColumn
	extTop = minRow
	extBot = maxRow
    
	return (extLeft, extRight, extBot, extTop)

# INPUT: colorful image
# OUTPUT: dictionary - location of each of the pegs
def peg_piece_locations(image):
	
	# ~ global letterToLocation
	
	# ~ boardBW = masks.black_mask_rgb(image)
	boardBW = masks.detectColor_HSV_lights(image, "black")
	
	
	
	# Correct the board tilt
	angle = whatAngle(boardBW)
	boardBW = tilt(boardBW, angle) 
	image = tilt(image, angle) 
	
	#get the max edges of the board
	(edgeLeft, edgeRight, edgeBot, edgeTop) = get_edges(boardBW)
	
	edgeRight = edgeRight +0
	edgeBot = edgeBot +0 #-5
	
	distanceFromEdge = 50
	height = (edgeBot - distanceFromEdge) - (edgeTop + distanceFromEdge)	 # distance between row A and G 
	width = (edgeRight - distanceFromEdge) - (edgeLeft + distanceFromEdge) # distance between column 1 and 10
	
	# ~ height = 300
	# ~ width = 450
	
	 
    
	# ~ distY = int(height/6) # average distance between consecutive rows (i.e. E and F)
	# ~ distX = int(width/9)  # average distance between consecutive columns (i.e. 3 and 4)

	distY = (height/12.0) # average distance between consecutive rows (i.e. E and F)
	distX = (width/18.0)  # average distance between consecutive columns (i.e. 3 and 4)
		
	print(distY)
	print(distX)
	print("------------------")

	
	bottomLeftCorner = (edgeLeft + distanceFromEdge, edgeBot - distanceFromEdge) 
	topLeftCorner = (edgeLeft + distanceFromEdge, edgeTop + distanceFromEdge)
	topRightCorner = (edgeRight - distanceFromEdge, edgeTop + distanceFromEdge)
	bottomRightCorner = (edgeRight - distanceFromEdge, edgeBot - distanceFromEdge)
	
	# ~ letters = ['G', 'F', 'E', 'D', 'C', 'B', 'A']
	# ~ letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
	letters = ['A', 'AB', 'B', 'BC', 'C', 'CD', 'D','DE', 'E', 'EF', 'F', 'FG', 'G']
	
	# ~ for num in range(0, 10):
		# ~ for letter in range(0,7):
	for num in range(0, 19):
		for letter in range(0,13):
			x = edgeLeft + distanceFromEdge + int(num*distX)
			y = edgeTop + distanceFromEdge + int(letter*distY)
			
			letterToLocation[num+1 , letters[letter]] = x, y
			
		
		
		# ~ for letter in letters:
			
			
			
			
			# ~ x = int(((9-num)/9) * (((6 - letters.index(letter))/6) * (topLeftCorner[0] + num * distX) + (letters.index(letter)/6) * (bottomLeftCorner[0] + num * distX)) +\
			# ~ (num/9) * (((6 - letters.index(letter))/6) * (topRightCorner[0] - (9 - num) * distX) + (letters.index(letter)/6) * (bottomRightCorner[0] - (9 - num) * distX)))
			# ~ y = int(((9-num)/9) * (((6 - letters.index(letter))/6) * (topLeftCorner[1] + letters.index(letter) * distY) + (letters.index(letter)/6) * (bottomLeftCorner[1] - (6 - letters.index(letter)) * distY)) +\
			# ~ (num/9) * (((6 - letters.index(letter))/6) * (topRightCorner[1] + letters.index(letter) * distY) + (letters.index(letter)/6) * (bottomRightCorner[1] - (6 - letters.index(letter)) * distY)))


			# ~ letterToLocation[num+1 , letter] = x, y
			
	for key in letterToLocation:
		cv2.circle(image, letterToLocation[key], 2, (200, 200, 200), -1)
		
	cv2.imwrite("/home/scazlab18/catkin_ws/src/P2P_tutoring/snap_circuit_cv/src/board" + '.jpg', image)
	cv2.imwrite("/home/scazlab18/catkin_ws/src/P2P_tutoring/snap_circuit_cv/src/board2" + '.jpg', boardBW)
	# ~ cv2.imshow("image_new", cv2.resize(image, (550, 400)))
	# ~ cv2.imshow("image_new2", cv2.resize(boardBW, (550, 400)))
	# ~ cv2.waitKey(0)
	
	return letterToLocation,angle


