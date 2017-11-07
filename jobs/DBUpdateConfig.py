import os

try:
    if os.environ['DJANGOENV'] == 'prod':
		print 'running PROD'
		database = 'd9aigals9rapf5'
		user = 'lzxjlsyjaxpyyj'
		password = '19c915a470a3c43c8dde4e398d787ecb770a9bbd43ebffc5e18741accf178ad5'
		host = 'ec2-184-72-255-211.compute-1.amazonaws.com'

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
