import os

try:
    if os.environ['DJANGOENV'] == 'prod':
		print 'running PROD'
		database = 'd41hn3nmqj59mj'
		user = 'cxuazrriajgxck'
		password = '82148144f1b692e97575a0032adfb8da72ba7abcb4ce6fdd952117055758703a'
		host = 'ec2-54-235-119-27.compute-1.amazonaws.com'

    if os.environ['DJANGOENV'] == 'qa':
        print 'running QA'
        database = 'd97kd12l7m174t'
        user = 'kkppagovrjzfwt'
        password = '705c84b75f16eb5deee3400c041f1063c0adff2ec46ac5e254de1416f781098c'
        host = 'ec2-107-21-205-25.compute-1.amazonaws.com'
except Exception as e:
	print 'running local test'
	host = 'localhost'
	user = 'postgres'
	password = 'root'
	database = 'infinv'
