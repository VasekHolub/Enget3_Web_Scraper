2017 CZECH ELECTION WEB SCRAPER

Overview

The script is designed to scrape election data from a specified URL and export the results into a CSV file.
It scrapes the following website: https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ
For the script to work, you have to choose a district you want to have scraped a provide its URL as an argument when launching the script.
	example of a viable URL for Prostějov district: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
The script does not work for the "Zahraničí" section as this was out of scope.
The CSV file contains the following information for all towns in the selected district:
	town code, name, n. of registered voters, n. of issued envelopes, n. of valid votes, list of all the political parties with the corresponding number of votes. 


Runnig the script

First you have to install dependencies into the folder from which you'll be running the script. This can be done in the following way:
	1. download the project directory from github and have the main.py and requirements.txt in the same folder.
	2. run a terminal and navigate to the project folder
	3. run the following command in the terminal: pip install -r requirements.txt
	4. this installs the necessary dependencies
Open the command line and navigate to the folder where main.py and installed dependencies are located and run the script with two following arguments:
	1. first argument is the URL of the district from "volby.cz/pls/ps2017nss/" which you want scraped.
	   this can be for example the Prostějov district: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
	2. second argument is the name for the resulting .csv file the script creates. The name has to end in .csv, otherwise it is invalid.
	3. arguments have to be passed as strings so in between quotation marks "".
	4. as an example, this is how you would start do script in the Windows environment: py main.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "results_prostejov.csv"

After running the script this way, a CSV file with the name you selected will appear in the folder where main.py is located.





	
		


