"""Stewart Filmscreen Protocol."""

class StewartFilmscreenProtocol:
    # Types
    TYPE_COMMAND = "command"
    TYPE_QUERY = "query"
    TYPE_EVENT = "event"

    # Prefix
    PREFIX_COMMAND = "#"
    PREFIX_EVENT = "!"

    # Postfix
    POSTFIX = ";"

    # Motors
    MOTOR_ALL = "1.1.0.MOTOR"
    MOTOR_A = "1.1.1.MOTOR"
    MOTOR_B = "1.1.2.MOTOR"
    MOTOR_C = "1.1.3.MOTOR"
    MOTOR_D = "1.1.4.MOTOR"

    # Commands
    COMMAND_UP = "UP"
    COMMAND_DOWN = "DOWN"
    COMMAND_STOP = "STOP"
    COMMAND_RETRACT = "RETRACT"
    COMMAND_RECALL = "RECALL"
    COMMAND_STORE = "STORE"

    # Query
    QUERY_POSITION = "POSITION"

    # Events
    EVENT_STATUS = "STATUS"
    EVENT_POSITION = "POSITION"

    # Status Event Values
    STATUS_STOP = "STOP"
    STATUS_RETRACTING = "RETRACTING"
    STATUS_EXTENDING = "EXTENDING"
    STATUS_HOME = "HOME"
    STATUS_END = "END"

    @staticmethod
    def command(motor, command, argument=None):
        raw_command = f"{StewartFilmscreenProtocol.PREFIX_COMMAND}{motor}={command}"

        if argument is not None:
            raw_command = f"{raw_command},{argument}"
        
        return f"{raw_command};"

    def query(motor, query):
        return f"{StewartFilmscreenProtocol.PREFIX_COMMAND}{motor}.{query}=?;"
    
    @staticmethod
    def parse_message(data_str):
        parsed_messaged = None

        for motor in (StewartFilmscreenProtocol.MOTOR_ALL, StewartFilmscreenProtocol.MOTOR_A,
                      StewartFilmscreenProtocol.MOTOR_B, StewartFilmscreenProtocol.MOTOR_C,
                      StewartFilmscreenProtocol.MOTOR_D):
            
            if data_str[1:].startswith(motor):
            
                if data_str[0] == StewartFilmscreenProtocol.PREFIX_COMMAND:
                    command_part = data_str[len(motor)+1:]

                    if command_part.startswith(f".{StewartFilmscreenProtocol.QUERY_POSITION}"):
                        parsed_messaged = {
                            "type": StewartFilmscreenProtocol.TYPE_QUERY,
                            "motor": motor,
                            "command": StewartFilmscreenProtocol.QUERY_POSITION,
                            "value": None
                        }
                    else:
                        command, value = StewartFilmscreenProtocol._parse_command(data_str[len(motor)+1:])
                        parsed_messaged = {
                            "type": StewartFilmscreenProtocol.TYPE_COMMAND,
                            "motor": motor,
                            "command": command,
                            "value": value
                        }
                        
                elif data_str[0] == StewartFilmscreenProtocol.PREFIX_EVENT:
                    event, value = StewartFilmscreenProtocol._parse_event(data_str[len(motor)+1:])

                    parsed_messaged = {
                        "type": StewartFilmscreenProtocol.TYPE_EVENT,
                        "motor": motor,
                        "event": event,
                        "value": value
                    }
            
        return parsed_messaged

    @staticmethod
    def _parse_command(command_part):
        for command in (StewartFilmscreenProtocol.COMMAND_UP, StewartFilmscreenProtocol.COMMAND_DOWN,
                        StewartFilmscreenProtocol.COMMAND_STOP, StewartFilmscreenProtocol.COMMAND_RETRACT):
            
            if command_part.startswith(f"={command}"):
                return command, None
            
        for command in (StewartFilmscreenProtocol.COMMAND_RECALL, StewartFilmscreenProtocol.COMMAND_STORE):

            if command_part.startswith(f"={command}"):
                return command, command_part.split("(")[0].split(",")[1]
    
    @staticmethod
    def _parse_event(event_part):
        for event in (StewartFilmscreenProtocol.EVENT_STATUS, StewartFilmscreenProtocol.EVENT_POSITION):
                    
            if event_part.startswith(f".{event}"):
                
                return event, event_part.split("=")[1][:-1]