import requests
import json
from peewee import *
import os
import sqlite3
key1="jhuddr2ar2x395x23fzr56mx"
###############################################################################
#function to request car id
def carid_request(car_make,car_model,car_year,key):
    carid=requests.get("https://api.edmunds.com/api/vehicle/v2/{}/{}?state=used&year={}&view=basic&fmt=json&api_key={}".format(car_make,car_model,car_year,key))
    if carid.status_code==400:
        print(("*"*5)+"Invalid Year selection"+("*"*5))
        exit()
    elif carid.status_code==404:
        print(("*"*5)+"Invalid car selection. Please check your spelling and try again"+("*"*5))
        exit()
    return carid.json()
#functions for horsepower and torque requests based on submodelid
def horsepower_request(requestid):
    engineid=requests.get("https://api.edmunds.com/api/vehicle/v2/styles/{}/engines?availability=standard&fmt=json&api_key=jhuddr2ar2x395x23fzr56mx".format(requestid))
    enginedata=engineid.json()
    try:
        horsepower=enginedata['engines'][0]['horsepower']
    except KeyError:
         print(("*"*5)+"Horsepower data is not avaliable for at least 1 of these models"+("*"*5))
         horsepower=0
    return horsepower

def torque_request(requestid):
    engineid=requests.get("https://api.edmunds.com/api/vehicle/v2/styles/{}/engines?availability=standard&fmt=json&api_key=jhuddr2ar2x395x23fzr56mx".format(requestid))
    enginedata=engineid.json()
    try:
        torque=enginedata['engines'][0]['torque']
    except KeyError:
        print(("*"*5)+"Torque data is not avaliable for at least one of these models"+("*"*5))
        torque=0
    return torque

#function to print submodels and create dictionary for user to pick from
def display_submodels():
    try:
        print("Please pick a sub model: ")
        x=0
        for submodel in  data['years'][0]['styles']:
            print(str(x) + ": " +data['years'][0]['styles'][x]['name'])
            submodel_dict[x]=data['years'][0]['styles'][x]['id']
            x+=1
    except IndexError:
        print(("*"*5)+"Model year data not avaliable yet. Try a different year."+("*"*5))
        exit()
def create_submodel_list():
    x=0
    #Create a list of dictionaries of various attributes of each submodel
    for submodel in data['years'][0]['styles']:
        hp=horsepower_request(data['years'][0]['styles'][x]['id'])
        tq=torque_request(data['years'][0]['styles'][x]['id'])
        submodel_list.append({'submodel': data['years'][0]['styles'][x]['name'],'id':data['years'][0]['styles'][x]['id'],'horsepower':hp,'torque':tq})
        x+=1
db = SqliteDatabase("submodel.db")
class Submodel(Model):
    name = CharField(max_length=200)
    car_id = IntegerField(default=0)
    horsepower= IntegerField(default=0)
    torque=IntegerField(default=0)
    #defining what database this model belongs to
    class Meta:
        database = db
def add_car():
    for submodel in submodel_list:
        Submodel.create(name=submodel['submodel'],car_id=submodel['id'], horsepower=submodel['horsepower'], torque=submodel['torque'])
###############################################################################
#Query user for their first car
print("What is your first car?")
car1_make=input("make: ")
car1_model=input("model: ")
car1_year=input("year: ")
data=carid_request(car1_make,car1_model,car1_year,key1)

#write output for car1 into car1.json. For debugging and viewing jason
with open('car1.json','w') as outfile:
    json.dump(data,outfile,sort_keys = True,indent = 4,ensure_ascii = False)


#prompt user to pick a submodel
submodel_dict={}
submodel_list=[]
display_submodels()
create_submodel_list()
selection1= int(input("Enter your selection number: "))
try:
    selection1_id=submodel_dict[selection1]
except KeyError:
    print("Selection invalid.")
    exit()

#create database to store this data
if __name__ == '__main__':
    try:
        os.remove("submodel.db") #clear old database file
    except FileNotFoundError:
        pass
    db.connect()
    db.create_tables([Submodel], safe=True)
    db.close()
    add_car()
#Find the horsepower and torque for this particular trim
for submodel in Submodel.select().where(Submodel.car_id==selection1_id):
    car1_hp=submodel.horsepower
    car1_tq=submodel.torque

#Query user for their second car
print("What is your second car?")
car2_make=input("make: ")
car2_model=input("model: ")
car2_year=input("year: ")
data=carid_request(car2_make,car2_model,car2_year,key1)

#Prompt user for second submodel
submodel_dict={}
submodel_list=[]
display_submodels()
create_submodel_list()
selection2= int(input("Enter your selection number: "))
try:
    selection2_id=submodel_dict[selection2]
except KeyError:
    print("Selection invalid.")
    exit()

#Check if cars are the same. If they are exit program
if selection1_id==selection2_id:
    print("Please choose a different car than your first choice")
    exit()

#Add to database
if __name__ == '__main__':
    db.create_tables([Submodel], safe=True)
    db.close()
    add_car()

for submodel in Submodel.select().where(Submodel.car_id==selection2_id):
    car2_hp=submodel.horsepower
    car2_tq=submodel.torque

#Compare both cars
if car1_hp>car2_hp:
    output="Car 1 has more horsepower "
elif car2_hp>car1_hp:
    output="Car 2 has more horsepower "
elif car1_hp==car2_hp:
    output="Both cars have the same horsepower "
if car1_hp==0:
    output= "There is no horsepower info for Car 1"
elif car2_hp==0:
    output= "There is no horsepower info for Car 2"
if car1_tq==0:
    output+= "and there is no horsepower info for Car 1"
elif car2_tq==0:
    output+= "and there is no horsepower info for Car 2"
elif car1_tq>car2_tq:
    output+="and Car 1 has more torque."
elif car2_tq>car1_tq:
    output+="and Car 2 has more torque."
elif car1_tq==car2_tq:
    output+="and both cars have the same torque."

print(output)
print("Car 1 has {} horsepower and {} torque.".format(car1_hp,car1_tq))
print("Car 2 has {} horsepower and {} torque.".format(car2_hp,car2_tq))


