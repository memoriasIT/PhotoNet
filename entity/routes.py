from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import functools
from app import db, app
from bson import ObjectId
import pymongo
import os
import requests
import json
import re

photos = db['photonet']

# Flickr
ImageURLUpload = "https://api.imgbb.com/1/upload"
Expiration = "" # in seconds
ImageAPIKey = ""

# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

@app.route('/directorio', methods=['GET', 'POST'])
@login_required
def showDirectorio():
  if request.method == 'GET' :
    return render_template('directorio.html', photos = list(photos.find().sort('likes',pymongo.DESCENDING)))
  else:
    search = request.form['busqueda']

    return render_template(
      'directorio.html', busqueda=search,
      photos = list(photos.find(
                      {"descripcion" : {'$regex': search}}
                      ).sort('likes',pymongo.DESCENDING)))


@app.route('/new', methods = ['GET', 'POST'])
def newAd():

    if request.method == 'GET' :
        return render_template('new.html')
    else:
      # UPLOAD image
      try:
        fileURL = ""
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            
            # return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
        if file:
          print(file)

          fullImageUploadURL = "https://api.imgbb.com/1/upload?expiration=" + Expiration + "&key= " + ImageAPIKey
          files=[
            ('image', file)
          ]
          response = requests.request("POST", fullImageUploadURL, files=files)

          data = json.loads(response.text)
          print(data)
          fileURL = data["data"]['url'] 
          print(fileURL)
      except:
        fileURL = ""
      
      
      hashtagsDB = []
      # try:
      hashtagsRaw = request.form['descripcion']
      delimiters = [' ', '.', ',', ':']
      hashedWords = get_hashed_words(hashtagsRaw, delimiters)
      
      print(hashedWords)
      for elem in hashedWords:
        hashtagsDB.append(elem)
      

      entrada = {
        'imagen' : fileURL,
        'descripcion': request.form['descripcion'],
        'likes': int(0), 
        'hashtags' : hashtagsDB,
        'email': session['user']['email']
        
      }

      

      # ADD TO DB
      photos.insert_one(entrada)
      return redirect(url_for('showDirectorio'))

@app.route('/like/<_id>', methods = ['GET', 'POST'])
def like(_id):
  # #Only one like per user
  # if db.users.find(
  #   { "email": session['user']['email'] },
  #   { "likes": str(_id) }
  #   ).count() == 0 :
    
  #   print("LIKE")
  #   # Like
  #   db.users.update_one(
  #     {'_id': ObjectId(_id) }, 
  #     { '$push': { 'likes': _id }}
  #   )
  photos.update_one(
    {'_id': ObjectId(_id) }, 
    { '$inc': { 'likes': +1 }}
  )   
  # else:
  #   print("NOT LIKE") 
  return redirect(url_for('showDirectorio'))

@app.route('/edit/<_id>', methods = ['GET', 'POST'])
def editEntrada(_id):
    
    if request.method == 'GET' :
        entrada = photos.find_one({'_id': ObjectId(_id)})
        return render_template('edit.html', entrada = entrada)
    else:
      # UPLOAD image
      try:
        fileURL = ""
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            
            # return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
        if file:
          print(file)

          fullImageUploadURL = "https://api.imgbb.com/1/upload?expiration=" + Expiration + "&key= " + ImageAPIKey
          files=[
            ('image', file)
          ]
          response = requests.request("POST", fullImageUploadURL, files=files)

          data = json.loads(response.text)
          print(data)
          fileURL = data["data"]['url'] 
          print(fileURL)
      except:
        fileURL = ""

      hashtagsDB = []
      # try:
      hashtagsRaw = request.form['descripcion']
      delimiters = [' ', '.', ',', ':']
      hashedWords = get_hashed_words(hashtagsRaw, delimiters)
      
      print(hashedWords)
      for elem in hashedWords:
        hashtagsDB.append(elem)
      # except:
      #   pass

      entrada = {
        'imagen' : fileURL,
        'descripcion': request.form['descripcion'],
        'hashtags' : hashtagsDB,
      }


      photos.update_one({'_id': ObjectId(_id) }, { '$set': entrada })    
      return redirect(url_for('showDirectorio'))


@app.route('/view/<_id>', methods = ['GET'])
def viewEntrada(_id):
  if request.method == 'GET' :
      entrada = directorio.find_one({'_id': ObjectId(_id)})
      return render_template('view.html', entrada = entrada)


@app.route('/delete/<_id>', methods = ['GET'])
def deleteAd(_id):
    
    photos.delete_one({'_id': ObjectId(_id)})
    return redirect(url_for('showDirectorio'))




# HASHTAGS
def hash_position(string):
    return string.find('#')

def delimiter_position(string, delimiters):
    positions = filter(lambda x: x >= 0, map(lambda delimiter: string.find(delimiter), delimiters))
    try:
        return functools.reduce(min, positions)
    except TypeError:
        return -1

def get_hashed_words(string, delimiters):
    maximum_length = len(string)
    current_hash_position = hash_position(string)
    string = string[current_hash_position:]
    results = []
    counter = 0
    while current_hash_position != -1:
        current_delimiter_position = delimiter_position(string, delimiters)
        if current_delimiter_position == -1:
            results.append(string)
        else:
            results.append(string[0:current_delimiter_position])
        # Update offsets and the haystack
        string = string[current_delimiter_position:]
        current_hash_position = hash_position(string)
        string = string[current_hash_position:]
    return results