import mysql.connector
from pysamp.dialog import Dialog
from pysamp.player import Player
from pysamp import(
    set_timer,
    get_pvar_int,
    set_pvar_int,
    get_player_name,
    send_client_message,
    send_client_message_to_all,
)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="123",
  database="omp_server_python_project")

mycursor = mydb.cursor()

"""Funciones"""

def timer_user_leaves_function(playerid: Player):
    playerid.kick()

"""Funciones asociadas a una interfaz gráfica en la cual el usuario interactua"""

def dialog(playerid: Player, response, list_item, input_text):
    user_id = playerid.get_id()
    user_name = get_player_name(user_id)
    db_user_id = get_pvar_int(user_id, "db_user_id")
    
    def register_the_user():
        if input_text.isspace() or not(input_text): register_dialog.show(playerid)
        else:
            sql_register = "INSERT INTO users (name, password) VALUES (%s, %s)"
            val = [user_name, input_text]

            mycursor.execute(sql_register, val)
            mydb.commit()

            playerid.set_pvar_int("db_user_id", mycursor.lastrowid)

            send_client_message_to_all(-1, "¡{00FF00}" + f"{user_name} " + "{FFFFFF}" + "se registró en el servidor!")

    def check_the_password():
        if input_text.isspace() or not(input_text): login_dialog.show(playerid)

        sql_login = "SELECT password FROM users WHERE id = %s"
        val = [db_user_id, ]

        mycursor.execute(sql_login, val)
        myresult = mycursor.fetchone()

        if myresult[0] != input_text:
            send_client_message(user_id, -1, "Has puesto una contraseña incorrecta. Has sido expulsado")
            return False
        else: send_client_message_to_all(-1, "¡Denle la bienvenida nuevamente a " + "{00FF00}" + f"{user_name}" + "{FFFFFF}" + "!")

    if response and db_user_id == -1: register_the_user()
    elif check_the_password() == False or response == 0: playerid.kick()

"""Llamadas a eventos que ocurren dentro del servidor"""

@Player.on_connect
def player_connects(playerid: Player):
    playerid.toggle_spectating(True)
    
    user_id = playerid.get_id()
    user_name = get_player_name(user_id)   

    sql = "SELECT id FROM users WHERE name = %s"
    val = [user_name,]

    mycursor.execute(sql, val)
    myresult = mycursor.fetchone()

    global register_dialog
    global login_dialog
    
    register_dialog = Dialog.create(1, "Registrarse", "{FFFFFF}" + f"Hola {user_name}, ingresa una contraseña para registrarte.", "Continuar", "Salir", dialog)
    login_dialog = Dialog.create(1, "Iniciar sesión", "{FFFFFF}" + f"Hola {user_name}, ingresa tu contraseña para iniciar sesión", "Continuar", "Salir", dialog)

    if myresult == None: 
        register_dialog.show(playerid)
        set_pvar_int(user_id, "db_user_id", -1)
    else: 
        login_dialog.show(playerid)
        set_pvar_int(user_id, "db_user_id", myresult[0])
