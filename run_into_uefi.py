import sys
import rrbsu


def run_client(HOST, username, password):
        r_client = rrbsu.RemoteRbsuClient(HOST, username, password)
        r_client.connect()
        while True:
                data = r_client.recv_data()
                if data:
                        print"%r" %data
                        if "\x1b[5n" in data:
                                r_client.exec_cmd(CMD_DEV_OK)
                        elif "few moments" in data:
                                print "----Send ESC + 9"
                                r_client.exec_cmd(CMD_ESC_9)

                                # UEFI menu is interacted with shell mode.
                                r_client.change_to_shell()

                        elif "> System Configuration" in data:
                                print "----Selecting System Configuration"
                                r_client.shell_execute(CMD_DOWN)
                        elif "> One" in data:
                                print "----Select One-Time Boot Menu"
                                r_client.shell_execute(CMD_DOWN)
                        elif "> Embedded Applications" in data:
                                print "----Select Embedded Applications"
                                r_client.shell_execute("\r") # Enter Embedded Applications menu
                        elif "User Physical Presence" in data:
                                r_client.shell_execute(" ")

        r_client.close_connect()


if __name__ == '__main__' :
        if len(sys.argv) < 4:
                usage = "Usage : python %s <hostname> <username> <password>" % __file__[__file__.rfind('/')+1:]
                print usage
                sys.exit(1)

        run_client(sys.argv[1], sys.argv[2], sys.argv[3])
