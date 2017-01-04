#coding=utf-8
#tensorflow高效数据读取训练
import tensorflow as tf
import cv2
import  random

#把train.txt文件格式，每一行：图片路径名   类别标签
#奖数据打包，转换成tfrecords格式，以便后续高效读取
def encode_to_tfrecords(lable_file,data_root,new_name='data.tfrecords',resize=None):
    labelfile_lines=[]
    with open(lable_file,'r') as f:
        for l in f.readlines():
            labelfile_lines.append(l)
        random.shuffle(labelfile_lines)
    print "样本数据量：",len(labelfile_lines)

    writer=tf.python_io.TFRecordWriter(data_root+'/'+new_name)
    num_example=0
    for l in labelfile_lines:
        l=l.split()
        image=cv2.imread(data_root+"/"+l[0])
        label=cv2.imread(data_root+'/'+l[1])
        image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        label=cv2.cvtColor(label,cv2.COLOR_BGR2GRAY)
        if resize is not None:
            image=cv2.resize(image,resize)#为了
            label=cv2.resize(label,resize)
        #cv2.imshow("fa",label)
        #cv2.waitKey(0)
        #print image
        height,width=image.shape
        nchannel=1


        example=tf.train.Example(features=tf.train.Features(feature={
            'height':tf.train.Feature(int64_list=tf.train.Int64List(value=[height])),
            'width':tf.train.Feature(int64_list=tf.train.Int64List(value=[width])),
            'nchannel':tf.train.Feature(int64_list=tf.train.Int64List(value=[nchannel])),
            'image':tf.train.Feature(bytes_list=tf.train.BytesList(value=[image.tobytes()])),
            'label':tf.train.Feature(bytes_list=tf.train.BytesList(value=[label.tobytes()]))
        }))
        serialized=example.SerializeToString()
        writer.write(serialized)
        num_example+=1
        print num_example


    writer.close()
#读取tfrecords文件
def decode_from_tfrecords(filename,istrain=True,num_epoch=None):
    filename_queue=tf.train.string_input_producer([filename,filename,filename,filename],num_epochs=num_epoch)#因为有的训练数据过于庞大，被分成了很多个文件，所以第一个参数就是文件列表名参数


    reader=tf.TFRecordReader()
    _,serialized=reader.read(filename_queue)









    example=tf.parse_single_example(serialized,features={
        'height':tf.FixedLenFeature([],tf.int64),
        'width':tf.FixedLenFeature([],tf.int64),
        'nchannel':tf.FixedLenFeature([],tf.int64),
        'image':tf.FixedLenFeature([],tf.string),
        'label':tf.FixedLenFeature([],tf.string)
    })

    image=tf.decode_raw(example['image'],tf.uint8)
    image=tf.reshape(image,tf.pack([
        tf.cast(example['height'], tf.int32),
        tf.cast(example['width'], tf.int32),
        tf.cast(example['nchannel'], tf.int32)]))


    label=tf.decode_raw(example['label'], tf.uint8)
    label=tf.reshape(label,tf.pack([
        tf.cast(example['height'], tf.int32),
        tf.cast(example['width'], tf.int32),
        tf.cast(example['nchannel'], tf.int32)]))
    return image,label
#根据队列流数据格式，解压出一张图片后，输入一张图片，对其做预处理、及样本随机扩充
def get_batch(image, label, batch_size,shape):


    #生成batch
    #shuffle_batch的参数：capacity用于定义shuttle的范围，如果是对整个训练数据集，获取batch，那么capacity就应该够大
    #保证数据打的足够乱
    image=tf.reshape(image,shape)
    label=tf.reshape(label,shape)
    images, label_batch = tf.train.shuffle_batch([image, label],batch_size=batch_size,
                                                 num_threads=8,capacity=1000+3*128,min_after_dequeue=1000)

    #images, label_batch=tf.train.batch([distorted_image, label],batch_size=batch_size)



    # 调试显示
    #tf.image_summary('images', images)
    return images, label_batch#tf.reshape(label_batch, [batch_size])
#这个是用于测试阶段，使用的get_batch函数
def get_test_batch(image, label, batch_size,crop_size,ori_size):
        #数据扩充变换
    #distorted_image=tf.image.central_crop(image,float(crop_size)/ori_size)
    #distorted_image = tf.random_crop(distorted_image, [crop_size, crop_size, 3])#随机裁剪
    distorted_image=image
    images, label_batch=tf.train.batch([distorted_image, label],num_threads=8,batch_size=batch_size)
    return images, tf.reshape(label_batch, [batch_size])






#直接加载所有的训练样本到内存，而不是在线加载的方式，适用于小数据
def preload_data(data_path):
    image,label=decode_from_tfrecords(data_path,num_epoch=1)
    image_nps=[]
    label_nps=[]
    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        try:
            while True:
                image_np,label_np=session.run([image,label])
                image_nps.append(image_np)
                label_nps.append(label_np)
                print len(image_nps)
        except OutOfRangeError, e:
            coord.request_stop(e)
        finally:
            coord.request_stop()
            coord.join(threads)


    return image_nps,label_nps


#测试上面的压缩、解压代码
def test():
    encode_to_tfrecords("../data/oriimage.txt","../data",'data.tfrecords',(224,224))
    image,label=decode_from_tfrecords('../data/data.tfrecords')
    batch_image,batch_label=get_batch(image,label,2,[224,224,1])#batch 生成测试
    init=tf.initialize_all_variables()
    with tf.Session() as session:
        session.run(init)
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        for l in range(100):#每run一次，就会指向下一个样本，一直循环
            #image_np,label_np=session.run([image,label])#每调用run一次，那么
            '''cv2.imshow("temp",image_np)
            cv2.waitKey()'''
            #print label_np
            #print image_np.shape


            batch_image_np,batch_label_np=session.run([batch_image,batch_label])
            print "image shape:",batch_image_np.shape
            print "label shape:",batch_label_np.shape



        coord.request_stop()#queue需要关闭，否则报错
        coord.join(threads)
#test()
#ti,tl=preload_data('../data/mutil-light/val.tfrecords')



