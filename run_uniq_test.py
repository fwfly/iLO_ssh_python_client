import time
import sys
import rrbsu



def run_uniq_test(HOST, username, password):
	r_client = rrbsu.RemoteRbsuClient(HOST, username, password)
	r_client.connect()
	r_client.change_to_shell()

	r_client.shell_execute("FS0:\r")
	time.sleep(2)
	r_client.shell_execute("uniq_test.nsh\r")

	while True:
		data = r_client.recv_data()
		if data:
			print"%s" %data
			if "Finished UNIQ test" in data:
				r_client.close_connect()
				print "Finish test"
				sys.exit(0)
			elif "User Physical Presence" in data:
                                r_client.shell_execute(" ")



if __name__ == '__main__':
	if len(sys.argv) < 4:
		usage = "Usage : python %s <hostname> <username> <password>" % __file__[__file__.rfind('/')+1:]
		print usage
		sys.exit(1)

	run_uniq_test(sys.argv[1], sys.argv[2], sys.argv[3])
