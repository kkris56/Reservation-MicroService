import time
import json
import os
import zmq
from datetime import timedelta, datetime


class NoDbException(Exception):
    pass


def get_list():
    """Gets message from sender to determine what function is to be carried out"""
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://localhost:4000")

    json_data = socket.recv()

    py_data = json.loads(json_data.decode('utf-8'))

    socket.close()
    context.term()

    return py_data


def send_string(string):
    """Sends string back to client who requested service"""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:4000")

    socket.send_string(string)

    socket.close()
    context.term()


def send_data(py_list):
    """Sends requested data to the client"""
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind("tcp://*:4000")  # You can choose the appropriate transport and address here (e.g., tcp, ipc, etc.)

    # Serialize the list to JSON before sending
    json_data = json.dumps(py_list)

    # Send the serialized data
    socket.send(json_data.encode('utf-8'))

    socket.close()
    context.term()


# upon start up: a dictionary
db_data = {}  # used to hold db setup for when a new json file is to be created

slot_increment = timedelta(minutes=30)  # used to increment time for each slot

start = datetime.strptime('00:00', '%H:%M')  # For having a start and end time to run loop to create db json
end = datetime.strptime('23:59', '%H:%M')

for date in range(0, 31):
    current_time = start  # sets current time to the specified start time

    db_data[date+1] = [{current_time.strftime('%H:%M'): 'Available'}]
    # '+1' is used to make the date reflect as it would in reality
    # e.g. instead of 0, the 1st is used for the 1st of the month
    current_time += slot_increment

    while current_time < end:  # append time and availability to db_data
        db_data[date+1].append({current_time.strftime('%H:%M'): 'Available'})
        current_time += slot_increment


def create_json(data, filename):
    """Used to create a new json file for storing db_data"""
    with open(f'{filename}.json', 'w') as db:
        json.dump(data, db, indent=4)

    db.close()
    return


def show_times(filename, start_date, end_date):
    """Returns a list of dates and times based on the
    start_date and end_date entered by the user"""
    if os.path.exists(f'{filename}.json') is False:
        raise NoDbException('No database exists by that name')

    if start_date == end_date:
        file = open(f'{filename}.json')
        time_data = json.load(file)

        ret_data = [{start_date: time_data[str(start_date)]}]

        file.close()

        return ret_data

    file = open(f'{filename}.json')
    time_data = json.load(file)
    ret_data = []

    for day in range(int(start_date), (int(end_date)+1)):
        ret_data.append({str(day): time_data[str(day)]})

    file.close()

    return ret_data


def edit_json(db_name, start_date, end_date, start_t, end_t, avail_str='Booked'):
    """
    Edits the values each time key of the specified dates of the specified
    db_name (json file name). If file does not exist, returns error
    """
    if os.path.exists(f'{db_name}.json') is False:
        raise NoDbException('No database exists by that name')
        #  create_json(db_data, db_name)

    with open(f'{db_name}.json', 'r') as db:
        j_data = json.load(db)

        # hold_time = start_t
        # hold_date = start_date

        if avail_str.lower() == 'booked':
            if start_date == end_date:
                for i in j_data[str(start_date)]:  # i represents dictionary
                    for k, v in i.items():    # k represents key
                        if start_t <= k < end_t:
                            i[k] = 'Booked'

                db.close()

            else:
                for e_date in range(int(start_date), (int(end_date)+1)):
                    if e_date == int(start_date):
                        # if on start date, times must be greater than or equal to start_t
                        for i in j_data[str(e_date)]:
                            for k, v in i.items():
                                if k >= start_t:
                                    i[k] = 'Booked'

                    elif e_date == int(end_date):
                        # if on end date, times must be less than or equal to end_t
                        for i in j_data[str(e_date)]:
                            for k, v in i.items():
                                if k < end_t:
                                    i[k] = 'Booked'

                    else:  # if e_date is neither the start date nor end_date, all times are booked
                        for i in j_data[str(e_date)]:
                            for k, v in i.items():
                                i[k] = 'Booked'

        else:
            if start_date == end_date:
                for i in j_data[str(start_date)]:
                    for k, v in i.items():
                        if start_t <= k < end_t:
                            i[k] = 'Available'

                db.close()

            else:
                for e_date in range(int(start_date), (int(end_date)+1)):
                    if e_date == int(start_date):
                        # if on start date, times must be greater than or equal to start_t
                        for i in j_data[str(e_date)]:
                            for k, v in i.items():
                                if k >= start_t:
                                    i[k] = 'Available'

                    elif e_date == int(end_date):
                        # if on end date, times must be less than or equal to end_t
                        for i in j_data[str(e_date)]:
                            for k, v in i.items():
                                if k < end_t:
                                    i[k] = 'Available'

                    else:  # if e_date is neither the start date nor end_date, all times are booked
                        for i in j_data[str(e_date)]:
                            for k, v in i.items():
                                i[k] = 'Available'

    with open(f'{db_name}.json', 'w') as db:
        json.dump(j_data, db, indent=4)
        db.close()


# where requests are received and processed
while True:
    # request list from client that tells the microservice what to do
    request_list = get_list()

    # request_list = ["edit", "lizard", 1, 1, "00:00", "00:30"]

    # if-else checks '0' index of list to determine what function to carry out
    # first condition is for making a new db
    if request_list[0].lower() == "create db":
        create_json(db_data, filename=request_list[1])

        if os.path.exists(f'{request_list[1]}.json') is False:
            raise NoDbException('No database exists by that name')

        # send_string("Database creation was successful!")

    elif request_list[0].lower() == "show":
        if os.path.exists(f'{request_list[1]}.json') is False:
            raise NoDbException('No database exists by that name')

        send_data(show_times(request_list[1], request_list[2], request_list[3]))

    # Checks if changes to availability is requested
    elif request_list[0].lower() == "edit":
        if os.path.exists(f'{request_list[1]}.json') is False:
            raise NoDbException('No database exists by that name')

        if len(request_list) < 6 or len(request_list) > 7:
            print("List is too small to carry out this action")
            # send_string("List is too small to carry out this action")

        elif len(request_list) == 7:
            edit_json(request_list[1], request_list[2], request_list[3], request_list[4], request_list[5],
                      request_list[6])

            # send_string("Changes were made successfully")

        else:
            edit_json(request_list[1], request_list[2], request_list[3], request_list[4], request_list[5])

            # send_string("Changes were made successfully")

# print(db_data)
# create_json(db_data, 'test')
#
# print(show_times('test', 1, 2))
#
# edit_json('test', '1', '2', '00:00', '01:30', 'Available')
#
# print(show_times('test', 1, 2))
#
# # next: make 'while True' loop
