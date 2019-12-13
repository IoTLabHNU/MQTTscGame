#MQTT TestClient GUI
"""
Author      : Marcell Oosthuizen 
Project     : Supply Chain Game
School      : HNU & UWC

Description 
-------------
This project is a collaboration between HNU university of applied Sciences and UWC from Germany and South Africa respectively.
The project concerns the flow of products and information in complex supply chains. This information is used to introduce students
to the nature of supply chain management. Some learning objectives include lean management of stock and product flow on terms of inbound
and outbound.
There are two scripts for this game to work. This Client.py script for clients and the Admin.py script which is for the admin

What is this script ?
---------------------
This script functions as the client side , meaning the tiers which will consist of 4 different clients(Differentiated by the ID used at connect)
This scrip houses the UI and functionality of producing products , ordering products and delivering products as well as receiving products.

How does it work ?
------------------
The following steps it what is needed to follow in order to reproduce the desired result of a working client:
    ->run the script using python3 Client.py
    ->Enter the ID of the client(assigned tier from one to four)
    ->The script will then try to connect to the hive MQTT broker
    ->If the connection was successful a connected text will appear next to the button connect(This is essential)
    ->After this the client will be in a standby state , waiting for the admin pi to issue orders(start round,stop round, and more)
    ->User can use the production,order and deliver buttons during a round. Order and deliver can only be used once. Production more than once.
    ->When the admin pi signals the round to stop , most of the functions will grey out, but the get delivery button will become available
    ->The get delivery button can be used once and it is crucial that even if you deliver nothing that the tag is scanned with 0 as the inputs.
    ->After 20 seconds the next round will start and the UI will be available for use again
    ->This cycle will repeat until the game is quite, or the admin stops the game.
    ->If the admin quits , the client's should quit as well.

How is data handeled in the game:
---------------------------------
At start:
The game starts as a blank but when the client connects to the hive MQTT broker the client will lie dormant until the admin is connected 
to the broker. When the admin connects to the broker, the admin will share the starting information of the game. This information is shaherd
via a MQTT publish from the admin's side. The client will then receive the data as a JSON object consisting of an array of array's.(2D array)
This object will have the starting data for the game and once this is received the values of all the lables will change.

During the game:
    While the game is played the variables I use to do data operations upon(given production,delivery or orders) will be the lables themselfs.

Storage:
    Transcations for the game will be stored in a mysql database. This meaing from transactions like production to to round additions and backlog entries.
    The list of products that is shared in the beginning from the admin will also be sotred.
    Important ! When a client was persay client 1 in the past before the client can be assigned another number the db must be cleaned !
    The reason for this is the product list and how its set up.

Also important:
    In the documentation and comments when I refer to client , this script is implied. When I refer to Admin , the admin script is implied.

"""




"""
    Imports used to make this client interface work
"""
import tkinter as tk
from tkinter import *
import paho.mqtt.client as mqtt
from initialClientDataList import initialClientDataList
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import threading
from threading import Timer
import time

"""
Constant variables , mostly used for topics that is subscribed and published to
"""
CONST_TOPIC_START_ROUND = "startRound"
CONST_TOPIC_STOP_ROUND = "stopRound"
CONST_SEND_DATA = "sendData"
CONST_GAME_ID = "gameId"
CONST_SEND_STATE_T1 = "statet1"
CONST_SEND_STATE_T2 = "statet2"
CONST_SEND_STATE_T3 = "statet3"
CONST_SEND_STATE_T4 = "statet4"
CONST_SEND_ORDER = "send_order"
CONST_SEND_PRODUCTION = "produce"
CONST_SEND_DELIVERY = "send_delivery"
CONST_SEND_ORDER_ACK ="orderAck"
CONST_SEND_DELIVER_ACK ="deliverAck"

#some ore variables
global game_id
game_id =0
global round_time
round_time =120
round_time_copy =round_time

#setting up the rfid reader
reader = SimpleMFRC522()
"""
Connection to the mysql database.
Each client has it's own database on the device. This makes for the fact that the clients can look locally for their db with name clientdb
"""

connection = mysql.connector.connect(host='127.0.0.1',  database='clientdb', user='pi',password='pi',auth_plugin='mysql_native_password')
cur=connection.cursor()




#after connection was established
"""
This is the function that runs after the client connected to the hive mqtt broker
    This function will subscribe the client to the correct topics given its ID
    This function will also subscribe the client to the other necessary topics
"""
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    label_connected.config(text = "connected")   # change the labels text to connected so the user can view that it worked
    tier = entry_id_number.get()
    #subscribe to topic that is needed to recieve information and given wich one
    if (tier == '1'): 
        client.subscribe(CONST_SEND_STATE_T1,0)
    elif(tier =='2'):
        client.subscribe(CONST_SEND_STATE_T2,0)
    elif(tier =='3'):
        client.subscribe(CONST_SEND_STATE_T3,0)
    elif(tier =='4'):
        client.subscribe(CONST_SEND_STATE_T4,0)

    client.subscribe(CONST_TOPIC_START_ROUND, 0)
    client.subscribe(CONST_TOPIC_STOP_ROUND, 0)
    client.subscribe(CONST_GAME_ID,0)
    client.subscribe(CONST_SEND_ORDER_ACK,0)
    
    


#Reseive messages: startRound, stopRound

"""
The on_message function is communication critical!
--------------------------------------------------
This function is critical toward how this client receives communication from the admin pi.

Function: Each time a message is published by the admin and the client is subscribed to that topic this function will be used to determine 
which events will transpire afterwards.

Parameters: 
The main parameter we are concerned with is the msq. This is the message sent by the admin to this client. This will be checked against the 
constant variables with the topic.startwith function to determine what information is received


"""
def on_message(mosq, obj, msg):
    try:

        """
        If the topic is CONST_TOPIC_START_ROUND it will first start the timer using a different thread. After that it will break down the 
        recieved the data from the admin so it gets the round number and round ID

        """
        if msg.topic.startswith(CONST_TOPIC_START_ROUND):
            global round_time
            round_time = round_time_copy
            #global listenerThread
            count_down_timer = countDownThread(1, "Listener Thread", 1) # initiate the timer
            count_down_timer.daemon = True                         # when it its a daemon the thread will close when it completed its function
            count_down_timer.start()                               #start the timer
            nr = str(msg.payload).replace('b', '')
            nr = nr.replace('\'', '')                       
            print(nr)
            barrier = nr.find("#") 
            r = nr[:barrier]                                     # Splits into round number and round Id 
            round_id = nr[barrier+1:]
            print(round_id)

            QUERY="SELECT * FROM clientdb.game"   #returns all the products
            cur=connection.cursor()
            cur.execute(QUERY)
            games=cur.fetchall()
            games = list(games[-1]) # get last row in game table
            game_id = games[0]
            print(game_id)

            #inserts new round in to table
            QUERY="INSERT INTO clientdb.rounds (round_id,round_number,length,start_time,end_time,game_id) VALUES (%s, %s, %s, %s, %s, %s)"
            print("db insert round")
            vals = (round_id,r,round_time,datetime.now(),datetime.now(),game_id)
            cur.execute(QUERY, vals)
            connection.commit() 
            print("round inserted")           


            # This next section affects the game's UI
            label_roundNr.config(text = r)
            label_roundState.config(text = "running")
            label_roundNr.config(state = "normal")
            label_actual_round.config(state = "normal")
            label_roundState.config(state = "normal")
            #content enable

            #raw
            label_raw_materials.config(state = "normal")
            label_raw_1.config(state = "normal")
            label_raw_2.config(state = "normal")
            label_raw_3.config(state = "normal")
            label_raw_4.config(state = "normal")
            label_raw_1_amount.config(state = "normal")
            label_raw_2_amount.config(state = "normal")
            label_raw_3_amount.config(state = "normal")
            label_raw_4_amount.config(state = "normal")

            #wh
            label_finished_materials.config(state = "normal")
            label_finished_1.config(state = "normal")
            label_finished_2.config(state = "normal")
            label_finished_3.config(state = "normal")
            label_finished_4.config(state = "normal")
            label_finished_1_amount.config(state = "normal")
            label_finished_2_amount.config(state = "normal")
            label_finished_3_amount.config(state = "normal")
            label_finished_4_amount.config(state = "normal")

            #produce
            label_produce_materials.config(state = "normal")
            label_produce_1.config(state = "normal")
            label_produce_2.config(state = "normal")
            label_produce_3.config(state = "normal")
            label_produce_4.config(state = "normal")

            entry_produce_1_amount.config(state = "normal")
            entry_produce_1_amount.delete(0, 'end')
            entry_produce_1_amount.insert(0,'0')
            
            entry_produce_2_amount.config(state = "normal")
            entry_produce_2_amount.delete(0, 'end')
            entry_produce_2_amount.insert(0,'0')

            entry_produce_3_amount.config(state = "normal")
            entry_produce_3_amount.delete(0, 'end')
            entry_produce_3_amount.insert(0,'0')
            
            entry_produce_4_amount.config(state = "normal")
            entry_produce_4_amount.delete(0, 'end')
            entry_produce_4_amount.insert(0,'0')

            bt_production.config(state = "normal")

            #open orders
            label_opendeliveries.config(state = "normal")
            label_opendeliveries_1.config(state = "normal")
            label_opendeliveries_2.config(state = "normal")
            label_opendeliveries_3.config(state = "normal")
            label_opendeliveries_4.config(state = "normal")
            label_opendeliveries_1_amount.config(state = "normal")
            label_opendeliveries_2_amount.config(state = "normal")
            label_opendeliveries_3_amount.config(state = "normal")
            label_opendeliveries_4_amount.config(state = "normal")

            #backlog
            label_backlog.config(state = "normal")
            label_backlog_1.config(state = "normal") 
            label_backlog_2.config(state = "normal")
            label_backlog_3.config(state = "normal") 
            label_backlog_4.config(state = "normal")
            label_backlog_1_amount.config(state = "normal")
            label_backlog_2_amount.config(state = "normal")
            label_backlog_3_amount.config(state = "normal")
            label_backlog_4_amount.config(state = "normal")
            
            #order
            label_order.config(state = "normal")
            label_order_1.config(state = "normal")
            label_order_2.config(state = "normal")
            label_order_3.config(state = "normal")
            label_order_4.config(state = "normal")

            entry_order_1_amount.config(state = "normal")
            entry_order_1_amount.delete(0, 'end')
            entry_order_1_amount.insert(0,'0')

            entry_order_2_amount.config(state = "normal")
            entry_order_2_amount.delete(0, 'end')
            entry_order_2_amount.insert(0,'0')

            entry_order_3_amount.config(state = "normal")
            entry_order_3_amount.delete(0, 'end')
            entry_order_3_amount.insert(0,'0')

            entry_order_4_amount.config(state = "normal")
            entry_order_4_amount.delete(0, 'end')
            entry_order_4_amount.insert(0,'0')

            bt_order.config(state = "normal")

            #delivery
            label_deliver.config(state = "normal")
            label_deliver_1.config(state = "normal")
            label_deliver_2.config(state = "normal")
            label_deliver_3.config(state = "normal")
            label_deliver_4.config(state = "normal")

            entry_deliver_1_amount.config(state = "normal")
            entry_deliver_1_amount.delete(0, 'end')
            entry_deliver_1_amount.insert(0,'0')

            entry_deliver_2_amount.config(state = "normal")
            entry_deliver_2_amount.delete(0, 'end')
            entry_deliver_2_amount.insert(0,'0')

            entry_deliver_3_amount.config(state = "normal")
            entry_deliver_3_amount.delete(0, 'end')
            entry_deliver_3_amount.insert(0,'0')

            entry_deliver_4_amount.config(state = "normal")
            entry_deliver_4_amount.delete(0, 'end')
            entry_deliver_4_amount.insert(0,'0')

            bt_deliver.config(state = "normal")

            #
            label_time_left.config(state = "normal")
            label_cost_inbound_wh.config(state = "normal")
            label_cost_outbound_wh.config(state = "normal")
            label_cost_backlog.config(state = "normal")
            bt_done.config(state = "disabled")

            #production times
            label_production_times.config(state = "normal")
            label_production_times_product_1.config(state = "normal")
            label_production_times_product_2.config(state = "normal")
            label_production_times_product_3.config(state = "normal")
            label_production_times_product_4.config(state = "normal")

            add_stock(round_id) # Current Stock is taken and added to the database with each new round



        """
        If the topic is CONST_TOPIC_START_ROUND it will first incrememt the number or rounds in the game and also add the open deliveries 
        as well as backlog after each round. After that has been done the function will make changes on the UI for example disabling buttons
        of the functions Production,order and deliver as well as their counterparts
        """
        if msg.topic.startswith(CONST_TOPIC_STOP_ROUND):
            label_roundState.config(text = "stopped")
            inc_round_count_db()                            #increments the number of rounds in the current game
            add_open_deliveries()                           #store open deliveries to the database
            #add_backlog()                                  #store backlog to the database

            # disable some UI features
            label_roundNr.config(state = "disabled")
            label_roundState.config(state = "disabled")

            cur=connection.cursor()
        
            #selects the current round ID 
            QUERY="SELECT round_id FROM clientdb.rounds ORDER BY round_id DESC LIMIT 1"   #returns last round
            cur.execute(QUERY)
            previous_round = cur.fetchall()
            previous_round = previous_round[0][0]
        
            #amends the stoptime of the round to the correct stop time
            sql = "UPDATE clientdb.rounds SET end_time = %s WHERE round_id = %s"
            val = (datetime.now(), previous_round)
            cur.execute(sql, val)
            connection.commit()

            #content disable
            #raw
            label_raw_materials.config(state = "disabled")
            label_raw_1.config(state = "disabled")
            label_raw_2.config(state = "disabled")
            label_raw_3.config(state = "disabled")
            label_raw_4.config(state = "disabled")
            label_raw_1_amount.config(state = "disabled")
            label_raw_2_amount.config(state = "disabled")
            label_raw_3_amount.config(state = "disabled")
            label_raw_4_amount.config(state = "disabled")

            #wh
            label_finished_materials.config(state = "disabled")
            label_finished_1.config(state = "disabled")
            label_finished_2.config(state = "disabled")
            label_finished_3.config(state = "disabled")
            label_finished_4.config(state = "disabled")
            label_finished_1_amount.config(state = "disabled")
            label_finished_2_amount.config(state = "disabled")
            label_finished_3_amount.config(state = "disabled")
            label_finished_4_amount.config(state = "disabled")

            #produce
            label_produce_materials.config(state = "disabled")
            label_produce_1.config(state = "disabled")
            label_produce_2.config(state = "disabled")
            label_produce_3.config(state = "disabled")
            label_produce_4.config(state = "disabled")
            entry_produce_1_amount.config(state = "disabled")
            entry_produce_2_amount.config(state = "disabled")
            entry_produce_3_amount.config(state = "disabled")
            entry_produce_4_amount.config(state = "disabled")
            bt_production.config(state = "disabled")

            #open orders
            label_opendeliveries.config(state = "disabled")
            label_opendeliveries_1.config(state = "disabled")
            label_opendeliveries_2.config(state = "disabled")
            label_opendeliveries_3.config(state = "disabled")
            label_opendeliveries_4.config(state = "disabled")
            label_opendeliveries_1_amount.config(state = "disabled")
            label_opendeliveries_2_amount.config(state = "disabled")
            label_opendeliveries_3_amount.config(state = "disabled")
            label_opendeliveries_4_amount.config(state = "disabled")

            #backlog
            label_backlog.config(state = "disabled")
            label_backlog_1.config(state = "disabled")
            label_backlog_2.config(state = "disabled")
            label_backlog_3.config(state = "disabled")
            label_backlog_4.config(state = "disabled")
            label_backlog_1_amount.config(state = "disabled")
            label_backlog_2_amount.config(state = "disabled")
            label_backlog_3_amount.config(state = "disabled")
            label_backlog_4_amount.config(state = "disabled")
            
            #order
            label_order.config(state = "disabled")
            label_order_1.config(state = "disabled")
            label_order_2.config(state = "disabled")
            label_order_3.config(state = "disabled")
            label_order_4.config(state = "disabled")
            entry_order_1_amount.config(state = "disabled")
            entry_order_2_amount.config(state = "disabled")
            entry_order_3_amount.config(state = "disabled")
            entry_order_4_amount.config(state = "disabled")
            bt_order.config(state = "disabled")

            #delivery
            label_deliver.config(state = "disabled")
            label_deliver_1.config(state = "disabled")
            label_deliver_2.config(state = "disabled")
            label_deliver_3.config(state = "disabled")
            label_deliver_4.config(state = "disabled")
            entry_deliver_1_amount.config(state = "disabled")
            entry_deliver_2_amount.config(state = "disabled")
            entry_deliver_3_amount.config(state = "disabled")
            entry_deliver_4_amount.config(state = "disabled")
            bt_deliver.config(state = "disabled")

            #
            label_time_left.config(state = "disabled")
            label_cost_inbound_wh.config(state = "disabled")
            label_cost_outbound_wh.config(state = "disabled")
            label_cost_backlog.config(state = "disabled")
            bt_done.config(state = "normal")

            #production times
            label_production_times.config(state = "disabled")
            label_production_times_product_1.config(state = "disabled")
            label_production_times_product_2.config(state = "disabled")
            label_production_times_product_3.config(state = "disabled")
            label_production_times_product_4.config(state = "disabled")

        """
        If the topic is CONST_SEND_STATE_T1 and the current ID of the client is 1 then the client will update the database and UI with the 
        information provided by the admin given its tier
        """
        if msg.topic.startswith(CONST_SEND_STATE_T1) and entry_id_number.get() == '1':

            s = str(msg.payload)
            s=s[1:]                                 #drop the b at the start of the msg
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)   #convert the JSON to a object
            print(o.list_data)                      
            data = o.list_data                      #get the list of product information
            fill_init(data)                         #fill the information into the UI
            addProd(data)                           #add the products to the database 
        """
        If the topic is CONST_SEND_STATE_T2 and the current ID of the client is 2 then the client will update the database and UI with the 
        information provided by the admin given its tier
        """
        if msg.topic.startswith(CONST_SEND_STATE_T2) and entry_id_number.get() == '2':

            s = str(msg.payload)
            s=s[1:]                                 #drop the b at the start of the msg
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)   #convert the JSON to a object
            print(o.list_data)                      
            data = o.list_data                      #get the list of product information
            fill_init(data)                         #fill the information into the UI
            addProd(data)                           #add the products to the database 
        """
        If the topic is CONST_SEND_STATE_T3 and the current ID of the client is 3 then the client will update the database and UI with the 
        information provided by the admin given its tier
        """
        if msg.topic.startswith(CONST_SEND_STATE_T3) and entry_id_number.get() == '3':

            s = str(msg.payload)
            s=s[1:]                                 #drop the b at the start of the msg
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)   #convert the JSON to a object
            print(o.list_data)                      
            data = o.list_data                      #get the list of product information
            fill_init(data)                         #fill the information into the UI
            addProd(data)                           #add the products to the database 

        """
        If the topic is CONST_SEND_STATE_T4 and the current ID of the client is 4 then the client will update the database and UI with the 
        information provided by the admin given its tier
        """
        if msg.topic.startswith(CONST_SEND_STATE_T4) and entry_id_number.get() == '4':

            s = str(msg.payload)
            s=s[1:]                                 #drop the b at the start of the msg
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)   #convert the JSON to a object
            print(o.list_data)                      
            data = o.list_data                      #get the list of product information
            fill_init(data)                         #fill the information into the UI
            addProd(data)                           #add the products to the database 

        """
        If the topic is CONST_GAME_ID , it will insert a new game record into the database with the information provided.(game number)
        """
        if msg.topic.startswith(CONST_GAME_ID):
            
            #retrieve gameID from the msg
            s = str(msg.payload).replace('b', '')
            s = s.replace('\'', '')
            game_id =str(s)             
            print("game id : " ,game_id)

            #inserts into the database
            cur=connection.cursor()
            QUERY="INSERT INTO clientdb.game (game_id,rounds) VALUES (%s, %s)"
            vals = (game_id,str(0))
            cur.execute(QUERY, vals)
            connection.commit()

        """
        If the topic is CONST_SEND_ORDER_ACK , this means that this data comes from another client (the one this tier supply's to) via the
        admin. The data consists of the order the other client has made to this client.
        """
        if msg.topic.startswith(CONST_SEND_ORDER_ACK):

            s = str(msg.payload)
            s=s[1:]
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)                   #JSON object conversion
            print("This is the data that came from another order")
            print(o.list_data)                                     
            data = o.list_data                                      #getting the order as a list

            if (entry_id_number.get() == (data[0])[2]):
                print("true this is tier true")
                #if this client's ID match the correct one in the order it will update the values in backlog
                label_backlog_1_amount.config(text= str(int(label_backlog_1_amount.cget('text')) + int(data[0][1])))    
                label_backlog_2_amount.config(text= str(int(label_backlog_2_amount.cget('text')) + int(data[1][1])))
                label_backlog_3_amount.config(text= str(int(label_backlog_3_amount.cget('text')) + int(data[2][1])))
                label_backlog_4_amount.config(text= str(int(label_backlog_4_amount.cget('text')) + int(data[3][1])))

        ##########################################################################
        """
            This is the receiving of the delivered products (NOT USED , DELIVERY IS DONE WITH THE RFID TAG NOW)
        """
        ###########################################################################

        """
        if msg.topic.startswith(CONST_SEND_DELIVER_ACK):

            s = str(msg.payload)
            s=s[1:]
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)
            print("This is the data that came from another order")
            print(o.list_data)
            data = o.list_data

            if (entry_id_number.get() == (data[-1])[0]):
                print("true this is tier true")
                label_opendeliveries_1_amount.config(text= str(int(label_opendeliveries_1_amount.cget('text')) - int(data[0][1])))
                label_opendeliveries_2_amount.config(text= str(int(label_opendeliveries_2_amount.cget('text')) - int(data[1][1])))
                label_raw_1_amount.config(text= str(int(label_raw_1_amount.cget('text')) + int(data[0][1])))
                label_raw_2_amount.config(text= str(int(label_raw_2_amount.cget('text')) + int(data[1][1])))
        """

  
    except:
        e = sys.exc_info()[0]
        print("why are errro")
        print(e)
        

#############################################################################################################################
#                                              FUNCTIONS FOR GAME ACTIVITIES                                                #
#############################################################################################################################
"""
inc_round_count_db
Description:
This function increments the number of rounds of the game each time a new round is started. eg. one game can have many rounds
This happens by selecting the last game from the database and updating its value with each new round
"""
def inc_round_count_db():
    cur=connection.cursor()
    QUERY="SELECT MAX(game_id) FROM clientdb.game"   #returns last game id
    cur.execute(QUERY)
    current_game_id = cur.fetchall()
    print("this is the current gameID")
    print(current_game_id)
    current_game_id = current_game_id[0][0]  #extracting value out of a tuple

    sql = "UPDATE clientdb.game SET rounds = %s WHERE game_id = %s" #updating the value rounds where the game id is the same
    val = (label_roundNr.cget('text'), current_game_id)
    cur.execute(sql, val)
    connection.commit()


"""

"""
def process_sendData():
    #data = str(entry_data.get()) +"#" +str(entry_id_number.get())
    ok = client.publish(CONST_SEND_DATA, "data",qos=2)

"""
Filling up the window
Description:
This function fills out the user interface when the data arrives from the admin. This includes all labels and will be executed in the 
beginning of the game.
"""
def fill_init(data):
    raw = []
    fg = []
    #split data into two new arrays to easily use
    for i in data: 
        if i[2] == 'raw':
            raw.append(i)
        else:
            fg.append(i)
            
    label_raw_1.config(text = raw[0][1])
    label_raw_1_amount.config(text = raw[0][8])
    label_raw_2.config(text=raw[1][1])
    label_raw_2_amount.config(text=raw[1][8])
    label_raw_3.config(text = raw[2][1])
    label_raw_3_amount.config(text = raw[2][8])
    label_raw_4.config(text=raw[3][1])
    label_raw_4_amount.config(text=raw[3][8])

    label_finished_1.config(text = fg[0][1])
    label_finished_1_amount.config(text = fg[0][8])
    label_finished_2.config(text=fg[1][1])
    label_finished_2_amount.config(text=fg[1][8])
    label_finished_3.config(text = fg[2][1])
    label_finished_3_amount.config(text = fg[2][8])
    label_finished_4.config(text=fg[3][1])
    label_finished_4_amount.config(text=fg[3][8])

    label_produce_1.config(text = fg[0][1])
    label_produce_2.config(text = fg[1][1])
    label_produce_3.config(text = fg[2][1])
    label_produce_4.config(text = fg[3][1])

    label_production_times_product_1.config(text= str(fg[0][1]) + " : " + str(fg[0][3]))
    label_production_times_product_2.config(text= str(fg[1][1]) + " : " + str(fg[1][3]))
    label_production_times_product_3.config(text= str(fg[2][1]) + " : " + str(fg[2][3]))
    label_production_times_product_4.config(text= str(fg[3][1]) + " : " + str(fg[3][3]))

    label_opendeliveries_1.config(text = raw[0][1])
    label_opendeliveries_1_amount.config(text = '0')
    label_opendeliveries_2.config(text = raw[1][1])
    label_opendeliveries_2_amount.config(text = '0')
    label_opendeliveries_3.config(text = raw[2][1])
    label_opendeliveries_3_amount.config(text = '0')
    label_opendeliveries_4.config(text = raw[3][1])
    label_opendeliveries_4_amount.config(text = '0')

    label_backlog_1.config(text = fg[0][1])
    label_backlog_1_amount.config(text = '0')
    label_backlog_2.config(text = fg[1][1])
    label_backlog_2_amount.config(text = '0')
    label_backlog_3.config(text = fg[2][1])
    label_backlog_3_amount.config(text = '0')
    label_backlog_4.config(text = fg[3][1])
    label_backlog_4_amount.config(text = '0')

    label_order_1.config(text = raw[0][1])
    label_order_2.config(text=raw[1][1])
    label_order_3.config(text = raw[2][1])
    label_order_4.config(text=raw[3][1])

    label_deliver_1.config(text=fg[0][1])
    label_deliver_2.config(text=fg[1][1])
    label_deliver_3.config(text=fg[2][1])
    label_deliver_4.config(text=fg[3][1])


#Connect to Server
"""
Connect to Server
Description:
This function will connect the program to the MQTT server to enable cross device communication
Better idea is to give a pop-up or add a field to take in the ip from the user so the IP needs not to be changed in the code
"""
def process_connect2Server():
    bt_connect2Server.config(state = "disabled")     #Button disable

    ##connect 2 MQTTServer:
    print("Start conecting to Server")
    number = str(entry_id_number.get())
    entry_id_number.config(state = "disabled")     #disable

    client.connect("192.168.0.101")   # IP adress of the MQTT server
    client.loop_start()

"""
Add products
Description:
This function will get the data(list of products assigned to this client) and store it in the product table in the database. This will not input duplicates
"""
def addProd(data):
    cur=connection.cursor()
    for i in data:
        QUERY="INSERT INTO clientdb.product (product_id,product_name,type,production_time,cost,prerequisites,prerequisites_amount,tier_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        vals = ( str(i[0]), str(i[1]), str(i[2]), int(i[3]), float(i[4]), str(i[5]), str(i[6]), int(i[7]))
        cur.execute(QUERY, vals)
        connection.commit()
"""
Add Stock 
Description:
This function will store the stock that the player currently has inside the database. There will be 4 writes to the database, one for each of the 
products per start of round.
Parameters: round - round id
"""
def add_stock(round):
    cur=connection.cursor()
    QUERY="SELECT product_id,product_name FROM clientdb.product"
    cur.execute(QUERY)
    product_names_id=cur.fetchall() 
    print(product_names_id)

    p1 = label_raw_1.cget('text')
    p2 = label_raw_2.cget('text')
    p3 = label_raw_3.cget('text')
    p4 = label_raw_4.cget('text')
    p1_a = label_raw_1_amount.cget('text')
    p2_a = label_raw_2_amount.cget('text')
    p3_a = label_raw_3_amount.cget('text')
    p4_a = label_raw_4_amount.cget('text')

    p11 = label_finished_1.cget('text')
    p22 = label_finished_2.cget('text')
    p33 = label_finished_3.cget('text')
    p44 = label_finished_4.cget('text')
    p11_a = label_finished_1_amount.cget('text')
    p22_a = label_finished_2_amount.cget('text')
    p33_a = label_finished_3_amount.cget('text')
    p44_a = label_finished_4_amount.cget('text')

    stck = [[p1,p1_a],[p2,p2_a],[p3,p3_a],[p4,p4_a],[p11,p11_a],[p22,p22_a],[p33,p33_a],[p44,p44_a]] #builds a list of stock that needs to be inserted

    #insets the current stock for the round into the database
    for i in stck:
        QUERY="INSERT INTO clientdb.stock (stock_amount,product_id,round_id) VALUES (%s, %s, %s)"
        pid =''
        for j in product_names_id:
            if j[1] == i[0]:
                pid = j[0]
        
        vals = (i[1],pid,round)
        cur.execute(QUERY, vals)
        connection.commit()
"""
Produce products
Description:
This function takes the data filled into the entries above the produce button to gather how much of what the user wants to produce.
The functions checks if the user has enough time as well as raw materials to do the transaction. The function also checks for user input erros
When the produce button is pressed the program will also input the data into the database, 4 records for each of the fields
The function wll also publish the data for the admin , this is so that the admin can keep track to that record.

Caveats/future work:
Does not yet check for negative inputs
Reduce records by only inputing records with non zero values
"""
def produce():
    

    #get the products the user wants
    prod_1 = label_produce_1.cget('text')
    prod_2 = label_produce_2.cget('text')
    prod_3 = label_produce_3.cget('text')
    prod_4 = label_produce_4.cget('text')

    prod_1_a = entry_produce_1_amount.get()
    prod_2_a = entry_produce_2_amount.get()
    prod_3_a = entry_produce_3_amount.get()
    prod_4_a = entry_produce_4_amount.get()

    fg = [[prod_1,prod_1_a],[prod_2,prod_2_a],[prod_3,prod_3_a],[prod_4,prod_4_a]]

    #get the raw materieals 

    raw_1 = label_raw_1.cget('text')  
    raw_2 = label_raw_2.cget('text')
    raw_3 = label_raw_3.cget('text')  
    raw_4 = label_raw_4.cget('text')

    raw_1_a = label_raw_1_amount.cget('text')  
    raw_2_a = label_raw_2_amount.cget('text')
    raw_3_a = label_raw_3_amount.cget('text')  
    raw_4_a = label_raw_4_amount.cget('text')

    raw = [[raw_1,raw_1_a],[raw_2,raw_2_a],[raw_3,raw_3_a],[raw_4,raw_4_a]]

    #first check if the user has sufficeint raw materials
    cur=connection.cursor()
    QUERY="SELECT product_id,product_name,prerequisites,prerequisites_amount,production_time FROM clientdb.product WHERE type = 'fg'"
    cur.execute(QUERY)
    product_names_id=cur.fetchall() 
    print(product_names_id)

    for i in range(len(fg)):
        fg[i].append(list(product_names_id[i])[4])
        fg[i].append(list(product_names_id[i])[0])

    print(fg)

    produuct1_pre = (list(product_names_id[0])[2]).split('#')  
    produuct2_pre = (list(product_names_id[1])[2]).split('#')  
    produuct3_pre = (list(product_names_id[2])[2]).split('#')  
    produuct4_pre = (list(product_names_id[3])[2]).split('#')  

    print("pre p1 :" )
    print(produuct1_pre)
    print("pre p2 :" )
    print(produuct2_pre)

    produuct1_pre_amt = (list(product_names_id[0])[3]).split('#')
    produuct2_pre_amt = (list(product_names_id[1])[3]).split('#')
    produuct3_pre_amt = (list(product_names_id[2])[3]).split('#')
    produuct4_pre_amt = (list(product_names_id[3])[3]).split('#')

    try:
        # working out amounts of raw products needed 
        for i in range(len(produuct1_pre_amt)):
            produuct1_pre_amt[i] = int(produuct1_pre_amt[i])*int(entry_produce_1_amount.get())

        for i in range(len(produuct2_pre_amt)):
            produuct2_pre_amt[i] = int(produuct2_pre_amt[i])*int(entry_produce_2_amount.get())

        for i in range(len(produuct3_pre_amt)):
            produuct3_pre_amt[i] = int(produuct3_pre_amt[i])*int(entry_produce_3_amount.get())

        for i in range(len(produuct4_pre_amt)):
            produuct4_pre_amt[i] = int(produuct4_pre_amt[i])*int(entry_produce_4_amount.get())

        #builds an arrray of total amounts of raw products needed for the operation
        total_pre = [produuct1_pre_amt[0]+produuct2_pre_amt[0]+produuct3_pre_amt[0]+produuct4_pre_amt[0],
        produuct1_pre_amt[1]+produuct2_pre_amt[1]+produuct3_pre_amt[1]+produuct4_pre_amt[1],
        produuct1_pre_amt[2]+produuct2_pre_amt[2]+produuct3_pre_amt[2]+produuct4_pre_amt[2],
        produuct1_pre_amt[3]+produuct2_pre_amt[3]+produuct3_pre_amt[3]+produuct4_pre_amt[3]]

        #[2,2,3,4]
        sufficeint_raw = True
        total_prod_time = 0
        print(total_pre)
        #check if there is sufficient raw products
        for i in range(len(total_pre)):
            if int(raw[i][1]) < total_pre[i]:
                sufficeint_raw = False
        
        #check for sufficient time
        for i in range(len(fg)):
            time = int(fg[i][1])*fg[i][2]
            total_prod_time += time
        print(total_prod_time)
        flag = True
        
    except:
        flag = False
        popupmsg("Please reformat so it is only positive numbers.") # not yet checking for negatives
    if flag == True:
        global round_time
        if(sufficeint_raw == False or total_prod_time > round_time):
            popupmsg("You either do not have enought raw materials or no time for the requested production.")
            #print("you do not have enought raw materials or no time")
        else:
            label_raw_1_amount.config(text= str( int(label_raw_1_amount.cget('text'))- total_pre[0]))
            label_raw_2_amount.config(text= str( int(label_raw_2_amount.cget('text'))- total_pre[1]))
            label_raw_3_amount.config(text= str( int(label_raw_3_amount.cget('text'))- total_pre[2]))
            label_raw_4_amount.config(text= str( int(label_raw_4_amount.cget('text'))- total_pre[3]))

            label_finished_1_amount.config(text= str( int(label_finished_1_amount.cget('text'))+ int(entry_produce_1_amount.get())))
            label_finished_2_amount.config(text= str( int(label_finished_2_amount.cget('text'))+ int(entry_produce_2_amount.get())))
            label_finished_3_amount.config(text= str( int(label_finished_3_amount.cget('text'))+ int(entry_produce_3_amount.get())))
            label_finished_4_amount.config(text= str( int(label_finished_4_amount.cget('text'))+ int(entry_produce_4_amount.get())))


            QUERY="SELECT round_id FROM clientdb.rounds ORDER BY round_id DESC LIMIT 1"   #returns last round
            cur.execute(QUERY)
            previous_round =cur.fetchall()
            print(previous_round)

            QUERY="SELECT production_id FROM clientdb.production"   #returns all the round_id's
            cur=connection.cursor()
            cur.execute(QUERY)
            production=cur.fetchall()
            print(production)
            if(len(production)>=1):
                production = list(production) # get last row in game table
                print(production)
                production = production[-1]
                production = production[0]        # get the game id 
                production = production[5:]       # slice the game id 
                print("in if :",production)
                production_id = str(int(production)+1 ) # add one to the game id
            else:
                production_id = str(1)

            for i in fg:
                #building id for production table
                if len(production_id) == 1:
                    production_id = "prd00000" +str(production_id)
                elif(len(production_id) == 2):
                    production_id = "prd0000" +str(production_id)
                elif(len(production_id) == 3):
                    production_id = "prd000" +str(production_id)
                elif(len(production_id) == 4):
                    production_id = "prd00" +str(production_id)
                elif(len(production_id) == 5):
                    production_id = "prd0" +str(production_id)
                else:
                    production_id = "prd"+str(production_id)

        
                cur=connection.cursor()
                QUERY="INSERT INTO clientdb.production (production_id, amount, product_id, total_production_time, time_stamp, round_id) VALUES (%s, %s, %s, %s, %s, %s)"
                print("db insert products : " + str(i))
                vals = (production_id,i[1],i[3],(int(i[1])*i[2]),datetime.now(),previous_round[0][0])
                cur.execute(QUERY, vals)
                connection.commit()

                production_id = str(int(production_id[4:])+1)

            for i in fg:
                i.append(entry_id_number.get())


            produce_Data_t = initialClientDataList()  #reuse the initial clients data class to ransmit data to the admin
            produce_Data_t.list_data= fg
            data = produce_Data_t.obj2JSON(produce_Data_t)
            res = client.publish(CONST_SEND_PRODUCTION,data,qos=2)
            round_time -= total_prod_time 
            #time.sleep(2)
        


#backlog function ==========================================================================
"""
Adding backlog
Description:
This unction will append the backlog statistics of each round to the database for use in data analysis.
"""
def add_backlog():
    lst = [['1','1'],['2','1'],['3','2'],['4','3']]

    to_who = ''
    #checks to who the backlog is
    for i in lst:
        if i[0] == entry_id_number.get():
            to_who = i[1]

    p1 = [label_backlog_1.cget('text'),label_backlog_1_amount.cget('text')]
    p2 = [label_backlog_2.cget('text'),label_backlog_2_amount.cget('text')]
    p3 = [label_backlog_3.cget('text'),label_backlog_3_amount.cget('text')]
    p4 = [label_backlog_4.cget('text'),label_backlog_4_amount.cget('text')]

    prod_list = [p1,p2,p3,p4]

    cur=connection.cursor()
    QUERY="SELECT product_id,product_name FROM clientdb.product WHERE type = 'fg'" # select the finished goods product's names and id's
    cur.execute(QUERY)
    product_names_id=cur.fetchall() 
    print(product_names_id)
    #matching the product names to get the product id's
    for i in product_names_id:
        for j in prod_list: 
            if i[1] == j[0]:
                j.append(i[0])

    print("full list of backlog")
    print(prod_list)

    QUERY="SELECT backlog_id FROM clientdb.backlog ORDER BY backlog_id DESC LIMIT 1"   #returns last backlog id 
    cur.execute(QUERY)
    last_back_log =cur.fetchall()
    print(last_back_log)

    if(len(last_back_log)>=1):
        new_back = last_back_log[0][0]
        new_back = new_back[4:]       # slice the game id 
        print("in if :",new_back)
        backlog_ids = str(int(new_back)+1 ) # add one to the game id # add one to the game id
    else:
        backlog_ids = str(1)

    QUERY="SELECT round_id FROM clientdb.rounds ORDER BY round_id DESC LIMIT 1"   #returns last round
    cur.execute(QUERY)
    previous_round =cur.fetchall()
    print(previous_round[0][0])
    previous_round =previous_round[0][0]

    #builds new backlog id
    for i in prod_list:
        if len(backlog_ids) == 1:
            backlog_ids = "back00000" +str(backlog_ids)
        elif(len(backlog_ids) == 2):
            backlog_ids = "back0000" +str(backlog_ids)
        elif(len(backlog_ids) == 3):
            backlog_ids = "back000" +str(backlog_ids)
        elif(len(backlog_ids) == 4):
            backlog_ids = "back00" +str(backlog_ids)
        elif(len(backlog_ids) == 5):
            backlog_ids = "back0" +str(backlog_ids)
        else:
            backlog_ids = "back"+str(backlog_ids)


        cur=connection.cursor()
        QUERY="INSERT INTO 'clientdb'.'backlog' (backlog_id, amount, time_stamp, round_id, product_id) VALUES (%s, %s, %s, %s, %s)"
        print("db insert open orders: " + str(i))
        #inserts the record into the database
        vals = ("back000001","0",datetime.now(),"round00001","prod00006")
        print(vals)
        cur.execute(QUERY, vals)
        print("done")
        connection.commit()

        backlog_ids = str(int(backlog_ids[4:])+1)


#open orders function =========================================================================
"""
Add open deliveries
Description: This function will store the state of the open deliveries for each round to the database to be used for tracking:
The function will output 4 records each round. The open deliveries is what comes from a lower tier 
Note that in the code open orders and deliveries is used in the same breath
"""
def add_open_deliveries():
    print("in open del")
    lst = [['1','2'],['2','3'],['3','4'],['4','4']]

    from_who = ''

    #works out given the clients tier form who is the open deliveries
    for i in lst:
        if i[0] == entry_id_number.get():
            from_who = i[1]

    p1 = [label_opendeliveries_1.cget('text'),label_opendeliveries_1_amount.cget('text')]
    p2 = [label_opendeliveries_2.cget('text'),label_opendeliveries_2_amount.cget('text')]
    p3 = [label_opendeliveries_3.cget('text'),label_opendeliveries_3_amount.cget('text')]
    p4 = [label_opendeliveries_4.cget('text'),label_opendeliveries_4_amount.cget('text')]

    #builds a product list from the lables to be inputed
    prod_list = [p1,p2,p3,p4]

    cur=connection.cursor()
    QUERY="SELECT product_id,product_name FROM clientdb.product WHERE type = 'raw'" #get the id's of said products
    cur.execute(QUERY)
    product_names_id=cur.fetchall() 
    print(product_names_id)

    #adds the id's to the product list
    for i in product_names_id:
        for j in prod_list: 
            if i[1] == j[0]:
                j.append(i[0])

    print("full list of open orders")
    print(prod_list)



    QUERY="SELECT openorders_id FROM clientdb.openorders ORDER BY openorders_id DESC LIMIT 1"   #returns last round
    cur.execute(QUERY)
    last_open_del =cur.fetchall()
    print(last_open_del)
    last_open_order = last_open_del

    if(len(last_open_order)>=1):
        new_open = last_open_order[0][0]
        new_open = new_open[4:]                         #slice the open order id 
        print("in if :",new_open)
        open_order_id = str(int(new_open)+1 ) # add one to the open order id 
    else:
        open_order_id = str(1)

    QUERY="SELECT round_id FROM clientdb.rounds ORDER BY round_id DESC LIMIT 1"   #returns last round
    cur.execute(QUERY)
    previous_round =cur.fetchall()
    print(previous_round[0][0])
    previous_round =previous_round[0][0]
    # build open order id
    for i in prod_list:
        if len(open_order_id) == 1:
            open_order_id = "open00000" +str(open_order_id)
        elif(len(open_order_id) == 2):
            open_order_id = "open0000" +str(open_order_id)
        elif(len(open_order_id) == 3):
            open_order_id = "open000" +str(open_order_id)
        elif(len(open_order_id) == 4):
            open_order_id = "open00" +str(open_order_id)
        elif(len(open_order_id) == 5):
            open_order_id = "open0" +str(open_order_id)
        else:
            open_order_id = "open"+str(open_order_id)


        cur=connection.cursor()
        # inserts 4 records into the open orders table
        QUERY="INSERT INTO clientdb.openorders (openorders_id, amount, time_stamp, round_id, product_id, from_id) VALUES (%s, %s, %s, %s, %s, %s)"
        print("db insert open orders: " + str(i))
        vals = (open_order_id,i[1],datetime.now(),previous_round,i[2],from_who)
        print(vals)
        cur.execute(QUERY, vals)
        connection.commit()

        open_order_id = str(int(open_order_id[4:])+1) # increments the open order id


"""
Note used
"""
def p_button():
    bt_production.config(state = "disabled")
    produce()
    bt_production.config(state = "normal")

"""
Order Function
Description:
This function is invoked when the user filled out the entry fields above the order button and proceed to press the button. 
This function is used to place an order to the tier below the current client in order to get raw products for use in production.
This function does do some error checking in terms of user input(not yet for negative numbers)

Caveat/Future work:
When the user orders check orders and don't input orders to the database with a zero value
Add negative number error checking
"""
def order_function():
    lst = [['1','2'],['2','3'],['3','4'],['4','4']]
    order_from =''
    for i in lst:
        if str(entry_id_number.get()) == i[0]: #checking to what client the order needs to be sent
            order_from = i[1]
    print(order_from)

    cur=connection.cursor()
    QUERY="SELECT product_id,product_name FROM clientdb.product WHERE type = 'raw'"
    cur.execute(QUERY)
    product_names_id=cur.fetchall() 
    print(product_names_id)
    flag = False
    #getting data to buid order from the interface
    p1 = label_order_1.cget('text')
    p1_a = entry_order_1_amount.get()
    p2 = label_order_2.cget('text')
    p2_a = entry_order_2_amount.get()
    p3 = label_order_3.cget('text')
    p3_a = entry_order_3_amount.get()
    p4 = label_order_4.cget('text')
    p4_a = entry_order_4_amount.get()
    #try to catch if the data was inputted correctly
    try:
        order_lst = [[p1,int(p1_a)],[p2,int(p2_a)],[p3,int(p3_a)],[p4,int(p4_a)]] 
        flag = True
    except:
        flag = False
        popupmsg("Please reformat the fields so it contains only positive numbers")
    print(order_lst)
    counter = 0
    if flag == True :
        # match the product names and the id of the product. The ID is needed for capture
        for i in order_lst:
            for j in product_names_id:
                if i[0] == j[1]:
                    order_lst[counter][0] = j[0]
                    counter +=1
        print(order_lst)

        #build order for sql

        QUERY="SELECT order_id FROM clientdb.order"   #returns all the round_id's
        cur=connection.cursor()
        cur.execute(QUERY)
        orders=cur.fetchall()
        print(orders)

        if(len(orders)>=1):
            orders = list(orders) # get last row in game table
            print(orders)
            orders = orders[-1]
            orders = orders[0]        # get the order id
            orders = orders[5:]       # slice the order i
            print("in if :",orders)
            order_id = str(int(orders)+1 ) # add one to the order id
        else:
            order_id = str(1)

        QUERY="SELECT round_id FROM clientdb.rounds ORDER BY round_id DESC LIMIT 1"   #returns last round
        cur.execute(QUERY)
        previous_round =cur.fetchall()
        print(previous_round)
        # builing of the primary key of the order table    
        for i in order_lst:

            if len(order_id) == 1:
                order_id = "ord00000" +str(order_id)
            elif(len(order_id) == 2):
                order_id = "ord0000" +str(order_id)
            elif(len(order_id) == 3):
                order_id = "ord000" +str(order_id)
            elif(len(order_id) == 4):
                order_id = "ord00" +str(order_id)
            elif(len(order_id) == 5):
                order_id = "ord0" +str(order_id)
            else:
                order_id = "ord"+str(order_id)

            #writing data to the order table
            cur=connection.cursor()
            QUERY="INSERT INTO clientdb.order (order_id, amount, time_stamp, product_id, tier_id, round_id) VALUES (%s, %s, %s, %s, %s, %s)"
            print("db insert orders : " + str(i))
            vals = (order_id,i[1],datetime.now(),i[0],order_from,previous_round[0][0])
            cur.execute(QUERY, vals)
            connection.commit()

            order_id = str(int(order_id[4:])+1)
            
        for i in order_lst:
            i.append(order_from)
        print("to send to admin order")
        print(order_lst)
        

        orders_Data_t = initialClientDataList()  #reuse the initial clients data class to ransmit data to the admin
        orders_Data_t.list_data= order_lst
        data = orders_Data_t.obj2JSON(orders_Data_t) # concversion fo data to a JSON object
        res = client.publish(CONST_SEND_ORDER,data,qos=2) # publish the data to the CONST_SEND_ORDER topic for the admin to recieve
        label_opendeliveries_1_amount.config(text=str(int(label_opendeliveries_1_amount.cget('text'))+int(order_lst[0][1]))) 
        label_opendeliveries_2_amount.config(text=str(int(label_opendeliveries_2_amount.cget('text'))+int(order_lst[1][1])))
        label_opendeliveries_3_amount.config(text=str(int(label_opendeliveries_3_amount.cget('text'))+int(order_lst[2][1]))) 
        label_opendeliveries_4_amount.config(text=str(int(label_opendeliveries_4_amount.cget('text'))+int(order_lst[3][1])))
        bt_order.config(state = "disabled")


"""
Function that only condenses the starting of the delivery thread
"""
def deliver_rfid():
    deliverThread = deliver1(1, "Deliver Thread")
    deliverThread.daemon = True
    deliverThread.start()
"""
Function that only condenses the starting of the getdelivery thread
"""
def getDelivery():
    deliverThread = deliver2(1, "Deliver get Thread")
    deliverThread.daemon = True
    deliverThread.start()
    
#Main-Program
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

win = tk.Tk()
win.title("TEST MQTT Client")
win.geometry("800x420") #size of window


##############################################################################################################################
#                                               BUILDING OF THE INTERFACE                                                    #
##############################################################################################################################
#widgets --------------------------------------------------------
#Label
label_id = tk.Label(win, text="ID:")
label_id.grid(column=0, row=0)

#entry for Client ID
entry_id_number = tk.Entry(width=5)
entry_id_number.grid(column=1, row=0)

#Button connect
bt_connect2Server = tk.Button(text="Connect to Server", command=process_connect2Server)
bt_connect2Server.grid(column=2, row=0)

label_connected = tk.Label(win, text="")
label_connected.grid(column=3, row=0)
label_connected.config(state = "disabled")     

label_actual_round = tk.Label(win, text="Actual Round:")
label_actual_round.grid(column=0, row=1)
label_actual_round.config(state = "disabled")    

label_roundNr = tk.Label(win, text="")
label_roundNr.grid(column=1, row=1)
label_roundNr.config(state = "disabled")    

label_roundState = tk.Label(win, text="")
label_roundState.grid(column=2, row=1)
label_roundState.config(state = "disabled")

#raw materials section

label_raw_materials = tk.Label(win, text="Raw Materials:",font='Helvetica 10 bold')
label_raw_materials.grid(column=0, row=2)
label_raw_materials.config(state = "disabled")

label_raw_1 = tk.Label(win, text="First raw: ")
label_raw_1.grid(column=0, row=3)
label_raw_1.config(state = "disabled")

label_raw_2 = tk.Label(win, text="Second Raw: ")
label_raw_2.grid(column=0, row=4)
label_raw_2.config(state = "disabled")

label_raw_3 = tk.Label(win, text="Third raw: ")
label_raw_3.grid(column=0, row=5)
label_raw_3.config(state = "disabled")

label_raw_4 = tk.Label(win, text="Forth Raw: ")
label_raw_4.grid(column=0, row=6)
label_raw_4.config(state = "disabled")

label_raw_1_amount = tk.Label(win, text="0")
label_raw_1_amount.grid(column=1, row=3)
label_raw_1_amount.config(state = "disabled")

label_raw_2_amount = tk.Label(win, text="0")
label_raw_2_amount.grid(column=1, row=4)
label_raw_2_amount.config(state = "disabled")

label_raw_3_amount = tk.Label(win, text="0")
label_raw_3_amount.grid(column=1, row=5)
label_raw_3_amount.config(state = "disabled")

label_raw_4_amount = tk.Label(win, text="0")
label_raw_4_amount.grid(column=1, row=6)
label_raw_4_amount.config(state = "disabled")
    
#current warehouse

label_finished_materials = tk.Label(win, text="Finished goods:",font='Helvetica 10 bold')
label_finished_materials.grid(column=2, row=2)
label_finished_materials.config(state = "disabled")

label_finished_1 = tk.Label(win, text="First finished: ")
label_finished_1.grid(column=2, row=3)
label_finished_1.config(state = "disabled")

label_finished_2 = tk.Label(win, text="Second finished: ")
label_finished_2.grid(column=2, row=4)
label_finished_2.config(state = "disabled")

label_finished_3 = tk.Label(win, text="Third finished: ")
label_finished_3.grid(column=2, row=5)
label_finished_3.config(state = "disabled")

label_finished_4 = tk.Label(win, text="Forth finished: ")
label_finished_4.grid(column=2, row=6)
label_finished_4.config(state = "disabled")

label_finished_1_amount = tk.Label(win, text="0")
label_finished_1_amount.grid(column=3, row=3)
label_finished_1_amount.config(state = "disabled")

label_finished_2_amount = tk.Label(win, text="0")
label_finished_2_amount.grid(column=3, row=4)
label_finished_2_amount.config(state = "disabled")

label_finished_3_amount = tk.Label(win, text="0")
label_finished_3_amount.grid(column=3, row=5)
label_finished_3_amount.config(state = "disabled")

label_finished_4_amount = tk.Label(win, text="0")
label_finished_4_amount.grid(column=3, row=6)
label_finished_4_amount.config(state = "disabled")

#to produce
label_produce_materials = tk.Label(win, text="Produce goods:",font='Helvetica 10 bold')
label_produce_materials.grid(column=4, row=2)
label_produce_materials.config(state = "disabled")

label_produce_1 = tk.Label(win, text="First produce: ")
label_produce_1.grid(column=4, row=3)
label_produce_1.config(state = "disabled")

label_produce_2 = tk.Label(win, text="Second produce: ")
label_produce_2.grid(column=4, row=4)
label_produce_2.config(state = "disabled")

label_produce_3 = tk.Label(win, text="Third produce: ")
label_produce_3.grid(column=4, row=5)
label_produce_3.config(state = "disabled")

label_produce_4 = tk.Label(win, text="Forth produce: ")
label_produce_4.grid(column=4, row=6)
label_produce_4.config(state = "disabled")

entry_produce_1_amount = tk.Entry(width='15')
entry_produce_1_amount.insert(END, '0')
entry_produce_1_amount.grid(column=5, row=3)
entry_produce_1_amount.config(state = "disabled")

entry_produce_2_amount = tk.Entry(width='15')
entry_produce_2_amount.insert(END, '0')
entry_produce_2_amount.grid(column=5, row=4)
entry_produce_2_amount.config(state = "disabled")

entry_produce_3_amount = tk.Entry(width='15')
entry_produce_3_amount.insert(END, '0')
entry_produce_3_amount.grid(column=5, row=5)
entry_produce_3_amount.config(state = "disabled")

entry_produce_4_amount = tk.Entry(width='15')
entry_produce_4_amount.insert(END, '0')
entry_produce_4_amount.grid(column=5, row=6)
entry_produce_4_amount.config(state = "disabled")

bt_production = tk.Button(text="Start Production", command=lambda: produce())
bt_production.grid(column=5, row=7)
bt_production.config(state = "disabled")

#production times and timer 

#open Deliveries

label_opendeliveries = tk.Label(win, text="Open Deliveries:",font='Helvetica 10 bold')
label_opendeliveries.grid(column=0, row=8)
label_opendeliveries.config(state = "disabled")

label_opendeliveries_1 = tk.Label(win, text="First open del:")
label_opendeliveries_1.grid(column=0, row=9)
label_opendeliveries_1.config(state = "disabled")

label_opendeliveries_2 = tk.Label(win, text="Second open del:")
label_opendeliveries_2.grid(column=0, row=10)
label_opendeliveries_2.config(state = "disabled")

label_opendeliveries_3 = tk.Label(win, text="Third open del: ")
label_opendeliveries_3.grid(column=0, row=11)
label_opendeliveries_3.config(state = "disabled")

label_opendeliveries_4 = tk.Label(win, text="Forth open del:")
label_opendeliveries_4.grid(column=0, row=12)
label_opendeliveries_4.config(state = "disabled")

label_opendeliveries_1_amount = tk.Label(win, text="0")
label_opendeliveries_1_amount.grid(column=1, row=9)
label_opendeliveries_1_amount.config(state = "disabled")

label_opendeliveries_2_amount = tk.Label(win, text="0")
label_opendeliveries_2_amount.grid(column=1, row=10)
label_opendeliveries_2_amount.config(state = "disabled")

label_opendeliveries_3_amount = tk.Label(win, text="0")
label_opendeliveries_3_amount.grid(column=1, row=11)
label_opendeliveries_3_amount.config(state = "disabled")

label_opendeliveries_4_amount = tk.Label(win, text="0")
label_opendeliveries_4_amount.grid(column=1, row=12)
label_opendeliveries_4_amount.config(state = "disabled")

#back log

label_backlog = tk.Label(win, text="Back log:",font='Helvetica 10 bold')
label_backlog.grid(column=2, row=8)
label_backlog.config(state = "disabled")

label_backlog_1 = tk.Label(win, text="First backlog:")
label_backlog_1.grid(column=2, row=9)
label_backlog_1.config(state = "disabled")

label_backlog_2 = tk.Label(win, text="Second back log:")
label_backlog_2.grid(column=2, row=10)
label_backlog_2.config(state = "disabled")

label_backlog_3 = tk.Label(win, text="First backlog:")
label_backlog_3.grid(column=2, row=11)
label_backlog_3.config(state = "disabled")

label_backlog_4 = tk.Label(win, text="Second back log:")
label_backlog_4.grid(column=2, row=12)
label_backlog_4.config(state = "disabled")

label_backlog_1_amount = tk.Label(win, text="0")
label_backlog_1_amount.grid(column=3, row=9)
label_backlog_1_amount.config(state = "disabled")

label_backlog_2_amount = tk.Label(win, text="0")
label_backlog_2_amount.grid(column=3, row=10)
label_backlog_2_amount.config(state = "disabled")

label_backlog_3_amount = tk.Label(win, text="0")
label_backlog_3_amount.grid(column=3, row=11)
label_backlog_3_amount.config(state = "disabled")

label_backlog_4_amount = tk.Label(win, text="0")
label_backlog_4_amount.grid(column=3, row=12)
label_backlog_4_amount.config(state = "disabled")

#orders
label_order = tk.Label(win, text="Order:",font='Helvetica 10 bold')
label_order.grid(column=4, row=8)
label_order.config(state = "disabled")

label_order_1 = tk.Label(win, text="First order:")
label_order_1.grid(column=4, row=9)
label_order_1.config(state = "disabled")

label_order_2 = tk.Label(win, text="Second order:")
label_order_2.grid(column=4, row=10)
label_order_2.config(state = "disabled")

label_order_3 = tk.Label(win, text="third order:")
label_order_3.grid(column=4, row=11)
label_order_3.config(state = "disabled")

label_order_4 = tk.Label(win, text="forth order:")
label_order_4.grid(column=4, row=12)
label_order_4.config(state = "disabled")

entry_order_1_amount = tk.Entry(width='15')
entry_order_1_amount.insert(END, '0')
entry_order_1_amount.grid(column=5, row=9)
entry_order_1_amount.config(state = "disabled")

entry_order_2_amount = tk.Entry(width='15')
entry_order_2_amount.insert(END, '0')
entry_order_2_amount.grid(column=5, row=10)
entry_order_2_amount.config(state = "disabled")

entry_order_3_amount = tk.Entry(width='15')
entry_order_3_amount.insert(END, '0')
entry_order_3_amount.grid(column=5, row=11)
entry_order_3_amount.config(state = "disabled")

entry_order_4_amount = tk.Entry(width='15')
entry_order_4_amount.insert(END, '0')
entry_order_4_amount.grid(column=5, row=12)
entry_order_4_amount.config(state = "disabled")

bt_order = tk.Button(text="Start order", command=order_function)
bt_order.grid(column=5, row=13)
bt_order.config(state = "disabled")

# deliver

label_deliver = tk.Label(win, text="Deliver :",font='Helvetica 10 bold')
label_deliver.grid(column=0, row=14)
label_deliver.config(state = "disabled")

label_deliver_1 = tk.Label(win, text="First delivery:")
label_deliver_1.grid(column=0, row=15)
label_deliver_1.config(state = "disabled")

label_deliver_2 = tk.Label(win, text="Second delivery:")
label_deliver_2.grid(column=0, row=16)
label_deliver_2.config(state = "disabled")

label_deliver_3 = tk.Label(win, text="Third delivery:")
label_deliver_3.grid(column=2, row=15)
label_deliver_3.config(state = "disabled")

label_deliver_4 = tk.Label(win, text="Forth delivery:")
label_deliver_4.grid(column=2, row=16)
label_deliver_4.config(state = "disabled")

entry_deliver_1_amount = tk.Entry(width = 5)
entry_deliver_1_amount.grid(column=1, row=15)
entry_deliver_1_amount.config(state = "disabled")

entry_deliver_2_amount = tk.Entry(width = 5)
entry_deliver_2_amount.grid(column=1, row=16)
entry_deliver_2_amount.config(state = "disabled")

entry_deliver_3_amount = tk.Entry(width = 5)
entry_deliver_3_amount.grid(column=3, row=15)
entry_deliver_3_amount.config(state = "disabled")

entry_deliver_4_amount = tk.Entry(width = 5)
entry_deliver_4_amount.grid(column=3, row=16)
entry_deliver_4_amount.config(state = "disabled")

bt_deliver = tk.Button(text="Start delivery", command=deliver_rfid)
bt_deliver.grid(column=0, row=17)
bt_deliver.config(state = "disabled")

#production times

label_production_times = tk.Label(win, text="Production times :",font='Helvetica 10 bold')
label_production_times.grid(column=6, row=2)
label_production_times.config(state = "disabled")

label_production_times_product_1 = tk.Label(win, text="First product:  10")
label_production_times_product_1.grid(column=6, row=3)
label_production_times_product_1.config(state = "disabled")

label_production_times_product_2 = tk.Label(win, text="Second product:  5")
label_production_times_product_2.grid(column=6, row=4)
label_production_times_product_2.config(state = "disabled")

label_production_times_product_3 = tk.Label(win, text="Third product:  10")
label_production_times_product_3.grid(column=6, row=5)
label_production_times_product_3.config(state = "disabled")

label_production_times_product_4 = tk.Label(win, text="Forth product:  5")
label_production_times_product_4.grid(column=6, row=6)
label_production_times_product_4.config(state = "disabled")



#management info

#label_spacer = tk.Label(win, text="")
#label_spacer.grid(column=6, row=5)
#label_spacer.config(state = "disabled")


label_time_left = tk.Label(win, text="Time left : not set")
label_time_left.grid(column=5, row=0)
label_time_left.config(state = "disabled")

label_cost_inbound_wh = tk.Label(win, text="Cost inboub WH:  100")
label_cost_inbound_wh.grid(column=6, row=9)
label_cost_inbound_wh.config(state = "disabled")

label_cost_outbound_wh = tk.Label(win, text="Cost outbound wh:  100")
label_cost_outbound_wh.grid(column=6, row=10)
label_cost_outbound_wh.config(state = "disabled")

label_cost_backlog = tk.Label(win, text="Cost backlog : 100")
label_cost_backlog.grid(column=6, row=11)
label_cost_backlog.config(state = "disabled")


bt_done = tk.Button(text="Get delivery", command=getDelivery)
bt_done.grid(column=5, row=15)
bt_done.config(state = "disabled")

label_get_delivery = tk.Label(win, text="Prod 1, prod 2, prod 3, prod 4")
label_get_delivery.grid(column=5, row=16)
label_get_delivery.config(state = "disabled")
########################################################################################################################################
#                                                     POP UP                                                                                  #
########################################################################################################################################
"""
POP-UP function
Description:
This function creates a pop up message to convey some information to the user
Parameters:
msg-The message that is found within the pop up window(set by other functions)
Caveat:
This function for some reason makes the next line of code not exist or have some error(fixed by adding a dummy line)
"""
def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = tk.Label(popup, text=msg, font='Helvetica 10 bold')
    label.pack(side="top", fill="x", pady=10)
    B1 = tk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

########################################################################################################################################
#                                                     THREADED HELPER CLASSES                                                                                #
########################################################################################################################################
"""
Timer thread
Description:
This class is used as a timer to track and count down the time left in the round.
When it is invoked it will count down the time and displaying it through the label the counts down the time.
The Thread will be destroyed after the run function is finished  
"""
class countDownThread(threading.Thread):
    """
    Initiation function
    Description:
    Initializes the class object for the countdown timer
    Parameters:
    threadID - Threads ID
    name - Name of the tread
    counter - time in seconds for the thread to use to count down 
    """
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    """
    run function
    Description:
    When the thread is called and started , this is the function which will execute.
    IT will count down from the time given in seconds and change the label that indicates the time left for the user
    """
    def run(self):
        global round_time
        global counter_time
        counter_time =round_time
        while counter_time > 0 :
            round_time -=1
            counter_time -=1
            label_time_left.config(text="time left :" +str(counter_time))
            time.sleep(1)
"""
Delivery thread
Description:
This thread is used to make the delivery of goods to another tier. When the user fills out the amounts they want to send to the next tier
and click the deliver button while holding the rfid tag over the scanner, this thread will get invoked. This tread will write the data to 
database of what has been delivered as well as deducting from the finished goods. The functions does have error checking. The delivery goods will be
written to the database 
"""
class deliver1(threading.Thread):

    """
    Initiation function
    Description:
    Initializes the class object for the delivery of goods
    Parameters:
    threadID - Threads ID
    name - Name of the tread
    """
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    """
    This function will execute when the thread is started and will destroy the thread once ot has finished running.
    Description:
    This function will work out to whom the next shipment will be sent and capture what will be sent in the database as well as write that data 
    to a rfid tag. This tag will be scanned by the next tier 
    """
    def run(self):
        lst = [['1','1'],['2','1'],['3','2'],['4','3']]
        deliver_to =''
        for i in lst:
            if str(entry_id_number.get()) == i[0]:      
                deliver_to = i[1]                          # works out to who the shipment must go
        print(deliver_to) 

        cur=connection.cursor()
        QUERY="SELECT product_id,product_name FROM clientdb.product WHERE type = 'fg'"       #selectiong the products which can be shipped
        cur.execute(QUERY)
        product_names_id=cur.fetchall() 
        print(product_names_id)                                                           # list of those products containing names and id's
        flag1 = False
        # getting data from the labels and entries
        p1 = label_deliver_1.cget('text')
        p1_a = entry_deliver_1_amount.get()
        p2 = label_deliver_2.cget('text')
        p2_a = entry_deliver_2_amount.get()
        p3 = label_deliver_3.cget('text')
        p3_a = entry_deliver_3_amount.get()
        p4 = label_deliver_4.cget('text')
        p4_a = entry_deliver_4_amount.get()
        try:                      # catching errors like incorrect data types
            deliver_list = [[p1,int(p1_a)],[p2,int(p2_a)],[p3,int(p3_a)],[p4,int(p4_a)]]  # string to int conversion of the product anounts
            flag1 = True #flags are used to track certain occurrences
        except:
            flag1 = False 
            popupmsg("Please reformat, only positive numbers are accepted in the delivery fields !")
        
        if(flag1 == True): # if the flag is tire that means the data provided was correct
            f1 = label_finished_1.cget('text')
            f1_a = label_finished_1_amount.cget('text')
            f2 = label_finished_2.cget('text')
            f2_a = label_finished_2_amount.cget('text')
            f3 = label_finished_3.cget('text')
            f3_a = label_finished_3_amount.cget('text')
            f4 = label_finished_4.cget('text')
            f4_a = label_finished_4_amount.cget('text')

            fg_list = [[f1,f1_a],[f2,f2_a],[f3,f3_a],[f4,f4_a]]

            flag = True 

            for i in range(len(fg_list)):
                if int(fg_list[i][1])<int(deliver_list[i][1]):  # checking if the user has enough finished goods to deliver
                    flag = False
                    break
            if(flag):  #if the user has enough finished goods the operation will proceed to writing to the database and rfid
                print(deliver_list)
                counter = 0

                # match the product names and the id of the product. The ID is needed for capture
                for i in deliver_list:
                    for j in product_names_id:
                        if i[0] == j[1]:
                            deliver_list[counter][0] = j[0]
                            counter +=1
                print(deliver_list)

                #build order for sql

                QUERY="SELECT deliver_id FROM clientdb.deliver"   #returns all the round_id's
                cur=connection.cursor()
                cur.execute(QUERY)
                deliveries=cur.fetchall()
                print(deliveries)

                if(len(deliveries)>=1):
                    deliveries = list(deliveries) # get last row in game table
                    print(deliveries)
                    deliveries = deliveries[-1]
                    deliveries = deliveries[0]        # get the game id 
                    deliveries = deliveries[5:]       # slice the game id 
                    print("in if :",deliveries)
                    deliver_id = str(int(deliveries)+1 ) # add one to the game id
                else:
                    deliver_id = str(1)

                QUERY="SELECT round_id FROM clientdb.rounds ORDER BY round_id DESC LIMIT 1"   #returns last round
                cur.execute(QUERY)
                previous_round =cur.fetchall()
                print(previous_round)
                #building id for delivery table   
                for i in deliver_list:
                    
                    if len(deliver_id) == 1:
                        deliver_id = "del00000" +str(deliver_id)
                    elif(len(deliver_id) == 2):
                        deliver_id = "del0000" +str(deliver_id)
                    elif(len(deliver_id) == 3):
                        deliver_id = "del000" +str(deliver_id)
                    elif(len(deliver_id) == 4):
                        deliver_id = "del00" +str(deliver_id)
                    elif(len(deliver_id) == 5):
                        deliver_id = "del0" +str(deliver_id)
                    else:
                        deliver_id = "del"+str(deliver_id)


                    cur=connection.cursor()
                    QUERY="INSERT INTO clientdb.deliver (deliver_id, amount, time_stamp, product_id, to_tier_id, round_id) VALUES (%s, %s, %s, %s, %s, %s)"
                    print("db insert orders : " + str(i))
                    vals = (deliver_id,i[1],datetime.now(),i[0],deliver_to,previous_round[0][0])
                    cur.execute(QUERY, vals)
                    connection.commit()

                    deliver_id = str(int(deliver_id[4:])+1)
                    
                for i in deliver_list:
                    i.append(deliver_to)
                print("to send to admin order")
                print(deliver_list)

                #updating lables after sucessfull delivery
                label_finished_1_amount.config(text=str(int(f1_a)-int(p1_a)))
                label_finished_2_amount.config(text=str(int(f2_a)-int(p2_a)))
                label_finished_3_amount.config(text=str(int(f3_a)-int(p3_a)))
                label_finished_4_amount.config(text=str(int(f4_a)-int(p4_a)))
                label_backlog_1_amount.config(text=str(int(label_backlog_1_amount.cget('text'))-int(p1_a))) 
                label_backlog_2_amount.config(text=str(int(label_backlog_2_amount.cget('text'))-int(p2_a)))
                label_backlog_3_amount.config(text=str(int(label_backlog_3_amount.cget('text'))-int(p3_a))) 
                label_backlog_4_amount.config(text=str(int(label_backlog_4_amount.cget('text'))-int(p4_a)))

                for i in deliver_list:                         # adds the sender id 
                    i.append(entry_id_number.get())
 
                deliveries = initialClientDataList()  #reuse the initial clients data class to ransmit data to the admin
                deliveries.list_data= deliver_list
                data = deliveries.obj2JSON(deliveries)  # object to json conversion
                res = client.publish(CONST_SEND_DELIVERY,data,qos=2) # send data to the broker where the admin will receive it to track the transactions

                rfid_data =''
                for i in deliver_list:
                    rfid_data = rfid_data + i[1]
                    rfid_data = rfid_data + "#"
                print(rfid_data)
                # write data to the rifd tag
                try:
                        text = rfid_data
                        print("Now place your tag to write")
                        reader.write(text)
                        print("Written")
                finally:
                        GPIO.cleanup()

                bt_deliver.config(state = "disabled")
                return "rfid"
            else:
                print("insufficient finished goods")

"""
Get delivery thread
Description:
This thread is used for getting the data from the rfid tags 
"""
class deliver2(threading.Thread):
    """
    Initiation function
    Description:
    Initializes the class object for the delivery of goods
    Parameters:
    threadID - Threads ID
    name - Name of the tread
    """
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    """
    This function will execute when the thread is started and will destroy the thread once ot has finished running.
    Description:
    This function will be executed when the user press the get delivery button reading the rfid tag and adding the products delivered 
    """        
    def run(self):
        # reading data
        try:
            id, text = reader.read()
            print(id)
            print(text)
        finally:
                GPIO.cleanup()
        data = text.split('#') # making a array from a string by spliting up the read data at a #
        #updateing lables using the data read from the tag
        label_raw_1_amount.config(text= str( int(label_raw_1_amount.cget('text'))+ int(data[0])))
        label_raw_2_amount.config(text= str( int(label_raw_2_amount.cget('text'))+ int(data[1])))
        label_raw_3_amount.config(text= str( int(label_raw_3_amount.cget('text'))+ int(data[2])))
        label_raw_4_amount.config(text= str( int(label_raw_4_amount.cget('text'))+ int(data[3])))
        label_opendeliveries_1_amount.config(text= str( int(label_opendeliveries_1_amount.cget('text'))- int(data[0])))
        label_opendeliveries_2_amount.config(text= str( int(label_opendeliveries_2_amount.cget('text'))- int(data[1])))
        label_opendeliveries_3_amount.config(text= str( int(label_opendeliveries_3_amount.cget('text'))- int(data[2])))
        label_opendeliveries_4_amount.config(text= str( int(label_opendeliveries_4_amount.cget('text'))- int(data[3])))
        label_get_delivery.config(text=text)
        bt_done.config(state = "disabled") # button can only be used once






#start the event-loop of main-Windows-----------------------------
win.mainloop()


