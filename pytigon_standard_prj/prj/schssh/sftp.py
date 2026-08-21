import argparse
import getpass
import os
import sys
from contextlib import chdir

import paramiko

# --- Global UI Text Variables ---
PROMPT_PASSWORD = "Enter SSH password (characters will be hidden): "
PROMPT_KEY_PASSPHRASE = "Enter private key passphrase (if encrypted): "
MSG_CONNECTING = "\nConnecting to {hostname}:{port}..."
MSG_DONE = "Done."
MSG_SIZE = "{value} file(s) transferred."
MSG_ERROR = "Error: {error}"


def get_open_ssh_client(hostname, port, username, password, key):
    """Establishes and returns an SSHClient connection (reused by the SFTP helpers)."""
    pkey = None
    passwd = None

    if key:
        try:
            pkey = paramiko.RSAKey.from_private_key_file(key)
        except paramiko.PasswordRequiredException:
            passphrase = getpass.getpass(PROMPT_KEY_PASSPHRASE)
            pkey = paramiko.RSAKey.from_private_key_file(key, password=passphrase)
    else:
        if password:
            passwd = password
        else:
            passwd = getpass.getpass(PROMPT_PASSWORD)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(MSG_CONNECTING.format(hostname=hostname, port=port))
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=passwd,
        pkey=pkey,
        timeout=10,
    )
    return client


def send_files(
    hostname,
    files,
    remote_dir=".",
    port=22,
    username=None,
    password=None,
    key=None,
):
    """Uploads one or more files to the server using the SFTP protocol."""
    client = get_open_ssh_client(hostname, port, username, password, key)
    try:
        with client.open_sftp() as sftp:
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                sftp.mkdir(remote_dir)
            for local_file in files:
                name = os.path.basename(local_file)
                remote_path = os.path.join(remote_dir, name)
                sftp.put(local_file, remote_path)
        print(MSG_DONE)
        print(MSG_SIZE.format(value=len(files)))
    finally:
        client.close()


def receive_files(
    hostname,
    remote_files,
    local_dir=".",
    port=22,
    username=None,
    password=None,
    key=None,
):
    """Downloads one or more files from the server using the SFTP protocol."""
    os.makedirs(local_dir, exist_ok=True)
    client = get_open_ssh_client(hostname, port, username, password, key)
    try:
        with client.open_sftp() as sftp:
            for remote_file in remote_files:
                name = os.path.basename(remote_file)
                local_path = os.path.join(local_dir, name)
                sftp.get(remote_file, local_path)
        print(MSG_DONE)
        print(MSG_SIZE.format(value=len(remote_files)))
    finally:
        client.close()


def client():
    """Command line client wrapping the send_files and receive_files functions."""
    help_epilog = (
        "commands:\n"
        "  send      Upload file(s) to the server over SFTP\n"
        "  receive   Download file(s) from the server over SFTP\n"
        "\n"
        "examples:\n"
        "  python sftp.py send user@host -x secret -d /remote/dir file1.txt file2.txt\n"
        "  python sftp.py receive user@host -k ~/.ssh/id_rsa -d /local/dir /remote/file.txt"
    )
    parser = argparse.ArgumentParser(
        description="Paramiko SFTP file transfer client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog,
    )

    subparsers = parser.add_subparsers(dest="action", required=False)

    def add_common_args(sub):
        sub.add_argument(
            "hostname", help="Target server IP or hostname or username@hostname"
        )
        sub.add_argument("-u", "--username", help="SSH username")
        sub.add_argument(
            "-p", "--port", type=int, default=22, help="SSH port (default: 22)"
        )
        sub.add_argument("-k", "--key", help="Path to private SSH key file")
        sub.add_argument("-x", "--password", help="Password")

    parser_send = subparsers.add_parser("send", help="Upload file(s) to the server")
    add_common_args(parser_send)
    parser_send.add_argument(
        "-d", "--remote-dir", default=".", help="Remote destination directory"
    )
    parser_send.add_argument("files", nargs="+", help="Local file(s) to upload")

    parser_receive = subparsers.add_parser(
        "receive", help="Download file(s) from the server"
    )
    add_common_args(parser_receive)
    parser_receive.add_argument(
        "-d", "--local-dir", default=".", help="Local destination directory"
    )
    parser_receive.add_argument("files", nargs="+", help="Remote file(s) to download")

    if "run_schssh.sftp" in sys.argv:
        idx = sys.argv.index("run_schssh.sftp")
        sys.argv = sys.argv[:1] + sys.argv[idx + 1 :]

    args = parser.parse_args()

    if args.action is None:
        parser.print_help()
        sys.exit(0)

    username = args.username
    hostname = args.hostname
    if "@" in hostname:
        username, hostname = hostname.split("@", 1)

    try:
        if args.action == "send":
            send_files(
                hostname,
                args.files,
                remote_dir=args.remote_dir,
                port=args.port,
                username=username,
                password=args.password,
                key=args.key,
            )
        elif args.action == "receive":
            receive_files(
                hostname,
                args.files,
                local_dir=args.local_dir,
                port=args.port,
                username=username,
                password=args.password,
                key=args.key,
            )
    except Exception as e:
        print(MSG_ERROR.format(error=e))
        sys.exit(1)


with chdir(os.environ["START_PATH"]):
    client()
