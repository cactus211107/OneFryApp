import subprocess,requests,time,json
base='http://localhost:11434/api/'
subprocess.call('open /Applications/Ollama.app',shell=True)
print('Waiting For Ollama to start.')
while True:
	try:
		if requests.get(base+'tags').status_code == 200:
			break
	except:pass
	time.sleep(0.5)
print('Successfully running Ollama')
subprocess.call('open "/Applications/Visual Studio Code.app"',shell=True)


def createModel(base_model,filename,system_prompt):requests.post(base+'create',json={"name": str(filename),"modelfile": f"FROM {base_model}\nSYSTEM {system_prompt}"}).text
def getResponseFrom(model,messages):return requests.post(base+'chat',json.dumps({"model": str(model),"messages":messages,"stream":True}),stream=True)
def complete(model,prompt,options={}):return requests.post(base+'generate',json.dumps({"model":str(model),"prompt":prompt,"stream":False,"options":options}),stream=False).json()