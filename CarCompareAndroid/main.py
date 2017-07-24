from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.config import Config
import requests
import json
from peewee import *
import os
import sqlite3
key1="jhuddr2ar2x395x23fzr56mx"
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '500')
class Submodel(Model):
    name = CharField(max_length=200)
    car_id = IntegerField(default=0)
    horsepower= IntegerField(default=0)
    torque=IntegerField(default=0)
class Car(BoxLayout):
    def carid_request(self,car_make,car_model,car_year,key):
        carid=requests.get("https://api.edmunds.com/api/vehicle/v2/{}/{}?state=used&year={}&view=basic&fmt=json&api_key={}".format(car_make,car_model,car_year,key))
        if carid.status_code==400:
            self.ids.console_log.text=(("*"*5)+"Invalid Year selection"+("*"*5))
        elif carid.status_code==404:
            self.ids.console_log.text=(("*"*5)+"Invalid car selection. Please check your spelling and try again"+("*"*5))
        data=carid.json()
        return carid.json()
    #functions for horsepower and torque requests based on submodelid
    def horsepower_request(self,requestid):
        engineid=requests.get("https://api.edmunds.com/api/vehicle/v2/styles/{}/engines?availability=standard&fmt=json&api_key=jhuddr2ar2x395x23fzr56mx".format(requestid))
        enginedata=engineid.json()
        try:
            horsepower=enginedata['engines'][0]['horsepower']
        except KeyError:
             self.ids.console_log.text=(("*"*5)+"Horsepower data is not avaliable for at least 1 of these models"+("*"*5))
             horsepower=0
        return horsepower
    def torque_request(self,requestid):
        engineid=requests.get("https://api.edmunds.com/api/vehicle/v2/styles/{}/engines?availability=standard&fmt=json&api_key=jhuddr2ar2x395x23fzr56mx".format(requestid))
        enginedata=engineid.json()
        try:
            torque=enginedata['engines'][0]['torque']
        except KeyError:
            self.ids.console_log.text=(("*"*5)+"Torque data is not avaliable for at least one of these models"+("*"*5))
            torque=0
        return torque
    def display_submodels(self,data):
        submodel_dict={}
        submodel_display=""
        try:
            #self.console_lbl.text=("Please pick a sub model: ")
            x=0
            for submodel in  data['years'][0]['styles']:
                submodel_display+=(str(x) + ": " +data['years'][0]['styles'][x]['name']+"\n")
                submodel_dict[x]=data['years'][0]['styles'][x]['id']
                x+=1
            self.ids.console_log.text=submodel_display
        except IndexError:
            self.ids.console_log.text=(("*"*5)+"Model year data not avaliable yet. Try a different year."+("*"*5))
    def create_submodel_list(self,rawdata):
        data=rawdata
        submodel_list=[]
        x=0
        #Create a list of dictionaries of various attributes of each submodel
        for submodel in data['years'][0]['styles']:
            hp=self.horsepower_request(data['years'][0]['styles'][x]['id'])
            tq=self.torque_request(data['years'][0]['styles'][x]['id'])
            submodel_list.append({'submodel': data['years'][0]['styles'][x]['name'],'id':data['years'][0]['styles'][x]['id'],'horsepower':hp,'torque':tq})
            x+=1
        return submodel_list

    def add_car(self,submodel_list):
        for submodel in submodel_list:
            Submodel.create(name=submodel['submodel'],car_id=submodel['id'], horsepower=submodel['horsepower'], torque=submodel['torque'])

    def cartrim1_select(self,btn,carid_request,car_make,car_model,car_year):
        key1="jhuddr2ar2x395x23fzr56mx"
        data1=self.carid_request(self.ids.car1make.text,self.ids.car1model.text,self.ids.car1year.text,key1)
        self.display_submodels(data1)

    def cartrim2_select(self,btn,carid_request,car_make,car_model,car_year):
        key1="jhuddr2ar2x395x23fzr56mx"
        data2=self.carid_request(self.ids.car2make.text,self.ids.car2model.text,self.ids.car2year.text,key1)
        self.display_submodels(data2)

    def compare_cars(self,btn,horsepower_request,torque_request,add_car):
        try:
            #requesting again b/c cant get data from othe functions for now...
            data1=self.carid_request(self.ids.car1make.text,self.ids.car1model.text,self.ids.car1year.text,key1)
            data2=self.carid_request(self.ids.car2make.text,self.ids.car2model.text,self.ids.car2year.text,key1)
            car1_list=self.create_submodel_list(data1)
            car2_list=self.create_submodel_list(data2)

            db = SqliteDatabase("submodel.db")
            database = db
            #create database to store this data
            if __name__ == '__main__':
                try:
                    os.remove("submodel.db") #clear old database file
                except FileNotFoundError:
                    pass
                db.connect()
                db.create_tables([Submodel], safe=True)
                db.close()
                self.add_car(car1_list)
                self.add_car(car2_list)

            #Get selection from the selection inputs
            selection1_userinput=int(self.ids.car1select.text)
            selection2_userinput=int(self.ids.car2select.text)
            submodel1_dict={}
            submodel2_dict={}
            x=0
            for submodel in  data1['years'][0]['styles']:
                submodel1_dict[x]=data1['years'][0]['styles'][x]['id']
                x+=1
            x=0
            for submodel in  data2['years'][0]['styles']:
                submodel2_dict[x]=data2['years'][0]['styles'][x]['id']
                x+=1

            selection1_id=submodel1_dict[selection1_userinput]
            selection2_id=submodel2_dict[selection2_userinput]

            for submodel in Submodel.select().where(Submodel.car_id==selection1_id):
                car1_hp=submodel.horsepower
                car1_tq=submodel.torque
            for submodel in Submodel.select().where(Submodel.car_id==selection2_id):
                car2_hp=submodel.horsepower
                car2_tq=submodel.torque

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

            if selection1_id==selection2_id:
                final_output="Please choose a different car than your first choice"
            else:
                final_output=output+("\nCar 1 has {} horsepower and {} torque.".format(car1_hp,car1_tq))+("\nCar 2 has {} horsepower and {} torque.".format(car2_hp,car2_tq))
            
            self.ids.console_log.text=final_output
        except ValueError:
            self.ids.console_log.text="Please input a trim selection before proceeding"


class CarCompare(App):
    def build(self):
        return Car()

if __name__ == "__main__":
    CarCompare().run()