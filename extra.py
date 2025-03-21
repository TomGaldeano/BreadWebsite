import logging
import datetime
from config import Data
import json
data = Data()

class Log(object):
    def __init__(self, name, file):
        login_ch = logging.FileHandler(file)
        login_ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        login_ch.setFormatter(formatter)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(login_ch)

    def warn(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

class ReVerify(object):
    def __init__(self, logger):
        self.logger = logger
        self.invalid_values = data.invalid_characters

    def verify_string(self, string):
        string = str(string)
        for letter in string:
            if letter in self.invalid_values:
                self.logger.error("error in string")
                return False
        return True

    def verify_int(self, integer, minimum, maximum):
        """
        verifies if iteger is an integer and within minimum and maximum
        """
        try:
            value = int(integer)
            if not (minimum <= value <= maximum):
                self.logger.error(f"invalid integer in loaf form -->{value}")
                return False
            else:
                return True
        except ValueError:
            self.logger.error("non integer in loaf form")
            return False


class OrderViewer(object):
    def __init__(self, order, lang):
        if lang == "en":
            self.en = True
            self.es = False
            self.message = "Your Order"
        elif lang == "es":
            self.en = False
            self.es = True
            self.message = "Tu pedido:"
            self.tipos_pan = data.tipos_pan
        self.order = order
        self.is_form = False

    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        """
        iterator method to show the orders of bread in the sql request self.order
        """
        if self.a < min([20, len(self.order)]):
            b = 1
            self.price = 0
            self.current_order = json.loads(self.order[self.a].order)
            self.date = self.order[self.a].date
            self.order_instance = self.order[self.a]
            self.time_day = self.order[self.a].time_day
            d = self.date.split("-")
            self.date = datetime.date(int(d[0]),int(d[1]),int(d[2])).strftime('%d/%m/%y')
            if self.es:
                if self.time_day == "Morning":
                    self.time_day = "Mañana"
                elif self.time_day == "Evening":
                    self.time_day = "Tarde"
            self.message = ""
            self.customer = self.order[self.a].client
            for bread in self.current_order.keys():
                if self.current_order[bread] == 1:
                    if self.en:
                        self.message += f" 1 {bread.replace('_', ' ')},"
                    elif self.es:
                        self.message += f" 1 {data.tipos_pan[bread]},"
                    self.price += data.prices[bread]
                elif self.current_order[bread] > 1:
                    if self.en:
                        if bread[-1] == "k":
                            self.message += f" {self.current_order[bread]} {bread.replace('_', ' ')}s,"
                        elif bread[-1] == "f":
                            self.message += f" {self.current_order[bread]} {bread.replace('_', ' ')[:-1]}ves,"
                    elif self.es:
                        self.message += f" {self.current_order[bread]} {data.tipos_pan[bread].replace('a d','as d')},"
                    self.price += self.current_order[bread]*data.prices[bread]
                b += 1
                if self.is_form:
                    values = [name for name in self.form.__dict__.keys() if name.startswith("field_")]
                    self.form_data = eval(f"self.form.{values[self.a]}")
            self.a += 1
            try:
                if self.message[-1] == ",":
                    self.message = self.message[:-1]
            except IndexError:
                return self.a
            return self.a
        else:
            raise StopIteration

    def add_form(self, form):
        self.is_form = True
        self.form = form

    def simple_view(self):
        self.simple_order = {"White_loaf": 0,
              "Seeds_loaf": 0,
              "Walnut_loaf": 0,
              "Walnut_and_Sultanas_loaf": 0,
              "Pistacho_loaf": 0,
              "Wholemeal_Spelt_loaf": 0,
              "Wholemeal_White_loaf": 0,
              "Wholemeal_Seeds_loaf": 0,
              "Wholemeal_Walnut_loaf": 0,
              "Wholemeal_Walnut_and_Sultanas_loaf": 0,
              "Wholemeal_Pistacho_loaf": 0,
              "White_stick": 0,
              "Seeds_stick": 0,
              "Walnut_stick": 0,
              "Walnut_and_Sultanas_stick": 0,
              "Pistacho_stick": 0,
              "Wholemeal_Spelt_stick": 0,
              "Wholemeal_White_stick": 0,
              "Wholemeal_Seeds_stick": 0,
              "Wholemeal_Walnut_stick": 0,
              "Wholemeal_Walnut_and_Sultanas_stick": 0,
              "Wholemeal_Pistacho_stick": 0}
        for i in self.order:
            num_breads = json.loads(i.order)
            for j in self.simple_order.keys():
                self.simple_order[j] += num_breads[j]



class Statistic_generator(object):
    def __init__(self, previous, current):
        costs = data.costs
        self.num_breads = {"White_loaf": 0,
              "Seeds_loaf": 0,
              "Walnut_loaf": 0,
              "Walnut_and_Sultanas_loaf": 0,
              "Pistacho_loaf": 0,
              "Wholemeal_Spelt_loaf": 0,
              "Wholemeal_White_loaf": 0,
              "Wholemeal_Seeds_loaf": 0,
              "Wholemeal_Walnut_loaf": 0,
              "Wholemeal_Walnut_and_Sultanas_loaf": 0,
              "Wholemeal_Pistacho_loaf": 0,
              "White_stick": 0,
              "Seeds_stick": 0,
              "Walnut_stick": 0,
              "Walnut_and_Sultanas_stick": 0,
              "Pistacho_stick": 0,
              "Wholemeal_Spelt_stick": 0,
              "Wholemeal_White_stick": 0,
              "Wholemeal_Seeds_stick": 0,
              "Wholemeal_Walnut_stick": 0,
              "Wholemeal_Walnut_and_Sultanas_stick": 0,
              "Wholemeal_Pistacho_stick": 0}
        self.past_month = {"gross":0,"costs":0,"benefit":0,"loaves":0,"sticks":0}
        self.present_month = {"gross":0,"costs":0,"benefit":0,"loaves":0,"sticks":0}
        try:
            for i in list(previous):
                order = json.loads(i[0])
                for j in order.keys():
                    self.num_breads[j] += order[j]
                    self.past_month["gross"] += order[j]*costs[j]["price"]
                    self.past_month["costs"] += order[j]*costs[j]["cost"]
                    self.past_month["benefit"] += order[j]*costs[j]["benefits"]
                    if j[-1] == "k":
                        self.past_month["sticks"] += order[j]
                    elif j[-1] == "f":
                        self.past_month["loaves"] += order[j]
        except:
            pass
        try:
            for i in list(current):
                order = json.loads(i[0])
                for j in order.keys():
                    self.present_month["gross"] += order[j]*costs[j]["price"]
                    self.present_month["costs"] += order[j]*costs[j]["cost"]
                    self.present_month["benefit"] += order[j]*costs[j]["benefits"]
                    if j[-1] == "k":
                        self.present_month["sticks"] += order[j]
                    elif j[-1] == "f":
                        self.present_month["loaves"] += order[j]
        except:
            pass


    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        """
        iterator method to show the orders of bread in the sql request self.order
        """
        if self.a < min([10, len(self.order)]):
            values = [name for name in self.form.__dict__.keys() if name.startswith("field_")] + ["submit"]
            b = 1
            self.price = 0
            self.current_order = json.loads(self.order[self.a].order)
            self.date = self.order[self.a].date
            self.order_instance = self.order[self.a]
            self.time_day = self.order[self.a].time_day
            d = self.date.split("-")
            self.date = datetime.date(int(d[0]),int(d[1]),int(d[2])).strftime('%d/%m/%y')
            if self.es:
                if self.time_day == "Morning":
                    self.time_day = "Mañana"
                elif self.time_day == "Evening":
                    self.time_day = "Tarde"
            self.message = ""
            self.customer = self.order[self.a].client
            for bread in self.current_order.keys():
                if self.current_order[bread] == 1:
                    if self.en:
                        self.message += f" 1 {bread.replace('_', ' ')},"
                    elif self.es:
                        self.message += f" 1 {data.tipos_pan[bread]},"
                    self.price += data.prices[bread]
                elif self.current_order[bread] > 1:
                    if self.en:
                        if bread[-1] == "k":
                            self.message += f" {self.current_order[bread]} {bread.replace('_', ' ')}s,"
                        elif bread[-1] == "f":
                            self.message += f" {self.current_order[bread]} {bread.replace('_', ' ')[:-1]}ves,"
                    elif self.es:
                        self.message += f" {self.current_order[bread]} {data.tipos_pan[bread].replace('a d','as d')},"
                    self.price += self.current_order[bread]*data.prices[bread]
                b += 1
                if self.is_form:

                    self.form_data = eval(f"self.form.{values[self.a]}")
            self.a += 1
            try:
                if self.message[-1] == ",":
                    self.message = self.message[:-1]
            except IndexError:
                return self.a
            return self.a
        else:
            raise StopIteration

def valid_day(date, lang):
    """
    Checks if the date is valid to order bread
    Returns None if valid and a message in the correct language if not
    """
    days = [4, 5, 6]
    data = date.weekday()
    if data in days:
        if lang == "en":
            return "Current day is   not valid"
        elif lang == "es":
            return "Dia Invalido"
    else:
        return

def valid_period(date, period, lang):
    """
    Returns None if no issue and error string depending on period and date in the correct language
    """
    date = date.weekday()
    if date in [0, 1, 2, 3] and period == "Morning":
        if lang == "en":
            return "No bread in the Morning on this day"
        elif lang == "es":
            return "No hay pan por la mañana este dia"

