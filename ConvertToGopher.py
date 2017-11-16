import json
import os
import sys

#	Thread / post format is as follows:
#        index page is a standard Python list, where
#        index[0] is the first thread with ID 1,
#            index[1] is the second thread etc.
#        index[n][0] is the ID of n-th thread
#        index[n][1] is the subject
#        index[n][2] is the first reply, where
#            index[n][2][0] is the name (default is Anonymous)
#            index[n][2][1] is the Unix timestamp
#            index[n][2][2] is the ID (post number)
#            index[n][2][3] is the text (body)
#        index[n][k], where k > 1, is the k-th reply to n-th thread


HOSTNAME = "localhost"
PORT = "70"

GOPHER_ROOT = "gopher"

def parse_post(p):
	if len(p) < 4:
		name = "Anonymous"
		time = str(p[0])
		id_no = str(p[1])
		body = str(p[2])
	else:
		name = str(p[0])
		time = str(p[1])
		id_no = str(p[2])
		body = str(p[3])
	return {"name":name, "time":time, "id_no":id_no, "body":body}


def index_to_fs(json_in_folder, gopher_out_folder):
	index_path = os.path.join(json_in_folder, "index")
	with open(index_path, 'r') as f:
		buf = json.load(f)

	for n in buf: # Each thread
		subject = n[1]
		thread_id = str(n[0])
		
		content = subject+"\n"
		for p in n[2:]:
			post = parse_post(p)
			content = content + post['id_no'] + "    time:"+post['time']+"    name:"+post['name']+"\n--------\n"+post['body']+"\n\n"

		if not os.path.isdir(gopher_out_folder):
			os.makedirs(gopher_out_folder)

		with open(os.path.join(gopher_out_folder, thread_id), "w") as t:
			t.write(content)


def build_board_root(json_in_folder, gopher_out_folder, board_name):
	index_path = os.path.join(json_in_folder, "index")
	with open(index_path) as f:
		buf = json.load(f)
	
	content = ""
	for thread in buf: # buf has newest bumped threads first
		subject = thread[1]
		if subject == "":
			subject = "[no subject]"
		thread_id = str(thread[0])
		op = parse_post(thread[2])
		
		content = content+"\n\n\n0"+subject+"\t/"+board_name+"/"+thread_id+"\t"+HOSTNAME+"\t"+PORT+"\n--------\n"
		content = content + op["body"][:255] + "\n"
		if len(thread) < 4:
			break
		posts = thread[3:]
		for p in posts[-3:]:
			p = parse_post(p)
			content = content + p["body"][:255] + "\n\n"
			
	if not os.path.isdir(gopher_out_folder):
		os.makedirs(gopher_out_folder)
	
	with open(os.path.join(gopher_out_folder, "root"), "w") as r:
		r.write(content)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("No board name given!")
		sys.exit()
	else:
		board_path = sys.argv[1]
		board_name = os.path.basename(board_path)
	index_to_fs(board_path, os.path.join(GOPHER_ROOT, board_name))
	build_board_root(board_path, os.path.join(GOPHER_ROOT, board_name), board_name)
