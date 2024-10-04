import socket
import chatlib
import num2words as n2w

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5678


# HELPER SOCKET METHODS

def connect():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER_IP, SERVER_PORT))
    return my_socket


def build_and_send_message(conn, cmd, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    protocol_msg = chatlib.build_message(cmd, data)
    conn.send(protocol_msg.encode())


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket,
    then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    data = conn.recv(1024).decode()
    paras_data = chatlib.parse_message(data)
    return paras_data


def login(conn):
    recv_msg = ""
    while recv_msg != (None, None):
        username = input("Please enter your username for login: \n")
        password = input("please enter password:\n")
        build_and_send_message(conn, 'LOGIN', f"{username}#{password}")
        recv_msg = recv_message_and_parse(conn)
        if recv_msg[0] == "ERROR":
            print(recv_msg[1])
        else:
            break

    print("LOGIN OK!")


def get_users_list(conn):
    users_str = build_send_recv_paras(conn, "USERS_LIST", "")
    return users_str[1]


def send_new_user(conn, username, password):
    build_and_send_message(conn, "NEW_USER", f"{username}#{password}")


def logout(conn):
    build_and_send_message(conn, "LOGOUT", "")
    print("you are logout")
    conn.close()


def build_send_recv_paras(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    recv = recv_message_and_parse(conn)
    return recv


def get_score(conn):
    my_score = build_send_recv_paras(conn, "MY_SCORE", "")
    return my_score[1]

def get_my_best_score(conn):
    my_score = build_send_recv_paras(conn, "BEST_SCORE", "")
    return my_score[1]


def get_high_score(conn):
    high_score = build_send_recv_paras(conn, "HIGHSCORE", "")
    return high_score[1]


def new_user(user_list, conn):
    good_user = 0
    while good_user != 1:
        user_exist = input("do you have user? (yes or no):\n")
        if user_exist == "yes":
            break
        if user_exist == "no":
            while good_user != 1:
                user_name = input("please write you user name:\n")
                if user_name not in user_list.split("#"):
                    while True:
                        password = input("please write your password:\n")
                        confirm_password = input("please confirm your password:\n")
                        if password == confirm_password:
                            print("you have new user!\ngood lack!!")
                            send_new_user(conn, user_name, password)
                            good_user = 1
                            break
                        else:
                            print("your password are different please try again")
                else:
                    print("this username is used please choose different user name")


def play_question(conn):
    wrong_questions = 0
    # player_start_score = 0
    while True:
        my_question = build_send_recv_paras(conn, "GET_QUESTION", "")
        if my_question[0] == "YOUR_QUESTION":
            answer_list = my_question[1].split("#")
            # return answer_list
            print(f"""Q:{answer_list[1]}
1.{answer_list[2]}
2.{answer_list[3]}
3.{answer_list[4]}
4.{answer_list[5]}""")
            while True:
                answer = input("Please choose an answer [1-4]:")
                try:
                    if int(answer) == 1 or 2 or 3 or 4:
                        confirm_answer = build_send_recv_paras(conn, "SEND_ANSWER",
                                                               f"{answer_list[0]}#{answer}")
                        if confirm_answer[0] == "WRONG_ANSWER":
                            wrong_questions += 1
                            print(f"SORRY...\nthe correct answer is answer {confirm_answer[1]}: "
                                  f"{answer_list[int(confirm_answer[1]) + 1]}\nyou have {wrong_questions}/3"
                                  f"wrong answer")
                        if confirm_answer[0] == "CORRECT_ANSWER":
                            print("CORRECT!!!")
                            print(f"your score now is: {get_score(conn)}")
                    break
                except ValueError:
                    print("you must choose answer between 1-4\n"
                          "please try again")
        if my_question[0] == "END_QUESTION":
            print("Good job!!\nyou answered all the questions")
        if wrong_questions == 3:
            build_and_send_message(conn,"END_GAME","")
            print("sorry you have three wrong answer\nyou are out")
            break


def get_logged_users(conn):
    logged_user = build_send_recv_paras(conn, "LOGGED", "")
    return logged_user[1]


def main():
    try:
        conn = connect()
        new_user(get_users_list(conn), conn)
        login(conn)
        print("hii welcome to the trivia game !!!")
        while True:
            print("""p       Play a trivia question
s       Get my highest score
h       Get high score table
l       Get logged users
q       Quit           
    """)
            server_choice = input("please write you choice:\n")
            if server_choice == "s":
                print(f"your best score is: {get_my_best_score(conn)}")
            elif server_choice == "h":
                print(f"high score table: \n{get_high_score(conn)}")
            elif server_choice == "p":
                play_question(conn)
            elif server_choice == "l":
                print(f"there is {n2w.num2words(len(get_logged_users(conn).split(',')), lang='en')} "
                      f"logged user's:\n{get_logged_users(conn)}")
            elif server_choice == "q":
                break
            else:
                print("Wrong input")
        logout(conn)
        print("GOOD BYE !!!")
    except ConnectionRefusedError:
        print("opsss...\ni have problem with connecting to the server...")


if __name__ == '__main__':
    main()
