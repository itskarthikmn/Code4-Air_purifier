connect  the air purifier to app.py file at line 16

*how to connect an air purifier to this system:*
    This is a smart air purifier control system that can work with compatible air purifiers that have:
        WiFi/network connectivity
        API support for remote control
        Sensor capabilities for PM2.5, PM10, NO2, SO2, CO, O3
    To connect your air purifier, you would need to: 
        a. Make sure your air purifier is network-enabled and supports external API connections 
        b. Get the device's connection details (IP address, port, authentication tokens) 
        c. Configure these details in the application

*To connect your air purifier:*
    1.First, check your air purifier's manual or documentation for:
        Network connectivity features
        API documentation
        Required authentication methods
    2.Then, set these environment variables before running the application:
        PURIFIER_IP=your_purifier_ip
        PURIFIER_PORT=your_purifier_port
        PURIFIER_API_KEY=your_api_key
        PURIFIER_ID=your_device_id
    3.If your air purifier doesn't have built-in network capabilities, you might need:
        A smart plug or hub that can connect to the purifier
        An IoT gateway device
        Additional sensors for air quality measurements

open terminal and run "python app.py"
then access the site "http://localhost:8000" in your browser
