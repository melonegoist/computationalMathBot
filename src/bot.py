import telebot
from telebot import types
import json
import sys
import re
import os
from .scripts.lab1 import find_system_of_linear_equations_roots
from .scripts.lab2 import bisection_method, secant_method, simple_iteration_method, newton_method
from .scripts.lab3 import calculate_integral
from .scripts.tools import plot_function_with_highlight
from lib.integratedAITools import ai_tools
from random import randint



#------paths-----------------
src_dir = os.path.dirname(__file__)


conf_dir = os.path.abspath(os.path.join(src_dir, "..", "conf"))

config_json_path = os.path.abspath(os.path.join(conf_dir, "config.json"))
messages_json_path = os.path.abspath(os.path.join(conf_dir, "messages.json"))
regex_json_path = os.path.abspath(os.path.join(conf_dir, "regex.json"))


lib_dir = os.path.abspath(os.path.join(src_dir, "..", "lib"))

ai_tools_dir = os.path.abspath(os.path.join(lib_dir, "integratedAITools"))
ai_graphs_dir = os.path.abspath(os.path.join(ai_tools_dir, "graphs"))
ai_audio_dir = os.path.abspath(os.path.join(ai_tools_dir, "audio"))
voice_main_mp3 = os.path.abspath(os.path.join(ai_audio_dir, "voice_main.mp3"))


data_dir = os.path.abspath(os.path.join(src_dir, "..", "data"))

configuration_data_dir = os.path.abspath(os.path.join(data_dir, "configuration_data"))
graph_storage_dir = os.path.abspath(os.path.join(data_dir, "graph_storage"))
current_configuration = os.path.abspath(os.path.join(configuration_data_dir, "current_configuration.txt"))
graph_png = os.path.abspath(os.path.join(graph_storage_dir, "graph.png"))


#------config----------------
config_json = open(config_json_path, "r", encoding="utf-8")
config_data: dict = json.load(config_json)
config_json.close()

token = config_data.get("token")
admins:dict = config_data.get("admins")

sys.setrecursionlimit(100000)



#------messages--------------
messages_json = open(messages_json_path, "r", encoding="utf-8")
messages_data: dict = json.load(messages_json)
messages_json.close()

info_messages: dict = messages_data.get("info_messages")
input_messages: dict = messages_data.get("input_messages")
output_messages: dict = messages_data.get("output_messages")
option_messages: dict = messages_data.get("option_messages")
success_messages: dict = messages_data.get("success_messages")
warning_messages: dict = messages_data.get("warning_messages")
error_messages: dict = messages_data.get("error_messages")



#------regex-----------------
regex_json = open(regex_json_path, "r", encoding="utf-8")
regex_data: dict = json.load(regex_json)
regex_json.close()



#------values----------------
DEFAULT_VALUE = "not stated..."

INTERVAL = "not stated..."
ACCURACY = "not stated..."
MATRIX = "not stated..."
EQUATION = "not stated..."
SYSTEM_OF_EQUATIONS = "not stated..."

current_page = 0

VERIFIED_STATE = False



#------telebot---------------
bot = telebot.TeleBot(token=token)
processor = ai_tools.MathFunctionProcessor()



#------functions-------------

def send_analyze(message: types.Message, equation: str, interval: tuple, result):
    desc, graph, audio = processor.process_function(equation)
    print(f"Текстовое описание:\n{desc}")
    print(f"График сохранен: {graph}")
    print(f"Аудиофайл сохранен: {audio}")

    img = plot_function_with_highlight(equation=equation, highlight_xmin=interval[0], highlight_xmax=interval[1], total_xmin=-8, total_xmax=8)
    audio_file = open(voice_main_mp3, "rb")

    bot.send_photo(message.chat.id, img)
    bot.send_voice(message.chat.id, audio_file)
    bot.send_message(message.chat.id, f"Integral value: {result[0]}\nIntervals count: {result[1]}")

    audio_file.close()




#------commands--------------
#? "/start"
@bot.message_handler(commands=["start"])
def start(message):    
    global current_page

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Choose option:")

    markup.add(types.KeyboardButton("#️⃣ Parameters"), types.KeyboardButton("✅ Solve"))
    markup.add(types.KeyboardButton("🗒 Instruction"))
    markup.add(types.KeyboardButton("ℹ️ About"))

    current_page = 0

    bot.send_message(message.chat.id, info_messages.get("welcome_message") + "\n" + info_messages.get("instruction_message") + "\n" + info_messages.get("info_commands_message"), parse_mode="HTML", reply_markup=markup)


#? "/help"
@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, info_messages.get("help_message"), parse_mode="HTML")


#? "/get_my_id"
@bot.message_handler(commands=["get_my_id"])
def iddd(message):
    bot.send_message(message.chat.id, f"your id: {message.from_user.id}")


#? "/admin"
@bot.message_handler(commands=["admin"])
def admin_console(message: types.Message):
    if VERIFIED_STATE:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Решить чью-то судьбу😈", callback_data="choose_someones_destiny"))

        bot.send_message(message.chat.id, "Hello, my lord, " + message.from_user.full_name, reply_markup=markup)

    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("verify me", callback_data="verification"))

        bot.send_message(message.chat.id, "Would u like to log in as admin?))", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "verification")
def admin_verification(call):
    global VERIFIED_STATE

    current_user = call.from_user.id

    if str(current_user) in admins.values():
        bot.send_message(call.from_user.id, "Verification was successed!")
        VERIFIED_STATE = True

@bot.callback_query_handler(func=lambda call: call.data == "choose_someones_destiny")
def choose_destiny(call):
    bot.send_message(call.from_user.id, "Пожалуйста введите имя подсудимого:")
    bot.register_next_step_handler_by_chat_id(call.from_user.id, next_step)

def next_step(message):
    name = message.text

    bot.send_message(message.chat.id, f"Итак, судьба {name} решается сейчас:")
    bot.send_dice(message.chat.id, emoji="🎲")



#? "/save_configuration"
@bot.message_handler(commands=["save_configuration"])
def save_config_to_file(message):
    global INTERVAL, ACCURACY, EQUATION, MATRIX, SYSTEM_OF_EQUATIONS

    file = open(current_configuration, "w")
    
    file.write(f"INTERVAL: {INTERVAL}\n")
    file.write(f"ACCURACY: {ACCURACY}\n")
    file.write(f"MATRIX: {MATRIX}\n")
    file.write(f"EQUATION: {EQUATION}\n")
    file.write(f"SYSTEM_OF_EQUATIONS: {SYSTEM_OF_EQUATIONS}")
    
    file.close()

    bot.send_message(message.chat.id, "Configuration was saved!")


#? "/load_configuration"
@bot.message_handler(commands=["load_configuration"])
def load_config_by_file(message):
    global INTERVAL, ACCURACY, MATRIX, EQUATION, SYSTEM_OF_EQUATIONS

    data = []
    data_display = ""

    #TODO refactor to json
    try:
        file = open(current_configuration, "r")

        for line in file.readlines():
            data.append(line.split(":")[1].strip())
            data_display += line

        file.close()

        interval_data = data[0].replace("(", "").replace(")", "").split(",")

        interval_value = (float(interval_data[0]), float(interval_data[1]))

        if data[0] != DEFAULT_VALUE: INTERVAL = interval_value
        if data[1] != DEFAULT_VALUE: ACCURACY = float(data[1])
        MATRIX = data[2]
        EQUATION = data[3]
        SYSTEM_OF_EQUATIONS = data[4]

        bot.send_message(message.chat.id, f"Your configuration was loaded!:\n\n{data_display}")

    except:
        bot.send_message(message.chat.id, "Error with file(")
    

#? "/show_configuration"
@bot.message_handler(commands=["show_configuration"])
def show_current_configuration(message):
    try:
        output = ""

        file = open(current_configuration, "r")

        for line in file.readlines():
            output += line
        
        bot.send_message(message.chat.id, f"Current configuration:\n\n{output}")

    except:
        bot.send_message(message.chat.id, "Error")


#? "/clear"
@bot.message_handler(commands=["clear"])
def clear_parameters(message):
    global INTERVAL, ACCURACY, MATRIX, EQUATION, SYSTEM_OF_EQUATIONS

    INTERVAL = ACCURACY = MATRIX = EQUATION = SYSTEM_OF_EQUATIONS = DEFAULT_VALUE

    bot.send_message(message.chat.id, "Parameters were cleared!")

            

#--------markup--------------
#? Parameters list
@bot.message_handler(func=lambda msg: msg.text == "#️⃣ Parameters")
def react(message):
    global current_page

    current_page = 1

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="List of parameters:")
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("back", callback_data="data"))

    markup.add(types.KeyboardButton("Interval"), types.KeyboardButton("Accuracy level"))
    markup.add(types.KeyboardButton("Matrix data"))
    markup.add(types.KeyboardButton("Equation"), types.KeyboardButton("System of equations"))
    markup.add(types.KeyboardButton("⬅️"))

    bot.send_message(message.chat.id, "you can go /back", reply_markup=markup)


#? Interval button
@bot.message_handler(func=lambda msg: msg.text == "Interval")
def interval_handle(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Set interval", callback_data="set_interval"))

    bot.send_message(message.chat.id, f"interval = <code>{INTERVAL}</code>\nYou can set new:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "set_interval")
def set_interval_handle(call):
    bot.send_message(call.from_user.id, "Your interval: ")
    bot.register_next_step_handler_by_chat_id(call.from_user.id, set_interval_by_keyboard)

def set_interval_by_keyboard(message: types.Message):
    global INTERVAL

    text = message.text

    if re.fullmatch(regex_data.get("interval").get("regex"), text):
        text = text.replace("[", "").replace("]", "")
        INTERVAL = tuple(map(float, text.split()))

        bot.send_message(message.chat.id, "interval was set!")
    else:
        #TODO: refactor
        bot.send_message(message.chat.id, "wrong!")


#? Back button
@bot.message_handler(func=lambda msg: msg.text == "⬅️")
def go_back(message):
    global current_page

    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Choose option:")

    if current_page == 1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Choose option:")

        markup.add(types.KeyboardButton("#️⃣ Parameters"), types.KeyboardButton("✅ Solve"))
        markup.add(types.KeyboardButton("🗒 Instruction"))
        markup.add(types.KeyboardButton("ℹ️ About"))

        current_page = 0

    elif current_page == 2:
        #TODO name
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Choose option:")


        markup.add(types.KeyboardButton("Solve system of linear equations"))
        markup.add(types.KeyboardButton("Solve non-linear equation"), types.KeyboardButton("Solve system of non-linear equations"))
        markup.add(types.KeyboardButton("Solve integral"))
        markup.add(types.KeyboardButton("⬅️"))

        current_page = 1

    bot.send_message(message.chat.id, "<i>going back...</i>", reply_markup=markup, parse_mode="HTML")


#? Accuracy button
@bot.message_handler(func=lambda msg: msg.text == "Accuracy level")
def accuracy_handle(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Set accuracy level", callback_data="set_accuracy"))

    bot.send_message(message.chat.id, f"Accuracy level = <code>{ACCURACY}</code>\nYou can set new:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "set_accuracy")
def set_accuracy_handle(call, flag=False):
    bot.send_message(call.from_user.id, "Your accuracy: ")
    bot.register_next_step_handler_by_chat_id(call.from_user.id, set_accuracy_by_keyboard, flag)
        
def set_accuracy_by_keyboard(message, flag):
    global ACCURACY

    #TODO: try
    if re.fullmatch(regex_data.get("accuracy").get("regex"), message.text):
        ACCURACY = float(message.text)
        
        bot.send_message(message.chat.id, "Accuracy was set!")
    else:
        #TODO: refactor
        bot.send_message(message.chat.id, "error")


    if flag:
        solve_system(message)


#? Matrix data button
@bot.message_handler(func=lambda msg: msg.text == "Matrix data")
def matrix_handle(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Set matrix data", callback_data="set_matrix"))

    #TODO: refactor
    bot.send_message(message.chat.id, f"Matrix data = <code>{MATRIX}</code>\nYou can set new:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "set_matrix")
def set_matrix_handle(call, flag=False):
    bot.send_message(call.from_user.id, f"Your matrix:")
    bot.register_next_step_handler_by_chat_id(call.from_user.id, set_matrix_by_keyboard, flag)

def set_matrix_by_keyboard(message, flag):
    global MATRIX

    if re.fullmatch(regex_data.get("matrix").get("regex"), message.text):
        MATRIX = [el.split() for el in message.text.split("\n")]

        bot.send_message(message.chat.id, "Matrix was set!")
    else:
        bot.send_message(message.chat.id, "error!")

    if flag:
        solve_system(message)


#? Equation button
@bot.message_handler(func=lambda msg: msg.text == "Equation")
def linear_equation_handle(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Set equation", callback_data="set_equation"))

    display_message = EQUATION.replace("**", "^").replace("*", "")

    bot.send_message(message.chat.id, f"Equation = <code>{display_message}</code>\nYou can set new:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "set_equation")
def set_linear_equation_handle(call):
    bot.send_message(call.from_user.id, "Your equation: ")
    bot.register_next_step_handler_by_chat_id(call.from_user.id, set_equation_by_keyboard)

def set_equation_by_keyboard(message):
    global EQUATION

    msg:str = message.text
    msg = msg.replace("^", "**")


    EQUATION = msg


#? System of equations button
#TODO: add regex
@bot.message_handler(func=lambda msg: msg.text == "System of equations")
def system_linear_equations_handle(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Set system of equations", callback_data="set_system"))

    bot.send_message(message.chat.id, f"System of equations = <code>{EQUATION}</code>\nYou can set new:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "set_system")
def set_system_of_linear_equations_handle(call):
    bot.send_message(call.from_user.id, "Your system of equations: ")
    bot.register_next_step_handler_by_chat_id(call.from_user.id, set_system_of_equations_by_keyboard)

def set_system_of_equations_by_keyboard(message):
    global EQUATION

    #TODO: refactor
    EQUATION = message.text

    bot.send_message(message.chat.id, "System of equations was set!")


#? Solve list
@bot.message_handler(func=lambda msg: msg.text == "✅ Solve")
def solve(message):
    global current_page

    current_page = 1

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Choose mode:")

    markup.add(types.KeyboardButton("Solve system of linear equations"))
    markup.add(types.KeyboardButton("Solve non-linear equation"), types.KeyboardButton("Solve system of non-linear equations"))
    markup.add(types.KeyboardButton("Solve integral"))
    markup.add(types.KeyboardButton("⬅️"))

    bot.send_message(message.chat.id, "solve", reply_markup=markup)


#? Solve system
@bot.message_handler(func=lambda msg: msg.text == "Solve system of linear equations")
def solve_system(message):
    id = message.chat.id

    if (ACCURACY != 0) and (MATRIX != ""):
        result = find_system_of_linear_equations_roots(MATRIX, ACCURACY)

        bot.send_message(id, result, parse_mode="HTML")

    else:
        if ACCURACY == 0:
            markup_acc = types.InlineKeyboardMarkup()
            markup_acc.add(types.InlineKeyboardButton("set accuracy level", callback_data="go_to_acc"))

            bot.send_message(id, "Your accuracy is 0", reply_markup=markup_acc)
            return

        if MATRIX == "":
            markup_matrix = types.InlineKeyboardMarkup()
            markup_matrix.add(types.InlineKeyboardButton("set matrix", callback_data="go_to_matrix"))

            bot.send_message(id, "Your matrix is empty", reply_markup=markup_matrix)


@bot.callback_query_handler(func=lambda call: call.data == "go_to_acc")
def go_to_accuracy(call):
    set_accuracy_handle(call, True)


@bot.callback_query_handler(func=lambda call: call.data == "go_to_matrix")
def go_to_matrix(call):
    set_matrix_handle(call, True)


#? Solve equation
@bot.message_handler(func=lambda msg: msg.text == "Solve non-linear equation")
def solve_non_linear_equation(message):
    global current_page

    current_page = 2

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(types.KeyboardButton("Bisection method"), types.KeyboardButton("Secant method"))
    markup.add(types.KeyboardButton("Simple iteration method"))
    markup.add(types.KeyboardButton("⬅️"))

    bot.send_message(message.chat.id, "Choose which method do u want to use?", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ["Bisection method", "Secant method", "Simple iteration method"])
def methods_handle(message):
    result = ""

    if message.text == "Bisection method":
        result = bisection_method(EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY, 0)
    elif message.text == "Secant method":
        result = secant_method(EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)
    elif message.text == "Simple iteration method":
        result = simple_iteration_method(EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)

    if result.count(None) > 0:
        print("error")
    else:
        bot.send_message(message.chat.id, f"Root: {result[0]}\nf(root): {result[1]}\niteration number: {result[2]}")


#? Solve system
@bot.message_handler(func=lambda msg: msg.text == "Solve system of non-linear equations")
def solve_system_of_non_linear_equations(message):
    global current_page

    current_page = 2

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    markup.add(types.KeyboardButton("Newton method"))
    markup.add(types.KeyboardButton("⬅️"))

    bot.send_message(message.chat.id, "which method do u want to use?", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Newton method")
def newton_solve(message):
    result = newton_method(SYSTEM_OF_EQUATIONS, INTERVAL[0], INTERVAL[1], ACCURACY)

    send_analyze(message, SYSTEM_OF_EQUATIONS.split(";")[0], INTERVAL, result)
    send_analyze(message, SYSTEM_OF_EQUATIONS.split(";")[1].replace("y", "x"), INTERVAL, result)

    bot.send_message(message.chat.id, f"x: {result[0]}\ny:{result[1]}\nf1(x, y): {result[2]}\nf2(x, y): {result[3]}\niteration numbers: {result[4]}")


#? Solve integral
@bot.message_handler(func=lambda msg: msg.text == "Solve integral")
def solve_integral(message):
    global current_page

    current_page = 2

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    markup.add(types.KeyboardButton("Left rectangles method"), types.KeyboardButton("Middle rectangles method"), types.KeyboardButton("Right rectangles method"))
    markup.add(types.KeyboardButton("Trapezoidal method"))
    markup.add(types.KeyboardButton("Simpson method"))
    markup.add(types.KeyboardButton("⬅️"))

    bot.send_message(message.chat.id, "Choose integral solving method:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ["Left rectangles method", "Middle rectangles method", "Right rectangles method"])
def solve_rectangles(message):
    if message.text == "Left rectangles method":
        result = calculate_integral("rectangle_left", EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)
    elif message.text == "Middle rectangles method":
        result = calculate_integral("rectangle_mid", EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)
    elif message.text == "Right rectangles method":
        result = calculate_integral("rectangle_right", EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)
    else:
        bot.send_message(message.chat.id, "Wrong method")
        
        return

    send_analyze(message, EQUATION, INTERVAL, result)

@bot.message_handler(func=lambda msg: msg.text == "Trapezoidal method")
def solve_trapezoida(message):
    result = calculate_integral("trapezoidal", EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)

    send_analyze(message, EQUATION, INTERVAL, result)


@bot.message_handler(func=lambda msg: msg.text == "Simpson method")
def solve_simpson(message):
    result = calculate_integral("simpson", EQUATION, INTERVAL[0], INTERVAL[1], ACCURACY)
    
    send_analyze(message, EQUATION, INTERVAL, result)

bot.infinity_polling()
