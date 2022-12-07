# IOTEZ, painless Graphs for the ESP32

IotEZ is cool little project that aims to replace the influxDB and Grafana stack with a simple and easy to use python stack.

IotEZ uses the **ESP32** as its mcu of choice as it is well established in the maker community, EZ to use and readily available. The ESP32 is also capable of running micropython, which makes it easy to develop and deploy. 

IotEZ uses the **streamlit** library to provide a simple and easy to use web interface.

Having One unified stack for the datalogging and the web interface makes it possible to offer a NoCode solution for connecting the ESP32 to the Internet of things.

The project is still in its early stages and is not ready for production use. The goal is not to develop a production hardened solution, but rather to provide a simple and easy to use solution for small projects.

## Usage

IotEZ aims to be simple to use and easy to deploy. To get started, simply run the following command:

To start the server, run the following command:

```bash
python3 data_server.py
```

To start the web interface, run the following command:

```bash
streamlit run front_server.py
```

<!-- in bold -->

make sure to install the dependencies first with:

```bash
python3 -m pip install -r requirements.txt
```

## NoCode

IotEZ also provides a NoCode solution for those who don't want to write any code. To get started, start the front end server and navigate to the NoCode page. Then, simply fill in the form and click on the generate button. The generated code will be displayed in the text area. 

A the moment, the NoCode solution is not yet implemented. There are reference implementations in the `firmware/` folder. **Do not forget to change the wifi settings in the `secrets.h` file**.

## configuration

The configuration file is called `settings.py`. 

## coming soon

-  [ ] Add support for multiple sensors
-  [ ] Add Nocode generation
-  [ ] Hookup the frontend to the backend
-  [ ] and much more !!
