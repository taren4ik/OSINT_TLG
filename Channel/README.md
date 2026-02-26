#forward_messages - A Telegram client for receiving information from chat and channel participants

### Start project:


Clone the repository and switch to it on the command line:

```
bash
git clone https://github.com/taren4ik/OSINT_TLG
cd OSINT_TLG
```

Create and activate a virtual environment:

```
bash
python -m venv venv
```

For *nix-систем:
```
bash
source venv/bin/activate
```

Для windows-систем:
```
bash
source venv/Scripts/activate
```

Install dependencies from file requirements.txt:

```
bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Install dependencies from file:
```
cd OSINT_TLG/Channel
```

Log in to Telegram at https://my.telegram.org and go to the 
'API development tools' tab
API_ID
API_HASH and enter them in the .env file

```
.env
API_ID_3=XXXXX
API_HASH_3=XXXXX

SOURCE=XXXXXX,XXXXXXX,XXXXXXX
TARGET=XXXX
```

Start project:
```
bash
python osint_tlg.py
```


### When you first launch the client, you will need to confirm your phone number.
#Please enter your phone (or bot token): 
#Please enter the code you received: 


***Над проектом работал:***
* Dmitry Permyakoff | Github:https://github.com/taren4ik

