from distutils import command
from itertools import count
from matplotlib.pyplot import sca
from pythonping import ping
import netifaces
import socket
from getmac import get_mac_address
import requests
from mac_vendor_lookup import MacLookup
import os
from os import system, name
import colorama
from colorama import Fore
from colorama import Style


colorama.init()

scanOptions = f'''
Scan Types:

    0: Lightning Scan || Scan Time (Seconds Per 255 Addresses) = 2.55 Seconds
    1: Quick Scan     || Scan Time (Seconds Per 255 Addresses) = 38.25 Seconds
    2: Default Scan   || Scan Time (Seconds Per 255 Addresses) = 63.75 Seconds
    3: Deep Scan      || Scan Time (Seconds Per 255 Addresses) = 255 Seconds

{Fore.YELLOW}Note: The lower the scan option, the lower accuracy in the results. {Style.RESET_ALL}
'''


def getVendor(mac_address):
    vendorName = ""

    try:
        vendorName = MacLookup().lookup(mac_address.upper())
    except:
        vendorName = "N/A"

    return vendorName


scanLength = [0.01, 0.15, 0.25, 1]
scanType = 2
while True:
    print(scanOptions)
    # Get preffered scan length, default is option 2
    scanType = input('Scan Type: ')

    try:
        # Default scan
        if ((scanType == "\n") or (scanType == "")):
            scanType = 2
            break
        # Check for integer input
        else:
            int(scanType)

        if((int(scanType) >= 0) and (int(scanType) <= 3)):
            break
        else:
            print(Fore.RED + "Enter an Integer In Range 0-3." + Style.RESET_ALL)
    except:
        print(Fore.RED + "Enter an Integer." + Style.RESET_ALL)


gateways = netifaces.gateways()
default_gateway = gateways['default'][netifaces.AF_INET][0]
print(f"Default Gateway: {default_gateway}")
matches, j, matchIndex = 0, 0, 0

defGatewayNoLastDigits = ""
defGatewayNoLastDigitsString = ""

IPsFound = []
macsFound = []
vendorsFound = []

defList = list(default_gateway)


for i in range(len(default_gateway)):

    if (default_gateway[i] == "."):
        matches += 1
        if(matches >= 3):
            matchIndex = i
            while(j <= i):
                defList[j] = ""
                j += 1
    i += 1

# Break down the default gateway to get rid of the last digit(s)
for k in range(len(default_gateway)):

    defGatewayNoLastDigits += default_gateway[k]
    if(k >= matchIndex):
        break
defGatewayNoLastDigitsString = "".join(defGatewayNoLastDigits)

i = 1
# Check for all IPs in the known range
while (i <= 255):
    # Check if the IP exists
    if(ping(f'{defGatewayNoLastDigitsString}{i}', count=1, size=1, timeout=scanLength[int(scanType)]).success() == True):
        # if(ping(f'{defGatewayNoLastDigitsString}{i}', count=1, size=1, timeout=0.25).success() == True):
        # If IP is up, then append to array
        IPsFound.append(defGatewayNoLastDigitsString + str(i))
    i += 1

# Get macs for each IP found
for h in range(len(IPsFound)):
    # Get MAC address and save it to variable
    macAddr = get_mac_address(ip=(IPsFound[h]))
    # Append IP to array
    macsFound.append(macAddr)
    h += 1

# Get vendor for each MAC found
for p in range(len(IPsFound)):
    # Get vendor using the MAC addresses in the macsFound array
    vendor = getVendor(macsFound[p])
    # Vendor to vendorsFound array
    vendorsFound.append(vendor)
    p += 1


# Output the results table
def outputRes():
    for l in range(len(IPsFound)):
        print(
            f'''|{l}| IP> {IPsFound[l]} || MAC> {macsFound[l]} || Vendor> {vendorsFound[l]}'''
        )


# Return information of client at the requested index
def outputIndex(index):

    print(
        f"|{index}| IP> {IPsFound[index]} || MAC> {macsFound[index]} || Vendor> {vendorsFound[index]}")


# Print the help menu using the dictionary supplied as an arg
def printHelpMenu(menu):
    for key, value in menu.items():
        print(key, value)


# Output results table
outputRes()

print(Fore.LIGHTBLUE_EX +
      f"Done Scanning! {str(len(IPsFound))} IP Adresses Found." + Style.RESET_ALL)

userInput = ""

helpMenu = {
    'print': "| Output the results table",
    'ping ': "| usage: ping 0-255 [REPLACE IP INDEX]",
    'ip   ': "| Pick a certain index to print all info about a certain IP adddress",
    'clear': "| Clears terminal window",
    'save ': "| Saves results to log.txt",
    'help ': "| Prints this help menu",
    'exit ': "| Quits program",
}

commands = ['exit', 'print', 'ip', 'help', 'clear', 'save', 'ping']

# TODO: Add error handling
while True:

    userInput = input('# ').lower()

    # Exit
    if(userInput == commands[0]):
        print("Bye :D")
        break

    # Output results table
    elif(userInput == commands[1]):
        outputRes()

    # Get info of a certain index
    elif userInput == commands[2]:
        while True:
            try:
                userInput = int(input('Index: '))
                outputIndex(userInput)
                break

            except:
                print("Something Went Wrong :/")

    # Help menu
    elif(userInput == commands[3]):
        printHelpMenu(helpMenu)

    elif(userInput == commands[4]):
        # for windows
        if name == 'nt':
            system('cls')

        # for mac and linux(here, os.name is 'posix')
        else:
            system('clear')

    elif(userInput == commands[5]):
        try:

            f = open("log.txt", "w")
            
            for l in range(len(IPsFound)):
                f.write(
                    f'''|{l}| IP> {IPsFound[l]} || MAC> {macsFound[l]} || Vendor> {vendorsFound[l]}\n'''
                )
            f.close()
        except:
            print(Fore.RED + "An error occured while saving" + Style.RESET_ALL)
    
    elif(commands[6] in userInput):

        try:
            newString = userInput.replace("ping", "")
            newString = newString.replace(" ", "")
            indexFound = int(newString)
            system(f"ping {IPsFound[indexFound]}")

        except:
            print(Fore.RED + 'Invalid Usage. Enter "help" to see usage.' + Style.RESET_ALL)

# Invalid Commands
    elif(userInput not in commands):
        print(
            Fore.RED + f'"{userInput}" is not a valid command!' + Style.RESET_ALL)
