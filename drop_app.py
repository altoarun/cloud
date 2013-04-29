# Include the Dropbox SDK libraries
from dropbox import client, rest, session
import os, random, struct
from Crypto.Cipher import AES

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)


# Get your app key and secret from the Dropbox developer website
APP_KEY = 'sb20p35axyr4aqz'
APP_SECRET = 'klds1ipqn209lsz'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'dropbox'

sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

request_token = sess.obtain_request_token()

# Make the user sign in and authorize this token
url = sess.build_authorize_url(request_token)
print "url:", url
print "Please authorize in the browser. After you're done, press enter."
raw_input()

# This will fail if the user didn't visit the above URL and hit 'Allow'
access_token = sess.obtain_access_token(request_token)

client = client.DropboxClient(sess)
print "linked account:", client.account_info()


while 1:
	opt = raw_input("Enter choice : U- Encrypt and upload, D- Download and decrypt, E- Exit")
	if(opt=="U"):
		f_name = raw_input("Enter the full path of the file to be encrypted (including the file extension):")
		key_opt = raw_input("Do you want to use a new key or encrypt with default ? (N/D)")
		if(key_opt=="N"):
			opt1=raw_input("Enter key...minimum 16 bytes long")
		else:
			opt1="1234567891234567"
		encrypt_file(opt1,f_name)
		f_new_name=f_name+".enc"
		f = open(f_new_name)
		f_new_name_ext = "/"+f_new_name
		response = client.put_file(f_new_name_ext, f)
		print "File uploaded successfully:", response
		try: 	
			os.remove(f_new_name)
		except Exception, e:
			print e


	if(opt=="D"):
		f_name = raw_input("Enter filename (with file extension):")
		key_opt = raw_input("Use a specific key or the default ? (S/D)")
		if(key_opt=="S"):
			opt1=raw_input("Enter key used to encrypt the file ?")
		else:
			opt1 = "1234567891234567"
		f_new_name="/"+f_name
		f, metadata = client.get_file_and_metadata(f_new_name)
		out = open(f_name, 'w')
		out.write(f.read())
		out.close()
		decrypt_file(opt1,f_name)
		f_new = os.path.splitext(f_name)[0]
		print "File decrypted successfully and saved as "+f_new
		try: 	
			os.remove(f_name)
		except Exception, e:
			print e
	
	if(opt=="E"):
		break
	
	
