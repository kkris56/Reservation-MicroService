# Reservation-MicroService
How to request data:

  There are three requests that can be made: "create db", "show", and "edit".
  For each request, a list must be sent to the service via zmq. 
  The list that is sent via the zmq pipeline must be in a specific order based on the request being made.
  
  List for "create db": ('create db', <filename>)
  
    <filename> is a string provided by the user. The json db that contains the dates and times will be named after this.
    It is recommended that this name be related to what the admin is using it for (e.g. restaurant or hotel name)

  List for "show": ('show', <filename>, <start date>, <end date>)
  
    Start date and end date can be entered as either integers or strings as they will be converted to strings or integers within the service as needed.
    The times between the start and end dates provided will be what is sent to the user.
    <filename> corresponds to the name used to create the json db. Must be a string.

  List for "edit": ('edit', <filename>, <start date>, <end date>, <initial time>, <final time>, <avail_str>(optional))
  
    start date is the starting point for the edit and the end date is the end point.
    The initial and final time entries are the starting time of an edit to the final time.
    Times must be written as strings (e.g. '00:30', '12:30', '17:00'). Military time must be used
    If nothing is entered for <avail str>, the status of the times in the range specified by the user or admin will be marked as booked.
    If anything at all is entered for <avail str>, the specified times will be marked as 'available'.

  example request:
  
    def send_list_via_zmq(list_data):
      context = zmq.Context()
      socket = context.socket(zmq.PUSH)
      socket.bind("tcp://*:4000")

      # Serialize the list to JSON before sending
      serialized_data = json.dumps(list_data)
  
      # Send the serialized data
      socket.send(serialized_data.encode('utf-8'))
  
      socket.close()
      context.term()

    list = ['show', "Bob's Burgers", 2, 3]
    send_list_via_zmq(list)

  Note: The first element/entry of the list for a request must be the action you wish to take (create db, show, edit)

How to receive data:
  Data can only be received by using 'show'. To receive the list the service sends, use this code:
  
    def get_list():
      """Gets message from sender to determine what function is to be carried out"""
      context = zmq.Context()
      socket = context.socket(zmq.PULL)
      socket.connect("tcp://localhost:4000")
  
      json_data = socket.recv()
  
      py_data = json.loads(json_data.decode('utf-8'))
  
      socket.close()
      context.term()
  
      return py_data  ---> This returns the list of data that was requested

    This is a function I used to test my service. It can be used to obtain a list of the desired data.

  This service ONLY sends lists back if requested. Otherwise, it simply creates and maintains a database.

  Note: the list that is sent is a list of dictionaries that are embedded.
  
    For example, [{'1': [{'00:00': 'Available'}, {'00:30': 'Booked'}, .....]}]
    Also, take note that the dates are strings
  
![Screenshot (245)](https://github.com/kkris56/Reservation-MicroService/assets/107962398/38b27e8b-dc45-4fd6-847b-f19924a098be)
