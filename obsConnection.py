# python 3.10
# OBS Script
__version__ = "0.9"

from enum import Enum
import obspython as obs
import serial
import time

source_name = None
audio_sources = []
selected_audio_source = None
property_settings = None
device_version = None
signal_handler = None

# serial Object Initialization
PORT = "COM4"
BAUDRATE = 19200
TIMEOUT = 5
ser = serial.Serial()
ser.baudrate = BAUDRATE
ser.port = PORT
ser.timeout = TIMEOUT


# Connects Script to react to when target source is muted
def connect_signal_handler(source):
    global signal_handler
    signal_handler = obs.obs_source_get_signal_handler(source)
    obs.signal_handler_connect(signal_handler, "mute", mute_callback)


# Actions to take On Mute Event
def mute_callback(calldata):
    ser.write(generate_state_command())


# Called to set default values of data settings
def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "source_name", "")


# Open and connect to the Serial connection
def script_load(settings):
    print("Script Load")
    connect()


def connect():
    if not ser.is_open:
        ser.open()
        print("Opened Connection, Sending Command")
        ser.write(HotMicComms.get_start_command().encode())
        time.sleep(2)
        global device_version
        device_version = ser.readline().decode().strip()
        print("Device Version : " + device_version)
    else:
        print("Serial Already Open")


# Send the end signal through serial bus and close the connection
def script_unload():
    if ser.is_open:
        ser.write(HotMicComms.get_end_command().encode())
        time.sleep(0.5)
        ser.close()


# Called to populate properties Description
def script_description():
    description = "Script to work in tandem with \"Moustache-Brand Hot Mic Indicator\" through USB Connection." \
                  "Select the source that is to be monitored, and communication with device starts on startup." \
                  "If an audio source is not listed, please make sure that the source is applied to any audio track " \
                  "and refresh."
    return description


# Called to display the properties GUI
def script_properties():
    props = obs.obs_properties_create()
    # Drop-down list of sources
    list_property = obs.obs_properties_add_list(props, "source_name", "Source name",
                                                obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)
    # Button to refresh the drop-down list
    obs.obs_properties_add_button(props, "button", "Refresh list of sources",
                                  lambda props, prop: True if populate_list_property_with_source_names(
                                      list_property) else True)
    # Button to read some debugging information
    obs.obs_properties_add_button(props, "buttonLog", "Log Info",
                                  lambda props, prop: print(
                                      "Device Version : " + str(device_version) + "\n"
                                      "Connection Status : " + str(ser.is_open) + "\n"
                                      "Source Name : " + str(obs.obs_source_get_name(selected_audio_source)) + "\n"
                                      "Source State : " + str(source_is_live())
                                  )
                                  )
    # Button to resync device and obs
    obs.obs_properties_add_button(props, "buttonResync", "Resync",
                                  lambda props, prop: ser.write(generate_state_command())
                                  )

    return props


# Called after change of settings including once after script load
def script_update(settings):
    print("Script Update")
    global source_name
    source_name = obs.obs_data_get_string(settings, "source_name")
    global property_settings
    property_settings = settings
    # dataframe or some other hash based data structure would make for O(1)
    global selected_audio_source
    sources = obs.obs_enum_sources()
    for source in sources:
        if obs.obs_source_get_name(source) == source_name:
            print(obs.obs_source_get_name(source))
            selected_audio_source = source
            break
    try:
        sources.remove(selected_audio_source)
    except ValueError:
        print("Log : Failed to find targeted source in source list")
        pass
    ser.write(generate_state_command())
    connect_signal_handler(selected_audio_source)
    obs.source_list_release(sources)


# Fills the given list property object with the names of all sources plus an empty one
def populate_list_property_with_source_names(list_property):
    global audio_sources
    audio_sources.clear()
    sources = obs.obs_enum_sources()
    obs.obs_property_list_clear(list_property)
    obs.obs_property_list_add_string(list_property, "", "")
    for source in sources:
        # Check for source use in Any audio Channel
        if obs.obs_source_get_audio_mixers(source):
            audio_sources.append(source)
            name = obs.obs_source_get_name(source)
            obs.obs_property_list_add_string(list_property, name, name)
    # Note : Sources are a SwigObject and are not hashable
    obs.source_list_release(sources)


def source_is_live() -> bool:
    return not obs.obs_source_muted(
        selected_audio_source
    )


# Generate Serial Bus device command
def generate_state_command():
    if source_is_live():
        return HotMicComms.get_hot_command(HotMicComms.LedColor.GREEN).encode()
    else:
        return HotMicComms.get_mute_command(HotMicComms.LedColor.GREEN).encode()


# Standardized Serial Bus Communications
class HotMicComms:
    __version__ = "0.9"
    EOL_MARKER = "\n"

    class LedColor(Enum):
        GREEN = "GREEN"
        ONBOARD = "ONBOARD"

    class LedCommand(Enum):
        HOT = 1
        MUTE = 2
        BLINK = 3
        HELLO = 4
        GOODBYE = 5

    @classmethod
    def get_flash_command(cls, led_color: LedColor, count: int) -> str:
        return "_".join([led_color.name, cls.LedCommand.BLINK.name, str(count)]) + cls.EOL_MARKER

    @classmethod
    def get_hot_command(cls, led_color: LedColor) -> str:
        return "_".join([led_color.name, cls.LedCommand.HOT.name]) + cls.EOL_MARKER

    @classmethod
    def get_mute_command(cls, led_color: LedColor) -> str:
        return "_".join([led_color.name, cls.LedCommand.MUTE.name]) + cls.EOL_MARKER

    @classmethod
    def get_start_command(cls):
        return cls.LedCommand.HELLO.name + cls.EOL_MARKER

    @classmethod
    def get_end_command(cls):
        return cls.LedCommand.GOODBYE.name + cls.EOL_MARKER
