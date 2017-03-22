import sys
import nibabel as nib
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3' #Suppress TF FYIs below ERROR
import numpy as np
import tensorflow as tf
import tfbasic

def main():


    def subsectimage (f, img_data,start,stop): #function will take an image and slice it
        for i in range(start,stop+1):
            slice = img_data[: , i, :] # the ith slice, x<=i<=y
            filesave = f[0:5] + '-' + str(i) + '.dat'
            slice.dump(filesave)


    def reshapelabels(labels):
    #Reshape labels into mx3 matrix
    #1 = NPH, 2 = AD, 3 = Normal Control
    #1 = 100, 2 = 010, 3 = 001
        newlabels = np.empty((0,3))
        for i in labels:
            if i == 1:
                newlabels = np.vstack((newlabels,[1,0,0]))
            if i == 2:
                newlabels = np.vstack((newlabels,[0,1,0]))
            if i == 3:
                newlabels = np.vstack((newlabels,[0,0,1]))
        return newlabels

    def caselookup(casenums):
        casepairs = np.empty((0,1))
        for i in casenums: #for every case in casenums
            pairind = np.where(casekey[:,0]==i)[0]#lookup index of i-th case w/in casekey
            # pairind[0] holds index within casekey
            pair = casekey[pairind,1]
            casepairs= np.vstack((casepairs,pair))   
        return casepairs


    print 'program started' #debugging
    cwd = os.getcwd()
    slicesfilepath = cwd + "/slices"
    validationfilepath = slicesfilepath + "/Validation"

    numpixels = 256 * 256
    isaxial = True
    isnarrowaxial = True
    fstart = -1
    fstop = -1
    os.chdir(slicesfilepath)
    
    if 'validationnums.dat' in os.listdir(slicesfilepath):
        flatcasesmatrix = np.load('flatcasesmatrix.dat')
        casenums=np.load('casenums.dat')
        flatvalidationmatrix = np.load('flatvalidationmatrix.dat')
        validationnums = np.load('validationnums.dat')
        print 'flatcasesmatrix, casenums loaded'
        
        #Whatever command
    else:
        print 'slicing images'
        os.chdir(cwd)
        caseindices = np.genfromtxt('casesliceindices.csv', delimiter=',') #case 1 is indexed as 0, etc
        os.chdir(slicesfilepath)
        for f in os.listdir(slicesfilepath):
            if f.find('.nii') != -1: #If it's a .nii file
                epi_img = nib.load(f)
                epi_img_data = epi_img.get_data()
                if epi_img_data.shape[0] * epi_img_data.shape[1] == numpixels:
                    findex = int(f[1:5])-1
                    if isaxial and isnarrowaxial:                    
                        fstart = caseindices[findex,1]
                        fstop = caseindices[findex,2]
                    elif isaxial == True and isnarrowaxial == False:
                        fstart = caseindices[findex,0]
                        fstop = caseindices[findex,3]
                    else:
                        fstart = caseindices[findex,4]
                        fstop = caseindices[findex,5]
                    fstart = int(fstart)
                    fstop = int(fstop)
                    subsectimage(f,epi_img_data,fstart,fstop)


        os.chdir(validationfilepath)
        for f in os.listdir(validationfilepath):
            if f.find('.nii') != -1: #If it's a .nii file
                epi_img = nib.load(f)
                epi_img_data = epi_img.get_data()
                if epi_img_data.shape[0] * epi_img_data.shape[1] == numpixels:
                    findex = int(f[1:5])-1
                    if isaxial and isnarrowaxial:                    
                        fstart = caseindices[findex,1]
                        fstop = caseindices[findex,2]
                    elif isaxial == True and isnarrowaxial == False:
                        fstart = caseindices[findex,0]
                        fstop = caseindices[findex,3]
                    else:
                        fstart = caseindices[findex,4]
                        fstop = caseindices[findex,5]
                    fstart = int(fstart)
                    fstop = int(fstop)
                    subsectimage(f,epi_img_data,fstart,fstop)

    
    # This process will flatten all '.dat' files into one matrix and track labels

    # initializations, constants
        flatcasesmatrix = np.empty((0,numpixels))
        flatvalidationmatrix = np.empty((0,numpixels))
        casenums = np.empty((0,1))
        validationnums = np.empty((0,1))
        counter = 0

        os.chdir(slicesfilepath)
        for i in os.listdir(slicesfilepath):
            if '.dat' in i:
                boxdata = np.load(i) # load the data
                if boxdata.shape[0]*boxdata.shape[1]==numpixels:
                    flatdata = boxdata.flatten() # flatten the data
                    flatdata.shape = (1,numpixels) #make the data horizontal
                    flatcasesmatrix = np.vstack((flatcasesmatrix,flatdata)) # flatten data
                    casenums = np.vstack((casenums,int(str(i[1:5])))) # store casenumber
                    counter = counter +1
                '''if counter > 25: break #for debugging'''

        os.chdir(validationfilepath)
        for i in os.listdir(validationfilepath):
            if '.dat' in i:
                boxdata = np.load(i) # load the data
                if boxdata.shape[0]*boxdata.shape[1]==numpixels:
                    flatdata = boxdata.flatten() # flatten the data
                    flatdata.shape = (1,numpixels) #make the data horizontal
                    flatvalidationmatrix = np.vstack((flatvalidationmatrix,flatdata))
                    validationnums = np.vstack((validationnums,int(str(i[1:5]))))
                    counter = counter +1

        
        os.chdir(slicesfilepath)
        flatcasesmatrix.dump('flatcasesmatrix.dat')
        casenums.dump('casenums.dat')
        flatvalidationmatrix.dump('flatvalidationmatrix.dat')
        validationnums.dump('validationnums.dat')
        print 'flatcasesmatrix, casenums created and saved'
        print counter,' flat case matrix generated'



    print flatcasesmatrix.shape, ' flat case matrix shape'
    '''print casenums'''
    print casenums.shape, ' casenums shape'
    print flatvalidationmatrix.shape, ' validation shape'
    
    casekeyfilepath =cwd
    os.chdir(casekeyfilepath)
    casekey = np.genfromtxt('casekey.csv',delimiter=',')
    
    labels = caselookup(casenums) #returns list of labels 
    validationlabels = caselookup(validationnums)

    labels = reshapelabels(labels)
    validationlabels = reshapelabels(validationlabels)
    if len(sys.argv) == 1:
        print 'running on default gpu'
        tfbasic.main(flatcasesmatrix,labels,flatvalidationmatrix,validationlabels)
    
    else:
        gpuname = sys.argv[1]
        gpuname = '/gpu:' + gpuname
        print 'running on specified gpu'
        with tf.device(gpuname):
            tfbasic.main(flatcasesmatrix,labels)

if __name__ == '__main__':
	main()
