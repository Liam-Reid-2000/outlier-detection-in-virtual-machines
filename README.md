# Oulier Detection in Virtual Machines

App Startup:

Application can run locally and in the cloud.

	The application is running on an azure container and can be accessed using this link:
		outlier-detection-dashboard.eastus.azurecontainer.io
		If the application is for whatever reason unavailable, it can be started locally.

	The application can run from a terminal window:
		Install the following: 
			Python v3.8
		On a terminal window, inside the project directory run:
			pip install -r requirements.txt
		Run the command:
			python app.py
		Navigate to the address specified using a browser (Usually 127.0.0.1:8050)
		Use the UI to generate data and display results
		To run the server for real time detection run command:
			python cpu_usage_server.py

