import webrepl

repl = webrepl.Webrepl(**{'host': '192.168.4.1', 'port': 8266, 'password': 'infiray1', 'debug': True})
# # resp=repl.sendcmd("import os; os.listdir()")
# # print(resp.decode("ascii"))
#
# # ver = repl.get_ver()
# # print(ver)
# #
# # with open('test.txt', 'w') as fp:
# #     fp.write("test\nsample")
# #
# # repl.
repl.put_file('esp32/emulator.py', 'emulator.py')
# # # resp = repl.sendcmd('import os;', 1)
# # # print(resp.decode("ascii"))
# # # repl.sendcmd("os.remove('src/test')")
# file = repl.get_file_content('emulator.py')
# print(file)
#
# resp=repl.sendcmd("import emulator")
# print(resp.decode("ascii"))

# resp=repl.sendcmd("import random; random.randrange(0, 3000, 0.1)")
# print(resp.decode("ascii"))