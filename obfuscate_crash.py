from __future__ import print_function
import sys
import re
import uuid
import random

"""iOS app crash obfuscator by Abraham Masri @cheesecakeufo"""

new_binary_name = 'process_xyz'

if (len(sys.argv) < 2):
	print ('[ERROR]: No crash log was given')
	print ('[INFO]: run: python obfuscate_crash.py file.ips')
	quit()

path = sys.argv[1]

crash_string = ''

for line in open(path):
    crash_string += line + '\n'

hex_matches = re.findall("0[xX][0-9a-fA-F]+", crash_string)

for hex_string in hex_matches:

	hex_value = hex(int(hex_string, 16))

	# fixes an issue with values
	if(hex_value <= 0x3fffffffffffffff):
		new_hex_value = hex(abs(int(hex_string, 16) * random.randint(2,3) ^ random.randint(1,3) + random.randint(1,101000)))
	else:
		new_hex_value = hex(abs(int(hex_string, 16) * random.randint(2,3) - random.randint(1,101000)))

	# to maintain consistency, if we update one address, we'll update any other matching addresses
	crash_string = crash_string.replace(str(hex_value), str(new_hex_value))


binary_images = re.findall(r"[^ ]* (?=arm64)", crash_string)

if (len(binary_images) <= 0):
	print ('[ERROR]: could not find binary images in the crash')
	quit()


# process is always first
binary_name = binary_images[0].strip()

# replace all binary names with something different
crash_string = crash_string.replace(binary_name, new_binary_name)

# allow anything that starts with the following:
whitelisted_libs = ['libsystem_', 'libSystem', 'libc++', 'libobjc', 'CoreFoundation', 'dyld']

i = 0
for line in binary_images:

	line = line.strip()

	should_allow = False
	for lib in whitelisted_libs:
		if(lib in line):
			should_allow = True

	if (should_allow):
		continue

	crash_string = crash_string.replace(line, 'binary_{}'.format(i))
	i += 1


# mess with the paths
random_paths_list = ['/System/Library/', '/usr/', '/bin/', '/System/Library/CoreServices', '/tmp/', '/usr/local/']

# TODO: this can actually just replace the binary_images thing
paths = re.findall(r"(\/.*?\/)((?:[^\/]|\\\/)+?)(?:(?<!\\)\s|$)", crash_string)

for path in paths:
	crash_string = crash_string.replace(path[:1][0], random_paths_list[random.randint(0, len(random_paths_list) - 1)])


# remove everything between quotes (only what's important)
quotes_values = re.findall(r'"([A-Za-z0-9_\./\\-]*)"', crash_string)

for value in quotes_values:

	# skip our binary name
	if value in new_binary_name:
		continue

	crash_string = crash_string.replace(value, '')

# replace the hex values of binaries
binaries_hex_values = re.findall(r'(<)(.*?)(>)', crash_string)

for hex_value in binaries_hex_values:

	# tricky way to generate a fake uuid hex
	new_uuid = uuid.uuid4().hex
	new_uuid = new_uuid[:len(new_uuid) / 2 - 1]
	new_uuid += new_uuid
	crash_string = crash_string.replace(hex_value[1], new_uuid)


# hacky way to replace stack values
stack_values = re.findall(r' [+].{1,200}', crash_string)

for value in stack_values:

	crash_string = crash_string.replace(value, ' + ' + str(random.randint(1,101000)))

# fix new lines
crash_string = crash_string.replace('\n\n', '\n')

with open(new_binary_name + '-' + str(random.randint(1,101000)) + '.ips', 'w') as f:
    f.write(crash_string)
# file_path 
# print(sys.argv, len(sys.argv))