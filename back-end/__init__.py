from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import numpy as np
import tensorflow as tf
import os
from flask import Flask, render_template, request, jsonify, redirect
from PIL import Image
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = "/var/www/FlaskApp/FlaskApp/static/images"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# index = 0

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) 
    if file.filename not in os.listdir(UPLOAD_FOLDER):
    	file.save(f)
    # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)
#     global index
#     file_name = UPLOAD_FOLDER +"/img" +str(index) +".png"
#     index += 1
#     os.rename(f, file_name)
    try:
    	temp = main(f)
    	if not temp:
    		return render_template('error.html')   	
    	return redirect("https://www.edmunds.com/" + temp)
    except:
    	return render_template('error.html') 
    	
def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(
        file_reader, channels=3, name="png_reader")
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(
        tf.image.decode_gif(file_reader, name="gif_reader"))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
  else:
    image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


def main(file_name):
  path = "/var/www/FlaskApp/FlaskApp/static/images"
  model_file = "/var/www/FlaskApp/FlaskApp/output_graph.pb"
  label_file = "/var/www/FlaskApp/FlaskApp/output_labels.txt"
  input_height = 299
  input_width = 299
  input_mean = 0
  input_std = 255
  input_layer = "Placeholder"
  output_layer = "final_result"

#   for filename in os.listdir(path):
#   	os.rename(path+"/"+filename, path +"/myimage.png")
#   	file_name = path + "/myimage.png"
  	
  graph = load_graph(model_file)
  t = read_tensor_from_image_file(
      file_name,
      input_height=input_height,
      input_width=input_width,
      input_mean=input_mean,
      input_std=input_std)

  input_name = "import/" + input_layer
  output_name = "import/" + output_layer
  input_operation = graph.get_operation_by_name(input_name)
  output_operation = graph.get_operation_by_name(output_name)

  with tf.Session(graph=graph) as sess:
    results = sess.run(output_operation.outputs[0], {
        input_operation.outputs[0]: t
    })
  results = np.squeeze(results)

  top_k = results.argsort()[-5:][::-1]
  labels = load_labels(label_file)
  top_result = top_k[0]
  
#   os.remove(file_name)
  
  return labels[top_result]
  # for i in top_k:
  #   print(labels[i], results[i])
  #   print(results)

if __name__ == "__main__":
  app.run() 