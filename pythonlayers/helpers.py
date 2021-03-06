# --------------------------------------------------------
# floor_recog
# Written by Sai Prabhakar
# CMU-RI Masters
# --------------------------------------------------------

#helper function for blob loading and stuff

import numpy as np
import cv2
import caffe
from random import randint


def im_list_to_blob(ims):
    """Convert a list of images into a network input.

    Assumes images are already prepared (means subtracted, BGR order, ...).
    """
    max_shape = [227, 227]  #np.array([im.shape for im in ims]).max(axis=0)
    num_images = len(ims)
    #print "num images ", num_images
    blob = np.zeros(
        (num_images, max_shape[0], max_shape[1], 3), dtype=np.float32)
    for i in xrange(num_images):
        im = ims[i]
        blob[i, 0:im.shape[0], 0:im.shape[1], :] = im
    # Move channels (axis 3) to axis 1
    # Axis order will become: (batch elem, channel, height, width)
    channel_swap = (0, 3, 1, 2)
    blob = blob.transpose(channel_swap)
    return blob


def im_to_blob(im):
    """Convert a list of images into a network input.

    Assumes images are already prepared (means subtracted, BGR order, ...).
    """
    max_shape = im.shape
    blob = np.zeros((1, max_shape[0], max_shape[1], 3), dtype=np.float32)
    blob[0, 0:im.shape[0], 0:im.shape[1], :] = im

    # Move channels (axis 3) to axis 1
    # Axis order will become: (batch elem, channel, height, width)
    channel_swap = (0, 3, 1, 2)
    blob = blob.transpose(channel_swap)
    return blob


def _get_image_from_binaryproto(fileName):
    """Returns image from binaryproto
    """
    blob = caffe.proto.caffe_pb2.BlobProto()
    data = open(fileName, 'rb').read()
    blob.ParseFromString(data)
    arr = np.array(caffe.io.blobproto_to_array(blob))
    arr = np.squeeze(arr.transpose((2, 3, 1, 0)))

    #im_scaley = float(im_target_size) / float(256)
    #im_scalex = float(im_target_size) / float(256)
    #meanImg = cv2.resize(arr, None, None, fx=im_scalex, fy=im_scaley,
    #                interpolation=cv2.INTER_LINEAR)

    return arr


def _image_processor(imageName, mean_image, scale_min_size, final_image_size):
    """Loads image and prepares image (mean subtraction, random cropping
    ...), in BGR order.
    """
    im = cv2.imread(imageName)
    #print imageName
    target_size = scale_min_size
    min_curr_size = min(im.shape[:2])
    im_scale = float(target_size) / float(min_curr_size)
    #im_scalex = float(target_size) / float(im.shape[1])
    im = cv2.resize(
        im[:min_curr_size, :min_curr_size, :],
        None,
        None,
        fx=im_scale,
        fy=im_scale,
        interpolation=cv2.INTER_LINEAR)
    im = im.astype(np.float32)
    im -= mean_image
    #TODO augumentation
    xrand = randint(0, scale_min_size - final_image_size)
    yrand = randint(0, scale_min_size - final_image_size)
    im_processed = im[yrand:yrand + final_image_size, xrand:xrand +
                      final_image_size, :]

    #import IPython
    #IPython.embed()
    return im_processed


def _get_image_list_blob(im_list, mean_image, scale_min_size,
                         final_image_size):
    #"""Takes in a list of image name, mean file, scaling size
    #and final image size.
    #
    #Generates blob of processed image.
    #"""
    num_images = len(im_list)
    processed_ims = []
    for i in xrange(num_images):
        processed_ims.append(
            _image_processor(im_list[i][0], mean_image, scale_min_size,
                             final_image_size))
    #Create a blob to hold the input images
    blob = im_list_to_blob(processed_ims)

    return blob


def _get_label_blob(im_list1):
    #import IPython
    #IPython.embed()
    label = np.array([im_list1[i][1] for i in range(len(im_list1))]) - 2
    return label.astype(np.float32)


def _get_sim_list_blob(im_list1, im_list2):
    """Takes in list of tuples of imagename and the
    corresponding class.

    Generate similarity data label.
    """
    #blob = np.zeros(len(im_list1), dtype=np.float32)
    #blob = np.zeros( len(im_list1), dtype=np.float32)
    sim = np.array([1 if im_list1[i][1] == im_list2[i][1] else 0
                    for i in range(len(im_list1))])
    #sim = sim[:, np.newaxis, np.newaxis, np.newaxis]
    #import IPython
    #IPython.embed()
    blob = sim.astype(np.float32)
    return blob
