import requests
import json
from peewee import *
import os
import sqlite3
key1="jhuddr2ar2x395x23fzr56mx"
import kivy

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.uix.popup import Popup  
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '500')
###############################################################################
#function to request car id
###############################################################################
def carid_request(car_make,car_model,car_year,key):
    carid=requests.get("https://api.edmunds.com/api/vehicle/v2/{}/{}?state=used&year={}&view=basic&fmt=json&api_key={}".format(car_make,car_model,car_year,key))
    if carid.status_code==400:
        self.console_lbl.text=(("*"*5)+"Invalid Year selection"+("*"*5))
        exit()
    elif carid.status_code==404:
        self.console_lbl.text=(("*"*5)+"Invalid car selection. Please check your spelling and try again"+("*"*5))
        exit()
    data=carid.json()
    return carid.json()
#functions for horsepower and torque requests based on submodelid
def horsepower_request(requestid):
    engineid=requests.get("https://api.edmunds.com/api/vehicle/v2/styles/{}/engines?availability=standard&fmt=json&api_key=jhuddr2ar2x395x23fzr56mx".format(requestid))
    enginedata=engineid.json()
    try:
        horsepower=enginedata['engines'][0]['horsepower']
    except KeyError:
         self.console_lbl.text=(("*"*5)+"Horsepower data is not avaliable for at least 1 of these models"+("*"*5))
         horsepower=0
    return horsepower

def torque_request(requestid):
    engineid=requests.get("https://api.edmunds.com/api/vehicle/v2/styles/{}/engines?availability=standard&fmt=json&api_key=jhuddr2ar2x395x23fzr56mx".format(requestid))
    enginedata=engineid.json()
    try:
        torque=enginedata['engines'][0]['torque']
    except KeyError:
        self.console_lbl.text=(("*"*5)+"Torque data is not avaliable for at least one of these models"+("*"*5))
        torque=0
    return torque

#function to print submodels and create dictionary for user to pick from
def display_submodels(car_make,car_model,car_year,key):
    data=carid_request(car_make,car_model,car_year,key)
    try:
        #self.console_lbl.text=("Please pick a sub model: ")
        x=0
        for submodel in  data['years'][0]['styles']:
            submodel_display=(str(x) + ": " +data['years'][0]['styles'][x]['name'])
            submodel_dict[x]=data['years'][0]['styles'][x]['id']
            x+=1
        self.console_lbl.text=submodel_display
        print(submodel_dict[1])
    except IndexError:
        self.console_lbl.text=(("*"*5)+"Model year data not avaliable yet. Try a different year."+("*"*5))
        exit()
def create_submodel_list():
    x=0
    #Create a list of dictionaries of various attributes of each submodel
    for submodel in data['years'][0]['styles']:
        hp=horsepower_request(data['years'][0]['styles'][x]['id'])
        tq=torque_request(data['years'][0]['styles'][x]['id'])
        submodel_list.append({'submodel': data['years'][0]['styles'][x]['name'],'id':data['years'][0]['styles'][x]['id'],'horsepower':hp,'torque':tq})
        x+=1


def add_car():
    for submodel in submodel_list:
        Submodel.create(name=submodel['submodel'],car_id=submodel['id'], horsepower=submodel['horsepower'], torque=submodel['torque'])
class Submodel(Model):
    name = CharField(max_length=200)
    car_id = IntegerField(default=0)
    horsepower= IntegerField(default=0)
    torque=IntegerField(default=0)
    #defining what database this model belongs to
class Meta:
    db = SqliteDatabase("submodel.db")
    database = db

class MyApp(App):
    
    
    # layout
    def build(self):
        self.car1make_txt=TextInput(text="Audi")
        self.car1model_txt=TextInput(text="q5")
        self.car1year_txt=TextInput(text="2012")
        self.car1select_txt=TextInput()
        self.car2make_txt=TextInput(text="Audi")
        self.car2model_txt=TextInput(text="q5")
        self.car2year_txt=TextInput(text="2013")
        self.car2select_txt=TextInput()

        #layout = GridLayout(cols=4, rows =6,row_force_default=True, row_default_height=40)
        #grid layouts in separate box layouts. multiple buttons
        grid1 = GridLayout(cols=4, rows =1,row_force_default=True, row_default_height=40)
        grid2 = GridLayout(cols=4, rows =1,row_force_default=True, row_default_height=40)
        grid3 = GridLayout(cols=4, rows =1,row_force_default=True, row_default_height=40)
        grid4 = GridLayout(cols=4, rows =1,row_force_default=True, row_default_height=40)
        grid5 = GridLayout(cols=4, rows =1,row_force_default=True, row_default_height=80)
        grid6 = GridLayout(cols=4, rows =1,row_force_default=True, row_default_height=80)

        grid1.add_widget(Label(text='Car 1 Make:'))
        grid1.add_widget(self.car1make_txt)
        grid1.add_widget(Label(text='Car 2 Make:'))
        grid1.add_widget(self.car2make_txt)

        grid2.add_widget(Label(text='Car 1 Model:'))
        grid2.add_widget(self.car1model_txt)
        grid2.add_widget(Label(text='Car 2 Model:'))
        grid2.add_widget(self.car2model_txt)

        grid3.add_widget(Label(text='Car 1 Year:'))
        grid3.add_widget(self.car1year_txt)
        grid3.add_widget(Label(text='Car 2 Year:'))
        grid3.add_widget(self.car2year_txt)

        car1_btn=Button(text="Pick trim")
        car1_btn.bind(on_press=self.car1select)
        grid4.add_widget(car1_btn)
        grid4.add_widget(self.car1select_txt)
        car2_btn=Button(text="Pick trim")
        car2_btn.bind(on_press=self.car1select)
        grid4.add_widget(car2_btn)
        grid4.add_widget(self.car2select_txt)


        btn1 = Button(text="Compare")
        btn1.bind(on_press=self.buttonClicked)
        grid5.add_widget(btn1)
        self.console_lbl= Label(text="")
        grid6.add_widget(self.console_lbl)

        layout=BoxLayout(orientation='vertical')
        layout.add_widget(grid1)
        layout.add_widget(grid2)
        layout.add_widget(grid3)
        layout.add_widget(grid4)
        layout.add_widget(grid5)
        layout.add_widget(grid6)
        return layout
    def car1select(self,btn):
        display_submodels()
        self.console_lbl.text=submodel_display

    def buttonClicked(self,btn):
        
        #printedoutput=comparisonapp(self.car1make_txt.text,self.car1model_txt.text,self.car1year_txt.text,self.car2make_txt.text,self.car2model_txt.text,self.car2year_txt.text)


        car1_make=self.car1make_txt.text
        car1_model=self.car1model_txt.text
        car1_year=self.car1year_txt.text
        data=carid_request(car1_make,car1_model,car1_year,key1)
        db = SqliteDatabase("submodel.db")
        database = db
        #write output for car1 into car1.json. For debugging and viewing jason
        with open('car1.json','w') as outfile:
            json.dump(data,outfile,sort_keys = True,indent = 4,ensure_ascii = False)


        #prompt user to pick a submodel
        submodel_dict={}
        submodel_list=[]

        display_submodels(car1_make,car1_model,car1_year,key1)
        create_submodel_list()
        selection1= int(input("Enter your selection number: "))
        try:
            selection1_id=submodel_dict[selection1]
        except KeyError:
            print("Selection invalid.")
            exit()

        #create database to store this data
        if __name__ == '__main__':
            os.remove("submodel.db") #clear old database file
            db.connect()
            db.create_tables([Submodel], safe=True)
            db.close()
            add_car()
        #Find the horsepower and torque for this particular trim
        for submodel in Submodel.select().where(Submodel.car_id==selection1_id):
            car1_hp=submodel.horsepower
            car1_tq=submodel.torque

        #Query user for their second car
        car2_make=self.car2make_txt.text
        car2_model=self.car2model_txt.text
        car2_year=self.car2year_txt.text
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

        final_output=output+("\nCar 1 has {} horsepower and {} torque.".format(car1_hp,car1_tq))+("\nCar 2 has {} horsepower and {} torque.".format(car2_hp,car2_tq))

        printed_output=final_output
        self.console_lbl.text = printed_output
        '''
        self.output_popup=Popup(title="Faster Car", content="test",size_hint=(.75,.75))
        self.output_popup.open()
        '''



# run app
if __name__ == "__main__":
    MyApp().run()

