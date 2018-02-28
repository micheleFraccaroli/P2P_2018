import dir_login as cl

dir_host = 'localhost'
port = 50000

res = cl.dir_login(dir_host, port, IPeer)
print(res)

if(res == '0000000000000000'):
	print("Ops! There is an error with login")
