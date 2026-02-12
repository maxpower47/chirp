# Copyright 2023 Jim Unroe <rock.unroe@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import struct
import logging
from enum import Enum

from chirp import chirp_common, directory, memmap
from chirp import bitwise, errors, util
from chirp.settings import RadioSetting, RadioSettingGroup, \
    RadioSettingValueInteger, RadioSettingValueList, \
    RadioSettingValueBoolean, RadioSettingValueString, \
    RadioSettingValueFloat, RadioSettings

LOG = logging.getLogger(__name__)

MEM_FORMAT = """
// #seekto 0x0000;
struct settingsold {
  char startuplabel[32];  // Startup Label         0000-001f
  char personalid[16];    // Personal ID           0020-002f
  u8 displaylogo:1,       // Display Startup Logo  0030
     displayvoltage:1,    // Display Voltage
     displaylabel:1,      // Display Startup Label
     tailtone:1,          // Tail Tone
     startupringtone:1,   // Startup Ringtone
     voiceprompt:1,       // Voice Prompt
     keybeep:1,           // Key Beep
     unknown_0:1;
  u8 txpriority:1,        // TX Priority           0031
     rogerbeep:2,         // Roger Beep
     savemode:1,          // Save Mode
     frequencystep:4;     // Frequency Step
  u8 squelch:4,           // Squelch               0032
     talkaround:2,        // Talkaround
     noaaalarm:1,         // NOAA Alarm
     dualdisplay:1;       // Dual Display
  u8 displaytimer;        // Display Timer         0033
  u8 locktimer;           // Lock Timer            0034
  u8 timeouttimer;        // Timeout Timer         0035
  u8 voxlevel:4,          // VOX Level             0036
     voxdelay:4;          // Delay
  ul16 tonefrequency;     // Tone Frequency        0037-0038
  ul16 fmfrequency;       // FM Frequency          0039-003a
  u8 fmstandby:1,         // FM Standby            003b
     dualstandby:1,       // Dual Standby
     standbyarea:1,       // Standby Area
     scandirection:1,     // Scan Direction
     unknown_2:2,
     workmode:1,          // Work Mode
     unknown_3:1;
  ul16 areaach;           // Area A CH             003c-003d
  ul16 areabch;           // Area B CH             003e-003f
  u8 unused_0:4,          //                       0040
     key1long:4;          // Key 1 Long
  u8 unused_1:4,          //                       0041
     key1short:4;         // Key 1 Short
  u8 unused_2:4,          //                       0042
     key2long:4;          // Key 2 Long
  u8 unused_3:4,          //                       0043
     key2short:4;         // Key 2 Short
  u8 unknown_4:4,         //                       0044
     vox:1,               // VOX
     unknown_5:3;
  u8 xposition;           // X position (0-159)    0045
  u8 yposition;           // Y position (0-110)    0046
  ul16 bordercolor;       // Border  Color         0047-0048
  u8 unknown_6[9];        // 0x00                  0049-0051
  u8 unknown_7[2];        // 0xFF                  0052-0053
  u8 range174_240;        // 174-240 MHz           0054
  u8 range240_320;        // 240-320 MHz           0055
  u8 range320_400;        // 320-400 MHz           0056
  u8 range480_560;        // 480-560 MHz           0057
  u8 unused_4[7];         // 0xFF                  0058-005e
  u8 unknown_8;           // 0x00                  005f
  u8 unused_5[12];        // 0xFF                  0060-006b
  u8 unknown_9[4];        // 0x00                  006c-006f
  ul16 quickch2;          // Quick CH 2            0070-0071
  ul16 quickch1;          // Quick CH 1            0072-0073
  ul16 quickch4;          // Quick CH 4            0074-0075
  ul16 quickch3;          // Quick CH 3            0076-0077
};

struct {
  u8 unknown_1[44];
  char startuplabel[32];  // Startup Label                            002c-004b
  char personalid[16];    // Personal ID                              004c-005b
  u8 voice_prompt;        // Voice Prompt 0=Off, 1=On                 005c
  u8 key_beep;            // Key Beep 0=Off, 1=On                     005d
  u8 unknown_2;           //                                          005e
  u8 lock_timer;          // Lock Timer 0=Off, 1=5 Sec, 2=10 Sec...   005f
  u8 key_led;             // Key LED 0=Off, 1=On                      0060
  u8 brightness;          // Brightness                               0061
  u8 lcd_timer;           // LCD Timer  0=Off, 1=5 Sec, 2=10 Sec...   0062
  u8 save_mode;           // Save Mode                                0063
  u8 unknown_4;           //                                          0064
  u8 menu_exit;           // Menu Exit 0=Off, 1=5 Sec, 2=10 Sec...    0065
  u8 tx_priority;         // Tx Priority 0=Edit, 1=Busy               0066
  u8 talkaround;          // Talkaround 0=Off, 1=Talkaround, 2=Invert 0067
  u8 alarm_type;          // Alarm Type                               0068
  u8 unknown_5[11];       //                                          0069-073
  u8 work_range;          // Work Range                               0074
  u8 unknown_6[3];        //                                          0075-077
  u8 freq_step;           // Frequency Step                           0078
  u8 area_a_mode;         // Area A Mode                              0079
  u8 unknown_7[32];       //                                          007a-098
  u8 unknown_8[3];        //                                          0099-09b
  u8 scan_direction;      // Scan Direction                           009c
  u8 scan_mode;           // Scan Mode                                009d
  u8 scan_return;         // Scan Return                              009e
} settings;

struct memoryold {
  ul32 rxfreq;      // RX Frequency          00-03
  ul16 rx_tone;     // PL/DPL Decode         04-05
  ul32 txfreq;      // TX Frequency          06-09
  ul16 tx_tone;     // PL/DPL Encode         0a-0b
  ul24 mutecode;    // Mute Code             0c-0e
  u8 unknown_0:2,   //                       0f
     mutetype:2,    // Mute Type
     unknown_1:4;   //
  u8 isnarrow:1,    // Bandwidth             00
     lowpower:1,    // Power
     scan:1,        // Scan Add
     bcl:2,         // Busy Lock
     is_airband:1,  // Air Band (AM)
     unknown_3:1,   //
     unknown_4:1;   //
  u8 unknown_5;     //                       01
  u8 unused_0:4,    //                       02
     scno:4;        // SC No.
  u8 unknown_6[3];  //                       03-05
  char name[10];    //                       06-0f
};

struct memory {
  u8 rx_mode;         // Rx Mode 0=FM, 1=AM, 2=SSB                                                         00
  u8 limit_rx_tx;     // Limit Rx/Tx 0=Rx+Tx, 1=Only Rx, 2=Only Tx                                         01
  u8 unknown_1;       //                                                                                   02
  u8 isnarrow;        // Bandwidth                                                                         03
  ul16 rx_tone;       // PL/DPL Decode                                                                     04-05
  ul32 rxfreq;        // RX Frequency                                                                      06-0a
  ul32 txfreq;        // TX Frequency                                                                      0b-0e
  ul16 tx_tone;       // PL/DPL Encode                                                                     0f-10
  u8 power;           // Power 0=Low, 1=Med, 2=High                                                        11
  u8 bcl;             // Busy Lock 0=Off, 1=Carrier Match, 2=CTX/DCS Match                                 12
  u8 dcs_encrypt:3,   // DCS Encrypt 0=Standard, 1=Encrypt 1, 2=Encrypt 2, 3=Encrypt 3, 4=Mute Code        13
     tot:5;           // TOT 0=Off, 1=5 Sec, 2=10 Sec...   (Hardware bug here, can only select up to 10)
  u8 scan_remove:1,   // Scan 0=Add, 1=Remove                                                              14
     tail_tone:3,     // Tail Tone 0=Off, 1=55Hz No Shift, 2=120 Shift, 3=180 Shift, 4=240 Shift
     scrambler:4;     // Scrambler 0=Off, 1-8=Values
  ul32 mutecode;      // Mute Code Hex value                                                               15-18
  u8 unknown_4[8];    //                                                                                   19-20
  char name[16];      // Channel Alias                                                                     21-2f
};

#seekto 0x2000;
struct memory channels[1024];

#seekto 0x8D20;
struct {
  u8 senddelay;           // Send Delay            8d20
  u8 sendinterval;        // Send Interval         8d21
  u8 unused_0:6,          //                       8d22
     sendmode:2;          // Send Mode
  u8 unused_2:4,          //                       8d23
     sendselect:4;        // Send Select
  u8 unused_3:7,          //                       8d24
     recvdisplay:1;       // Recv Display
  u8 encodegain;          // Encode Gain           8d25
  u8 decodeth;            // Decode TH             8d26
} dtmf;

#seekto 0x8D30;
struct {
  char code[14];          // DTMF code
  u8 unused_ff;
  u8 code_len;            // DTMF code length
} dtmfcode[16];

// #seekto 0x8E30;
struct {
  char kill[14];          // Remotely Kill         8e30-8e3d
  u8 unknown_0;           //                       8e3e
  u8 kill_len;            // Remotely Kill Length  83ef
  char stun[14];          // Remotely Stun         8e40-834d
  u8 unknown_1;           //                       8e4e
  u8 stun_len;            // Remotely Stun Length  8e4f
  char wakeup[14];        // Wake Up               8e50-8e5d
  u8 unknown_2;           //                       8e5e
  u8 wakeup_len;          // Wake Up Length        8e5f
} dtmf2;

"""

CMD_ACK = b"\x06"

DTCS_CODES = tuple(sorted(chirp_common.DTCS_CODES + (645,)))

_STEP_LIST = [0.25, 1.25, 2.5, 5., 6.25, 10., 12.5, 25., 50., 100., 500.,
              1000., 5000.]

LIST_AB = ["A", "B"]
LIST_BCL = ["Off", "Carrier", "CTC/DCS"]
LIST_DELAY = ["%s ms" % x for x in range(0, 2100, 100)]
LIST_DIRECTION = ["Up", "Down"]
LIST_FREQSTEP = ["0.25K", "1.25K", "2.5K", "5K", "6.25K", "10K", "12.5K",
                 "20K", "25K", "50K", "100K", "500K", "1M", "5M"]
LIST_INTERVAL = ["%s ms" % x for x in range(30, 210, 10)]
LIST_LIMITRXTX = ["Rx+Tx", "Only Rx", "Only Tx"]
LIST_MUTETYPE = ["Off", "-", "23b", "24b"]
LIST_ROGER = ["Off", "Roger 1", "Roger 2", "Send ID"]
LIST_SENDM = ["Off", "TX Start", "TX End", "Start and End"]
LIST_SENDS = ["DTMF %s" % x for x in range(1, 17)]
LIST_SKEY = ["None", "Monitor", "Frequency Detect", "Talkaround",
             "Quick CH", "Local Alarm", "Remote Alarm", "Weather CH",
             "Send Tone", "Roger Beep"]
LIST_REPEATER = ["Off", "Talkaround", "Frequency Reversal"]
LIST_TIMER = ["Off", "5 seconds", "10 seconds"] + [
    "%s seconds" % x for x in range(15, 615, 15)]
LIST_TXPRI = ["Edit", "Busy"]
LIST_WORKMODE = ["Frequency", "Channel"]

TXALLOW_CHOICES = ["RX Only", "TX/RX"]
TXALLOW_VALUES = [0xFF, 0x00]

VALID_CHARS = chirp_common.CHARSET_ALPHANUMERIC + \
    "`{|}!\"#$%&'()*+,-./:;<=>?@[]^_"
DTMF_CHARS = list("0123456789ABCD*#")


class MemoryRegions(Enum):
    """
    Defines the logical memory regions for this radio model.
    """
    settingData = 0
    channelData = 1


MEMORY_REGIONS_RANGES = {
    MemoryRegions.settingData: (0, 8),   # (Start addr, len)
    MemoryRegions.channelData: (8192, 48)}


def _checksum(data):
    cs = 0
    for byte in data:
        cs += byte
    return cs % 256


def _enter_programming_mode(radio):
    serial = radio.pipe

    exito = False
    for i in range(0, 5):
        serial.write(radio.magic)
        ack = serial.read(1)

        try:
            if ack == CMD_ACK:
                exito = True
                break
        except Exception:
            LOG.debug("Attempt #%s, failed, trying again" % i)
            pass

    # check if we had EXITO
    if exito is False:
        msg = "The radio did not accept program mode after five tries.\n"
        msg += "Check you interface cable and power cycle your radio."
        raise errors.RadioError(msg)


def _exit_programming_mode(radio):
    serial = radio.pipe
    try:
        serial.write(b"4R" + b"\x05\xEE\x79")
    except Exception:
        raise errors.RadioError("Radio refused to exit programming mode")


def _read_block(radio, block_addr, block_size):
    serial = radio.pipe

    cmd = struct.pack(">BH", ord(b'R'), block_addr + radio.READ_OFFSET)

    ccs = bytes([_checksum(cmd)])

    expectedresponse = b"R" + cmd[1:]

    cmd = cmd + ccs

    LOG.debug("Reading block %04x..." % block_addr)

    try:
        serial.write(cmd)
        response = serial.read(3 + block_size + 1)

        cs = _checksum(response[:-1])

        if response[:3] != expectedresponse:
            raise Exception("Error reading block %04x." % block_addr)

        chunk = response[3:]

        if chunk[-1] != cs:
            raise Exception("Block failed checksum!")

        block_data = chunk[:-1]
    except Exception:
        raise errors.RadioError("Failed to read block at %04x" % block_addr)

    return block_data


def _write_block(radio, block_addr, block_size, region):
    serial = radio.pipe

    # map the upload address to the mmap start and end addresses
    start_addr = block_addr * block_size
    end_addr = start_addr + block_size

    data = radio.get_mmap()[start_addr:end_addr]

    cmd = struct.pack(">BH", region, block_addr)

    cs = bytes([_checksum(cmd + data)])
    data += cs

    LOG.debug("Writing Data:")
    LOG.debug(util.hexprint(cmd + data))

    try:
        serial.write(cmd + data)
        if serial.read(1) != CMD_ACK:
            raise Exception("No ACK")
    except Exception:
        raise errors.RadioError("Failed to send block "
                                "to radio at %04x" % block_addr)


def _write_block2(radio, block_addr, block_size, region, databytes):
    serial = radio.pipe

    # map the upload address to the mmap start and end addresses
    start_addr = block_addr * block_size
    end_addr = start_addr + block_size

    data = databytes[start_addr:end_addr]

    cmd = struct.pack(">BH", region, block_addr)

    cs = bytes([_checksum(cmd + data)])
    data += cs

    LOG.debug("Writing Data:")
    LOG.debug(util.hexprint(cmd + data))

    try:
        serial.write(cmd + data)
        if serial.read(1) != CMD_ACK:
            raise Exception("No ACK")
    except Exception:
        raise errors.RadioError("Failed to send block "
                                "to radio at %04x" % block_addr)


def do_download(radio):
    LOG.debug("download")
    _enter_programming_mode(radio)

    data = b""

    status = chirp_common.Status()
    status.msg = "Cloning from radio"

    status.cur = 0
    status.max = radio.END_ADDR

    for addr in range(radio.START_ADDR, radio.END_ADDR, 1):
        status.cur = addr
        radio.status_fn(status)

        block = _read_block(radio, addr, radio.BLOCK_SIZE)
        data += block

        LOG.debug("Address: %04x" % addr)
        LOG.debug(util.hexprint(block))

    _exit_programming_mode(radio)

    return memmap.MemoryMapBytes(data)


def do_upload(radio):
    status = chirp_common.Status()
    status.msg = "Uploading to radio"

    _enter_programming_mode(radio)

    status.cur = 0
    status.max = radio._memsize

    # The OEM software reads the 1st block from the radio before commencing
    # with the upload. That behavior will be mirrored here.
    _read_block(radio, radio.START_ADDR, radio.BLOCK_SIZE)

    # TODO - status
    # TODO - fix region
    # TODO - cleanup

    data_bytes = radio.get_mmap()

    for item in MemoryRegions:
        start, length = MEMORY_REGIONS_RANGES[item]
        item_bytes = get_write_item_bytes(data_bytes, item, radio.BLOCK_SIZE)

        for addr in range(0x0000, length - 1, 1):
            region = int("0x90", 16) if item == MemoryRegions.settingData else int(
                "0x91", 16)
            addr1 = addr
            _write_block2(radio, addr1, radio.BLOCK_SIZE, region, item_bytes)

    # for start_addr, end_addr in radio._ranges:
    #    for addr in range(start_addr, end_addr, 1):
    #        status.cur = addr * radio.BLOCK_SIZE
    #        radio.status_fn(status)
    #        _write_block(radio, addr, radio.BLOCK_SIZE)

    _exit_programming_mode(radio)


def get_write_item_bytes(all_bytes: bytearray, item, blockSize):
    """
       Get the bytes for a specific memory region
       - Uses MEMORY_REGIONS_RANGES to find start and length
    """
    if item not in MEMORY_REGIONS_RANGES:
        LOG.debug(f"Unknown memory Range:{item}")
        return b""
    start, length = MEMORY_REGIONS_RANGES[item]
    return all_bytes[start:start+(length*blockSize)]


class Iradio98(chirp_common.CloneModeRadio):
    """IRADIO UV5118plus"""
    VENDOR = "Iradio"
    MODEL = "UV-5118plus"
    NAME_LENGTH = 16
    BAUD_RATE = 115200

    BLOCK_SIZE = 0x400
    magic = b"4R" + b"\x05\x10\x9b"

    VALID_BANDS = [(108000000, 136000000),  # RX only (Air Band)
                   (136000000, 174000000),  # TX/RX (VHF)
                   (174000000, 240000000),  # TX/RX
                   (240000000, 320000000),  # TX/RX
                   (320000000, 400000000),  # TX/RX
                   (400000000, 480000000),  # TX/RX (UHF)
                   (480000000, 560000000)]  # TX/RX

    POWER_LEVELS = [chirp_common.PowerLevel("Low", watts=1.00),
                    chirp_common.PowerLevel("Medium", watts=5.00),
                    chirp_common.PowerLevel("High", watts=10.00)]

    # Radio's write address starts at 0x0000
    # Radio's write address ends at 0x0140
    START_ADDR = 0
    END_ADDR = 0x035b
    # Radio's read address starts at 0x7820
    # Radio's read address ends at 0x795F
    READ_OFFSET = 0x0008

    _ranges = [
        (0x0000, 0x0140),
    ]
    _memsize = 0x32000  # 0x0140 * 0x400

    _upper = 999

    def get_features(self):
        rf = chirp_common.RadioFeatures()
        rf.has_settings = True
        rf.has_bank = False
        rf.has_ctone = True
        rf.has_cross = True
        rf.has_rx_dtcs = True
        rf.has_tuning_step = False
        rf.can_odd_split = True
        rf.has_name = True
        rf.valid_name_length = self.NAME_LENGTH
        rf.valid_characters = chirp_common.CHARSET_ASCII
        rf.valid_skips = ["", "S"]
        rf.valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]
        rf.valid_cross_modes = ["Tone->Tone", "Tone->DTCS", "DTCS->Tone",
                                "->Tone", "->DTCS", "DTCS->", "DTCS->DTCS"]
        rf.valid_power_levels = self.POWER_LEVELS
        rf.valid_duplexes = ["", "-", "+", "split"]
        rf.valid_modes = ["FM", "NFM"]  # 25 kHz, 12.5 kHz.
        rf.valid_dtcs_codes = DTCS_CODES
        rf.memory_bounds = (1, self._upper)
        rf.valid_tuning_steps = _STEP_LIST
        rf.valid_bands = self.VALID_BANDS

        return rf

    def process_mmap(self):
        self._memobj = bitwise.parse(MEM_FORMAT, self._mmap)

    def sync_in(self):
        """Download from radio"""
        try:
            data = do_download(self)
        except errors.RadioError:
            # Pass through any real errors we raise
            raise
        except Exception:
            # If anything unexpected happens, make sure we raise
            # a RadioError and log the problem
            LOG.exception('Unexpected error during download')
            raise errors.RadioError('Unexpected error communicating '
                                    'with the radio')
        self._mmap = data
        self.process_mmap()

    def sync_out(self):
        """Upload to radio"""
        try:
            do_upload(self)
        except Exception:
            # If anything unexpected happens, make sure we raise
            # a RadioError and log the problem
            LOG.exception('Unexpected error during upload')
            raise errors.RadioError('Unexpected error communicating '
                                    'with the radio')

    def get_raw_memory(self, number):
        return repr(self._memobj.memory[number - 1])

    @staticmethod
    def _decode_tone(toneval):
        # DCS examples:
        # D023N - 1013 - 0011 0000 0001 0011
        #                   ^-DCS
        # D023I - 2013 - 0011 0000 0001 0100
        #                   ^-DCS inverted
        # D754I - 21EC - 0010 0001 1110 1100
        #    code in octal-------^^^^^^^^^^^

        if toneval == 0x0000:
            return '', None, None
        elif toneval & 0x3000 == 0x3000:
            # DTCS R
            code = int('%o' % (toneval & 0x1FF))
            return 'DTCS', code, 'R'
        elif toneval & 0x2000:
            # DTCS N
            code = int('%o' % (toneval & 0x1FF))
            return 'DTCS', code, 'N'
        else:
            return 'Tone', ((toneval & 0xFFF) / 10.0), None

    @staticmethod
    def _encode_tone(mode, val, pol):
        # TODO - fix this
        if not mode:
            return 0x3000
        elif mode == 'Tone':
            return int(val * 10)
        elif mode == 'DTCS':
            code = int('%i' % val, 8)
            if pol == 'N':
                code |= 0x1800
            if pol == 'R':
                code |= 0x2800
            return code
        else:
            raise errors.RadioError('Unsupported tone mode %r' % mode)

    def get_memory(self, number):
        mem = chirp_common.Memory()
        _mem = self._memobj.channels[number - 1]
        mem.number = number

        mem.freq = int(_mem.rxfreq) * 10

        # We'll consider any blank (i.e. 0 MHz frequency) to be empty
        if mem.freq == 0:
            mem.empty = True
            return mem

        if _mem.rxfreq.get_raw() == b"\xFF\xFF\xFF\xFF":
            mem.freq = 0
            mem.empty = True
            return mem

        # Freq and offset
        mem.freq = int(_mem.rxfreq) * 10
        # TX freq set
        offset = (int(_mem.txfreq) * 10) - mem.freq
        if offset != 0:
            if chirp_common.is_split(self.get_features().valid_bands,
                                     mem.freq, int(_mem.txfreq) * 10):
                mem.duplex = "split"
                mem.offset = int(_mem.txfreq) * 10
            elif offset < 0:
                mem.offset = abs(offset)
                mem.duplex = "-"
            elif offset > 0:
                mem.offset = offset
                mem.duplex = "+"
        else:
            mem.offset = 0

        mem.name = str(_mem.name).rstrip(" ").replace("\xFF", " ")

        mem.mode = _mem.isnarrow and "NFM" or "FM"

        chirp_common.split_tone_decode(mem,
                                       self._decode_tone(_mem.tx_tone),
                                       self._decode_tone(_mem.rx_tone))

        mem.power = self.POWER_LEVELS[_mem.power]

        if _mem.scan_remove:
            mem.skip = "S"

        mem.extra = RadioSettingGroup("Extra", "extra")

        rs = RadioSettingValueList(
            LIST_LIMITRXTX, current_index=_mem.limit_rx_tx)
        rset = RadioSetting("limit_rx_tx", "Limit Rx/Tx", rs)
        mem.extra.append(rset)

        """  if mem.freq < 136000000:
            _mem.is_airband = True
        else:
            _mem.is_airband = False




        mem.extra = RadioSettingGroup("Extra", "extra")

        rs = RadioSettingValueList(LIST_BCL, current_index=_mem.bcl)
        rset = RadioSetting("bcl", "Busy Channel Lockout", rs)
        mem.extra.append(rset)

        rs = RadioSettingValueList(LIST_MUTETYPE, current_index=_mem.mutetype)
        rset = RadioSetting("mutetype", "Mute Type", rs)
        mem.extra.append(rset)

        rs = RadioSettingValueInteger(0, 16777215, _mem.mutecode)
        rset = RadioSetting("mutecode", "Mute Code", rs)
        rset.set_doc('Value between 0-16777215')
        mem.extra.append(rset)

        rs = RadioSettingValueInteger(0, 8, _mem.scno)
        rset = RadioSetting("scno", "SC No.", rs)
        rset.set_doc('Value between 0-8')
        mem.extra.append(rset) """

        return mem

    def set_memory(self, mem):
        LOG.debug("Setting %i(%s)" % (mem.number, mem.extd_number))
        _mem = self._memobj.channels[mem.number - 1]

        # if empty memory
        if mem.empty:
            _mem.set_raw("\xFF" * 48)
            return

        # _mem.set_raw("\xFF" * 48)

        _mem.rxfreq = mem.freq / 10

        if mem.duplex == "split":
            _mem.txfreq = mem.offset / 10
        elif mem.duplex == "+":
            _mem.txfreq = (mem.freq + mem.offset) / 10
        elif mem.duplex == "-":
            _mem.txfreq = (mem.freq - mem.offset) / 10
        else:
            _mem.txfreq = mem.freq / 10

        LOG.info(mem.name)
        _mem.name = mem.name

        _mem.scan_remove = mem.skip == "S"
        _mem.isnarrow = mem.mode == "NFM"

        _mem.rx_mode = 0

        # dtcs_pol = ["N", "N"]

        # txtone, rxtone = chirp_common.split_tone_encode(mem)
        # _mem.tx_tone = self._encode_tone(*txtone)
        # _mem.rx_tone = self._encode_tone(*rxtone)

        # _mem.lowpower = mem.power == self.POWER_LEVELS[1]

        # for setting in mem.extra:
        #    setattr(_mem, setting.get_name(), setting.value)

    def get_settings(self):
        # _dtmf = self._memobj.dtmf
        # _dtmf2 = self._memobj.dtmf2
        _settings = self._memobj.settings
        basic = RadioSettingGroup("basic", "Basic Settings")
        # dtmf = RadioSettingGroup("dtmf", "DTMF Settings")
        startup = RadioSettingGroup("startup", "Startup Settings")
        # txallow = RadioSettingGroup("txallow", "TX Allow Settings")
        # top = RadioSettings(basic, dtmf, startup, txallow)
        top = RadioSettings(basic, startup)

        # Basic Settings

        # Menu 21 - Personal ID
        _codeobj = _settings.personalid
        _code = str(_codeobj).rstrip('\xFF')
        rs = RadioSettingValueString(0, 16, _code, True)
        rset = RadioSetting("personalid", "Personal ID", rs)
        basic.append(rset)

        # Startup Settings

        _codeobj = _settings.startuplabel
        _code = str(_codeobj).rstrip('\xFF')
        rs = RadioSettingValueString(0, 32, _code, True)
        rset = RadioSetting("startuplabel", "Startup Label", rs)
        startup.append(rset)

        return top

    def set_settings(self, settings):
        for element in settings:
            if not isinstance(element, RadioSetting):
                self.set_settings(element)
                continue
            else:
                try:
                    name = element.get_name()
                    if "." in name:
                        bits = name.split(".")
                        obj = self._memobj
                        for bit in bits[:-1]:
                            if "/" in bit:
                                bit, index = bit.split("/", 1)
                                index = int(index)
                                obj = getattr(obj, bit)[index]
                            else:
                                obj = getattr(obj, bit)
                        setting = bits[-1]
                    else:
                        obj = self._memobj.settings
                        setting = element.get_name()

                    if element.has_apply_callback():
                        LOG.debug("Using apply callback")
                        element.run_apply_callback()
                    elif setting in ["areaach",
                                     "areabch",
                                     "quickch1",
                                     "quickch2",
                                     "quickch3",
                                     "quickch4"
                                     ]:
                        setattr(obj, setting, int(element.value) - 1)
                    elif element.value.get_mutable():
                        LOG.debug("Setting %s = %s" % (setting, element.value))
                        setattr(obj, setting, element.value)
                except Exception as e:
                    LOG.debug(element.get_name(), e)
                    raise

    @classmethod
    def match_model(cls, filedata, filename):
        # This radio has always been post-metadata, so never do
        # old-school detection
        return False


@directory.register
class Radtel880G(Iradio98):
    """Radtel 80G"""
    VENDOR = "Radtel"
    MODEL = "880G"
