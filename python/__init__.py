from typing import Dict
import mysql.connector
from abc import ABC
from pysamp.dialog import Dialog
from pysamp.player import Player
from pysamp import(
    set_timer,
    get_player_name,
    send_client_message_to_all,
)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="123",
  database="omp_server_python_project"
)
mycursor = mydb.cursor()

"""Alojamiento de datos útiles del jugador"""

users_dictionary: Dict[int, dict] = {}

"""Funciones"""
def timer_user_leaves_function(playerid: Player):
    playerid.kick()

"""Clases"""

class KickAndBanSettings(Player):
    def __init__(self, playerid, reason, user_name, admin_name):
        super().__init__(playerid)
        self.reason = reason
        self.user_name = user_name
        self.admin_name = admin_name

    @staticmethod
    def user_leaves():
        set_timer(timer_user_leaves_function, 1000, False)

class Kick(KickAndBanSettings):
    def __init__(self, playerid, reason, user_name, admin_name):
        super().__init__(playerid, reason, user_name, admin_name)

    def text(self):
        if self.admin_name.lower() == "server":
            send_client_message_to_all(-1, f"El server ha expulsado a {self.user_name}. Razón: {self.reason}")
        else:
            send_client_message_to_all(-1, f"Admin {self.admin_name} ha expulsado a {self.user_name}. Razón: {self.reason}")
        
        return super().user_leaves()

class Ban(KickAndBanSettings):
    def __init__(self, playerid, reason, user_name, admin_name):
        super().__init__(playerid, reason, user_name, admin_name)

    def text(self):
        if self.admin_name.lower() == "server":
            send_client_message_to_all(-1, f"El server ha baneado a {self.user_name}. Razón: {self.reason}")
        else:
            send_client_message_to_all(-1, f"Admin {self.admin_name} ha baneado a {self.user_name}. Razón: {self.reason}")
        
        return super().user_leaves()


def response_register_dialog(playerid: Player, response, input_text):
    if response:
        user_id = playerid.get_id()

        sql = f"INSERT INTO users (name, password) VALUES ({users_dictionary[user_id].get("user_name")}, {input_text})"
        mycursor.execute(sql)
        mydb.commit()

        send_client_message_to_all(-1, f"¡{users_dictionary[user_id].get("user_name")} se registró en el servidor!")

        users_dictionary[user_id] = mycursor.lastrowid
    else: playerid.kick()







def response_login_dialog(playerid: Player, response, input_text):
    if response:
        sql = f"SELECT password WHERE password = {input_text}"
        
        mycursor.execute(sql)
        myresult = mycursor.fetchone()

        if myresult == None: playerid.kick()
        else: send_client_message_to_all(-1, f"Denle nuevamente la bienvenida a {get_player_name(playerid.get_id())}!")
    else: playerid.kick()





"""Llamadas a eventos que ocurren dentro del servidor"""

@Player.on_connect
def player_connects(playerid: Player):
    playerid.toggle_spectating(True)

    user_id = playerid.get_id()
    users_dictionary[user_id]["user_name"] = get_player_name(user_id)

    sql = f"SELECT id FROM users WHERE name = {users_dictionary[user_id].get("user_name")}"

    mycursor.execute(sql)
    myresult = mycursor.fetchone()

    if myresult == None: Dialog.create(1, "Registrarse", "{FFFFFF}" + f"Hola {users_dictionary[user_id].get("user_name")}, ingresa una contraseña para registrarte.", "Continuar", "Salir", response_register_dialog)
    else: 
        Dialog.create(1, "Iniciar sesión", "{FFFFFF}" + f"Hola {users_dictionary[user_id].get("user_name")}, ingresa tu contraseña para iniciar sesión", "Continuar", "Salir", response_login_dialog)
        
        users_dictionary[user_id]["user_db_id"] = myresult

    Dialog.show(playerid)

@Player.on_disconnect
def player_disconnects(playerid: Player):
    if users_dictionary.get(playerid) != None:
        users_dictionary.pop(playerid, None)