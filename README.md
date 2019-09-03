PyExo
=====

PyExo is a Python API for accessing the REST API provided by the [MYOB EXO](http://developer.myob.com/api/exo) 
accounting tool. It allows access to local, remote and cloud applications.

## Quickstart:

Include the library folder with your application and import it.

### Authentication

All requests made to the MYOB EXO API require authentication headers that contain your EXO username, password, a 
developer key and an EXO token generated using the EXO Config application in your installation. You can find details 
for the how to get these from the 
[MYOB EXO API page](http://developer.myob.com/api/exo/exo-api-overview/authentication/).

#### Environment variables

For convenience you can setup the following environment variables:
MYOB_EXO_USERNAME, MYOB_EXO_PASSWORD, MYOB_EXO_API_KEY, MYOB_EXO_TOKEN. For example, in Linux you could add these 
variables into ~./bashrc and for MacOS into ~/.bash_profile as shown below. You can also specify the environment 
variables in Windows. 
Note that you will need to reload the terminal for these to come into effect e.g using . ~/.bashrc or by restarting the
terminal.

```bash
export MYOB_EXO_USERNAME=demo
MYOB_EXO_PASSWORD=DEMO
export MYOB_EXO_API_KEY=ABCta353c5R6YXRvcjo=
export MYOB_EXO_TOKEN=123AA353c5R6YXRsTAQ18*%
```

#### Setting the Authentication Headers

Setting the authentication headers is done when initialising an instance of the API. First import the modules:

```python
>>> from exo import Exo
>>> from exo.auth import Credentials
```

If you have the environment variables setup then:

```python
>>> credentials = Credentials()
```

Otherwise you can enter them manually:

```python
>>> credentials = Credentials(<username>, <passoword>, <key>, <token>)
```

Then pass them into an instance of the Exo class:

```python
>>> exo = Exo(credentials)
```

#### EXO API Base IP and Port
Create a '.env' file in the root directory of your application and configure it as shown below:
```dotenv
[DEFAULT]
EXO_IP = <IP ADDRESS OF COMPUTER TO ACCESS>
EXO_PORT = <PORT>
```
e.g.
```dotenv
[DEFAULT]
EXO_IP = 192.168.0.1
EXO_PORT = 8888
```
## Using the EXO API

The API is a work in progress, it returns dictionaries exactly as provided by the EXO API.

## TODO
Add tests
