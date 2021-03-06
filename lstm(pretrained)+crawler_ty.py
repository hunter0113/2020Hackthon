# -*- coding: utf-8 -*-
"""LSTM(pretrained)+Crawler_ty.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ay3XF4b2b1wE46M8ua-e_MKN2xHs8HFQ
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from itertools import accumulate

from google.colab import drive
drive.mount('/content/drive')

import pickle
import numpy as np
import pandas as pd
from keras.utils import np_utils, plot_model
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.layers import LSTM, Dense, Embedding, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 匯入資料
# 檔案的資料中，特徵為Comment, 類別為label.
def load_data(filepath, input_shape=20):
    df = pd.read_csv(filepath, encoding = 'utf_8')  # big5, big5hkscs, cp950, utf_8

    # 標籤及詞彙表
    labels, vocabulary = list(df['label'].unique()), list(df['Comment'].unique())

    # 構造字元級別的特徵
    string = ''
    #stops = ["不過","Apple","apple","蘋果","哀鳳","Watch","watch","pro","htc","HTC","Zenfone","zf","zf6","ZF6","ZF7","zf3","u11","u12","U11","U12","U20","pro","5Z","10","小米","oppo","OPPO","4a","ASUS","asus"]

    for word in vocabulary:
      #if word not in stops:
        string += word

    vocabulary = set(string)

    # 字典列表
    word_dictionary = {word: i+1 for i, word in enumerate(vocabulary)}
    with open('/content/drive/My Drive/Hackthon/word_dict.pk', 'wb') as f:
        pickle.dump(word_dictionary, f)
    inverse_word_dictionary = {i+1: word for i, word in enumerate(vocabulary)}
    label_dictionary = {label: i for i, label in enumerate(labels)}
    with open('/content/drive/My Drive/Hackthon/label_dict.pk', 'wb') as f:
        pickle.dump(label_dictionary, f)
    output_dictionary = {i: labels for i, labels in enumerate(labels)}

    vocab_size = len(word_dictionary.keys()) # 詞彙表大小
    label_size = len(label_dictionary.keys()) # 標籤類別數量

    # 序列填充，按input_shape填充，長度不足的按0補充
    x = [[word_dictionary[word] for word in sent] for sent in df['Comment']]
    x = pad_sequences(maxlen=input_shape, sequences=x, padding='post', value=0)
    y = [[label_dictionary[sent]] for sent in df['label']]
    y = [np_utils.to_categorical(label, num_classes=label_size) for label in y]
    y = np.array([list(_[0]) for _ in y])

    return x, y, output_dictionary, vocab_size, label_size, inverse_word_dictionary

# 建立深度學習模型， Embedding + LSTM + Softmax.
def create_LSTM(n_units, input_shape, output_dim, filepath):
    x, y, output_dictionary, vocab_size, label_size, inverse_word_dictionary = load_data(filepath)
    model = Sequential()
    model.add(Embedding(input_dim=vocab_size + 1, output_dim=output_dim,
                        input_length=input_shape, mask_zero=True))
    model.add(LSTM(n_units, input_shape=(x.shape[0], x.shape[1])))
    model.add(Dropout(0.2))
    model.add(Dense(label_size, activation='sigmoid'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    plot_model(model, to_file='./model_lstm.png', show_shapes=True)
    model.summary()

    return model

# 模型訓練
def model_train(input_shape, filepath, model_save_path):

    # 將資料集分為訓練集和測試集，佔比為9:1
    # input_shape = 100
    x, y, output_dictionary, vocab_size, label_size, inverse_word_dictionary = load_data(filepath, input_shape)
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size = 0.1, random_state = 42)

    # 模型輸入引數，需要自己根據需要調整
    n_units = 100
    batch_size = 32
    epochs = 6
    output_dim = 20

    # 模型訓練
    lstm_model = create_LSTM(n_units, input_shape, output_dim, filepath)
    lstm_model.fit(train_x, train_y, epochs=epochs, batch_size=batch_size, verbose=1)

    # 模型儲存
    lstm_model.save(model_save_path)

    N = test_x.shape[0]  # 測試的條數
    predict = []
    label = []
    for start, end in zip(range(0, N, 1), range(1, N+1, 1)):
        sentence = [inverse_word_dictionary[i] for i in test_x[start] if i != 0]
        y_predict = lstm_model.predict(test_x[start:end])
        label_predict = output_dictionary[np.argmax(y_predict[0])]
        label_true = output_dictionary[np.argmax(test_y[start:end])]
        print(''.join(sentence), label_true, label_predict) # 輸出預測結果
        predict.append(label_predict)
        label.append(label_true)

    acc = accuracy_score(predict, label) # 預測準確率
    print('模型在測試集上的準確率為: %s.' % acc)

if __name__ == '__main__':
    filepath = '/content/drive/My Drive/Hackthon/Done/Data/Comment_All.csv'
    input_shape = 27
    model_save_path = '/content/drive/My Drive/Hackthon/save_model.h5'
    model_train(input_shape, filepath, model_save_path)

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import argparse
import re

def Market_Analysis(keyword, pageNum):
  import requests
  from bs4 import BeautifulSoup
  from tqdm import tqdm
  import pandas as pd
  import argparse
  import re
  url='https://www.ptt.cc/bbs/MobileComm/search?q='+keyword #  定義搜尋關鍵字
  # 爬蟲設定(數量)
  
  #pageNum = 3 #要搜尋幾頁
  #all_href = []
  for page in range(1,pageNum):
      r = requests.get(url)
      soup = BeautifulSoup(r.text,"html.parser")
      btn = soup.select('div.btn-group > a')
      try:
        up_page_href = btn[3]['href']
        next_page_url = 'https://www.ptt.cc' + up_page_href
        url = next_page_url
        results = soup.select("div.title")
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.select("div.title")
        all_href = []
        for item in results:
            a_item = item.select_one("a")
            title = item.text
            if a_item:
                print(title, 'https://www.ptt.cc'+ a_item.get('href'))
                all_href.append('https://www.ptt.cc'+ a_item.get('href')) 
        all_soup = []
        for i in range(len(all_href)):
            res = requests.get(all_href[i])
            soup = BeautifulSoup(res.text)
            all_soup.append(soup)
        push = []
        for i in range(len(all_soup)):
          push_content = all_soup[i].select(".push-content")
          #print("第"+ str(i+1) +"篇")
          for j in range(len(push_content)):
            push_text = push_content[j].text.replace(": ","")
            print(push_text)
            push.append(push_content[j].text.replace(": ",""))
        with open('/content/drive/My Drive/Hackthon/word_dict.pk', 'rb') as f:
            word_dictionary = pickle.load(f)
        with open('/content/drive/My Drive/Hackthon/label_dict.pk', 'rb') as f:
            output_dictionary = pickle.load(f)
        

        push = []
        Pos = 0
        Neg = 0
        Other = 0
        PosComment = []
        NegComment = []

        for i in range(len(all_soup)):
          push_content = all_soup[i].select(".push-content")
          #print("第"+ str(i+1) +"篇")
          for j in range(len(push_content)):
            push_text = push_content[j].text.replace(": ","")
            #print(push_text)
            push.append(push_content[j].text.replace(": ",""))
            try:
              # 資料預處理
              input_shape = 27
              sent = push_content[j].text.replace(": ","")
              x = [[word_dictionary[word] for word in sent]]
              x = pad_sequences(maxlen=input_shape, sequences=x, padding='post', value=0)

              # 載入模型
              model_save_path = '/content/drive/My Drive/Hackthon/save_model.h5'
              lstm_model = load_model(model_save_path)

              # 模型預測
              y_predict = lstm_model.predict(x)
              label_dict = {v:k for k,v in output_dictionary.items()}
              print('輸入語句: %s' % sent)
              print('情感預測結果: %s' % label_dict[np.argmax(y_predict)])

              # 列出1、2 的結果
              if label_dict[np.argmax(y_predict)] == 0:
                Pos+=1
                PosComment.append(sent)
              elif label_dict[np.argmax(y_predict)] == 1:
                Neg+=1
                NegComment.append(sent)
              elif label_dict[np.argmax(y_predict)] == 2:
                Other+=1

            except KeyError as err:
              print("您輸入的句子有漢字不在詞彙表中，請重新輸入！")
              print("不在詞彙表中的單詞為：%s." % err)
              
        print('\n----------------------------------------------\n')
        print('正面評價: %d'%(Pos))
        print('負面評價: %d'%(Neg))
        print('其他評價: %d\n'%(Other))
        print('正面評價:\n')
        for k in range(len(PosComment)):
          print(PosComment[k])
                
        print('負面評價:\n')
        for k in range(len(NegComment)):
          print(NegComment[k])
      except KeyError as err:
        break

Market_Analysis(keyword='apple', pageNum = 2)

print('正面評價:\n')
for k in range(len(PosComment)):
  print(PosComment[k])

print('負面評價:\n')
for k in range(len(NegComment)):
  print(NegComment[k])