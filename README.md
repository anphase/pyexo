PyExo
=====

PyExo is a Python API for accessing the REST API provided by the [MYOB EXO](http://developer.myob.com/api/exo) 
accounting tool. It allows access to local, remote and cloud applications.

## Quickstart:

Include the library folder with your application and import it.

### Authentication

All requests made to the MYOB EXO API require authentication headers that contain your EXO username, password, a 
developer key and an EXO token generated using the EXO Config application in your installation. You can find details 
for how to get these from the MYOB EXO Developer pages:[MYOB EXO API page](http://developer.myob.com/api/exo/exo-api-overview/authentication/).

#### Environment variables

For convenience you can setup the following environment variables:
EXO_USERNAME, EXO_PASSWORD, EXO_API_KEY, MYOB_EXO_TOKEN. For example, in Linux you could add these 
variables into ~./bashrc and for MacOS into ~/.bash_profile as shown below. You can also specify the environment 
variables in Windows. 
Note that you will need to reload the terminal for these to come into effect e.g using 
```shell script
$ . ~/.bashrc
```
or by restarting the terminal.

```shell script
$ export MYOB_EXO_USERNAME=demo
$ export MYOB_EXO_PASSWORD=DEMO
$ export EXO_API_KEY=ABCta353c5R6YXRvcjo=
$ export EXO_TOKEN=123AA353c5R6YXRsTAQ18*%
```

You can also set the environment variables from a configuration file as below:

Create a '.env' file in the root directory of your application and configure it as shown below:
```dotenv
[DEFAULT]
EXO_IP = <exo server ip>
EXO_PORT = <api port>
[AUTH]
EXO_USERNAME = <your exo username>
EXO_PASSWORD = <you exo password>
EXO_API_KEY = <key>
EXO_TOKEN = <token>
```
e.g.
```dotenv
[DEFAULT]
EXO_IP = 192.168.0.1
EXO_PORT = 8888
[AUTH]
EXO_USERNAME = demo
EXO_PASSWORD = DEMO
EXO_API_KEY = ABCta353c5R6YXRvcjo=
EXO_TOKEN = 11111111111122222222222222222333333333...
```

#### Setting the Authentication Headers

Setting the authentication headers is done when initialising an instance of the API. First import the modules:

```shell script
$ from exo import Exo
$ from exo.auth import Credentials
```

If you have the environment variables setup then:

```shell script
$ credentials = Credentials()
```

Otherwise you can enter them manually:

```shell script
$ credentials = Credentials(<username>, <passoword>, <key>, <token>)
```

Then pass them into an instance of the Exo class:

```shell script
$ exo = Exo(credentials)
```

## Using the EXO API

The API is a work in progress, it returns dictionaries exactly as provided by the EXO API.

## TODO
Add tests and examples

## Requirements
This project requires the requests module for the API calls
