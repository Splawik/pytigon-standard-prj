import sys
import select
import tty
import termios
import getpass
import paramiko
import signal
import os
import argparse

# --- Global UI Text Variables ---
PROMPT_PASSWORD = "Enter SSH password (characters will be hidden): "
PROMPT_KEY_PASSPHRASE = "Enter private key passphrase (if encrypted): "
MSG_CONNECTING = "\nConnecting to {hostname}:{port}..."
MSG_CONNECTED = "*** Connected! Starting interactive SSH console... ***\n"
MSG_CONN_ERROR = "\nConnection error: {error}"
MSG_CONN_CLOSED = "\n*** Connection closed ***"

def get_terminal_size():
    """Retrieves the current width and height of the local console window"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24  # Default values in case of error

def run_interactive_shell(chan):
    """Function handling the interactive terminal in Linux"""
    oldtty = termios.tcgetattr(sys.stdin)
    
    def resize_handler(signum, frame):
        try:
            col, row = get_terminal_size()
            chan.resize_pty(width=col, height=row)
        except Exception:
            pass

    signal.signal(signal.SIGWINCH, resize_handler)

    try:
        tty.setraw(sys.stdin.fileno())
        chan.setblocking(0)

        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            
            if chan in r:
                try:
                    x = chan.recv(1024).decode('utf-8', errors='ignore')
                    if len(x) == 0:
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except Exception:
                    break
                    
            if sys.stdin in r:
                x = os.read(sys.stdin.fileno(), 4096)
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)

# --- Argument Parsing & Configuration ---

def parse_arguments():
    """Parses command line arguments, replacing the complex if-else logic"""
    parser = argparse.ArgumentParser(description="Interactive Paramiko SSH Client")
    
    # Required arguments
    parser.add_argument("hostname", help="Target server IP or hostname or username@hostname")
    
    # Optional arguments
    parser.add_argument("-u", "--username", help="SSH username")
    parser.add_argument("-p", "--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("-k", "--key", help="Path to private SSH key file")
    parser.add_argument("-x", "--password", help="Password")
    
    
    # Compatibility fallback for old positional index checks if needed
    if "run_schssh.connect" in sys.argv:
        idx = sys.argv.index("run_schssh.connect")
        sys.argv = sys.argv[:1] + sys.argv[idx+1:]
    return parser.parse_args()

def get_connection_credentials(args):
    """Determines whether to use a key or password and collects inputs"""
    pkey = None
    password = None

    # Case 1: Private key authentication
    if args.key:
        try:
            pkey = paramiko.RSAKey.from_private_key_file(args.key)
        except paramiko.PasswordRequiredException:
            passphrase = getpass.getpass(PROMPT_KEY_PASSPHRASE)
            pkey = paramiko.RSAKey.from_private_key_file(args.key, password=passphrase)
    
    # Case 2: Standard password authentication
    else:
        if args.password:
            password = args.password
        else:
            password = getpass.getpass(PROMPT_PASSWORD)
        
    return pkey, password

# --- Main Execution Flow ---

args = parse_arguments()
if '@' in args.hostname:
    username, hostname = args.hostname.split('@', 1)
    args.hostname = hostname
    args.username = username
 
pkey, password = get_connection_credentials(args)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(MSG_CONNECTING.format(hostname=args.hostname, port=args.port))
    
    client.connect(
        hostname=args.hostname, 
        port=args.port, 
        username=args.username, 
        password=password, 
        pkey=pkey,
        timeout=10
    )
    
    current_col, current_row = get_terminal_size()
    chan = client.invoke_shell(term='xterm-256color', width=current_col, height=current_row)
    
    print(MSG_CONNECTED)
    run_interactive_shell(chan)
    chan.close()

except Exception as e:
    print(MSG_CONN_ERROR.format(error=e))

finally:
    client.close()
    print(MSG_CONN_CLOSED)

