import hashlib
import hmac

# creates a hash using sh256
x = hashlib.sha256("udacity")
print x
print x.hexdigest()

# create a hash using HMAC
y = hmac.new("aSecretKey","stringToHash")
print y.hexdigest()
