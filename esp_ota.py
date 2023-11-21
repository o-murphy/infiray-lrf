import argparse
import os
from pathlib import Path

import webrepl

parser = argparse.ArgumentParser(
    description='webrepl - connect to websocket webrepl',
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument('--host', '-i', default=os.environ.get('WEBREPL_HOST', '192.168.4.1'), help="Host to connect to")
parser.add_argument('--port', '-P', type=int, default=os.environ.get('WEBREPL_PORT', 8266), help="Port to connect to")
parser.add_argument('--verbose', '-v', action='store_true', help="Verbose information")
parser.add_argument('--debug', '-d', action='store_true', help="Enable debugging messages")
parser.add_argument('--password', '-p', default=os.environ.get('WEBREPL_PASSWORD', 'infiray1'),
                    help="Use following password to connect")

args = parser.parse_args()


def iter_esp32_dir():
    file_paths = []
    for root, dirs, files in os.walk('esp32'):
        for file_name in files:
            if file_name.endswith('.py'):
                file_paths.append(os.path.join(root, file_name))
    return file_paths


def upload_firmware():
    repl = webrepl.Webrepl(**args.__dict__)

    for file_path in iter_esp32_dir():
        relative_path = os.path.relpath(file_path, 'esp32')
        print(f"Put {file_path}")
        repl.put_file(file_path, Path(relative_path).as_posix())

    resp = repl.sendcmd("import machine; print('REBOOT')")
    if resp.decode('ascii'):
        print("Reset...")
    try:
        repl.sendcmd("machine.reset()")
    except Exception:
        pass


upload_firmware()
