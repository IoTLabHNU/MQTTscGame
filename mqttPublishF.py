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
There are two scripts for this game to work. This mqttTestClientF.py script for clients and the mqttPublishF.py script which is for the admin

What is this script ?
---------------------
This script functions as the admin side script. This script will open a UI that the admin of the gamewill use to set game state rules and values
like the production times of products and the initial amount of products the clients will have. the admin will also set the round time of the game
The admin will first connect to the MQTT server then fill in the data as needed then share state. this will share the data to the clients 
based on their respective tier. After that the admin can press the start round button to start the game. From there on the game will run 
in a automated state and no action is needed from the admin. The Stop round button must not be used now and will be removed since it has no use now.
To stop the game the admin should close the window

How does it work ?
------------------
The following steps it what is needed to follow in order to reproduce the desired result of a working client:
    ->run the script using python3 mqttPublishF.py
    ->Press the connect button
    ->The script will then try to connect to the hive MQTT broker
    ->If the connection was successful a connected text will appear next to the button connect(This is essential)
    ->After the admin is connected the admin can fill in and change game state data for the game.
    ->When the data is changed to the admin's liking the admin should press the share state button
    ->pressing the share state button will share the data to all the clients(data like the products assigned to the clients)
    ->After that the admin can start the game by clicking on the start round button
    ->To stop or quit the game , the user needs to close the window


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
Imports needed to make this file run
"""
import paho.mqtt.publish as publish
#MQTT TestClient GUI
import tkinter as tk
from tkinter import *
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
from initialClientDataList import initialClientDataList
from datetime import datetime
import threading
from threading import Timer
import time

#constant global variables used in the script
CONST_TOPIC_START_ROUND = "startRound"
CONST_TOPIC_STOP_ROUND = "stopRound"
CONST_GAME_ID = "gameId"
CONST_SEND_DATA = "sendData"
CONST_SEND_STATE_T1 = "statet1"
CONST_SEND_STATE_T2 = "statet2"
CONST_SEND_STATE_T3 = "statet3"
CONST_SEND_STATE_T4 = "statet4"

CONST_SEND_ORDER = "send_order"
CONST_SEND_PRODUCTION = "produce"
CONST_SEND_DELIVERY = "send_delivery"


CONST_SEND_ORDER_ACK ="orderAck"
CONST_SEND_DELIVER_ACK ="deliverAck"


global round_time
round_time = 120
round_num = 0
#global game_id
game_id = 0
global product_List

#=================Gets the product list to update the labels on the interface==========================================================#
connection = mysql.connector.connect(host='db',  database='admindb', user='root',password='root',auth_plugin='mysql_native_password')
QUERY="SELECT * FROM admindb.products"   #returns all the products
cur=connection.cursor()
cur.execute(QUERY)
product_List=cur.fetchall() # puts all products into a list
print(product_List) # log product list
QUERY="SELECT * FROM admindb.initialinventory"
cur=connection.cursor()
cur.execute(QUERY)
product_initial_list=cur.fetchall() #puts all products into a list

"""
Update labels
Description:
This function will be invoked once the user connects to the MQTT server. This function uses the product list in the database that is added 
prior to the first run of the game and then update the lables and text's on the UI.
"""
def update_prodcut_lables_inv():
    #fill tier 4
    tier_4 = []
    initial=[]
    production_times = []

    for i in product_List:
        if i[2] =='raw' and i[7] == '4':
            tier_4.append(i[1])
            initial.append(i[8])
            production_times.append(i[3])
    print(tier_4)
    #======inv amounts tier4 ========#
    label_inventory_amounts_4_product_1.config(text=tier_4[0])
    label_inventory_amounts_4_product_2.config(text=tier_4[1])
    label_inventory_amounts_4_product_3.config(text=tier_4[2])
    label_inventory_amounts_4_product_4.config(text=tier_4[3])

    entry_inventory_amounts_4_product_1.insert(0,initial[0])
    entry_inventory_amounts_4_product_2.insert(0,initial[1])
    entry_inventory_amounts_4_product_3.insert(0,initial[2])
    entry_inventory_amounts_4_product_4.insert(0,initial[3])

    tier_3 = []
    initial=[]
    production_times = []
    for i in product_List:
        if i[2] =='raw' and i[7] == '3':
            tier_3.append(i[1])
            initial.append(i[8])
            production_times.append(i[3])
    print(tier_3)

    #======inv amounts tier3 ========#
    label_inventory_amounts_3_product_1.config(text=tier_3[0])
    label_inventory_amounts_3_product_2.config(text=tier_3[1])
    label_inventory_amounts_3_product_3.config(text=tier_3[2])
    label_inventory_amounts_3_product_4.config(text=tier_3[3])

    entry_inventory_amounts_3_product_1.insert(0,initial[0])
    entry_inventory_amounts_3_product_2.insert(0,initial[1])
    entry_inventory_amounts_3_product_3.insert(0,initial[2])
    entry_inventory_amounts_3_product_4.insert(0,initial[3])

    tier_2 = []
    initial=[]
    production_times = []
    for i in product_List:
        if i[2] =='raw' and i[7] == '2':
            tier_2.append(i[1])
            initial.append(i[8])
            production_times.append(i[3])
    print(tier_2)


    #======inv amounts tier2 ========#
    label_inventory_amounts_2_product_1.config(text=tier_2[0])
    label_inventory_amounts_2_product_2.config(text=tier_2[1])
    label_inventory_amounts_2_product_3.config(text=tier_2[2])
    label_inventory_amounts_2_product_4.config(text=tier_2[3])

    entry_inventory_amounts_2_product_1.insert(0,initial[0])
    entry_inventory_amounts_2_product_2.insert(0,initial[1])
    entry_inventory_amounts_2_product_3.insert(0,initial[2])
    entry_inventory_amounts_2_product_4.insert(0,initial[3])

    tier_1 = []
    initial=[]
    production_times = []
    for i in product_List:
        if i[2] =='raw' and i[7] == '1':
            tier_1.append(i[1])
            initial.append(i[8])
            production_times.append(i[3])
    print(tier_1)

    #======inv amounts tier3 ========#
    label_inventory_amounts_1_product_1.config(text=tier_1[0])
    label_inventory_amounts_1_product_2.config(text=tier_1[1])
    label_inventory_amounts_1_product_3.config(text=tier_1[2])
    label_inventory_amounts_1_product_4.config(text=tier_1[3])
    #entry_inventory_amounts_1_product_1.delete(0,END)
    #entry_inventory_amounts_1_product_2.delete(0,END)

    entry_inventory_amounts_1_product_1.insert(0,str(initial[0]))
    entry_inventory_amounts_1_product_2.insert(0,str(initial[1]))
    entry_inventory_amounts_1_product_3.insert(0,str(initial[2]))
    entry_inventory_amounts_1_product_4.insert(0,str(initial[3]))
    print(initial)

#========================================================================#
        #  production time update labels and text entries #

#========================================================================#
def update_labels_production_times():
        #fill tier 4
    tier_4 = []
    production_times = []
    for i in product_List:
        if i[2] =='fg' and i[7] == '4':
            tier_4.append(i[1])
            production_times.append(i[3])

    print(tier_4)
    label_production_time_4_product_1.config(text=tier_4[0])
    label_production_time_4_product_2.config(text=tier_4[1])
    label_production_time_4_product_3.config(text=tier_4[2])
    label_production_time_4_product_4.config(text=tier_4[3])
    entry_production_time_4_product_1.insert(0,production_times[0])
    entry_production_time_4_product_2.insert(0,production_times[1])
    entry_production_time_4_product_3.insert(0,production_times[2])
    entry_production_time_4_product_4.insert(0,production_times[3])


    tier_3 = []

    production_times = []
    for i in product_List:
        if i[2] =='fg' and i[7] == '3':
            tier_3.append(i[1])
            production_times.append(i[3])
    print(tier_3)
    label_production_time_3_product_1.config(text=tier_3[0])
    label_production_time_3_product_2.config(text=tier_3[1])
    label_production_time_3_product_3.config(text=tier_3[2])
    label_production_time_3_product_4.config(text=tier_3[3])
    entry_production_time_3_product_1.insert(0,production_times[0])
    entry_production_time_3_product_2.insert(0,production_times[1])
    entry_production_time_3_product_3.insert(0,production_times[2])
    entry_production_time_3_product_4.insert(0,production_times[3])

    tier_2 = []
    production_times = []
    for i in product_List:
        if i[2] =='fg' and i[7] == '2':
            tier_2.append(i[1])
            production_times.append(i[3])
    print(tier_2)
    label_production_time_2_product_1.config(text=tier_2[0])
    label_production_time_2_product_2.config(text=tier_2[1])
    label_production_time_2_product_3.config(text=tier_2[2])
    label_production_time_2_product_4.config(text=tier_2[3])
    entry_production_time_2_product_1.insert(0,production_times[0])
    entry_production_time_2_product_2.insert(0,production_times[1])
    entry_production_time_2_product_3.insert(0,production_times[2])
    entry_production_time_2_product_4.insert(0,production_times[3])

    tier_1 = []
    initial=[]
    production_times = []
    for i in product_List:
        if i[2] =='fg' and i[7] == '1':
            tier_1.append(i[1])
            production_times.append(i[3])
    print(tier_1)

    label_production_time_1_product_1.config(text=tier_1[0])
    label_production_time_1_product_2.config(text=tier_1[1])
    label_production_time_1_product_3.config(text=tier_1[2])
    label_production_time_1_product_4.config(text=tier_1[3])
    entry_production_time_1_product_1.insert(0,production_times[0])
    entry_production_time_1_product_2.insert(0,production_times[1])
    entry_production_time_1_product_3.insert(0,production_times[2])
    entry_production_time_1_product_4.insert(0,production_times[3])


    print(initial)


#after connection was established
"""
on connect
Description:
After the admin script has connected to the MQTT broker, this function will add a new game record to the game table with the new game
The function will also subscribe the admin script to certain topics that is necessary for gameplay/function so that the admincan receive
data from the other client scripts 
"""
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    labelC.config(text = "connected")

    QUERY="SELECT * FROM admindb.game"   #returns all the products
    cur=connection.cursor()
    cur.execute(QUERY)
    games=cur.fetchall()
    print(games)

    if(len(games)>=1):
        games = list(games) # get last row in game table
        print(games)
        games = games[-1]
        games = games[0]        # get the game id 
        games = games[4:]       # slice the game id 
        print("in if :",games)
        game_id = str(int(games)+1 ) # add one to the game id
    else:
        game_id = str(1)

    if len(game_id) == 1:
        game_id = "game000" +str(game_id)
    elif(len(game_id) == 2):
        game_id = "game00" +str(game_id)
    elif(len(game_id) == 3):
        game_id = "game0" +str(game_id)
    else:
        game_id = "game"+str(game_id)



    
    print(game_id)
    cur=connection.cursor()
    QUERY="INSERT INTO admindb.game (game_id,rounds) VALUES (%s, %s)"
    print("db insert")
    vals = (game_id,str(0))
    cur.execute(QUERY, vals)
    connection.commit()
    


    #subscribe for topics
    client.subscribe(CONST_SEND_DATA, 0)
    client.subscribe(CONST_SEND_ORDER, 0)
    client.subscribe(CONST_SEND_DELIVERY, 0)
    client.subscribe(CONST_SEND_PRODUCTION, 0)
    


#============================now lets send the states====================================#

#----------------------------------state for tier 1--------------------------------------#
"""
send_state_tier1
Description:
This function selects the data from the product list that needs to be sent to tier one.
Returns:
A fixed list for tier1 consisting of products for that tier.
"""
def send_state_tier1():

    tier1_data =[]
    counter = 0
    counter2 = 0
    for i in product_List:
        i = list(i)
        if i[7] == '1':
            if(i[2] == 'fg' and counter ==0):
                i[3] = entry_production_time_1_product_1.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==1):
                i[3] = entry_production_time_1_product_2.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==1):
                i[3] = entry_production_time_1_product_3.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==1):
                i[3] = entry_production_time_1_product_4.get()
            elif(i[2] == 'raw' and counter2 ==0):
                i[8] = entry_inventory_amounts_1_product_1.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==1):
                i[8] = entry_inventory_amounts_1_product_2.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==2):
                i[8] = entry_inventory_amounts_1_product_3.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==3):
                i[8] = entry_inventory_amounts_1_product_4.get()

            tier1_data.append(i)
    print(tier1_data)
    return tier1_data

#----------------------------------state for tier 2--------------------------------------#
"""
send_state_tier2
Description:
This function selects the data from the product list that needs to be sent to tier two.
Returns:
A fixed list for tier2 consisting of products for that tier.
"""
def send_state_tier2():

    tier2_data =[]
    counter = 0
    counter2 = 0
    for i in product_List:
        i = list(i)
        if i[7] == '2':
            if(i[2] == 'fg' and counter ==0):
                i[3] = entry_production_time_2_product_1.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==1):
                i[3] = entry_production_time_2_product_2.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==2):
                i[3] = entry_production_time_2_product_3.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==3):
                i[3] = entry_production_time_2_product_4.get()

            elif(i[2] == 'raw' and counter2 ==0):
                i[8] = entry_inventory_amounts_2_product_1.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==1):
                i[8] = entry_inventory_amounts_2_product_2.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==2):
                i[8] = entry_inventory_amounts_2_product_3.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==3):
                i[8] = entry_inventory_amounts_2_product_4.get()
            tier2_data.append(i)

    print(tier2_data)
    return tier2_data
    

#----------------------------------state for tier 3--------------------------------------#
"""
send_state_tier3
Description:
This function selects the data from the product list that needs to be sent to tier three.
Returns:
A fixed list for tier3 consisting of products for that tier.
"""
def send_state_tier3():

    tier3_data =[]
    counter = 0
    counter2= 0
    for i in product_List:
        i = list(i)
        if i[7] == '3':
            if(i[2] == 'fg' and counter ==0):
                i[3] = entry_production_time_3_product_1.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==1):
                i[3] = entry_production_time_3_product_2.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==2):
                i[3] = entry_production_time_3_product_3.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==3):
                i[3] = entry_production_time_3_product_4.get()
            elif(i[2] == 'raw' and counter2 ==0):
                i[8] = entry_inventory_amounts_3_product_1.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==1):
                i[8] = entry_inventory_amounts_3_product_2.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==2):
                i[8] = entry_inventory_amounts_3_product_3.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==3):
                i[8] = entry_inventory_amounts_3_product_4.get()

            tier3_data.append(i)
    print(tier3_data)
    return tier3_data


#----------------------------------state for tier 4--------------------------------------#
"""
send_state_tier4
Description:
This function selects the data from the product list that needs to be sent to tier four.
Returns:
A fixed list for tier4 consisting of products for that tier.
"""
def send_state_tier4():

    tier4_data =[]
    counter = 0
    counter2 =0
    for i in product_List:
        i = list(i)
        if i[7] == '4':
            if(i[2] == 'fg' and counter ==0):
                i[3] = entry_production_time_4_product_1.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==1):
                i[3] = entry_production_time_4_product_2.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==2):
                i[3] = entry_production_time_4_product_3.get()
                counter+=1
            elif(i[2] == 'fg' and counter ==3):
                i[3] = entry_production_time_4_product_4.get()
            elif(i[2] == 'raw' and counter2 ==0):
                i[8] = entry_inventory_amounts_4_product_1.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==1):
                i[8] = entry_inventory_amounts_4_product_2.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==2):
                i[8] = entry_inventory_amounts_4_product_3.get()
                counter2+=1
            elif(i[2] == 'raw' and counter2 ==3):
                i[8] = entry_inventory_amounts_4_product_4.get()
            tier4_data.append(i)
    print(tier4_data)
    return tier4_data

"""

Share states
Description:
This function just 
"""
def share_states():

    #res = client.publish(CONST_SEND_STATE_T1,send_state_tier1,qos=2)

    #publish tier 1 state#
    t=send_state_tier1()
    initialData_t = initialClientDataList()
    initialData_t.list_data=t
    data = initialData_t.obj2JSON(initialData_t)
    res = client.publish(CONST_SEND_STATE_T1,data,qos=2)
    

    #publish tier 2 state#
    t=send_state_tier2()
    initialData_t = initialClientDataList()

    initialData_t.list_data=t
    data = initialData_t.obj2JSON(initialData_t)
    res = client.publish(CONST_SEND_STATE_T2,data,qos=2)

    #publish tier 3 state#
    t=send_state_tier3()
    initialData_t = initialClientDataList()
    initialData_t.list_data=t
    data = initialData_t.obj2JSON(initialData_t)
    res = client.publish(CONST_SEND_STATE_T3,data,qos=2)
    
    #publish tier 4 state#
    t=send_state_tier4()
    initialData_t = initialClientDataList()
    initialData_t.list_data=t
    data = initialData_t.obj2JSON(initialData_t)
    res = client.publish(CONST_SEND_STATE_T4,data,qos=2)


    round_time = int(entry_set_round_time.get())

    QUERY="SELECT * FROM admindb.game"   #returns all the products
    cur.execute(QUERY)
    games=cur.fetchall()
    games = list(games[-1]) # get last row in game table
    game_id = games[0]
    print(game_id)
    client.publish(CONST_GAME_ID,game_id,qos=2)
    print(res)
    print(round_time)

"""
OEM Order
Description:
This function is used to make orders from the first tier and as to produce a artificial need for products. this will happen on a round to
round basis. For the first 5 rounds one of each of the products is ordered but after that it is stepped up to 2.

"""
def OEM_orders():

    amts = [1,2]
    amt = 0
    if int(label_roundNr.cget('text')) <= 5:
        amt = amts[0]
    else:
        amt = amts[1]

    cur=connection.cursor()
    QUERY="SELECT product_id,product_name FROM admindb.products WHERE type = 'fg' AND tier_tier_id = '1'"   #returns all products
    cur.execute(QUERY)
    products =cur.fetchall()
    products = products
    print(products)

    #returns transaction ID from the transactions table in order to build the new ID
    QUERY="SELECT transaction_id FROM admindb.transaction ORDER BY transaction_id DESC LIMIT 1"   #returns all the round_id's
    cur=connection.cursor()
    cur.execute(QUERY)
    tran =cur.fetchall()
    print("transactions")
    print(tran)
   

    if(len(tran)>=1):
        tran = tran[0][0]
        tran = tran[4:]       # slice the transaction id
        print("in if :",tran)
        transaction_id = str(int(tran)+1 ) # add one to the transaction id
               
    else:
        transaction_id = '1'

    QUERY="SELECT round_id FROM admindb.round ORDER BY round_id DESC LIMIT 1"   #returns last round
    cur.execute(QUERY)
    current_round =cur.fetchall()
    current_round = current_round[0]
    print(current_round)           
    #for loop for each of the 4 products        
    for i in products:

        if len(transaction_id) == 1:
            transaction_id = "tran00000" +str(transaction_id) #building of the new ID
        elif(len(transaction_id) == 2):
            transaction_id = "tran0000" +str(transaction_id)
        elif(len(transaction_id) == 3):
            transaction_id = "tran000" +str(transaction_id)
        elif(len(transaction_id) == 4):
            transaction_id = "tran00" +str(transaction_id)
        elif(len(transaction_id) == 5):
            transaction_id = "tran0" +str(transaction_id)
        else:
            transaction_id = "tran"+str(transaction_id)

        print(transaction_id)

        print(i)
        cur=connection.cursor()
        #inserting this new transaction into the transaction table
        QUERY="INSERT INTO admindb.transaction (transaction_id, to_tier_id, from_tier_id, transaction_type_id, amount, product_id, Round_round_id, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        print("db insert transaction : " + str(i))
        vals = (transaction_id,'1','5','1',amt,i[0],current_round[0],datetime.now())
        print(vals)
        cur.execute(QUERY, vals)
        connection.commit()

        transaction_id = str(int(transaction_id[5:])+1)
            
    #adds the tier to the start of the products to be sent to       
    data =[]
    for i in products:
        data.append(list(i[1:]))
    for i in data:
        i.append(amt)
        i.append('1')

    print("data to send to order reciever")
    print(data)


            
    t=data
    Data_t = initialClientDataList() #instance of the class used for the JSON type
    Data_t.list_data=t
    data = Data_t.obj2JSON(Data_t) #converts the data to be sent as a JSON type.
    client.publish(CONST_SEND_ORDER_ACK,data,qos=2) #publish data to the MQTT broker under the CONST_SEND_ORDER_ACK topic

 

    


#Reseive messages: startRound, stopRound

"""

"""
def on_message(mosq, obj, msg):
    try:
        if msg.topic.startswith(CONST_SEND_DATA):
            #print(str(msg.payload))
            nr = str(msg.payload).replace('b', '')
            nr = nr.replace('\'', '')
            hashIndex = nr.index("#")
            #print(nr)
            labelamt.config(text = nr[:hashIndex])
            labeltier.config(text = nr[hashIndex+1:])
            label_roundState.config(text = "runnning")

        """
        If the topic starts with CONST_SEND_ORDER this means that the message contains a order from one of the tiers. this order contains 
        a JSON data type with a matrix(2-d array) inside that needs to be converted so it can be used. This data is used to write the
        order into the database as a transaction. This is important since the ADMIN script and database is used as sort of a ledger containing
        all of the transactions that transpire in the game. After that the order is also sent to the client that needs to supply the goods.
        Again as a JSON package
        """
        if msg.topic.startswith(CONST_SEND_ORDER):
            s = str(msg.payload)
            s=s[1:]
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)
            #print(o.list_data)
            data = o.list_data
            print(data)

            QUERY="SELECT transaction_id FROM admindb.transaction"   #returns all the round_id's
            cur=connection.cursor()
            cur.execute(QUERY)
            tran =cur.fetchall()
            print("transactions")
            print(tran)
            print(len(tran))


            new_trans = []
            for i in tran:
                new_trans.append(i[0])
            print("presorted")
            print(new_trans)
            new_trans.sort()
            print("sorted")
            print(new_trans)
            

           

            if(len(new_trans)>=1):
                new_trans = new_trans # get last row in game table
                new_trans = new_trans[-1]       # get the game id 
                new_trans = new_trans[4:]       # slice the game id 
                print("in if :",new_trans)
                transaction_id = str(int(new_trans)+1 ) # add one to the game id
               
            else:
                transaction_id = '1'

            QUERY="SELECT round_id FROM admindb.round ORDER BY round_id DESC LIMIT 1"   #returns last round
            cur.execute(QUERY)
            current_round =cur.fetchall()
            current_round = current_round[0]
            print(current_round)           
            
            for i in data:

                if len(transaction_id) == 1:
                    transaction_id = "tran00000" +str(transaction_id)
                elif(len(transaction_id) == 2):
                    transaction_id = "tran0000" +str(transaction_id)
                elif(len(transaction_id) == 3):
                    transaction_id = "tran000" +str(transaction_id)
                elif(len(transaction_id) == 4):
                    transaction_id = "tran00" +str(transaction_id)
                elif(len(transaction_id) == 5):
                    transaction_id = "tran0" +str(transaction_id)
                else:
                    transaction_id = "tran"+str(transaction_id)

                print(transaction_id)

                lst = [['1','2'],['2','3'],['3','4'],['4','4']]
                order_from =''
                for j in lst:
                    if str(i[2]) == j[1]:
                        order_from = j[0]
                print(order_from)
                print(i)
                cur=connection.cursor()
                QUERY="INSERT INTO admindb.transaction (transaction_id, to_tier_id, from_tier_id, transaction_type_id, amount, product_id, Round_round_id, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                print("db insert transaction : " + str(i))
                vals = (transaction_id,i[2],order_from,'1',i[1],i[0],current_round[0],datetime.now())
                print(vals)
                cur.execute(QUERY, vals)
                connection.commit()

                transaction_id = str(int(transaction_id[5:])+1)
            
            
            QUERY="SELECT product_id, product_name, type FROM  admindb.products"   #returns all products
            cur.execute(QUERY)
            products =cur.fetchall()
            products = products
            print(products)
            p_names=[]
            for i in data:
                for j in products:
                    if i[0] == j[0]:
                        i.append(j[1])

            print("data to send to order reciever")
            print(data)


            
            t=data
            Data_t = initialClientDataList()
            Data_t.list_data=t
            data = Data_t.obj2JSON(Data_t)
            client.publish(CONST_SEND_ORDER_ACK,data,qos=2)
            

            

        #========================================================================================================

                                                #Getting the delivery
        #========================================================================================================

        if msg.topic.startswith(CONST_SEND_DELIVERY):
            s = str(msg.payload)
            s=s[1:]
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)
            #print(o.list_data)
            data = o.list_data
            print(data)

            #from_id = data[0][4]


            QUERY="SELECT transaction_id FROM admindb.transaction"   #returns all the round_id's
            cur=connection.cursor()
            cur.execute(QUERY)
            transactions=cur.fetchall()
            new_trans = []
            for i in transactions:
                new_trans.append(i[0])
            print("presorted")
            print(new_trans)
            new_trans.sort()
            print("sorted")
            print(new_trans)
            

           

            if(len(new_trans)>=1):
                new_trans = new_trans # get last row in game table
                new_trans = new_trans[-1]       # get the game id 
                new_trans = new_trans[4:]       # slice the game id 
                print("in if :",new_trans)
                transaction_id = str(int(new_trans)+1 ) # add one to the game id # add one to the game id
            else:
                transaction_id = str(1)

            QUERY="SELECT round_id FROM admindb.round ORDER BY round_id DESC LIMIT 1"   #returns last round
            cur.execute(QUERY)
            previous_round =cur.fetchall()
            print(previous_round[0][0])
            previous_round =previous_round[0][0]
                
            for i in data:

                if len(transaction_id) == 1:
                    transaction_id = "tran00000" +str(transaction_id)
                elif(len(transaction_id) == 2):
                    transaction_id = "tran0000" +str(transaction_id)
                elif(len(transaction_id) == 3):
                    transaction_id = "tran000" +str(transaction_id)
                elif(len(transaction_id) == 4):
                    transaction_id = "tran00" +str(transaction_id)
                elif(len(transaction_id) == 5):
                    transaction_id = "tran0" +str(transaction_id)
                else:
                    transaction_id = "tran"+str(transaction_id)
                print(transaction_id)

                
                cur=connection.cursor()
                QUERY="INSERT INTO admindb.transaction (transaction_id, to_tier_id, from_tier_id, transaction_type_id, amount, product_id, Round_round_id, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                print("db insert delivery to transaction : " + str(i))
                vals = (transaction_id,i[2],i[3],'3',i[1],i[0],previous_round,datetime.now())
                print(vals)
                cur.execute(QUERY, vals)
                connection.commit()

                transaction_id = str(int(transaction_id[4:])+1)
                
            """
            p_id = [tran[0][5],tran[1][5]]
            print(p_id) 
            QUERY="SELECT product_id, product_name, type FROM  admindb.products"   #returns all products
            cur.execute(QUERY)
            products =cur.fetchall()
            products = products
            print(products)
            p_names=[]
            for i in p_id:
                for j in products:
                    if i == j[0]:
                        p_names.append(j[1])
            print(p_names)
            data = [[p_names[0],tran[0][4]],[p_names[1],tran[1][4]],[tran[0][1]]]


            #t=data
            #Data_t = initialClientDataList()
            #Data_t.list_data=t
            #data = Data_t.obj2JSON(Data_t)

            #client.publish(CONST_SEND_DELIVER_ACK,data,qos=2)
            """
        """
        When the topic is under CONST_SEND_PRODUCTION, this means on of the tiers produced some products. Since as earlier stated the admin
        device functions similar to a leadger consisting of all operations that transpire in the game the details of said production
        is written into the transaction database 
        """
        if msg.topic.startswith(CONST_SEND_PRODUCTION):

            s = str(msg.payload)
            s=s[1:]
            s = s.replace('\'', '')
            o = initialClientDataList.json2obj(s)
            #print(o.list_data)
            data = o.list_data
            print(data)

            from_id = data[0][4]


            QUERY="SELECT transaction_id FROM admindb.transaction"   #returns all the round_id's
            cur=connection.cursor()
            cur.execute(QUERY)
            transactions=cur.fetchall()
            new_trans = []
            for i in transactions:
                new_trans.append(i[0])
            print("presorted")
            print(new_trans)
            new_trans.sort()
            print("sorted")
            print(new_trans)
            

           

            if(len(new_trans)>=1):
                new_trans = new_trans[-1]       # get the transaction id
                new_trans = new_trans[4:]       # slice the transaction id 
                print("in if :",new_trans)
                transaction_id = str(int(new_trans)+1 ) # add one to the transaction id #
            else:
                transaction_id = str(1)

            QUERY="SELECT round_id FROM admindb.round ORDER BY round_id DESC LIMIT 1"   #returns last round
            cur.execute(QUERY)
            previous_round =cur.fetchall()
            print(previous_round[0][0])
            previous_round =previous_round[0][0]
                
            for i in data:

                if len(transaction_id) == 1:
                    transaction_id = "tran00000" +str(transaction_id)
                elif(len(transaction_id) == 2):
                    transaction_id = "tran0000" +str(transaction_id)
                elif(len(transaction_id) == 3):
                    transaction_id = "tran000" +str(transaction_id)
                elif(len(transaction_id) == 4):
                    transaction_id = "tran00" +str(transaction_id)
                elif(len(transaction_id) == 5):
                    transaction_id = "tran0" +str(transaction_id)
                else:
                    transaction_id = "tran"+str(transaction_id)


                cur=connection.cursor()
                QUERY="INSERT INTO admindb.transaction (transaction_id, to_tier_id, from_tier_id, transaction_type_id, amount, product_id, Round_round_id, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                print("db insert production to transaction : " + str(i))
                vals = (transaction_id,from_id,from_id,'2',i[1],i[3],previous_round,datetime.now())
                print(vals)
                cur.execute(QUERY, vals)
                connection.commit()

                transaction_id = str(int(transaction_id[4:])+1)



        


            
    
                
    except:
        e = sys.exc_info()[0]
        print(e)

#Send data from Client to Admin via Server

"""
Start Round 
Description:
This function will be invoked once the user presses the start round button. This function will add the round to the database as well as lock
the interface in a way that the admin can't change state details or influence the game. This rounds last for as long as the timer of the 
timer thread calls the stop round function.
"""
def process_start_round():
    global round_num
    round_num = round_num + 1

    QUERY="SELECT round_id FROM admindb.round"   #returns all the round_id's
    cur=connection.cursor()
    cur.execute(QUERY)
    rounds=cur.fetchall()
    #print(rounds)

    if(len(rounds)>=1):
        rounds = list(rounds) # get last row in game table
        #print(rounds)
        rounds = rounds[-1]
        rounds = rounds[0]        # get the game id 
        rounds = rounds[5:]       # slice the game id 
        print("in if :",rounds)
        round_id = str(int(rounds)+1 ) # add one to the game id
    else:
        round_id = str(1)

    if len(round_id) == 1:
        round_id = "round0000" +str(round_id)
    elif(len(round_id) == 2):
        round_id = "round000" +str(round_id)
    elif(len(round_id) == 3):
        round_id = "round00" +str(round_id)
    elif(len(round_id) == 4):
        round_id = "round0" +str(round_id)
    else:
        round_id = "round"+str(round_id)

    QUERY="SELECT * FROM admindb.game"   #returns all the games
    cur.execute(QUERY)
    games=cur.fetchall()
    games = list(games[-1]) # get last row in game table
    game_id = games[0]
    print(game_id)

    cur=connection.cursor()
    QUERY="INSERT INTO admindb.round (round_id,round_number,round_length,start_time,end_time,game_id) VALUES (%s, %s, %s, %s, %s, %s)"
    print("db insert round")
    vals = (round_id,round_num,round_time,datetime.now(),datetime.now(),game_id)
    cur.execute(QUERY, vals)
    connection.commit()

    label_roundNr.config(text = str(round_num))
    client.publish("startRound",str(round_num)+"#"+str(round_id))
    #threading.Thread(target=timers).start()
    
    #client.publish("startRound",str(round_num)+"#"+str(round_id))
    

    #====================content_production_times=======================#
    lable_production_times_1.config(state = "disabled")
    label_production_time_1_product_1.config(state = "disabled") #label_name of section_tier_product number
    label_production_time_1_product_2.config(state = "disabled")
    label_production_time_1_product_3.config(state = "disabled") 
    label_production_time_1_product_4.config(state = "disabled")
    entry_production_time_1_product_1.config(state = "disabled")
    entry_production_time_1_product_2.config(state = "disabled")
    entry_production_time_1_product_3.config(state = "disabled")
    entry_production_time_1_product_4.config(state = "disabled")
    #==
    lable_production_times_2.config(state = "disabled")
    label_production_time_2_product_1.config(state = "disabled")
    label_production_time_2_product_2.config(state = "disabled")
    label_production_time_2_product_3.config(state = "disabled")
    label_production_time_2_product_4.config(state = "disabled")
    entry_production_time_2_product_1.config(state = "disabled")
    entry_production_time_2_product_2.config(state = "disabled")
    entry_production_time_2_product_3.config(state = "disabled")
    entry_production_time_2_product_4.config(state = "disabled")
    #==
    lable_production_times_3.config(state = "disabled")
    label_production_time_3_product_1.config(state = "disabled")
    label_production_time_3_product_2.config(state = "disabled")
    label_production_time_3_product_3.config(state = "disabled")
    label_production_time_3_product_4.config(state = "disabled")
    entry_production_time_3_product_1.config(state = "disabled")
    entry_production_time_3_product_2.config(state = "disabled")
    entry_production_time_3_product_3.config(state = "disabled")
    entry_production_time_3_product_4.config(state = "disabled")
    #==
    lable_production_times_4.config(state = "disabled")
    label_production_time_4_product_1.config(state = "disabled")
    label_production_time_4_product_2.config(state = "disabled")
    label_production_time_4_product_3.config(state = "disabled")
    label_production_time_4_product_4.config(state = "disabled")
    entry_production_time_4_product_1.config(state = "disabled")
    entry_production_time_4_product_2.config(state = "disabled")
    entry_production_time_4_product_3.config(state = "disabled")
    entry_production_time_4_product_4.config(state = "disabled")
    #====================content_initial_amounts=======================#
    lable_inventory_amounts_1.config(state = "disabled")
    label_inventory_amounts_1_product_1.config(state = "disabled")
    label_inventory_amounts_1_product_2.config(state = "disabled")
    label_inventory_amounts_1_product_3.config(state = "disabled")
    label_inventory_amounts_1_product_4.config(state = "disabled")
    entry_inventory_amounts_1_product_1.config(state = "disabled")
    entry_inventory_amounts_1_product_2.config(state = "disabled")
    entry_inventory_amounts_1_product_3.config(state = "disabled")
    entry_inventory_amounts_1_product_4.config(state = "disabled")
    #==
    lable_inventory_amounts_2.config(state = "disabled")
    label_inventory_amounts_2_product_1.config(state = "disabled")
    label_inventory_amounts_2_product_2.config(state = "disabled")
    label_inventory_amounts_2_product_3.config(state = "disabled")
    label_inventory_amounts_2_product_4.config(state = "disabled")
    entry_inventory_amounts_2_product_1.config(state = "disabled")
    entry_inventory_amounts_2_product_2.config(state = "disabled")
    entry_inventory_amounts_2_product_3.config(state = "disabled")
    entry_inventory_amounts_2_product_4.config(state = "disabled")
    #==
    lable_inventory_amounts_3.config(state = "disabled")
    label_inventory_amounts_3_product_1.config(state = "disabled")
    label_inventory_amounts_3_product_2.config(state = "disabled")
    label_inventory_amounts_3_product_3.config(state = "disabled")
    label_inventory_amounts_3_product_4.config(state = "disabled")
    entry_inventory_amounts_3_product_1.config(state = "disabled")
    entry_inventory_amounts_3_product_2.config(state = "disabled")
    entry_inventory_amounts_3_product_3.config(state = "disabled")
    entry_inventory_amounts_3_product_4.config(state = "disabled")
    #==
    lable_inventory_amounts_4.config(state = "disabled")
    label_inventory_amounts_4_product_1.config(state = "disabled")
    label_inventory_amounts_4_product_2.config(state = "disabled")
    label_inventory_amounts_4_product_3.config(state = "disabled")
    label_inventory_amounts_4_product_4.config(state = "disabled")
    entry_inventory_amounts_4_product_1.config(state = "disabled")
    entry_inventory_amounts_4_product_2.config(state = "disabled")
    entry_inventory_amounts_4_product_3.config(state = "disabled")
    entry_inventory_amounts_4_product_4.config(state = "disabled")
    #========round_time============================================#
    label_set_round_time.config(state = "disabled")
    entry_set_round_time.config(state = "disabled")
    #bt_set_round_time.config(state = "disabled")
    bt_set_state.config(state = "disabled")
    #this next code starts the timer of the game. This will make rounds top and start
    listenerThread = timer_thread(1, "Listener Thread")
    listenerThread.daemon = True
    listenerThread.start()


"""
inc 
"""
def inc_round_count_db():
    cur=connection.cursor()
    QUERY="SELECT MAX(game_id) FROM admindb.game"   #returns last game id
    cur.execute(QUERY)
    current_game_id = cur.fetchall()
    print("this is the current gameID")
    print(current_game_id)
    current_game_id = current_game_id[0][0]

    sql = "UPDATE admindb.game SET rounds = %s WHERE game_id = %s"
    val = (label_roundNr.cget('text'), current_game_id)
    cur.execute(sql, val)
    connection.commit()


"""
Stop Round
Description:
This function is used to signal the clients connected to the game that the round has stopped. When stopping the round , it will push a new
round record into the database. A line of code would also run updating the end time of that round. After that a publish is sent to the MQTT broker
and the clients which are subscribed gets the message to stop the round. 
"""
def process_stop_round():
    inc_round_count_db()
    QUERY="SELECT round_id FROM admindb.round"   #returns all the round_id's
    cur=connection.cursor()
    cur.execute(QUERY)
    rounds=cur.fetchall()
    print(rounds)

    rounds = list(rounds) # get last row in game table
    print(rounds)
    rounds = rounds[-1]
    rounds = rounds[0]        # get the round_id 

    sql = "UPDATE admindb.round SET end_time = %s WHERE round_id = %s"  #update the end time of the round
    val = (datetime.now(), rounds)

    cur.execute(sql, val)

    connection.commit()
    OEM_orders()            #orders from the first tier as the OEM

    res = client.publish("stopRound","round stopped",qos=2)

#Connect to Server
"""
Connect to the MQTT server
Description:
This function is used to connect the admin script to the MQTT server. This is essential since the MQTT server manages the communication 
between the clients and the admin script. When the process connects the admin to the server other functions is called 
update_prodcut_lables_inv,update_labels_production_times which updates the labels to the correct products.

"""
def process_connect2Server():
    bt_connect2Server.config(state = "disabled")     #Button disable

    ##connect 2 MQTTServer:
    print("Start connecting to Server")
    
    label_roundNr.config(text = str(round))
    label_roundState.config(text = "running")
    label_roundNr.config(state = "normal")
    label2.config(state = "normal")
    labelC.config(state = "normal")
    bt_start.config(state = "normal")
    bt_stop.config(state = "normal")
    label_roundState.config(state = "normal")
    



    #====================content_production_times=======================#
    lable_production_times_1.config(state = "normal")
    label_production_time_1_product_1.config(state = "normal")
    label_production_time_1_product_2.config(state = "normal")
    label_production_time_1_product_3.config(state = "normal")
    label_production_time_1_product_4.config(state = "normal")

    entry_production_time_1_product_1.config(state = "normal")
    entry_production_time_1_product_2.config(state = "normal")
    entry_production_time_1_product_3.config(state = "normal")
    entry_production_time_1_product_4.config(state = "normal")
    #==
    lable_production_times_2.config(state = "normal")
    label_production_time_2_product_1.config(state = "normal")
    label_production_time_2_product_2.config(state = "normal")
    label_production_time_2_product_3.config(state = "normal")
    label_production_time_2_product_4.config(state = "normal")

    entry_production_time_2_product_1.config(state = "normal")
    entry_production_time_2_product_2.config(state = "normal")
    entry_production_time_2_product_3.config(state = "normal")
    entry_production_time_2_product_4.config(state = "normal")
    #==
    lable_production_times_3.config(state = "normal")
    label_production_time_3_product_1.config(state = "normal")
    label_production_time_3_product_2.config(state = "normal")
    label_production_time_3_product_3.config(state = "normal")
    label_production_time_3_product_4.config(state = "normal")

    entry_production_time_3_product_1.config(state = "normal")
    entry_production_time_3_product_2.config(state = "normal")
    entry_production_time_3_product_3.config(state = "normal")
    entry_production_time_3_product_4.config(state = "normal")
    #==
    lable_production_times_4.config(state = "normal")
    label_production_time_4_product_1.config(state = "normal")
    label_production_time_4_product_2.config(state = "normal")
    label_production_time_4_product_3.config(state = "normal")
    label_production_time_4_product_4.config(state = "normal")

    entry_production_time_4_product_1.config(state = "normal")
    entry_production_time_4_product_2.config(state = "normal")
    entry_production_time_4_product_3.config(state = "normal")
    entry_production_time_4_product_4.config(state = "normal")

    #====================content_initial_amounts=======================#
    lable_inventory_amounts_1.config(state = "normal")
    label_inventory_amounts_1_product_1.config(state = "normal")
    label_inventory_amounts_1_product_2.config(state = "normal")
    label_inventory_amounts_1_product_3.config(state = "normal")
    label_inventory_amounts_1_product_4.config(state = "normal")

    entry_inventory_amounts_1_product_1.config(state = "normal")
    entry_inventory_amounts_1_product_2.config(state = "normal")
    entry_inventory_amounts_1_product_3.config(state = "normal")
    entry_inventory_amounts_1_product_4.config(state = "normal")
    #==
    lable_inventory_amounts_2.config(state = "normal")
    label_inventory_amounts_2_product_1.config(state = "normal")
    label_inventory_amounts_2_product_2.config(state = "normal")
    label_inventory_amounts_2_product_3.config(state = "normal")
    label_inventory_amounts_2_product_4.config(state = "normal")

    entry_inventory_amounts_2_product_1.config(state = "normal")
    entry_inventory_amounts_2_product_2.config(state = "normal")
    entry_inventory_amounts_2_product_3.config(state = "normal")
    entry_inventory_amounts_2_product_4.config(state = "normal")

    #==
    lable_inventory_amounts_3.config(state = "normal")
    label_inventory_amounts_3_product_1.config(state = "normal")
    label_inventory_amounts_3_product_2.config(state = "normal")
    label_inventory_amounts_3_product_3.config(state = "normal")
    label_inventory_amounts_3_product_4.config(state = "normal")

    entry_inventory_amounts_3_product_1.config(state = "normal")
    entry_inventory_amounts_3_product_2.config(state = "normal")
    entry_inventory_amounts_3_product_3.config(state = "normal")
    entry_inventory_amounts_3_product_4.config(state = "normal")

    #==
    lable_inventory_amounts_4.config(state = "normal")
    label_inventory_amounts_4_product_1.config(state = "normal")
    label_inventory_amounts_4_product_2.config(state = "normal")
    label_inventory_amounts_4_product_3.config(state = "normal")
    label_inventory_amounts_4_product_4.config(state = "normal")

    entry_inventory_amounts_4_product_1.config(state = "normal")
    entry_inventory_amounts_4_product_2.config(state = "normal")
    entry_inventory_amounts_4_product_3.config(state = "normal")
    entry_inventory_amounts_4_product_4.config(state = "normal")
    #========round_time============================================#
    label_set_round_time.config(state = "normal")
    entry_set_round_time.config(state = "normal")
    #bt_set_round_time.config(state = "normal")
    bt_set_state.config(state = "normal")

    update_prodcut_lables_inv()
    update_labels_production_times()
    entry_set_round_time.delete(0, 'end')
    entry_set_round_time.insert(0, '120')


    client.connect("127.0.0.1")
    client.loop_start()

#Main-Program
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

win = tk.Tk()
win.title("TEST MQTT Admin")
win.geometry("1100x400")



##############################################################################################################################
#                                               BUILDING OF THE INTERFACE                                                    #
##############################################################################################################################
#widgets --------------------------------------------------------
bt_connect2Server = tk.Button(text="Connect", command=process_connect2Server)
bt_connect2Server.grid(column=0, row=0)

labelC = tk.Label(win, text="Connected")
labelC.grid(column=1, row=0)
labelC.config(state = "disabled")


#Button connect
bt_start = tk.Button(text="Start round", command=process_start_round) 
bt_start.grid(column=2, row=0)
bt_start.config(state = "disabled")


#stop round button
bt_stop = tk.Button(text="Stop round", command=process_stop_round)
bt_stop.grid(column=3, row=0)
bt_stop.config(state = "disabled")

#new row
label2 = tk.Label(win, text="Actual Round:")
label2.grid(column=4, row=0)
label2.config(state = "disabled")    

label_roundNr = tk.Label(win, text="")
label_roundNr.grid(column=5, row=0)
label_roundNr.config(state = "disabled")  
 
label_roundState = tk.Label(win, text="")
label_roundState.grid(column=6, row=0)
label_roundState.config(state = "disabled")  

bt_set_state = tk.Button(text="Share State", command=share_states) 
bt_set_state.grid(column=7, row=0)
bt_set_state.config(state = "disabled")

#tier 1 production times
lable_production_times_1 = tk.Label(win, text="Tier 1 Production Times")
lable_production_times_1.grid(column=0, row=1)
lable_production_times_1.config(state = "disabled")

label_production_time_1_product_1 = tk.Label(win, text="Product one")
label_production_time_1_product_1.grid(column=0, row=2)
label_production_time_1_product_1.config(state = "disabled")

label_production_time_1_product_2 = tk.Label(win, text="Product two")
label_production_time_1_product_2.grid(column=0, row=3)
label_production_time_1_product_2.config(state = "disabled")

label_production_time_1_product_3 = tk.Label(win, text="Product three")
label_production_time_1_product_3.grid(column=0, row=4)
label_production_time_1_product_3.config(state = "disabled")

label_production_time_1_product_4 = tk.Label(win, text="Product four")
label_production_time_1_product_4.grid(column=0, row=5)
label_production_time_1_product_4.config(state = "disabled")

entry_production_time_1_product_1 = tk.Entry(win)
entry_production_time_1_product_1.grid(column=1, row=2)
entry_production_time_1_product_1.config(state = "disabled")

entry_production_time_1_product_2 = tk.Entry(win)
entry_production_time_1_product_2.grid(column=1, row=3)
entry_production_time_1_product_2.config(state = "disabled")

entry_production_time_1_product_3 = tk.Entry(win)
entry_production_time_1_product_3.grid(column=1, row=4)
entry_production_time_1_product_3.config(state = "disabled")

entry_production_time_1_product_4 = tk.Entry(win)
entry_production_time_1_product_4.grid(column=1, row=5)
entry_production_time_1_product_4.config(state = "disabled")


#tier2 production times
lable_production_times_2 = tk.Label(win, text="Tier 2 Production Times")
lable_production_times_2.grid(column=2, row=1)
lable_production_times_2.config(state = "disabled")

label_production_time_2_product_1 = tk.Label(win, text="Product one")
label_production_time_2_product_1.grid(column=2, row=2)
label_production_time_2_product_1.config(state = "disabled")

label_production_time_2_product_2 = tk.Label(win, text="Product two")
label_production_time_2_product_2.grid(column=2, row=3)
label_production_time_2_product_2.config(state = "disabled")

label_production_time_2_product_3 = tk.Label(win, text="Product three")
label_production_time_2_product_3.grid(column=2, row=4)
label_production_time_2_product_3.config(state = "disabled")

label_production_time_2_product_4 = tk.Label(win, text="Product four")
label_production_time_2_product_4.grid(column=2, row=5)
label_production_time_2_product_4.config(state = "disabled")

entry_production_time_2_product_1 = tk.Entry(win)
entry_production_time_2_product_1.grid(column=3, row=2)
entry_production_time_2_product_1.config(state = "disabled")

entry_production_time_2_product_2 = tk.Entry(win)
entry_production_time_2_product_2.grid(column=3, row=3)
entry_production_time_2_product_2.config(state = "disabled")

entry_production_time_2_product_3 = tk.Entry(win)
entry_production_time_2_product_3.grid(column=3, row=4)
entry_production_time_2_product_3.config(state = "disabled")

entry_production_time_2_product_4 = tk.Entry(win)
entry_production_time_2_product_4.grid(column=3, row=5)
entry_production_time_2_product_4.config(state = "disabled")


#tier 3 production times
lable_production_times_3 = tk.Label(win, text="Tier 3 Production Times")
lable_production_times_3.grid(column=4 ,row=1)
lable_production_times_3.config(state = "disabled")

label_production_time_3_product_1 = tk.Label(win, text="Product one")
label_production_time_3_product_1.grid(column=4, row=2)
label_production_time_3_product_1.config(state = "disabled")

label_production_time_3_product_2 = tk.Label(win, text="Product two")
label_production_time_3_product_2.grid(column=4, row=3)
label_production_time_3_product_2.config(state = "disabled")

label_production_time_3_product_3 = tk.Label(win, text="Product one")
label_production_time_3_product_3.grid(column=4, row=4)
label_production_time_3_product_3.config(state = "disabled")

label_production_time_3_product_4 = tk.Label(win, text="Product two")
label_production_time_3_product_4.grid(column=4, row=5)
label_production_time_3_product_4.config(state = "disabled")

entry_production_time_3_product_1 = tk.Entry(win)
entry_production_time_3_product_1.grid(column=5, row=2)
entry_production_time_3_product_1.config(state = "disabled")

entry_production_time_3_product_2 = tk.Entry(win)
entry_production_time_3_product_2.grid(column=5, row=3)
entry_production_time_3_product_2.config(state = "disabled")

entry_production_time_3_product_3 = tk.Entry(win)
entry_production_time_3_product_3.grid(column=5, row=4)
entry_production_time_3_product_3.config(state = "disabled")

entry_production_time_3_product_4 = tk.Entry(win)
entry_production_time_3_product_4.grid(column=5, row=5)
entry_production_time_3_product_4.config(state = "disabled")

#tier 4 production times
lable_production_times_4 = tk.Label(win, text="Tier 4 Production Times")
lable_production_times_4.grid(column=6, row=1)
lable_production_times_4.config(state = "disabled")

label_production_time_4_product_1 = tk.Label(win, text="Product one")
label_production_time_4_product_1.grid(column=6, row=2)
label_production_time_4_product_1.config(state = "disabled")

label_production_time_4_product_2 = tk.Label(win, text="Product two")
label_production_time_4_product_2.grid(column=6, row=3)
label_production_time_4_product_2.config(state = "disabled")

label_production_time_4_product_3 = tk.Label(win, text="Product one")
label_production_time_4_product_3.grid(column=6, row=4)
label_production_time_4_product_3.config(state = "disabled")

label_production_time_4_product_4 = tk.Label(win, text="Product two")
label_production_time_4_product_4.grid(column=6, row=5)
label_production_time_4_product_4.config(state = "disabled")

entry_production_time_4_product_1 = tk.Entry(win)
entry_production_time_4_product_1.grid(column=7, row=2)
entry_production_time_4_product_1.config(state = "disabled")

entry_production_time_4_product_2 = tk.Entry(win)
entry_production_time_4_product_2.grid(column=7, row=3)
entry_production_time_4_product_2.config(state = "disabled")

entry_production_time_4_product_3 = tk.Entry(win)
entry_production_time_4_product_3.grid(column=7, row=4)
entry_production_time_4_product_3.config(state = "disabled")

entry_production_time_4_product_4 = tk.Entry(win)
entry_production_time_4_product_4.grid(column=7, row=5)
entry_production_time_4_product_4.config(state = "disabled")



#=====================================================================================
#tier 1 initial inventory amount
lable_inventory_amounts_1 = tk.Label(win, text="Tier 1 initial inventory")
lable_inventory_amounts_1.grid(column=0, row=6)
lable_inventory_amounts_1.config(state = "disabled")

label_inventory_amounts_1_product_1 = tk.Label(win, text="Product one")
label_inventory_amounts_1_product_1.grid(column=0, row=7)
label_inventory_amounts_1_product_1.config(state = "disabled")

label_inventory_amounts_1_product_2 = tk.Label(win, text="Product two")
label_inventory_amounts_1_product_2.grid(column=0, row=8)
label_inventory_amounts_1_product_2.config(state = "disabled")

label_inventory_amounts_1_product_3 = tk.Label(win, text="Product three")
label_inventory_amounts_1_product_3.grid(column=0, row=9)
label_inventory_amounts_1_product_3.config(state = "disabled")

label_inventory_amounts_1_product_4 = tk.Label(win, text="Product four")
label_inventory_amounts_1_product_4.grid(column=0, row=10)
label_inventory_amounts_1_product_4.config(state = "disabled")

entry_inventory_amounts_1_product_1 = tk.Entry(win)
entry_inventory_amounts_1_product_1.grid(column=1, row=7)
entry_inventory_amounts_1_product_1.config(state = "disabled")

entry_inventory_amounts_1_product_2 = tk.Entry(win)
entry_inventory_amounts_1_product_2.grid(column=1, row=8)
entry_inventory_amounts_1_product_2.config(state = "disabled")

entry_inventory_amounts_1_product_3 = tk.Entry(win)
entry_inventory_amounts_1_product_3.grid(column=1, row=9)
entry_inventory_amounts_1_product_3.config(state = "disabled")

entry_inventory_amounts_1_product_4 = tk.Entry(win)
entry_inventory_amounts_1_product_4.grid(column=1, row=10)
entry_inventory_amounts_1_product_4.config(state = "disabled")

#tier 2 initial inventory amount
lable_inventory_amounts_2 = tk.Label(win, text="Tier 2 initial inventory")
lable_inventory_amounts_2.grid(column=2, row=6)
lable_inventory_amounts_2.config(state = "disabled")

label_inventory_amounts_2_product_1 = tk.Label(win, text="Product one")
label_inventory_amounts_2_product_1.grid(column=2, row=7)
label_inventory_amounts_2_product_1.config(state = "disabled")

label_inventory_amounts_2_product_2 = tk.Label(win, text="Product two")
label_inventory_amounts_2_product_2.grid(column=2, row=8)
label_inventory_amounts_2_product_2.config(state = "disabled")

label_inventory_amounts_2_product_3 = tk.Label(win, text="Product three")
label_inventory_amounts_2_product_3.grid(column=2, row=9)
label_inventory_amounts_2_product_3.config(state = "disabled")

label_inventory_amounts_2_product_4 = tk.Label(win, text="Product four")
label_inventory_amounts_2_product_4.grid(column=2, row=10)
label_inventory_amounts_2_product_4.config(state = "disabled")

entry_inventory_amounts_2_product_1 = tk.Entry(win)
entry_inventory_amounts_2_product_1.grid(column=3, row=7)
entry_inventory_amounts_2_product_1.config(state = "disabled")

entry_inventory_amounts_2_product_2 = tk.Entry(win)
entry_inventory_amounts_2_product_2.grid(column=3, row=8)
entry_inventory_amounts_2_product_2.config(state = "disabled")

entry_inventory_amounts_2_product_3 = tk.Entry(win)
entry_inventory_amounts_2_product_3.grid(column=3, row=9)
entry_inventory_amounts_2_product_3.config(state = "disabled")

entry_inventory_amounts_2_product_4 = tk.Entry(win)
entry_inventory_amounts_2_product_4.grid(column=3, row=10)
entry_inventory_amounts_2_product_4.config(state = "disabled")

#tier 3 initial inventory amount
lable_inventory_amounts_3 = tk.Label(win, text="Tier 3 initial inventory")
lable_inventory_amounts_3.grid(column=4, row=6)
lable_inventory_amounts_3.config(state = "disabled")

label_inventory_amounts_3_product_1 = tk.Label(win, text="Product one")
label_inventory_amounts_3_product_1.grid(column=4, row=7)
label_inventory_amounts_3_product_1.config(state = "disabled")

label_inventory_amounts_3_product_2 = tk.Label(win, text="Product two")
label_inventory_amounts_3_product_2.grid(column=4, row=8)
label_inventory_amounts_3_product_2.config(state = "disabled")

label_inventory_amounts_3_product_3 = tk.Label(win, text="Product three")
label_inventory_amounts_3_product_3.grid(column=4, row=9)
label_inventory_amounts_3_product_3.config(state = "disabled")

label_inventory_amounts_3_product_4 = tk.Label(win, text="Product four")
label_inventory_amounts_3_product_4.grid(column=4, row=10)
label_inventory_amounts_3_product_4.config(state = "disabled")

entry_inventory_amounts_3_product_1 = tk.Entry(win)
entry_inventory_amounts_3_product_1.grid(column=5, row=7)
entry_inventory_amounts_3_product_1.config(state = "disabled")

entry_inventory_amounts_3_product_2 = tk.Entry(win)
entry_inventory_amounts_3_product_2.grid(column=5, row=8)
entry_inventory_amounts_3_product_2.config(state = "disabled")

entry_inventory_amounts_3_product_3 = tk.Entry(win)
entry_inventory_amounts_3_product_3.grid(column=5, row=9)
entry_inventory_amounts_3_product_3.config(state = "disabled")

entry_inventory_amounts_3_product_4 = tk.Entry(win)
entry_inventory_amounts_3_product_4.grid(column=5, row=10)
entry_inventory_amounts_3_product_4.config(state = "disabled")

#tier 4 initial inventory amount
lable_inventory_amounts_4 = tk.Label(win, text="Tier 4 initial inventory")
lable_inventory_amounts_4.grid(column=6, row=6)
lable_inventory_amounts_4.config(state = "disabled")

label_inventory_amounts_4_product_1 = tk.Label(win, text="Product one")
label_inventory_amounts_4_product_1.grid(column=6, row=7)
label_inventory_amounts_4_product_1.config(state = "disabled")

label_inventory_amounts_4_product_2 = tk.Label(win, text="Product two")
label_inventory_amounts_4_product_2.grid(column=6, row=8)
label_inventory_amounts_4_product_2.config(state = "disabled")

label_inventory_amounts_4_product_3 = tk.Label(win, text="Product three")
label_inventory_amounts_4_product_3.grid(column=6, row=9)
label_inventory_amounts_4_product_3.config(state = "disabled")

label_inventory_amounts_4_product_4 = tk.Label(win, text="Product four")
label_inventory_amounts_4_product_4.grid(column=6, row=10)
label_inventory_amounts_4_product_4.config(state = "disabled")

entry_inventory_amounts_4_product_1 = tk.Entry(win)
entry_inventory_amounts_4_product_1.grid(column=7, row=7)
entry_inventory_amounts_4_product_1.config(state = "disabled")

entry_inventory_amounts_4_product_2 = tk.Entry(win)
entry_inventory_amounts_4_product_2.grid(column=7, row=8)
entry_inventory_amounts_4_product_2.config(state = "disabled")

entry_inventory_amounts_4_product_3 = tk.Entry(win)
entry_inventory_amounts_4_product_3.grid(column=7, row=9)
entry_inventory_amounts_4_product_3.config(state = "disabled")

entry_inventory_amounts_4_product_4 = tk.Entry(win)
entry_inventory_amounts_4_product_4.grid(column=7, row=10)
entry_inventory_amounts_4_product_4.config(state = "disabled")
#=============================================================================================

label_spacer_1 = tk.Label(win, text="")
label_spacer_1.grid(column=0, row=11)
label_spacer_1.config(state = "disabled")

label_spacer_2 = tk.Label(win, text="")
label_spacer_2.grid(column=1, row=11)
label_spacer_2.config(state = "disabled")

label_spacer_3 = tk.Label(win, text="")
label_spacer_3.grid(column=2, row=11)
label_spacer_3.config(state = "disabled")

label_set_round_time = tk.Label(win, text="Round time: ")
label_set_round_time.grid(column=0, row=12)
label_set_round_time.config(state = "disabled")

entry_set_round_time = tk.Entry()
entry_set_round_time.grid(column=1, row=12)
entry_set_round_time.config(state = "disabled")

"""
timer_thread
Description:
This class is used to create a thread that controls the timings of the game. This tread will once the user of the admin script starts the first
round control the starts and stops of the rounds as the game progresses based on the required amount the admin specified.
This function will allow 20 seconds between the stop of a round and the start of a next. 

Parameters: 
threadID - id given to the thread
name - name given to the thread

notes:
Add another paramete that passes in the time of the rounds instead of getting it within this function
"""
class timer_thread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    """
    run function
    Description:
    This function will start running as soon as the class is invoked. This function will start and stop the rounds based on the amount of
    time the admin specified and the 20 seconds between each stop and start of the rounds.
    """
    def run(self):
        time.sleep(int(entry_set_round_time.get())) # gets the amount of time in seconds that the round length will be
        process_stop_round()                        # calls the start round function
        time.sleep(20)
        process_start_round()                       # calls the stop round function

#starts the UI up
win.mainloop()
 


