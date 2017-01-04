#coding=utf-8
#对一批训练数据，里面包含多个文件夹，每个文件夹下面存放的是相同类别的物体
# 根据这些文件夹生成列表、切分验证、训练集数据
import os
import shutil
import  random
#因为caffe中,不允许文件名中有空格,所有需要重命名去除空格
def stdrename(imgfiles):
	for l in imgfiles:
		x_list=l.split(' ')
		y = ''.join(x_list)
		if l!=y:
			print 'rename'
			os.rename(l,y)

def GetFileList(FindPath,FlagStr=[]):
	FileList=[]
	FileNames=os.listdir(FindPath)
	if len(FileNames)>0:
		for fn in FileNames:
			if len(FlagStr)>0:
				if IsSubString(FlagStr,fn):
					fullfilename=os.path.join(FindPath,fn)
					FileList.append(fullfilename)
			else:
				fullfilename=os.path.join(FindPath,fn)
				FileList.append(fullfilename)


	if len(FileList)>0:
		FileList.sort()

	return FileList

def spiltdata(path_root,valratio=0.05):
	classify_temp=os.listdir(path_root)
	classify_file=[]
	for c in classify_temp:
		classify_file.append(os.path.join(path_root,c))



	for f in classify_file:
		imgfiles=GetFileList(f)
		stdrename(imgfiles)#caffe 文件名不允许有空格
	for c in classify_temp:
		imgfiles=os.listdir(os.path.join(path_root,c))
		nval=int(len(imgfiles)*valratio)
		print nval
		imgfvals=imgfiles[:nval]
	#验证数据文件列表
		for j in imgfvals:
			if os.path.exists(os.path.join('val',c)) is False:
				os.makedirs(os.path.join('val',c))
			newname=os.path.join('val',c)+'/'+j
			oldname=os.path.join(path_root,c)+'/'+j
			shutil.move(oldname,newname)
	#训练数据文件列表
		imgftrains=imgfiles[nval:]
		for j in imgftrains:
			if os.path.exists(os.path.join('train',c)) is False:
				os.makedirs(os.path.join('train',c))
			newname=os.path.join('train',c)+'/'+j
			oldname=os.path.join(path_root,c)+'/'+j
			shutil.move(oldname,newname)



def writetrainlist(path_root):
	oriimage_root=path_root+'/oriimage'
	classify_temp=os.listdir(oriimage_root)
	strlist=''
	for c in classify_temp:
		labelimage=os.path.join(oriimage_root,c)#原始图片作为类别标签
		croot=os.path.join(path_root,os.basename(c))
		for d in os.listdir(croot):
			trainimage=os.path.join(croot,d)

			strlist+=trainimage+' '+labelimage+'\n'



	txtlist=open(path_root+'.txt','w')
	txtlist.write(strlist)
	txtlist.close()
#无监督训练反卷积网络数据文件制作
def writeunsupervise(images_root):
	classify_temp=os.listdir(images_root)
	strlist=''
	for c in classify_temp:
		labelimage=os.path.join(images_root,c)#原始图片作为类别标签
		strlist+=labelimage+' '+labelimage+'\n'#输入等于输出



	txtlist=open(images_root+'.txt','w')
	txtlist.write(strlist)
	txtlist.close()



#spiltdata('newtrain')
#writetrainlist('../data')
#writeunsupervise('../data/oriimage')
#writetrainlist('newtrain_val')




