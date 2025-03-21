import os


class Data(object):
    invalid_characters = ["<", ">", "'", '"', "#", "%", "_", ";", "~"]
    bread_types = ["White_loaf","Seeds_loaf","Walnut_loaf","Walnut_and_Sultanas_loaf","Pistacho_loaf","Wholemeal_Spelt_loaf","Wholemeal_White_loaf",
              "Wholemeal_Seeds_loaf","Wholemeal_Walnut_loaf","Wholemeal_Walnut_and_Sultanas_loaf","Wholemeal_Pistacho_loaf","White_stick","Seeds_stick",
              "Walnut_stick","Walnut_and_Sultanas_stick","Pistacho_stick","Wholemeal_Spelt_stick",
              "Wholemeal_White_stick","Wholemeal_Seeds_stick","Wholemeal_Walnut_stick","Wholemeal_Walnut_and_Sultanas_stick","Wholemeal_Pistacho_stick"]
 
    tipos_pan = {"White_loaf": "Hogaza de Pan Blanco",
              "Seeds_loaf": "Hogaza de Pan de Semillas",
              "Walnut_loaf": "Hogaza de Pan de Nueces",
              "Walnut_and_Sultanas_loaf": "Hogaza de Nueces y Pasas",
              "Pistacho_loaf": "Hogaza de Pan de Pistachos",
              "Wholemeal_Spelt_loaf": "Hogaza de Pan Integral de Centeno>",
              "Wholemeal_White_loaf": "Hogaza de Pan Blanco Integral",
              "Wholemeal_Seeds_loaf": "Hogaza de Pan Integral de Semillas",
              "Wholemeal_Walnut_loaf": "Hogaza de Pan Integrales de Nueces",
              "Wholemeal_Walnut_and_Sultanas_loaf": "Hogaza de Pan Integral de Nueces y Pasas",
              "Wholemeal_Pistacho_loaf": "Hogaza de Pan de Pistachos",  
              "White_stick": "Barra de Pan Blanco",
              "Seeds_stick": "Barra de Pan de Semillas",
              "Walnut_stick": "Barra de Pan de Nueces",
              "Walnut_and_Sultanas_stick": "Barra de Pan de Nueces y Pasas",
              "Pistacho_stick": "Barra de Pan de Pistachos",
              "Wholemeal_Spelt_stick": "Barra de Pan Integral de Espelta",
              "Wholemeal_White_stick": "Barra de Pan Blanco Integral",
              "Wholemeal_Seeds_stick": "Barra de Pan Blanco",
              "Wholemeal_Walnut_stick": "Barra de Pan Blanco",
              "Wholemeal_Walnut_and_Sultanas_stick": "Barra de Pan Blanco",
              "Wholemeal_Pistacho_stick": "Barra de Pan de Pistachos"}
    prices = {"White_loaf": 3,
              "Seeds_loaf": 3,
              "Walnut_loaf": 4,
              "Walnut_and_Sultanas_loaf": 4,
              "Pistacho_loaf": 4.5,
              "Wholemeal_Spelt_loaf": 4,
              "Wholemeal_White_loaf": 4,
              "Wholemeal_Seeds_loaf": 4,
              "Wholemeal_Walnut_loaf": 4,
              "Wholemeal_Walnut_and_Sultanas_loaf": 4,
              "Wholemeal_Pistacho_loaf": 5,
              "White_stick": 2,
              "Seeds_stick": 2,
              "Walnut_stick": 2.5,
              "Walnut_and_Sultanas_stick": 2.5,
              "Pistacho_stick": 3,
              "Wholemeal_Spelt_stick": 2.5,
              "Wholemeal_White_stick": 2.5,
              "Wholemeal_Seeds_stick": 2.5,
              "Wholemeal_Walnut_stick": 2.5,
              "Wholemeal_Walnut_and_Sultanas_stick": 2.5,
              "Wholemeal_Pistacho_stick": 3}
    costs = {
    "White_stick": {
        "benefits": 1.565,
        "cost": 0.435,
        "price": 2},
    "White_loaf": {
        "benefits": 2.24,
        "cost": 0.76,
        "price": 3},
    "Wholemeal_Spelt_stick": {
        "benefits": 1.89625,
        "cost": 0.60375,
        "price": 2.5},
    "Wholemeal_Spelt_loaf": {
        "benefits": 2.8899999999999997,
        "cost": 1.11,
        "price": 4},
    "Wholemeal_White_stick": {
        "benefits": 2.01225,
        "cost": 0.48775,
        "price": 2.5},
    "Wholemeal_White_loaf": {
        "benefits": 3.122,
        "cost": 0.8780000000000001,
        "price": 4},
    "Wholemeal_Seeds_stick": {
        "benefits": 1.91425,
        "cost": 0.58575,
        "price": 2.5},
    "Wholemeal_Seeds_loaf": {
        "benefits": 2.742,
        "cost": 1.2580000000000002,
        "price": 4},
    "Walnut_stick": {
        "benefits": 1.4462499999999998,
        "cost": 1.0537500000000002,
        "price": 2.5},
    "Walnut_loaf": {
        "benefits": 2.0024999999999995,
        "cost": 1.9975000000000003,
        "price": 4},
    "Wholemeal_Walnut_stick": {
        "benefits": 1.42925,
        "cost": 1.07075,
        "price": 2.5},
    "Wholemeal_Walnut_loaf": {
        "benefits": 1.956,
        "cost": 2.044,
        "price": 4},
    "Walnut_and_Sultanas_stick": {
        "benefits": 1.576,
        "cost": 0.9239999999999999,
        "price": 2.5},
    "Walnut_and_Sultanas_loaf": {
        "benefits": 2.262,
        "cost": 1.738,
        "price": 4},
    "Wholemeal_Walnut_and_Sultanas_stick": {
        "benefits": 1.16425,
        "cost": 1.33575,
        "price": 2.5},
    "Wholemeal_Walnut_and_Sultanas_loaf": {
        "benefits": 2.366,
        "cost": 1.634,
        "price": 4},
    "Pistacho_stick": {
        "benefits": 1.3624999999999998,
        "cost": 1.6375000000000002,
        "price": 3},
    "Pistacho_loaf": {
        "benefits": 1.8725,
        "cost": 2.6275,
        "price": 4.5},
    "Wholemeal_Pistacho_stick": {
        "benefits": 1.6017499999999998,
        "cost": 1.3982500000000002,
        "price": 3},
    "Wholemeal_Pistacho_loaf": {
        "benefits": 2.4385,
        "cost": 2.5615,
        "price": 5},
    "Seeds_stick": {
        "benefits": 1.2474999999999998,
        "cost": 0.7525000000000002,
        "price": 2},
    "Seeds_loaf": {
        "benefits": 1.9849999999999999,
        "cost": 1.0150000000000001,
        "price": 3}}

class SecretData(object):
    secret_key = os.getenv('SECRET_KEY_FlASK')


if __name__ == "__main__":
    data = SecretData()