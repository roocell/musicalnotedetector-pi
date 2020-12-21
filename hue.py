# for phillips hue
import requests
import json

# https://developers.meethue.com/develop/get-started-2/
# https://192.168.1.102/debug/clip.html

# url
# /api/ze2dqsTNbtu5dF94FevyWtjHbM3Ax9Elrb4-tVTa/lights/1/state
# body
# {"on":true, "sat":254, "bri":254,"hue":10000}

# Phillips Hue control
hue_ip="192.168.1.102"
hue_user = "ze2dqsTNbtu5dF94FevyWtjHbM3Ax9Elrb4-tVTa"

lamp1_id = "3"
lamp2_id = "5"
lamp3_id = "6"
lamp4_id = "7"
lamp_outside_id = "4"

green = 21845
red = 0
blue = 43690
yellow = 10000
white = 8000

def lightSet (id, bri, colour):
  global hue_ip, hue_user
  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id+"/state"
  #print(hue_state_url)
  blue = {"on":True, "sat":229, "bri":bri,"hue":colour}
  r = requests.put(hue_state_url, json.dumps(blue), timeout=5)
  #print(r.json())

def lightSetWithBreathe (id, bri, colour):
  global hue_ip, hue_user
  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id+"/state"
  #print(hue_state_url)
  blue = {"on":True, "sat":229, "bri":bri,"hue":colour,  "alert":"select"}
  r = requests.put(hue_state_url, json.dumps(blue), timeout=5)
  #print(r.json())

def lightAlert(id, bri, colour):
  global hue_ip, hue_user
  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id+"/state"
  #print(hue_state_url)
  blue = {"on":True, "sat":229, "bri":bri,"hue":colour, "alert":"lselect"}
  r = requests.put(hue_state_url, json.dumps(blue), timeout=5)
  #print(r.json())

def lightOff (id):
  global hue_ip, hue_user
  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id+"/state"
  data_off = {"on":False}
  r = requests.put(hue_state_url, json.dumps(data_off), timeout=5)
  #print(r.json())

def lightOn (id):
  global hue_ip, hue_user
  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id+"/state"
  data_off = {"on":True}
  r = requests.put(hue_state_url, json.dumps(data_off), timeout=5)
  #print(r.json())

def lightToggle (id):
  global hue_ip, hue_user
  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id
  r = requests.get(hue_state_url, timeout=5)
  #print(r.json()["state"]["on"])
  data = {"on": True}
  if r.json()["state"]["on"] == True:
    data = {"on": False}

  hue_state_url = "http://"+hue_ip+"/api/"+hue_user+"/lights/"+id+"/state"
  r = requests.put(hue_state_url, json.dumps(data), timeout=5)
  #print(r.json())
