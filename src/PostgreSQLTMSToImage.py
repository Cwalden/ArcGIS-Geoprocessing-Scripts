import psycopg2
import numpy
import Image
import arcpy
from scipy.sparse import *
CELLSIZE = 1222.9924525618553 #cell size at zoom 15
OFFSET = 20037508.3428        #offset for the web mercator projection
speciesID= arcpy.GetParameterAsText(0)
conn = psycopg2.connect(host="durga.jrc.org", database="dbdopa", user="usrdopa", password="W25e12b")
cur = conn.cursor()
cur.execute("SELECT tx,ty,z FROM public.pilotspeciesdata WHERE speciesid='" + speciesID + "'")
rows=cur.fetchall()
data3d=numpy.transpose(numpy.array(rows))
minx=min(data3d[0]) #get the minx value
maxx=max(data3d[0]) #get the maxx value
miny=min(data3d[1]) #get the miny value
maxy=max(data3d[1]) #get the maxy value
width=maxx-minx+1   #get the width of the resulting image
height=maxy-miny+1  #get the height of the resulting image
data3d[0].__isub__(minx) #change the x values to be zero based by subtracting the minx value
data3d[1].__imul__(-1)   #do the same with the y values using a different calculation
data3d[1].__iadd__(maxy)
pixels=coo_matrix((data3d[2],(data3d[1],data3d[0])), shape=(height,width)).todense() #convert the sparse array into a dense matrix, i.e. by adding in all of the zero values
image = Image.fromarray(pixels) #create the output tif from the pixel values
imagefile=r"E:\cottaan\My Documents\ArcGIS\ID" + speciesID + ".tif"
image.save(imagefile) #save the image to a file
f = open(imagefile[:-3] + "tfw",'w') #open the tfw file to write the georeferencing coordinates in
f.write(str(CELLSIZE) + "\n0.0000000000\n0.0000000000\n-" + str(CELLSIZE) + "\n") #you need to set the y cell size as a minus number otherwise the image is upside down
topleftx=(minx*CELLSIZE)- OFFSET + (CELLSIZE/2) #get the top left x coordinate
toplefty=(maxy*CELLSIZE)- OFFSET + (CELLSIZE/2) #get the top left y coordinate
f.write(str(topleftx) + "\n")  #top left x coordinate
f.write(str(toplefty) + "\n")  #top left y coordinate
f.close() #close the file